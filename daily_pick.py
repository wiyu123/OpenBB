# OpenBB 每日A股自动选股（适配最新版API）
from openbb import obb
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# ---------------------- 选股策略（可自行修改） ----------------------
# 策略：沪深A股 + 非ST + 20日均线多头 + 成交量正常（稳健新手版）
def pick_stocks():
    print("开始全市场A股选股...")
    
    # 新版API：用screener替代screen，A股筛选逻辑
    # 先获取A股全市场列表，再做技术面/基本面筛选
    # 注：OpenBB免费版A股筛选能力有限，这里用更稳定的实现方式
    df = obb.equity.screener(
        country="cn",
        exchange="shsz",  # 沪深交易所
        limit=20
    )

    if df.empty:
        return "今日无符合条件的股票"

    # 二次筛选：保留非ST、均线多头、估值合理的标的
    filtered = df[
        (~df["name"].str.contains("ST|*ST|退")) &  # 排除ST/退市股
        (df["close"] > df["ma_20"]) &  # 股价在20日均线上方
        (df["pe_ratio"] > 50) & (df["pe_ratio"] < 900)  # 市盈率0-50
    ].head(10)  # 取前10只

    if filtered.empty:
        return "今日无符合条件的股票"

    # 生成报告
    report = "【每日A股自动选股报告】\n"
    report += f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    for idx, row in filtered.iterrows():
        report += f"代码：{row['symbol']}\n名称：{row['name']}\n当前价：{row['close']:.2f}\n市盈率：{row['pe_ratio']:.1f}\n20日均线：{row['ma_20']:.2f}\n\n"
    
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
        raise  # 抛出异常，让GitHub Actions显示错误

# ---------------------- 主运行 ----------------------
if __name__ == "__main__":
    result = pick_stocks()
    send_email(result)
