import logging
import random
from datetime import datetime as dt

import requests
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import FileSystemStorage
from django.db import IntegrityError
from django.db.models import F
from django.http import Http404, HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.utils import json

from panther_ad import database
from panther_ad.models import *

logger = logging.getLogger(__name__)


def index(request):
    if request.user.is_authenticated:
        campaigns_list = Campaign.objects.filter(
            user_id=request.user.id).order_by('-date_created')

        return render(request, 'panther_ad/dashboard.html', {"user": request.user, "campaigns": campaigns_list})
    else:
        return render(request, 'panther_ad/signin.html')


def dashboard_data(request, campaign_id):
    if request.is_ajax():
        print(campaign_id)
        data = load_dashboard(campaign_id)
        if data is None:
            raise Http404
        else:
            data = json.dumps(data)
            return HttpResponse(data, content_type='application/json')
    else:
        raise Http404


def sign_in(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('panther_ad:index'))
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('panther_ad:index'))
            else:
                return render(request, 'panther_ad/signin.html', {'message': 'Invalid login'})
        elif request.method == 'GET':
            return render(request, 'panther_ad/signin.html')


def signup(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('panther_ad:index'))
    else:
        if request.method == 'POST':
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            repassword = request.POST['repassword']
            if password.__eq__(repassword):
                try:
                    user = User.objects.create_user(username, email, password)
                    user.save()
                    return HttpResponseRedirect(reverse('panther_ad:signin'))
                except IntegrityError:
                    return render(request, 'panther_ad/signup.html', {'message': 'Username or Email existed'})
            else:
                return render(request, 'panther_ad/signup.html', {'message': 'Password not matched'})
        elif request.method == 'GET':
            return render(request, 'panther_ad/signup.html')


