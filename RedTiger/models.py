from django.db import models

# Create your models here.
class Hello(models.Model):
    id = models.IntegerField(default=0, primary_key=True)
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text

class Order(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)