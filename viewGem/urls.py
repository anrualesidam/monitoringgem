from django.urls import path
from . import views
from .views import minitoringGem
urlpatterns = [
    #path('', views.home),
    path('', minitoringGem().cargar_archivo, name='cargar_archivo'),
    path('pdf/', minitoringGem().getpdf, name='generate_pdf'),
    path('searchfilege21/', minitoringGem().searchfilege21, name='searchfilege21'),
    path('upload_file/', minitoringGem().uploaddatabase, name='uploadfile'),
    path('contact/', minitoringGem().contac, name='contact'), 
    #path('', views.mostrar_plot, name='mostrar_imagen'),

]
