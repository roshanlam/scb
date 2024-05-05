from django.urls import path
from . import views

urlpatterns = [
    path('sign-out/<str:session_id>/', views.sign_out, name='sign_out'),   # URL for sign-out
    path('auth-receiver', views.auth_receiver, name='auth_receiver'),   # URL for sign-in
    path('post-to-forum/', views.post_to_forum, name='post_to_forum'),  # URL for creating a post
    path('get-all-posts/', views.get_all_posts, name='get_all_posts'),  # URL for getting all posts with a specific class name
    path('enroll-in-class/', views.enroll_in_class, name='enroll_in_class'),  # URL for enrolling in a class
    path('get-enrolled-classes/', views.get_enrolled_classes, name='get_enrolled_classes'),  # URL for enrolling in a class
    path('create-new-class/', views.create_new_class, name='create_new_class'),  # URL for creating a class
    path('post-comment-to-forum/', views.post_comment_to_forum, name='post_comment_to_forum'),  # URL for posting a comment
    path('get-post-comments/', views.get_post_comments, name='get_post_comments'),  # URL for retrieving post comments
    path('get-user-points/', views.get_user_points, name='get_user_points'),  # URL for retrieving user points
    path('update-user-points/', views.update_user_points, name='update_user_points'),  # URL for adding/removing user points
    path('post-class-video/', views.post_class_video, name='post_class_video'), # URL for posting video and generating questions
    path('get-class-video-list/', views.get_class_video_list, name='get_class_video_list'), # URL for getting video list from class
]