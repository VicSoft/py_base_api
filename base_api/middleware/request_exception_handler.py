from django.http.response import *
from ..settings import API_PROJECT, os


class RequestExceptionHandler(object):

    def __init__(self, next_layer=None):
        self.get_response = next_layer

    def __call__(self, request):
        if not self.is_authenticated(request):
            return JsonResponse({
                'response_status_code': HttpResponseForbidden.status_code,
                'error': 'Request not authenticated',
                'cause': 'You have to give a valid API-KEY on header request'
            }, status=HttpResponseForbidden.status_code)

        try:
            response = self.get_response(request)

            if isinstance(response, HttpResponseNotFound):
                return JsonResponse({
                    'error': 'Page not found at ' + request.path,
                    'response_status_code': response.status_code
                }, status=response.status_code)
            elif isinstance(response, HttpResponseBadRequest):
                return JsonResponse({
                    'error': 'Bad request for ' + request.path,
                    'response_status_code': response.status_code
                }, status=response.status_code)
            elif isinstance(response, HttpResponseNotAllowed):
                return JsonResponse({
                    'error': 'Response not allowed for ' + request.path,
                    'response_status_code': response.status_code
                }, status=response.status_code)
            elif isinstance(response, HttpResponseGone):
                return JsonResponse({
                    'error': 'Response gone in ' + request.path,
                    'response_status_code': response.status_code
                }, status=response.status_code)
            elif isinstance(response, HttpResponseForbidden):
                return JsonResponse({
                    'error': 'Not allowed access (Forbidden) at ' + request.path,
                    'response_status_code': response.status_code
                }, status=response.status_code)
            elif isinstance(response, HttpResponseServerError):
                return JsonResponse({
                    'error': 'Server error for ' + request.path,
                    'response_status_code': response.status_code
                }, status=response.status_code)
            else:
                try:
                    response = JsonResponse(json.loads(response.content), status=response.status_code)
                    return response
                except AttributeError as attErr:
                    return JsonResponse({
                        'error': 'AttributeError (' + attErr.message + ')',
                        'response_status_code': response.status_code
                    }, status=response.status_code)
                except ValueError as valErr:
                    return JsonResponse({
                        'error': 'ValueError (' + valErr.message + ')',
                        'response_status_code': response.status_code
                    }, status=response.status_code)
                except Exception as e:
                    return JsonResponse({
                        'error': 'Error (' + e.message + ')',
                        'response_status_code': response.status_code
                    }, status=response.status_code)

        except AttributeError:
            pass

    def is_authenticated(self, request):
        if 'HTTP_API_KEY' in request.META:
            api_key = request.META['HTTP_API_KEY']
            with open(os.path.join(API_PROJECT, 'api_keys.json')) as data_file:
                data_keys = json.load(data_file)
                for platform, key in data_keys['main_keys'].iteritems():
                    if api_key == key:
                        return True

            return False
        else:
            return False
