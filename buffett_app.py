import streamlit as st
import openai
import yfinance as yf
import os
import pandas as pd

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

st.set_page_config(page_title="SmartInvestor v6.1", layout="centered")
st.title("📈 SmartInvestor – Buffett-analyse med ticker-søgning og vurdering")

# 📘 Indlæs virksomhedsliste til dropdown
@st.cache_data
def load_company_data():
    df = pd.read_csv("company_dropdown_list.csv")
    return df

df_lookup = load_company_data()

# 📌 Dropdown med virksomhedsnavne
valgt_selskab = st.selectbox("📊 Vælg virksomhed", df_lookup["DropdownOption"])
valgt_ticker = df_lookup[df_lookup["DropdownOption"] == valgt_selskab]["Ticker"].values[0]

købspris = st.number_input("💰 Din købspris (valgfri)", min_value=0.0, step=0.1, format="%.2f")

prompt = st.text_area("✏️ Hvad vil du gerne have GPT til at vurdere?",
                      "Er denne aktie undervurderet, og bør jeg sælge eller holde ud fra min købspris?")

st.caption("ℹ️ Brug tekstfeltet til at specificere din analyse – fx: 'Vurder langsigtet potentiale', "
           "'Vurder om den er undervurderet ift. intrinsic value', eller 'Hvordan klarer den sig mod konkurrenter?'")

# 📊 Datahentning
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

        vækstrate = 0.08
        diskonteringsrente = 0.10
        intrinsic_value = None
        if eps and isinstance(eps, (int, float)):
            intrinsic_value = round(eps * (1 + vækstrate) / (diskonteringsrente - vækstrate), 2)

        # Dummy moat score
        moat_score = 2 if roe and roe > 0.15 else 1 if roe and roe > 0.08 else 0

        return {
            "Ticker": ticker,
            "P/E": pe_ratio,
            "ROIC": roe,
            "Free Cash Flow": fcf,
            "Debt": gæld,
            "Current Price": pris,
            "Estimated Intrinsic Value (DCF)": intrinsic_value,
            "Currency": valuta,
            "Moat Score (0–2)": moat_score,
            "Stable?": "Yes" if fcf and fcf > 0 else "No"
        }
    except Exception as e:
        return {"Fejl": str(e)}

# 🚀 Analyseknap
if st.button("🚀 Find ud af om aktien er værd at eje"):
    if valgt_ticker:
        noegletal = hent_noegletal(valgt_ticker)
        st.subheader("📊 Nøgletal hentet fra Yahoo Finance")
        st.json(noegletal)

        fakta_tekst = "\n".join([f"{k}: {v}" for k, v in noegletal.items()])
        købspris_tekst = f"Brugerens købspris er: {købspris}" if købspris > 0 else "Ingen købspris angivet."

        messages = [
            {"role": "system", "content": (
                "Du er en professionel investeringsrådgiver, der arbejder ud fra Warren Buffetts principper. "
                "Brug de nøgletal, du har fået herunder – og henvis til dem i analysen, så brugeren får tillid til vurderingen. "
                "Kom også med en konklusion baseret på intrinsic value og brugerens købspris."
                f"\n\nNøgletal:\n{fakta_tekst}\n{købspris_tekst}")},
            {"role": "user", "content": f"Ticker: {valgt_ticker}\n{prompt}"}
        ]

        with st.spinner("GPT analyserer baseret på dine data..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.3,
                )
                st.success("✅ Analyse færdig")
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Fejl under GPT-analyse: {e}")
    else:
        st.warning("Du skal vælge en virksomhed.")

