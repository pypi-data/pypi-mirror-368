from adestis_netbox_plugin_account_management.validators.ssh import validate_ssh_key
from ..nested_serializer import *
from rest_framework import serializers
from django.core.exceptions import ValidationError
from adestis_netbox_plugin_account_management.models import *
from netbox.api.serializers import NetBoxModelSerializer
from netbox.api.fields import ChoiceField
from tenancy.models import *
from tenancy.api.serializers import *
from dcim.api.serializers import *
from dcim.models import *
from virtualization.api.serializers import *
import re


class SshKeySerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:adestis_netbox_plugin_account_management-api:logincredentials-detail'
    )

    contact = ContactSerializer(many=False, nested=True, read_only=False, required=True)

    encoded_key = serializers.CharField(required=False, default=None, allow_null=True)

    key_type = ChoiceField(choices=SshKeyTypeChoices, allow_blank=True, allow_null=True, required=False)

    valid_from = serializers.DateField(required=False, allow_null=True)
    valid_to = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = SshKey
        fields = (
            'id',
            'tags',
            'custom_fields',
            'display',
            'url',
            'raw_ssh_key',
            'key_comment',
            'ssh_key_current_status',
            'ssh_key_desired_status',
            'encoded_key',
            'key_type',
            'contact',
            'created',
            'last_updated',
            'custom_field_data',
            'valid_from',
            'valid_to',
            'comments',
        )
        brief_fields = (
            'id',
            'tags',
            'display',
            'url',
            'raw_ssh_key',
            'key_comment',
            'ssh_key_current_status',
            'ssh_key_desired_status',
            'encoded_key',
            'key_type',
            'contact',
            'created',
            'last_updated',
            'custom_field_data',
            'valid_from',
            'valid_to',
            'comments',
        )

    def validate(self, data):
        if data["raw_ssh_key"]:
            stripped_ssh_key = data["raw_ssh_key"].strip()

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
                data["raw_ssh_key"] = f"{parsed_key_type} {parsed_encoded_key}"
            else:
                data["raw_ssh_key"] = f"{parsed_key_type} {parsed_encoded_key} {parsed_key_comment}"

            if not validate_ssh_key(data["raw_ssh_key"]):
                raise ValidationError("Invalid SSH key.")

            data["encoded_key"] = parsed_encoded_key
            data["key_type"] = parsed_key_type
            data["key_comment"] = parsed_key_comment

        shouldValidate = False

        if 'valid_from' in data and 'valid_to' in data:
            shouldValidate = True

        if shouldValidate == True:
            valid_from_data = data["valid_from"]
            valid_to_data = data["valid_to"]
            # Only do something if both fields are valid so far.
            if valid_to_data < valid_from_data:
                raise ValidationError("Invalid date range! Field 'Valid to' must be older than field 'Valid from'")

        return super().validate(data)
