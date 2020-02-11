from django.urls import path

from . import views

app_name = 'saml2_mdq'


urlpatterns = [
    path('entities/', views.saml2_entities, name='saml2_entities'),
    path('entities/<path:entity>', views.saml2_entity, name='saml2_entity'),
]
