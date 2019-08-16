import re
from HttpTesting.library.http import HttpWebRequest
from HttpTesting.library.assert_case import Ac
from HttpTesting.library.func import FUNC
from HttpTesting.library.parse import (
    parse_args_func, 
    parse_output_parameters, 
    eval_string_parse, 
    parse_string_value,
    parse_cookie_string
    )
from HttpTesting.library.scripts import (print_backgroup_color, print_font_color)


def out_param_parse(oname, param):
    """
    Parse args
    Param:
        oname: object
        param: args
    Usage:
        ret = out_param_parse('result', 'result.res.data[0].id')
    Example:
        Data.tr.id为 Data['tr']['id']
        res.tr.id为 res['tr]['id]
        res[0].tr.id 为res[0]['tr']['id']
        cookie.SESSION 为 Response cookie, cookie['SESSION']
        headers.Content-Type为 headers['Content-Type']
    Return: 
        Example:
        result['res']['data'][0]['id']
    """
    param_list = param.split(".")
    dt = oname
    tmpl = "['{}']"
    m_jion = ''

    # Filter parameters.
    if param_list[0] in ('result', 'res', 'cookie', 'headers', 'header'):
        param_list.pop(0)

    ds = param_list[0]
    # Parse parammeters.
    if ds in param_list:
        for args in param_list:
            if "[" in args:
                a_jion = ''
                for num, val in enumerate(args.split("[")):
                    if num == 0:
                        val = "['{}']".format(val)
                    a_jion = a_jion + val + "["
                a_jion = (a_jion[:-1])
                m_jion = m_jion + a_jion
            else:
                m_jion = m_jion + tmpl.format(args)
    else:
        print("出参错误,格式应为data.2级.3级:{}".format(param))
    return dt + m_jion


def assert_func(res, headers, cookie, result, assertlist):
    """
    Assertion function.
    Args:
        self: Unittest instance object.
        res: Request object.
        headers: Reponse headers object.
        cookie: Reponse cookie object.
        result: Reponse text or reponse json.
    Usage:
        assert_func(self, res, headers, cookie, result, data[i]['Assert'])
    Return:
        There is no return.
    """
    for ass_dit in assertlist:

        for key, value in ass_dit.items():

            ac = getattr(Ac, key)

            for ite, val in enumerate(value):

                if '.' in str(val):
                    value[ite] = eval(out_param_parse(val.split(".")[0], val))
            # Distinguish between two parameters and one parameter by key.
            if value.__len__() == 1:
                assert eval(ac.format(value[0]))
            if value.__len__() == 2:
                assert eval(ac.format(value[0], value[1]))


def param_content_parse(queue, data):
    """
    Pass parameters with DATA information.

    args:
        queue: List the queue.
        data: The DATA content.

    return:
        There is no return.
    """

    for ki, value in enumerate(queue):
        for key, val in value.items():
            filed_list = ['Headers', 'Data', 'Url', 'Assert']
            for filed in filed_list:
                # data参数 正则匹配
                m = str(data[filed])
                content = re.findall('\\${.*?}\\$', m)
                if content:
                    k = ""
                    # 替换数到data中
                    for k in content:
                        if key in content:
                            try:
                                # string replace diff
                                if isinstance(val, str):
                                    m = m.replace(str(k), str(val))
                                else:
                                    m = m.replace("'{}'".format(k), str(val)).replace('"{}"'.format(k), str(val))    
                                m = eval(m)
                            except Exception:
                                m = m.replace("'{}'".format(k), str(val)).replace('"{}"'.format(k), str(val))                                  
                        data[filed] = m
                        break  # break