def signout(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect(reverse('panther_ad:index'))
    else:
        return HttpResponseRedirect(reverse('panther_ad:index'))


def forgot(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('panther_ad:index'))
    else:
        if request.method == 'POST':
            email = request.POST['email']
            pass
            return
        elif request.method == 'GET':
            return render(request, 'panther_ad/forgot.html')


def create_ad(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('panther_ad:index'))
    else:
        if request.method == 'POST':
            size = request.POST['size']
            name = request.POST['name']

            uploaded_banner = request.FILES['upload_banner']
            uploaded_banner.name = uploaded_banner.name.replace(' ', '_')

            fss = FileSystemStorage()
            file_name = fss.save(uploaded_banner.name, uploaded_banner)
            url = fss.url(file_name)

            logger.debug(fss.size(file_name))
            logger.debug(fss.url(file_name))
            logger.debug(fss.path(file_name))

            try:
                Ad.objects.create(user_id=request.user.id,
                                  name=name, url=url, size=size)
                return redirect('panther_ad:ads')
            except Exception as e:
                logger.error(e)
                return render(request, 'panther_ad/create-new-ad.html',
                              {"error_message": 'Something went wrong!'})
        elif request.method == 'GET':
            return render(request, 'panther_ad/create-new-ad.html')


def create_campaign(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('panther_ad:signin'))
    else:
        user_id = request.user.id
        if request.method == 'POST':
            name = request.POST['name']
            description = request.POST['description']
            budget = request.POST['budget']
            start_date = request.POST['str_date_1']
            end_date = request.POST['end_date_1']
            destination_url = request.POST['destination_url']

            target_os = request.POST.getlist('target_os')
            target_city = request.POST.getlist('target_city')
            target_browser = request.POST.getlist('target_browser')

            ad_checked_list = request.POST.getlist('ad_checked_list')

            logger.debug(ad_checked_list)
            try:
                Campaign.objects.create(user_id=user_id, name=name, description=description,
                                        budget=budget, spent_amount=0,
                                        start_date=datetime.datetime.strptime(start_date, "%d %B, %Y"),
                                        end_date=datetime.datetime.strptime(end_date, "%d %B, %Y"),
                                        destination_url=destination_url, status='Pending')

                # get the id of the created campaign
                cp_id = Campaign.objects.filter(
                    user_id=user_id).latest('id').id

                logger.debug(cp_id)
                cp = Campaign.objects.get(id=cp_id)
                logger.debug(cp.id)
                # chosen Ad
                for ad_id in ad_checked_list:
                    # AdInCampaign.objects.create(ad_id=ad_id, campaign_id=cp_id)
                    ad = Ad.objects.get(id=ad_id)
                    logger.debug(ad.id)
                    # ad.campaigns.add(cp)
                    cp.ads.add(ad)
                # insert into target_os table with that campaign_id
                for os_id in target_os:
                    TargetOS.objects.create(
                        campaign_id=cp_id, os_id=os_id)
                for city_id in target_city:
                    TargetCity.objects.create(
                        campaign_id=cp_id, city_id=city_id)
                for browser_id in target_browser:
                    TargetBrowser.objects.create(
                        campaign_id=cp_id, browser_id=browser_id)

                prf = Profile.objects.get(user_id=request.user.id)
                prf.current_account_balance = F(
                    'current_account_balance') - budget
                prf.total_spent = F('total_spent') + budget
                prf.save()

                TransactionHistory.objects.create(
                    trans_type='Provide budget', description='Provide budget for campaign \'' + name + '\'',
                    amount=budget, user_id=request.user.id)

                return redirect('panther_ad:campaigns')

            except Exception as e:
                logger.error(e)
                browser_list = Browser.objects.all()
                os_list = OS.objects.all()
                city_list = City.objects.all()
                return render(request, 'panther_ad:create_campaign',
                              {"error_message": 'Create campaign failed!',
                               "browser_list": browser_list,
                               "os_list": os_list,
                               "city_list": city_list
                               })

        elif request.method == 'GET':
            browser_list = Browser.objects.all()
            os_list = OS.objects.all()
            city_list = City.objects.all()
            ad_list = Ad.objects.filter(user_id=request.user.id)
            return render(request, 'panther_ad/create-new-campaign.html', {
                "browser_list": browser_list,
                "os_list": os_list,
                "city_list": city_list,
                "user_profile": Profile.objects.get(user_id=request.user.id),
                "ad_list": ad_list
            })


def user_profile(request):
    if request.user.is_authenticated:
        return render(request, 'panther_ad/user.profile.html')
    else:
        return HttpResponseRedirect(reverse('panther_ad:index'))


# display all campaign belong to user Paging
def campaign_list(request):
    if request.user.is_authenticated:
        # logger.debug('camp')
        campaigns_list = Campaign.objects.filter(
            user_id=request.user.id).order_by('-date_created')
        for cp in campaigns_list:
            cp.spent_amount = round(cp.spent_amount, 3)
        logger.debug(campaign_list)

        return render(request, 'panther_ad/campaigns.html', {'campaigns': campaigns_list})
    else:
        return render(request, 'panther_ad/signin.html')


# display all ads belong to users
def ad_list(request):
    if request.user.is_authenticated:
        ads = Ad.objects.filter(
            user_id=request.user.id).order_by('-date_created')

        logger.debug(ads)
        # paginator = Paginator(ads_list, 5)
        # page = request.GET.get('page')
        # ads = paginator.get_page(page)
        return render(request, 'panther_ad/ads.html', {
            'ads': ads,
        })
    else:
        return render(request, 'panther_ad/signin.html')


# display campaign detail informations
def campaign_detail(request, campaign_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            extra_budget = request.POST['extra_budget']

            cp = Campaign.objects.get(id=campaign_id)
            cp.budget = F('budget') + request.POST['extra_budget']
            cp.save()

            prf = Profile.objects.get(user_id=request.user.id)
            prf.current_account_balance = F('current_account_balance') - request.POST['extra_budget']
            prf.save()

            # handle target object change
            target_city = request.POST.getlist('target_city')
            target_os = request.POST.getlist('target_os')
            target_browser = request.POST.getlist('target_browser')

            logger.debug(target_city)
            logger.debug(target_os)
            logger.debug(target_browser)

            # update target city
            for id in target_city:
                TargetCity.objects.get_or_create(campaign_id=campaign_id, city_id=id)
            TargetCity.objects.filter(campaign_id=campaign_id).exclude(city__in=target_city).delete()

            # update target os
            for id in target_os:
                TargetOS.objects.get_or_create(campaign_id=campaign_id, os_id=id)
            TargetOS.objects.filter(campaign_id=campaign_id).exclude(os__in=target_os).delete()

            # update target browser
            logger.debug(target_browser)
            for id in target_browser:
                TargetBrowser.objects.get_or_create(campaign_id=campaign_id, browser_id=id)
            TargetBrowser.objects.filter(campaign_id=campaign_id).exclude(browser__in=target_browser).delete()

            ad_check_list = request.POST.getlist('ad_checked_list')
            for id in ad_check_list:
                AdInCampaign.objects.get_or_create(campaign_id=campaign_id, ad_id=id)
            AdInCampaign.objects.filter(campaign_id=campaign_id).exclude(ad__in=ad_check_list).delete()

            return HttpResponseRedirect(reverse('panther_ad:campaign_detail', kwargs={
                'campaign_id': campaign_id,
            }))

        elif request.method == 'GET':
            if is_exist_campaign(campaign_id):
                # current_userid = request.user.id
                # campaign_userid = Campaign.objects.get(id=campaign_id).user_id
                if user_own_campaign(request.user.id, Campaign.objects.get(id=campaign_id).user_id):
                    campaign = database.get_campaign(campaign_id)

                    # get all Ad belong to current user
                    ad_in_campaign = campaign.ads.all()

                    # get all Ad do not belong to campaign
                    ad_not_in_campaign = Ad.objects.filter(campaign__isnull=True).filter(user_id=request.user.id)
                    logger.debug(ad_in_campaign)
                    logger.debug(ad_not_in_campaign)
                    logger.debug(campaign)

                    return render(request, 'panther_ad/campaign_detail.html', {
                        'campaign': campaign,
                        'ad_in_campaign': ad_in_campaign,
                        'ad_not_in_campaign': ad_not_in_campaign,
                        'start_date': campaign.start_date.strftime('%Y-%m-%d'),
                        'end_date': campaign.end_date.strftime('%Y-%m-%d'),
                        "profile": Profile.objects.get(user_id=request.user.id),
                        "target_os": OS.objects.exclude(id__in=[tg.os_id for tg in TargetOS.objects.filter(campaign_id=campaign_id)]),
                        "target_city": City.objects.exclude(id__in=[tg.city_id for tg in TargetCity.objects.filter(campaign_id=campaign_id)]),
                        "target_browser": Browser.objects.exclude(
                            id__in=[tg.browser_id for tg in TargetBrowser.objects.filter(campaign_id=campaign_id)]),
                        "campaign_target_os": OS.objects.filter(id__in=[tg.os_id for tg in TargetOS.objects.filter(campaign_id=campaign_id)]),
                        "campaign_target_city": City.objects.filter(id__in=[tg.city_id for tg in TargetCity.objects.filter(campaign_id=campaign_id)]),
                        "campaign_target_browser": Browser.objects.filter(
                            id__in=[tg.browser_id for tg in TargetBrowser.objects.filter(campaign_id=campaign_id)])
                    })
                else:
                    return render('panther_ad/not_found.html')
            else:
                return render(request, 'panther_ad/not_found.html')
    elif campaign_id not in Campaign.objects.filter(user_id=request.user.id):
        return render(request, 'panther_ad/not_found.html')
    else:
        return render(request, 'panther_ad/signin.html')


def campaign_statistic(request, campaign_id):
    load_dashboard()
    return render(request, 'panther_ad/dashboard.v1.html')


@api_view(['POST'])
def get_ad(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        body['city'] = body['city'].lower().replace(' ', '')
        body['os'] = body['os'].lower().replace(' ', '')
        body['browser'] = body['browser'].lower().replace(' ', '')
        logger.debug(body)
        # TEST CODE
        # get running campaign
        campaign_query_set = Campaign.objects.filter(status='Running')
        campaign_dict = {}
        final_campaign_id = ""
        # classify campaign to get match and none
        for campaign in campaign_query_set:
            # define how many case of request match with campaign
            match = 0
            # define how many case of campaign is all (none)
            none = 0
            filter_city = City.objects.filter(
                targetcity__campaign_id=campaign.id)
            filter_os = OS.objects.filter(targetos__campaign_id=campaign.id)
            filter_browser = Browser.objects.filter(
                targetbrowser__campaign_id=campaign.id)
            if filter_city.count() > 0:
                for city in filter_city:
                    city.name = city.name.lower().replace(' ', '')
                    if body['city'].lower().__contains__(city.name):
                        match += 1
                        break
            else:
                none += 1
            if filter_os.count() > 0:
                for os in filter_os:
                    os.name = os.name.lower().replace(' ', '')
                    if body['os'].lower().__contains__(os.name):
                        match += 1
                        break
            else:
                none += 1
            if filter_browser.count() > 0:
                for browser in filter_browser:
                    browser.name = browser.name.lower().replace(' ', '')
                    if body['browser'].lower().__contains__(browser.name):
                        match += 1
                        break
            else:
                none += 1
            campaign_dict[campaign.id] = {'match': match, 'none': none}
        valid_all_cam = []
        valid_2in3_cam = []
        valid_1in3_cam = []
        banner_width = int(body['banner_w'].replace("px", ""))
        banner_height = int(body['banner_h'].replace("px", ""))
        banner_size = str(banner_width) + 'x' + str(banner_height)
        logger.debug(campaign_dict)
        # classify campaign depend on match and none
        for campaign_id in campaign_dict.keys():
            match_all_case = [campaign_dict[campaign_id]['match'] == 3,
                              campaign_dict[campaign_id]['match'] == 2 and campaign_dict[campaign_id]['none'] == 1,
                              campaign_dict[campaign_id]['match'] == 1 and campaign_dict[campaign_id]['none'] == 2]
            match_2in3_case = [campaign_dict[campaign_id]['match'] == 2 and campaign_dict[campaign_id]['none'] == 0,
                               campaign_dict[campaign_id]['match'] == 1 and campaign_dict[campaign_id]['none'] == 1,
                               campaign_dict[campaign_id]['match'] == 0 and campaign_dict[campaign_id]['none'] == 2]
            match_1in3_case = [campaign_dict[campaign_id]['match'] == 1 and campaign_dict[campaign_id]['none'] == 0,
                               campaign_dict[campaign_id]['match'] == 0 and campaign_dict[campaign_id]['none'] == 1]
            filtered_ad = Ad.objects.filter(campaign=Campaign.objects.get(id=campaign_id), size=banner_size)
            logger.debug(filtered_ad)
            if filtered_ad.count() > 0:
                if any(match_all_case):
                    valid_all_cam.append(campaign_id)
                elif any(match_2in3_case):
                    valid_2in3_cam.append(campaign_id)
                elif any(match_1in3_case):
                    valid_1in3_cam.append(campaign_id)
        # get random ad from final campaign
        if len(valid_all_cam) > 0:
            final_campaign_id = random.choice(valid_all_cam)
        elif len(valid_2in3_cam) > 0:
            final_campaign_id = random.choice(valid_2in3_cam)
        elif len(valid_1in3_cam) > 0:
            final_campaign_id = random.choice(valid_1in3_cam)
        # response with src of final ad
        if final_campaign_id != "":
            # get all Ad object where id in final_aic
            filtered_ad = Ad.objects.filter(campaign=Campaign.objects.get(id=campaign_id), size=banner_size)
            # get destination url
            des_url = Campaign.objects.get(id=final_campaign_id).destination_url
            final_ad = random.choice(filtered_ad)
            src = "http://panther-ad.xyz/" + str(final_ad.url)
            city = ''
            if body['regionName'].lower().replace(' ', '') == 'hanoi':
                city = 'hanoi'
            # save impression
            impression = Impression.objects.create(ad_id=final_ad.id, campaign_id=final_campaign_id,
                                                   time=timezone.now(),
                                                   city=city, os=body['os'],
                                                   browser=body['browser'], ip=body['ip'])
            save_impression_elastic(impression)
            increase_spent_amount('impression', final_campaign_id)
            # return ad
            return Response(
                {"campaign_id": final_campaign_id, "ad_id": final_ad.id, "src": src, "destination_url": des_url})
        else:
            src = 'http://panther-ad.xyz/media/default/' + banner_size + '.png'
            return Response({"campaign_id": "", "ad_id": "", "src": src, "destination_url": ""})


def increase_spent_amount(type, final_campaign_id):
    campaign = Campaign.objects.get(id=final_campaign_id)
    if type.__eq__('impression'):
        x = campaign.spent_amount + 0.0028
        campaign.spent_amount = x
        campaign.save()
    elif type.__eq__('click'):
        x = campaign.spent_amount + 0.75
        campaign.spent_amount = x
        campaign.save()
    # stop campaign if budget lower than spent amount
    if campaign.budget < campaign.spent_amount:
        campaign.STATUS = 'Finished'


@api_view(['POST'])
def save_click(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        logger.debug(body)

        ad_id = body['ad_id']
        campaign_id = body['campaign_id']
        domain = body['domain']
        city = body['city'].lower().replace(' ', '')
        city = 'hanoi'
        os = body['os'].lower().replace(' ', '')
        browser = body['browser'].lower().replace(' ', '')
        ip = body['ip']
        url = body['url']

        logger.debug(ad_id)

        try:
            ad_click = Click.objects.create(ad_id=ad_id, campaign_id=campaign_id, time=timezone.now(),
                                            city=city, os=os,
                                            browser=browser, ip=ip, url=url)
            save_click_elastic(ad_click)
            increase_spent_amount('click', campaign_id)
            return Response({"success_message": "Sucessed"})
        except Exception as e:
            logger.debug(e)
            return Response({"success_message": "Something went wrong"})


def pause_campaign(request, campaign_id):
    if request.method == 'POST':
        campaign = Campaign.objects.get(id=campaign_id)
        campaign.status = 'Paused'
        campaign.save()
        return HttpResponse()


def resume_campaign(request, campaign_id):
    if request.method == 'POST':
        campaign = Campaign.objects.get(id=campaign_id)
        campaign.status = 'Running'
        campaign.save()
        return HttpResponse()


def user_own_campaign(current_user_id, campaign_user_id):
    if current_user_id == campaign_user_id:
        return True
    else:
        return False


def is_exist_campaign(campaign_id):
    if Campaign.objects.filter(id=campaign_id).exists():
        return True
    else:
        return False


def load_dashboard(campaign_id):
    url_impression = "http://elasticsearch.panther-ad.xyz/impression/_search"
    url_click = "http://elasticsearch.panther-ad.xyz/click/_search"
    headers = {'Content-type': 'application/json'}
    impression_groupby_days = []
    click_groupby_days = []
    city_groupby_city = []
    days = []
    money_spend_inweek = []
    query_impression_click = json.dumps({
        "size": 0,
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "campaign_id": campaign_id
                    }
                },
                "filter": {
                    "range": {
                        "time": {
                            "gte": "now-6d/d",
                            "lte": "now+1d/d"
                        }
                    }
                }

            }
        },
        "aggs": {
            "group_by_month": {
                "date_histogram": {
                    "field": "time",
                    "interval": "day"
                }
            }
        }
    })
    query_city = json.dumps({
        "size": 0,
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "campaign_id": campaign_id
                    }
                }
            }
        },
        "aggs": {
            "test": {
                "terms": {"field": "city"}
            }
        }
    })
    # get impression statistic from elastic
    response_impression = requests.post(url=url_impression,
                                        headers=headers,
                                        data=query_impression_click,
                                        auth=('elastic', 'changeme'))
    # get click statistic from elastic
    response_click = requests.post(url=url_click,
                                   headers=headers,
                                   data=query_impression_click,
                                   auth=('elastic', 'changeme'))
    # get impression statistic from elastic group by city
    response_city = requests.post(url=url_impression,
                                  headers=headers,
                                  data=query_city,
                                  auth=('elastic', 'changeme'))
    # load statistic to dictionary
    dic_impression = json.loads(response_impression.content)
    dic_click = json.loads(response_click.content)
    dic_city = json.loads(response_city.content)

    # remove data that is not needed to display
    if len(dic_impression['aggregations']['group_by_month']['buckets']) == 1:
        impression_groupby_days.append(0)
        click_groupby_days.append(0)
        money_spend_inweek.append(0)
        days.append('Start')
    try:
        for i in range(7):
            impression_groupby_days.append(dic_impression['aggregations']['group_by_month']['buckets'][i]['doc_count'])
            money_spend_inweek.append(dic_impression['aggregations']['group_by_month']['buckets'][i]['doc_count'] * 100)
            days.append(dic_impression['aggregations']['group_by_month']['buckets'][i]['key_as_string'][:10])
            click_groupby_days.append(dic_click['aggregations']['group_by_month']['buckets'][i]['doc_count'])


    except IndexError as e:
        pass
    for i in range(3):
        city_groupby_city.append(0)
    try:
        for i in range(9):
            if str(dic_city['aggregations']['test']['buckets'][i]['key']).__eq__('hanoi'):
                city_groupby_city[2] = (dic_city['aggregations']['test']['buckets'][i]['doc_count'])
            elif str(dic_city['aggregations']['test']['buckets'][i]['key']).__eq__('hochiminh'):
                city_groupby_city[1] = (dic_city['aggregations']['test']['buckets'][i]['doc_count'])
            elif str(dic_city['aggregations']['test']['buckets'][i]['key']).__eq__('danang'):
                city_groupby_city[0] = (dic_city['aggregations']['test']['buckets'][i]['doc_count'])
    except IndexError as e:
        pass
    spent_amount = round(Campaign.objects.get(id=campaign_id).spent_amount, 3)
    money_left = Campaign.objects.get(id=campaign_id).budget - spent_amount

    # response to ajax request
    data = {'impressions': impression_groupby_days, 'clicks': click_groupby_days, 'days': days,
            'money_spend_inweek': money_spend_inweek, 'city': city_groupby_city, 'money_left': money_left,
            'spent_amount': spent_amount}
    logger.debug(data)
    return data


