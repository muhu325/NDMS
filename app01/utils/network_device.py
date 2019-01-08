import telnetlib, time, re
from app01.utils.others import mydecode, my_read_very_eager, port_mapping
from app01.utils.NDMS_settings import username1, password1
from app01 import models

"""NetworkDevie为基础类；类名称包含厂商名称的为继承类，定义了该厂商设备不同版本的登录方法、割接查询方法
类名称包含设备定位（比如POP/PE/BRAS）为二次继承子类，定义了统一名称的device_login、cutting_query方法；这是最终用于使用的类"""


class NetworkDevie:
    def __init__(self, IP):
        self.device_obj = models.Device.objects.get(IP=IP)
        self.IP = IP
        self.tn = self.__connect()

    def __connect(self):
        obj = None
        try:
            obj = telnetlib.Telnet(self.IP, port=23, timeout=10)
        except:
            print("telnet %s连接失败，创建NetworkDevie对象失败" % self.IP)
        return obj

    def close(self,index=0):
        try:
            if self.device_obj.tag.version == "ISCOM5800E-SMCB_1.44":
                self.tn.write(b'terminal page-break enable \n')
            self.tn.close()
            # print("序号：%s关闭连接%s" % (index,self.IP))
        except:
            pass


class H3C(NetworkDevie):
    def _telnet_h3c_ver_5(self, username, password):
        self.tn.read_until(b"Username:", timeout=10)
        self.tn.write(username + b"\n")  # 连接到win系统，使用cmd时，使用r'rn'
        self.tn.read_until(b"Password:", timeout=10)
        self.tn.write(password + b"\n")
        time.sleep(0.2)
        self.tn.write(b'super' + b"\n")  # 记得进入super模式
        time.sleep(0.1)
        # tn.read_until(b"Password:") # 又遇到这个super没有密码的。。。
        self.tn.write(b'hzcnc_enable' + b"\n")
        # 以下为交换机操作
        time.sleep(0.1)
        self.tn.write(b"screen-length disable" + b"\n")  # 设置命令不分页显示
        time.sleep(0.1)
        self.tn.write(b"system" + b"\n")
        time.sleep(0.1)
        content = mydecode(my_read_very_eager(self.tn))
        if not self.device_obj.enable:
            self.device_obj.name = re.findall(r"\[(.*)\]", content)[0].lower()
            self.device_obj.enable = True
            self.device_obj.save()

    def _telnet_h3c_ver_7(self, username, password):
        self.tn.read_until(b"login:", timeout=10)
        self.tn.write(username + b"\n")  # 连接到win系统，使用cmd时，使用r'rn'
        self.tn.read_until(b"Password:", timeout=10)
        self.tn.write(password + b"\n")
        time.sleep(0.1)
        self.tn.write(b'super' + b"\n")  # 记得进入super模式
        time.sleep(1)
        # tn.read_until(b"Password:") # 又遇到这个super没有密码的。。。
        self.tn.write(b'hzcnc_enable' + b"\n")
        # 以下为交换机操作
        time.sleep(0.1)
        self.tn.write(b"screen-length disable" + b"\n")  # 设置命令不分页显示
        time.sleep(0.1)
        self.tn.write(b"system-view\n")
        time.sleep(1)
        content = mydecode(my_read_very_eager(self.tn))
        if not self.device_obj.enable:
            self.device_obj.name = re.findall(r"[\[<](.*)[\]>]", content)[0].lower()
            self.device_obj.enable = True
            self.device_obj.save()

    def _query_h3c_ver_5_switch(self, query_obj):
        self.tn.write(b"dis inter %s \n" % query_obj.interfaces.encode())
        time.sleep(0.1)
        per_content = mydecode(my_read_very_eager(self.tn))
        aaa = re.findall(
            r"current state: (UP|DOWN).*Description: ([\S ]*).*sec ([\d-]+ bytes/sec).*sec ([\d-]+ bytes/sec)",
            per_content, re.S)
        if aaa:
            interface_status, desc, input_flow, output_flow = aaa[0]
            query_obj.desc = desc
        else:
            query_obj.desc = "端口无描述or匹配错误"
            interface_status = "无匹配结果"
            input_flow = "无匹配结果"
            output_flow = "无匹配结果"
        query_obj.command_result_detail = per_content
        self.tn.write(b"dis mac-address  inter %s \n" % query_obj.interfaces.encode())
        time.sleep(0.1)
        per_content = mydecode(my_read_very_eager(self.tn))
        query_obj.command_result_detail += per_content  # 保存了该对象输入的所有命令的结果
        has_mac = "有mac" if re.findall(r"\w{4}-\w{4}-\w{4}", per_content) else "无mac"

        query_obj.result_brief = "%s,%s,%s,%s" % (interface_status, has_mac, input_flow, output_flow)

    def _query_h3c_ver_7_switch(self, query_obj):

        self.tn.write(b"dis inter %s \n" % query_obj.interfaces.encode())
        time.sleep(0.1)
        per_content = mydecode(my_read_very_eager(self.tn))
        aaa = re.findall(
            r"Current state: (UP|DOWN).*Description: ([\S ]*).*sec ([\d-]+ bytes/sec).*sec ([\d-]+ bytes/sec)",
            per_content, re.S)
        if aaa:
            interface_status, desc, input_flow, output_flow = aaa[0]
            query_obj.desc = desc
        else:
            query_obj.desc = "端口无描述or匹配错误"
            interface_status = "无匹配结果"
            input_flow = "无匹配结果"
            output_flow = "无匹配结果"
        query_obj.command_result_detail = per_content
        self.tn.write(b"dis mac-address  inter %s \n" % query_obj.interfaces.encode())
        time.sleep(0.1)
        per_content = mydecode(my_read_very_eager(self.tn))
        query_obj.command_result_detail += per_content  # 保存了该对象输入的所有命令的结果
        has_mac = "有mac" if re.findall(r"\w{4}-\w{4}-\w{4}", per_content) else "无mac"

        query_obj.result_brief = "%s,%s,%s,%s" % (interface_status, has_mac, input_flow, output_flow)


