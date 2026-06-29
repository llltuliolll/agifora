from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('simular/', views.simulacao_nova, name='simulacao_nova'),
    path('historico/', views.historico, name='historico'),
    path('estabelecimentos/', views.credores_lista, name='credores_lista'),
    path('estabelecimentos/novo/', views.credor_novo, name='credor_novo'),
    path('estabelecimentos/<int:pk>/editar/', views.credor_editar, name='credor_editar'),
    path('estabelecimentos/<int:pk>/', views.credor_detalhe, name='credor_detalhe'),
    path('sobre/', views.sobre, name='sobre'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
