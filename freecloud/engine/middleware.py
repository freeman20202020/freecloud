import random
import threading

from django.utils.deprecation import MiddlewareMixin

local = threading.local()


class AddLogInfoMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        try:
            local.path = str(request.path).replace('/', '__')
            local.random_string = str(random.randint(10 ** 8, 10 ** 9))
            print(local.__dict__)
        except Exception as e:
            print(e)

    @staticmethod
    def process_response(request, response):
        return response
