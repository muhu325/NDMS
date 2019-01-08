import json
import requests
import re
from bs4 import BeautifulSoup


def get_businesses_info_by_id(id):  #
    '''通过id去爬虫，返回的dict保存了该id所对应的业务信息'''
    dict1 = {}
    url2 = "http://125.210.113.44/resource/config/detail/%s"  # 获得大部分的业务信息(%s用业务id来替换）
    r2 = requests.get(url=url2 % id)
    # print(url2%id)
    # print(r2.url)
    soup = BeautifulSoup(r2.text, "html.parser")
    aaa = soup.select('div[class="form-group form-group-sm"]')
    for i in aaa:
        # key = i.label.get_text().replace("*","")
        key = i.label.get("for")
        value = ""
        if i.select('option[selected="selected"]'):
            value = i.select('option[selected="selected"]')[0].get_text().replace(" ", "").replace("\r", "").replace(
                "\n", "")
        elif i.select('input[id="id_vpn_name"]'):  # VPN名称
            value = i.select('input[id="id_vpn_name"]')[0].get("value")
        elif i.select('input[id="id_user_type"]'):  # 用户类型
            value = i.select('input[id="id_user_type"]')[0].get("value")
        elif i.select('input[id="id_user_gateway"]'):  # 用户自用IP网关
            value = i.select('input[id="id_user_gateway"]')[0].get("value")
        elif i.select('input[id="id_code"]'):  # 设备配置信息
            value = i.select('input[id="id_code"]')[0].get("value")
        elif i.select('input[id="id_remark1"]'):  # 备注
            value = i.select('input[id="id_remark1"]')[0].get("value")
        elif i.select('input[id="id_bussiness_code"]'):  # 用户编号
            value = i.select('input[id="id_bussiness_code"]')[0].get("value")
        elif i.select('input[id="id_business_code"]'):  # 用户编号
            value = i.select('input[id="id_business_code"]')[0].get("value")
        elif i.select('input[id="id_unit"]'):  # 接入单位
            value = i.select('input[id="id_unit"]')[0].get("value")
        elif i.select('input[id="id_user_address"]'):  # 用户地址
            value = i.select('input[id="id_user_address"]')[0].get("value")
        elif i.select('input[id="id_mac_onu"]'):  # MAC地址ONU
            value = i.select('input[id="id_mac_onu"]')[0].get("value")
        # 当前逻辑机房这个是否需要？？？
        if value:
            dict1[key] = value

        # print(i)
        # print("---------------")

    parameters2 = {'draw': 1,  # 带#表示被修改过
                   'columns[0][data]': 'id',
                   'columns[0][name]': '',
                   'columns[0][searchable]': 'true',
                   'columns[0][orderable]': 'false',
                   'columns[0][search][value]': '',
                   'columns[0][search][regex]': 'false',
                   'columns[1][data]': 'code',  #
                   'columns[1][name]': '',
                   'columns[1][searchable]': 'true',
                   'columns[1][orderable]': 'false',
                   'columns[1][search][value]': '',
                   'columns[1][search][regex]': 'false',
                   'columns[2][data]': 'room_code',  #
                   'columns[2][name]': '',
                   'columns[2][searchable]': 'true',
                   'columns[2][orderable]': 'false',
                   'columns[2][search][value]': '',
                   'columns[2][search][regex]': 'false',
                   'start': 0,
                   'length': 10,
                   'search[value]': '',
                   'search[regex]': 'false',
                   'flag': 'a',
                   '_': 1541485611832,  # 是个时间戳，但具体是什么时候的时间戳呢？
                   }  # 用于查看业务信息时，获取vlan编号
    url3 = "http://125.210.113.44/resource/config/getVlanTabe/%s"  # 获得vlan资源的vlan编号
    r3 = requests.get(url=url3 % id, params=parameters2)
    # print(r3.url)
    # print("r3文本：",r3.text)
    dict1["vlan"] = json.loads(r3.text).get("data")[0].get("code") if json.loads(r3.text).get("data") else "None"
    return dict1


