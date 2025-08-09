from adestis_netbox_plugin_account_management.models import LoginCredentials, System
from adestis_netbox_plugin_account_management.models.ssh_key import SshKey
from netbox.filtersets import NetBoxModelFilterSet
from django.db.models import Q
from django import forms
import django_filters
from django.utils.translation import gettext as _
from utilities.forms.fields import DynamicModelMultipleChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.widgets import DatePicker
from tenancy.models import Contact

__all__ = ('LoginCredentialsFilterSet',)


class LoginCredentialsFilterSet(NetBoxModelFilterSet):

    contact_id = DynamicModelMultipleChoiceField(
        queryset=Contact.objects.all(), required=False, null_option='None', label=_('Group')
    )

    contact = DynamicModelMultipleChoiceField(
        queryset=Contact.objects.all(), required=False, null_option='None', label=_('Group')
    )

    valid_from = forms.DateField(required=False, widget=DatePicker)

    valid_to = forms.DateField(required=False, widget=DatePicker)

    system_name = django_filters.ModelMultipleChoiceFilter(
        field_name='system__name',
        queryset=System.objects.all(),
        to_field_name='name',
        label='System (Name)',
        required=False,
    )

    ssh_key_id = django_filters.ModelMultipleChoiceFilter(
        field_name='ssh_keys',
        queryset=SshKey.objects.all(),
        label=_('SSH Key (ID)'),
    )

    class Meta:
        model = LoginCredentials
        fields = [
            'id',
            'logon_name',
            'login_credentials_status',
            'contact',
            'ssh_keys',
            'system',
            'valid_from',
            'valid_to',
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(logon_name__icontains=value)
            | Q(contact__name__icontains=value)
            | Q(login_credentials_status__icontains=value)
            | Q(system__name__icontains=value)
        )
