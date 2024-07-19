from django.db import models


# Create your models here.

class Account(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    balance = models.FloatField()
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
