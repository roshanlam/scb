from django.urls import path
from . import views

urlpatterns = [
    path('sign-out/<str:session_id>/', views.sign_out, name='sign_out'),
    path('auth-receiver', views.auth_receiver, name='auth_receiver'),
    path('post-to-forum/', views.post_to_forum, name='post_to_forum'),  # URL for creating a post
    path('get-all-posts/', views.get_all_posts, name='get_all_posts'),  # URL for getting all posts with a specific class name
    path('enroll-in-class/', views.enroll_in_class, name='enroll_in_class'),  # URL for enrolling in a class
    path('get-enrolled-classes/', views.get_enrolled_classes, name='get_enrolled_classes'),  # URL for enrolling in a class
    path('create-new-class/', views.create_new_class, name='create_new_class'),  # URL for creating a class
]
