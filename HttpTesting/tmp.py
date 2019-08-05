# import io
# import json
# import os
# import collections
# import yaml

# class ConvertHarToYAML:

#     @classmethod
#     def from_har_to_dict(cls, harpath):
#         """
#         Convert from Charles HAR to a dict object.
#         :Param harpath: HAR file path.
#         usage:
#             dictReq = from_har_to_dict(harpath)
#         return: dictReq Har's dict object.
#         """
#         if os.path.exists(harpath):

#             with io.open(harpath, 'r+', encoding='utf-8-sig') as fp:
#                 rjson =fp.read()
#                 content_dict = json.loads(rjson)
#                 return content_dict['log']['entries']
#         else:
#             raise Exception("HAR file path error.{}".format(harpath))

#     @classmethod
#     def convert_to_list(cls, harpath):
#         """
#         convert HAR content to list
#         :param harpath: HAR file path.
#         usage:
#             ret_list = convert_to_list(harpath)
#         return:
#             [] request list.
#         """
#         ret = cls.from_har_to_dict(harpath)

#         req_list = []

#         for req in ret:
#             req_list.append(req['request'])

#         return req_list



#     @classmethod
#     def parse_headers_dict(cls, header):
#         """
#         parse Headers information.
#         """
#         try:
#             headers = {}
#             for i_dict in header:
#                 headers[i_dict['name']] = i_dict['value']
#             # print(headers)
#         except (KeyError, TypeError) as ex:
#             raise ex
#         return headers
    
#     @classmethod
#     def parse_post_data(cls, postData):
#         """
#         parse POST Data.
#         :param postData: HAR post data.
#         usage:
#         return:
#             dict data.
#         """
#         if isinstance(postData, dict):
#             data = postData['params']
#         else:
#             data = postData
#         dt = {}
#         try:
#             for i_list in data:
#                 dt[i_list['name']] = i_list['value']
#         except (KeyError, TypeError) as ex:
#             raise ex
#         return dt

#     @classmethod
#     def ordered_dump(cls, data, stream=None, Dumper=yaml.Dumper, **kwds):
#         """
#         Convert the unordered dictionary to ordered and write yaml.
#         param:
#             data: 
#             stream: 
#             allow_unicode:
#             default_flow_style:
#             indent:
#         return: There is no.
#         """
#         class OrderedDumper(Dumper):
#             pass
#         def _dict_representer(dumper, data):
#             return dumper.represent_mapping(
#                 yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
#                 data.items())
#         OrderedDumper.add_representer(collections.OrderedDict, _dict_representer)
#         return yaml.dump(data, stream, OrderedDumper, **kwds)


#     @classmethod
#     def write_case_to_yaml(cls, yampath, contentDict):
#         """
#         Write the test case to yaml.
#         param:
#             yampath: Yaml file path.
#         return:
#             There is no.
#         """
#         yamFile = os.path.join(yampath, 'har_testcase.yaml')
#         with io.open(yamFile, 'w', encoding='utf-8') as fp:
#             cls.ordered_dump(
#                 contentDict, 
#                 fp, 
#                 Dumper=yaml.SafeDumper, 
#                 allow_unicode=True, 
#                 default_flow_style=False, 
#                 indent=4
#             )


#     @classmethod
#     def convert_har_to_ht(cls, harfile):
#         """
#         Convert har files to pyhttp the test cases.
#         param:
#             harfile: HAR file full path.
#         return:
#             {} dict case.
#         """

#         temp_dict = {}
#         temp_dict['TEST_CASE'] = collections.OrderedDict()

#         ret = cls.convert_to_list(harfile)
#         # print(ret[0])

#         for n, val in enumerate(ret):
#             case = 'case{}'.format(n)
#             temp_dict['TEST_CASE'][case] =[]
#             temp_dict['TEST_CASE'][case].append({'Desc':'请添加接口描述'})

#             if val['method'] == 'GET':
#                 data = val['queryString']
#             else:
#                 data = val['postData']

#             url = val['url']
#             if '?' in val['url']:
#                 url = val['url'].split('?')[0]
                
#             temp_dict['TEST_CASE'][case].append(collections.OrderedDict({
#                 'Url': url,
#                 'Method': val['method'],
#                 'Headers': cls.parse_headers_dict(val['headers']),
#                 'Data': cls.parse_post_data(data),
#                 'InPara': "",
#                 'OutPara': "",
#                 'Assert': []
#             }))
#         # print(temp_dict)
#         return temp_dict

# import os
# from pyhttp.globalVar import gl
# from pyhttp.library.scripts import get_yaml_field


# def start_web_service():
#     """
#     Start a web service.
#     Args:
#     Uasge:
#         start_web_service()
#     Return:
#         There is no.
#     """
#     #Get configuration information.
#     ret = get_yaml_field(gl.configFile)

#     # Host and port Numbers.
#     _HOST = ret['REPORT_HOST']
#     _PORT = ret['REPORT_PORT']

#     # Web startup file.
#     service =  'service.py'

#     #Set the web directory to the current command line directory.
#     cmd = 'cd {} && python {} --host {} --port {}'.format(gl.webPath, service, _HOST, _PORT)

#     #Command to start service.
#     os.system(cmd)


# if __name__ == "__main__":
#     start_web_service()
#     # temp_dict = ConvertHarToYAML.convert_har_to_ht(r'D:\httphar.har')
#     # ConvertHarToYAML.write_case_to_yaml('', temp_dict)
#     # start_web_service()
#     service = os.path.join(gl.webPath, 'service.py')
#     os.system(r'python {}'.format(service))





# write_case_to_yaml('aaaa.yaml', data)


# convert_yaml('aaaa.yaml')
# import requests
# import io
# headers = {
#             "content-type": "application/x-www-form-urlencoded",
#             "corpId": "bd71adbcca6943858c044df160d994f1",
#             "userId": "7a86cd7c203b45ee9b881fc3a5312f32"
# }
# url = 'http://10.152.64.9:2222/cloudfi/report/excel/accountbalancereport'
# pyload = {"datas":'{\"yearSumColumnNotShow\":false,\"corpid\":\"2f19d3a991a547b09a5aad8df82cddb2\",\"cleanNegative\":false,\"ac_max\":1,\"per_min\":201904,\"per_max\":201904}'}
# res = requests.request("POST", url, data=pyload, headers=headers)


# with open('aaa.xls','wb') as fp:
#     fp.write(res.content)

    # Case9: #用例1
    #     -
    #         Desc: 查询指定流水号储值记录详情
    #     -
    #         Desc: 查询指定流水号储值记录详情
    #         Url: /charge/detailbybiz
    #         Method: POST
    #         Headers:
    #             content-type: "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW"
    #             cache-control: "no-cache"
    #         Data: 
    #             req: 
    #                 biz_id: 20190524145002007
    #             appid: "dp3lF7bop2e5PTFXwLHTszgv"
    #             sig: 1111
    #             v: 2.0
    #             ts: 123
    #         OutPara: 
    #         Assert:
    #             - eq: [result.errcode, 0]
    #             - bt: [result.res.status]

# import re
# tmp = {'${version}$': 1.0, '${data}$': {'req': {'sid': '1380598237', 'wxcode': '164073966187485312752286'}, 'appid': 'dp0Rm4wNl6A7q6w1QzcZQstr', 'sig': '9c8c96b38d759abe6633c124a5d37225', 'v': '${version}$', 'ts': 1564643536}}

# for key, val in tmp.items():
#     content = re.findall('\$\{.*?}\$', str(val))
#     if content:
#         for klist in content:
#             tmp[key] = eval(str(val).replace(str(klist), str(tmp[klist])))

