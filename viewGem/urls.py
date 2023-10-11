from django.urls import path
from . import views
from .views import minitoringGem,minitoringLogin,Home
urlpatterns = [
    #path('', views.home),
    path('', minitoringLogin().login, name="baselogin"),
    path('contactin/', Home().contactin, name='contactin'),
    path('cargar_archivo/', minitoringGem().cargar_archivo, name='cargar_archivo'),
    path('pdf/', minitoringGem().getpdf, name='generate_pdf'),
    path('searchfilege21/', minitoringGem().searchfilege21, name='searchfilege21'),
    path('upload_file/', minitoringGem().uploaddatabase, name='uploadfile'),
    path('contact/', minitoringGem().contac, name='contact'), 
    #path('', views.mostrar_plot, name='mostrar_imagen'),

]
