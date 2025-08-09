import django_tables2 as tables

from netbox.tables import NetBoxTable, ChoiceFieldColumn, columns
from adestis_netbox_plugin_account_management.models import *


class SshKeyTable(NetBoxTable):
    key_comment = tables.Column(linkify=True)

    raw_ssh_key = tables.Column(linkify=True)

    contact = tables.Column(linkify=True)

    ssh_key_current_status = ChoiceFieldColumn()

    ssh_key_desired_status = ChoiceFieldColumn()

    key_type = ChoiceFieldColumn()

    comments = columns.MarkdownColumn()

    tags = columns.TagColumn()

    class Meta(NetBoxTable.Meta):
        model = SshKey
        fields = [
            'pk',
            'id',
            'raw_ssh_key',
            'key_comment',
            'encoded_key',
            'key_type',
            'contact',
            'valid_from',
            'valid_to',
            'ssh_key_desired_status',
            'ssh_key_current_status',
            'comments',
            'actions',
            'tags',
            'created',
            'last_updated',
        ]
        default_columns = [
            'key_comment',
            'contact',
            'ssh_key_desired_status',
            'ssh_key_current_status',
            'valid_from',
            'valid_to',
            'tags',
        ]


class LoginCredentialsSshKeysTable(SshKeyTable):
    actions = columns.ActionsColumn(
        actions=('edit',),
    )

    class Meta(SshKeyTable.Meta):
        fields = (
            'pk',
            'id',
            'raw_ssh_key',
            'key_comment',
            'encoded_key',
            'key_type',
            'contact',
            'valid_from',
            'valid_to',
            'ssh_key_current_status',
            'ssh_key_desired_status',
            'comments',
            'actions',
            'tags',
            'created',
            'last_updated',
        )
        default_columns = (
            'key_comment',
            'contact',
            'ssh_key_current_status',
            'ssh_key_desired_status',
            'valid_from',
            'valid_to',
            'tags',
        )
