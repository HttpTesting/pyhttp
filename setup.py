from setuptools import setup, find_packages, command
import io

with io.open('README.md', encoding='utf-8') as fp:
    long_description = fp.read()


setup(
    name='HttpTesting', # 应用名
    version='1.1.37', # 版本号
    description="HttpTesting",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="天枢",
    author_email="lengyaohui@163.com",
    url='https://github.com/HttpTesting/HttpTesting',
    license="Apache 2.0",
    python_requires=">=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4",
    packages=find_packages(), # 包括在安装包内的 Python 包
    package_data = {
        'HttpTesting': [
            'config/*.yaml',
            'template/*.yaml',
            ],
        '': ['*.py']
        },
    #依赖包
    install_requires = [
        'pytest',
        'PyYAML==5.1.1',
        'requests',
        'requests-toolbelt',
        'pytest-html',
        'pytest-xdist',
        'pytest-rerunfailures',
        'pytest-repeat',
    ],
    exclude_package_data = { 
        '': ['README.txt'] 
        }, # 排除所有 README.txt
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    #命令行时使用命令
    entry_points={
        'console_scripts': [
            'amt=HttpTesting.main:run_min',
            'AMT=HttpTesting.main:run_min',      
            ]
    },
    #发布到pypi
    # cmdclass={
    #     'upload': UploadCommand
    # }
)