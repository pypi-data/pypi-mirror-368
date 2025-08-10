from django.template import Context, Template
from django.utils.safestring import SafeText

from netbox.plugins import PluginConfig, get_plugin_config


class NetpickerConfig(PluginConfig):
    name = __name__
    verbose_name = "Netpicker Plugin"
    description = "Netpicker Configuration view and Simple Automation"
    version = '1.1.13'
    base_url = "netpicker"

    def logo(self, css_class: str = '', safe: bool = True, **kwargs) -> str:
        if css_class:
            kwargs.setdefault('class', css_class)
        opts = ' '.join((f'{k}="{v}"' for k, v in kwargs.items()))
        tpl = Template(f"""
            {{% load static %}}
            <img src="{{% static '{self.name}/netpicker.svg' %}}" alt="{self.name}" {opts}>""")
        text = tpl.render(Context({}))
        result = SafeText(text) if safe else text
        return result

    def ready(self):
        global netpicker_app
        netpicker_app = self
        from . import signals  # noqa
        from .templatetags import netpicker  # noqa
        super().ready()


config = NetpickerConfig
netpicker_app: NetpickerConfig | None = None


def get_config(cfg):
    return get_plugin_config(get_config.__module__, cfg)
