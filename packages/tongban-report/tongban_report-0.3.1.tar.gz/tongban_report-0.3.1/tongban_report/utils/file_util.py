# encoding: utf-8
import datetime
import os

current_time = datetime.datetime.now().strftime("%Y%m%d%H%M")
base_path = os.path.join(os.getcwd(), "output", current_time)

class FileUtil(object):

    def __init__(self, project_num, year, month, title, type):
        self.project_num = project_num
        self.year = year
        self.month = month
        self.title = title
        self.type = type  # 1功能 2安全
        self.path = os.path.join(base_path, f"{self.year}年{self.month}月")

    def folder_path(self):
        path = None
        if self.project_num == 0:
            if self.type == 1:
                path = FileUtil.single_folder_functional(self)
            elif self.type == 2:
                path = FileUtil.single_folder_safety(self)
        else:
            if self.type == 1:
                path = FileUtil.double_folder_functional(self)
            elif self.type == 2:
                path = FileUtil.double_folder_safety(self)
        return path


    def double_folder_functional(self):
        # report_path = os.path.join(self.path, self.title, "功能测试报告")
        report_path = os.path.join(self.path, self.title)
        if not os.path.exists(report_path):
            os.makedirs(report_path)
        save_path = os.path.join(report_path, "一网通办标准政务服务事项自测报告.docx")
        return save_path

    def double_folder_safety(self):
        # report_path = os.path.join(self.path, self.title, "安全测试报告")
        report_path = os.path.join(self.path, self.title)
        if not os.path.exists(report_path):
            os.makedirs(report_path)
        save_path = os.path.join(report_path, "一网通办应用上线安全检查测试报告.docx")
        return save_path

    def single_folder_functional(self):
        os.system(rf'mkdir "{base_path}\功能报告\{self.project_num}"\"{self.year}年{self.month}月实施"')
        os.system(rf'mkdir "{base_path}\功能报告\{self.project_num}"\"{self.year}年{self.month}月实施"\“{self.title}"')
        os.system(rf'mkdir "{base_path}\功能报告\{self.project_num}"\"{self.year}年{self.month}月实施"\”{self.title}"\"2.测试报告"')
        save_path = rf'{base_path}\功能报告\{self.project_num}\{self.year}年{self.month}月实施\{self.title}\2.功能测试报告\“一网通办”标准政务服务事项自测报告.docx'
        return save_path

    def single_folder_safety(self):
        save_path = f'../document_output/2023/{self.project_num}/{self.year}年{self.month}月实施/' + \
                    f'{self.title}/2.测试报告/一网通办应用上线安全检查测试报告.docx'
        return save_path


if __name__ == '__main__':
    print(FileUtil(4, 2024, 10, '你好', 1).folder_path())
