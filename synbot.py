from synbot import SmartBudgetAdvisor
import re
import requests
import yfinance as yf
import streamlit as st
from cohere import ClientV2  # <-- Added Cohere import

class SynBot:
    def __init__(self, provider="openrouter", model=None):
        """
        provider: "openrouter" or "cohere"
        model: defaults to:
            - OpenRouter: google/gemma-3n-e2b-it:free
            - Cohere: command-a-03-2025
        """
        self.provider = provider.lower()
        self.model = model or (
            "google/gemma-3n-e2b-it:free" if self.provider == "openrouter" else "command-a-03-2025"
        )

        if self.provider == "openrouter":
            self.api_key = st.secrets.get("openrouter_api_key")
            self.base_url = "https://openrouter.ai/api/v1"
        elif self.provider == "cohere":
            self.api_key = st.secrets.get("cohere_api_key")
        else:
            raise ValueError("Unsupported provider. Use 'openrouter' or 'cohere'.")

    # --- Build Context ---
    def _format_financial_summary(self, df_exp, df_inc, analytics_data):
        parts = []
        # Expenses
        if df_exp is not None and not df_exp.empty:
            spent = df_exp["Amount"].sum()
            parts.append(f"Total spent ₹{spent:.2f} across {len(df_exp)} transactions.")
            try:
                top_cat = df_exp.groupby("Category")["Amount"].sum().idxmax()
                avg_exp = df_exp["Amount"].mean()
                cat_split = df_exp.groupby("Category")["Amount"].sum().to_dict()
                parts += [f"Top category: {top_cat}", f"Average expense: ₹{avg_exp:.2f}",
                          f"Category breakdown: {cat_split}"]
            except Exception:
                pass
        # Income
        if df_inc is not None and not df_inc.empty:
            earned = df_inc["Amount"].sum()
            avg_inc = df_inc["Amount"].mean()
            parts += [f"Total income: ₹{earned:.2f} from {len(df_inc)} sources.",
                      f"Average income: ₹{avg_inc:.2f}"]
            if df_exp is not None and not df_exp.empty:
                parts.append(f"Net balance: ₹{earned - df_exp['Amount'].sum():.2f}")
        # Analytics
        if analytics_data:
            trend = analytics_data.get("trend", 1)
            trend_status = "increasing" if trend > 1.1 else "stable" if trend > 0.9 else "decreasing"
            parts.append(f"Spending patterns: peak on {analytics_data.get('peak_day', 'weekdays')}, "
                         f"trend: {trend_status}, top category: {analytics_data.get('top_category', 'miscellaneous')}.")
        return " ".join(parts)

    # --- Live Price ---
    def _live_price(self, symbol):
        try:
            tk = yf.Ticker(symbol)
            df = tk.history(period="1d", interval="1m")
            if df.empty:
                return f"❌ *{symbol.upper()}*: no recent trades."
            last = df.iloc[-1]
            chg = (last.Close - last.Open) / last.Open * 100
            return f"📈 *{symbol.upper()}*\nPrice: **${last.Close:.2f}**\nChange: **{chg:+.2f}%**"
        except Exception as e:
            return f"⚠ *{symbol}*: {e}"

    # --- Main Answer ---
    def answer(self, question, df_exp=None, df_inc=None, analytics_data=None):
        q_clean = question.strip()
        symbol_match = re.search(r"\b([A-Z]{2,5})\b", q_clean.upper())
        if "price" in q_clean.lower() and symbol_match:
            return self._live_price(symbol_match.group(1))

        context = self._format_financial_summary(df_exp, df_inc, analytics_data)
        if not self.api_key:
            return f"🤖 API Key missing! Please add your {self.provider.title()} API key to Streamlit secrets."

        messages = [
            {"role": "system", "content": "You are SynBot, a financial AI coach. Provide clear, concise, friendly advice."},
            {"role": "user", "content": f"Question: {q_clean}\n\nUser's Financial Context: {context}"}
        ]

        if self.provider == "openrouter":
            return self._call_openrouter_api(messages)
        elif self.provider == "cohere":
            return self._call_cohere_stream(messages)

    # --- OpenRouter Call ---
    def _call_openrouter_api(self, messages):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://neurobux.streamlit.app/",
            "X-Title": "NeuroBux Finance Tracker"
        }
        try:
            r = requests.post(f"{self.base_url}/chat/completions", headers=headers, json={
                "model": self.model, "messages": messages,
                "max_tokens": 500, "temperature": 0.7, "top_p": 0.9
            }, timeout=30)
            errs = {401: "🔑 Authentication Failed!", 429: "⏳ Rate Limit!", 403: "🚫 Access Forbidden!"}
            if r.status_code in errs: return errs[r.status_code]
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"🤖 Error: {str(e)[:100]}"

    # --- Cohere Call with Streaming ---
    def _call_cohere_stream(self, messages):
        try:
            client = ClientV2(api_key=self.api_key)
            # Convert our list of dicts to Cohere's expected format
            cohere_msgs = [{"role": m["role"], "content": m["content"]} for m in messages]
            stream = client.chat_stream(model=self.model, messages=cohere_msgs, temperature=0.3)
            output = []
            for event in stream:
                if event.type == "content-delta":
                    output.append(event.delta.message.content.text)
            return "".join(output).strip()
        except Exception as e:
            return f"🤖 Cohere Error: {str(e)[:100]}"
