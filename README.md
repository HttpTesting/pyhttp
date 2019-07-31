# HttpTesting

[![Build status](https://travis-ci.org/atotto/travisci-golang-example.png)](https://travis-ci.org/atotto/travisci-golang-example)



HttpTesting 是HTTP(S) 协议测试框架，通过YAML来编写测试用例；支持通过pip直接从PyPi安装，支持命令行运行代码，不固定结构，通过命令生成脚手架。

## 版本信息

|序号|版本号|描述|
|:---|:---|:---| 
|1|v1.0|使用unittest框架|
|2|v1.1|使用pytest框架|




## 快速开始

### python虚拟环境virtualenv使用

- 安装虚拟环境: pip install virtualenv

- 创建虚拟环境: virtualenv  demo_env

- 命令行模式切换到虚拟环境Script目录: /../scripts/

- 激活虚拟环境: activate.bat 

### HttpTesting安装


#### pip在线安装

- pip install HttpTesting==1.0.26

#### 下载whl文件进行安装

- pip install HttpTesting-1.0.40-py3-none-any.whl 


#### 更新HttpTesting包

已安装HttpTesting包,通过pip命令进行更新

- pip list  查看HttpTesting安装包版本信息

- pip install --upgrade HttpTesting

- pip install --upgrade HttpTesting==1.0.26



### amt 或 AMT命令

|序号|命令参数|描述|
|:---|:---|:---|  
|1|amt -config set|此命令用来设置config.yaml基本配置|
|2|amt -file template.yaml|执行YAML用例，支持绝对或相对路径|
|3|amt -dir testcase|批量执行testcase目录下的YAML用例，支持绝对路径或相对路径|
|4|amt -startproject demo|生成脚手架demo目录,以及用例模版|
|5|amt -har httphar.har|根据抓包工具导出的http har文件，生成测试用例YAML|
|6|amt -convert demo.yaml|转换数据为HttpTesting测试用例|


#### 基本配置

- URL设置

- 钉钉机器人设置

- 测试报告设置

- EMAIL邮箱设置


#### 用例执行

- YAML执行: amt -file template.yaml

- YAML批量执行: amt -dir testcase



####  脚手架生成

- 脚手架功能,是生成一个测试用例模版.



#### HAR

har命令来解析, Charles抓包工具导出的http .har请求文件, 自动生成HttpTesting用例格式.





## 用例编写


### 用例模型

>TESTCASE{

>>'case1':['description',{},{}],  #场景模式每个{}一个接口

>>'case2':['description',{}],     #单接口模式

>}


### YAML用例格式  


    TESTCASE:
	    #Case1由两个请求组成的场景
        Case1:
	        -
	            Desc: xxxx业务场景(登录->编辑)
	        -
			    Desc: 登录接口
	            Url: /login/login
	            Method: GET
	            Headers:
	                content-type: "application/json"
	                cache-control: "no-cache"
	            Data:
	                name: "test"
	                pass: "test123"
	            OutPara: 
	                "$H_token$": result.data
					"${content_type}$": header.content-type
					"${name}$": Data.name 
					"${pass}$": Data.pass
	            Assert:
	                - eq: [result.status, 'success']
	        -
			    Desc: 编辑接口
	            Url: /user/edit
	            Method: GET
	            Headers:
	                content-type: "${content_type}$"   
	                cache-control: "no-cache"
					token: "$H_token$"
	            Data:
	                name: "${name}$"
	                pass: "${pass}$"
	            OutPara: 
	                "$H_token$": result.data
	            Assert:
	                - ai: ['success', result.status]
					- eq: ['result.status', '修改成功']


    TESTCASE:
	    #同一接口,不同参数,扩充为多个CASE
		Case1:
		    -
			    Desc: 登录接口-正常登录功能
            -
			    Desc: 登录接口
	            Url: /login/login
	            Method: GET
	            Headers:
	                content-type: "application/json"
	                cache-control: "no-cache"
	            Data:
	                name: "test"
	                pass: "test123"
	            OutPara: 
	                "$H_cookie$": cookie.SESSION
	            Assert:
	                - eq: [result.status, 'success']
		Case2:
		    -
			    Desc: 登录接口-错误密码
            -
			    Desc: 登录接口
	            Url: /login/login
	            Method: GET
	            Headers:
	                content-type: "application/json"
	                cache-control: "no-cache"
	            Data:
	                name: "test"
	                pass: "test123"
	            OutPara:
	                "$H_cookie$": cookie.SESSION 
	            Assert:
	                - eq: [result.status, 'error']

### 参数说明

- "${H_token}$": 为参数变量,可以头信息里与Data数据里进行使用
- "%{md5('aaaa')}%": 为函数原型,具体支持函数下方表格可见.

### 自定义变量

变量作用域为当前CASE.


### 示例(部分代码片断)

    TESTCASE: 
        Case1:
            - 
                Desc: 接口详细描述
                USER_VAR:
                    token:  xxxxxxxx
            -
                Url: /xxxx/xxxx
                Method: POST
                Headers: {}
                Data:
                OutPara:
                Assert: []


	
- 以上通过USER_VAR字典对象来定义变量, key为变量名, value为变量值; 使用方法: ${token}$

- 无需定义变量, USER_VAR字段在用例中,可以省略.

#### OutPara字段变量使用

OutPara字段用来做公共变量,供其它接口使用,默认为""; 

-  示例: "${H_token}$": result.data 是请求结果，返回的嵌套级别
-  OutPara为dict类型,可以做多个公共变量.


#### Assert断言

Assert字段默认为[].

|序号|断言方法|断言描述|
|:---|:---|:---|
|1|eq: [a, b]|判断 a与b相等,否则fail|
|2|nq: [a, b]|判断 a与b不相等,否则fail|
|3|al: [a, b]|判断 a is b 相当于id(a) == id(b),否则fail|
|4|at: [a, b]|判断 a is not b 相当于id(a) != id(b)|
|5|ai: [a, b]|判断 a in b ,否则fail|
|6|ani: [a, b]|判断 a in not b,否则fail|
|7|ais: [a, b]|判断 isinstance(a, b) True|
|8|anis: [a, b]|判断 isinstance(a, b) False|
|9|ln: [a]|判断 a is None,否则fail|
|10|lnn: [a]|判断 a is not none|
|11|bt: [a]|判断 a 为True|
|12|bf: [a]|判断 a 为False|


#### 内置函数及扩展

使用原型(带参数与不带参数)

- "%{md5('aaaa')}%" 或 "%{timestamp()}%"



|函数名|参数|说明|
|:---|:---|:---|
|md5|txt字符串|生成md5字符串示例: cbfbf4ea6d7c8032584dcf0defa10276|
|timestamp|-|秒级时间戳示例: 1563183829|
|uuid1|-|生成唯一id,uuid1示例:ebcd6df8a77611e99bb588b111064583|
|datetimestr|-|生成日期时间串,示例:2019-07-16 10:50:16|
|mstimestamp|-|毫秒级时间戳,20位|

- 其它后续添加


## 常用对象(通常做参数变量时使用)
- res: 请求Response对象
- result: res.json 或 res.text
- cookie: res.cookie 响应cookie字典对象;  当做为参数时如果cookie.SESSION这样的写法代表取cookie中的SESSION对象. 如果只写cookie,会解析成"SESSION=xxxxxxx; NAME=xxxxxx"
- headers: res.headers 响应头字典对象
- header: header.content-type 请求头对象


## 用例执行
- 1、生成脚手架
- 2、编写脚手架中testcase下YAML模版用例
- 3、切换到testcase目录
- 4、amt -dir testcase 自动运行testcase下YAML用例
- 5、自动生成测试报告Html


##  框架基本配置
- 1、通过命令打开框架config.yaml
- 2、amt -config set
- 3、修改基本配置，并保存




## 代码打包与上传PyPi

  

### 通过setuptools工具进行框架打包,需要编写setup.py



- 打包：python3 setup.py bdist_wheel

  

- 上传PyP: twine upload dist/*

  