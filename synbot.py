import re
import yfinance as yf
import streamlit as st
from cohere import ClientV2  # Ensure cohere is installed: pip install cohere

class SynBot:
    def __init__(self, model="command-a-03-2025"):
        """
        Uses Cohere API for financial AI coaching.
        model: Cohere model name (default: command-a-03-2025)
        """
        self.model = model
        self.api_key = st.secrets.get("cohere_api_key")
        if not self.api_key:
            raise ValueError("🤖 API Key missing! Please add 'cohere_api_key' to Streamlit secrets.")

    def _format_financial_summary(self, df_exp, df_inc, analytics_data):
        parts = []

        if df_exp is not None and not df_exp.empty:
            spent = df_exp["Amount"].sum()
            parts.append(f"Total spent ₹{spent:.2f} across {len(df_exp)} transactions.")
            try:
                top_cat = df_exp.groupby("Category")["Amount"].sum().idxmax()
                avg_exp = df_exp["Amount"].mean()
                category_split = df_exp.groupby("Category")["Amount"].sum().to_dict()
                parts += [
                    f"Top category: {top_cat}",
                    f"Average expense: ₹{avg_exp:.2f}",
                    f"Category breakdown: {category_split}"
                ]
            except Exception:
                pass

        if df_inc is not None and not df_inc.empty:
            earned = df_inc["Amount"].sum()
            avg_inc = df_inc["Amount"].mean()
            parts += [
                f"Total income: ₹{earned:.2f} from {len(df_inc)} sources.",
                f"Average income: ₹{avg_inc:.2f}"
            ]
            if df_exp is not None and not df_exp.empty:
                parts.append(f"Net balance: ₹{earned - df_exp['Amount'].sum():.2f}")

        if analytics_data:
            trend = analytics_data.get("trend", 1)
            trend_status = "increasing" if trend > 1.1 else "stable" if trend > 0.9 else "decreasing"
            parts.append(
                f"Spending patterns: peak on {analytics_data.get('peak_day', 'weekdays')}, "
                f"trend: {trend_status}, top category: {analytics_data.get('top_category', 'miscellaneous')}."
            )

        return " ".join(parts)

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

    def answer(self, question, df_exp=None, df_inc=None, analytics_data=None):
        q_clean = question.strip()
        symbol_match = re.search(r"\b([A-Z]{2,5})\b", q_clean.upper())
        if "price" in q_clean.lower() and symbol_match:
            return self._live_price(symbol_match.group(1))

        context = self._format_financial_summary(df_exp, df_inc, analytics_data)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are NeuroBot, a knowledgeable financial AI assistant for NeuroBux. "
                    "Analyze spending patterns, give budgeting & saving tips, investment basics, "
                    "and motivational advice. Be friendly, concise, and occasionally use emojis."
                )
            },
            {
                "role": "user",
                "content": f"Question: {q_clean}\n\nUser's Financial Context: {context}"
            }
        ]
        return self._call_cohere_stream(messages)

    def _call_cohere_stream(self, messages):
        try:
            client = ClientV2(api_key=self.api_key)
            cohere_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
            stream = client.chat_stream(model=self.model, messages=cohere_messages, temperature=0.3)
            output = []
            for event in stream:
                if event.type == "content-delta":
                    output.append(event.delta.message.content.text)
            return "".join(output).strip()
        except Exception as e:
            return f"🤖 Cohere Error: {str(e)[:100]}"

class SmartBudgetAdvisor:
    def __init__(self, analyzer=None):
        self.analyzer = analyzer

    def generate_budget_insights(self, user_data, patterns):
        insights = []

        trend = patterns.get('spending_trend', 1)
        if trend > 1.2:
            insights.append({
                'type': 'warning',
                'message': f"📈 Spending increased by {(trend - 1) * 100:.1f}%",
                'suggestion': "Review purchases, set daily limits, and try the 24-hour rule for non-essentials over ₹500."
            })
        elif trend < 0.8:
            insights.append({
                'type': 'positive',
                'message': f"📉 Spending decreased by {(1 - trend) * 100:.1f}%",
                'suggestion': "Great job! Allocate savings into an emergency fund or investments."
            })

        top_cat = patterns.get('top_category', 'N/A')
        if top_cat != 'N/A':
            insights.append({
                'type': 'insight',
                'message': f"💡 Highest spending category: {top_cat}",
                'suggestion': f"Use envelope budgeting for {top_cat}, set monthly limits, and review weekly."
            })

        unusual = patterns.get('unusual_expenses', [])
        if unusual:
            count = len(unusual)
            insights.append({
                'type': 'alert',
                'message': f"⚠ {count} unusual expense{'s' if count > 1 else ''} detected",
                'suggestion': "Review these transactions; decide if one-time or require budget adjustments."
            })

        return insights
