import re
from httptesting.library.func import *
from httptesting.library.scripts import print_backgroup_color


def parse_output_parameters(params):
    """
    Parse the test case output parameters.

    Args:
        params: res[0].tr.id
    Example:
        ret = parse_output_parameters('result.res.data[0].id')
        e.g. Data.tr.id => Data['tr']['id']
             res.tr.id => res['tr]['id]
             res[0].tr.id => res[0]['tr']['id']
             cookie.SESSION => cookie['SESSION']
             headers.Content-Type => headers['Content-Type']
    """
    param_list = params.split(".")

    # Interception object.
    param_obj = param_list[0]
    param_list.pop(0)

    # Template string.
    template = "['{}']"
    parse_string = ''
    # Parse the test case output parameters.
    for args in param_list:
        if "[" in args:
            left_string = ''
            for num, val in enumerate(args.split("[")):
                if num == 0:
                    val = "['{}']".format(val)
                left_string = left_string + val + "["
            left_string = (left_string[:-1])
            parse_string = parse_string + left_string
        else:
            parse_string = parse_string + template.format(args)
    ret_string = param_obj.lower() + parse_string
    return ret_string


def parse_param_variables(data):
    """
    """
    var_regx_compile = re.compile(r"\${(.*?)}")

    take_list = var_regx_compile.findall(str(data))

    return take_list


def parse_args_func(func_class, data):
    """
    Parse the function variables in the data.

    Args:
        func_class: FUNC  class object.
        data: string.

    Example:
        import re
        from httptesting.library.func import *
        >>> parse_args_func(FUNC, 'md5:%{md5("123")}; timestamp:%{timestamp()}')
        md5:202cb962ac59075b964b07152d234b70; timestamp:1565840163

    Return:
        Replacement data.
    """
    data_bool = False
    if not isinstance(data, str):
        data_bool = True
        data = str(data)

    take = re.findall(r'%{.*?}%', data)

    for val in take:
        func = val.split("%{")[1][:-2]

        func = '{}.{}'.format(func_class.__name__, func)
        ret = eval(func)

        # print_backgroup_color(ret, color='green')
        data = data.replace(val, str(ret))

    if data_bool:
        data = eval_string_parse(data)
    return data


def replace_list_batch_string(string, list_string, new):
    """
    Batch replace value in string.

    Args:
        string： The original string。
            e.g.'md5:%{md5("123")}; timestamp:%{timestamp()}'
        list_string: ["%{md5("123")}", '"%{md5(\"123\")}"', '%{md5("123")}']
        new: 202cb962ac59075b964b07152d234b70

    Example:
        >>> val = "%{md5('123')"
        >>> list_string = ["'%{" + val + "}'", '"%{' + val + '}"', '%{' + val + '}']
        >>> data = replace_list_batch_string(data, list_string, ret_func)
    Return:
        string: Replaced string
    """
    for old in list_string:
        string = string.__str__().replace(old.__str__(), new.__str__())
    return string


def eval_string_parse(string):
    """
    Parse the string to native.

    Args:
        string: A string to be parsed.
    Example:
        >>> eval_string_parse("123")
        123 <class 'int'>

        >>> eval_string_parse("12.3")
        12.3 <class 'float'>

        >>> eval_string_parse("{'name': 'yhleng', 'age': 27}")
        {'name': 'yhleng', 'age': 27}  <class 'dict'>

        >>> eval_string_parse("[1,2,3,4,5]")
        [1,2,3,4,5] <class 'list'>
    Return:
        String prototype.
    """
    try:
        ret = eval(string)
    except (TypeError, ValueError, NameError, SyntaxError):
        ret = string
    return ret


def parse_string_value(str_value):
    """ 
    Parse string, restore type.

    Example:
        >>> parse_string_value("123") 
        123 <class 'int'>

        >>> parse_string_value("12.3") 
        12.3 <class 'float'>

        >>> parse_string_value("abc") 
        abc <class 'str'>
    """
    try:
        return eval_string_parse(str_value)
    except (ValueError, SyntaxError):
        return str_value


def parse_cookie_string(cookie, cookie_string):
    """
    Parse cookies as strings.

    Args:
        cookie: Response cookie object.
        cookie_string: 
            e.g. "cookie['SESSION']"
            e.g. "cookie"
    """
    queue_val = ''
    if 'cookie' in cookie_string:
        #split cookie
        if '[' in cookie_string:
            # e.g. "cookie['SESSION']" => SESSION
            cookie_key = cookie_string.split("[")[1][1:-2] 

            try:
                cookie_val = eval(cookie_string)
            except (TypeError, ValueError, NameError, SyntaxError):
                cookie_val = cookie_string
            queue_val = '{}={}'.format(cookie_key, cookie_val)
        else:
            temp_list = []
            for ky, vak in cookie.items():
                temp_list.append('{}={}'.format(ky, vak))
            queue_val = '; '.join(temp_list)

    return queue_val


