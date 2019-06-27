import json
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from user.views.auth import login_required
from user.helper.token import Token
from user.helper.User import User
from user.helper.constants import ADDED_SUCCESS, UPDATE_SUCESS, DOESNOT_EXISTS

@login_required
def docker_cred(request):

    try:

        if request.method == 'GET':
            token = Token(request)
            username=token.get_username()

            _user=User(username)

            res = _user.get_docker_cred()

            if res== DOESNOT_EXISTS:
                return HttpResponseBadRequest(json.dumps({
                    "message": res
                }), content_type='application/json')

            else:
                return HttpResponse(json.dumps({
                    "message": res
                }), content_type='application/json')

        else:

            token = Token(request)
            username=token.get_username()
            _user=User(username)
            _structure = json.loads(request.body.decode())
            res = _user.add_docker_cred(_structure)
            if res == ADDED_SUCCESS or res == UPDATE_SUCESS:
                return HttpResponse(json.dumps({
                    "message": res
                }), content_type='application/json')
            
            else:
                return HttpResponseBadRequest(json.dumps({
                    "message": res
                }), content_type='application/json')


    except Exception as e:
        return HttpResponseServerError(json.dumps({
                'message': str(e)
            }), content_type='application/json')

@login_required
def kube_cred(request):

    try:

        if request.method=='GET':
            token = Token(request)
            username=token.get_username()

            _user=User(username)

            res = _user.get_kubernetes_cred()

            if res== DOESNOT_EXISTS:
                return HttpResponseBadRequest(json.dumps({
                    "message": res
                }), content_type='application/json')

            else:
                return HttpResponse(json.dumps({
                    "message": res
                }), content_type='application/json')


        else:
                
            token = Token(request)
            username=token.get_username()

            _user=User(username)

            _structure = json.loads(request.body.decode())

            res = _user.add_kubernetes_cred(_structure)

            if res == ADDED_SUCCESS or res == UPDATE_SUCESS:
                return HttpResponse(json.dumps({
                    "message": res
                }), content_type='application/json')
            
            else:
                return HttpResponseBadRequest(json.dumps({
                    "message": res
                }), content_type='application/json')


    except Exception as e:
        return HttpResponseServerError(json.dumps({
                'message': str(e)
            }), content_type='application/json')