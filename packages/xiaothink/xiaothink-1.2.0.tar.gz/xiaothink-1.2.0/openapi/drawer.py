import requests
import urllib.parse


class Drawer():
    def __init__(self,return_type='bytes'):
        self.return_type=return_type

    def draw(self,description,style,filename=None):
        

        """
        根据给定的艺术图像描述和风格编号，调用清韵AI艺术图创作API，并返回生成的图像内容。

        :param description: str 艺术图像描述
        :param style: int 图像风格编号（1-8）
        :return: bytes 图像二进制数据
        """

        # 对描述进行URL编码
        encoded_description = urllib.parse.quote(description)

        # 构造请求URL
        url = f"https://4147093qp2.imdo.co/aidrawnew?text={encoded_description}&syle={style}"#注意这里是syle，别问为什么

        try:
            # 发送GET请求
            response = requests.get(url)
            
            # 检查请求是否成功
            if response.status_code == 200:
                # 获取并返回图像二进制数据
                if self.return_type=='bytes':
                    return response.content
                elif self.return_type=='file':
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    return None
                        
            else:
                print(f"请求失败，状态码：{response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"请求过程中发生错误：{e}")
            return None

    def help(self):
        print('''风格编号（1-8）：
    风格1 - 糖果 （candy）
    风格2 - 组成vii（composition vii）
    风格3 - 羽毛 （feathers）
    风格4 - la muse
    风格5 - 马赛克（mosaic）
    风格6 - 梵高·星空（starry_night）
    风格7 - 奶油（the_scream）
    风格8 - 波形（the_wave）
——————————————————————————————————
    支持的return_type：1.'bytes'——返回为图像的二进制数据
                       2.'file'——直接保存为filename
                       
''')

