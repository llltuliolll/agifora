from django.urls import path
from . import views

app_name = 'auditoria'

urlpatterns = [
    path('calcular/<int:pk>/', views.calcular, name='calcular'),
    path('resultado/<int:pk>/', views.resultado, name='resultado'),
    path('mapa/', views.mapa, name='mapa'),
]
