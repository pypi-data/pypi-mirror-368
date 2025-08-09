from django.db import models
from django.urls import reverse
from adestis_netbox_plugin_account_management.models.ssh_key import SshKey
from adestis_netbox_plugin_account_management.models.system import System
from netbox.models import NetBoxModel
from utilities.choices import ChoiceSet
from tenancy.models import *

__all__ = (
    'LoginCredentialsStatusChoices',
    'LoginCredentials',
)


class LoginCredentialsStatusChoices(ChoiceSet):
    key = 'LoginCredentials.status'

    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_STAGED = 'staged'
    STATUS_FAILED = 'failed'
    STATUS_INVENTORY = 'inventory'
    STATUS_DECOMMISSIONING = 'decommissioning'

    CHOICES = [
        (STATUS_ACTIVE, 'Active', 'green'),
        (STATUS_OFFLINE, 'Offline', 'gray'),
        (STATUS_PLANNED, 'Planned', 'cyan'),
        (STATUS_STAGED, 'Staged', 'blue'),
        (STATUS_FAILED, 'Failed', 'red'),
        (STATUS_INVENTORY, 'Inventory', 'purple'),
        (STATUS_DECOMMISSIONING, 'Decommissioning', 'yellow'),
    ]


class LoginCredentials(NetBoxModel):

    system = models.ForeignKey(
        to=System,
        on_delete=models.PROTECT,
        null=True,
        verbose_name='System',
        help_text='System that is used by the Contact',
    )

    logon_name = models.CharField(
        max_length=254, verbose_name='Logon name', help_text='Username of the user to login into system'
    )

    valid_from = models.DateField(null=True, blank=True, verbose_name='Valid from', help_text='Start of validity')

    valid_to = models.DateField(null=True, blank=True, verbose_name='Valid to', help_text='End of validity')

    login_credentials_status = models.CharField(
        max_length=50, choices=LoginCredentialsStatusChoices, verbose_name='Status', help_text='Status of the entry'
    )

    contact = models.ForeignKey(
        to='tenancy.Contact',
        on_delete=models.PROTECT,
        related_name='logincredentials_contact',
        null=True,
        verbose_name='Contact',
        help_text='Contact that uses the System',
    )

    comments = models.TextField(blank=True)

    ssh_keys = models.ManyToManyField(
        to=SshKey,
        verbose_name='SSH Keys',
        related_name='logincredentials_sshkey',
        blank=True,
    )

    class Meta:
        verbose_name_plural = "Login Credentials"
        verbose_name = 'Login Credentials'
        ordering = ('contact',)
        constraints = [
            models.UniqueConstraint(
                fields=['system', 'contact', 'logon_name'], name='%(app_label)s_%(class)s_unique_login_credentials'
            )
        ]

    def __str__(self):
        return self.logon_name

    def get_absolute_url(self):
        return reverse('plugins:adestis_netbox_plugin_account_management:logincredentials', args=[self.pk])

    def get_login_credentials_status_color(self):
        return LoginCredentialsStatusChoices.colors.get(self.login_credentials_status)
