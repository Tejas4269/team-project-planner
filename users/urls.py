from django.urls import path
from .views import CreateUserView, ListUsersView, UserDetailView, UserTeamsView

urlpatterns = [
    path('', ListUsersView.as_view()),
    path('create/', CreateUserView.as_view()),
    path('<str:user_id>/', UserDetailView.as_view()),
    path('<str:user_id>/teams/', UserTeamsView.as_view()),
]
