import re
from contextlib import suppress

from django import forms
from django.core.exceptions import ValidationError
from django.forms import HiddenInput, TextInput
from django.utils.safestring import SafeText
from django.utils.translation import gettext_lazy as _
from netaddr import AddrFormatError
from netaddr.ip import IPNetwork

from dcim.models import Device, Module
from netbox.forms import NetBoxModelForm
from netpicker import models
from netpicker import client
from netpicker.models import MappedDevice
from utilities.forms.fields import DynamicModelChoiceField


re_commands = re.compile(r'(?:[^{]*(\{[a-zA-Z_]\w*})??[^{]*)??',
                         re.MULTILINE | re.DOTALL)


def validate_identifier(value):
    if isinstance(value, str) and value.isidentifier():
        return value
    raise ValidationError(f'{value} is not a valid identifier')


def validate_command(value):
    if not re_commands.fullmatch(value):
        raise ValidationError('Invalid commands specified')


class DeviceComponentForm(NetBoxModelForm):
    device = DynamicModelChoiceField(
        label=_('Device'),
        queryset=Device.objects.all(),
        selector=True,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Disable reassignment of Device when editing an existing instance
        if self.instance.pk:
            self.fields['device'].disabled = False


class ModularDeviceComponentForm(DeviceComponentForm):
    module = DynamicModelChoiceField(
        label=_('Module'),
        queryset=Module.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )


class PlatformMultipleChoiceField(forms.MultipleChoiceField):
    def __init__(self, **kwargs):
        domains = client.get_domains()
        platforms = domains['platforms']
        choices = dict(zip(platforms, platforms))
        kwargs['choices'] = choices
        super().__init__(**kwargs)

    @staticmethod
    def get_choices():
        return PlatformMultipleChoiceField(
            label=_('Platforms'),
            required=False,
        )


class SettingsForm(NetBoxModelForm):
    server_url = forms.CharField(required=True, label=_('API url'),
                                 help_text=_('Netpicker API base url (root url)'))
    tenant = forms.CharField(required=True, label=_('Tenant'), help_text=_('Name of your Netpicker tenant'))
    api_key = forms.CharField(required=True, label=_('API key'), widget=TextInput(),
                              help_text=SafeText('Key obtained from <a id="np-admin" href="" target="_blank">'
                                                 'Netpicker API admin</a>'))

    class Meta:
        model = models.Setting
        fields = ['server_url', 'api_key', 'tenant']


class JobEditForm(NetBoxModelForm):
    name = forms.CharField(
        required=True,
        label=_('Name'),
        help_text=_("The job's unique name"),
        validators=[validate_identifier]
    )
    commands = forms.CharField(
        required=True,
        validators=[validate_command],
        widget=forms.Textarea(attrs={
            'rows': 15,
            'cols': 80,
            'placeholder': 'Enter CLI configure commands separated by new-line...',
            'class': 'form-control .monospaced'
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['platforms'] = PlatformMultipleChoiceField()

        if self.instance and self.instance.commands:
            cmds = '\n'.join(self.instance.commands)
            self.initial['commands'] = cmds

    def clean_commands(self):
        commands = self.cleaned_data['commands']
        cleared = [n.strip() for n in commands.splitlines()]
        return cleared

    def save(self, commit=True):
        client.save_job(self.instance)
        self.instance.pk = self.instance.name
        return self.instance

    class Meta:
        model = models.Job
        fields = 'name', 'platforms', 'commands'


def valid_ip(s):
    with suppress(ValueError, AddrFormatError):
        return IPNetwork(s)


def get_job_exec_form(job: models.Job, fixtures):
    params = {p.name: p for p in job.signature.params if p.name not in set(fixtures)}
    variables = params.keys()
    selectables = MappedDevice.objects.filter(platform__in=job.platforms).values('netbox_id')
    qs = Device.objects.filter(pk__in=selectables)
    dev_field = forms.ModelMultipleChoiceField(
        queryset=qs,
        help_text=('Devices known to Netpicker by IP address'
                   ' (and comply to platform(s) specified by the job)'))
    devices = dict(devices=dev_field)
    vars = {v: forms.CharField(label=v, required=params[v].has_default is False) for v in variables}
    meta = dict(Meta=type('Meta', tuple(), dict(model=models.Job, fields=variables)))
    misc = dict(confirm=forms.BooleanField(required=False, widget=HiddenInput()))
    attrs = devices | vars | misc | meta | dict(field_order=['devices', *variables])
    cls = type(forms.ModelForm)(f"Job_{job.signature}", (forms.ModelForm,), attrs)
    return cls
