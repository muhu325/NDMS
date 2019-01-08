import time, re

port_mapping = {"1": "1/1",
                "2": "1/2",
                "3": "1/3",
                "4": "1/4",
                "5": "2/1",
                "6": "2/2",
                "7": "2/3",
                "8": "2/4",
                "9": "3/1",
                "10": "3/2",
                "11": "3/3",
                "12": "3/4",
                "13": "4/1",
                "14": "4/2",
                "15": "4/3",
                "16": "4/4",
                }

port_mapping_reverse = {"1/1": "1",
                        "1/2": "2",
                        "1/3": "3",
                        "1/4": "4",
                        "2/1": "5",
                        "2/2": "6",
                        "2/3": "7",
                        "2/4": "8",
                        "3/1": "9",
                        "3/2": "10",
                        "3/3": "11",
                        "3/4": "12",
                        "4/1": "13",
                        "4/2": "14",
                        "4/3": "15",
                        "4/4": "16",
                        }


def my_read_very_eager(tn):  # 专用于enter后，读取内容,返回bytes类型数据
    content = b""
    time.sleep(0.1)
    for i in range(500):  # 不要用while，避免不可预知的错误
        time.sleep(0.03)
        curr_content = tn.read_very_eager()
        content = b"".join([content, curr_content])
        # if b"--More--" in content:
        #     content.replace(b"--More--", b"")
        #     print("匹配了--More--")
        #     tn.write(b" ")
        #     time.sleep(0.05)
        if re.findall(b"[\]#>:] ?$", curr_content):
            # print("匹配退出")
            break
    return content


def mydecode(content):
    try:
        aaa = content.decode("gb2312")
    except:
        aaa = content.decode("utf8", errors="ignore")
    return aaa
