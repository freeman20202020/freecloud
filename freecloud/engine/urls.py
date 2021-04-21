from django.conf.urls import url
from engine import views
urlpatterns = [
    url("^test", views.TestView.as_view()),
    url("^$", views.AdminView.as_view()),
]