def get_id_list_by_olt_name_and_onu_interface(olt_name, onu_interface):
    '''通过分光器编号和onu编号查询，返回一个包含业务id的列表'''
    id_code = "%s%%%s" % (olt_name, onu_interface)
    parameters1 = {'draw': 2,
                   'columns[0][data]': 'id',
                   'columns[0][name]': '',
                   'columns[0][searchable]': 'true',
                   'columns[0][orderable]': 'false',
                   'columns[0][search][value]': '',
                   'columns[0][search][regex]': 'false',
                   'columns[1][data]': 'businessCode',
                   'columns[1][name]': '',
                   'columns[1][searchable]': 'true',
                   'columns[1][orderable]': 'false',
                   'columns[1][search][value]': '',
                   'columns[1][search][regex]': 'false',
                   'columns[2][data]': 'code',
                   'columns[2][name]': '',
                   'columns[2][searchable]': 'true',
                   'columns[2][orderable]': 'false',
                   'columns[2][search][value]': '',
                   'columns[2][search][regex]': 'false',
                   'columns[3][data]': 'macOnu',
                   'columns[3][name]': '',
                   'columns[3][searchable]': 'true',
                   'columns[3][orderable]': 'false',
                   'columns[3][search][value]': '',
                   'columns[3][search][regex]': 'false',
                   'columns[4][data]': 'unit',
                   'columns[4][name]': '',
                   'columns[4][searchable]': 'true',
                   'columns[4][orderable]': 'false',
                   'columns[4][search][value]': '',
                   'columns[4][search][regex]': 'false',
                   'columns[5][data]': 'business_type',
                   'columns[5][name]': '',
                   'columns[5][searchable]': 'true',
                   'columns[5][orderable]': 'false',
                   'columns[5][search][value]': '',
                   'columns[5][search][regex]': 'false',
                   'columns[6][data]': 'user_address',
                   'columns[6][name]': '',
                   'columns[6][searchable]': 'true',
                   'columns[6][orderable]': 'false',
                   'columns[6][search][value]': '',
                   'columns[6][search][regex]': 'false',
                   'columns[7][data]': 'room_name',
                   'columns[7][name]': '',
                   'columns[7][searchable]': 'true',
                   'columns[7][orderable]': 'false',
                   'columns[7][search][value]': '',
                   'columns[7][search][regex]': 'false',
                   'start': 0,
                   'length': 100,
                   'search[value]': '',
                   'search[regex]': 'false',
                   'room': '',
                   'business_code': '',
                   'unit': '',
                   'business_type': '',
                   'code': id_code,
                   'mac_onu': '',
                   'user_address': '',
                   '_': 1541476630092,  # 是个时间戳，但具体是什么时候的时间戳呢？
                   }  # 用于搜索配置信息

    id_list = []
    url1 = "http://125.210.113.44/onuEdit/getTable"  # 用于搜索
    r = requests.get(url=url1, params=parameters1)
    dict1 = json.loads(r.text)

    for i in dict1.get('data'):
        rmss_info = re.findall(r"^(.+?)\..+?\.(\d{2})", i.get("code"))[0]
        # print(rmss_info,type(rmss_info))
        if rmss_info[1] == onu_interface and rmss_info[0].replace(" ", "").lower() == olt_name:
            # 因为光靠1327e-hl%01这种筛选条件，可能会匹配到1327E-HL.5800E.07.01.02，所以在这里进一步筛选
            id_list.append(i.get("id"))
    return id_list


