import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .service import BoardService

service = BoardService()


def error_response(msg, status=400):
    return JsonResponse({"error": str(msg)}, status=status)


@method_decorator(csrf_exempt, name='dispatch')
class CreateBoardView(View):
    def post(self, request):
        try:
            result = service.create_board(request.body.decode())
            return JsonResponse(json.loads(result), status=201)
        except Exception as e:
            return error_response(e)


@method_decorator(csrf_exempt, name='dispatch')
class CloseBoardView(View):
    def post(self, request, board_id):
        try:
            result = service.close_board(json.dumps({"id": board_id}))
            return JsonResponse(json.loads(result))
        except Exception as e:
            return error_response(e)


@method_decorator(csrf_exempt, name='dispatch')
class ListBoardsView(View):
    def get(self, request, team_id):
        try:
            result = service.list_boards(json.dumps({"id": team_id}))
            return JsonResponse(json.loads(result), safe=False)
        except Exception as e:
            return error_response(e, 404)


@method_decorator(csrf_exempt, name='dispatch')
class AddTaskView(View):
    def post(self, request, board_id):
        try:
            data = json.loads(request.body.decode())
            data["board_id"] = board_id
            result = service.add_task(json.dumps(data))
            return JsonResponse(json.loads(result), status=201)
        except Exception as e:
            return error_response(e)


@method_decorator(csrf_exempt, name='dispatch')
class UpdateTaskStatusView(View):
    def patch(self, request, task_id):
        try:
            data = json.loads(request.body.decode())
            data["id"] = task_id
            result = service.update_task_status(json.dumps(data))
            return JsonResponse(json.loads(result))
        except Exception as e:
            return error_response(e)


@method_decorator(csrf_exempt, name='dispatch')
class ExportBoardView(View):
    def get(self, request, board_id):
        try:
            result = service.export_board(json.dumps({"id": board_id}))
            return JsonResponse(json.loads(result))
        except Exception as e:
            return error_response(e)
