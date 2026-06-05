from django.urls import path
from .views import CreateTeamView, ListTeamsView, TeamDetailView, TeamUsersView

urlpatterns = [
    path('', ListTeamsView.as_view()),
    path('create/', CreateTeamView.as_view()),
    path('<str:team_id>/', TeamDetailView.as_view()),
    path('<str:team_id>/users/', TeamUsersView.as_view()),
]
