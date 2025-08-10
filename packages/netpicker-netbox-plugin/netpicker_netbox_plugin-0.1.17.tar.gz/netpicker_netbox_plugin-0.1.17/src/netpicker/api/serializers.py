from netbox.api.serializers import NetBoxModelSerializer

from netpicker.models import Setting


__all__ = 'SettingSerializer',


class SettingSerializer(NetBoxModelSerializer):
    class Meta:
        model = Setting
        fields = ('id', 'server_url', 'api_key', 'tenant')
