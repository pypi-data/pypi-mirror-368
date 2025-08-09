from netbox.views import generic
from adestis_netbox_plugin_account_management.forms import *
from adestis_netbox_plugin_account_management.models import *
from adestis_netbox_plugin_account_management.filtersets import *
from adestis_netbox_plugin_account_management.tables import *
from tenancy.models import Contact

from netbox.views import generic
from utilities.views import ViewTab, register_model_view

__all__ = (
    'SshKeyView',
    'SshKeyListView',
    'SshKeyEditView',
    'SshKeyDeleteView',
    'SshKeyBulkDeleteView',
    'SshKeyBulkEditView',
    'SshKeyBulkImportView',
    'ContactSshKeys',
)


class SshKeyView(generic.ObjectView):
    queryset = SshKey.objects.all()


class SshKeyListView(generic.ObjectListView):
    queryset = SshKey.objects.all()
    table = SshKeyTable
    filterset = SshKeyFilterSet
    filterset_form = SshKeyFilterForm


class SshKeyEditView(generic.ObjectEditView):
    queryset = SshKey.objects.all()
    form = SshKeyForm


class SshKeyDeleteView(generic.ObjectDeleteView):
    queryset = SshKey.objects.all()


class SshKeyBulkDeleteView(generic.BulkDeleteView):
    queryset = SshKey.objects.all()
    table = SshKeyTable


class SshKeyBulkEditView(generic.BulkEditView):
    queryset = SshKey.objects.all()
    filterset = SshKeyFilterSet
    table = SshKeyTable
    form = SshKeyBulkEditForm


class SshKeyBulkImportView(generic.BulkImportView):
    queryset = SshKey.objects.all()
    model_form = SshKeyCSVForm
    table = SshKeyTable


@register_model_view(Contact, 'ssh-keys')
class ContactSshKeys(generic.ObjectChildrenView):

    queryset = Contact.objects.all()
    child_model = SshKey
    table = SshKeyTable
    filterset = SshKeyFilterSet
    filterset_form = SshKeyFilterForm
    template_name = "adestis_netbox_plugin_account_management/contacts/contact_ssh_keys.html"
    actions = {
        'add': {'add'},
        'import': {'add'},
        'export': {'view'},
    }

    tab = ViewTab(
        label='SSH Keys',
        badge=None,
        hide_if_empty=False,
    )

    def get_children(self, request, parent):
        return SshKey.objects.restrict(request.user, 'view').filter(contact=parent)


@register_model_view(SshKey, 'login-credentials')
class SshKeyLoginCredentialsView(generic.ObjectChildrenView):

    queryset = SshKey.objects.all()
    child_model = SshKey
    table = SshKeyLoginCredentialsTable
    filterset = LoginCredentialsFilterSet
    filterset_form = LoginCredentialsFilterForm
    template_name = 'adestis_netbox_plugin_account_management/ssh_keys/login_credentials.html'
    actions = {
        'add': {'add'},
        'import': {'add'},
        'export': {'view'},
    }
    tab = ViewTab(label='Login Credentials', badge=None, hide_if_empty=False)

    def get_children(self, request, parent):
        return LoginCredentials.objects.filter(ssh_keys__id=parent.id)