class Raisecom(NetworkDevie):
    def _telnet_Raisecom(self, username, password):
        self.tn.read_until(b"Login:", timeout=10)
        self.tn.write(username + b"\n")  # 连接到win系统，使用cmd时，使用r'rn'
        self.tn.read_until(b"Password:", timeout=10)
        self.tn.write(password + b"\n")
        time.sleep(0.1)
        self.tn.write(b'en' + b"\n")  # 记得进入super模式
        time.sleep(0.1)
        self.tn.write(b'hzcnc_enable' + b"\n")
        # 以下为交换机操作
        time.sleep(0.1)
        self.tn.write(b"terminal page-break disable" + b"\n")  # 设置命令不分页显示
        time.sleep(0.6)
        my_read_very_eager(self.tn)


class Cisco(NetworkDevie):
    """Version 12.1的登录/查询逻辑与Version 12.2一致"""

    def _telnet_Cisco_Version_12_2(self, username, password):
        self.tn.read_until(b"username:", timeout=10)
        self.tn.write(username + b"\n")  # 连接到win系统，使用cmd时，使用r'rn'
        self.tn.read_until(b"password:", timeout=10)
        self.tn.write(password + b"\n")
        my_read_very_eager(self.tn)
        self.tn.write(b"enable\n")
        self.tn.read_until(b"password:", timeout=10)
        self.tn.write(password + b"\n")
        time.sleep(0.1)
        # 以下为交换机操作
        self.tn.write(b"terminal length 0\n")  # 设置命令不分页显示,CiscoNexus下次登录默认分页
        time.sleep(0.6)
        content = mydecode(my_read_very_eager(self.tn))
        if not self.device_obj.enable:
            self.device_obj.name = re.findall(r"(.*)#$", content)[0].lower()
            self.device_obj.enable = True
            self.device_obj.save()

    def _query_Cisco_Version_12_2(self, query_obj):
        self.tn.write(b"show interfaces %s\n" % query_obj.interfaces.encode())
        time.sleep(0.1)
        per_content = mydecode(my_read_very_eager(self.tn))
        aaa = re.findall(
            r"line protocol is (up|down).*Description: ([\S ]*).*input rate ([\d-]+ bits/sec).*tput rate ([\d-]+ bits/sec)",
            per_content, re.S)
        if aaa:
            interface_status, desc, input_flow, output_flow = aaa[0]
            query_obj.desc = desc
        else:
            query_obj.desc = "端口无描述or匹配错误"
            interface_status = "无匹配结果"
            input_flow = "无匹配结果"
            output_flow = "无匹配结果"
        query_obj.command_result_detail = per_content
        self.tn.write(b"show mac-address-table  interface %s \n" % query_obj.interfaces.encode())
        time.sleep(0.1)
        per_content = mydecode(my_read_very_eager(self.tn))
        query_obj.command_result_detail += per_content  # 保存了该对象输入的所有命令的结果
        bbb = re.findall(r"\w{4}\.\w{4}\.\w{4}", per_content)
        has_mac = "有mac" if bbb else "无mac"

        query_obj.result_brief = "%s,%s,%s,%s" % (interface_status, has_mac, input_flow, output_flow)


