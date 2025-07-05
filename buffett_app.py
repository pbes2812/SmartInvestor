import streamlit as st
import openai
import yfinance as yf
import os
openai.api_key = os.environ.get("OPENAI_API_KEY")

st.set_page_config(page_title="SmartInvestor med Intrinsic Value", layout="centered")
st.title("📊 SmartInvestor – Buffett-analyse med intrinsic value")

ticker = st.text_input("Indtast aktieticker (f.eks. AAPL, MSFT, NOVO-B.CO)", "")
prompt = st.text_area("Hvad vil du gerne have vurderet?",
"Er denne aktie undervurderet ifølge Warren Buffetts principper?")

def hent_noegletal(ticker):
try:
aktie = yf.Ticker(ticker)
info = aktie.info
pe_ratio = info.get("trailingPE", "Ukendt")
roe = info.get("returnOnEquity", "Ukendt")
fcf = info.get("freeCashflow", None)
eps = info.get("trailingEps", None)
vækstrate = 0.08 # 8% vækst som default
diskonteringsrente = 0.10 # 10% som WACC/afkastkrav
intrinsic_value = None
if eps and isinstance(eps, (int, float)):
intrinsic_value = round(eps * (1 + vækstrate) / (diskonteringsrente - vækstrate), 2)
pris = info.get("currentPrice", "Ukendt")
valuta = info.get("financialCurrency", "Ukendt")
return {
"P/E": pe_ratio,
"ROE": roe,
"EPS": eps,
"Free Cash Flow": fcf,
"Aktuel Pris": pris,
"Intrinsic Value (DCF estimeret)": intrinsic_value,
"Valuta": valuta
}
except Exception as e:
return {"Fejl": str(e)}

if st.button("🔍 Analyser aktie"):
if ticker:
noegletal = hent_noegletal(ticker)
st.subheader("🔢 Hentede nøgletal")
st.json(noegletal)

fakta_tekst = "\n".join([f"{k}: {v}" for k, v in noegletal.items()])
messages = [
{"role": "system", "content": (
"Du er en investeringsrådgiver, der vurderer aktier ud fra Warren Buffetts principper. "
"Her er de vigtigste nøgletal for aktien baseret på live data:\n" + fakta_tekst)},
{"role": "user", "content": f"Ticker: {ticker}\nSpørgsmål: {prompt}"}
]

with st.spinner("GPT analyserer..."):
try:
response = openai.ChatCompletion.create(
model="gpt-4",
messages=messages,
temperature=0.3,
)
st.success("Analyse færdig")
st.markdown(response['choices'][0]['message']['content'])
except Exception as e:
st.error(f"Fejl under GPT-analyse: {e}")
else:
st.warning("Indtast venligst et aktieticker.")
