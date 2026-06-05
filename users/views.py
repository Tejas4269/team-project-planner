import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .service import UserService

service = UserService()


def error_response(msg, status=400):
    return JsonResponse({"error": str(msg)}, status=status)


@method_decorator(csrf_exempt, name='dispatch')
class CreateUserView(View):
    def post(self, request):
        try:
            result = service.create_user(request.body.decode())
            return JsonResponse(json.loads(result), status=201)
        except Exception as e:
            return error_response(e)


@method_decorator(csrf_exempt, name='dispatch')
class ListUsersView(View):
    def get(self, request):
        try:
            return JsonResponse(json.loads(service.list_users()), safe=False)
        except Exception as e:
            return error_response(e)


@method_decorator(csrf_exempt, name='dispatch')
class UserDetailView(View):
    def get(self, request, user_id):
        try:
            body = json.dumps({"id": user_id})
            return JsonResponse(json.loads(service.describe_user(body)))
        except Exception as e:
            return error_response(e, 404)

    def patch(self, request, user_id):
        try:
            data = json.loads(request.body.decode())
            data["id"] = user_id
            result = service.update_user(json.dumps(data))
            return JsonResponse(json.loads(result))
        except Exception as e:
            return error_response(e)


@method_decorator(csrf_exempt, name='dispatch')
class UserTeamsView(View):
    def get(self, request, user_id):
        try:
            body = json.dumps({"id": user_id})
            return JsonResponse(json.loads(service.get_user_teams(body)), safe=False)
        except Exception as e:
            return error_response(e, 404)
