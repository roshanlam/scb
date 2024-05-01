from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=(('student', 'Student'), ('teacher', 'Teacher')))
    classes = models.ManyToManyField('Class', related_name='students', blank=True)

    # Specify unique related_name arguments for groups and user_permissions
    groups = models.ManyToManyField('auth.Group', related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='customuser_set', blank=True)

class Class(models.Model):
    class_code = models.IntegerField(unique=True)
    class_name = models.CharField(max_length=15, default='')
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='classes_taught')
    
class Post(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    class_field = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sub_posts = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='parent_post')

class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reply_users')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
