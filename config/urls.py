"""
URL configuration for whatsapp_sentiment project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.http import HttpResponse
from django.contrib import admin
from django.urls import path
from apps.whatsapp_bot.views import whatsapp_webhook, dashboard

def home(request):
    return HttpResponse("Bonjour, Django tourne bien !")

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('dashboard/', dashboard, name='dashboard'),
    path('webhook/', whatsapp_webhook, name='whatsapp_webhook'),
]

