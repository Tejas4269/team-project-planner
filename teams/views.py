import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .service import TeamService

service = TeamService()


def error_response(msg, status=400):
    return JsonResponse({"error": str(msg)}, status=status)


@method_decorator(csrf_exempt, name='dispatch')
class CreateTeamView(View):
    def post(self, request):
        try:
            result = service.create_team(request.body.decode())
            return JsonResponse(json.loads(result), status=201)
        except Exception as e:
            return error_response(e)


@method_decorator(csrf_exempt, name='dispatch')
class ListTeamsView(View):
    def get(self, request):
        try:
            return JsonResponse(json.loads(service.list_teams()), safe=False)
        except Exception as e:
            return error_response(e)


@method_decorator(csrf_exempt, name='dispatch')
class TeamDetailView(View):
    def get(self, request, team_id):
        try:
            return JsonResponse(json.loads(service.describe_team(json.dumps({"id": team_id}))))
        except Exception as e:
            return error_response(e, 404)

    def patch(self, request, team_id):
        try:
            data = json.loads(request.body.decode())
            data["id"] = team_id
            return JsonResponse(json.loads(service.update_team(json.dumps(data))))
        except Exception as e:
            return error_response(e)


@method_decorator(csrf_exempt, name='dispatch')
class TeamUsersView(View):
    def get(self, request, team_id):
        try:
            return JsonResponse(json.loads(service.list_team_users(json.dumps({"id": team_id}))), safe=False)
        except Exception as e:
            return error_response(e, 404)

    def post(self, request, team_id):
        try:
            data = json.loads(request.body.decode())
            data["id"] = team_id
            action = request.GET.get("action", "add")
            if action == "remove":
                result = service.remove_users_from_team(json.dumps(data))
            else:
                result = service.add_users_to_team(json.dumps(data))
            return JsonResponse(json.loads(result))
        except Exception as e:
            return error_response(e)
