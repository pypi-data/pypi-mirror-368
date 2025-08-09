from adestis_netbox_plugin_account_management.models import *
from netbox.filtersets import NetBoxModelFilterSet
from django.db.models import Q

from dcim.models import Device
from utilities.filters import TreeNodeMultipleChoiceFilter
from django.utils.translation import gettext as _
import django_filters
from utilities.forms.fields import DynamicModelMultipleChoiceField
from virtualization.models import VirtualMachine, ClusterGroup, Cluster
from tenancy.models import TenantGroup, Tenant
from ipam.api.serializers import *
from ipam.api.field_serializers import *

__all__ = ('SystemFilterSet',)


class SystemFilterSet(NetBoxModelFilterSet):

    cluster_group_id = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(), required=False, label=_('Cluster group (name)')
    )

    cluster_id = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(), required=False, label=_('Cluster (name)')
    )

    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label=_('Device (ID)'),
    )

    device = django_filters.ModelMultipleChoiceFilter(
        field_name='device__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label=_('Device (name)'),
    )

    virtual_machine_id = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(), required=False, label=_('Virtual machine (name)')
    )

    group = TreeNodeMultipleChoiceFilter(
        queryset=TenantGroup.objects.all(),
        field_name='group',
        lookup_expr='in',
        to_field_name='group',
        label=_('Tenant group (group)'),
    )

    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label=_('Tenant (ID)'),
    )

    tenant = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        field_name='tenant__name',
        to_field_name='tenant',
        label=_('Tenant (name)'),
    )

    class Meta:
        model = System
        fields = (
            'id',
            'tenant',
            'group',
            'cluster_group_id',
            'cluster_id',
            'device',
            'virtual_machine_id',
            'name',
            'system_url',
            'system_status',
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(system_url__icontains=value) | Q(system_status__icontains=value)
        )
