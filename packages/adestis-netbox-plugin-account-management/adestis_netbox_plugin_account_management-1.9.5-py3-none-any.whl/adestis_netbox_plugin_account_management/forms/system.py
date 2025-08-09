from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm, NetBoxModelBulkEditForm, NetBoxModelImportForm
from tenancy.models import *
from dcim.models import *
from utilities.forms.fields import (
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    CSVModelChoiceField,
    CSVChoiceField,
    TagFilterField,
)
from virtualization.models import VirtualMachine, ClusterGroup, Cluster
from adestis_netbox_plugin_account_management.models.login_credentials import (
    LoginCredentials,
    LoginCredentialsStatusChoices,
)
from adestis_netbox_plugin_account_management.models.system import System, SystemStatusChoices
from django.utils.translation import gettext_lazy as _
from utilities.forms.rendering import FieldSet

__all__ = ('SystemForm', 'SystemFilterForm', 'SystemBulkEditForm', 'SystemCSVForm')


class SystemForm(NetBoxModelForm):

    group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        null_option='None',
    )

    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        query_params={'group_id': '$group'},
    )

    cluster_group = DynamicModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        null_option='None',
        help_text=_("Pin the system to a specific cluster group"),
    )

    cluster = DynamicModelChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'group_id': '$cluster_group',
        },
        help_text=_("Choose a cluster within the selected cluster group that contains the system"),
    )

    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'cluster_id': '$cluster',
        },
        help_text=_("Pin this system to a specific device within the selected cluster"),
    )

    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'cluster_id': '$cluster',
            'device_id': '$device',
        },
        help_text=_("Pin this system to a specific virtual machine of the selected device"),
    )

    fieldsets = (
        FieldSet('name', 'system_url', 'system_status', 'tags'),
        FieldSet('group', 'tenant', 'cluster_group', 'cluster', 'device', 'virtual_machine'),
    )

    class Meta:
        model = System
        fields = (
            'cluster_group',
            'cluster',
            'device',
            'virtual_machine',
            'name',
            'system_url',
            'group',
            'tenant',
            'system_status',
            'comments',
            'tags',
        )


class SystemBulkEditForm(NetBoxModelBulkEditForm):

    group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(), required=False, null_option='None', initial_params={'tenants': '$tenant'}
    )

    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        query_params={'group_id': '$group'},
    )

    cluster_group = DynamicModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        initial_params={
            'tenant_id': '$tenant',
            'group_id': '$group',
        },
        null_option='None',
        help_text=_("Pin the system to a specific cluster group"),
    )

    cluster = DynamicModelChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'group_id': '$cluster_group',
        },
        help_text=_("Choose a cluster within the selected cluster group that contains the system"),
    )

    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        null_option='None',
        help_text=_("Pin this system to a specific device within the selected cluster"),
    )

    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        null_option='None',
        help_text=_("Pin this system to a specific virtual machine of the selected device"),
    )

    fieldsets = (FieldSet('group', 'tenant', 'cluster_group', 'cluster', 'device', 'virtual_machine'),)

    model = System

    nullable_fields = [
        'cluster',
        'device',
        'virtual_machine',
        'group',
        'tenant',
        'cluster_group',
        'add_tags',
        'remove_tags',
    ]


class SystemFilterForm(NetBoxModelFilterSetForm):
    model = System

    fieldsets = (
        FieldSet('q', 'index', 'tag'),
        FieldSet('system_url', 'system_status'),
        FieldSet('group_id', 'tenant_id', 'cluster_group_id', 'cluster_id', 'device_id', 'virtual_machine_id'),
    )

    index = forms.IntegerField(required=False)

    system_url = forms.CharField(required=False, label=_('URL'))

    system_status = forms.MultipleChoiceField(choices=SystemStatusChoices, required=False, label=_('Status'))

    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'cluster_id': '$cluster_id',
        },
        label=_('Device'),
    )

    virtual_machine_id = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'cluster_id': '$cluster_id',
            'device_id': '$device_id',
        },
        label=_('Virtual Machine'),
    )

    cluster_group_id = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(), required=False, null_option='None', label=_('Cluster Group')
    )

    cluster_id = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        null_option='None',
        query_params={'group_id': '$cluster_group_id'},
        label=_('Cluster'),
    )

    group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(), required=False, null_option='None', label=_('Tenant group')
    )

    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        null_option='None',
        query_params={'group_id': '$group_id'},
        label=_('Tenant'),
    )

    tag = TagFilterField(model)


class SystemCSVForm(NetBoxModelImportForm):

    system_status = CSVChoiceField(
        choices=SystemStatusChoices,
        help_text=_('Status'),
        required=True,
    )

    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
    )

    group = CSVModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        to_field_name='group',
    )

    virtual_machine = CSVModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        to_field_name='name',
    )

    cluster_group = CSVModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        to_field_name='name',
    )

    cluster = CSVModelChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        to_field_name='name',
    )

    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
    )

    class Meta:
        model = System
        fields = [
            'name',
            'system_status',
            'device',
            'group',
            'virtual_machine',
            'cluster_group',
            'cluster',
            'tenant',
            'system_url',
        ]
        default_return_url = 'plugins:adestis_netbox_plugin_account_management:system_list'
