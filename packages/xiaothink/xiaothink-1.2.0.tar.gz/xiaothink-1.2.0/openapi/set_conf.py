import os
def set_user(name):
    p='C:'+os.environ['HOMEPATH']
    try:
        open(os.path.join(p,'xiaothink_conf.conf','rb'))
        with open(os.path.join(p,'xiaothink_conf.conf'),'r',encoding='utf-8')as f:
            data=eval(f.read())
    except FileNotFoundError:
        
            data={}
            
    data['XIAOTHINK_USERNAME']=name
    with open(os.path.join(p,'xiaothink_conf.conf'),'w',encoding='utf-8')as f:
            f.write(str(data))

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
    

