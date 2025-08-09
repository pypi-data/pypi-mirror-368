from django import forms
from django.core.exceptions import ValidationError
from adestis_netbox_plugin_account_management.models.ssh_key import SshKey
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm, NetBoxModelBulkEditForm, NetBoxModelImportForm
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    CSVModelMultipleChoiceField,
    CSVChoiceField,
    CSVModelChoiceField,
    TagFilterField,
)
from utilities.forms.widgets import DatePicker
from adestis_netbox_plugin_account_management.models.login_credentials import (
    LoginCredentials,
    LoginCredentialsStatusChoices,
)
from adestis_netbox_plugin_account_management.models.system import System
from tenancy.models import Contact
from django.utils.translation import gettext_lazy as _
from extras.models import Tag
from tenancy.forms import ContactModelFilterForm
from utilities.forms import ConfirmationForm
from utilities.forms.rendering import FieldSet

__all__ = (
    'LoginCredentialsForm',
    'LoginCredentialsFilterForm',
    'LoginCredentialsBulkEditForm',
    'LoginCredentialsCSVForm',
    'LoginCredentialsAssignSshKeyForm',
    'LoginCredentialWithSelectedSshKeyForm',
    'LoginCredentialsRemoveSshKeys',
)


class LoginCredentialsForm(NetBoxModelForm):
    comments = CommentField()

    contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=True,
    )

    system = DynamicModelChoiceField(
        queryset=System.objects.all(),
        required=True,
    )

    fieldsets = (
        FieldSet('logon_name', 'contact', 'system', 'login_credentials_status', 'tags'),
        FieldSet('valid_from', 'valid_to'),
    )

    class Meta:
        model = LoginCredentials
        fields = [
            'logon_name',
            'contact',
            'system',
            'valid_from',
            'valid_to',
            'login_credentials_status',
            'comments',
            'tags',
        ]
        widgets = {'valid_from': DatePicker(), 'valid_to': DatePicker()}
        help_texts = {
            'logon_name': "Logon name",
        }

    def clean(self):
        super().clean()

        fieldsToValidate = [field for field in ('valid_from', 'valid_to') if self.cleaned_data[field]]

        shouldValidate = len(fieldsToValidate) == 2

        if shouldValidate == True:
            valid_from_data = self.cleaned_data["valid_from"]
            valid_to_data = self.cleaned_data["valid_to"]
            # Only do something if both fields are valid so far.
            if valid_to_data < valid_from_data:
                raise ValidationError("Invalid date range! Field 'Valid to' must be older than field 'Valid from'")


class LoginCredentialsBulkEditForm(NetBoxModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=LoginCredentials.objects.all(), widget=forms.MultipleHiddenInput)

    system = DynamicModelChoiceField(queryset=System.objects.all(), required=False)

    contact = DynamicModelChoiceField(queryset=Contact.objects.all(), required=False)

    logon_name = forms.CharField(max_length=254, required=False)

    valid_from = forms.DateField(required=False)

    valid_to = forms.DateField(required=False)

    login_credentials_status = forms.ChoiceField(
        required=False,
        choices=LoginCredentialsStatusChoices,
    )

    ssh_keys = DynamicModelMultipleChoiceField(
        queryset=SshKey.objects.all(),
        label=_('SSH Keys'),
        to_field_name='key_comment',
        null_option='None',
        required=False,
    )

    model = LoginCredentials

    fieldsets = (
        FieldSet('logon_name', 'contact', 'system', 'ssh_keys', 'login_credentials_status'),
        FieldSet('valid_from', 'valid_to'),
    )

    nullable_fields = ['valid_from', 'valid_to', 'add_tags', 'remove_tags']


class LoginCredentialsFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):

    model = LoginCredentials

    fieldsets = (
        FieldSet('q', 'index', 'tag'),
        FieldSet('contact', 'system', 'login_credentials_status'),
    )

    index = forms.IntegerField(required=False)

    system = forms.ModelMultipleChoiceField(queryset=System.objects.all(), required=False)

    login_credentials_status = forms.MultipleChoiceField(
        choices=LoginCredentialsStatusChoices, required=False, label=_('Status')
    )

    tag = TagFilterField(model)


