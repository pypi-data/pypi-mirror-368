import django_tables2 as tables

from netbox.tables import NetBoxTable, ChoiceFieldColumn, columns
from adestis_netbox_plugin_account_management.models import *


class LoginCredentialsTable(NetBoxTable):
    logon_name = tables.Column(linkify=True)

    contact = tables.Column(linkify=True)

    system = tables.Column(linkify=True)

    login_credentials_status = ChoiceFieldColumn()

    comments = columns.MarkdownColumn()

    tags = columns.TagColumn()

    ssh_keys = columns.ManyToManyColumn(linkify_item=True, verbose_name='SSH Keys')

    class Meta(NetBoxTable.Meta):
        model = LoginCredentials
        fields = [
            'pk',
            'id',
            'logon_name',
            'contact',
            'ssh_keys',
            'system',
            'valid_from',
            'valid_to',
            'login_credentials_status',
            'comments',
            'actions',
            'tags',
            'created',
            'last_updated',
        ]
        default_columns = [
            'logon_name',
            'contact',
            'system',
            'ssh_keys',
            'valid_from',
            'valid_to',
            'login_credentials_status',
            'tags',
        ]


class SshKeyLoginCredentialsTable(LoginCredentialsTable):
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
    )

    class Meta(LoginCredentialsTable.Meta):
        fields = (
            'pk',
            'id',
            'logon_name',
            'contact',
            'ssh_keys',
            'system',
            'valid_from',
            'valid_to',
            'login_credentials_status',
            'comments',
            'actions',
            'tags',
            'created',
            'last_updated',
        )
        default_columns = (
            'logon_name',
            'contact',
            'system',
            'ssh_keys',
            'valid_from',
            'valid_to',
            'login_credentials_status',
            'tags',
        )
