from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Campaign, Ad, Browser, City, OS, TargetBrowser, TargetCity, TargetOS, AdInCampaign

# admin.site.register(Campaign)
# admin.site.register(Ad)
admin.site.register(Browser)
admin.site.register(City)
admin.site.register(OS)
admin.site.register(TargetBrowser)
admin.site.register(TargetCity)
admin.site.register(TargetOS)
admin.site.register(AdInCampaign)


class AdCpInLine(admin.TabularInline):
    model = Campaign.ads.through
    # list_display = ('size', 'url')


class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'status', 'denied_message', 'image_tag')
    list_editable = ('status', 'denied_message',)
    search_fields = ('status',)

    def image_tag(self, obj):
        img_tags = ""
        for adsz in obj.ads.all():
            img_tags += '<div style="background-color: blue; width: {}px; height: {}px;margin-bottom:20px"><div style="width: 100%;height: 100%;overflow: hidden;"><img src="{}" /></div></div>'.format(
                adsz.ad_width, adsz.ad_height, adsz.url)
        return format_html(img_tags)


class AdInLine(admin.ModelAdmin):
    model = Ad
    list_display = ('name', 'size', 'url', 'date_created', 'myimg', 'user')
    fields = ['name', 'size', 'url', 'myimg', 'user', ]
    readonly_fields = ['myimg']

    def myimg(self, obj):
        return mark_safe(
            '<div style="background-color: blue; width: {w}px; height: {h}px;"><div style="width: 100%;height: 100%;overflow: hidden;"><img src="{url}"></div "></div>'.format(
                w=obj.ad_width, h=obj.ad_height, url=obj.url
            )
        )


admin.site.register(Campaign, CampaignAdmin)

admin.site.register(Ad, AdInLine)
