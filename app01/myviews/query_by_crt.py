from django.shortcuts import render, HttpResponse, redirect
from app01.utils.auth_decorator import auth
from app01.utils.spider import get_businesses_info_list_by_olt_name_and_onu_interface,get_businesses_info_list_by_businesses_code
from app01.utils.NDMS_settings import AES,Random
from app01 import models
import re

text_520 = """# $language = "python"
# $interface = "1.0"

def main():
    cmd = "/TELNET {telnet_ip} 23"
    crt.Session.Connect(cmd)
    outPut = crt.Screen.ReadString(":", 10)
    crt.Screen.Send(\"{username}\\r\\n\" )
    crt.Screen.ReadString(":", 10)
    crt.Screen.Send(\"{password}\\r\\n\")
    crt.Screen.ReadString(">", 10)
    crt.Screen.Send("su \\r\\n")
    crt.Screen.ReadString(":", 10)
    crt.Screen.Send("hzcnc_enable\\r\\n")
    crt.Screen.ReadString(">", 10)
    crt.Screen.Send("screen-length disable\\r\\n")
    crt.Screen.ReadString(">", 10)
    crt.Screen.Send("sy\\r\\n")
    crt.Screen.ReadString("]", 10)
    crt.Screen.Send(\"dis onu-event int {onu}\\r\\n\")
    crt.Screen.ReadString("]", 10)
    crt.Screen.Send("dis onuinf int {onu}\\r\\n")
    crt.Screen.ReadString("]", 10)
    crt.Screen.Send("dis transceiver diagnosis interface {onu}\\r\\n")
    crt.Screen.ReadString("]", 10)
    crt.Screen.Send("interface {onu}\\r\\n")
    crt.Screen.ReadString("]", 10)
    crt.Screen.Send("dis th\\r\\n")
    crt.Screen.ReadString("]", 10)
    crt.Screen.Send("dis onu-protocol stp\\r\\n")
    crt.Screen.ReadString("]", 10)
    crt.Screen.Send("dis mac-address int {onu}\\r\\n")

main()"""

text_71 = """# $language = "python"
# $interface = "1.0"

def main():
    cmd = "/TELNET {telnet_ip} 23"
    crt.Session.Connect(cmd)
    outPut = crt.Screen.ReadString(":", 10)
    crt.Screen.Send(\"{username}\\r\\n\" )
    crt.Screen.ReadString(":", 10)
    crt.Screen.Send(\"{password}\\r\\n\")
    crt.Screen.ReadString(">", 10)
    crt.Screen.Send("su \\r\\n")
    crt.Screen.ReadString(":", 10)
    crt.Screen.Send("hzcnc_enable\\r\\n")
    crt.Screen.ReadString(">", 10)
    crt.Screen.Send("screen-length disable\\r\\n")
    crt.Screen.ReadString(">", 10)
    crt.Screen.Send("sy\\r\\n")
    crt.Screen.ReadString("]", 10)
    crt.Screen.Send(\"dis epon onu-event int {onu}\\r\\n\")
    crt.Screen.ReadString("]", 10)
    crt.Screen.Send("dis onu int {onu}\\r\\n")
    crt.Screen.ReadString("]", 10)
    crt.Screen.Send("dis transceiver diagnosis interface {onu}\\r\\n")
    crt.Screen.ReadString("]", 10)
    crt.Screen.Send("interface {onu}\\r\\n")
    crt.Screen.ReadString("]", 10)
    crt.Screen.Send("dis th\\r\\n")
    crt.Screen.ReadString("]", 10)
    crt.Screen.Send("dis onu  protocol  stp\\r\\n")
    crt.Screen.ReadString("]", 10)
    crt.Screen.Send("dis mac-address interface {onu}\\r\\n")

main()"""

