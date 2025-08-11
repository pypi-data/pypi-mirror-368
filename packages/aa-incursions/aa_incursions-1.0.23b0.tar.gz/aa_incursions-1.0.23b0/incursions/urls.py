from corptools.views import add_char

from django.urls import path, re_path

from incursions import views
from incursions.api import api

app_name = "incursions"

urlpatterns = [
    re_path(r'^waitlist/', views.waitlist, name="waitlist"),
    re_path(r'^api/', api.urls),
    path('char/add', add_char, name="add_char"),
    path('char/add_fc', views.add_char_fc, name="add_char_fc"),
]
