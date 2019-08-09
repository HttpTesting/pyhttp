import os
import shutil
from HttpTesting.globalVar import gl


def create_falsework(path):
    """
        创建脚手架
        :目录
            testcase   #用例文件夹
                template.yaml  #用例文件
        :命令
            amt --files= ./template.yaml  #指定单个case执行
            amt --dirs= ./testcase  #执行该目录下所有case
        :param path: 脚手架根目录
        :invoke
            from HttpTesting.library.falsework import create_falsework
            create_falsework(path)
        :return :
    """
    # 创建结构
    if not os.path.exists(path):

        # 处理测试用例结构及模版
        dirs = os.path.join(path, 'testcase')
        try:
            os.makedirs(dirs)

            template = os.path.join(gl.testCasePath, 'template.yaml')
            dst = os.path.join(dirs, 'template.yaml')
            if os.path.exists(template):
                shutil.copyfile(template, dst)
            else:
                raise Exception("template.yaml模版未找到。")

        except Exception:
            shutil.rmtree(dirs)
    else:
        raise Exception("项目结构已存在")


if __name__ == "__main__":
    dirpath = r'D:\test_project\amtproject'
    create_falsework(dirpath)
