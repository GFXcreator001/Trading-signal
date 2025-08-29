
import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd

st.title("📈 Super Signal App")
st.write("This is a demo trading signal app using TradingView_TA.")

# Example usage
symbol = "AAPL"
exchange = "NASDAQ"

handler = TA_Handler(
    symbol=symbol,
    exchange=exchange,
    screener="america",
    interval=Interval.INTERVAL_1_DAY,
    timeout=10
)

analysis = handler.get_analysis()
st.write("Recommendation:", analysis.summary["RECOMMENDATION"])
