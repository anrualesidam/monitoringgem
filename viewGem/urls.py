from django.urls import path
from . import views
from .views import minitoringGem
urlpatterns = [
    #path('', views.home),
    path('', minitoringGem().cargar_archivo, name='cargar_archivo'),
    path('pdf/', minitoringGem().generate_pdf, name='generate_pdf'),
    #path('', views.mostrar_plot, name='mostrar_imagen'),

]
