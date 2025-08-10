import logging
from functools import partial

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from dcim.models import Device, Interface
from ipam.models import IPAddress

from netpicker.models import MappedDevice


log = logging.getLogger(__name__)


@receiver(pre_save, sender=Device)
def handle_device_pre_change(sender, instance, **kwargs):
    original = Device.objects.filter(pk=instance.pk).first()
    instance._original_primary_ip4 = original.primary_ip4 if original else None
    instance._original_primary_ip6 = original.primary_ip6 if original else None


@receiver(post_save, sender=Device)
def handle_device_change(sender, instance, created, **kwargs):
    """
    Handle Device model changes, including primary IP changes.
    """
    if created:
        if (ipv4 := instance.primary_ip4) is not None:
            handle_device_primary_ip_change(instance, None, ipv4, ip_version=4)
        if (ipv6 := instance.primary_ip6) is not None:
            handle_device_primary_ip_change(instance, None, ipv6, ip_version=6)
    else:
        handler = partial(handle_device_primary_ip_change, instance)
        if instance._original_primary_ip4 != instance.primary_ip4:
            handler(instance._original_primary_ip4, instance.primary_ip4, ip_version=4)

        if instance._original_primary_ip6 != instance.primary_ip6:
            handler(instance._original_primary_ip6, instance.primary_ip6, ip_version=6)


@receiver(pre_save, sender=IPAddress)
def handle_ip_address_pre_change(sender, instance, **kwargs):
    """
    Handle the IP address before it's changed.
    Store the original assigned object for comparison.
    """
    if instance.pk:  # Only for existing objects
        if original := IPAddress.objects.get(pk=instance.pk):
            instance._original_assigned_object = original.assigned_object
            instance._original_address = original.address
            instance._original = original
        else:
            instance._original_assigned_object = None
            instance._original_address = None
            instance._original = None


@receiver(post_save, sender=IPAddress)
def handle_ip_address_change(sender: IPAddress, instance: IPAddress, created: bool, **kwargs):
    """
    Handle IP address changes for device interfaces.
    Triggered when an IPAddress is saved (created or updated).
    """
    # Check if the IP address is assigned to an interface
    if instance.assigned_object_type and instance.assigned_object:
        # Get the content type for the Interface model
        interface_ct = ContentType.objects.get_for_model(Interface)

        # Check if the assigned object is an Interface
        if instance.assigned_object_type == interface_ct:
            interface = instance.assigned_object
            device = interface.device
            if device.primary_ip4_id == instance.pk:
                handle_device_primary_ip_change(device, instance._original, instance, ip_version=4)
            if device.primary_ip6_id == instance.pk:
                handle_device_primary_ip_change(device, instance._original, instance, ip_version=6)


def handle_device_primary_ip_change(
        device: Device,
        old_ip: IPAddress | None,
        new_ip: IPAddress | None,
        ip_version: int
) -> None:
    """
    Handle when a device's primary IP is changed.

    Args:
        device: Device instance
        old_ip: Previous IPAddress instance (can be None)
        new_ip: New IPAddress instance (can be None)
        ip_version: 4 or 6
    """
    # is this a known mapped device?
    if old_ip:
        MappedDevice.objects.filter(ipaddress=str(old_ip.address.ip)).update(netbox=None)

    if new_ip:
        MappedDevice.objects.filter(ipaddress=str(new_ip.address.ip)).update(netbox=device)
