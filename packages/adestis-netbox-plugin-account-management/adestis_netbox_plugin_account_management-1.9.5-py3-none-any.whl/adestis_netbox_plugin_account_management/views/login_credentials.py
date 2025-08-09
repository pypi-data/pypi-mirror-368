from netbox.views import generic
from adestis_netbox_plugin_account_management.forms import *
from adestis_netbox_plugin_account_management.models import *
from adestis_netbox_plugin_account_management.filtersets import *
from adestis_netbox_plugin_account_management.tables import *
from tenancy.models import Contact
from utilities.views import ViewTab, register_model_view
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.db import transaction
from django.db.models import Q
from django.contrib import messages

__all__ = (
    'LoginCredentialsView',
    'LoginCredentialsListView',
    'LoginCredentialsEditView',
    'LoginCredentialsDeleteView',
    'ContactLoginCredentials',
    'LoginCredentialsBulkDeleteView',
    'LoginCredentialsBulkEditView',
    'LoginCredentialsBulkImportView',
    'LoginCredentialsAssignSshKey',
    'LoginCredentialsSshKeysView',
)


class LoginCredentialsView(generic.ObjectView):
    queryset = LoginCredentials.objects.all()


class LoginCredentialsListView(generic.ObjectListView):
    queryset = LoginCredentials.objects.all()
    table = LoginCredentialsTable
    filterset = LoginCredentialsFilterSet
    filterset_form = LoginCredentialsFilterForm


class LoginCredentialsEditView(generic.ObjectEditView):
    queryset = LoginCredentials.objects.all()
    form = LoginCredentialsForm


class LoginCredentialsDeleteView(generic.ObjectDeleteView):
    queryset = LoginCredentials.objects.all()


@register_model_view(Contact, name='login-credentials')
class ContactLoginCredentials(generic.ObjectChildrenView):

    queryset = Contact.objects.all()
    child_model = LoginCredentials
    table = LoginCredentialsTable
    filterset = LoginCredentialsFilterSet
    filterset_form = LoginCredentialsFilterForm
    template_name = "adestis_netbox_plugin_account_management/contacts/contact_login_credentials.html"
    actions = {
        'add': {'add'},
        'import': {'add'},
        'export': {'view'},
    }
    tab = ViewTab(label='Login Credentials', badge=None, hide_if_empty=False)

    def get_children(self, request, parent):
        return LoginCredentials.objects.restrict(request.user, 'view').filter(contact=parent)


class LoginCredentialsBulkDeleteView(generic.BulkDeleteView):
    queryset = LoginCredentials.objects.all()
    table = LoginCredentialsTable


class LoginCredentialsBulkEditView(generic.BulkEditView):
    queryset = LoginCredentials.objects.all()
    filterset = LoginCredentialsFilterSet
    table = LoginCredentialsTable
    form = LoginCredentialsBulkEditForm


class LoginCredentialsBulkImportView(generic.BulkImportView):
    queryset = LoginCredentials.objects.all()
    model_form = LoginCredentialsCSVForm
    table = LoginCredentialsTable


@register_model_view(LoginCredentials, 'assign_ssh_key')
class LoginCredentialsAssignSshKey(generic.ObjectEditView):
    contactQuerySet = Contact.objects.all()
    queryset = LoginCredentials.objects.prefetch_related(
        'ssh_keys', 'tags', 'contact').all()

    form = LoginCredentialsAssignSshKeyForm
    template_name = 'adestis_netbox_plugin_account_management/login_credentials/assign_ssh_key.html'

    def get(self, request, pk):
        loginCredentials = get_object_or_404(self.queryset, pk=pk)
        contact = get_object_or_404(
            self.contactQuerySet, pk=loginCredentials.contact.id)
        form = self.form(loginCredentials, contact, initial=request.GET)

        return render(
            request,
            self.template_name,
            {
                'loginCredentials': loginCredentials,
                'contact': contact,
                'form': form,
                'return_url': reverse(
                    'plugins:adestis_netbox_plugin_account_management:logincredentials', kwargs={'pk': pk}
                ),
                'edit_url': reverse(
                    'plugins:adestis_netbox_plugin_account_management:logincredentials_assign_ssh_key',
                    kwargs={'pk': pk},
                ),
            },
        )

    def post(self, request, pk):
        loginCredentials = get_object_or_404(self.queryset, pk=pk)
        contact = get_object_or_404(
            self.contactQuerySet, pk=loginCredentials.contact.id)
        form = self.form(loginCredentials, contact, request.POST)

        if form.is_valid():

            device_pks = form.cleaned_data['sshkeys']
            with transaction.atomic():

                # Assign the selected Devices to the Cluster
                for sshKey in SshKey.objects.filter(pk__in=device_pks):
                    loginCredentials.ssh_keys.add(sshKey)

            loginCredentials.save()

            return redirect(loginCredentials.get_absolute_url())

        return render(
            request,
            self.template_name,
            {
                'loginCredentials': loginCredentials,
                'form': form,
                'return_url': loginCredentials.get_absolute_url(),
                'edit_url': reverse(
                    'plugins:adestis_netbox_plugin_account_management:logincredentials_assign_ssh_key',
                    kwargs={'pk': pk},
                ),
            },
        )