def save_impression_elastic(impression):
    ad_id = impression.ad_id
    campaign_id = impression.campaign_id
    time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    city = impression.city
    os = impression.os
    browser = impression.browser
    document_str = '{{\n"ad_id": "{}","campaign_id": "{}","time": "{}","city": "{}", "os": "{}", "browser": "{}"\n}}'.format(
        ad_id,
        campaign_id,
        time,
        city,
        os,
        browser)
    logger.debug(document_str)
    url = "http://elasticsearch.panther-ad.xyz/impression/_doc"
    headers = {'Content-type': 'application/json'}
    response = requests.post(url=url,
                             headers=headers,
                             data=document_str,
                             auth=('elastic', 'changeme'))
    print('status: {}'.format(response.status_code))


def save_click_elastic(ad_click):
    ad_id = ad_click.ad_id
    campaign_id = ad_click.campaign_id
    time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    city = ad_click.city
    os = ad_click.os
    browser = ad_click.browser
    url = ad_click.url
    document_str = '{{\n"ad_id": {},"campaign_id": "{}","time": "{}","city": "{}", "os": "{}", "browser": "{}", "url": "{}"\n}}'.format(
        ad_id, campaign_id, time, city, os, browser, url)
    logger.debug(document_str)
    url = "http://elasticsearch.panther-ad.xyz/click/_doc"

    headers = {'Content-type': 'application/json'}
    response = requests.post(url=url,
                             headers=headers,
                             data=document_str,
                             auth=('elastic', 'changeme'))
    print('status click: {}'.format(response.status_code))


