from netbox.views import generic
from adestis_netbox_plugin_account_management.forms import *
from adestis_netbox_plugin_account_management.models import *
from adestis_netbox_plugin_account_management.filtersets import *
from adestis_netbox_plugin_account_management.tables import *

__all__ = (
    'SystemView',
    'SystemListView',
    'SystemEditView',
    'SystemDeleteView',
    'SystemBulkEditView',
    'SystemBulkDeleteView',
    'SystemBulkImportView',
)


class SystemView(generic.ObjectView):
    queryset = System.objects.all()

    def get_extra_context(self, request, instance):
        filtered_data = LoginCredentials.objects.filter(system=instance)

        systemview_filtered_table = LoginCredentialsTable(
            filtered_data,
        )

        return {
            'systemview_filtered_table': systemview_filtered_table,
        }


class SystemListView(generic.ObjectListView):
    queryset = System.objects.all()
    table = SystemTable
    filterset = SystemFilterSet
    filterset_form = SystemFilterForm


class SystemEditView(generic.ObjectEditView):
    queryset = System.objects.all()
    form = SystemForm


class SystemDeleteView(generic.ObjectDeleteView):
    queryset = System.objects.all()


class SystemBulkDeleteView(generic.BulkDeleteView):
    queryset = System.objects.all()
    table = SystemTable


class SystemBulkEditView(generic.BulkEditView):
    queryset = System.objects.all()
    filterset = SystemFilterSet
    table = SystemTable
    form = SystemBulkEditForm


class SystemBulkImportView(generic.BulkImportView):
    queryset = System.objects.all()
    model_form = SystemCSVForm
    table = SystemTable
