import django_tables2 as tables

from netbox.tables import NetBoxTable, ChoiceFieldColumn, columns
from adestis_netbox_plugin_account_management.models import *


class SystemTable(NetBoxTable):
    name = tables.Column(
        linkify=True,
    )

    system_status = ChoiceFieldColumn()

    comments = columns.MarkdownColumn()

    tags = columns.TagColumn()

    device = tables.Column(linkify=True)

    virtual_machine = tables.Column(linkify=True)

    cluster_group = tables.Column(linkify=True)

    cluster = tables.Column(linkify=True)

    tenant = tables.Column(linkify=True)

    group = tables.Column(
        linkify=True,
    )

    class Meta(NetBoxTable.Meta):
        model = System
        fields = (
            'pk',
            'id',
            'device',
            'virtual_machine',
            'cluster_group',
            'cluster',
            'name',
            'system_url',
            'system_status',
            'comments',
            'actions',
            'tags',
            'created',
            'last_updated',
        )
        default_columns = (
            'name',
            'system_url',
            'system_status',
            'tenant',
            'group',
            'cluster',
            'cluster_group',
            'device',
            'virtual_machine',
        )