text_Raisecom = """# $language = "python"
# $interface = "1.0"

def main():
    cmd = "/TELNET {telnet_ip} 23"
    crt.Session.Connect(cmd)
    outPut = crt.Screen.ReadString(":", 10)
    crt.Screen.Send(\"{username}\\r\\n\" )
    crt.Screen.ReadString(":", 10)
    crt.Screen.Send(\"{password}\\r\\n\")
    crt.Screen.ReadString(">", 10)
    crt.Screen.Send("enable\\r\\n")
    crt.Screen.ReadString(":", 10)
    crt.Screen.Send("hzcnc_enable\\r\\n")
    crt.Screen.ReadString("#", 10)
    crt.Screen.Send("terminal page-break disable\\r\\n")
    crt.Screen.ReadString("#", 10)
    crt.Screen.Send("show alarm  log  int onu {onu}\\r\\n")
    crt.Screen.ReadString("#", 10)
    crt.Screen.Send("show int onu {onu} inf\\r\\n")
    crt.Screen.ReadString("#", 10)
    crt.Screen.Send("show int onu {onu} uni eth inf\\r\\n")
    crt.Screen.ReadString("#", 10)
    crt.Screen.Send("show int onu {onu} loop\\r\\n")
    crt.Screen.ReadString("#", 10)
    crt.Screen.Send("show run onu {onu}\\r\\n")
    crt.Screen.ReadString("#", 10)
    crt.Screen.Send("show int onu {onu} transceiver detail\\r\\n")
    crt.Screen.ReadString("#", 10)
    crt.Screen.Send("show int onu {onu} mac-addr l2 dy\\r\\n")
    crt.Screen.ReadString("#", 10)
    crt.Screen.Send("terminal page-break enable\\r\\n")


main()"""

text_520_olt = """# $language = "python"
# $interface = "1.0"

def main():
    cmd = "/TELNET {telnet_ip} 23"
    crt.Session.Connect(cmd)
    outPut = crt.Screen.ReadString(":", 10)
    crt.Screen.Send(\"{username}\\r\\n\" )
    crt.Screen.ReadString(":", 10)
    crt.Screen.Send(\"{password}\\r\\n\")
    crt.Screen.ReadString(">", 10)
    crt.Screen.Send("su \\r\\n")
    crt.Screen.ReadString(":", 10)
    crt.Screen.Send("hzcnc_enable\\r\\n")
    crt.Screen.ReadString(">", 10)
    crt.Screen.Send("screen-length disable\\r\\n")
    crt.Screen.ReadString(">", 10)
    crt.Screen.Send("sy\\r\\n")
    crt.Screen.ReadString("]", 10)
    crt.Screen.Send(\"dis cu int {olt}\\r\\n\")
    crt.Screen.ReadString("]", 10)
    crt.Screen.Send("dis onuinf int {olt}\\r\\n")

main()"""

text_71_olt = """# $language = "python"
# $interface = "1.0"

def main():
    cmd = "/TELNET {telnet_ip} 23"
    crt.Session.Connect(cmd)
    outPut = crt.Screen.ReadString(":", 10)
    crt.Screen.Send(\"{username}\\r\\n\" )
    crt.Screen.ReadString(":", 10)
    crt.Screen.Send(\"{password}\\r\\n\")
    crt.Screen.ReadString(">", 10)
    crt.Screen.Send("su \\r\\n")
    crt.Screen.ReadString(":", 10)
    crt.Screen.Send("hzcnc_enable\\r\\n")
    crt.Screen.ReadString(">", 10)
    crt.Screen.Send("screen-length disable\\r\\n")
    crt.Screen.ReadString(">", 10)
    crt.Screen.Send("sy\\r\\n")
    crt.Screen.ReadString("]", 10)
    crt.Screen.Send(\"dis cu int {olt}\\r\\n\")
    crt.Screen.ReadString("]", 10)
    crt.Screen.Send("dis onu int {olt}\\r\\n")

main()"""

text_Raisecom_olt = """# $language = "python"
# $interface = "1.0"

def main():
    cmd = "/TELNET {telnet_ip} 23"
    crt.Session.Connect(cmd)
    outPut = crt.Screen.ReadString(":", 10)
    crt.Screen.Send(\"{username}\\r\\n\" )
    crt.Screen.ReadString(":", 10)
    crt.Screen.Send(\"{password}\\r\\n\")
    crt.Screen.ReadString(">", 10)
    crt.Screen.Send("enable\\r\\n")
    crt.Screen.ReadString(":", 10)
    crt.Screen.Send("hzcnc_enable\\r\\n")
    crt.Screen.ReadString("#", 10)
    crt.Screen.Send("show interface olt {olt} inf\\r\\n")
    crt.Screen.ReadString("#", 10)
    crt.Screen.Send("show interface onu inf | inc {olt}/\\r\\n")


main()"""

