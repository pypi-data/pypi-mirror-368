import requests
from django.utils.safestring import SafeText
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from netbox.views import generic
from netpicker import forms
from utilities.views import ViewTab, register_model_view

from netpicker.client import get_netpicker_devices
from netpicker.models import Setting
from netpicker.utilities import get_device_ip, get_logo


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


@register_model_view(Setting, '', detail=False)
@register_model_view(Setting, 'edit')
class SettingsView(generic.ObjectEditView):
    form = forms.SettingsForm
    queryset = Setting.objects.all()
    template_name = 'netpicker/settings/netpicker.html'

    def get_object(self, **kwargs):
        return self.queryset.first()


class NetpickerDeviceTab(ViewTab):
    def render(self, instance):
        device = instance
        ipaddress = get_device_ip(device)
        if ipaddress is None or ipaddress not in get_netpicker_devices():
            return None
        logo = get_logo(style="width:16px;height:16px")
        return {
            'label': SafeText('Netpicker ' + logo),
            'badge': None,
            'weight': self.weight,
        }
