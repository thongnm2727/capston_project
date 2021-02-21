from panther_ad.models import *
from .models import Campaign


# def signup(username, email, password):
#     if ' ' in username:
#         return False
#     username = str.lower(username).strip()
#     email = str.lower(email).strip()
#     if User.objects.filter(email=email).count() | User.objects.filter(username=username).count():
#         return False
#     else:
#         user = User.objects.create(username=username, email=email, password=make_password(password),
#                                    joined_date=timezone.now())
#         user.save()
#         return True
#
#
# def login(email, password):
#     try:
#         try:
#             validate_email(str.lower(email).strip())
#             user = User.objects.get(email=str.lower(email).strip())
#         except ValidationError:
#             user = User.objects.get(username=str.lower(email).strip())
#     except ObjectDoesNotExist:
#         return False
#     if check_password(password, user.password):
#         return user
#     else:
#         return False


def get_all_campaign(user_id):
    return Campaign.objects.filter(user_id=user_id)


def get_campaign(campaign_id):
    return Campaign.objects.get(id=campaign_id)


def get_all_ad(user_id):
    return Ad.objects.filter(user_id=user_id)


def get_ad_in_campaign(campaign_id):
    return AdInCampaign.objects.filter(campaign_id=campaign_id)
