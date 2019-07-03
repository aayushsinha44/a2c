from django.shortcuts import render
from user.views.auth import login_required
from user.helper.User import User
from agent.helper.agent import Agent
from tracking.helper.tracking import Tracking
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest
import json
from user.helper.token import Token
import threading
from tracking.helper.constants import SUCCESS

# Create your views here.
@login_required
def start_process(request):
    try:

        token = Token(request)
        username=token.get_username()

        _user=User(username)

        _data=json.loads(request.body.decode())
        _data=_data["vm_id"]

        # TODO check_system

        _tracking = Tracking(_user, _data)

        _res = _tracking.check_system()
        if _res != SUCCESS:
            return HttpResponseBadRequest(json.dumps({
                "message": _res
            }), content_type='application/json')

        # _tracking.start()
        t1 = threading.Thread(target=_tracking.start)
        t1.start() 
        _tracking.create_vm_pool()
        return HttpResponse(json.dumps({
            "message": "started",
            "pool_id": _tracking.pool_id
        }), content_type='application/json')

    except Exception as e:
        return HttpResponseServerError(json.dumps({
            "message": str(e)
        }), content_type='application/json')
