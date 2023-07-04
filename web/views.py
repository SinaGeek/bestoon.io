from json import JSONEncoder
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from web.models import User, Token, Expense, Income
from datetime import datetime
# Create your views here.

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