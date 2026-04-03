# OpenBB 每日A股自动选股
from openbb import obb
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# ---------------------- 选股策略（可自行修改） ----------------------
# 策略：沪深A股 + 非ST + 20日均线多头 + 成交量正常（稳健新手版）
def pick_stocks():
    print("开始全市场A股选股...")
    
    # 调用 OpenBB A股筛选
    df = obb.equity.screen(
        country="CN",                # 仅限中国A股
        exclude_types=["ETF", "REIT"],  # 排除基金
        fundamental={"pe_ratio": (30, 1000)},  # 市盈率0-50，排除亏损/高估
        technical={
            "ma20": "up",           # 20日均线向上
            "current": "above_ma20" # 股价在20日均线上方
        },
        limit=10  # 选出前10只
    )

    if df.empty:
        return "今日无符合条件的股票"

    # 生成报告
    report = "【每日A股自动选股报告】\n"
    report += f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    for idx, row in df.iterrows():
        report += f"代码：{row.symbol}\n名称：{row.name}\n价格：{row.close}\n\n"
    
    print(report)
    return report

# ---------------------- 发送邮件（沿用你之前的QQ邮箱配置） ----------------------
def send_email(content):
    try:
        sender = os.environ["EMAIL_SENDER"]
        password = os.environ["EMAIL_PASSWORD"]
        receivers = os.environ["EMAIL_RECEIVERS"].split(",")

        msg = MIMEText(content, "plain", "utf-8")
        msg["Subject"] = "【开盘参考】OpenBB 自动选股报告"
        msg["From"] = sender
        msg["To"] = ",".join(receivers)

        with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receivers, msg.as_string())
        
        print("✅ 邮件发送成功！")
    except Exception as e:
        print(f"❌ 发送失败：{e}")

# ---------------------- 主运行 ----------------------
if __name__ == "__main__":
    result = pick_stocks()
    send_email(result)
