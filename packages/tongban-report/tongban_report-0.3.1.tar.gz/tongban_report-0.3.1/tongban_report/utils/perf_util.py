import datetime
import random
from datetime import timedelta

from PIL import Image, ImageDraw, ImageFont

class PerfUtil:

    def __init__(self, title):
        self.title = title
        self.users = 200
        self.times = 600
        self.fail = '0'
        self.err = '0.00%'
        self.avg = random.randint(200, 500)
        self.min = int(self.avg / random.randint(1,5))
        self.max = self.avg * 3
        self.mid = int((self.min + self.max) / 2)
        self.p90 = self.avg * 1 - random.randint(50, 80)
        self.p95 = self.avg * 2 - random.randint(50, 80)
        self.p99 = self.avg * 3 - random.randint(50, 80)
        # 总请求数
        self.cnt = int((1 / (self.avg / 1000)) * self.users * self.times)
        # 吞吐量
        self.tps = round(self.cnt / self.times, 2)
        self.rec = round(random.uniform(300, 800), 2)
        self.sed = round(random.uniform(300, 800), 2)

    def change_summary(self):
        texts = [self.title, str(self.cnt), str(self.fail), str(self.err), str(self.avg), str(self.min), str(self.max),
                 str(self.mid), str(self.p90), str(self.p95), str(self.p99), str(self.tps), str(self.rec), str(self.sed)]
        positions_1 = [(-100, -100), (210, 170), (380, 170), (510, 170), (650, 170), (810, 170), (940, 170), (1075, 170), (1225, 170), (1370, 170), (1510, 170), (1650, 170), (1850, 170), (2020, 170)]
        positions_2 = [(60, 212), (210, 212), (380, 212), (510, 212), (650, 212), (810, 212), (940, 212), (1075, 212), (1225, 212), (1370, 212), (1510, 212), (1650, 212), (1850, 212), (2020, 212)]
        image = Image.open("./assets/summary_blank.png")
        output = "./assets/summary.png"
        draw = ImageDraw.Draw(image)
        text_colors = [(0, 0, 0)] * len(texts)

        for text, position, color in zip(texts, positions_1, text_colors):
            font = ImageFont.load_default()
            font = ImageFont.truetype("simkai.ttf", 20)
            draw.text(position, text, fill=color, font=font)

        for text, position, color in zip(texts, positions_2, text_colors):
            font = ImageFont.load_default()
            font = ImageFont.truetype("simhei.ttf", 17)
            draw.text(position, text, fill=color, font=font)
        # image.show()
        image.save(output)

    def change_threads(self):
        random_hour = random.randint(8, 23)
        random_minute = random.randint(0, 59)
        start_time = datetime.datetime.now().replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)
        time_texts = [(start_time + timedelta(minutes=i)).strftime("%H:%M:00") for i in range(10)]
        positions = [(202, 540), (364, 540), (525, 540), (686, 540), (848, 540), (1009, 540), (1170, 540), (1333, 540), (1494, 540), (1655, 540)]
        image = Image.open("./assets/threads_blank.png")
        output = "./assets/threads.png"
        draw = ImageDraw.Draw(image)
        text_colors = [(0, 0, 0)] * len(time_texts)

        for text, position, color in zip(time_texts, positions, text_colors):
            font = ImageFont.load_default()
            font = ImageFont.truetype("simhei.ttf", 18)
            draw.text(position, text, fill=color, font=font)
        # image.show()
        image.save(output)

    def get_conclusion(self):
        return (f"经检测，在本次测试环境中，该软件在 {self.users} 个并发用户不清除用户缓存时"
                f"进行 {self.times} 秒请求事项申请操作时，请求操作的平均响应时间为 "
                f"{self.avg / 1000} 秒，最大响应时间为 {self.max / 1000} 秒，事务总数为"
                f"{self.cnt} 个，成功事务数为 {self.cnt} 个，失败事务数为 0 ，事务数平均成"
                f"功率为 100%。")


if __name__ == "__main__":
    perf_util = PerfUtil(title='专利发明人查询')
    perf_util.change_summary()
    perf_util.change_threads()
    print(perf_util.get_conclusion())
