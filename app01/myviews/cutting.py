from django.shortcuts import render
from app01.utils.auth_decorator import auth
from app01.utils.class_for_query_by_excel import FinalResult

@auth
def sql_cutting_query(req):  # 应该加入一个判断，设置最大查询数目，超出则报错
    username = req.session.get("username")
    password = req.session.get("password")
    if req.method == "GET":
        return render(req, "query_cutting.html", )
    else:
        excel_content = req.POST.get("cutting_words")  # excel表内容
        previous_online_onu_mac_result = req.POST.get("previous_online_onu_mac_result")  # excel中之前的onu在线情况

        final_result_obj = FinalResult()
        """-----------------------下面进行excel表处理--------------------------------------"""
        final_result_obj.processing_excel_content(excel_content)
        """-----------------------开始telnet设备进行查询--------------------------------------"""
        print("需要登录%s台设备进行查询" % len(final_result_obj.queried_obj_sored_by_IP))
        final_result_obj.telnet_query(username, password)
        """------------------------表1，表2的处理完了，接下来就是准备割接后表3表4表5的准备了---------------"""
        final_result_obj.processing_data_for_excel345(previous_online_onu_mac_result, username, password)
        """----------------下面开始把查询到的数据写入excel中------------------------"""
        final_result_obj.save_into_file()
        download_url = "/statics/cutting_query_result/割接查询结果.xlsx"
        # 最后的任务就是把数据写入到txt文档和excel表格中，同时最好rmss和onu的绑定工作
        return render(req, "query_cutting.html", {"string": excel_content,
                                                  "download_url": download_url})  #
