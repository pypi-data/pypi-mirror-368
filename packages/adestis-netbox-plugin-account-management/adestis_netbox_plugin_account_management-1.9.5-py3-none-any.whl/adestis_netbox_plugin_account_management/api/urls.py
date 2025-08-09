from netbox.api.routers import NetBoxRouter
from . import views

app_name = 'adestis_netbox_plugin_account_management'

router = NetBoxRouter()
router.register('systems', views.SystemListViewSet)
router.register('login-credentials', views.LoginCredentialsViewSet)
router.register('ssh-keys', views.SshKeyViewSet)

urlpatterns = router.urls
