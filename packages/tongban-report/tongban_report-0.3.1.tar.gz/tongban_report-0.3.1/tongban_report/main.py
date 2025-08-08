import argparse
import importlib.metadata
import sys

from tongban_report.utils.func_report import func_report
from tongban_report.utils.safe_report import safe_report
from tongban_report.utils.upload_util import upload

sheet = 'Sheet1'

def main():
    # 获取版本号
    try:
        version = importlib.metadata.version('tongban_report')
    except importlib.metadata.PackageNotFoundError:
        version = "未知版本"

    # 解析命令行参数
    parser = argparse.ArgumentParser(description="报告生成工具")
    parser.add_argument('-d', '--data', required=True, help='数据来源Excel文件的路径(必填)')
    parser.add_argument("-f", "--func", help="功能测试报告模板")
    parser.add_argument("-s", "--safe", help="安全测试报告模板")
    parser.add_argument("-u", "--upload", help="上传测试报告")
    parser.add_argument("-v", "--version", action="version", version=f"v{version}", help="显示当前版本")
    args = parser.parse_args()

    print("数据来源:", args.data)

    if args.func:
        print("功能模板:", args.func)
        func_report(docx=args.func, xlsx=args.data, sheet=sheet, project_num=2)
    if args.safe:
        print("安全模板:", args.safe)
        safe_report(docx=args.safe, xlsx=args.data, sheet=sheet, project_num=2)
    if args.upload:
        print("准备上传钉钉云盘 ...")
        upload()
    if not args.func and not args.safe:
        print("错误：必须指定 -f 或 -s 中的至少一个")
        sys.exit(1)

if __name__ == "__main__":
    main()
