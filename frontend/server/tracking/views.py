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
from tracking.helper.track import Track

# Create your views here.
@login_required
def start_process(request):
    try:

        token = Token(request)
        username=token.get_username()

        _user=User(username)

        _data=json.loads(request.body.decode())
        _data=_data["vm_id"]

        _tracking = Tracking(_user, _data)

        _res = _tracking.check_system()
        if _res != SUCCESS:
            return HttpResponseBadRequest(json.dumps({
                "message": _res
            }), content_type='application/json')


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

@login_required
def track(request, pool_id=None):
    try:

        if pool_id is None:
            return HttpResponseBadRequest(json.dumps({
                "message": "id not set"
            }), content_type='application/json')
        
        token = Token(request)
        username=token.get_username()

        _user=User(username)

        _track=Track(_user, pool_id)
        
        return HttpResponse(json.dumps({
            "data": _track.get_info()
        }), content_type='application/json')


    except Exception as e:
        return HttpResponseServerError(json.dumps({
            "message": str(e)
        }), content_type='application/json')

@login_required
def get_services(request):
    try:

        token = Token(request)
        username=token.get_username()

        _user=User(username)

        _tracking = Tracking(_user, [])

        _res = _tracking.check_system()
        if _res != SUCCESS:
            return HttpResponseBadRequest(json.dumps({
                "message": _res
            }), content_type='application/json')

        return HttpResponse(json.dumps({
            "message": _tracking.get_services(),
        }), content_type='application/json')

    except Exception as e:
        return HttpResponseServerError(json.dumps({
            "message": str(e)
        }), content_type='application/json')
