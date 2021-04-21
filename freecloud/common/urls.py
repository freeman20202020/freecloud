from django.conf.urls import url
from common import views
urlpatterns = [
    url("^common", views.TestView.as_view()),


]