class LoginCredentialsCSVForm(NetBoxModelImportForm):

    system = CSVModelChoiceField(
        queryset=System.objects.all(), required=True, to_field_name='system_url', help_text='System URL'
    )

    contact = CSVModelChoiceField(
        queryset=Contact.objects.all(), required=True, to_field_name='email', help_text='Email address of the contact'
    )

    login_credentials_status = CSVChoiceField(
        choices=LoginCredentialsStatusChoices,
        help_text=_('Status'),
        required=True,
    )

    ssh_keys = CSVModelMultipleChoiceField(
        label=_('SSH Keys'),
        queryset=SshKey.objects.all(),
        required=False,
        to_field_name='key_comment',
        help_text=_('SSH Keys'),
    )

    class Meta:
        model = LoginCredentials
        fields = ['system', 'contact', 'ssh_keys', 'login_credentials_status', 'logon_name']
        default_return_url = 'plugins:adestis_netbox_plugin_account_management:logincredentials_list'


class LoginCredentialsAssignSshKeyForm(forms.Form):

    contact = DynamicModelChoiceField(queryset=Contact.objects.all(), required=True, label=_('Owner of the SSH Key'))

    sshkeys = DynamicModelMultipleChoiceField(
        label=_('SSH Keys'),
        queryset=SshKey.objects.prefetch_related('contact'),
        query_params={
            'contact': '$contact',
        },
    )

    class Meta:
        fields = [
            'sshkeys',
        ]

    def __init__(self, loginCredentials, contact, *args, **kwargs):

        self.loginCredentials = loginCredentials

        self.contact = DynamicModelChoiceField(
            queryset=Contact.objects.all(),
            required=False,
            label=_('Region'),
            initial=contact,
        )

        self.sshkeys = DynamicModelMultipleChoiceField(
            label=_('SSH Keys'),
            queryset=SshKey.objects.prefetch_related('contact'),
            query_params={
                'contact_id': '$contact_id',
            },
        )

        super().__init__(*args, **kwargs)

        self.fields['sshkeys'].choices = []


class LoginCredentialWithSelectedSshKeyForm(forms.Form):

    valid_from = forms.DateField(required=False, widget=DatePicker)

    valid_to = forms.DateField(required=False, widget=DatePicker)

    sshkeys = DynamicModelMultipleChoiceField(label=_('SSH Keys'), queryset=SshKey.objects.all(), disabled=True)

    logon_name = forms.CharField(max_length=254, required=True, label=_('Logon name'))

    comments = CommentField()

    contact = DynamicModelChoiceField(queryset=Contact.objects.all(), required=True, disabled=True)

    system = DynamicModelChoiceField(
        queryset=System.objects.all(),
        required=True,
    )

    login_credentials_status = forms.ChoiceField(
        label=_('Status'),
        choices=LoginCredentialsStatusChoices,
        required=True,
    )

    tags = DynamicModelMultipleChoiceField(label=_('Tags'), queryset=Tag.objects.all(), required=False)

    fieldsets = (
        FieldSet('logon_name', 'contact', 'ssh_keys', 'system', 'login_credentials_status', 'tags'),
        FieldSet('valid_from', 'valid_to'),
    )

    class Meta:
        fields = [
            'sshkeys',
            'logon_name',
            'system',
            'contact',
            'login_credentials_status',
            'valid_from',
            'valid_to',
            'tags',
        ]
        help_texts = {
            'logon_name': "Logon name",
        }

    def __init__(self, sshkey, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sshkeys'].initial = [sshkey]
        self.fields['contact'].initial = sshkey.contact

    def clean(self):
        super().clean()

        fieldsToValidate = [field for field in ('valid_from', 'valid_to') if self.cleaned_data[field]]

        shouldValidate = len(fieldsToValidate) == 2

        if shouldValidate == True:
            valid_from_data = self.cleaned_data["valid_from"]
            valid_to_data = self.cleaned_data["valid_to"]
            # Only do something if both fields are valid so far.
            if valid_to_data < valid_from_data:
                raise ValidationError("Invalid date range! Field 'Valid to' must be older than field 'Valid from'")


class LoginCredentialsRemoveSshKeys(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(queryset=SshKey.objects.all(), widget=forms.MultipleHiddenInput())
