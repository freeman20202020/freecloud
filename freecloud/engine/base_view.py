import functools
import sys
import time
import types

from django.views import View
from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponse, StreamingHttpResponse
from engine.utils import get_log_object

LOG = get_log_object(__name__)


class _MetaDeco(type):
    def __init__(cls, *args):
        super(_MetaDeco, cls).__init__(*args)

    def __new__(mcs, name, bases, attributes):

        for attr_name, attr_value in attributes.items():
            handler_chain = []
            if isinstance(attr_value, types.FunctionType) and attr_name in [
                "get", "post", "os_get", "os_post", "ct_get", "ct_post"
            ]:
                if attr_name in ["get", "post"]:
                    handler_chain = [mcs.time_log, mcs.view_exception_catcher]
                else:
                    handler_chain = [mcs.view_exception_catcher]
            for handler in handler_chain:
                attributes[attr_name] = handler(attr_value)
        return super(_MetaDeco, mcs).__new__(mcs, name, bases, attributes)

    @classmethod
    def log_local(mcs, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def trace_return(frame, event, arg):
                try:
                    print(frame, event, arg)
                    if event == 'return':
                        _locals = frame.f_locals.copy()
                        for k, v in _locals.items():
                            LOG.info("local var:{} = {}".format(k, v))
                except Exception as e:
                    LOG.info("WARNING add local var log error:{}".format(e))

            def trace_calls(frame, event, arg, to_be_traced):
                print(frame, event, arg, to_be_traced)
                if event != 'call':
                    return
                co = frame.f_code
                func_name = co.co_name
                if func_name == 'write':
                    return
                if func_name in to_be_traced:
                    return trace_return

            tracer = functools.partial(trace_calls, to_be_traced=["ct_get", "ct_post",
                                                                  "os_get", "os_post"])
            sys.settrace(tracer)
            try:
                ret = func(*args, **kwargs)
            finally:
                sys.setprofile(None)
            return ret

        return wrapper

    @classmethod
    def time_log(mcs, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                class_name = args[0].__class__.__name__
            except IndexError:
                class_name = None
            start = time.time()
            ret = func(*args, **kwargs)
            try:
                end = time.time()
                cost_sec = end - start
                msg = "view time counter, {}.{} Cost {:.2f}s".format(class_name, func.__name__, cost_sec)
                if cost_sec > 4:
                    msg = "SLOW WARNING {}".format(msg)
                LOG.info(msg)
            except Exception as e:
                LOG.info("WARNING add time cost error:{}".format(e))
            return ret

        return wrapper

    @classmethod
    def view_exception_catcher(mcs, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                ret = func(*args, **kwargs)
                return ret
            except Exception as e:
                LOG.info(str(args))
                raise e
                # return JsonResponse({"error": str(e)})

        return wrapper


class BaseView(View, metaclass=_MetaDeco):
    API_TITLE = ""
    KWARGS = {
        # 参数名  默认值  示例  类型  是否必填 长度 说明
        # "name": ("name", "kfc", str, "required", 128, "名称"),
        # "age": ("name", 18, int, "required", "", "年龄()"),
        # "description": (None, {"a": "dsb"}, dict, "required", 128, "描述"),
    }
    TEST_PARAMS = {

    }
    METHOD = "post"

    def get(self, request):
        if str(request.GET.get('doc')) == str(1):
            doc = self.get_doc(request)

            return render(request, "doc.html", doc)
        elif request.GET.get('test_api'):
            url = request.build_absolute_uri()
            url = url.replace("doc=1", "").replace("test_api=1", "")
            print(url)
            import requests
            return JsonResponse(getattr(requests, self.METHOD)(url, json=self.TEST_PARAMS).json())
        return getattr(self, "my_get")(request)

    def get_doc(self, request):
        l1, l2, l3, l4, l5, l6 = self.get_var_length()
        doc = dict(path=request.path, method=self.METHOD.upper(), title=self.API_TITLE)
        params = []
        for k, v in self.KWARGS.items():
            print(v)
            params += [dict(r1=k, r2=v[1], r3=v[2], r4=v[3], r5=v[0], r6=v[4], r7=v[5])]
        doc['params'] = params
        return doc

    def get_var_length(self):
        if self.KWARGS:
            # print((self.KWARGS))
            l1 = max([len(i) for i in self.KWARGS.keys()] + [0])
            l2 = max([len(str(i[1])) for i in list(self.KWARGS.values())])
            l3 = max([len(str(i[2])) for i in list(self.KWARGS.values())])
            l4 = max([len(str(i[3])) for i in list(self.KWARGS.values())])
            l5 = max([len(str(i[0])) for i in list(self.KWARGS.values())])
            l6 = max([len(str(i[4])) for i in list(self.KWARGS.values())])
        else:
            l1 = l2 = l3 = l4 = l5, l6 = 0
        return [i * 10 for i in [l1, l2, l3, l4, l5, l6]]