def user_params_variables(data):
    """
        User parameterized execution.

        Args:
            data:
            [
                {
                    "Desc": "接口用例详细描述",
                    "PARAM_VAR":{
                        "sig": [1,2]
                    },
                },
                {   
                    "Desc": "接口名称1",
                    "Url": "/send/code",
                    "Method": "POST",
                    "Headers":{},
                    "Data":         
                        {
                            "appid": "dp1svA1gkNt8cQMkoIv7HmD1",
                            "req": {
                                "cno": "1623770534820512"
                            },
                            "sig": "${sig}$",
                            "ts": 123,
                            "v": 2.0
                        },
                    "OutPara": None,
                    "Assert": [],

                }

            ]

        Usage:
            user_params_variables(data) 

        After:
            data:
            [
                {
                    "Desc": "接口用例详细描述",
                    "PARAM_VAR":{
                        "sig": [1,2]
                    },
                },
                {   
                    "Desc": "接口名称1_2",
                    "Url": "/send/code",
                    "Method": "POST",
                    "Headers":{},
                    "Data":                 
                        {
                            "appid": "dp1svA1gkNt8cQMkoIv7HmD1",
                            "req": {
                                "cno": "1623770534820512"
                            },
                            "sig": "2",
                            "ts": 123,
                            "v": 2.0
                        },
                    "OutPara": None,
                    "Assert": [],

                },
                {
                    "Desc": "接口名称1_1",
                    "Url": "/send/code",
                    "Method": "POST",
                    "Headers":{},
                    "Data":
                        {
                            "appid": "dp1svA1gkNt8cQMkoIv7HmD1",
                            "req": {
                                "cno": "1623770534820512"
                            },
                            "sig": "1",
                            "ts": 123,
                            "v": 2.0
                        },
                    "OutPara": None,
                    "Assert": [],

                }
            ]
        Returns:
            There is no return.
    """
    if 'PARAM_VAR' in data[0].keys():
        params_dict = data[0]['PARAM_VAR']
        if params_dict:
            for key, value in params_dict.items():
                # 取到参数${key}$，到其它case中遍历，并扩充case
                for _num, val_dict in enumerate(data):
                    if _num == 0:
                        continue
                    content = val_dict
                    init_desc = val_dict['Desc']
                    # 如果${key}$变量在Data中，说明要进行参数化。
                    var_name = "${%s}$" % str(key)
                    if var_name in str(content):
                        # 遍历参数化，增加case
                        params_len = len(params_dict[str(key)])
                        for _iter, val in enumerate(params_dict[str(key)]):
                            # 更改Desc描述，给加个序号
                            content['Desc'] = '{}_{}'.format(content['Desc'], _iter + 1)

                            # 最后一个参数化后，将原来${sig}$替换掉
                            if isinstance(val, str):
                                tmp_val = str(content).replace(str(var_name), str(val))
                            else:
                                tmp_val = str(content).replace("'{}'".format(var_name), str(val)).replace('"{}"'.format(var_name), str(val))
                            if val != params_len:
                                data.append(eval(tmp_val))
                            else:
                                data[_num] = eval(tmp_val)
                            # 恢复最初描述
                            content['Desc'] = init_desc


def user_custom_variables(queue, args, data):
    """
    Handles custom variables in USER_VAR

    args:
        queue: variables queue
        args: User variables
        data: user variables value

    return:
        There is no return.
    """
    # User-defined variables.
    if 'USER_VAR' in data.keys():
        for key, value in data['USER_VAR'].items():
            if "${" in str(value):
                content = re.findall('\$\{.*?}\$', str(value))
                for ilist in content:
                    if str(ilist) in args.keys():
                        va = args[str(ilist)]
                        if isinstance(value, str):
                            value = str(value).replace(str(ilist), str(va))
                        else:
                            value = str(value).replace("'{}'".format(ilist), str(va)).replace('"{}"'.format(ilist), str(va))

            if '%{' in str(value):
                temp = parse_args_func(FUNC, value)
            else:
                temp = value

            args['${%s}$' % key] = temp
        queue.append(args)

        var_dict = queue[0]

        # Handles custom variables in USER_VAR
        for key, val in var_dict.items():
            content = re.findall('\$\{.*?}\$', str(val))
            if content:
                for klist in content:
                    var_dict[key] = eval(str(val).replace(str(klist), str(var_dict[klist])))


