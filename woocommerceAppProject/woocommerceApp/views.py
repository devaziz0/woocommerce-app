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
from woocommerce import API
# Create your views here.

@login_required
def set_timezone(request):
    if request.method == 'POST':
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('/')
    else:
        return render(request, 'woocommerce/timezone.html', {'timezones': pytz.common_timezones})


def landing(request):
    return render(request,"woocommerce/landing.html")

@login_required
def index(request):
    schedules=Schedule.objects.filter(profil__id=request.user.profil.id)
    context = {'schedules': schedules}
    return render(request, "woocommerce/index.html", context)

@login_required
def schedule_creation(request):
    profil = Profil.objects.get(user=request.user)
    subscription = None
    if profil.free_subscription != None:
        subscription = profil.free_subscription
    elif profil.basic_subscription != None:
        subscription = profil.basic_subscription
    elif profil.premium_subscription != None:
        subscription = profil.premium_subscription
    elif profil.gold_subscription != None:
        subscription = profil.gold_subscription

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
                schedule_form = ScheduleForm()

                context = { 'schedule_form' : schedule_form,
                            'response': response,
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
            priceinc = incr * schedule.AliExpress_Increment  # print(incr, priceinc)
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
                    'state' : schedule.file_state,
                    'post' : False
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

@login_required
def woocommerce_post(request,id):
    schedule =  Schedule.objects.get(pk=id)
    wcapi = API(
        url = schedule.woocommerce_url,
        consumer_key = schedule.woocommerce_consumer_key,
        consumer_secret= schedule.woocommerce_secret_key,
        wp_api=True,
        timeout= 100,
        version="wc/v2"
    )
    path = os.path.join(settings.BASE_DIR,schedule.schedule_file.path)
    f = open(path,'r')
    json_file = json.loads(f.read())

    getlistproducts = json_file['result']['products']
    print(getlistproducts)
    for resultsget in getlistproducts:
        producturls = resultsget['productUrl']
        productitles = resultsget['productTitle']
        productids = resultsget['productId']
        originalprices = resultsget['originalPrice']
        saleprices = resultsget['salePrice']
        incr = Decimal(sub(r'[^\d.]', '', saleprices))
        priceinc = incr * 3  # print(incr, priceinc)
        conint = int(priceinc)
        imageurls = resultsget[
            'imageUrl']  # print(productids, productitles,originalprices,saleprices,imageurls, producturls )
        urlpromo = "http://gw.api.alibaba.com/openapi/param2/2/portals.open/api.getPromotionLinks/9420?fields=promotionUrl&trackingId=bazaarmaya"  # GET PROMOTIONAL URL
        payloadpromo = {
            'urls': producturls
        }
        promoget = requests.get(urlpromo, params=payloadpromo)
        promotojson = promoget.text
        promoresult = json.loads(promotojson)
        promourl = promoresult['result']['promotionUrls'][0]['promotionUrl']
        divpromo = "<div class='invisible'>" + promourl + "</div>"
        getdetailsurl = 'http://gw.api.alibaba.com/openapi/param2/2/portals.open/api.getPromotionProductDetail/'  # GET DETAILS
        api_key = '9420'
        fields = '?fields=discount,evaluateScore,commission,commissionRate,30daysCommission,volume,packageType,lotNum,validTime,allImageUrls'
        payloads = {
            'productId': productids
        }
        detailurl = getdetailsurl + api_key + fields
        detailr = requests.get(detailurl, params=payloads)
        getlist = detailr.text
        tojson = json.loads(getlist)
        getresult = tojson['result']
        getdetailvol = getresult['volume']
        getdetailevalscore = getresult['evaluateScore']
        getdetaillotnum = getresult['lotNum']
        getdetaildiscount = getresult['discount']
        getdetailvalid = getresult['validTime']
        getdetailcommision = getresult['30daysCommission']
        getdetailpacktyper = getresult['packageType']
        getdetailallimage = tojson['result']['allImageUrls'].split(',')
        domUrl = "https://www.aliexpress.com/"  # GET DESCRIPTIONS
        dommer = "getDescModuleAjax.htm?productId="
        objecTo = str(productids)
        target = domUrl + dommer + objecTo
        r = requests.get(target)
        mored = r.text
        cutt = mored[29:-5]
        data = {
            "name": productitles,
            "type": "simple",
            "regular_price": str(conint),
            "description": cutt + divpromo,
            "short_description": "",
            "categories": [
                {
                    "id": schedule.AliExpress_category
                }
            ],
            "images": []
        }

        for number, url in enumerate(getdetailallimage):
            data["images"].append({"src": url, "position": number})

        wcapi.post("products", data)
        schedule.file_state = 'PS'
        context = { 'schedule': schedule.id,
                    'state' : schedule.file_state,
                    'post' : True
        }

        return render(request,"woocommerce/generate_success.html", context)


@transaction.atomic
def signup(request):

    if request.user.is_authenticated:
        return redirect(reverse('woocommerceApp:index'))

    if request.method == "POST":
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            subscription = Free_Trial.objects.create()
            profile.save()
            profile_form.save_m2m()
            subscription.profil = profile
            subscription.save()

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

@login_required
def subscription(request):
    profil = Profil.objects.get(user=request.user)
    subscription = None
    free_subscription = None
    basic_subscription = None
    premium_subscription = None
    gold_subscription = None

    try:
        free_subscription = Free_Trial.objects.get(profil=profil)

    except Exception as e:
        pass
    try:
        basic_subscription = Basic_Subscription.objects.get(profil=profil)

    except Exception as e:
        pass

    try:
        premium_subscription = Premium_Subscription.objects.get(profil=profil)
    except Exception as e:
        pass

    try:
        gold_subscription = Gold_Subscription.objects.get(profil=profil)
    except Exception as e:
        pass

    if free_subscription != None:
        subscription = free_subscription
    elif basic_subscription != None:
        subscription = basic_subscription
    elif premium_subscription != None:
        subscription = premium_subscription
    elif gold_subscription != None:
        subscription = gold_subscription
    context = { 'subscription' : subscription

    }

    return render(request, "woocommerce/subscription.html", context)

@login_required
def subscription_list(request):

    return render(request, "woocommerce/subscription_change.html")

@login_required
def subscription_change(request, id):
    profil = Profil.objects.get(user=request.user)
    subscription = None
    free_subscription = None
    basic_subscription = None
    premium_subscription = None
    gold_subscription = None

    try:
        free_subscription = Free_Trial.objects.get(profil=profil)

    except Exception as e:
        pass
    try:
        basic_subscription = Basic_Subscription.objects.get(profil=profil)

    except Exception as e:
        pass

    try:
        premium_subscription = Premium_Subscription.objects.get(profil=profil)
    except Exception as e:
        pass

    try:
        gold_subscription = Gold_Subscription.objects.get(profil=profil)
    except Exception as e:
        pass

    if free_subscription != None:
        subscription = free_subscription
    elif basic_subscription != None:
        subscription = basic_subscription
    elif premium_subscription != None:
        subscription = premium_subscription
    elif gold_subscription != None:
        subscription = gold_subscription

    subscription.delete()

    if id == 1:
        Basic_Subscription.objects.create(profil=profil)
    elif id == 2:
        Premium_Subscription.objects.create(profil=profil)
    elif id == 3:
        Gold_Subscription.objects.create(profil=profil)

    return redirect(reverse('woocommerceApp:index'))

@login_required
def notification(request):
    response = HttpResponse()
    profil = Profil.objects.get(user = request.user)
    notifications = None
    try :
        notifications = Notification.objects.get(profil=profil)
    except Exception as e:
        pass

    return notifications
