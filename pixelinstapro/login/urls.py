from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/<str:username>/", views.profile_view, name="profile_dynamic"),
    path("profile/<str:username>/follow/", views.follow_user, name="follow_user"),
    path("logout/", views.logout_view, name="logout"),
    path("posts/<int:post_id>/delete/", views.post_delete_view, name="post_delete"),
    path("posts/<int:post_id>/like/", views.like_post, name="post_like"),
    path("posts/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("search/", views.search_users, name="search"),
    path("messages/", views.inbox, name="inbox"),
    path("messages/<str:username>/", views.chat, name="chat"),
    path("notifications/", views.notifications, name="notifications"),
]
