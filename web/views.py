import string
from json import JSONEncoder
from django.conf import settings
from random import random
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import  User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from web.models import User, Token, Expense, Income , Passwordresetcodes
from datetime import datetime
from django.db.models import Sum,Count
from .utils import grecaptcha_verify


# Create your views here.

# create random string for Toekn
random_str = lambda N: ''.join(
    random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))


# register (web)
def register(request):
    if 'requestcode' in request.POST:  # form is filled. if not spam, generate code and save in db, wait for email confirmation, return message
        # is this spam? check reCaptcha
        if not grecaptcha_verify(request):  # captcha was not correct
            context = {
                'message': 'کپچای گوگل درست وارد نشده بود. شاید ربات هستید؟ کد یا کلیک یا تشخیص عکس زیر فرم را درست پر کنید. ببخشید که فرم به شکل اولیه برنگشته!'}  # TODO: forgot password
            return render(request, 'register.html', context)

        # duplicate email
        if User.objects.filter(email=request.POST['email']).exists():
            context = {
                'message': 'متاسفانه این ایمیل قبلا استفاده شده است. در صورتی که این ایمیل شما است، از صفحه ورود گزینه فراموشی پسورد رو انتخاب کنین. ببخشید که فرم ذخیره نشده. درست می شه'}  # TODO: forgot password
            # TODO: keep the form data
            return render(request, 'register.html', context)
        # if user does not exists
        if not User.objects.filter(username=request.POST['username']).exists():
            code = get_random_string(length=32)
            now = datetime.now()
            email = request.POST['email']
            password = make_password(request.POST['password'])
            username = request.POST['username']
            temporarycode = Passwordresetcodes(
                email=email, time=now, code=code, username=username, password=password)
            temporarycode.save()
            #message = PMMail(api_key=settings.POSTMARK_API_TOKEN,
            #                 subject="فعالسازی اکانت بستون",
            #                 sender="jadi@jadi.net",
            #                 to=email,
            #                 text_body=" برای فعال کردن اکانت بستون خود روی لینک روبرو کلیک کنید: {}?code={}".format(
            #                     request.build_absolute_uri('/accounts/register/'), code),
            #                 tag="account request")
            #message.send()
            message = 'ایمیلی حاوی لینک فعال سازی اکانت به شما فرستاده شده، لطفا پس از چک کردن ایمیل، روی لینک کلیک کنید.'
            message = 'قدیم ها ایمیل فعال سازی می فرستادیم ولی الان شرکتش ما رو تحریم کرده (: پس راحت و بی دردسر'
            body = " برای فعال کردن اکانت بستون خود روی لینک روبرو کلیک کنید: <a href=\"{}?code={}\">لینک رو به رو</a> ".format(request.build_absolute_uri('/accounts/register/'), code)
            message = message + body
            context = {
                'message': message }
            return render(request, 'index.html', context)
        else:
            context = {
                'message': 'متاسفانه این نام کاربری قبلا استفاده شده است. از نام کاربری دیگری استفاده کنید. ببخشید که فرم ذخیره نشده. درست می شه'}  # TODO: forgot password
            # TODO: keep the form data
            return render(request, 'register.html', context)
    elif 'code' in request.GET:  # user clicked on code
        code = request.GET['code']
        if Passwordresetcodes.objects.filter(
                code=code).exists():  # if code is in temporary db, read the data and create the user
            new_temp_user = Passwordresetcodes.objects.get(code=code)
            newuser = User.objects.create(username=new_temp_user.username, password=new_temp_user.password,
                                          email=new_temp_user.email)
            this_token = get_random_string(length=48)
            token = Token.objects.create(user=newuser, token=this_token)
            # delete the temporary activation code from db
            Passwordresetcodes.objects.filter(code=code).delete()
            context = {
                'message': 'اکانت شما ساخته شد. توکن شما {} است. آن را ذخیره کنید چون دیگر نمایش داده نخواهد شد! جدی!'.format(
                    this_token)}
            return render(request, 'index.html', context)
        else:
            context = {
                'message': 'این کد فعال سازی معتبر نیست. در صورت نیاز دوباره تلاش کنید'}
            return render(request, 'register.html', context)
    else:
        context = {'message': ''}
        return render(request, 'register.html', context)
        
        
@csrf_exempt
@require_POST
def login(request):
    # check if POST objects has username and password
    if 'username' and 'password' in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        this_user = get_object_or_404(User, username=username)
        if (check_password(password, this_user.password)):  # authentication
            this_token = get_object_or_404(Token, user=this_user)
            token = this_token.token
            context = {}
            context['result'] = 'ok'
            context['token'] = token
            # return {'status':'ok','token':'TOKEN'}
            return JsonResponse(context, encoder=JSONEncoder)
        else:
            context = {}
            context['result'] = 'error'
            # return {'status':'error'}
            return JsonResponse(context, encoder=JSONEncoder)


def index(request):
    context = {}
    return render(request, 'index.html', context)

@csrf_exempt
def generalstat(request):
    #TODO: should get valid duraion from (date) to (date) if nor 1 mounth.
    #TODO: Is the token valid!
    
    this_token = request.GET['token']
    this_user= User.objects.filter(token__token = this_token ).get()

    income = Income.objects.filter(user = this_user).aaggregate(Count('amount'), Sum('amount'))
    expense = Expense.objects.filter(user = this_user).aaggregate(Count('amount'), Sum('amount'))
    context ={}
    context['expense'] = expense
    context['income'] = income
    return JsonResponse(context, encoder= JSONEncoder) 


@csrf_exempt
def submit_expense(request):
    '''user submit a request an expense'''
    #TODO: validate date user may be fake, token may be fake, amount may be invalide
    this_token = request.GET['token']
    this_user= User.objects.filter(token__token = this_token ).get()
    print(request.GET)
    if 'date' not in request.GET:
        now = datetime.now()
    Expense.objects.create(user = this_user, amount = request.GET['amount'],
                            text=request.GET['text'], date=now )    
    return JsonResponse({
        'status' : 'ok'},
        encoder = JSONEncoder)

def submit_income(request):
    '''user submit a request an income'''
    #TODO: validate date user may be fake, token may be fake, amount may be invalide
    this_token = request.GET['token']
    this_user= User.objects.filter(token__token = this_token ).get()
    print(request.GET)
    if 'date' not in request.GET:
        now = datetime.now()
    Income.objects.create(user = this_user, amount = request.GET['amount'],
                            text=request.GET['text'], date=now )    
    return JsonResponse({
        'status' : 'ok'},
        encoder = JSONEncoder)