class CiscoNexus(NetworkDevie):
    def _telnet_CiscoNexus_version_2_8_0(self, username, password):
        self.tn.read_until(b"login:", timeout=10)
        self.tn.write(username + b"\n")  # 连接到win系统，使用cmd时，使用r'rn'
        self.tn.read_until(b"Password:", timeout=10)
        self.tn.write(password + b"\n")
        time.sleep(0.1)
        # 以下为交换机操作
        self.tn.write(b"terminal length 0\n")  # 设置命令不分页显示,CiscoNexus下次登录默认分页
        time.sleep(0.6)
        content = mydecode(my_read_very_eager(self.tn))
        if not self.device_obj.enable:
            self.device_obj.name = re.findall(r"(.*)#", content)[0].lower()
            self.device_obj.enable = True
            self.device_obj.save()

    def _query_CiscoNexus_version_2_8_0(self, query_obj):
        self.tn.write(b"show interface %s \n" % query_obj.interfaces.encode())
        time.sleep(0.1)
        per_content = mydecode(my_read_very_eager(self.tn))
        aaa = re.findall(
            r"Ethernet\d{1,2}/\d{1,2} is (up|down).*Description: ([\S ]*).*([\d-]+ bits/sec).*([\d-]+ bits/sec)",
            per_content, re.S)
        if aaa:
            interface_status, desc, input_flow, output_flow = aaa[0]
            query_obj.desc = desc
        else:
            query_obj.desc = "端口无描述or匹配错误"
            interface_status = "无匹配结果"
            input_flow = "无匹配结果"
            output_flow = "无匹配结果"
        query_obj.command_result_detail = per_content
        self.tn.write(b"show mac address-table interface %s \n" % query_obj.interfaces.encode())
        time.sleep(0.1)
        per_content = mydecode(my_read_very_eager(self.tn))
        query_obj.command_result_detail += per_content  # 保存了该对象输入的所有命令的结果
        has_mac = "有mac" if re.findall(r"\w{4}\.\w{4}\.\w{4}", per_content) else "无mac"

        query_obj.result_brief = "%s,%s,%s,%s" % (
            interface_status, has_mac, input_flow, output_flow)


class Cisco9K(NetworkDevie):
    def _telnet_Cisco9K_Version_4_3_4(self, username, password):
        self.tn.read_until(b"Username:", timeout=10)
        self.tn.write(username + b"\n")  # 连接到win系统，使用cmd时，使用r'rn'
        self.tn.read_until(b"Password:", timeout=10)
        self.tn.write(password + b"\n")
        time.sleep(0.1)
        # 以下为交换机操作
        self.tn.write(b"terminal length 0\n")  # 设置命令不分页显示,CiscoNexus下次登录默认分页
        time.sleep(0.6)
        content = mydecode(my_read_very_eager(self.tn))
        if not self.device_obj.enable:
            self.device_obj.name = re.findall(r":(.*)#$", content)[0].lower()
            self.device_obj.enable = True
            self.device_obj.save()

    def _query_Cisco9K_Version_4_3_4(self, query_obj):
        self.tn.write(b"show interfaces %s\n" % query_obj.interfaces.encode())
        time.sleep(0.1)
        per_content = mydecode(my_read_very_eager(self.tn))
        aaa = re.findall(
            r"line protocol is (up|down).*Description: ([\S ]*).*input rate ([\d-]+ bits/sec).*output rate ([\d-]+ bits/sec)",
            per_content, re.S)
        if aaa:
            interface_status, desc, input_flow, output_flow = aaa[0]
            query_obj.desc = desc
        else:
            query_obj.desc = "端口无描述or匹配错误"
            interface_status = "无匹配结果"
            input_flow = "无匹配结果"
            output_flow = "无匹配结果"
        query_obj.command_result_detail = per_content
        self.tn.write(b"show controllers %s phy\n" % query_obj.interfaces.encode())
        time.sleep(0.1)
        per_content = mydecode(my_read_very_eager(self.tn))
        query_obj.command_result_detail += per_content  # 保存了该对象输入的所有命令的结果
        bbb = re.findall(r"Rx Power: {2}.*mW \(([\.\-\d]* dBm)\)", per_content)
        has_rx = bbb[0] if bbb else "收光匹配错误"

        query_obj.result_brief = "%s,%s,%s,%s" % (interface_status, has_rx, input_flow, output_flow)


class Juniper(NetworkDevie):
    def _telnet_Juniper_13_3R9_S5_2(self, username, password):  # 登录MX960
        self.tn.read_until(b"login:", timeout=10)
        self.tn.write(username + b"\n")  # 连接到win系统，使用cmd时，使用r'rn'
        self.tn.read_until(b"password:", timeout=10)
        self.tn.write(password + b"\n")
        # time.sleep(0.1)
        # 命令没找到！！！！！
        # self.tn.write(b"show configuration | no-more \n")  # MX960设置命令不分页显示
        # time.sleep(0.6)
        content = mydecode(my_read_very_eager(self.tn))
        if not self.device_obj.enable:
            self.device_obj.name = re.findall(r"@(.*)>", content)[0].lower()
            self.device_obj.enable = True
            self.device_obj.save()

    def _query_Juniper_13_3R9_S5_2(self, query_obj):
        self.tn.write(b"show interfaces %s | no-more \n" % query_obj.interfaces.encode())
        time.sleep(0.1)
        per_content = mydecode(my_read_very_eager(self.tn))
        aaa = re.findall(
            r"Physical link is (Up|Down).*Description: ([\S ]*).*\(([\d-]+ pps)\).*\(([\d-]+ pps)\)",
            per_content, re.S)
        if aaa:
            interface_status, desc, input_flow, output_flow = aaa[0]
            query_obj.desc = desc
        else:
            query_obj.desc = "端口无描述or匹配错误"
            interface_status = "无匹配结果"
            input_flow = "无匹配结果"
            output_flow = "无匹配结果"
        query_obj.command_result_detail = per_content
        self.tn.write(b"show interfaces diagnostics optics %s | no-more\n" % query_obj.interfaces.encode())
        time.sleep(0.1)
        per_content = mydecode(my_read_very_eager(self.tn))
        query_obj.command_result_detail += per_content  # 保存了该对象输入的所有命令的结果
        bbb = re.findall(r"Laser rx power {5}[\S ]*mW / ([\.\-\d Inf]+ dBm)", per_content)
        if not bbb:
            bbb = re.findall(r"Receiver signal average optical power {5}[\S ]*mW / ([\.\-\d Inf]+ dBm)", per_content)
        if not bbb:
            bbb = re.findall(r"Laser receiver power {5}[\S ]*mW / ([\.\-\d Inf]+ dBm)", per_content)
        has_rx = bbb[0] if bbb else "收光匹配错误"

        query_obj.result_brief = "%s,%s,%s,%s" % (interface_status, has_rx, input_flow, output_flow)


