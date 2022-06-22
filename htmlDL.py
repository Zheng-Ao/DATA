'''
A universal html downloader.

const: The constant part of url string.
var: The changing part of url string.
'''





import requests


def getHtmlDoc(const, var):
    try:
        var = str(var)
        url = const + var
        r = requests.get(url, timeout=30)
        r.raise_for_status
        return r.text
    except Exception as ex:
        print("{}采集出错，出错原因：{}".format(var, ex))
        return ""

