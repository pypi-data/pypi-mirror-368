from netbox.views import generic
from netpicker import tables
from netpicker.models import MappedDevice
from netpicker.utilities import reload_devices
from netpicker.views.base import RequireSettingsMixin
from utilities.views import register_model_view


@register_model_view(MappedDevice, name='list', path='', detail=False)
class BackupSearch(RequireSettingsMixin, generic.ObjectListView):
    table = tables.MappedDeviceTable
    queryset = MappedDevice.objects.all()

    def get(self, request, *args, **kwargs):
        reload_devices()
        return super().get(request, *args, **kwargs)
