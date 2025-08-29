import sys
sys.path.insert(0, r"C:\Users\Siam\Desktop\tvdatafeed_full")

from tvdatafeed import TvDatafeed
import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import plotly.graph_objects as go

# ✅ Candlestick Pattern Checker
def detect_candlestick_pattern(df):
    last = df.iloc[-2]  # শেষ সম্পূর্ণ ক্যান্ডেল
    body = abs(last['close'] - last['open'])
    candle_range = last['high'] - last['low']
    upper_shadow = last['high'] - max(last['open'], last['close'])
    lower_shadow = min(last['open'], last['close']) - last['low']

    if body < candle_range * 0.3:
        if upper_shadow > body * 2 and lower_shadow < body * 0.5:
            return "Inverted Hammer"
        elif lower_shadow > body * 2 and upper_shadow < body * 0.5:
            return "Hammer"
        elif body < candle_range * 0.1:
            return "Doji"
    return None

# ✅ Filter Function
def get_filtered_signal(symbol, screener="forex", exchange="FX_IDC", interval=Interval.INTERVAL_1_MINUTE):
    try:
        handler = TA_Handler(
            symbol=symbol,
            screener=screener,
            exchange=exchange,
            interval=interval
        )
        analysis = handler.get_analysis()
        summary = analysis.summary
        indicators = analysis.indicators

        recommendation = summary.get("RECOMMENDATION")
        rsi = indicators.get("RSI")
        macd = indicators.get("MACD.macd")
        signal_macd = indicators.get("MACD.signal")
        ema20 = indicators.get("EMA20")
        close_price = indicators.get("close")

        tv = TvDatafeed()
        candle_data = tv.get_hist(symbol=symbol, exchange="FX_IDC", interval="1m", n_bars=5)
        pattern = detect_candlestick_pattern(candle_data) if candle_data is not None and not candle_data.empty else None

        if recommendation in ["STRONG_BUY", "BUY"]:
            if (
                rsi and 45 < rsi < 70 and
                macd and signal_macd and macd > signal_macd and
                close_price and ema20 and close_price > ema20 and
                pattern in ["Hammer", "Inverted Hammer", "Doji"]
            ):
                return {
                    "symbol": symbol,
                    "recommendation": "BUY ✅",
                    "RSI": round(rsi, 2),
                    "MACD": round(macd, 2),
                    "EMA20": round(ema20, 2),
                    "Pattern": pattern
                }

        if recommendation in ["STRONG_SELL", "SELL"]:
            if (
                rsi and 30 < rsi < 55 and
                macd and signal_macd and macd < signal_macd and
                close_price and ema20 and close_price < ema20 and
                pattern in ["Doji"]
            ):
                return {
                    "symbol": symbol,
                    "recommendation": "SELL ✅",
                    "RSI": round(rsi, 2),
                    "MACD": round(macd, 2),
                    "EMA20": round(ema20, 2),
                    "Pattern": pattern
                }

        return None

    except Exception as e:
        return {"symbol": symbol, "recommendation": f"Error: {e}", "RSI": None, "MACD": None, "EMA20": None}

# ✅ Streamlit App
st.set_page_config(page_title="Super Signal App", layout="wide")

st.markdown("<h1 style='text-align:center;color:#00ffff;'>💹 Super Signal App</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray;'>এই অ্যাপ purely educational এবং research purpose এর জন্য।</p>", unsafe_allow_html=True)

bot_on = st.checkbox("✅ Signal Bot চালু করুন", value=False)
symbols = st.text_input("📘 একাধিক Symbol দিন (কমা দিয়ে আলাদা করুন)", value="EURUSD,GBPUSD,BTCUSDT")
interval = st.selectbox("🌸 Interval বাছাই করুন", ["1m", "5m", "15m", "1h"], index=0)

interval_map = {
    "1m": Interval.INTERVAL_1_MINUTE,
    "5m": Interval.INTERVAL_5_MINUTES,
    "15m": Interval.INTERVAL_15_MINUTES,
    "1h": Interval.INTERVAL_1_HOUR
}

# ✅ Signal Button
if st.button("🚀 Signal এখনি দেখাও") and bot_on:
    symbol_list = [s.strip() for s in symbols.split(",")]
    filtered_results = []

    for symbol in symbol_list:
        result = get_filtered_signal(symbol, interval=interval_map[interval])
        if result:
            filtered_results.append(result)

    if filtered_results:
        df = pd.DataFrame(filtered_results)
        st.success(f"✅ {len(df)} টি Sure-Shot Signal পাওয়া গেছে!")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("😔 কোনো High-Probability Signal পাওয়া যায়নি।")

    # ✅ Candlestick Chart
    st.subheader(f"📈 {symbol_list[0]} লাইভ ক্যান্ডেল চার্ট")
    tv = TvDatafeed()
    try:
        candle_data = tv.get_hist(symbol=symbol_list[0], exchange="FX_IDC", interval=interval, n_bars=100)
        if not candle_data.empty:
            fig = go.Figure(data=[go.Candlestick(
                x=candle_data.index,
                open=candle_data["open"],
                high=candle_data["high"],
                low=candle_data["low"],
                close=candle_data["close"]
            )])
            fig.update_layout(xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("❌ ক্যান্ডেল ডেটা পাওয়া যায়নি!")
    except Exception as e:
        st.error(f"⚠️ চার্ট আনতে সমস্যা হয়েছে: {e}")
else:
    st.info("🔔 Signal Bot চালু করুন এবং 'Signal এখনি দেখাও' বাটন চাপুন।")
