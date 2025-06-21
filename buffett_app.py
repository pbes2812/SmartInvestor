import streamlit as st
import yfinance as yf
from openai import OpenAI
import datetime

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="BuffettGPT+", layout="wide")
st.title("📈 BuffettGPT+ – Din værdibaserede investeringsassistent")

# --- Watchlist eksempel ---
watchlist = ["AAPL", "PG", "JNJ", "NVO", "MSFT"]
st.sidebar.header("📋 Min Watchlist")
for ticker in watchlist:
    st.sidebar.write(f"🔹 {ticker}")

# --- DCF-rente valg ---
discount_rate = st.sidebar.slider("📉 Vælg diskonteringsrente (DCF)", 5.0, 12.0, 10.0, step=0.5)

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
            future_value = fcf * ((1 + growth) ** years)
            dcf_intrinsic = future_value / ((1 + discount_rate / 100) ** years)
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

    Afslut med én klar anbefaling i store bogstaver:
    - "KØB", "HOLD" eller "SÆLG"
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def find_undervalued_stocks():
    screening_prompt = f"""
    Du er en investor, der tænker som Warren Buffett.

    Ud fra kendt information foreslå 5 aktier, som pt. ser undervurderede ud ifølge:
    - Lav P/E (under 20)
    - ROIC > 12 %
    - Positiv og stabil FCF
    - Lav gæld
    - Klar moat
    - Pris under intrinsic value med margin of safety

    Format:
    1. Virksomhed (Ticker)
       - Branche:
       - P/E:
       - ROIC:
       - FCF:
       - Gæld:
       - Moat:
       - Vurdering: KØB / HOLD / SÆLG
       - Kommentar:
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": screening_prompt}]
    )
    return response.choices[0].message.content

# --- Analyse-knap ---
if st.button("🔍 Vurdér specifik aktie"):
    if ticker:
        with st.spinner("Henter data og analyserer..."):
            try:
                stock_data = get_stock_data(ticker)
                st.subheader("📊 Nøgletal")
                st.json(stock_data)
                analysis = ask_buffett_like_ai(stock_data)
                st.subheader("🧠 Buffetts vurdering")
                st.markdown(analysis)
            except Exception as e:
                st.error(f"Noget gik galt: {e}")
    else:
        st.warning("Skriv en aktie-ticker først.")

# --- Screening-knap ---
if st.button("💡 Find gode billige aktier"):
    with st.spinner("GPT screener markedet..."):
        try:
            recommendations = find_undervalued_stocks()
            st.subheader("📋 GPT’s screening")
            st.markdown(recommendations)
        except Exception as e:
            st.error(f"Noget gik galt: {e}")

# --- Daglig “screening”-visning (simuleret) ---
st.sidebar.markdown("---")
st.sidebar.subheader("📆 Seneste screening (simuleret)")
today = datetime.date.today()
st.sidebar.text(f"{today.strftime('%d-%m-%Y')}")
st.sidebar.text("🔹 PG – KØB\\n🔹 INTC – HOLD\\n🔹 T – SÆLG")
