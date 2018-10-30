from django.db import models
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
import requests
import json
from django.utils import timezone
from aliexpress_api_client import AliExpress
from woocommerce import API
import math
from re import sub
from decimal import Decimal
import os
import csv
from .upload import *
# Create your models here.

lorem = 'Lorem ipsum dolor sit amet, \
illum fastidii dissentias quo ne.\
 Sea ne sint animal iisque, nam an soluta sensibus. '

class Profil(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    NAG = 'X' #NotAGender
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (NAG, 'Not mentioned')
    )
    DEFAULT_PHOTO = "default/default-workshop.jpg"


    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mailing_Address = models.CharField(max_length = 100)
    photo = models.ImageField(upload_to=upload_to_profile_photo,
                                default=DEFAULT_PHOTO)
    birthday = models.DateTimeField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=NAG)

    def __str__(self):
        return str(self.user.id) +' ' + self.user.username

class Free_Trial(models.Model):
    description = models.CharField(max_length=500, default=lorem)
    days_time = models.IntegerField(default=30)
    schedules_nb = models.IntegerField(default=15)
    sites_limites = models.IntegerField(default=10)
    profil = models.OneToOneField(Profil,
                related_name='free_subscription',null=True, on_delete=models.CASCADE
                )
    def __str__(self):
        return 'Free Trail'

class Basic_Subscription(models.Model):
    description = models.CharField(max_length=500, default=lorem)
    days_time = models.IntegerField(default=45)
    schedules_nb = models.IntegerField(default=20)
    sites_limites = models.IntegerField(default=15)
    profil = models.OneToOneField(Profil,
            related_name='basic_subscription',null=True, on_delete=models.CASCADE
            )

    def __str__(self):
        return 'Standard Offer %s' % (self.id)

class Premium_Subscription(models.Model):
    description = models.CharField(max_length=500, default=lorem)
    days_time = models.IntegerField(default=60)
    schedules_nb = models.IntegerField(default=30)
    sites_limites = models.IntegerField(default=20)
    profil = models.OneToOneField(Profil,
            related_name='premium_subscription',null=True, on_delete=models.CASCADE
            )

    def __str__(self):
        return 'Premium Offer %s' % (self.id)

class Gold_Subscription(models.Model):
    description = models.CharField(max_length=500, default=lorem)
    days_time = models.IntegerField(default=80)
    schedules_nb = models.IntegerField(default=40)
    sites_limites = models.IntegerField(default=30)
    profil = models.OneToOneField(Profil,
            related_name='gold_subscription',null=True, on_delete=models.CASCADE
            )

    def __str__(self):
        return 'Gold Offer %s' % (self.id)


class Schedule(models.Model):

    ALIBABA_API_CATEGORIES = (
    ('3', 'Apparel & Accessories'),
    ('34', 'Automobiles & Motorcycles'),
    ('1501', 'Baby Products'),
    ('66', 'Beauty & Health'),
    ('7', 'Computer & Networking'),
    ('13', 'Construction & Real Estate'),
    ('44', 'Consumer Electronics'),
    ('100008578', 'Customized Products'),
    ('5', 'Electrical Equipment & Supplies'),
    ('502', 'Electronic Components & Supplies'),
    ('2', 'Food'),
    ('1503', 'Furniture'),
    ('200003655', 'Hair & Accessories'),
    ('42', 'Hardware'),
    ('15', 'Home & Garden'),
    ('6', 'Home Appliances'),
    ('200003590', 'Industry & Business'),
    ('36', 'Jewelry & Watch'),
    ('39', 'Lights & Lighting'),
    ('1524', 'Luggage & Bags'),
    ('21', 'Office & School Supplies'),
    ('509', 'Phones & Telecommunications'),
    ('30', 'Security & Protection'),
    ('322', 'Shoes'),
    ('200001075', 'Special Category'),
    ('18', 'Sports & Entertainment'),
    ('1420', 'Tools'),
    ('26', 'Toys & Hobbies'),
    ('1511', 'Watches'),
    ('320', 'Wedding & Events')
    )
    #en,pt,ru,es,fr,id,it,nl,tr,vi,th,de,ko,ja,ar,pl,he
    ALIBABA_API_LANGUAGE = (
    ('en', 'English'),
    ('pt','Portuguese'),
    ('es','Espagnol'),
    ('fr','French'),
    ('id','Indian'),
    ('it','Italian'),
    ('nl','Netherland'),
    )

    ALIBABA_API_CURRENCY = (
    ('USD','USD'),
    ('RUB','RUB'),
    ('GBP','GBP'),
    ('BRL','BRL')
    )

    HIGHQUALITY = (
    (True, 'Yes'),
    (False, 'No')
    )


    AliExpress_key = models.CharField(max_length=6)
    AliExpress_Id = models.CharField(max_length=20)
    AliExpress_fields = models.CharField(max_length=200,
                                        default=
                                        'productId,productUrl,productTitle,salePrice,originalPrice,imageUrl'
                                        )
    AliExpress_keywords = models.CharField(max_length=200)
    AliExpress_category = models.CharField(max_length = 100, choices=ALIBABA_API_CATEGORIES)
    AliExpress_language = models.CharField(max_length = 100, choices=ALIBABA_API_LANGUAGE)
    AliExpress_Currency = models.CharField(max_length= 100, choices=ALIBABA_API_CURRENCY)
    AliExpress_highquality = models.BooleanField(choices=HIGHQUALITY)
    AliExpress_Increment = models.IntegerField(default=1000)
    woocommerce_url = models.CharField(max_length=150)
    woocommerce_consumer_key = models.CharField(max_length=200)
    woocommerce_secret_key = models.CharField(max_length=100)
    keywords = models.CharField(max_length=300)

    active = models.BooleanField(default=True)
    schedule_start = models.DateTimeField(default = timezone.now())
    hours = models.IntegerField(default=24)
    profil = models.ForeignKey(Profil,
        on_delete=models.CASCADE,
        related_name='schedule'
        )

    schedule_file = models.FileField(upload_to=user_directory_path)
    schedule_file_csv = models.FileField(upload_to=user_directory_path)
    file_state = models.CharField(max_length=1, default='P')

    def __str__(self):
        return 'Request %s' % (self.id)

    def decrease_hour(self):
        self.hours = self.hours -1

    def ali_import(self):
        mainurl = 'http://gw.api.alibaba.com/openapi/param2/2/portals.open/api.listPromotionProduct/'
        url = mainurl + self.AliExpress_key + '?fields=' + self.AliExpress_fields+ '&keywords='+ self.AliExpress_keywords
        payload = {
            'pageSize': 40,
            'highQualityItems': self.AliExpress_highquality,
            'language': self.AliExpress_language,
            'sort': 'volumeDown',
            'categoryId' : int(self.AliExpress_category),
            'pageNo': 1
        }
        r = requests.get(url, params=payload)
        getlist = r.text
        tojson = json.loads(getlist)
        getlistproducts = tojson['result']['products']
        json_file = ContentFile(getlist)
        self.schedule_file.save('a.json',json_file,save=True)
        response = {
            "url" : self.schedule_file.url,
            "path" : self.schedule_file.path
        }

        return response



class Notification(models.Model):
    active = models.BooleanField(default=False)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length = 200, default='This is a notification')
    schedule = models.OneToOneField(Schedule,
                on_delete=models.CASCADE,
                related_name='notification'
                )
    link = models.CharField(max_length = 100, default='')
    profil = models.ForeignKey(Profil,
        on_delete=models.CASCADE,
        related_name='notification'
        )