"""（epon，ISP接入、pop、cmts_pop、core、BRAS、SR、PE、公安监控eopn、出口、电子政务网核心、电子政务网接入、郊县BRAS、郊县POP、）"""
"""登录的方法是一样的，只需要在登录时判断认证方式，若账号密码为其他类型，则将username,password的内容替换"""


class Epon(H3C, Raisecom):
    # def __init__(self, IP):
    #     self.device_obj = models.Device.objects.get(IP=IP)
    #     self.IP = IP
    #     self.tn = self.__connect()

    # def __connect(self):
    #     obj = None
    #     try:
    #         obj = telnetlib.Telnet(self.IP, port=23, timeout=10)
    #     except:
    #         print("telnet %s连接失败，创建EPON对象失败" % self.IP)
    #     return obj

    def __version_check_update(self):
        self.abc = "版本检查时"
        if self.tn:
            # time.sleep(7)
            time.sleep(1)
            content = mydecode(my_read_very_eager(self.tn))
            time.sleep(1)
            if "Username" in content:  # 判断为华三7502  软件版本5.0
                # print("判断为7502E")
                self.tn.write(username1 + b"\n")
                self.tn.read_until(b"Password:")
                self.tn.write(password1 + b"\n")
                time.sleep(0.1)
                content = mydecode(my_read_very_eager(self.tn))
                self.tn.write(b'su\n')
                # tn.read_until(b"Password:") #遇到一台super没有密码的，然后就挂了……
                time.sleep(0.1)
                self.tn.write(b'hzcnc_enable\n')
                time.sleep(0.1)
                self.tn.write(b'screen-length disable \n')
                time.sleep(0.1)
                content = mydecode(my_read_very_eager(self.tn))

                self.tn.write(b'dis version \n')
                time.sleep(0.2)
                content = mydecode(my_read_very_eager(self.tn))

                name = re.findall("<(.*)>", content)
                version = re.findall("Version \d\.\d{1,2}", content)
                if name and self.device_obj.name != name[0].lower():  # 设备名称有变化，则更新
                    self.device_obj.name = name[0].lower()

                company_obj = models.Company.objects.get(name="H3C")
                version_obj = models.Version.objects.get(name="Version 5.20")
                authmode_obj = models.AuthMode.objects.get(name="aaa+super")

                tag_obj = getattr(self.device_obj, "tag", None)
                # print("tag_obj:",tag_obj)
                if tag_obj and tag_obj.version == version_obj and tag_obj.authmode == authmode_obj and \
                        tag_obj.company == company_obj:

                    pass
                else:  # 重新绑定tag对象
                    print("%s,该设备绑定的Tag对象已重置" % self.IP)
                    tag_obj = models.Tag.objects.get(version=version_obj, authmode=authmode_obj, company=company_obj,name="EPON")
                    self.device_obj.tag = tag_obj
            elif "login" in content:
                # print("判断为7602")
                self.tn.write(username1 + b"\n")
                self.tn.read_until(b"Password:")
                self.tn.write(password1 + b"\n")
                time.sleep(0.1)
                # tn.read_until(b"Password:") #遇到一台super没有密码的，然后就挂了……
                self.tn.write(b'su\n')
                # self.tn.read_until(b"Password:")
                time.sleep(0.1)
                self.tn.write(b'hzcnc_enable\n')
                time.sleep(0.1)
                my_read_very_eager(self.tn)
                self.tn.write(b'screen-length disable \n')
                time.sleep(0.1)
                my_read_very_eager(self.tn)

                self.tn.write(b'dis version\n')
                time.sleep(0.3)
                content = mydecode(my_read_very_eager(self.tn))
                name = re.findall("<(.*)>", content)
                version = re.findall("Version \d\.\d{1,2}", content)
                if name and self.device_obj.name != name[0].lower():  # 设备名称有变化，则更新
                    self.device_obj.name = name[0].lower()

                company_obj = models.Company.objects.get(name="H3C")
                version_obj = models.Version.objects.get(name="Version 7.1")
                authmode_obj = models.AuthMode.objects.get(name="aaa+super")

                tag_obj = getattr(self.device_obj, "tag", None)
                if tag_obj and tag_obj.version == version_obj and tag_obj.authmode == authmode_obj and \
                        tag_obj.company == company_obj:
                    pass
                else:  # 重新绑定tag对象
                    print("%s,该设备绑定的Tag对象已重置" % self.IP)
                    tag_obj = models.Tag.objects.get(version=version_obj, authmode=authmode_obj, company=company_obj,name="EPON")
                    self.device_obj.tag = tag_obj
            elif "Login" in content:  #
                # print("判断为瑞斯康达")
                self.tn.write(username1 + b"\n")
                self.tn.read_until(b"Password:")
                self.tn.write(password1 + b"\n")
                time.sleep(0.5)  # 等待后开始读取数据，判断设备类型  这里不能太快，瑞斯康达设备有点慢啊
                my_read_very_eager(self.tn)
                time.sleep(0.5)
                self.tn.write(b'en \n')
                # self.tn.read_until(b"Password:")
                time.sleep(0.5)
                self.tn.write(b'hzcnc_enable\n')
                time.sleep(0.1)
                my_read_very_eager(self.tn)
                self.tn.write(b'terminal page-break disable \n')
                time.sleep(0.1)
                # my_read_very_eager(self.tn)

                # self.tn.write(b'show ver \n')
                # time.sleep(0.1)
                content = mydecode(my_read_very_eager(self.tn))
                name = re.findall("(\S*)#", content)

                if name and self.device_obj.name != name[0].lower():  # 设备名称有变化，则更新
                    self.device_obj.name = name[0].lower()

                company_obj = models.Company.objects.get(name="Raisecom")
                version_obj = models.Version.objects.get(name="ISCOM5800E-SMCB_1.44")
                authmode_obj = models.AuthMode.objects.get(name="aaa+hzcnc_enable")

                tag_obj = getattr(self.device_obj, "tag", None)
                if tag_obj and tag_obj.version == version_obj and tag_obj.authmode == authmode_obj and \
                        tag_obj.company == company_obj:
                    pass
                else:  # 重新绑定tag对象
                    print("%s,该设备绑定的Tag对象已重置" % self.IP)
                    tag_obj = models.Tag.objects.get(version=version_obj, authmode=authmode_obj, company=company_obj,name="EPON")
                    self.device_obj.tag = tag_obj
                    self.device_obj.enable = True
            else:
                print("%s 该EPON信息检查失败" % self.IP)

            self.device_obj.enable = True
            self.device_obj.save()
        else:
            print("%s登录失败" % self.IP)
            self.device_obj.enable = False
            self.device_obj.save()
        self.version = self.device_obj.tag.version.name

    def __olts_check_update(self):
        self.abc = "olts信息更新时"
        if self.tn:
            if self.version == "Version 5.20":
                # print("进入Version 5.20 olt更新")
                self.tn.write(b'dis int olt brief\n')
                time.sleep(0.2)
                content = mydecode(my_read_very_eager(self.tn))
                ret = re.findall(r"(Olt\d{1,2}/0/\d{1,2}).*?(\d{4}[A-Za-z]{1,2}-[A-Za-z]{1,2}-{0,1}[A-Za-z]{0,2})",
                                 content)
                for olt_interface, olt_name in ret:
                    try:
                        obj = models.Olt.objects.get_or_create(epon=self.device_obj, interface=olt_interface.lower())[0]

                        if obj.name != olt_name.lower():
                            obj.name = olt_name.lower()
                            obj.save()
                            print("H3C Version 5.20 %s %s 新增or修改" % (self.IP, obj.interface))
                    except Exception as errors:
                        print(errors, self.IP, "olt", olt_interface, olt_name)

                ret = re.findall(r"Olt\d{1,2}/0/\d{1,2}", content)
                # print("ret:%s" % ret)
                for olt_interface in ret:
                    try:
                        models.Olt.objects.get_or_create(epon=self.device_obj, interface=olt_interface.lower())
                    except Exception as errors:
                        print(errors)
            elif self.version == "Version 7.1":
                # print("进入Version 7.1 olt更新")
                self.tn.write(b'dis int olt brief\n')
                time.sleep(0.2)
                content = mydecode(my_read_very_eager(self.tn))
                ret = re.findall(r"(Olt\d{1,2}/0/\d{1,2}).*?(\d{4}[A-Za-z]{1,2}-[A-Za-z]{1,2}-{0,1}[A-Za-z]{0,2})",
                                 content)
                for olt_interface, olt_name in ret:
                    try:
                        obj = models.Olt.objects.get_or_create(epon=self.device_obj, interface=olt_interface.lower())[0]

                        if obj.name != olt_name.lower():
                            obj.name = olt_name.lower()
                            obj.save()
                            print("H3C Version 7.1 %s %s 新增or修改" % (self.IP, obj.interface))
                    except Exception as errors:
                        print(errors, self.IP, "olt", olt_interface, olt_name)
                ret = re.findall(r"Olt\d{1,2}/0/\d{1,2}", content)
                # print("ret:%s" % ret)
                for olt_interface in ret:
                    try:
                        models.Olt.objects.get_or_create(epon=self.device_obj, interface=olt_interface.lower())
                    except Exception as errors:
                        print(errors)
            elif self.version == "ISCOM5800E-SMCB_1.44":
                for k, v in port_mapping.items():
                    models.Olt.objects.get_or_create(epon=self.device_obj, interface=v)
                self.tn.write(b"show interface port description \n")
                time.sleep(0.1)
                content = mydecode(my_read_very_eager(self.tn))
                ret = re.findall(r"(\d{1,2}) *?(\d{4}[A-Za-z]{1,2}-[A-Za-z]{1,2}-{0,1}[A-Za-z]{0,2})", content)
                for port, olt_name in ret:
                    if int(port) < 17:
                        # 瑞斯康达port17及以上对应的分光器编号需要手动更新
                        try:
                            interface = port_mapping[port]
                            obj_olt = models.Olt.objects.get_or_create(epon=self.device_obj, interface=interface)[0]
                            if obj_olt.name != olt_name.lower():
                                obj_olt.name = olt_name.lower()
                                obj_olt.save()
                                print("瑞斯康达 %s %s 新增or修改" % (self.IP, obj_olt.interface))
                        except Exception as errors:
                            print(errors, self.IP, "olt", port, olt_name)
            else:
                pass

    def __onus_check_update(self):
        self.abc = "onus信息更新时"
        if self.tn:
            if self.version == "Version 5.20":
                olts_obj = self.device_obj.olt_set.all()
                for olt_obj in olts_obj:
                    try:
                        self.tn.write(b'dis onuinfo interface %s\n' % bytes(olt_obj.interface, "utf-8"))

                        time.sleep(0.2)
                        content = mydecode(my_read_very_eager(self.tn))
                        ret = re.findall(r"(\w{4}-\w{4}-\w{4}).*?(Onu(\d{1,2}/0/\d{1,2}):\d{1,2})", content)
                        for mac, onu_interface, olt_interface in ret:
                            try:
                                obj_olt = \
                                    models.Olt.objects.filter(epon=self.device_obj, interface__contains=olt_interface)[
                                        0]
                                onu_obj = models.Onu.objects.get_or_create(interface=onu_interface.lower(),
                                                                           olt=obj_olt)[0]
                                if not onu_obj.mac or onu_obj.mac != mac.replace("-", "").lower():
                                    onu_obj.mac = mac.replace("-", "").lower()
                                    onu_obj.save()
                                    print("H3C Version 5.20 %s %s 新增or修改" % (self.IP, onu_obj.interface))
                            except Exception as errors:
                                print(errors, self.IP, "onu1", onu_interface, mac)
                        ret = re.findall(r"(\w{4}-\w{4}-\w{4}).*?Silent", content)
                        if ret:
                            olt_obj.silent_onus = "#".join(ret).replace("-", "").lower()
                        else:
                            olt_obj.silent_onus = "None"
                        olt_obj.save()
                    except Exception as errors:
                        print(errors)
            elif self.version == "Version 7.1":
                # print("进入Version 7.1 olt更新")
                olts_obj = self.device_obj.olt_set.all()
                for olt_obj in olts_obj:
                    try:
                        self.tn.write(b'dis onu interface %s\n' % bytes(olt_obj.interface, "utf-8"))
                        time.sleep(0.2)
                        content = mydecode(my_read_very_eager(self.tn))
                        ret = re.findall(r"(\w{4}-\w{4}-\w{4}).*?(Onu(\d{1,2}/0/\d{1,2}):\d{1,2})", content)
                        for mac, onu_interface, olt_interface in ret:
                            try:
                                obj_olt = \
                                    models.Olt.objects.filter(epon=self.device_obj, interface__contains=olt_interface)[
                                        0]
                                onu_obj = models.Onu.objects.get_or_create(interface=onu_interface.lower(),
                                                                           olt=obj_olt)[0]
                                if not onu_obj.mac or onu_obj.mac != mac.replace("-", "").lower():
                                    onu_obj.mac = mac.replace("-", "").lower()
                                    onu_obj.save()
                                    print("H3C Version 7.1 %s %s 新增or修改" % (self.IP, onu_obj.interface))
                            except Exception as errors:
                                print(errors, self.IP, "onu", onu_interface, mac)
                        ret = re.findall(r"(\w{4}-\w{4}-\w{4}).*?Silent", content)
                        if ret:
                            olt_obj.silent_onus = "#".join(ret).replace("-", "").lower()
                        else:
                            olt_obj.silent_onus = "None"
                        olt_obj.save()
                    except Exception as errors:
                        print(errors)
            elif self.version == "ISCOM5800E-SMCB_1.44":
                self.tn.write(b'show inter onu information\n')
                time.sleep(0.2)
                content = mydecode(my_read_very_eager(self.tn))
                ret = re.findall(r"((\d/\d)/\d{1,2}).*?(\w{4}\.\w{4}\.\w{4})", content)
                for onu_interface, olt_interface, onu_mac in ret:
                    try:
                        obj_olt = models.Olt.objects.get_or_create(epon=self.device_obj, interface=olt_interface)[0]
                        onu_obj = models.Onu.objects.get_or_create(olt=obj_olt, interface=onu_interface)[0]
                        if not onu_obj.mac or onu_obj.mac != onu_mac.replace(".", "").lower():
                            onu_obj.mac = onu_mac.replace(".", "").lower()
                            onu_obj.save()
                            print("瑞斯康达 %s %s 新增or修改" % (self.IP, onu_obj.interface))
                    except Exception as errors:
                        print(errors, self.IP, "onu", onu_interface, onu_mac)
                olts_obj = models.Olt.objects.filter(epon=self.device_obj)
                for olt_obj in olts_obj:
                    try:
                        olt_obj.silent_onus = "None"
                        olt_obj.save()
                    except Exception as errors:
                        print(errors, self.IP, "重置silent_onus失败", olt_obj, )
                self.tn.write(b'show inter olt illegal-onu\n')
                time.sleep(0.2)
                content = mydecode(my_read_very_eager(self.tn))
                ret = re.findall(r"(\d/\d).*?(\w{4}\.\w{4}\.\w{4})", content)
                for olt_interface, onu_mac in ret:
                    try:
                        olt_obj = models.Olt.objects.filter(epon=self.device_obj, interface=olt_interface)[0]
                        olt_obj.silent_onus = "%s#%s" % (olt_obj.silent_onus, onu_mac.replace(".", "").lower())
                        olt_obj.save()
                    except Exception as errors:
                        print(errors, self.IP, "添加silent_onus失败", olt_interface, )

            else:
                pass

    def epon_check_update(self,index=0):
        self.abc = ""
        try:
            self.__version_check_update()
            self.__olts_check_update()
            self.__onus_check_update()
            self.close(index)
        except Exception as errors:
            print(errors)
            print("%s  %s出错，尝试关闭连接" % (self.IP,self.abc))
            self.close()

    def device_login(self, username, password):
        if self.device_obj.tag.version.name == "Version 5.20":
            self._telnet_h3c_ver_5(username, password)
        elif self.device_obj.tag.version.name == "Version 7.1":
            self._telnet_h3c_ver_7(username, password)
        # elif device_type == "Raisecom":
        else:
            self._telnet_Raisecom(username, password)


