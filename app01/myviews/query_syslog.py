from app01.utils.auth_decorator import auth
from django.shortcuts import render
from app01.utils.class_for_query_by_excel import FinalResult


@auth
def sql_syslog_query(req):#应该加入一个判断，设置最大查询数目，超出则报错
    if req.method == "GET":
        return render(req,"query_syslog.html",)
    else:
        username = req.session.get("username")
        password = req.session.get("password")

        excel_content = req.POST.get("syslog_alarm_words")  # excel表内容
        final_result_obj = FinalResult()
        """-----------------------下面进行syslog告警信息进行分组--------------------------------------"""
        final_result_obj.processing_excel_content(excel_content)
        """-----------------------开始telnet设备进行查询--------------------------------------"""
        print("需要登录%s台设备进行查询" % len(final_result_obj.queried_obj_sored_by_IP))
        final_result_obj.telnet_query(username, password)

        """-------------------------------下面开始生成返回信息---------------------------------"""
        result = "以下内容无查询结果\n"
        for i in final_result_obj.rows_list:
            if not i.query_obj_list:
                result += "%s\n" %i.row_excel
        for i in final_result_obj.queried_obj_sored_by_IP:
            for w in i.get("query_objs"):
                if not hasattr(w,"result_brief"):
                    for x in final_result_obj.rows_list:
                        if x.num == w.num:
                            result += "%s\n" % x.row_excel
                            break
        result += "--------------------------------------------------------------------------------\n"
        result += "以下为查询结果汇总\n"
        for i in final_result_obj.queried_obj_sored_by_IP:
            for w in i.get("query_objs"):
                if hasattr(w,"result_brief"):
                    result += "管理ip：%s，设备名称：%s, 端口：%s，状态：%s，描述：%s\n"%(w.ip,w.name,w.interfaces,getattr(w,"result_brief","无结果"),getattr(w,"desc","无结果"))
        result += "--------------------------------------------------------------------------------\n"
        result += "以下为查询结果详情\n"
        for i in final_result_obj.queried_obj_sored_by_IP:
            for w in i.get("query_objs"):
                result += "管理ip：%s，设备名称：%s \n" % (w.ip, w.name)
                result += getattr(w,"command_result_detail","无结果")

        return render(req, "query_syslog.html",
                      {"syslog_alarm_words": excel_content, "query_result": result})





