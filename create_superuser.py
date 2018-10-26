from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from woocommerceAppProject.woocommerceApp.models import Subscription
email = 'admin@example.com'
password = 'woocommerceadmin'

try:
    User.objects.get(username='admin')
    print ("User 'admin' already exist")
except User.DoesNotExist:
    User.objects.create_superuser('admin', email, password)
    Subscription.objects.create(name="Free Trial")
    print ("User 'admin created with default password'")
