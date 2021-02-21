import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.TextField(default='', null=True)
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    gender = models.CharField(max_length=10, null=True,
                              choices=GENDER_CHOICES, default='Male')
    date_of_birth = models.DateField(null=True)
    address = models.TextField(default='', null=True)
    phone = models.CharField(default='', max_length=15, null=True)
    current_account_balance = models.FloatField(default=0, null=True)
    total_deposit = models.FloatField(default=0, null=True)
    total_spent = models.FloatField(default=0, null=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class Ad(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.TextField()
    size = models.CharField(null=True, max_length=10)
    url = models.ImageField(blank=True, null=True)

    # current_date = datetime.datetime(2019, 12, 21, 14, 25, 25)

    # fmt_date = current_date.strftime('%Y/%m/%d')

    date_created = models.DateTimeField(auto_now=True, null=True)

    @property
    def ad_width(self):
        return self.size.split("x")[0]

    @property
    def ad_height(self):
        return self.size.split("x")[1]

    @property
    def show_img_admin(self):
        return '<div><img src="{url}"></div><br>'.format(url=self.url)

    def __str__(self):
        return self.name


class Campaign(models.Model):
    STATUS = [
        ('Ready', 'Ready'),
        ('Pending', 'Pending'),
        ('Running', 'Running'),
        ('Paused', 'Paused'),
        ('Finished', 'Finished'),
        ('Denied', 'Denied'),
        ('Canceled', 'Canceled')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.TextField(null=True)
    description = models.TextField(null=True)

    budget = models.FloatField(default=0)
    spent_amount = models.FloatField(default=0)
    # date
    date_created = models.DateTimeField(default=datetime.datetime.now)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

    denied_message = models.CharField(default='', null=True, max_length=200)

    ads = models.ManyToManyField(Ad)
    status = models.CharField(
        max_length=10,
        choices=STATUS,
        default='Pending'
    )
    destination_url = models.TextField()

    def __str__(self):
        return self.name


class AdInCampaign(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('ad', 'campaign')


# Target Models
class OS(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class Browser(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


# Target Lists
class TargetOS(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, null=True)
    os = models.ForeignKey(OS, on_delete=models.CASCADE)

    def __str__(self):
        return self.campaign.name + ' - ' + self.os.name


class TargetBrowser(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, null=True)
    browser = models.ForeignKey(Browser, on_delete=models.CASCADE)

    def __str__(self):
        return self.campaign.name + ' - ' + self.browser.name


class TargetCity(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return self.campaign.name + ' - ' + self.city.name


class Impression(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, null=False)
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, null=False)
    time = models.DateTimeField('what is this')
    city = models.TextField()
    os = models.TextField()
    browser = models.TextField()
    ip = models.TextField()
    publisher = models.TextField(null=True)


class Click(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, null=False)
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, null=False)
    time = models.DateTimeField('what is this')
    city = models.TextField()
    os = models.TextField()
    browser = models.TextField()
    ip = models.TextField()
    publisher = models.TextField(null=True)
    url = models.TextField(null=True)


class TransactionHistory(models.Model):
    date = models.DateTimeField(auto_now=True, null=True)
    description = models.TextField(default='')
    amount = models.BigIntegerField(default=0)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    trans_type = models.CharField(null=True, max_length=30)