def req_headers_default(data, index):
    """
    Specify the default request header.
    Args:
        data: [
            {"Desc": 'xxxx', "REQ_HEADER": {"content-type": 'application/json'}},
            {"Desc": 'xxxx', 'Url': 'ccc', "Assert":[], "Method": "POST", "Data": 'xxx', "OutPara": "xxxx"}
            {"Desc": 'xxxx', 'Url': 'ccc', "Assert":[], "Method": "POST", "Data": 'xxx', "OutPara": "xxxx"}
        ]
        index:
            data[index]
    Usage:
        req_headers_default(data)
    Return:
        There is no return.
    """
    if 'REQ_HEADER' in data[0].keys():
        headers_default = data[0]['REQ_HEADER']
        if 'Headers' in data[index].keys():
            if not data[index]['Headers']:
                data[index]['Headers'] = headers_default
        else:
            data[index]['Headers'] = headers_default
    else:
        # No request header is specified.
        pass


def exec_test_case(data):
    """
    Execute pytest test framework.
    Args:
        data: [[data]]
    Usage:
        exec_test_case(data)
    Return:
        There is no.
    """
    # Parameter storage queue.
    queue_list = []
    # To store variables.
    args_dict = {}
    # HTTP request instance.
    req = HttpWebRequest()

    # Through the case.
    for i, _ in enumerate(data):
        if i == 0:
            # User parameterized execution
            user_params_variables(data)

            # Handles custom variables in USER_VAR
            user_custom_variables(queue_list, args_dict, data[0])
            continue

        res = None
        # Request header default value.
        req_headers_default(data, i)

        # Pass parameters with DATA information.
        param_content_parse(queue_list, data[i])

        # Parse the custom functions in the following fields
        for key, value in data[i].items():
            data[i][key] = parse_args_func(FUNC, data[i][key])

        # Send http request.
        res, headers, cookie, result = send_http_request(req, data[i])
        # Assertions parsing
        assert_func(res, headers, cookie, result, data[i]['Assert'])

        # Output parameters are written to the queue
        param_to_queue(queue_list, data[i], args_dict, res, headers, cookie, result)


def send_http_request(req, data):
    """
    Handling HTTP is fun.
    """
    # Handling HTTP is fun.
    method = str(data['Method']).upper()
    if ('GET' in method) or (r'DELETE' in method):
        res, headers, cookie, result = req.get(
            params=data['Data'],
            desc=data['Desc'],
            gurl=data['Url'],
            headers=data['Headers'],
            method=method
            )
    elif ('POST' in method) or ('PUT' in method):
        res, headers, cookie, result = req.post(
            data=data['Data'],
            desc=data['Desc'],
            gurl=data['Url'],
            headers=data['Headers'],
            method=method
            )
    else:
        raise "Error request method: {}".format(data['Method'])    

    return (res, headers, cookie, result)


def param_to_queue(queue, dt, param_dict, res, headers, cookie, result):
    """
    Parse output parameters are written to the queue.

    args:
        queue: List the queue.
        data: The DATA content
        param_dict: Temporary storage queue parameters.
        res: Request object.
        headers: Repsonse headers.
        cookie: Repsonse cookies.
        result: Repsonse content JSON or text.

    usage:
        param_to_queue(outParaQueue, data[i], oPara, res, headers, cookie, result)

    return:
        There is no return.
    """
    # 出参写入队列
    if dt['OutPara']:
        header = eval_string_parse(dt['Headers'])
        data = eval_string_parse(dt['Data'])

        # 组参数
        for key, value in dt['OutPara'].items():
            # Parse output string. e.g ${var}$. write queue.
            output_string = parse_output_parameters(value)

            # Parse cookie object as strings.
            cookie_string = parse_cookie_string(cookie, output_string)

            # custom variables format ${var}$.
            if "${" not in key:
                key = "${%s}$" % key

            if not cookie_string:
                try:
                    ret = eval(output_string)
                except (TypeError, ValueError, NameError, SyntaxError):
                    ret = output_string
            else:
                ret = cookie_string
            param_dict[key] = ret

        queue.append(param_dict)
