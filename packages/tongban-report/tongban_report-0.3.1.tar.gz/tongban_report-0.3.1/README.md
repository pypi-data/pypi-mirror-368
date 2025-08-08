### tongban_report

### 通办信息报告生成工具

### 目录
- [安装](#安装)
- [模板](#模板)
- [使用](#使用)
- [打包&发布](#打包&发布)

### 安装
```commandline
pip install tongban_report

pip install --upgrade tongban_report
```

### 模板
> 注意: 事先需要准备好以下工作目录和相关文件
```commandline
| - workdir                     # 工作目录
    | - data.xlsx               # 测试数据
    | - functional.docx         # 功能测试报告模板
    | - safety.docx             # 安全测试报告模板
    | - assets                  # 图表目录
        | - summary_blank.png   # Jmeter聚合报告(空)
        | - threads_blank.png   # Jmeter线程图表(空)
```
以上文件都可以参考本项目 sample 目录中的样板文件

### 使用
```commandline
tongban_report [-h] -d DATA [-f FUNC] [-s SAFE]
options:
  -h, --help       show this help message and exit
  -d, --data DATA  数据来源Excel文件的路径(必填)
  -f, --func FUNC  功能测试报告模板
  -s, --safe SAFE  安全测试报告模板
```

- [x] 给定参数[-f]会生成功能测试报告;
- [x] 给定参数[-s]会生成安全测试报告;
- [x] 同时给定, 将同时生成两份报告;

示例：
```commandline
# 绝对路径执行
> tongban_report -d=d:\test\data.xlsx -f=d:\test\functional.docx -s=d:\test\safety.docx

# 当前文件夹下相对路径执行
> tongban_report -d=data.xlsx -f=functional.docx -s=safety.docx
```

### 打包&发布

```commandline
# 清理环境
python setup.py clean

# 重新打包
python setup.py sdist bdist_wheel

# 本地安装
pip install tongban_report
```

### 结束