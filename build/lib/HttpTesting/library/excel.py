#*_*coding:utf-8*_*
import xlrd as excel
import json
import gc #垃圾回收
import os
from HttpTesting.globalVar import gl



#Excel操作
class Excel(object):

    def __init__(self,excelPath):
        self.excelPath =excelPath

    #创建workbook对象
    def OpenExcel(self,file='file.xls'):
        try:
            ret = excel.open_workbook(filename=self.excelPath)
            #data = excel.open_workbook(filename=self.excelPath)
            return  ret
        except Exception as ex:
            print(ex)

    #获取指定行数据,返回数组
    def getRowData(self,rownum =0):
        try:
            data = self.OpenExcel(self.excelPath)
            table = data.sheet_by_index(0)
        except Exception as ex:
            return ex
        return table.row_values(rownum)

    #根据sheet名获取所有行数据，数组返回
    def getExcelDataByName(self,start_col=4,sheet_name='Sheet1'):
        data = self.OpenExcel(self.excelPath)
        table = data.sheet_by_name(sheet_name)
        RowCount = table.nrows
        ColCount = table.ncols
        ColName = table.row_values(start_col) #获取行，列名行数据，返回数组
        #print ColName
        list=[] #存储行数据，内容字典对象
        #遍历，列名与行数据存储在字典中，并将字典对象存在list中

        for rowNum in range(start_col+1,RowCount):
            #row = table.row_values(rowNum)
            dict = {}

            if table.cell_value(rowNum,0) !='END':
                #print type(table.cell_value(rowNum, 0))
                for i in range(len(ColName)):
                    dict[ColName[i]]=table.cell_value(rowNum,i)
                list.append(dict)
            else:
                break
        gc.collect()
        return list


        #获取字段值，返回数组,做过json处理
    def getData(self,fieldName='Expected Results'):
        result=[]
        exreturn= self.getExcelDataByName(5) #获取所有行数据，返回数组，每个元素一行数据 5字段名所在行
        #print exreturn
        #遍历所有行，批定数据，返回数组
        for rNum in exreturn:
            #print rNum[fieldName]

            #序列化为json串
            jsonStr=json.dumps(rNum,ensure_ascii=False)
            #反序列化为json格式
            jsonData = json.loads(jsonStr)
            resultVal = jsonData[fieldName.decode("utf-8")]
            result.append(resultVal)

            #result.append(rNum[fieldName])
        return result
        #print resultVal

    #获取post数据,做json处理,返回字典类型“name=xzdylyh&password=123455&vercode=df3c”
    def getFormDataDict(self,filedName="Data"):
        formDataList=[]
        formDataArr = self.getData(filedName)
        for i in formDataArr:
            dataList={}
            rVal = i.split('&')
            for j in rVal:
                con = j.split('=')
                dataList[str(con[0])]=con[1]
            formDataList.append(dataList)
        return formDataList





if __name__=="__main__":
    excelPath = os.path.join(gl.dataScenarioPath, '充值并撤销业务场景.xlsx').decode('utf-8')
    print(Excel(excelPath).getExcelDataByName(start_col=4))
    #print os.path.abspath(os.path.dirname(os.getcwd()))+'\data\\testCase.xlsx'
    print(excelPath)