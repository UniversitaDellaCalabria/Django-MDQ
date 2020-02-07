from django.conf import settings
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
]

if 'saml2_mdq' in settings.INSTALLED_APPS:
    import saml2_mdq.urls
    urlpatterns += path('', include((saml2_mdq.urls, 'saml2_mdq',))),
