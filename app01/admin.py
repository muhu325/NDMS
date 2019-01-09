from django.contrib import admin
from app01 import models
from app01.myviews.epon_info_update import Epon
from concurrent.futures import ThreadPoolExecutor
from app01.utils.NDMS_settings import INT3
import time


RUNNING = False
# Register your models here.

class MyDevice(admin.ModelAdmin):
    list_display = ("name", "IP", "enable", "tag",)
    search_fields = ("tag__name","IP","tag__company__name","tag__version__name",)
    list_filter = ("enable","tag",)
    fields = ("name", "IP", "enable", "tag",)
    readonly_fields = ("enable","name",)
    radio_fields = {"tag":admin.VERTICAL}
    # fieldsets = ((None,{'fields': ("name","IP","tag",)}),)
    list_per_page = 20
    actions = ["activate_epon", ]

    def epon_info_update(self,Epon,obj,index):
        obj = Epon(obj.IP)
        obj.epon_check_update(index)
    def activate_epon(self, req, queryset):
        pool = ThreadPoolExecutor(INT3)
        # generator1 = (i for i in queryset)
        if not RUNNING:
            for index,obj in enumerate(queryset,1):
                if obj.tag.name == "EPON":
                    pool.submit(self.epon_info_update,Epon,obj,index)
                    # 将子线程对象添加到列表中
                else:
                    print("%s 该设备不是epon设备"%obj.IP)
            time.sleep(3)
        else:
            print("程序运行中，无效")
        pool.shutdown(wait=False)

    activate_epon.short_description = "激活EPON"


class MyTag(admin.ModelAdmin):
    list_display = ("name", "authmode", "company", "version",)
    list_filter = ("name","version__name")
    search_fields = ("name",)


admin.site.register(models.Device, MyDevice)
admin.site.register(models.Tag, MyTag)
# admin.site.register(models.Version)
# admin.site.register(models.AuthMode)
# admin.site.register(models.Company)
# admin.site.register(models.Olt)
# admin.site.register(models.Onu)
