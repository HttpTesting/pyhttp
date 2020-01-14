import re
from httptesting.library.http import req
from httptesting.library.assert_case import Ac
from httptesting.library.func import FUNC
from httptesting.library.parse import (
    parse_args_func,
    parse_output_parameters,
    eval_string_parse,
    parse_string_value,
    parse_cookie_string,
    parse_parameters_variables
    )
from httptesting.library.scripts import (print_backgroup_color, print_font_color)


def assert_test_case(res, headers, cookie, result, assert_list, data):
    """
    Assertion function.
    Args:
        self: Unittest instance object.
        res: Request object.
        headers: Reponse headers object.
        cookie: Reponse cookie object.
        result: Reponse text or reponse json.
    Usage:
        assert_test_case(self, res, headers, cookie, result, data[index]['Assert'])
    Return:
        There is no return.
    """
    for ass_dict in assert_list:

        for key, value in ass_dict.items():

            ac = getattr(Ac, key)

            for ite, val in enumerate(value):

                if '.' in str(val):

                    value[ite] = eval(parse_output_parameters(val))

            # Distinguish between two parameters and one parameter by key.
            if value[0] == 'result':
                value[0] = result.__str__().replace("'", '"')
            try:
                if value.__len__() == 1:
                    ass_res = ac.format(eval_string_parse(value[0]))
                    assert eval(ass_res), ass_res
                else:
                    if value[1] == 'result':
                        value[1] = result.__str__().replace("'", '"')

                    ass_res = ac.format(value[0], value[1])
                    assert eval(ass_res), ass_res

            except (IndexError, KeyError, TypeError) as ex:
                raise Exception("预期结果的字典Key或列表索引超限或预期结果类型错误.{}".format(ex))


def user_custom_variables(queue, args, data):
    """
    Handles custom variables in USER_VAR

    args:
        queue: variables queue
        args: User variables
        data: user variables value. data[0]

    return:
        There is no return.
    """
    var_regx_compile = re.compile(r"\${.*?}\$")

    # User-defined variables.
    if 'USER_VAR' in data.keys():

        # Traverse user variables.
        for key, value in data['USER_VAR'].items():
            temp = ''
            if "${" in str(value):
                # Match regular expression.
                content = var_regx_compile.findall(value.__str__())
                # # Parse replace variables.
                for ilist in content:
                    if str(ilist) in args.keys():
                        va = args[str(ilist)]

                        value_var = eval_string_parse(va)
                        
                        if isinstance(value_var, str):
                            value = str(value).replace(str(ilist), str(va))
                        else:
                            value = str(value).replace(
                                "'{}'".format(ilist), va.__str__()
                                ).replace('"{}"'.format(ilist), str(va))

            if '%{' in str(value):
                temp = parse_args_func(FUNC, value)
            else:
                temp = value

            args['${%s}$' % key] = temp

        queue.append(args)

        var_dict = queue[0]

        # Handles custom variables in USER_VAR
        for key, val in var_dict.items():
            # Match regular expression.
            content = var_regx_compile.findall(val.__str__())

            # Parse replace variables.
            for klist in content:
                var_dict[key] = eval(str(val).replace(klist.__str__(), str(var_dict[klist])))


def req_headers_default(data, index):
    """
    Specify the default request header.
    Args:
        data: [
            {"Desc": 'xxxx', "REQ_HEADER": {"content-type": 'application/json'}},
            {"Desc": 'xxxx', 'Url': 'ccc', "Assert":[], "Method": "POST", "Data": 'xxx', "OutPara": "xxxx"}
            ]
        index:
            data[index]
    Usage:
        req_headers_default(data)
    Return:
        There is no return.
    """
    # Determines whether to set the request default value.
    if 'REQ_HEADER' in data[0].keys():

        headers_default = data[0]['REQ_HEADER']

        # Use itself or request header default; Itself is preferred
        if 'Headers' in data[index].keys():
            # The request header itself is not set,
            # and the request header default is adopted.
            if not data[index]['Headers']:

                data[index]['Headers'] = headers_default

        else:
            data[index]['Headers'] = headers_default
    else:
        # No request header is specified.
        pass


def parse_data_point(dt, data):
    regx_compile = re.compile(r"(data\.\w+)")

    data_point = regx_compile.findall(dt.__str__())

    for i in data_point:
        tmp = parse_output_parameters(i)

        var_value = eval(tmp)

        if isinstance(var_value, str) or isinstance(var_value, int):
            # Replace
            dt = dt.__str__().replace(i, eval(tmp).__str__())
        else:
            dt = dt.__str__().replace('"{}"'.format(i), eval(tmp).__str__()).replace("'{}'".format(i), eval(tmp).__str__())            

        dt = eval(dt)

    return dt


def parse_data_to_uservar(args_dict, queue_list, dt, data):
    """
    Parse outparam data point to user variable.
    """
    # # 推送outparam  data.到用户自定义变量
    regx_compile = re.compile(r"(data\.\w+[.\w]+[^,'\"])")

    if 'OutPara' in dt.keys():
        conditions = dt["OutPara"]
        regx_data_point = regx_compile.findall(conditions.__str__())
        if conditions and regx_data_point:
            for key, val in conditions.items():
                for point in regx_data_point:
                    key_str = r'${%s}$' % key
                    a = parse_output_parameters(point)
                    args_dict[key_str] = eval(a)
            queue_list.append(args_dict)


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

    # Through the case.
    for index, _ in enumerate(data):
        if index == 0:
            # Handles custom variables in USER_VAR
            user_custom_variables(queue_list, args_dict, data[0])
            continue

        # Push outparam  "data.sig" to user custom variable.
        parse_data_to_uservar(args_dict, queue_list, data[index], data[index]['Data'])

        # Parse to replace DATA in data. DATA.
        for key, value in data[index].items():
            # Parse data.appid
            if key.upper() == 'ASSERT':
                if '.data.' not in str(value):
                    data[index][key] = parse_data_point(value, data[index]['Data'])
            else:
                data[index][key] = parse_data_point(value, data[index]['Data'])

        res = None
        # Request header default value.
        req_headers_default(data, index)

        # Parse parameter variable and function
        data[index] = parse_parameters_variables(queue_list, data[index])

        # Parse the custom functions in the following fields
        for key, value in data[index].items():
            # Parse function
            data[index][key] = parse_args_func(FUNC, data[index][key])

        # Skip interface
        if 'TRUE' in data[index].get("Skip", "NotExistSkip").__str__():
            continue

        # Send http request.
        res, headers, cookie, result = send_http_request(req, data[index])
        # Assertions parsing
        assert_test_case(res, headers, cookie, result, data[index]['Assert'], data[index]['Data'])

        # Output parameters are written to the queue
        param_to_queue(queue_list, data[index], args_dict, res, headers, cookie, result)


def send_http_request(req, data):
    """
    Handling HTTP is fun.
    """
    # print_backgroup_color(data, color='red')
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
    try:
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
    except KeyError as ex:
        raise Exception(ex)
