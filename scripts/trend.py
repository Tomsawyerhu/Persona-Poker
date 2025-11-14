import matplotlib.pyplot as plt

# 定义轮次：共13轮
rounds = list(range(1, 21))  # R1 到 R13

# 原始筹码数据（从日志提取）
players_chips = {
    'James': [
        9950, 9950, 7150, 9950, 9950, 9950, 9950, 9950, 9950, 9950,
        9950, 18600, 15100, 9950, 9950, 9950, 9950, 9950, 15100, 9950
    ],
    'Susan': [
        7200, 9900, 9900, 4800, 6900, 9900, 7000, 6500, 7000, 0,
        2700, 9900, 9900, 9900, 9600, 8000, 7000, 9900, 9900, 9900
    ],
    'David': [
        10000, 10000, 10000, 10000, 10000, 12150, 10000, 10000, 10000, 10000,
        10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000
    ],
    'Lily': [
        22850, 0, 0, 25650, 0, 0, 0, 23550, 23050, 30050,
        0, 0, 15000, 20150, 0, 0, 0, 20150, 0, 0
    ],
    'Ethan': [
        0, 30150, 22950, 0, 23150, 18000, 23050, 0, 0, 0,
        27350, 11500, 0, 0, 20450, 22050, 23050, 0, 15000, 0
    ],
    'Olivia': [
        10000, 0, 10000, 9600, 10000, 10000, 10000, 10000, 10000, 10000,
        10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 30150
    ]
}



# Step 1: 转换为单局盈亏（当前筹码 - 10000）
single_profit_loss = {}
for player, chips in players_chips.items():
    single_profit_loss[player] = [chip - 10000 for chip in chips]

# Step 2: 计算累计盈亏（cumulative sum）
cumulative_pl = {}
for player, pl_list in single_profit_loss.items():
    cum_sum = []
    total = 0
    for pl in pl_list:
        total += pl
        cum_sum.append(total)
    cumulative_pl[player] = cum_sum

# Step 3: 找出每轮最大累计盈亏（用于标注峰值）
n_rounds = len(rounds)
round_max_cumpl = [
    max(cumulative_pl[p][i] for p in cumulative_pl) for i in range(n_rounds)
]

# 创建图表
plt.figure(figsize=(14, 8))

colors = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5']  # 自定义颜色便于区分

for idx, (player, cum_pl) in enumerate(cumulative_pl.items()):
    plt.plot(rounds, cum_pl, marker='o', label=player, linewidth=2, color=colors[idx])

    # 标注每轮最高累计盈利者
    for i, (r, val) in enumerate(zip(rounds, cum_pl)):
        if val == round_max_cumpl[i] and val > -1000:  # 忽略明显负值
            plt.annotate(f'{val:+}', (r, val), textcoords="offset points", xytext=(0, 10),
                         ha='center', fontsize=8, fontweight='bold', color='red')

# 添加 break-even 水平线
plt.axhline(y=0, color='gray', linestyle='--', linewidth=1.5, label='Break-even Line (Total P/L = 0)')

# 图表设置
plt.title('Cumulative Profit/Loss Over 13 Rounds (Base: 10,000 Chips)', fontsize=16)
plt.xlabel('Round', fontsize=12)
plt.ylabel('Cumulative Profit / Loss (chips)', fontsize=12)
plt.xticks(rounds)
plt.grid(True, alpha=0.3)

# Y轴范围和标签
min_val = min(min(cum) for cum in cumulative_pl.values())
max_val = max(max(cum) for cum in cumulative_pl.values())
plt.ylim(min_val - 500, max_val + 1000)
yticks = range(int(min_val // 1000) * 1000, int(max_val // 1000 + 2) * 1000, 2000)
plt.yticks(yticks, [f'{y:+}' for y in yticks])

# 图例位置
plt.legend(title='Players', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# 可选：保存图像
# plt.savefig('cumulative_profit_loss_13_rounds.png', dpi=150, bbox_inches='tight')

# 显示图表
plt.show()
