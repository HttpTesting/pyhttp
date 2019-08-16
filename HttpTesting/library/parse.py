import re
from HttpTesting.library.func import *


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
        from HttpTesting.library.func import *
        >>> parse_args_func(FUNC, 'md5:%{md5("123")}; timestamp:%{timestamp()}')
        md5:202cb962ac59075b964b07152d234b70; timestamp:1565840163

    Return:
        Replacement data.
    """
    data_bool = False
    if not isinstance(data, str):
        data_bool = True
        data = str(data)

    take = re.findall('%{.*?}%', data)

    for val in take:
        func = val.split("%{")[1][:-2]

        func = '{}.{}'.format(func_class.__name__, func)
        ret = eval_string_parse(func)

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
    ret = parse_output_parameters("cookie.SESSION")
    print(ret)