class CMTS_POP(H3C, CiscoNexus):
    def device_login(self, username, password):
        if self.device_obj.tag.version.name == "Version 5.20":
            self._telnet_h3c_ver_5(username, password)
        else:
            self._telnet_CiscoNexus_version_2_8_0(username, password)

    def cutting_query(self, query_obj):
        if self.device_obj.tag.version.name == "Version 5.20":
            self._query_h3c_ver_5_switch(query_obj)
        else:
            self._query_CiscoNexus_version_2_8_0(query_obj)


class POP(H3C, Cisco):
    def device_login(self, username, password):
        if self.device_obj.tag.version.name == "Version 7.1":
            self._telnet_h3c_ver_7(username, password)
        elif self.device_obj.tag.version.name == "Version 5.20":
            self._telnet_h3c_ver_5(username, password)
        elif self.device_obj.tag.version.name == "Version 12.2":
            self._telnet_Cisco_Version_12_2(username, password)

    def cutting_query(self, query_obj):
        if self.device_obj.tag.version.name == "Version 7.1":
            self._query_h3c_ver_7_switch(query_obj)
        elif self.device_obj.tag.version.name == "Version 5.20":
            self._query_h3c_ver_5_switch(query_obj)
        else:
            self._query_Cisco_Version_12_2(query_obj)


