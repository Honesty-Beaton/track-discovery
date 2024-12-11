from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.startGame, name='startGame'), #Default route
    path('play/<int:session_id>/', views.playGame, name='play'),
    path('results/<int:session_id>/', views.results, name='results'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('spotify/login', views.spotifyLogin, name='spotifyLogin'),
    path('spotify/callback/', views.spotifyCallback, name='spotifyCallback'),



]
