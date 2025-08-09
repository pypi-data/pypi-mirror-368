from django.urls import path
from netbox.views.generic import ObjectChangeLogView
from adestis_netbox_plugin_account_management.models import *
from adestis_netbox_plugin_account_management.views import *
from django.urls import include
from utilities.urls import get_model_urls

urlpatterns = (
    # System lists
    path('systems/', SystemListView.as_view(), name='system_list'),
    path('systems/add/', SystemEditView.as_view(), name='system_add'),
    path('systems/delete/', SystemBulkDeleteView.as_view(), name='system_bulk_delete'),
    path('systems/edit/', SystemBulkEditView.as_view(), name='system_bulk_edit'),
    path('systems/import/', SystemBulkImportView.as_view(), name='system_bulk_import'),
    path('systems/<int:pk>/', SystemView.as_view(), name='system'),
    path('systems/<int:pk>/edit/', SystemEditView.as_view(), name='system_edit'),
    path('systems/<int:pk>/delete/', SystemDeleteView.as_view(), name='system_delete'),
    path(
        'systems/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='system_changelog', kwargs={'model': System}
    ),
    # Login Credentials
    path('login-credentials/', LoginCredentialsListView.as_view(),
         name='logincredentials_list'),
    path('login-credentials/add/', LoginCredentialsEditView.as_view(),
         name='logincredentials_add'),
    path('login-credentials/delete/', LoginCredentialsBulkDeleteView.as_view(),
         name='logincredentials_bulk_delete'),
    path('login-credentials/edit/', LoginCredentialsBulkEditView.as_view(),
         name='logincredentials_bulk_edit'),
    path('login-credentials/import/', LoginCredentialsBulkImportView.as_view(),
         name='logincredentials_bulk_import'),
    path('login-credentials/<int:pk>/',
         LoginCredentialsView.as_view(), name='logincredentials'),
    path('login-credentials/<int:pk>/',
         include(get_model_urls("adestis_netbox_plugin_account_management", "logincredentials"))),
    path('login-credentials/<int:pk>/edit/',
         LoginCredentialsEditView.as_view(), name='logincredentials_edit'),
    path('login-credentials/<int:pk>/delete/',
         LoginCredentialsDeleteView.as_view(), name='logincredentials_delete'),
    path('login-credentials/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='logincredentials_changelog', kwargs={
        'model': LoginCredentials
    }),

    # SSH Keys
    path('ssh-keys/', SshKeyListView.as_view(), name='sshkey_list'),
    path('ssh-keys/add/', SshKeyEditView.as_view(), name='sshkey_add'),
    path('ssh-keys/delete/', SshKeyBulkDeleteView.as_view(), name='sshkey_bulk_delete'),
    path('ssh-keys/edit/', SshKeyBulkEditView.as_view(), name='sshkey_bulk_edit'),
    path('ssh-keys/import/', SshKeyBulkImportView.as_view(), name='sshkey_bulk_import'),
    path('ssh-keys/<int:pk>/', SshKeyView.as_view(), name='sshkey'),
    path('ssh-keys/<int:pk>/', include(get_model_urls("adestis_netbox_plugin_account_management", "sshkey"))),
    path('ssh-keys/<int:pk>/edit/', SshKeyEditView.as_view(), name='sshkey_edit'),
    path('ssh-keys/<int:pk>/delete/', SshKeyDeleteView.as_view(), name='sshkey_delete'),
    path(
        'ssh-keys/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='sshkey_changelog', kwargs={'model': SshKey}
    ),
)