@register_model_view(SshKey, 'new_login_credential')
class LoginCredentialWithSelectedSshKeyEdit(generic.ObjectEditView):
    queryset = SshKey.objects.prefetch_related('tags', 'contact').all()

    form = LoginCredentialWithSelectedSshKeyForm
    template_name = 'adestis_netbox_plugin_account_management/ssh_keys/new_login_credential.html'

    def get(self, request, pk):
        sshKey = get_object_or_404(self.queryset, pk=pk)
        form = self.form(sshKey, initial=request.GET)

        return render(
            request,
            self.template_name,
            {
                'sshkey': sshKey,
                'form': form,
                'return_url': reverse('plugins:adestis_netbox_plugin_account_management:sshkey', kwargs={'pk': pk}),
                'edit_url': reverse(
                    'plugins:adestis_netbox_plugin_account_management:sshkey_new_login_credential', kwargs={'pk': pk}
                ),
            },
        )

    def post(self, request, pk):
        ssh_key = get_object_or_404(self.queryset, pk=pk)
        form = self.form(ssh_key, request.POST)

        # save a new login credential
        if form.is_valid() and ssh_key:

            # add a login credential
            login_credentials = LoginCredentials()
            login_credentials.logon_name = form.cleaned_data['logon_name']
            login_credentials.contact = form.cleaned_data['contact']
            login_credentials.system = form.cleaned_data['system']
            login_credentials.login_credentials_status = form.cleaned_data[
                'login_credentials_status']
            login_credentials.valid_from = form.cleaned_data['valid_from']
            login_credentials.valid_to = form.cleaned_data['valid_to']
            login_credentials.tags = form.cleaned_data['tags']
            login_credentials.save()

            # try to assign the login credenial
            login_credentials.ssh_keys.add(ssh_key)
            login_credentials.save()

            return redirect(login_credentials.get_absolute_url())

        return render(
            request,
            self.template_name,
            {
                'sshkey': ssh_key,
                'form': form,
                'return_url': ssh_key.get_absolute_url(),
                'edit_url': reverse(
                    'plugins:adestis_netbox_plugin_account_management:sshkey_new_login_credential', kwargs={'pk': pk}
                ),
            },
        )


@register_model_view(LoginCredentials, 'ssh_keys')
class LoginCredentialsSshKeysView(generic.ObjectChildrenView):
    queryset = LoginCredentials.objects.all()
    child_model = LoginCredentials
    table = LoginCredentialsSshKeysTable
    filterset = SshKeyFilterSet
    filterset_form = SshKeyFilterForm
    template_name = 'adestis_netbox_plugin_account_management/login_credentials/ssh_keys.html'
    actions = {
        'add': {'add'},
        'import': {'add'},
        'export': {'view'},
        'bulk_remove_ssh_keys': {'change'},
    }

    tab = ViewTab(label='SSH Keys', badge=None, hide_if_empty=False)

    def get_children(self, request, parent):
        return parent.ssh_keys.all()


@register_model_view(LoginCredentials, 'remove_ssh_keys', path='ssh-keys/remove')
class LoginCredentialsRemoveSshKeysView(generic.ObjectEditView):
    queryset = LoginCredentials.objects.all()
    form = LoginCredentialsRemoveSshKeys
    template_name = 'generic/bulk_remove.html'

    def post(self, request, pk):

        login_credentials = get_object_or_404(self.queryset, pk=pk)

        if '_confirm' in request.POST:
            form = self.form(request.POST)

            if form.is_valid():
                ssh_key_pks = form.cleaned_data['pk']
                with transaction.atomic():
                    login_credentials.ssh_keys.remove(*ssh_key_pks)
                    login_credentials.save()

                messages.success(
                    request,
                    _("Removed {count} ssh keys from login credentials {login_credentials}").format(
                        count=len(ssh_key_pks), login_credentials=login_credentials
                    ),
                )
                return redirect(login_credentials.get_absolute_url())
        else:
            form = self.form(initial={'pk': request.POST.getlist('pk')})

        selected_objects = SshKey.objects.filter(
            contact=login_credentials.contact)
        ssh_keys_table = LoginCredentialsSshKeysTable(
            list(selected_objects), orderable=False)

        return render(
            request,
            self.template_name,
            {
                'form': form,
                'parent_obj': login_credentials,
                'table': ssh_keys_table,
                'obj_type_plural': 'ssh keys',
                'return_url': login_credentials.get_absolute_url(),
            },
        )
