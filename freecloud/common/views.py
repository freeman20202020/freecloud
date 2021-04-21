from django.http import JsonResponse

from engine.base_view import BaseView
from engine.utils import get_log_object

LOG = get_log_object(__name__)


class TestView(BaseView):
    API_TITLE = "测试接口"
    KWARGS = {
        "name": ("string", "必填", "128", "name", "名称", "name"),
        "age": ("int", "必填", "3", 18, "年龄(0-200)", 18),
        "description": ("string", "选填", 128, "", "描述", "-"),
    }
    METHOD = "get"

    def my_get(self, request):
        LOG.info(self)
        LOG.info(str(request.GET))
        return JsonResponse({"OK": "ok"})
