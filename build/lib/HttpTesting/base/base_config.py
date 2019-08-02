import os
from HttpTesting.globalVar import gl
from HttpTesting.library import scripts


class BaseConfig:

    @staticmethod
    def base_url():
        config_path = os.path.join(gl.configPath, 'config.yaml')
        url = scripts.get_yaml_field(config_path)
        return url['BASE_URL']


# if __name__=="__main__":
#     print BaseConfig.base_url