from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.safestring import SafeText
from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from netpicker import forms, tables
from netpicker.client import get_fixtures, get_job_details, get_job_log_details, get_job_logs, get_jobs, run_job
from netpicker.models import Job, Log
from netpicker.models.base import ProxyQuerySet
from netpicker.views.base import RequireSettingsMixin
from utilities.forms import restrict_form_fields
from utilities.views import ViewTab, register_model_view


class JobProxyMixin:
    def get_object(self, **kwargs):
        if name := kwargs.get('pk'):
            job = get_job_details(name=name)
        else:
            job = Job()
        return job

    def get_queryset(self, request: HttpRequest):
        # this is a fake method to satisfy the view protocol
        return ProxyQuerySet(model=Job)


@register_model_view(Log, name='list', path='', detail=False)
class AutomationLogsView(RequireSettingsMixin, generic.ObjectListView):
    table = tables.AutomationLogTable
    template_name = 'netpicker/automation/logs.html'

    def get_queryset(self, request):
        logs = get_job_logs()
        data = [Log.from_basemodel(obj) for obj in logs]
        return ProxyQuerySet(model=Log, data=data)


@register_model_view(Log)
class AutomationLogView(RequireSettingsMixin, generic.ObjectView):
    table = tables.AutomationLogTable
    template_name = 'netpicker/automation/log-detail.html'

    def get_queryset(self, request: HttpRequest):
        # this is a fake method to satisfy the view protocol
        return ProxyQuerySet(model=Log)

    def get_object(self, **kwargs):
        obj = get_job_log_details(id=str(kwargs['pk']))
        return Log.from_basemodel(obj)

# Jobs #


@register_model_view(Job, name='list', path='', detail=False)
class AutomationJobsListView(RequireSettingsMixin, generic.ObjectListView):
    table = tables.AutomationJobsTable
    template_name = 'netpicker/automation/jobs.html'

    def get_queryset(self, request):
        jobs = get_jobs()
        return ProxyQuerySet(model=Job, data=jobs)


@register_model_view(Job)
class AutomationJobsView(RequireSettingsMixin, JobProxyMixin, generic.ObjectView):
    template_name = 'netpicker/job.html'

    def get_extra_context(self, request, instance):
        netboxed = instance and instance.tags and 'netboxed' in instance.tags
        return {'netboxed': netboxed}


@register_model_view(Job, 'joblogs', path='job-logs')
class JobsLogView(JobProxyMixin, generic.ObjectChildrenView):
    child_model = Log
    table = tables.AutomationLogTable
    base_template = 'netpicker/automation/job.html'
    template_name = 'netpicker/automation/job-logs.html'

    tab = ViewTab(
        label=_('Logs'),
        badge=None,
        permission='dcim.view_job',
        weight=570,
        hide_if_empty=False
    )

    def get_children(self, request, parent: Job):
        logs = get_job_logs(job_name=parent.name)
        data = [Log.from_basemodel(obj) for obj in logs]
        return ProxyQuerySet(model=Log, data=data)


@register_model_view(Job, 'add', detail=False)
@register_model_view(Job, 'edit')
class AutomationJobEditView(RequireSettingsMixin, JobProxyMixin, generic.ObjectEditView):
    form = forms.JobEditForm
    template_name = 'netpicker/automation/job-edit.html'


@register_model_view(Job, 'delete')
class DeviceDeleteView(RequireSettingsMixin, JobProxyMixin, generic.ObjectDeleteView):
    def _get_dependent_objects(self, obj):
        return {}

    def get_return_url(self, request, obj=None):
        return reverse('plugins:netpicker:job_list')


@register_model_view(Job, 'run')
class AutomationJobRunView(RequireSettingsMixin, JobProxyMixin, generic.ObjectEditView):
    template_name = 'netpicker/automation/job-run.html'

    def form(self, instance: Job, **kwargs):
        fixtures = get_fixtures()
        form_cls = forms.get_job_exec_form(instance, fixtures)
        return form_cls(instance=instance, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs):
        obj = self.get_object(**kwargs)
        form = self.form(data=request.POST, files=request.FILES, instance=obj)
        restrict_form_fields(form, request.user)
        final_commands = {}
        if form.is_valid():
            data = form.cleaned_data
            unconfirmed_data = data.copy()
            devices = data.pop('devices', None)
            if data.pop('confirm', False):
                run_job(obj, devices=devices, variables=data)
                messages.success(request, 'Job was successfully dispatched for execution.')
                return_url = self.get_return_url(request, obj)
                # If the object has been created or edited via HTMX, return an HTMX redirect to the object view
                if request.htmx:
                    return HttpResponse(headers={
                        'HX-Location': return_url,
                    })

                return redirect(return_url)

            unconfirmed_data['confirm'] = True
            form = self.form(data=unconfirmed_data, instance=obj)
            final_commands = prefill_commands(obj, unconfirmed_data)

        context = {
            'model': Job,
            'object': obj,
            'form': form,
            'return_url': self.get_return_url(request, obj),
            'final_commands': final_commands,
            **self.get_extra_context(request, obj),
        }
        return render(request, self.template_name, context)


def prefill_commands(obj, data):
    if obj.commands is None:
        return 'Complex jobs cannot show rendered commands'

    hilited = {k: f"<b>{v}</b>" for k, v in data.items()}
    lines = [cmd.format(**hilited) for cmd in obj.commands]
    block = '<br/>'.join(lines)
    return SafeText(block)
