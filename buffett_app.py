import streamlit as st
import yfinance as yf
import openai
import os

# 👉 Tilføj din egen OpenAI API-nøgle her
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="BuffettGPT", layout="centered")
st.title("📈 BuffettGPT – Værdibaseret aktievurdering")

ticker = st.text_input("Indtast aktie-ticker (f.eks. AAPL, PG, JNJ)")

def get_stock_data(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)
    info = stock.info
    return {
        "Ticker": ticker_symbol,
        "P/E": info.get("trailingPE"),
        "ROIC": info.get("returnOnEquity"),
        "FCF": info.get("freeCashflow"),
        "Debt": info.get("totalDebt"),
        "Stable": "Yes" if info.get("beta", 1) < 1 else "No"
    }

def ask_chatgpt_about_stock(data):
    prompt = f"""
    Vurder følgende aktie ud fra Warren Buffetts metode:

    - Ticker: {data['Ticker']}
    - P/E: {data['P/E']}
    - ROIC: {data['ROIC']}
    - Free Cash Flow: {data['FCF']}
    - Total Debt: {data['Debt']}
    - Stabilitet: {data['Stable']}

    Brug Buffetts principper: moat, margin of safety, sund økonomi og ledelse. 
    Vurdér om aktien er interessant, og forklar hvorfor.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

if st.button("Analyser aktien"):
    if ticker:
        with st.spinner("Henter data og vurderer..."):
            try:
                stock_data = get_stock_data(ticker)
                st.subheader("📊 Fundamentale nøgletal")
                st.json(stock_data)

                analysis = ask_chatgpt_about_stock(stock_data)
                st.subheader("🤖 Buffetts vurdering")
                st.markdown(analysis)
            except Exception as e:
                st.error(f"Noget gik galt: {e}")
    else:
        st.warning("Skriv en aktie-ticker først.")
