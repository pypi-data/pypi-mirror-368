from adestis_netbox_plugin_account_management.api.serializers.ssh_key_serializer import SshKeySerializer
from ..nested_serializer import *
from rest_framework import serializers
from adestis_netbox_plugin_account_management.models import *
from netbox.api.serializers import NetBoxModelSerializer
from netbox.api.fields import SerializedPKRelatedField
from tenancy.models import *
from tenancy.api.serializers import *
from dcim.api.serializers import *
from dcim.models import *
from virtualization.api.serializers import *


class LoginCredentialsSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:adestis_netbox_plugin_account_management-api:logincredentials-detail'
    )

    system = NestedSystemSerializer(many=False, read_only=False, required=False)

    contact = ContactSerializer(many=False, nested=True, read_only=False, required=False)

    ssh_keys = SerializedPKRelatedField(
        queryset=SshKey.objects.all(), serializer=SshKeySerializer, nested=True, required=False, many=True
    )

    class Meta:
        model = LoginCredentials
        fields = (
            'id',
            'tags',
            'custom_fields',
            'display',
            'url',
            'system',
            'ssh_keys',
            'contact',
            'created',
            'last_updated',
            'custom_field_data',
            'logon_name',
            'valid_from',
            'valid_to',
            'login_credentials_status',
            'comments',
        )
        brief_fields = (
            'id',
            'tags',
            'custom_fields',
            'display',
            'url',
            'system',
            'ssh_keys',
            'contact',
            'created',
            'last_updated',
            'custom_field_data',
            'logon_name',
            'valid_from',
            'valid_to',
            'login_credentials_status',
            'comments',
        )
