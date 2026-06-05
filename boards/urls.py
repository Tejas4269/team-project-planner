from django.urls import path
from .views import (
    CreateBoardView, CloseBoardView, ListBoardsView,
    AddTaskView, UpdateTaskStatusView, ExportBoardView,
)

urlpatterns = [
    path('create/', CreateBoardView.as_view()),
    path('<str:board_id>/close/', CloseBoardView.as_view()),
    path('<str:board_id>/tasks/add/', AddTaskView.as_view()),
    path('<str:board_id>/export/', ExportBoardView.as_view()),
    path('team/<str:team_id>/', ListBoardsView.as_view()),
    path('tasks/<str:task_id>/status/', UpdateTaskStatusView.as_view()),
]
