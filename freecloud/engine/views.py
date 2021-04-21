from django.shortcuts import redirect, resolve_url, HttpResponse
from engine.base_view import BaseView
from engine.utils import get_log_object

# Create your views here.
LOG = get_log_object(__name__)


class AdminView(BaseView):
    def get(self, request):
        return redirect(resolve_url("admin/"))


class TestView(BaseView):
    def get(self, request):
        LOG.info(str(request.GET))
        return HttpResponse("OK")
