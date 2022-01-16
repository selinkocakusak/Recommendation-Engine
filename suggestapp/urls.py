from django.urls import path
from django.conf.urls import url
from .views import activation_sent_view, activate


from . import views
app_name = 'suggestapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('article_view/<slug:uidb64>/<int:no>/',
         views.article_view, name='article_view'),
    path('manage/<slug:uidb64>/<slug:token>/',
         views.manage, name='manage'),
    path('unsubscribe/<slug:uidb64>/<slug:token>/',
         views.unsubscribe, name='unsubscribe'),
    path('sent/', views.activation_sent_view, name="activation_sent"),
    path('activate/', views.activate, name="activation_done"),
    path('activate/', views.activate, name="activation_success"),
    path('activate/<slug:uidb64>/<slug:token>/',
         views.activate, name='activate'),

]
