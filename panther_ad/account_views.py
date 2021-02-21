import logging

from django.contrib.auth.hashers import check_password
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from panther_ad.models import *

logger = logging.getLogger(__name__)


def account_activity(request):
    if not request.user.is_authenticated:
        return render(request, 'panther_ad/signin.html')
    else:
        transaction_history = TransactionHistory.objects.filter(user_id=request.user.id).order_by('-date')
        return render(request, 'panther_ad/account_activity.html', {"user": request.user,
                                                                    "profile": Profile.objects.get(user_id=request.user.id),
                                                                    "transaction_history": transaction_history
                                                                    })


@api_view(['POST'])
def top_up_balance(request):
    if not request.user.is_authenticated:
        return render(request, 'panther_ad/signin.html')
    else:
        if request.method == 'POST':
            # logger.debug('tub 1')
            # logger.debug(request.POST)
            try:
                TransactionHistory.objects.create(trans_type='Top up balance', description='Top up balance', amount=request.POST['amount'],
                                                  user_id=request.user.id)
                prf = Profile.objects.get(user_id=request.user.id)
                prf.current_account_balance = F('current_account_balance') + request.POST['amount']
                prf.total_deposit = F('total_deposit') + request.POST['amount']
                prf.save()
                return Response({"success": "T"})
            except Exception as e:
                logger(e)
                return Response({"success": "F"})
        elif request.method == 'GET':
            return render(request, "panther_ad/account_activity.htm")


def view_profile(request):
    if request.user.is_authenticated:
        return render(request, 'panther_ad/user_profile.html', {"user": request.user, "profile": Profile.objects.get(user_id=request.user.id)})
    else:
        return render(request, 'panther_ad/signin.html')


def save_profile(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        gender = request.POST['gender']
        phone = request.POST['phone']
        address = request.POST['address']

        try:

            # date_time_obj = datetime.datetime.strptime(birth_date, "%Y-%m-%d")

            # logger.debug(birth_date)
            # logger.debug(date_time_obj)

            User.objects.filter(id=request.user.id).update(
                first_name=first_name, last_name=last_name, )
            Profile.objects.filter(user_id=request.user.id).update(
                gender=gender, address=address, phone=phone)

            return HttpResponseRedirect(reverse('panther_ad:user_profile'))
        except Exception as e:
            logger.error(e)
            return render(request, 'panther_ad/user_profile.html', {
                "update_faile": 'True'
            })
    elif request.method == 'GET':
        return redirect('panther_ad:index')


@api_view(['POST'])
def change_password(request):
    if request.method == 'POST':
        logger.debug('4')
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        logger.debug(request.user.id)
        try:
            if check_password(request.POST['old_password'], User.objects.get(id=request.user.id).password):
                u = User.objects.get(id=request.user.id)
                u.set_password(new_password)
                u.save()
                return Response({"success": "T", })
            else:
                logger.debug('2')
                return Response({"success": "F", })
        except Exception as e:
            logger.debug(e)
            return Response({"success": "F"})
    elif request.method == 'GET':
        return redirect('panther_ad:index')
    # return Response({"success":"Password has been updated!", "test_success":"succeeded"})
