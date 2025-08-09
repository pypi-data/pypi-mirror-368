import re
from django import forms
from django.core.exceptions import ValidationError
from adestis_netbox_plugin_account_management.models.ssh_key import SshKey, SshKeyStatusChoices, SshKeyTypeChoices
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm, NetBoxModelBulkEditForm, NetBoxModelImportForm
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    CSVChoiceField,
    CSVModelChoiceField,
    TagFilterField,
)
from utilities.forms.widgets import DatePicker
from tenancy.models import Contact
from django.utils.translation import gettext_lazy as _
from adestis_netbox_plugin_account_management.validators import validate_ssh_key
from tenancy.forms import ContactModelFilterForm
from utilities.forms.rendering import FieldSet

__all__ = ('SshKeyForm', 'SshKeyFilterForm', 'SshKeyBulkEditForm', 'SshKeyCSVForm')


class SshKeyForm(NetBoxModelForm):
    comments = CommentField()

    contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=True,
    )

    fieldsets = (
        FieldSet('raw_ssh_key', 'contact', 'ssh_key_current_status', 'ssh_key_desired_status', 'tags'),
        FieldSet('valid_from', 'valid_to'),
    )

    class Meta:
        model = SshKey
        fields = [
            'raw_ssh_key',
            'key_comment',
            'key_type',
            'encoded_key',
            'contact',
            'valid_from',
            'valid_to',
            'ssh_key_current_status',
            'ssh_key_desired_status',
            'comments',
            'tags',
        ]
        widgets = {
            'valid_from': DatePicker(),
            'valid_to': DatePicker(),
            'key_comment': forms.HiddenInput(),
            'key_type': forms.HiddenInput(),
            'encoded_key': forms.HiddenInput(),
        }
        help_texts = {
            'key_comment': "Logon name",
        }

    def clean(self):

        if self.cleaned_data["raw_ssh_key"]:
            stripped_ssh_key = self.cleaned_data["raw_ssh_key"].strip()

            # check if format is correct
            # the format of the authroized key must contain the protocol, the key but the comment is optional
            ssh_key_pattern = re.compile(
                r'^(ssh-(rsa|dss|ed25519)|ecdsa-sha2-nistp(256|384|521)) ([A-Za-z0-9+/=]+) ?(.*)?$'
            )
            matches = ssh_key_pattern.match(stripped_ssh_key)

            if not matches:
                raise ValidationError("Invalid SSH key format.")

            parsed_key_type = matches.group(1).strip()
            parsed_key_comment = matches.group(5).strip()
            parsed_encoded_key = stripped_ssh_key.replace(parsed_key_type, "").replace(parsed_key_comment, "").strip()

            if not parsed_key_comment:
                parsed_key_comment = ""
                self.cleaned_data["raw_ssh_key"] = f"{parsed_key_type} {parsed_encoded_key}"
            else:
                self.cleaned_data["raw_ssh_key"] = f"{parsed_key_type} {parsed_encoded_key} {parsed_key_comment}"

            if not validate_ssh_key(self.cleaned_data["raw_ssh_key"]):
                raise ValidationError("Invalid SSH key.")

            self.cleaned_data["encoded_key"] = parsed_encoded_key
            self.cleaned_data["key_type"] = parsed_key_type
            self.cleaned_data["key_comment"] = parsed_key_comment

        fieldsToValidate = [field for field in ('valid_from', 'valid_to') if self.cleaned_data[field]]

        shouldValidate = len(fieldsToValidate) == 2

        if shouldValidate == True:
            valid_from_data = self.cleaned_data["valid_from"]
            valid_to_data = self.cleaned_data["valid_to"]
            # Only do something if both fields are valid so far.
            if valid_to_data < valid_from_data:
                raise ValidationError("Invalid date range! Field 'Valid to' must be older than field 'Valid from'")

        super().clean()