def get_id_list_by_configure_info(configure_info):
    '''通过配置信息去查询，返回一个包含业务id的列表'''
    parameters1 = {'draw': 2,
                   'columns[0][data]': 'id',
                   'columns[0][name]': '',
                   'columns[0][searchable]': 'true',
                   'columns[0][orderable]': 'false',
                   'columns[0][search][value]': '',
                   'columns[0][search][regex]': 'false',
                   'columns[1][data]': 'businessCode',
                   'columns[1][name]': '',
                   'columns[1][searchable]': 'true',
                   'columns[1][orderable]': 'false',
                   'columns[1][search][value]': '',
                   'columns[1][search][regex]': 'false',
                   'columns[2][data]': 'code',
                   'columns[2][name]': '',
                   'columns[2][searchable]': 'true',
                   'columns[2][orderable]': 'false',
                   'columns[2][search][value]': '',
                   'columns[2][search][regex]': 'false',
                   'columns[3][data]': 'macOnu',
                   'columns[3][name]': '',
                   'columns[3][searchable]': 'true',
                   'columns[3][orderable]': 'false',
                   'columns[3][search][value]': '',
                   'columns[3][search][regex]': 'false',
                   'columns[4][data]': 'unit',
                   'columns[4][name]': '',
                   'columns[4][searchable]': 'true',
                   'columns[4][orderable]': 'false',
                   'columns[4][search][value]': '',
                   'columns[4][search][regex]': 'false',
                   'columns[5][data]': 'business_type',
                   'columns[5][name]': '',
                   'columns[5][searchable]': 'true',
                   'columns[5][orderable]': 'false',
                   'columns[5][search][value]': '',
                   'columns[5][search][regex]': 'false',
                   'columns[6][data]': 'user_address',
                   'columns[6][name]': '',
                   'columns[6][searchable]': 'true',
                   'columns[6][orderable]': 'false',
                   'columns[6][search][value]': '',
                   'columns[6][search][regex]': 'false',
                   'columns[7][data]': 'room_name',
                   'columns[7][name]': '',
                   'columns[7][searchable]': 'true',
                   'columns[7][orderable]': 'false',
                   'columns[7][search][value]': '',
                   'columns[7][search][regex]': 'false',
                   'start': 0,
                   'length': 100,
                   'search[value]': '',
                   'search[regex]': 'false',
                   'room': '',
                   'business_code': '',
                   'unit': '',
                   'business_type': '',
                   'code': configure_info,
                   'mac_onu': '',
                   'user_address': '',
                   '_': 1541476630092,  # 是个时间戳，但具体是什么时候的时间戳呢？
                   }  # 用于搜索配置信息
    url1 = "http://125.210.113.44/onuEdit/getTable"  # 用于搜索
    r1 = requests.get(url=url1, params=parameters1)
    dict1 = json.loads(r1.text)
    id_list = []
    for i in dict1.get('data'):
        if i["id"]:
            id_list.append(i["id"])
    return id_list


def get_id_list_by_businesses_code(businesses_code):
    '''通过业务编码去查询，返回一个包含业务id的列表'''
    parameters1 = {'draw': 2,
                   'columns[0][data]': 'id',
                   'columns[0][name]': '',
                   'columns[0][searchable]': 'true',
                   'columns[0][orderable]': 'false',
                   'columns[0][search][value]': '',
                   'columns[0][search][regex]': 'false',
                   'columns[1][data]': 'businessCode',
                   'columns[1][name]': '',
                   'columns[1][searchable]': 'true',
                   'columns[1][orderable]': 'false',
                   'columns[1][search][value]': '',
                   'columns[1][search][regex]': 'false',
                   'columns[2][data]': 'code',
                   'columns[2][name]': '',
                   'columns[2][searchable]': 'true',
                   'columns[2][orderable]': 'false',
                   'columns[2][search][value]': '',
                   'columns[2][search][regex]': 'false',
                   'columns[3][data]': 'macOnu',
                   'columns[3][name]': '',
                   'columns[3][searchable]': 'true',
                   'columns[3][orderable]': 'false',
                   'columns[3][search][value]': '',
                   'columns[3][search][regex]': 'false',
                   'columns[4][data]': 'unit',
                   'columns[4][name]': '',
                   'columns[4][searchable]': 'true',
                   'columns[4][orderable]': 'false',
                   'columns[4][search][value]': '',
                   'columns[4][search][regex]': 'false',
                   'columns[5][data]': 'business_type',
                   'columns[5][name]': '',
                   'columns[5][searchable]': 'true',
                   'columns[5][orderable]': 'false',
                   'columns[5][search][value]': '',
                   'columns[5][search][regex]': 'false',
                   'columns[6][data]': 'user_address',
                   'columns[6][name]': '',
                   'columns[6][searchable]': 'true',
                   'columns[6][orderable]': 'false',
                   'columns[6][search][value]': '',
                   'columns[6][search][regex]': 'false',
                   'columns[7][data]': 'room_name',
                   'columns[7][name]': '',
                   'columns[7][searchable]': 'true',
                   'columns[7][orderable]': 'false',
                   'columns[7][search][value]': '',
                   'columns[7][search][regex]': 'false',
                   'start': 0,
                   'length': 30,  # 这里控制了每次最多查询到多少数据
                   'search[value]': '',
                   'search[regex]': 'false',
                   'room': '',
                   'business_code': businesses_code,
                   'unit': '',
                   'business_type': '',
                   'code': '',
                   'mac_onu': '',
                   'user_address': '',
                   '_': 1541476630092,  # 是个时间戳，但具体是什么时候的时间戳呢？
                   }  # 用于搜索业务编码
    url1 = "http://125.210.113.44/onuEdit/getTable"  # 用于搜索
    r1 = requests.get(url=url1, params=parameters1)
    dict1 = json.loads(r1.text)
    id_list = []
    for i in dict1.get('data'):
        if i["id"]:
            id_list.append(i["id"])
    return id_list


