import streamlit as st
import openai
import yfinance as yf
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

st.set_page_config(page_title="SmartInvestor v4", layout="centered")
st.title("📊 SmartInvestor – Buffetts analyse med salgsvurdering")

ticker = st.text_input("Indtast aktieticker (f.eks. AAPL, MSFT, NOVO-B.CO)", "")
købspris = st.number_input("Indtast din købspris (valgfrit)", min_value=0.0, step=0.1, format="%.2f")
prompt = st.text_area("Hvad vil du gerne have vurderet?",
"Er denne aktie undervurderet, og bør jeg sælge eller holde ud fra min købspris?")

def hent_noegletal(ticker):
try:
aktie = yf.Ticker(ticker)
info = aktie.info
pe_ratio = info.get("trailingPE", "Ukendt")
roe = info.get("returnOnEquity", "Ukendt")
fcf = info.get("freeCashflow", None)
eps = info.get("trailingEps", None)
pris = info.get("currentPrice", "Ukendt")
gæld = info.get("totalDebt", "Ukendt")
valuta = info.get("financialCurrency", "Ukendt")

# DCF-beregning (simplificeret)
vækstrate = 0.08
diskonteringsrente = 0.10
intrinsic_value = None
if eps and isinstance(eps, (int, float)):
intrinsic_value = round(eps * (1 + vækstrate) / (diskonteringsrente - vækstrate), 2)

return {
"Ticker": ticker,
"P/E": pe_ratio,
"ROIC": roe,
"Free Cash Flow": fcf,
"Debt": gæld,
"Current Price": pris,
"Estimated Intrinsic Value (DCF)": intrinsic_value,
"Currency": valuta
}
except Exception as e:
return {"Fejl": str(e)}

if st.button("🔍 Analyser aktie"):
if ticker:
noegletal = hent_noegletal(ticker)
st.subheader("📊 Nøgletal")
st.json(noegletal)

fakta_tekst = "\n".join([f"{k}: {v}" for k, v in noegletal.items()])
købspris_tekst = f"Brugerens købspris er: {købspris}" if købspris > 0 else "Ingen købspris angivet."

messages = [
{"role": "system", "content": (
"Du er en investeringsrådgiver, der vurderer aktier ud fra Warren Buffetts principper. "
"Her er data for aktien:\n" + fakta_tekst + "\n" + købspris_tekst)},
{"role": "user", "content": f"Ticker: {ticker}\n{prompt}"}
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
