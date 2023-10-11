from django.db import models
from .managers import CustomUserManager
from django.contrib.auth.models import AbstractUser


# Create your models here.

class CustomUser(AbstractUser):
    # Your custom fields go here
    objects = CustomUserManager()

class MiTabla(models.Model):
    
    name_rbo=models.CharField(max_length=250)
    info_rbo=models.CharField(max_length=250)
    fechas=models.DateTimeField()
    
    def __str__(self):
        return self.name_rbo
    
    class Meta:
        db_table = 'robdb'

    #class Meta:
        # Especifica la base de datos a la que pertenece este modelo
     #   db_table = 'files_rob_db'  # Cambia 'miapp' por el nombre de tu aplicación
      #  managed = True  # Usa el nombre de la segunda base de datos configurada