from app01 import models
from concurrent.futures import ThreadPoolExecutor
from django.shortcuts import render,HttpResponse
from app01.utils.network_device import Epon
from app01.utils.NDMS_settings import INT3

def epon_create_update(req):
    objs_epon = models.Device.objects.filter(tag__name="EPON")
    print("开始进行EPON设备信息更新")
    pool = ThreadPoolExecutor(INT3)
    for obj_epon in objs_epon:
        if obj_epon.tag.name == "EPON":
            # print(obj,obj.name,obj.IP)
            obj = Epon(obj_epon.IP)
            pool.submit(Epon.epon_check_update, obj)
            # 将子线程对象添加到列表中
        else:
            print("wrong")
    pool.shutdown(wait=False)

    return HttpResponse("EPON设备信息更新正在运行中")

