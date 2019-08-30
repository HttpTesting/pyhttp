import io
import json
import os
import collections
import yaml


class ConvertHarToYAML:

    @classmethod
    def from_har_to_dict(cls, harpath):
        """
        Convert from Charles HAR to a dict object.
        :Param harpath: HAR file path.
        usage:
            dictReq = from_har_to_dict(harpath)
        return: dictReq Har's dict object.
        """
        if os.path.exists(harpath):

            with io.open(harpath, 'r+', encoding='utf-8-sig') as fp:
                rjson = fp.read()
                content_dict = json.loads(rjson)
                return content_dict['log']['entries']
        else:
            raise Exception("HAR file path error.{}".format(harpath))

    @classmethod
    def convert_to_list(cls, harpath):
        """
        convert HAR content to list
        :param harpath: HAR file path.
        usage:
            ret_list = convert_to_list(harpath)
        return:
            [] request list.
        """
        ret = cls.from_har_to_dict(harpath)

        req_dict = []
        for req in ret:
            req_dict.append(req['request'])

        return req_dict

    @classmethod
    def parse_headers_dict(cls, header):
        """
        parse Headers information.
        """
        try:
            headers = {}
            for i_dict in header:
                headers[i_dict['name']] = i_dict['value']
            # print(headers)
        except (KeyError, TypeError) as ex:
            raise ex
        return headers

    @classmethod
    def parse_post_data(cls, postData):
        """
        parse POST Data.
        :param postData: HAR post data.
        usage:
        return:
            dict data.
        """
        if isinstance(postData, dict):
            if 'params' in postData:
                data = postData['params']
            elif 'text' in postData:
                data = eval(postData['text'])
            else:
                data = postData
        else:
            data = postData
        dt = {}
        try:
            for i_list in data:
                if i_list.__len__() == 2:
                    dt[i_list['name']] = i_list['value']
                else:
                    dt = data
        except (KeyError, TypeError) as ex:
            raise ex
        return dt

    @classmethod
    def ordered_dump(cls, data, stream=None, Dumper=yaml.Dumper, **kwds):
        """
        Convert the unordered dictionary to ordered and write yaml.
        param:
            data:
            stream:
            allow_unicode:
            default_flow_style:
            indent:
        return: There is no.
        """
        class OrderedDumper(Dumper):
            pass

        def _dict_representer(dumper, data):
            return dumper.represent_mapping(
                yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                data.items())
        OrderedDumper.add_representer(collections.OrderedDict, _dict_representer)
        return yaml.dump(data, stream, OrderedDumper, **kwds)

    @classmethod
    def write_case_to_yaml(cls, yampath, contentDict):
        """
        Write the test case to yaml.
        param:
            yampath: Yaml file path.
        return:
            There is no.
        """
        yamFile = os.path.join(yampath, 'har_testcase.yaml')
        with io.open(yamFile, 'w', encoding='utf-8') as fp:
            cls.ordered_dump(
                contentDict,
                fp,
                Dumper=yaml.SafeDumper,
                allow_unicode=True,
                default_flow_style=False,
                indent=4
            )

    @classmethod
    def convert_har_to_ht(cls, harfile):
        """
        Convert har files to httptesting the test cases.
        param:
            harfile: HAR file full path.
        return:
            {} dict case.
        """

        temp_dict = {}
        temp_dict['TEST_CASE'] = collections.OrderedDict()

        ret = cls.convert_to_list(harfile)

        for n, val in enumerate(ret):
            case = 'case{}'.format(n)
            temp_dict['TEST_CASE'][case] = []
            temp_dict['TEST_CASE'][case].append({'Desc': '请添加接口测试描述'})

            if val['queryString']:
                data = val['queryString']
            elif val['postData']:
                data = val['postData']
            else:
                data = ""

            url = val['url']
            if '?' in val['url']:
                url = val['url'].split('?')[0]

            temp_dict['TEST_CASE'][case].append(collections.OrderedDict({
                'Desc': '示例:接口名称/user/lock',
                'Url': url,
                'Method': val['method'],
                'Headers': cls.parse_headers_dict(val['headers']),
                'Data': cls.parse_post_data(data),
                'OutPara': "",
                'Assert': []
            }))
        # print(temp_dict)
        return temp_dict
