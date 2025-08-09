import requests
import os
#import set_conf
def get_key(key):
    p='C:'+os.environ['HOMEPATH']
    try:
        #open(os.path.join(p,'xiaothink_conf.conf','rb'))
        with open(os.path.join(p,'xiaothink_conf.conf'),'r',encoding='utf-8')as f:
            data=eval(f.read())
    except FileNotFoundError:
        
            data={}
    if key in list(data.keys()):
        return data[key]
    else:
        return None


    
def chat(text,usern=None):
    """
    text: 聊天内容
    usern:你的用户名（暂时不需要注册，直接起一个就行）
    """
    if not usern:
        usern=get_key('XIAOTHINK_USERNAME')
    #print(usern)
    r = requests.get(f'https://4147093qp2.imdo.co/openapi/user-chat?inp={text}&user={usern}')
    return r.json()['data']['result'].split('\n')[0]
