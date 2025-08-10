from datetime import UTC, datetime, timedelta

import requests
from django.http import HttpRequest, StreamingHttpResponse
from django.utils.safestring import SafeText
from django.utils.translation import gettext_lazy as _
from django.views import View

from dcim.models import Device
from dcim.views import DeviceComponentsView
from netbox.views import generic
from netpicker.client import download_config, get_device_readouts, get_readout_history, search_configs
from netpicker.models import Backup, BackupHistory, BackupSearchHit, MappedDevice, ProxyQuerySet
from netpicker import tables
from netpicker.utilities import get_device_ip, get_logo, get_settings
from netpicker.views.base import RequireSettingsMixin
from utilities.views import ViewTab, register_model_view


def get_label(prefix: str) -> SafeText:
    result = SafeText(_(prefix) + ' ') + get_logo(style="width:16px; vertical-align:top")
    return result


class BackupProxyMixin:
    def get_object(self, **kwargs):
        backup = Backup()
        if pk := kwargs.get('pk'):
            backup.id = pk
            ipaddress, config_id = pk.split('-')
            backup.preview = download_config(ipaddress, config_id)
        return backup

    def get_queryset(self, request: HttpRequest):
        # this is a fake method to satisfy the view protocol
        return ProxyQuerySet(model=Backup)


class ConditionalViewTab(ViewTab):
    def render(self, instance):
        if settings := get_settings(instance._meta.current_request):
            is_mapped = MappedDevice.objects.filter(tenant=settings.tenant,
                                                    ipaddress=get_device_ip(instance)).first()
            if is_mapped:
                return super().render(instance)
        return {}


@register_model_view(Device, 'backups', path="netpicker/backups")
class DeviceBackupsView(RequireSettingsMixin, DeviceComponentsView):
    child_model = Backup
    force_redirect = False
    table = tables.DeviceBackupTable
    template_name = 'netpicker/backups.html'
    tab = ConditionalViewTab(
        label=get_label('Backups'),
        badge=None,
        permission='dcim.view_backups',
        weight=620,
        hide_if_empty=False
    )

    def get_children(self, request, parent):
        if request.settings and (ipaddress := get_device_ip(parent)):
            return get_device_readouts(parent.id, ipaddress)
        return []


@register_model_view(Backup)
class BackupPreviewView(RequireSettingsMixin, BackupProxyMixin, generic.ObjectView):
    template_name = 'netpicker/backup.preview.html'


@register_model_view(Backup, name='download')
class BackupDownloadView(View):
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        settings = get_settings(request)
        pk = request.resolver_match.kwargs.get('pk')
        ipaddress, config_id = pk.split('-')
        url = f"{settings.server_url}/api/v1/devices/{settings.tenant}/{ipaddress}/configs/{config_id}"
        headers = {'authorization': f"Bearer {settings.api_key}"}
        r = requests.get(url, headers=headers, stream=True)
        resp = StreamingHttpResponse(streaming_content=r.raw)
        resp['content-disposition'] = f'attachment; filename="{pk}.backup"'
        return resp


@register_model_view(Device, 'backup-history', path="netpicker/history")
class DeviceBackupHistoryView(RequireSettingsMixin, DeviceComponentsView):
    child_model = BackupHistory
    force_redirect = False
    table = tables.DeviceBackupHistoryTable

    template_name = 'netpicker/backups.html'
    tab = ConditionalViewTab(
        label=get_label('Change history'),
        badge=None,
        permission='dcim.view_backups',
        weight=620,
        hide_if_empty=False
    )

    def get_children(self, request, parent):
        if request.settings and (ipaddress := get_device_ip(parent)):
            start = datetime.now(UTC) - timedelta(days=30)
            after = start.strftime('%Y-%m-%d')
            return get_readout_history(ipaddress, after)
        return []


@register_model_view(BackupSearchHit, name='list', path='', detail=False)
class BackupSearch(RequireSettingsMixin, generic.ObjectListView):
    table = tables.DeviceBackupSearchTable

    def get_queryset(self, request):
        q = request.GET.get('q')
        hits = search_configs(q) if q else []
        return ProxyQuerySet(model=Backup, data=hits)
