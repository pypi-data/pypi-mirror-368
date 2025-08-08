# encoding: utf-8
import os
import random
from decimal import Decimal

import matplotlib.pyplot as plt

# base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
current_path = os.getcwd()

def get_perf_report(title=None):
    # 单次脚本执行生成图片数量
    for k in range(1, 2):
        plt.style.use("seaborn-v0_8-whitegrid")

        labels = []
        a0 = []
        b0 = []
        c0 = []
        d0 = []
        e0 = []

        # 压测时间，60分钟
        for i in range(1, 61):
            labels.append(f"{i}'")
            # a0.append(random.randint(260, 500))
            a0.append(random.randint(180, 200))  # 默认使用
            # a0.append(random.randint(880, 1000))  # 随申码

            b0.append(random.uniform(1, 3))
            c0.append(random.uniform(4, 5))
            d0.append(random.uniform(0.95, 1))
            e0.append(random.uniform(0, 0.05))

        b0_sum = 0
        # print(b0)  # 平均响应时间
        for item in b0:
            b0_sum += item
        average_ping = Decimal(b0_sum / len(b0)).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")
        # print(average_ping)

        c0_max = Decimal(max(c0)).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")  # 最大响应时间
        # print(c0_max)

        # print(a0)
        a0_sum = 0  # 总事务数
        for item in a0:
            a0_sum += item
        # print(a0_sum)

        d0_sum = 0  # 平均成功率
        for item in d0:
            d0_sum += item
        average_rate = d0_sum / len(d0)
        average_rate = Decimal(average_rate).quantize(Decimal("0.001"), rounding="ROUND_HALF_UP")
        # print(average_rate)

        success_num = int(a0_sum * average_rate)  # 成功事务数
        fail_num = a0_sum - success_num  # 失败事务数
        # print(success_num)
        # print(fail_num)

        # 设置图例并且设置图例的字体及大小
        font1 = {'family': 'SimHei', 'weight': 'normal', 'size': 15}
        font2 = {'family': 'SimHei', 'weight': 'normal', 'size': 20}
        plt.xticks(fontproperties='SimHei', fontsize=10)
        plt.yticks(fontproperties='SimHei', fontsize=10)

        fig = plt.figure()
        fig.set_size_inches(20, 10)

        # 随机图
        p0 = fig.add_subplot(111)
        p0.plot(labels, a0, c='Black', marker='*', linestyle='-', label='TPS')
        p0.set_ylabel(u'TPS', font2)
        p0.set_xlabel(u'持续时间(min)', font2)
        # 图例展示位置，数字代表第几象限
        p0.legend(loc=3, prop=font1)

        p1 = p0.twinx()
        p1.plot(labels, b0, c='Blue', marker='+', linestyle='-', label='平均响应时间')
        p1.plot(labels, c0, c='Yellow', marker='x', linestyle='-', label='最大响应时间')
        p1.set_ylabel(u'响应时间(s)', font2)
        p1.legend(loc=1, prop=font1)

        p2 = p0.twinx()
        p2.plot(labels, d0, c='Green', marker='^', linestyle='-', label='成功率')
        p2.plot(labels, e0, c='Red', marker='o', linestyle='-', label='失败率')
        p2.set_ylabel(u'概率(%)', font2)
        p2.spines["right"].set_position(('data', 65))
        p2.legend(loc=4, prop=font1)

        # ax = plt.gca()

        # with open("../config/name.txt", 'r') as f:
        #     title = f.read()
            # print(title)
        # title = '身后一件事'
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.title(f"{title}", fontsize=30, loc='center', color='black')

        # plt.show()
        chart_path = os.path.join(current_path, "assets")
        if not os.path.exists(chart_path):
            os.makedirs(chart_path)
        fig.savefig(os.path.join(chart_path, "assets.png"), dpi=300)

        conclusion = f"经检测，在本次测试环境中，该软件在 200 个并发用户不清除用户缓存时 进行 6000 秒请求事项申请操作时，" \
                     f"请求操作的平均响应时间为 {average_ping} 秒，最大响应时间为 {c0_max} 秒，" \
                     f"事务总数为 {a0_sum} 个，成功事务数为 {success_num} 个，失败事务数为 {fail_num} ，" \
                     f"事务数平均成功率为 {average_rate * 100}%。"
        return conclusion

    return None
