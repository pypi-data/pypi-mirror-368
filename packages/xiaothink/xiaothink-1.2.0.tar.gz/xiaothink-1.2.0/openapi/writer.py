import requests
import urllib.parse


def write(original_text):
    # 对原文内容进行URL编码
    encoded_text = urllib.parse.quote(original_text)

    # 构造API请求URL
    api_url = f"https://4147093qp2.imdo.co/zhxxapi?inp={encoded_text}"

    # 发送GET请求并获取响应
    response = requests.get(api_url)
    
    # 解析返回结果
    result = response.json()

    if result["Error"] == "None":
        return original_text + result["text"]
    else:
        print("错误信息：", result["Error"])
        return None

