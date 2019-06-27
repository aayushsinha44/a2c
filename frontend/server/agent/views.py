import json
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from user.views.auth import login_required
from user.helper.token import Token
from user.helper.User import User
from agent.helper.agent import Agent
from agent.helper.vm import VM
from agent.helper.constants import DOESNOT_EXISTS, INVALID_ACCESS, \
    INVALID_PARAMETER_STRUCTURE

@login_required
def agent_ip(request):

    try:

        if request.method=='GET':
            token = Token(request)
            username=token.get_username()

            _user=User(username)
            _agent=Agent(_user)

            res = _agent.get_agent_cred()

            if res == DOESNOT_EXISTS:
                return HttpResponseBadRequest(json.dumps({
                    "message": res
                }), content_type='application/json')
            
            return HttpResponse(json.dumps({
                "message": res
            }), content_type='application/json')

        elif request.method == 'POST' or request.method=='PUT':
            token = Token(request)
            username=token.get_username()

            _user=User(username)
            _agent=Agent(_user)

            data_structure=json.loads(request.body.decode())

            if "agent_ip" not in data_structure:
                return HttpResponseBadRequest(json.dumps({
                    "message": "vm_ip not in json body"
                }), content_type='application/json')

            res = _agent.add_agent_cred(data_structure["vm_ip"])

            return HttpResponse(json.dumps({
                "message": res
            }), content_type='application/json')

        else:
            return HttpResponseBadRequest(json.dumps({
                "message": "invalid request method"
            }), content_type='application/json')

    except Exception as e:
        return HttpResponseServerError(json.dumps({
            "message": str(e)
        }), content_type='application/json')


@login_required
def vm_cred(request, id=None):
    
    try:

        token = Token(request)
        username=token.get_username()

        _user=User(username)
        _vm = VM(_user)

        if request.method == 'GET':

            if id is None:
                res = _vm.get_all_vm_cred()

                return HttpResponse(json.dumps({
                    "data": res
                }), content_type='application/json')
                
            res = _vm.get_vm_cred(id)

            return HttpResponse(json.dumps({
                "data": res
            }), content_type='application/json')

        elif request.method == 'POST':
            
            data_structure=json.loads(request.body.decode())
            res = _vm.add_vm_cred(data_structure)

            if res == INVALID_ACCESS or res == INVALID_PARAMETER_STRUCTURE:
                return HttpResponseBadRequest(json.dumps({
                    "message": res
                }),
                content_type='application/json')

            return HttpResponse(json.dumps({
                "message": res
            }), 
            content_type='application/json')
            

        elif request.method == 'PUT':
            
            if id is None:
                return HttpResponseBadRequest(json.dumps({
                    "message": "invalid method"
                }),
                    content_type='application/json')
            
            data_structure=json.loads(request.body.decode())
            res = _vm.update_vm_cred(id, data_structure)
            if res == INVALID_ACCESS or res == INVALID_PARAMETER_STRUCTURE:
                return HttpResponseBadRequest(json.dumps({
                    "message": res
                }),
                content_type='application/json')

            return HttpResponse(json.dumps({
                "message": res
            }), 
            content_type='application/json')

        elif request.method == 'DELETE':
            
            if id is None:
                return HttpResponseBadRequest(json.dumps({
                    "message": "invalid method"
                }),
                    content_type='application/json')
            res = _vm.delete_vm(id)
            return HttpResponse(json.dumps({
                "message": res
            }), 
            content_type='application/json')


        else:
            return HttpResponseBadRequest(json.dumps({
                "message": "invalid request method"
            }), content_type='application/json')


    except Exception as e:

        return HttpResponseServerError(json.dumps({
            "message": str(e)
        }), content_type='application/json')