TELNET_KEY = ""

@auth
def query_crt(req):
    username = req.session.get("username")
    password = req.session.get("password")

    if req.method == "GET":
        # 这里承载了2个功能：1.页面初始化的get请求；2.根据前端发来的ajax get请求信息，生成crt命令行字符串
        if not req.GET:
            return render(req, "query_crt.html")
        query_type = req.GET.get("query_type")
        telnet_ip = req.GET.get("telnet_ip")
        version = req.GET.get("version")
        onu_interface = req.GET.get("onu_interface")
        olt_interface = req.GET.get("olt_interface")
        text = ""

        if query_type == "onu":
            if version == "Version 5.20":
                text = text_520.format(telnet_ip=telnet_ip, username=username, password=password, onu=onu_interface)
            elif version == "Version 7.1":
                text = text_71.format(telnet_ip=telnet_ip, username=username, password=password, onu=onu_interface)
            else:
                text = text_Raisecom.format(telnet_ip=telnet_ip, username=username, password=password, onu=onu_interface)
        elif query_type == "olt":
            if version == "Version 5.20":
                text = text_520_olt.format(telnet_ip=telnet_ip, username=username, password=password, olt=olt_interface)
            elif version == "Version 7.1":
                text = text_71_olt.format(telnet_ip=telnet_ip, username=username, password=password, olt=olt_interface)
            else:
                text = text_Raisecom_olt.format(telnet_ip=telnet_ip, username=username, password=password,
                                                olt=olt_interface)
        if text:
            key1 = b'dbbb91e398df2a69'  # 存放在本地
            key2 = Random.new().read(AES.block_size)  # 与key一样的16位的二进制字符串
            mycipher = AES.new(key1, AES.MODE_CFB, key2)
            # text = key2 + mycipher.encrypt(text.encode())
            global TELNET_KEY
            TELNET_KEY = key2 + mycipher.encrypt(text.encode())
            # print("TELNET_KE已修改",TELNET_KEY)
            # print(text)
            # with open("statics/crt_telnet/crt_telnet", "wb") as f:
            #     f.write(text)
        return HttpResponse("OK")  # 这里其实只要有返回就好，目的是让前端执行回调函数
    elif req.method == "POST":  # 到数据库查询数据,无telnet操作
        actions = req.POST.get("actions")
        query_keywords = req.POST.get("query_keywords").replace(" ", "").lower()
        queried_list = []
        message = ""
        if actions == "query_onu":
            query_keywords = query_keywords.replace(".", "").replace("-", "").replace(":",
                                                                                      "").replace("：", "")
            if len(query_keywords) < 4:  # 这里仅是验证是否输入空白查询关键字；直接在前端进行判断吧，同时去除两头空白
                message = "请至少输入4个字符"
                return render(req, "query_crt.html", {"message": message})
            # 搜索包含有查询关键字的ONU表内容
            queried_list = models.Onu.objects.filter(mac__contains=query_keywords)
            if len(queried_list) == 0:
                message = "数据库中无该数据"
                # logger.info("查询onu无数据，关键字：%s" % query_keywords)  # 记录logging
            else:
                for i in queried_list:
                    # print("找到的onu对象：",i.olt.name,i.olt.pon.ip_addr,i.olt.interface,i.name,i.mac_address,"olt id：",i.olt.id,"onu id:",i.id)
                    olt_name = i.olt.name
                    onu_interface = re.findall(r"\d+$", i.interface)[0]
                    if olt_name:
                        if int(onu_interface) < 10:
                            onu_interface = "0%s" % onu_interface
                        try:
                            rmss_list = get_businesses_info_list_by_olt_name_and_onu_interface(olt_name, onu_interface)
                            if rmss_list:
                                i.rmss_result = True
                                i.rmss_list = rmss_list
                            else:
                                i.rmss_result = False
                                i.rmss_list = "关键字：%s%%%s查询无结果" % (olt_name, onu_interface)
                        except Exception as f:
                            # print("爬虫出错:", f)
                            i.rmss_result = False
                            i.rmss_list = "爬虫出错"  # 前端判断i.rmss_list为空时，则提示爬虫出错
                    else:
                        i.rmss_result = False
                        i.rmss_list = "该onu所在的olt口在设备上无命名"

                    if i.olt.epon.tag.version.name == "ISCOM5800E-SMCB_1.44":
                        i.tag = "瑞斯onu"
                    else:
                        i.tag = "华三onu"
                    #未注册的onu在这里待拓展
                    #未注册的onu在这里待拓展
                    #未注册的onu在这里待拓展
                    #未注册的onu在这里待拓展
                    #未注册的onu在这里待拓展
                    #未注册的onu在这里待拓展
                    #未注册的onu在这里待拓展
                    #未注册的onu在这里待拓展
                    #未注册的onu在这里待拓展
                    #未注册的onu在这里待拓展
                    #未注册的onu在这里待拓展
                    #未注册的onu在这里待拓展
                    #未注册的onu在这里待拓展
            return render(req, "query_crt.html",
                          {"obj_onu_list": queried_list, "message": message, "onu_mac": query_keywords})
        elif actions == "query_olt":
            query_keywords = query_keywords.replace(".", "").replace(":", "").replace("：", "")
            if len(query_keywords) < 7:  # 这里仅是验证是否输入空白查询关键字；直接在前端进行判断吧，同时去除两头空白
                message = "请至少输入7个字符"
                return render(req, "query_crt.html", {"message": message})
            queried_list = models.Olt.objects.filter(name__contains=query_keywords)
            if len(queried_list) == 0:
                message = "数据库中无该数据"
                # logger.info("查询olt无数据，关键字：%s" % query_keywords)  # 记录logging
            else:
                for i in queried_list:
                    if i.epon.tag.version.name == "ISCOM5800E-SMCB_1.44":
                        i.tag = "瑞斯onu"
                    else:
                        i.tag = "华三onu"

            return render(req, "query_crt.html",
                          {"obj_olt_list": queried_list, "message": message, "olt_name": query_keywords})
        elif actions == "query_rmss":
            if len(query_keywords) < 6:  # 这里仅是验证是否输入空白查询关键字；直接在前端进行判断吧，同时去除两头空白
                message = "请至少输入6个字符"
                return render(req, "query_crt.html", {"message": message})
            rmss_info_list = get_businesses_info_list_by_businesses_code(query_keywords)
            rmss_info_list_v2 = []  # 这个里面储存字典
            # print("爬虫结果：",rmss_info_list)
            for rmss_info in rmss_info_list:
                dict1 = {}
                dict1["rmss_info"] = rmss_info
                dict1["objs_onu_list"] = []
                olt_name, onu_interface1 = re.findall(r"^(.+?)\..+?\.(\d{2})", rmss_info['id_code'])[0] if \
                    re.findall(r"^(.+?)\..+?\.(\d{2})", rmss_info['id_code']) else ("", "")
                objs_olt = ""
                if olt_name:
                    objs_olt = models.Olt.objects.filter(name=olt_name.lower())
                for obj_olt in objs_olt:
                    # print(obj_olt.name,obj_olt.pon.ip_addr,obj_olt.pon.version)
                    onu_interface = "%s/%s" % (obj_olt.interface, int(onu_interface1)) if obj_olt.epon.tag.version.name == "ISCOM5800E-SMCB_1.44" \
                        else "onu%s:%s" % (obj_olt.interface[3:], int(onu_interface1))
                    objs_onu = models.Onu.objects.filter(olt=obj_olt, interface=onu_interface)
                    for obj_onu in objs_onu:
                        if obj_onu.olt.epon.tag.version.name == "ISCOM5800E-SMCB_1.44":
                            obj_onu.tag = "瑞斯onu"
                        else:
                            obj_onu.tag = "华三onu"
                        dict1["objs_onu_list"].append(obj_onu)
                rmss_info_list_v2.append(dict1)

            return render(req, "query_crt.html",
                          {"rmss_info_list": rmss_info_list_v2, "message": message, "rmss_id_code": query_keywords})


def get_telnet_command(req):
    # with open("statics/crt_telnet/crt_telnet", "rb") as f:
    #     text = f.readlines()

    # return HttpResponse(text)
    # print(112233)
    print(TELNET_KEY)
    return HttpResponse(TELNET_KEY)