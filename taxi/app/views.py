from django.contrib import messages
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from . forms import CreateUser
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
import random
from .models import PreRegistration
from .forms import VerifyForm,LoginForm
from django.contrib.auth import login,logout,authenticate
# Create your views here.

def creatingOTP():
    otp = ""
    for i in range(6):
        otp+= f'{random.randint(0,9)}'
    return otp

def sendEmail(email):
    otp = creatingOTP()
    send_mail(
    'One Time Password',
    f'Your OTP pin is {otp}',
    settings.EMAIL_HOST_USER,
    [email],
    fail_silently=False,
    )
    return otp


def createUser(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = CreateUser(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                otp = sendEmail(email)
                dt = PreRegistration(first_name=form.cleaned_data['first_name'],last_name=form.cleaned_data['last_name'],username= form.cleaned_data['username'],email=email,otp=otp,password1 = form.cleaned_data['password1'],password2 = form.cleaned_data['password2'])
                dt.save()
                return HttpResponseRedirect('/verify/')
                
                
        else:
            form = CreateUser()
        return render(request,"newuser.html",{'form':form})
    else:
        return HttpResponseRedirect('/success/')

# def login_function(request):
#     if not request.user.is_authenticated:
#         if request.method == 'POST':
#             form = LoginForm(request=request,data=request.POST)
#             if form.is_valid():
#                 username = form.cleaned_data['username']
#                 password = form.cleaned_data['password']
#                 usr = authenticate(username=username,password = password)
#                 if usr is not None:
#                     login(request,usr)
#                     return HttpResponseRedirect('/success/')
#         else:
#             form = LoginForm()
#         return render(request,'login.html',{'form':form})
#     else:
#         return HttpResponseRedirect('/success/')

def verifyUser(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = VerifyForm(request.POST)
            if form.is_valid():
                otp = form.cleaned_data['otp']
                data = PreRegistration.objects.filter(otp = otp)
                if data:
                    username = ''
                    first_name = ''
                    last_name = ''
                    email = ''
                    password1 = ''
                    for i in data:
                        print(i.username)
                        username = i.username
                        first_name = i.first_name
                        last_name = i.last_name
                        email = i.email
                        password1 = i.password1

                    user = User.objects.create_user(username, email, password1)
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()
                    data.delete()
                    messages.success(request,'Account is created successfully!')
                    return HttpResponseRedirect('/verify/')   
                else:
                    messages.success(request,'Entered OTP is wrong')
                    return HttpResponseRedirect('/verify/')
        else:            
            form = VerifyForm()
        return render(request,'verify.html',{'form':form})
    else:
        return HttpResponseRedirect('/success/')

def success(request):
    if request.user.is_authenticated:
        return render(request,'success.html')
    else:
        return HttpResponseRedirect('/')

def logout_function(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/')
    
    
    
    
from django.shortcuts import get_object_or_404, render
import calendar
from datetime import datetime
from .models import *
from datetime import datetime



from django.shortcuts import render, get_object_or_404, redirect
from .models import Car, CarRental, Cities,PreRegistration  # Adjust the import path based on your project structure


from django.contrib.auth.decorators import login_required

# views.py

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Car, CarRental, Cities
from django.shortcuts import render
from datetime import datetime

@login_required
def home(request):
    if request.method == 'POST':
        car_id = request.POST.get('car')
        car = get_object_or_404(Car, pk=car_id)

        city_id = request.POST.get('to')
        city = get_object_or_404(Cities, pk=city_id)
        
        # Retrieve the email from PreRegistration model
        pre_registration = PreRegistration.objects.filter(user=request.user).first()

        email = PreRegistration.email
        print(f"Email to be used: {email}")  # Debugging line

        car_rental_data = {
            'user': request.user,
            'car': car,
            'pickup_date': request.POST.get('pickup_date'),
            'start': request.POST.get('start'),
            'to': city,
            'distance_traveled': request.POST.get('distance_traveled', '0.0'),
            'status': request.POST.get('status'),
        }

        car_rental = CarRental(**car_rental_data)
        car_rental.save()

        # After saving the CarRental instance
        send_booking_confirmation_email(email, car_rental.status, car_rental.pickup_date, car_rental.car, car_rental.user)
        return redirect('/invoice')
   
    # Rest of your code...

   

    object_list = CarRental.objects.all()
    another_model = Car.objects.all()
    cities = Cities.objects.all()

    return render(request, 'Home.html', {'object_list': object_list, 'another_model': another_model, 'cities': cities})


def send_booking_confirmation_email(user_email, booking_status,booking_pickup_date,booking_car,booking_user):
    try:
        subject = 'Car Booking Confirmation'
        
        # Customize the email content using a template
        context = {'booking_status': booking_status,'booking_pickup_date':booking_pickup_date,
                   'booking_car': booking_car,
                   'booking_user':booking_user}
        email_html_message = render_to_string('booking_confirmation_email.html', context)
        email_text_message = strip_tags(email_html_message)
        
        from_email = 'jagadeeshgoudayr@gmail.com'  # Update with your email
        to_email = [user_email]
        print(to_email)

        email = EmailMultiAlternatives(subject, email_text_message, from_email, to_email)
        email.attach_alternative(email_html_message, 'text/html')
        email.send()

        print("Email sent successfully!")

    except Exception as e:
        print(f"Email sending failed: {e}")



def driverss(request):
    object_list=drivers.objects.all()
    return render(request,"drivers.html",{'object_list':object_list})


def getcars(request):
    object_list=Car.objects.all()
    return render(request,"cars.html",{'object_list':object_list})

def more_details_view(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    context = {
        'car': car
    }


    return render(request, 'MoreDetails.html', context)


from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required


def login_form(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            usern = form.cleaned_data['username']
            userp = form.cleaned_data['password']
            user = authenticate(username= usern, password=userp)

            if user is not None:
                login(request, user)
                return redirect('/home')

    else:
        form = AuthenticationForm()
    context= {'form':form}
    return render(request, 'login.html', context)



#logout
@login_required(login_url='/')
def logout_form(request):
    logout(request)
    #return redirect('/login')
    return render(request, 'logout.html')

@login_required(login_url='login')
def changepassword(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PasswordChangeForm(user=request.user, data=request.POST)

            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                return redirect('login')
            else:
                return HttpResponse("password is not matching")
        else:
            form = PasswordChangeForm(user= request.user)
            context = {'form':form}
            return render(request, 'changepassword.html',context)
    else:
        return redirect('/changepassword')
    
    
from django.shortcuts import render
from .models import CarRental, PreRegistration  # Import your models

def info(request):
    user_bookings = CarRental.objects.filter(user=request.user)
    
    if user_bookings.exists():
        latest_booking = user_bookings.order_by('-id').first()
        object_list = [latest_booking] if latest_booking else []
    else:
        object_list = []

    another_model = PreRegistration.objects.filter(user=request.user)
    car = Car.objects.all()  # Assuming 'Car' is your Car model
    context = {
        'object_list': object_list,
        'another_model': another_model,
        'car': car,
    }

    if not object_list:
        context['no_history_message'] = "You do not have any invoice history."

    return render(request, "invoice.html", context)


from django.views.generic import ListView
from django.db.models import Q
class SearchResultsView(ListView):
    model=drivers
    template_name="search.html"
    def get_queryset(self):
        query = self.request.GET.get("q")
        object_list = drivers.objects.filter(Q(name__icontains = query)) | drivers.objects.filter(Q(gender__contains = query))
        return object_list


from django.views.generic import ListView
from django.db.models import Q
class SearchResultsView(ListView):
    model=Car
    template_name="search1.html"
    def get_queryset(self):
        query = self.request.GET.get("q")
        object_list = Car.objects.filter(Q(city__icontains = query)) |Car.objects.filter(Q(brand__contains=query))
        return object_list

# payment page

from django.shortcuts import render
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import CarRental

import razorpay

razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

def homepage(request):
    # Retrieve the latest car rental or adjust your logic based on your requirements
    latest_car_rental = CarRental.objects.latest('id')  # Assuming you have a 'pickup_date' field in CarRental

    currency = 'INR'
    amounts = latest_car_rental.get_total
    amount=int(amounts*100)

    razorpay_order = razorpay_client.order.create(dict(
        amount=amount,
        currency=currency,
        payment_capture='0'
    ))

    razorpay_order_id = razorpay_order['id']
    callback_url = 'paymenthandler/'

    context = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
        'razorpay_amount':amount,
        'currency': currency,
        'callback_url': callback_url
    }

    return render(request, 'index.html', context=context)

# The rest of your payment handling view remains unchanged

@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result is not None:
                try:
                    # Get the car rental associated with the Razorpay order
                    car_rental = CarRental.objects.get(pk=razorpay_order_id)

                    # Use the get_total property to calculate the expected amount
                    amount = car_rental.get_total()

                    razorpay_client.payment.capture(payment_id, amount)
                    return render(request, 'paymentsuccess.html')
                except CarRental.DoesNotExist:
                    return render(request, 'paymentfail.html')
            else:
                return render(request, 'paymentfail.html')
        except Exception as e:
            print(e)
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()
