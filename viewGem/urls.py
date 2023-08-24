from django.urls import path
from . import views
from .views import minitoringGem
urlpatterns = [
    #path('', views.home),
    path('', minitoringGem().cargar_archivo, name='cargar_archivo'),
    path('pdf/', minitoringGem().getpdf, name='generate_pdf'),
    path('contact/', minitoringGem().contac, name='contact'), 
    #path('', views.mostrar_plot, name='mostrar_imagen'),

]
