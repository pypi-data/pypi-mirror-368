import requests

def get_score(image_url="https://4147093qp2.imdo.co/yanzhi/54.jpg"):
    # API接口
    api_url = f"https://4147093qp2.imdo.co/yanzhi?url={image_url}"
    

    # 发送请求
    response = requests.get(api_url)
    
    # 检查请求是否成功
    if response.status_code == 200:
        # 从响应中获取颜值分数
        beauty_score = float(response.json()['ret'])
        return beauty_score
    else:
        print("Request failed with status code:", response.status_code)
        return None

