from adestis_netbox_plugin_account_management.models import LoginCredentials, System, SshKey
from adestis_netbox_plugin_account_management.filtersets import *
from netbox.api.viewsets import NetBoxModelViewSet
from .serializers import LoginCredentialsSerializer, SystemSerializer, SshKeySerializer


class LoginCredentialsViewSet(NetBoxModelViewSet):
    queryset = LoginCredentials.objects.prefetch_related('tags', 'contact', 'system')

    serializer_class = LoginCredentialsSerializer
    filterset_class = LoginCredentialsFilterSet


class SystemListViewSet(NetBoxModelViewSet):
    queryset = System.objects.prefetch_related('tags')

    serializer_class = SystemSerializer
    filterset_class = SystemFilterSet


class SshKeyViewSet(NetBoxModelViewSet):
    queryset = SshKey.objects.prefetch_related('tags', 'contact')

    serializer_class = SshKeySerializer
    filterset_class = SshKeyFilterSet
