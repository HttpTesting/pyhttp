import yaml
from yaml.parser import ParserError


class CONFIG:
    def __init__(self):
        pass

    def get_yaml_field(self, path):
        """
        Gets the YAML configuration file content.
        param:
            path: YAML file path.
        usage:
            ret_dict = get_yaml_field(path)
        return:
            ret_dict is all of YAML's content.
        """
        try:
            with open(path, 'rb') as fp:
                cont = fp.read()

            ret = yaml.load(cont, Loader=yaml.FullLoader)
            return ret
        except ParserError as ex:
            raise Exception('YAML格式出错,错误信息: {}'.format(ex))

    def write_yaml(self, path, data):
        """
        Write YAML file content.
        param:
            path: YAML file content.
            data: Dictionary type data.
        usage:
            write_yaml(r'd:\template.yaml', data)
        return:
            There is no.
        """
        with open(path, 'wb') as fp:
            yaml.dump(data, fp)

        try:
            with open(path, 'rb') as fp:
                cont = fp.read()

            ret = yaml.load(cont, Loader=yaml.FullLoader)
            return ret
        except ParserError as ex:
            raise Exception('YAML格式出错,错误信息: {}'.format(ex))


conf = CONFIG()

