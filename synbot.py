import re
import requests
import yfinance as yf
import streamlit as st

# ========================
#   SynBot: AI + Finance
# ========================
class SynBot:
    BASE_URL = "https://openrouter.ai/api/v1"
    MODEL ="deepseek/deepseek-r1-0528-qwen3-8b:free"

    def __init__(self):
        self.api_key = st.secrets.get("openrouter_api_key")

    # ---------- Utilities ----------
    def _handle_api_error(self, response):
        status_messages = {
            401: "🔑 Authentication Failed! Check your OpenRouter API key.",
            429: "⏳ Rate Limit Exceeded! Please wait before retrying.",
            403: "🚫 Access Forbidden! Your API key may lack permissions."
        }
        if response.status_code in status_messages:
            return status_messages[response.status_code]
        return f"🤖 API Error! HTTP {response.status_code}: {response.text[:100]}..."

    # ---------- Stock Price ----------
    def _live_price(self, symbol):
        try:
            data = yf.Ticker(symbol).history(period="1d", interval="1m")
            if data.empty:
                return f"❌ **{symbol.upper()}**: no recent trades."

            last = data.iloc[-1]
            change = (last.Close - last.Open) / last.Open * 100
            return f"📈 **{symbol.upper()}**\nPrice: **${last.Close:.2f}**\nChange: **{change:+.2f}%**"

        except Exception as e:
            return f"⚠️ **{symbol}**: {e}"

    # ---------- Context Builder ----------
    def _build_context(self, df_exp, df_inc, analytics_data):
        context = ""

        # Expenses
        if df_exp is not None and not df_exp.empty:
            total_spent = df_exp["Amount"].sum()
            context += f"Financial Summary: Total spent ₹{total_spent:.2f} across {len(df_exp)} transactions. "
            try:
                top_cat = df_exp.groupby("Category")["Amount"].sum().idxmax()
                avg_exp = df_exp["Amount"].mean()
                breakdown = df_exp.groupby("Category")["Amount"].sum().to_dict()
                context += f"Top category: {top_cat}. Avg expense: ₹{avg_exp:.2f}. Breakdown: {breakdown}. "
            except Exception:
                pass

        # Income
        if df_inc is not None and not df_inc.empty:
            total_income = df_inc["Amount"].sum()
            avg_income = df_inc["Amount"].mean()
            context += f"Total income: ₹{total_income:.2f} from {len(df_inc)} sources. Avg income: ₹{avg_income:.2f}. "

            if df_exp is not None and not df_exp.empty:
                net_balance = total_income - df_exp["Amount"].sum()
                context += f"Net balance: ₹{net_balance:.2f}. "

        # Analytics
        if analytics_data:
            trend = analytics_data.get("trend", 1)
            trend_label = "increasing" if trend > 1.1 else "stable" if trend > 0.9 else "decreasing"
            context += (
                f"Spending patterns: peak spending on {analytics_data.get('peak_day', 'weekdays')}, "
                f"trend: {trend_label}, primary category: {analytics_data.get('top_category', 'miscellaneous')}. "
            )

        return context

    # ---------- AI Query ----------
    def _query_ai(self, question, context):
        if not self.api_key:
            return "🤖 API Key missing! Add your OpenRouter API key in Streamlit secrets."

        payload = {
            "model": self.MODEL,
            "messages": [
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": f"Question: {question}\n\nUser's Financial Context: {context}"}
            ],
            "max_tokens": 500,
            "temperature": 0.7,
            "top_p": 0.9
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://neurobux-qvmhjhksxa8xchafukx9ng.streamlit.app/",
            "X-Title": "NeuroBux Finance Tracker"
        }

        try:
            resp = requests.post(f"{self.BASE_URL}/chat/completions", headers=headers, json=payload, timeout=30)
            if resp.status_code != 200:
                return self._handle_api_error(resp)

            return resp.json()["choices"][0]["message"]["content"].strip()

        except requests.exceptions.ConnectionError:
            return "🌐 Connection Error! Please check your internet."
        except requests.exceptions.Timeout:
            return "⏰ Request Timeout! Please try again."
        except KeyError:
            return "🤖 Invalid Response! Unexpected format."
        except Exception as e:
            return f"🤖 Unexpected Error! {str(e)[:100]}..."

    def _system_prompt(self):
        return (
            "You are SynBot, a friendly, practical financial assistant for NeuroBux.\n"
            "Provide detailed, actionable budgeting advice, money-saving tips, and clear explanations.\n"
            "Base advice on provided financial data. Use emojis occasionally for engagement."
        )

    # ---------- Main Answer ----------
    def answer(self, question, df_exp=None, df_inc=None, analytics_data=None):
        question = question.strip()
        match = re.search(r"\b([A-Z]{2,5})\b", question.upper())

        if "price" in question.lower() and match:
            return self._live_price(match.group(1))

        context = self._build_context(df_exp, df_inc, analytics_data)
        return self._query_ai(question, context)


# ================================
#   SmartBudgetAdvisor: Insights
# ================================
class SmartBudgetAdvisor:
    def __init__(self, analyzer):
        self.analyzer = analyzer

    def generate_budget_insights(self, user_data, patterns):
        insights = []

        # Spending trend
        trend = patterns['spending_trend']
        if trend > 1.2:
            insights.append(self._warning(f"📈 Your spending increased by {(trend-1)*100:.1f}% recently",
                                          "Review purchases, set daily limits, and apply the 24-hour rule for items over ₹500."))
        elif trend < 0.8:
            insights.append(self._positive(f"📉 Great job! Spending decreased by {(1-trend)*100:.1f}%",
                                           "Redirect savings to your emergency fund or investments."))

        # Top category
        if patterns['top_category'] != 'N/A':
            cat = patterns['top_category']
            insights.append(self._insight(f"💡 Highest spending category: {cat}",
                                          f"Use envelope budgeting for {cat}, set monthly limits, and track weekly."))

        # Unusual expenses
        if patterns['unusual_expenses']:
            count = len(patterns['unusual_expenses'])
            insights.append(self._alert(f"⚠️ {count} unusual expense{'s' if count > 1 else ''} detected",
                                        "Verify transactions and adjust budget if they are recurring."))

        return insights

    # ---------- Insight helpers ----------
    def _warning(self, msg, suggestion): return {'type': 'warning', 'message': msg, 'suggestion': suggestion}
    def _positive(self, msg, suggestion): return {'type': 'positive', 'message': msg, 'suggestion': suggestion}
    def _insight(self, msg, suggestion): return {'type': 'insight', 'message': msg, 'suggestion': suggestion}
    def _alert(self, msg, suggestion): return {'type': 'alert', 'message': msg, 'suggestion': suggestion}