class SshKeyBulkEditForm(NetBoxModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=SshKey.objects.all(), widget=forms.MultipleHiddenInput)

    valid_from = forms.DateField(required=False, widget=DatePicker)

    valid_to = forms.DateField(required=False, widget=DatePicker)

    ssh_key_current_status = forms.ChoiceField(required=False, choices=SshKeyStatusChoices, label=_('Status'))

    ssh_key_desired_status = forms.ChoiceField(required=False, choices=SshKeyStatusChoices, label=_('Status'))

    model = SshKey

    fieldsets = (
        ('Validity', ('valid_from', 'valid_to')),
        ('Other', ('ssh_key_current_status', 'ssh_key_desired_status')),
    )

    nullable_fields = ['valid_from', 'valid_to', 'add_tags', 'remove_tags']


class SshKeyFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = SshKey

    fieldsets = (
        FieldSet('q', 'index', 'tag'),
        FieldSet(
            'contact', 'raw_ssh_key', 'key_comment', 'key_type', 'ssh_key_current_status', 'ssh_key_desired_status'
        ),
    )

    key_comment = forms.CharField(required=False, label=_('Comment'))

    index = forms.IntegerField(required=False)

    ssh_key_current_status = forms.MultipleChoiceField(choices=SshKeyStatusChoices, required=False, label=_('Status'))

    ssh_key_desired_status = forms.MultipleChoiceField(choices=SshKeyStatusChoices, required=False, label=_('Status'))

    key_type = forms.MultipleChoiceField(choices=SshKeyTypeChoices, required=False)

    tag = TagFilterField(model)


class SshKeyCSVForm(NetBoxModelImportForm):

    contact = CSVModelChoiceField(
        queryset=Contact.objects.all(), required=False, to_field_name='email', help_text='Email address of the contact'
    )

    ssh_key_current_status = CSVChoiceField(
        choices=SshKeyStatusChoices,
        help_text=_('Status'),
        required=True,
    )

    ssh_key_desired_status = CSVChoiceField(
        choices=SshKeyStatusChoices,
        help_text=_('Status'),
        required=True,
    )

    class Meta:
        model = SshKey
        fields = [
            'contact',
            'raw_ssh_key',
            'key_comment',
            'key_type',
            'encoded_key',
            'valid_from',
            'valid_to',
            'ssh_key_current_status',
            'ssh_key_desired_status',
        ]
        default_return_url = 'plugins:adestis_netbox_plugin_account_management:logincredentials_list'

    def clean(self):

        if self.cleaned_data["raw_ssh_key"]:
            stripped_ssh_key = self.cleaned_data["raw_ssh_key"].strip()

            # check if format is correct
            # the format of the authroized key must contain the protocol, the key but the comment is optional
            ssh_key_pattern = re.compile(
                r'^(ssh-(rsa|dss|ed25519)|ecdsa-sha2-nistp(256|384|521)) ([A-Za-z0-9+/=]+) ?(.*)?$'
            )
            matches = ssh_key_pattern.match(stripped_ssh_key)

            if not matches:
                raise ValidationError("Invalid SSH key format.")

            parsed_key_type = matches.group(1).strip()
            parsed_key_comment = matches.group(5).strip()
            parsed_encoded_key = stripped_ssh_key.replace(parsed_key_type, "").replace(parsed_key_comment, "").strip()

            if not parsed_key_comment:
                parsed_key_comment = ""
                self.cleaned_data["raw_ssh_key"] = f"{parsed_key_type} {parsed_encoded_key}"
            else:
                self.cleaned_data["raw_ssh_key"] = f"{parsed_key_type} {parsed_encoded_key} {parsed_key_comment}"

            if not validate_ssh_key(self.cleaned_data["raw_ssh_key"]):
                raise ValidationError("Invalid SSH key.")

            self.cleaned_data["encoded_key"] = parsed_encoded_key
            self.cleaned_data["key_type"] = parsed_key_type
            self.cleaned_data["key_comment"] = parsed_key_comment

        fieldsToValidate = [field for field in ('valid_from', 'valid_to') if self.cleaned_data[field]]

        shouldValidate = len(fieldsToValidate) == 2

        if shouldValidate == True:
            valid_from_data = self.cleaned_data["valid_from"]
            valid_to_data = self.cleaned_data["valid_to"]
            # Only do something if both fields are valid so far.
            if valid_to_data < valid_from_data:
                raise ValidationError("Invalid date range! Field 'Valid to' must be older than field 'Valid from'")

        super().clean()
