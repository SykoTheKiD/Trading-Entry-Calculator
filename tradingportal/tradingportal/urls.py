from django.contrib import admin
from django.urls import include, path

from tradingportal import views

urlpatterns = [
    path('', views.index, name="home_page"),
    path('admin/', admin.site.urls),
    path('valueinvestor/', include('stockscreener.urls')),
]