def get_businesses_info_list(id_list):
    '''# 返回一个列表，列表内的每一个字典为一个业务信息'''
    businesses_info_list = []
    if id_list:
        for id in id_list:
            businesses_info_list.append(get_businesses_info_by_id(id))
    return businesses_info_list


# 返回一个列表，列表内的每一个字典为一个业务信息
def get_businesses_info_list_by_olt_name_and_onu_interface(olt_name, onu_interface):
    id_list = get_id_list_by_olt_name_and_onu_interface(olt_name, onu_interface)
    return get_businesses_info_list(id_list)


# 根据配置信息查询
def get_businesses_info_list_by_configure_info(configure_info):
    id_list = get_id_list_by_configure_info(configure_info)
    return get_businesses_info_list(id_list)


def get_businesses_info_list_by_businesses_code(businesses_code):
    id_list = get_id_list_by_businesses_code(businesses_code)
    return get_businesses_info_list(id_list)





'''从app01.myviews.sql_query_vpn 搬运过来的'''
def get_busenesses_brief_info_by_businesses_code(businesses_code):
    parameters1 = {'draw': 2,
                   'columns[0][data]': 'id',
                   'columns[0][name]': '',
                   'columns[0][searchable]': 'true',
                   'columns[0][orderable]': 'false',
                   'columns[0][search][value]': '',
                   'columns[0][search][regex]': 'false',
                   'columns[1][data]': 'businessCode',
                   'columns[1][name]': '',
                   'columns[1][searchable]': 'true',
                   'columns[1][orderable]': 'false',
                   'columns[1][search][value]': '',
                   'columns[1][search][regex]': 'false',
                   'columns[2][data]': 'code',
                   'columns[2][name]': '',
                   'columns[2][searchable]': 'true',
                   'columns[2][orderable]': 'false',
                   'columns[2][search][value]': '',
                   'columns[2][search][regex]': 'false',
                   'columns[3][data]': 'macOnu',
                   'columns[3][name]': '',
                   'columns[3][searchable]': 'true',
                   'columns[3][orderable]': 'false',
                   'columns[3][search][value]': '',
                   'columns[3][search][regex]': 'false',
                   'columns[4][data]': 'unit',
                   'columns[4][name]': '',
                   'columns[4][searchable]': 'true',
                   'columns[4][orderable]': 'false',
                   'columns[4][search][value]': '',
                   'columns[4][search][regex]': 'false',
                   'columns[5][data]': 'business_type',
                   'columns[5][name]': '',
                   'columns[5][searchable]': 'true',
                   'columns[5][orderable]': 'false',
                   'columns[5][search][value]': '',
                   'columns[5][search][regex]': 'false',
                   'columns[6][data]': 'user_address',
                   'columns[6][name]': '',
                   'columns[6][searchable]': 'true',
                   'columns[6][orderable]': 'false',
                   'columns[6][search][value]': '',
                   'columns[6][search][regex]': 'false',
                   'columns[7][data]': 'room_name',
                   'columns[7][name]': '',
                   'columns[7][searchable]': 'true',
                   'columns[7][orderable]': 'false',
                   'columns[7][search][value]': '',
                   'columns[7][search][regex]': 'false',
                   'start': 0,
                   'length': 30,  # 这里控制了每次最多查询到多少数据
                   'search[value]': '',
                   'search[regex]': 'false',
                   'room': '',
                   'business_code': businesses_code,
                   'unit': '',
                   'business_type': '',
                   'code': '',
                   'mac_onu': '',
                   'user_address': '',
                   '_': 1541476630092,  # 是个时间戳，但具体是什么时候的时间戳呢？
                   }  # 用于搜索业务编码
    url1 = "http://125.210.113.44/onuEdit/getTable"  # 用于搜索
    r1 = requests.get(url=url1, params=parameters1)
    dict1 = json.loads(r1.text)
    rmss_code_list = []
    for i in dict1.get('data'):
        # print(i)
        if i.get("code"):
            rmss_code_list.append(i.get("code"))
    return rmss_code_list