from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import *
from django.core.files import File
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.forms.models import model_to_dict
from django.forms import modelformset_factory
from django.urls import reverse
from django.utils import timezone
from django.db import transaction
from .models import *
import pytz
import json
import requests
from django.conf import settings
import os
# Create your views here.

@login_required
def set_timezone(request):
    if request.method == 'POST':
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('/')
    else:
        return render(request, 'woocommerce/timezone.html', {'timezones': pytz.common_timezones})


@login_required
def index(request):
    schedules=Schedule.objects.filter(profil__id=request.user.profil.id)
    context = {'schedules': schedules}
    return render(request, "woocommerce/index.html", context)

@login_required
def schedule_creation(request):
    profil = Profil.objects.get(user=request.user)
    subscription = profil.subscription
    if subscription.days_time >=1 and subscription.schedules_nb >= 1 and subscription.sites_limites >=1:
        if request.method == 'POST':
            schedule_form = ScheduleForm(request.POST)
            if schedule_form.is_valid():
                schedule = schedule_form.save(commit=False)
                schedule.profil=profil
                schedule.save()
                response = schedule.ali_import()
                schedule.save()
                subscription.schedules_nb=subscription.schedules_nb -1
                subscription.save()

                context = { 'response': response,
                            'schedule': schedule.id,
                            'scrap_done': True
                            }

                return render(request,"woocommerce/schedule_form.html",context)
        else:

            schedule_form = ScheduleForm()


        context = {'schedule_form' : schedule_form,'schedule': 0,
                'scrap_done': False
                }
        return render(request, "woocommerce/schedule_form.html", context)
    else:
        context = {"reject" : "rejected",'schedule': 0,'scrap_done': False}
        return render(request, "woocommerce/schedule_form.html", context)

@login_required
def generate_csv_file(request,id):
    schedule = Schedule.objects.get(pk=id)
    if schedule.file_state == 'P':
        path = settings.MEDIA_ROOT + '/profiles/dopeman2/schedule' + str(id)  +'.csv'
        f = open(path, 'w')
        writer = csv.writer(f)
        writer.writerow(['Product ID', 'Product Title', 'Product URL',
                    'Original Price', 'Sale Price','Image URL'])

        path_old = schedule.schedule_file.path
        response_path = os.path.join( settings.BASE_DIR, path_old )
        json_reader = json.loads(open(response_path).read())
        products = json_reader['result']['products']
        for product in products:
            productUrl = product['productUrl']
            productTitle = product['productTitle']
            productId = product['productId']
            originalPrice = product['originalPrice']
            salePrice = product['salePrice']
            incr = Decimal(sub(r'[^\d.]', '', salePrice))
            priceinc = incr * 3  # print(incr, priceinc)
            imageUrl = product['imageUrl']
            writer.writerow([productId,productTitle,productUrl,
                            originalPrice,salePrice,imageUrl])
        f.close()
        f = open(path, 'r')
        newFile = ContentFile(f.read())
        schedule.file_state= 'C'
        schedule.schedule_file.delete()
        schedule.schedule_file_csv.save('a.csv',newFile)
        os.remove(f.name)
        context = { 'schedule': schedule.id,
                    'state' : schedule.file_state

        }
        return render(request,"woocommerce/generate_success.html", context)
    else:
        context = { 'schedule': schedule.id,
                    'state' : schedule.file_state
        }
        return render(request,"woocommerce/generate_success.html", context)


@login_required
def get_csv_file(request,id):
    schedule = Schedule.objects.get(pk=id)
    path = schedule.schedule_file_csv.path
    response_path = os.path.join( settings.BASE_DIR, path )

    f = open(response_path, 'r')
    response = HttpResponse(f,content_type='text/csv')
    schedule.file_state = 'D'
    schedule.save()
    response['Content-Disposition'] = 'attachment; filename=%s' %'response'+ str(id)+'.csv'
    return response

@transaction.atomic
def signup(request):

    if request.user.is_authenticated:
        return redirect(reverse('woocommerceApp:index'))

    if request.method == "POST":
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)

        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            subscription = Subscription.objects.get(title= 'Free trial')
            profile.subscription = subscription
            profile.save()
            profile_form.save_m2m()

            user.save()
            login(request, user)
            return redirect(reverse('woocommerceApp:index'))
        else:
            return redirect(reverse('woocommerceApp:signup'))

    else:
        user_form = UserForm()
        profile_form = ProfileForm()

    context = {"user_form":user_form, "profile_form":profile_form}
    return render(request, 'woocommerce/signup.html', context)
