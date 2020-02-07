from django.urls import path

from . import views

app_name = 'saml2_mdq'


urlpatterns = [
    path('entities/<path:entity>', views.saml2_entity, name='saml2_entity'),
]
