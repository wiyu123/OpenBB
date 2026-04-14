# 真正 OpenBB 内核 + A 股全市场选股（你要的最终版）
import akshare as ak
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from openbb import obb  # <--- 真正调用 OpenBB 库！

# ----------------------
# 【核心】OpenBB 技术指标分析
# ----------------------
def analyze_with_openbb(symbol: str, name: str, price: float):
    try:
        # 获取K线数据
        df = obb.equity.price.historical(
            symbol=symbol,
            provider="yfinance",
            interval="1d",
            period="6m"
        ).to_df()

        # ========== OpenBB 原生指标计算 ==========
        # 均线
        df["ma20"] = obb.technical.sma(data=df["close"], length=20)
        df["ma60"] = obb.technical.sma(data=df["close"], length=60)
        
        # 震荡指标
        rsi = obb.technical.rsi(data=df["close"], length=14).iloc[-1]
        macd = obb.technical.macd(data=df["close"]).iloc[-1]
        
        # 趋势判断
        trend = "🚀 多头趋势" if price > df["ma20"].iloc[-1] > df["ma60"].iloc[-1] else "📉 震荡/空头"
        rsi_status = "超买" if rsi > 70 else "超卖" if rsi < 30 else "健康"

        return {
            "name": name,
            "price": price,
            "trend": trend,
            "rsi": round(rsi, 1),
            "rsi_status": rsi_status,
            "macd": round(macd["macd"], 2),
            "ma20": round(df["ma20"].iloc[-1], 2),
            "ma60": round(df["ma60"].iloc[-1], 2)
        }
    except Exception:
        return None

# ----------------------
# A 股全市场选股（AkShare）
# ----------------------
def pick_stocks():
    print("🔍 全市场 A 股扫描 + OpenBB 深度分析...")
    
    # 1. 从 AkShare 获取全市场 A 股
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

    report = "="*60 + "\n"
    report += "📊 OPENBB 专业量化选股报告\n"
    report += "="*60 + "\n"
    report += f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    # 2. 遍历股票，用 OpenBB 深度分析
    for _, row in df.iterrows():
        code = row["代码"]
        name = row["名称"]
        price = row["最新价"]
        
        # 转换为 Yahoo 格式（OpenBB 支持）
        yahoo_code = f"{code[:6]}.SS" if code.startswith("6") else f"{code[:6]}.SZ"
        
        # 调用 OpenBB 分析
        ana = analyze_with_openbb(yahoo_code, name, price)
        if not ana:
            continue

        report += f"【{code}】{name}\n"
        report += f"价格：{ana['price']:.2f}\n"
        report += f"趋势：{ana['trend']}\n"
        report += f"RSI：{ana['rsi']}（{ana['rsi_status']}）\n"
        report += f"MA20：{ana['ma20']} | MA60：{ana['ma60']}\n"
        report += f"MACD：{ana['macd']}\n"
        report += "-"*40 + "\n\n"

    report += "⚠️ 数据来源：OpenBB 量化引擎 + AkShare A 股数据\n"
    report += "="*60
    return report

# ----------------------
# 发送邮件
# ----------------------
def send_email(content):
    try:
        sender = os.environ["EMAIL_SENDER"]
        password = os.environ["EMAIL_PASSWORD"]
        receivers = os.environ["EMAIL_RECEIVERS"].split(",")

        msg = MIMEText(content, "plain", "utf-8")
        msg["Subject"] = "📊 OPENBB 专业 A 股选股报告"
        msg["From"] = sender

        with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receivers, msg.as_string())
        print("✅ 发送成功")
    except:
        pass

# ----------------------
# 主程序
# ----------------------
if __name__ == "__main__":
    result = pick_stocks()
    print(result)
    send_email(result)
