import hashlib
from collections import OrderedDict
from urllib.parse import urlencode, quote
from httptesting.library.scripts import print_backgroup_color

class Extend:

    @staticmethod
    def _sort_dict(pyload):
        """
        字典数据递归排序，包含列表排序
        :param pyload: 字典数据
        :return: 排序后的OrderedDict字典
        """
        item = 'p.items()'
        if type(pyload).__name__ == 'list':
            p = sorted(pyload)
            item = 'enumerate(p)'
        elif type(pyload).__name__ == 'dict':
            p = OrderedDict(sorted(pyload.items(), key=lambda a: a[0]))
        else:
            p = quote(pyload)

        for k, v in eval(item):

            if type(v).__name__ == 'list':
                if not v or (v is None) or v == "":
                    p.pop(k)
                else:
                    p[k] = list(Extend._sort_dict(sorted(v)))
            elif type(v).__name__ == 'dict':
                if not v or (v is None):
                    p.pop(k)
                else:
                    p[k] = dict(Extend._sort_dict(v))
                return p
            else:
                if v is None:
                    p.pop(k)
        return p

    # md5加密
    @staticmethod
    def _md5(str):
        """
        MD5加密
        :param str: 目标字符串
        :return: md5串
        """
        h1 = hashlib.md5()
        h1.update(str.encode(encoding='utf-8'))
        return h1.hexdigest()

    @staticmethod
    def _url_encode_func(payload):
        """
        生成url键值对
        :param payload: post数据
        :return: url键值对
        """
        newdict = {}
        payload = Extend._sort_dict(payload)

        for k, v in payload.items():

            if type(v).__name__ == 'list':
                for i, listval in enumerate(v):
                    if type(listval).__name__ == 'dict':
                        for m, vv in listval.items():
                            newdict['{}[{}][{}]'.format(k, i, m)] = vv
                    else:
                        newdict['{}[{}]'.format(k, i)] = listval
            elif type(v).__name__ == 'dict':
                for ck, cv in v.items():
                    i = 0
                    newdict['{}[{}]'.format(k, ck)] = cv
                    i += 1
            else:
                newdict[k] = v

        ret = urlencode(OrderedDict(sorted(newdict.items(),key=lambda a: a[0])))
        return ret

    @staticmethod
    def sign(data_dict):
        """
        根据微生活sig签名算法，生成sig签名md5
        :param kwargs: 参与签名的参数
        :return: sig签名md5字符串
        """
        print_backgroup_color(data_dict, color='green')
        kwargs = eval(data_dict)
        # 处理发送数据为空{}
        if kwargs['data']:
            URL_TMP = '{}&appid={}&appkey={}&v={}&ts={}'
        else:
            URL_TMP = '{}appid={}&appkey={}&v={}&ts={}'

        urlcode = URL_TMP.format(
            Extend._url_encode_func(kwargs['data']),
            kwargs['appid'],
            kwargs['appkey'],
            kwargs['v'],
            kwargs['ts']
        ).replace('False', '0').replace('True', '1')

        sig = str(Extend._md5(urlcode)).lower()
        return sig
    
    @staticmethod
    def demo2(a, b):
        return a + b

if __name__ == "__main__":
    data = {
        "remark": "test", 
        "shop_id": 1905736354, 
        "change_type": 1, 
        "cno": "1802326514043775", 
        "cashier_id": "1131294517", 
        "money": 100, 
        "award_money": 100
        }
    ts = 1564967996
    v = 2.0
    appid = "dp3Go73mm5jUiuQaWDe4W"
    appkey = "3ea8bfbf0574b89ae6b9e4717a34f53f"

    sig = Extend.sign(data=data, ts=ts, v=v, appid=appid, appkey=appkey)
    print(sig)
