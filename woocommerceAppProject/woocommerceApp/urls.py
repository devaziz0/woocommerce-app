from django.urls import path, include
from . import views
from django.contrib.auth.views import LoginView


app_name = "woocommerceApp"

urlpatterns = [
    path('dashboard/', views.index, name="index"),
    path('timezone/', views.set_timezone, name="timezone"),
    path('dashboard/schedule/<int:id>/download/', views.get_csv_file, name="download"),
    path('dashboard/schedule/<int:id>/generate/', views.generate_csv_file, name="generate"),
    path('dashboard/schedule/', views.schedule_creation, name="schedule"),
    path('signup/',views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls'))
]