def parse_parameters_variables(queue, data):
    """
    Parse variables.
        e.g. ['Headers', 'Data', 'Url', 'Assert', 'Desc', 'OutPara']

    Args:
        queue: List the queue.
        data: data[index].

    Examples:
        parse_parameters_variables(queue, data)
        e.g.
        Headers:{
            'content-type': 'application/json',
            'token': ${token}$
        }
        =>
        Headers:{
            'content-type': 'application/json',
            'token': '1q2w3e4r5t6y7u8i9o0a2s3d4f5g6h7j8k0l'
        }
    return:
        There is no return.
    """
    # Prepare the parsed list of CASE fields.
    parse_field_list = ['Headers', 'Data', 'Url', 'Assert', 'Desc']

    # regx
    var_regx_compile = re.compile(r"\${.*?}\$")

    # Parses the parameters in the fields separately.
    for _, field in enumerate(parse_field_list):
        # Regular match field.
        take_list = list(set(var_regx_compile.findall(data[field].__str__())))

        # Field to a variable.
        for regx_field in take_list:
            # print_backgroup_color(regx_field, color='green')
            # queue value
            for var_dict in queue:
                # print_backgroup_color(var_dict, color='red')
                try:
                    var_value = var_dict[regx_field]
                    # print_backgroup_color(var_value, color='green')
                    break
                except KeyError:
                    pass

            var_value = parse_string_value(var_value)

            if isinstance(var_value, str) or isinstance(var_value, int):
                # Replace
                data = data.__str__().replace(regx_field, var_value.__str__())
            else:
                data = data.__str__().replace('"{}"'.format(regx_field), var_value.__str__()).replace("'{}'".format(regx_field), var_value.__str__())  

        # Parse the function in the argument.
        data_string = parse_args_func(FUNC, data)

        # source
        data = eval_string_parse(data_string)

    return data


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

if __name__ == "__main__":
    data = {
        "md5": '%{md5("123")}',
        "timestamp": "${var}"
    }
    # ret = parse_args_func(FUNC, data)
    # print(ret)

    # ret = parse_param_variables("aaaa${var}bbbb${okay}")
    # print(ret)
    # e.g. "result.res[0].coupon.coupons[1]" >>> result['res'][0]['coupon']['coupons'][1]
    # Data.tr.id
    # ret = parse_output_parameters("cookie.SESSION")
    # print(ret)

    # queue = [{'${version}$': 1.0, '${data_var}$': "{'req': {'sid': '1380598237', 'wxcode': '164073966187485312752286'}, 'appid': 'dp0Rm4wNl6A7q6w1QzcZQstr', 'sig': '9c8c96b38d759abe6633c124a5d37225', 'v': 1.0, 'ts': 1564643536}"}]
    # data = {'Desc': '扫码校验券', 'Url': '/pos/checkcoupon', 'Method': 'POST', 'Headers': {'content-type': 'multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW', 'cache-control': 'no-cache'}, 'Data': '${data_var}$', 'OutPara': {'token': 'result.errcode'}, 'Assert': [{'eq': ['result.errcode', '30004']}]}
    # parse_parameters_variables(queue, data)

    # data = {'Desc': '给指定用户发送验证码(发送1->发送2)', 'REQ_HEADER': {'content-type': 'multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW', 'cache-control': 'no-cache'}, 'USER_VAR': {'req': {'cno': 1802326704347962}, 'appid': 'dp3Go73mm5jUiuQaWDe4W', 'v': 2.0, 'ts': 1564967996, 'appkey': '3ea8bfbf0574b89ae6b9e4717a34f53f', 'sig_dict': {'data': '${req}$', 'appid': '${appid}$', 'ts': '${ts}$', 'v': '${v}$', 'appkey': '${appkey}$'}}}
    # user_custom_variables([], {}, data)

    # FUNC.sign({'data': {'cno': 1802326704347962}, 'appid': 'dp3Go73mm5jUiuQaWDe4W', 'ts': '1564967996', 'v': '2.0', 'appkey': '3ea8bfbf0574b89ae6b9e4717a34f53f'})


