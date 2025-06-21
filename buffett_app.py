import streamlit as st
import yfinance as yf
from openai import OpenAI
import os

# Opret OpenAI klient med API-nøgle fra Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="BuffettGPT", layout="centered")
st.title("📈 BuffettGPT – Værdibaseret aktievurdering")

ticker = st.text_input("Indtast aktie-ticker (f.eks. AAPL, PG, JNJ)")

def get_stock_data(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)
    info = stock.info
    fcf = info.get("freeCashflow", None)
    pe = info.get("trailingPE", None)
    roic = info.get("returnOnEquity", None)
    beta = info.get("beta", 1)
    debt = info.get("totalDebt", None)
    price = info.get("currentPrice", None)

    moat_score = 0
    if roic and roic > 0.15:
        moat_score += 1
    if beta < 1:
        moat_score += 1

    dcf_intrinsic = None
    if fcf and price:
        try:
            growth = 0.08
            years = 5
            discount_rate = 0.10
            future_value = fcf * ((1 + growth) ** years)
            dcf_intrinsic = future_value / ((1 + discount_rate) ** years)
        except:
            pass

    return {
        "Ticker": ticker_symbol,
        "P/E": pe,
        "ROIC": roic,
        "Free Cash Flow": fcf,
        "Debt": debt,
        "Stable": "Yes" if beta < 1.2 else "No",
        "Moat Score (0-2)": moat_score,
        "Estimated Intrinsic Value (DCF)": round(dcf_intrinsic, 2) if dcf_intrinsic else "N/A",
        "Current Price": price
    }

def ask_buffett_like_ai(data):
    prompt = f"""
    Du er Warren Buffett, og du skal vurdere denne aktie ud fra dine investeringsprincipper.

    - Ticker: {data['Ticker']}
    - P/E: {data['P/E']}
    - ROIC: {data['ROIC']}
    - Free Cash Flow: {data['Free Cash Flow']}
    - Total Debt: {data['Debt']}
    - Stabilitet: {data['Stable']}
    - Moat Score: {data['Moat Score (0-2)']}
    - DCF Intrinsic Value: {data['Estimated Intrinsic Value (DCF)']}
    - Current Price: {data['Current Price']}

    Giv en kort analyse på dansk af aktien ud fra:
    - Forståelig forretning
    - Moat
    - Sund økonomi
    - Margin of safety

    Afslut din vurdering med en tydelig anbefaling i store bogstaver:
    - "KØB" hvis aktien er attraktiv og undervurderet
    - "HOLD" hvis den er fair prissat men solid
    - "SÆLG" hvis den er overvurderet eller ikke passer til dine kriterier
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

if st.button("Analyser aktien"):
    if ticker:
        with st.spinner("Henter data og vurderer..."):
            try:
                stock_data = get_stock_data(ticker)
                st.subheader("📊 Fundamentale nøgletal")
                st.json(stock_data)

                analysis = ask_buffett_like_ai(stock_data)
                st.subheader("🤖 Buffetts vurdering")
                st.markdown(analysis)
            except Exception as e:
                st.error(f"Noget gik galt: {e}")
    else:
        st.warning("Skriv en aktie-ticker først.")

