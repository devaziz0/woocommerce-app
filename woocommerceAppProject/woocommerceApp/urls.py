from django.urls import path, include
from . import views
from django.contrib.auth.views import LoginView


app_name = "woocommerceApp"

urlpatterns = [
    path('', views.landing, name="landing"),
    path('dashboard/', views.index, name="index"),
    path('subscription/',views.subscription, name="subscription"),
    path('subscription/list/',views.subscription_list, name="subscription_list"),
    path('subscription/change/<int:id>/',views.subscription_change, name="subscription_change"),
    path('dashboard/schedule/<int:id>/display/',views.schedule_display, name="schedule_display"),
    path('dashboard/schedule/<int:id>/download/', views.get_csv_file, name="download"),
    path('dashboard/schedule/<int:id>/generate/', views.generate_csv_file, name="generate"),
    path('dashboard/schedule/<int:id>/post/', views.woocommerce_post, name="post"),
    path('dashboard/schedule/', views.schedule_creation, name="schedule"),
    path('timezone/', views.set_timezone, name="timezone"),
    path('notification/', views.notification, name="notification"),
    path('signup/',views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls'))
]