class CORE(Juniper):
    def device_login(self, username, password):
        if self.device_obj.tag.version.name == "14_1R8_6":
            # MX2020看起来和MX960是一样的，暂时使用同一个方法
            self._telnet_Juniper_13_3R9_S5_2(username, password)

    def cutting_query(self, query_obj):
        if self.device_obj.tag.version.name == "14_1R8_6":
            self._query_Juniper_13_3R9_S5_2(query_obj)


class BRAS(Juniper):
    def device_login(self, username, password):
        if self.device_obj.tag.version.name == "13_3R9_S5_2":
            self._telnet_Juniper_13_3R9_S5_2(username, password)

    def cutting_query(self, query_obj):
        if self.device_obj.tag.version.name == "13_3R9_S5_2":
            self._query_Juniper_13_3R9_S5_2(query_obj)


class PE(Cisco9K):
    def device_login(self, username, password):
        if self.device_obj.tag.version.name == "Version 4.3.4":
            self._telnet_Cisco9K_Version_4_3_4(username, password)

    def cutting_query(self, query_obj):
        if self.device_obj.tag.version.name == "Version 4.3.4":
            self._query_Cisco9K_Version_4_3_4(query_obj)


class ISP_Access(H3C, Cisco):
    def device_login(self, username, password):
        if self.device_obj.tag.version.name == "Version 7.1":
            self._telnet_h3c_ver_7(username, password)
        elif self.device_obj.tag.version.name == "Version 5.20":
            self._telnet_h3c_ver_5(username, password)
        elif self.device_obj.tag.version.name == "Version 12.2":
            self._telnet_Cisco_Version_12_2(username, password)
        elif self.device_obj.tag.version.name == "Version 12.1":
            self._telnet_Cisco_Version_12_2(username, password)

    def cutting_query(self, query_obj):
        if self.device_obj.tag.version.name == "Version 7.1":
            self._query_h3c_ver_7_switch(query_obj)
        elif self.device_obj.tag.version.name == "Version 5.20":
            self._query_h3c_ver_5_switch(query_obj)
        elif self.device_obj.tag.version.name == "Version 12.2":
            self._query_Cisco_Version_12_2(query_obj)
        elif self.device_obj.tag.version.name == "Version 12.1":
            self._query_Cisco_Version_12_2(query_obj)


