import json
from user.helper.constants import VALID_TOKEN, INVALID_TOKEN, TOKEN_EXPIRED, HTTP_UNAUTHORIZED, \
    HTTP_INTERNAL_SERVER_ERROR, USER_ADDED_SUCCESS
from user.helper.token import check_token, Token, create_token
from user.helper.User import User
from django.http import HttpResponseBadRequest, HttpResponseServerError, HttpResponse


# Login required decorator
def login_required(view):
    def inner(request):
        try:
            status = check_token(request.META['HTTP_TOKEN'])
            if status == VALID_TOKEN:
                return view(request)
            elif status == INVALID_TOKEN:
                return HttpResponseBadRequest(json.dumps({"success": False,
                                                          "code": HTTP_UNAUTHORIZED,
                                                          "message": "invalid token"}), content_type='application/json')
            elif status == TOKEN_EXPIRED:
                return HttpResponseBadRequest(json.dumps({"success": False,
                                                          "code": HTTP_UNAUTHORIZED,
                                                          "message": "token expired"}), content_type='application/json')
            else:
                return HttpResponseServerError(json.dumps({"success": False,
                                                           "code": HTTP_INTERNAL_SERVER_ERROR,
                                                           "message": "something went wrong"}),
                                               content_type='application/json')
        except:
            return HttpResponseBadRequest(json.dumps({"success": False,
                                                      "code": HTTP_UNAUTHORIZED,
                                                      "message": "login required"}), content_type='application/json')

    return inner

def register(request):
    try:
        
        if request.method=='POST':
            
            user_structure = json.loads(request.body.decode())

            res = User.add_user(user_structure)

            if res==USER_ADDED_SUCCESS:
                token = create_token(user_structure["username"])

                return HttpResponse(json.dumps({
                    "message": "user successfully added",
                    "token": token
                }), content_type='application/json')

            else:
                return HttpResponseBadRequest(json.dumps({
                    "message": res
                }), content_type='application/json')
        else:
            return HttpResponseBadRequest(json.dumps({
                "message": "only post method"
            }), content_type='application/json')
        

    except Exception as e:
        print(e)
        return HttpResponseServerError(json.dumps({
                'message': str(e)
            }), content_type='application/json')

def login(request):
    try:
        
        if request.method=='POST':
            
            user_structure = json.loads(request.body.decode())

            if "username" not in user_structure or "password" not in user_structure:
                return HttpResponseBadRequest(json.dumps({
                    "message": "invalid data format"
                }), content_type='application/json')

            res = User.check_user(user_structure["username"],
                                user_structure["password"])

            if res==True:
                token = create_token(user_structure["username"])

                return HttpResponse(json.dumps({
                    "token": token
                }), content_type='application/json')

            else:
                return HttpResponseBadRequest(json.dumps({
                    "message": "user doesnot exists"
                }), content_type='application/json')
        else:
            return HttpResponseBadRequest(json.dumps({
                "message": "only post method"
            }), content_type='application/json')
        

    except Exception as e:
        print(e)
        return HttpResponseServerError(json.dumps({
                'message': str(e)
            }), content_type='application/json')


