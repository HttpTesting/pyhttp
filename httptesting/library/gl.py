
import os

"""
全局声明
"""
global globalPath  # global包路径
global configPath  # config包路径
global dataPath  # Data路径
global dataScenarioPath  # 场景路径
global tcodePath  # t-code路径
global reportPath  # 报告路径
global reportFile  # 报告文件
global configFile  # config.yaml文件
global debugFile  # debug文件
global webPath  # web路径
global templatesPath  # web模版路径
global templatesReportPath  # 模版测试报告发布路径
global exeConfigFile  # exeConfig.yaml配置
global testCasePath  # 测试用例文件夹
global loadcasePath

# ###############################跨模块调用传参##########################
# param: 调用模块需要先调用_init()进行dict初始化


def _init():  # 初始化
    global _global_dict
    _global_dict = {}


def set_value(key, value):
    """ 定义一个全局变量 """
    _global_dict[key] = value


def get_value(key, def_value=None):
    """获得一个全局变量,不存在则返回默认值"""
    try:
        return _global_dict[key]
    except KeyError:
        return def_value
########################################################################

# 初始化父路径


PATH = lambda p: os.path.abspath(os.path.join(os.path.dirname(__file__), p))

# ##################################全局变量赋值##########################
globalPath = os.path.abspath(os.path.dirname(__file__))
configPath = os.path.join(os.path.dirname(globalPath), 'config')
dataPath = os.path.join(PATH(os.path.dirname(globalPath)), 'data')
dataScenarioPath = os.path.join(dataPath, 'Scenario')
tcodePath = os.path.join(dataPath, 'TCode')
reportPath = os.path.join(os.path.dirname(globalPath), 'report')
configFile = os.path.join(configPath, 'config.yaml')
debugFile = os.path.join(reportPath, 'logging.log')
webPath = os.path.join(os.path.dirname(globalPath), 'web')
templatesPath = os.path.join(webPath, 'templates')
templatesReportPath = os.path.join(templatesPath, 'report')
reportFile = os.path.join(reportPath, "Report.html")
exeConfigFile = os.path.join(configPath, "exeConfig.yaml")
testCasePath = os.path.join(PATH(os.path.dirname(globalPath)), 'template')
loadcasePath = os.path.join(os.path.dirname(globalPath), 'case')
##########################################################################

if __name__ == "__main__":
    print(templatesPath)
    print(templatesReportPath)
    print(globalPath)
    print(configPath)
    print(dataPath)
    print(dataScenarioPath)
    print(tcodePath)
    print(reportPath)
    print(configFile)
    print(reportFile)
    print(exeConfigFile)
    print(testCasePath)