class VPN_Access(ISP_Access):
    # VPN接入网设备和ISP接入网的分类一样，直接继承
    pass


class JX_POP(H3C, Cisco):
    def device_login(self, username, password):
        if self.device_obj.tag.authmode.name == "admin+super":
            username = b"admin"
            password = b"hzcnc_vty"
        if self.device_obj.tag.version.name == "Version 5.20":
            self._telnet_h3c_ver_5(username, password)
        elif self.device_obj.tag.version.name == "Version 7.1":
            self._telnet_h3c_ver_7(username, password)
        elif self.device_obj.tag.version.name == "Version 12.2":
            self._telnet_Cisco_Version_12_2(username, password)

    def cutting_query(self, query_obj):
        if self.device_obj.tag.version.name == "Version 5.20":
            self._query_h3c_ver_5_switch(query_obj)
        elif self.device_obj.tag.version.name == "Version 7.1":
            self._query_h3c_ver_7_switch(query_obj)
        else:
            self._query_Cisco_Version_12_2(query_obj)


class NAP(Cisco9K):
    def device_login(self, username, password):
        if self.device_obj.tag.version.name == "Version 4.3.4":
            self._telnet_Cisco9K_Version_4_3_4(username, password)

    def cutting_query(self, query_obj):
        if self.device_obj.tag.version.name == "Version 4.3.4":
            self._query_Cisco9K_Version_4_3_4(query_obj)


