# OpenBB 风格 A 股全自动选股（底层数据源：AkShare）
import akshare as ak
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# ----------------------
# 全市场 A 股选股策略（OpenBB 风格筛选逻辑）
# ----------------------
def pick_stocks():
    print("📊 开始全市场 A 股自动选股（数据源：AkShare）...")

    # 1. 获取全市场 A 股实时数据（东方财富接口）
    df = ak.stock_zh_a_spot_em()

    # 2. 基础清洗
    df = df[~df["名称"].str.contains("ST|退|\\*", na=False)]  # 排除风险股
    df = df[df["最新价"] > 2]  # 排除极低价格股
    df = df[df["成交额"] > 50000000]  # 成交额大于 5000 万，流动性充足

    # 3. OpenBB 风格技术面筛选
    df = df[
        (df["涨跌幅"] > -4) &
        (df["涨跌幅"] < 6) &
        (df["换手率"] > 1) &
        (df["换手率"] < 12)
    ]

    # 4. 取强势票前 20 只
    df = df.sort_values(by="成交额", ascending=False).head(20)

    if df.empty:
        return "今日无符合条件的股票"

    # 5. 生成选股报告
    report = "【OpenBB 风格 · A 股全市场自动选股】\n"
    report += f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    for _, row in df.iterrows():
        report += f"股票代码：{row['代码']}\n"
        report += f"股票名称：{row['名称']}\n"
        report += f"当前价格：{row['最新价']:.2f}\n"
        report += f"涨跌幅：{row['涨跌幅']:.2f}%\n"
        report += f"换手率：{row['换手率']:.2f}%\n"
        report += f"成交额：{row['成交额'] / 100000000:.2f} 亿\n\n"

    print(report)
    return report

# ----------------------
# 发送邮件（沿用你之前的 QQ 邮箱）
# ----------------------
def send_email(content):
    try:
        sender = os.environ["EMAIL_SENDER"]
        password = os.environ["EMAIL_PASSWORD"]
        receivers = os.environ["EMAIL_RECEIVERS"].split(",")

        msg = MIMEText(content, "plain", "utf-8")
        msg["Subject"] = "📈 每日 A 股自动选股报告"
        msg["From"] = sender
        msg["To"] = ",".join(receivers)

        with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receivers, msg.as_string())

        print("✅ 邮件发送成功！")
    except Exception as e:
        print(f"❌ 发送失败：{str(e)}")
        raise

# ----------------------
# 主程序入口
# ----------------------
if __name__ == "__main__":
    result = pick_stocks()
    send_email(result)