# remove Ad
def remove_ad(request, ad_id):
    if request.method == 'POST':
        ad = Ad.objects.get(id=ad_id)
        ad.delete()
    return redirect('panther_ad:ads')


def remove_campaign(request, campaign_id):
    if request.method == 'POST':
        campaign = Campaign.objects.get(id=campaign_id)

        # get remaining budget from campaign back
        profile = Profile.objects.get(user_id=request.user.id)
        profile.current_account_balance = F('current_account_balance') + campaign.budget - campaign.spent_amount
        campaign.delete()
        return HttpResponse()


def update_campaign(request, campaign_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            extra_budget = request.POST['extra_budget']
            start_date = request.POST['str_date_1']
            end_date = request.POST['end_date_1']
            name = request.POST['name']
            descrtiprion = request.POST['description']

            logger.debug(start_date)
            logger.debug(end_date)
            # start_date=datetime.datetime.strptime(start_date, "%d %B, %Y")
            cp = Campaign.objects.get(id=campaign_id)
            x = cp.budget + float(request.POST['extra_budget'])
            cp.budget = x
            cp.start_date = datetime.datetime.strptime(start_date, "%d %B, %Y")
            cp.end_date = datetime.datetime.strptime(end_date, "%d %B, %Y")
            cp.name = name
            cp.description = descrtiprion   
            cp.status = 'Pending'
            cp.save()
            logger.debug(type('budget'))
            logger.debug(type('extra_budget'))
            logger.debug(cp.budget)
            prf = Profile.objects.get(user_id=request.user.id)
            prf.current_account_balance = F('current_account_balance') - request.POST['extra_budget']
            prf.save()
            # handle target object change
            target_city = request.POST.getlist('target_city')
            target_os = request.POST.getlist('target_os')
            target_browser = request.POST.getlist('target_browser')
            ad_in_campaign = cp.ads.all()
            ad_not_in_campaign = Ad.objects.filter(campaign__isnull=True).filter(user_id=request.user.id)
            # update target city
            for id in target_city:
                TargetCity.objects.get_or_create(campaign_id=campaign_id, city_id=id)
            TargetCity.objects.filter(campaign_id=campaign_id).exclude(city__in=target_city).delete()
            # update target os
            for id in target_os:
                TargetOS.objects.get_or_create(campaign_id=campaign_id, os_id=id)
            TargetOS.objects.filter(campaign_id=campaign_id).exclude(os__in=target_os).delete()
            # update target browser
            logger.debug(target_browser)
            for id in target_browser:
                TargetBrowser.objects.get_or_create(campaign_id=campaign_id, browser_id=id)
            TargetBrowser.objects.filter(campaign_id=campaign_id).exclude(browser__in=target_browser).delete()
            ad_check_list = request.POST.getlist('ad_checked_list')
            cp.ads.clear()
            for id in ad_check_list:
                ad = Ad.objects.get(id=id)
                cp.ads.add(ad)
                AdInCampaign.objects.get_or_create(campaign_id=campaign_id, ad_id=id)
            AdInCampaign.objects.filter(campaign_id=campaign_id).exclude(ad__in=ad_check_list).delete()
            return render(request, 'panther_ad/update_campaign.html', {
                'campaign': cp,
                'ad_in_campaign': ad_in_campaign,
                'ad_not_in_campaign': ad_not_in_campaign,
                'start_date': cp.start_date.strftime('%Y-%m-%d'),
                'end_date': cp.end_date.strftime('%Y-%m-%d'),
                "profile": Profile.objects.get(user_id=request.user.id),
                "target_os": OS.objects.exclude(
                    id__in=[tg.os_id for tg in TargetOS.objects.filter(campaign_id=campaign_id)]),
                "target_city": City.objects.exclude(
                    id__in=[tg.city_id for tg in TargetCity.objects.filter(campaign_id=campaign_id)]),
                "target_browser": Browser.objects.exclude(
                    id__in=[tg.browser_id for tg in TargetBrowser.objects.filter(campaign_id=campaign_id)]),
                "campaign_target_os": OS.objects.filter(
                    id__in=[tg.os_id for tg in TargetOS.objects.filter(campaign_id=campaign_id)]),
                "campaign_target_city": City.objects.filter(
                    id__in=[tg.city_id for tg in TargetCity.objects.filter(campaign_id=campaign_id)]),
                "campaign_target_browser": Browser.objects.filter(
                    id__in=[tg.browser_id for tg in TargetBrowser.objects.filter(campaign_id=campaign_id)])
            })
            return HttpResponseRedirect(reverse('panther_ad:update_campaign', kwargs={
                'campaign_id': campaign_id,
            }))
        elif request.method == 'GET':
            if is_exist_campaign(campaign_id):
                if user_own_campaign(request.user.id, Campaign.objects.get(id=campaign_id).user_id):
                    campaign = database.get_campaign(campaign_id)
                    # get all Ad belong to current user
                    ad_in_campaign = campaign.ads.all()
                    # get all Ad do not belong to campaign
                    ad_not_in_campaign = Ad.objects.filter(campaign__isnull=True).filter(user_id=request.user.id)
                    logger.debug(ad_in_campaign)
                    logger.debug(ad_not_in_campaign)
                    logger.debug(campaign)
                    return render(request, 'panther_ad/update_campaign.html', {
                        'campaign': campaign,
                        'ad_in_campaign': ad_in_campaign,
                        'start_date': campaign.start_date.strftime('%Y-%m-%d'),
                        'end_date': campaign.end_date.strftime('%Y-%m-%d'),
                        'ad_not_in_campaign': ad_not_in_campaign,
                        "profile": Profile.objects.get(user_id=request.user.id),
                        "target_os": OS.objects.exclude(id__in=[tg.os_id for tg in TargetOS.objects.filter(campaign_id=campaign_id)]),
                        "target_city": City.objects.exclude(id__in=[tg.city_id for tg in TargetCity.objects.filter(campaign_id=campaign_id)]),
                        "target_browser": Browser.objects.exclude(
                            id__in=[tg.browser_id for tg in TargetBrowser.objects.filter(campaign_id=campaign_id)]),
                        "campaign_target_os": OS.objects.filter(id__in=[tg.os_id for tg in TargetOS.objects.filter(campaign_id=campaign_id)]),
                        "campaign_target_city": City.objects.filter(id__in=[tg.city_id for tg in TargetCity.objects.filter(campaign_id=campaign_id)]),
                        "campaign_target_browser": Browser.objects.filter(
                            id__in=[tg.browser_id for tg in TargetBrowser.objects.filter(campaign_id=campaign_id)])
                    })
                else:
                    return render('panther_ad/not_found.html')
            else:
                return render(request, 'panther_ad/not_found.html')