class JX_PE(Cisco9K,Juniper,Cisco):
    def device_login(self, username, password):
        if self.device_obj.tag.version.name == "Version 4.3.4":
            self._telnet_Cisco9K_Version_4_3_4(username, password)
        elif self.device_obj.tag.version.name == "13_3R9_S5_2":
            self._telnet_Juniper_13_3R9_S5_2(username, password)
        elif self.device_obj.tag.version.name == "Version 12.2":
            self._telnet_Cisco_Version_12_2(username, password)

    def cutting_query(self, query_obj):
        if self.device_obj.tag.version.name == "Version 4.3.4":
            self._query_Cisco9K_Version_4_3_4(query_obj)
        elif self.device_obj.tag.version.name == "13_3R9_S5_2":
            self._query_Juniper_13_3R9_S5_2(query_obj)
        elif self.device_obj.tag.version.name == "Version 12.2":
            self._query_Cisco_Version_12_2(query_obj)


class JX_BRAS(Juniper):
    def device_login(self, username, password):
        if self.device_obj.tag.version.name == "13_3R9_S5_2":
            self._telnet_Juniper_13_3R9_S5_2(username, password)

    def cutting_query(self, query_obj):
        if self.device_obj.tag.version.name == "13_3R9_S5_2":
            self._query_Juniper_13_3R9_S5_2(query_obj)


class AC(H3C):
    def device_login(self, username, password):
        if self.device_obj.tag.version.name == "Version 7.1":
            self._telnet_h3c_ver_7(username, password)
        elif self.device_obj.tag.version.name == "Version 5.20":
            self._telnet_h3c_ver_5(username, password)

    def cutting_query(self, query_obj):
        if self.device_obj.tag.version.name == "Version 7.1":
            self._query_h3c_ver_7_switch(query_obj)
        elif self.device_obj.tag.version.name == "Version 5.20":
            self._query_h3c_ver_5_switch(query_obj)


class NAT_EPT(Juniper,Cisco):
    def device_login(self, username, password):
        if self.device_obj.tag.version.name == "13_3R9_S5_2":
            self._telnet_Juniper_13_3R9_S5_2(username, password)
        elif self.device_obj.tag.version.name == "Version 12.2":
            self._telnet_Cisco_Version_12_2(username, password)

    def cutting_query(self, query_obj):
        if self.device_obj.tag.version.name == "13_3R9_S5_2":
            self._query_Juniper_13_3R9_S5_2(query_obj)
        elif self.device_obj.tag.version.name == "Version 12.2":
            self._query_Cisco_Version_12_2(query_obj)


class GOV_CORE(Cisco):
    def device_login(self, username, password):
        if self.device_obj.tag.version.name == "Version 12.2":
            self._telnet_Cisco_Version_12_2(username, password)

    def cutting_query(self, query_obj):
        if self.device_obj.tag.version.name == "Version 12.2":
            self._query_Cisco_Version_12_2(query_obj)


class SR(Cisco9K):
    def device_login(self, username, password):
        if self.device_obj.tag.version.name == "Version 4.3.4":
            self._telnet_Cisco9K_Version_4_3_4(username, password)

    def cutting_query(self, query_obj):
        if self.device_obj.tag.version.name == "Version 4.3.4":
            self._query_Cisco9K_Version_4_3_4(query_obj)