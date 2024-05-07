from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=(
        ('student', 'Student'), ('teacher', 'Teacher')))
    classes = models.ManyToManyField(
        'Class', related_name='students', blank=True)
    points = models.IntegerField(default=0)

    # Specify unique related_name arguments for groups and user_permissions
    groups = models.ManyToManyField(
        'auth.Group', related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(
        'auth.Permission', related_name='customuser_set', blank=True)
    
class Class(models.Model):
    class_code = models.IntegerField(unique=True)
    class_name = models.CharField(max_length=15, default='')
    teacher = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='classes_taught')
    videos = models.ManyToManyField('Video', related_name='classes', blank=True)

class Post(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='posts')
    class_field = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name='class_posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sub_posts = models.ManyToManyField(
        'self', blank=True, symmetrical=False, related_name='parent_post')

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Video(models.Model):
    video_link = models.URLField()
    title = models.CharField(max_length=255)
    class_field = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name='class_videos')
    video_questions = models.ManyToManyField('VideoQuestion', related_name='videos', blank=True)

class VideoQuestion(models.Model):
    question = models.CharField(max_length=255)
    answers = models.JSONField()  # Store list of strings as JSON
    correct_answer_index = models.PositiveSmallIntegerField()