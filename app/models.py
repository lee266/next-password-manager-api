from django.db import models

# Create your models here.
class User(models.Model):
  name = models.CharField(max_length=255)
  email = models.EmailField()
  password = models.CharField(max_length=255)
  created_at = models.DateField(auto_now_add=True)
  
  def __str__(self):
    return self.name

class Message(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  Message = models.TextField(max_length=10000)
  created_at = models.DateField(auto_now_add=True)
  
  def __str__(self):
    return self.Message


