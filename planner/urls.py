from django.urls import path, include

urlpatterns = [
    path('api/users/', include('users.urls')),
    path('api/teams/', include('teams.urls')),
    path('api/boards/', include('boards.urls')),
]
