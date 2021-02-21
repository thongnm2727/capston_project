from django.urls import path

from . import views, account_views

app_name = 'panther_ad'
urlpatterns = [
    path('dashboard/<int:campaign_id>', views.dashboard_data, name='dashboard_data'),
    path('', views.index, name='index'),
    path('forgot/', views.forgot, name='forgot'),
    path('signin/', views.sign_in, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('signout/', views.signout, name='signout'),
    path('create_ad/', views.create_ad, name='create_ad'),
    path('create_campaign/', views.create_campaign, name='create_campaign'),
    # path('user_profile/', views.user_profile, name='user_profile'),
    path('get_ad/', views.get_ad, name='get_ad'),
    path('save_click/', views.save_click, name='save_click'),
    path('campaigns/', views.campaign_list, name='campaigns'),  # display all campaign
    path('campaign_detail/<int:campaign_id>', views.campaign_detail, name='campaign_detail'),  # display campaign detail
    path('ads/', views.ad_list, name='ads'),  # display all ads
    path('statistic/<int:campaign_id>', views.campaign_statistic, name='campaign_statistic'),  # display campaign statistic
    path('pause/<int:campaign_id>', views.pause_campaign, name="pause_campaign"),  # pause campaign
    path('resume/<int:campaign_id>', views.resume_campaign, name="resume_campaign"),  # resume campaign
    # account
    path('user_profile/', account_views.view_profile, name='user_profile'),
    path('save_profile/', account_views.save_profile, name='save_profile'),
    path('change_password/', account_views.change_password, name='change_password'),
    path('account_activity/', account_views.account_activity, name='account_activity'),
    path('top_up_balance/', account_views.top_up_balance, name='top_up_balance'),

    # remove Ad
    path('remove_ad/<int:ad_id>', views.remove_ad, name='remove_ad'),

    # update campaign
    path('update_campaign/<int:campaign_id>', views.update_campaign, name='update_campaign'),

    # remove campaign
    path('remove_campaign/<int:campaign_id>', views.remove_campaign, name='remove_campaign')
]
