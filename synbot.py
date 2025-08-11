import re
import requests
import yfinance as yf
import streamlit as st

class SynBot:
    def __init__(self):
        self.api_key = st.secrets.get("openrouter_api_key")
        self.base_url = "https://openrouter.ai/api/v1"

    # --- Utility Methods ---
    def _format_financial_summary(self, df_exp, df_inc, analytics_data):
        """Builds user financial context string"""
        ctx = []

        # Expenses Summary
        if df_exp is not None and not df_exp.empty:
            spent = df_exp["Amount"].sum()
            ctx.append(f"Total spent ₹{spent:.2f} across {len(df_exp)} transactions.")
            try:
                top_category = df_exp.groupby("Category")["Amount"].sum().idxmax()
                avg_expense = df_exp["Amount"].mean()
                category_spending = df_exp.groupby("Category")["Amount"].sum().to_dict()
                ctx.append(f"Top category: {top_category}")
                ctx.append(f"Average expense: ₹{avg_expense:.2f}")
                ctx.append(f"Category breakdown: {category_spending}")
            except Exception:
                pass

        # Income Summary
        if df_inc is not None and not df_inc.empty:
            earned = df_inc["Amount"].sum()
            avg_income = df_inc["Amount"].mean()
            ctx.append(f"Total income: ₹{earned:.2f} from {len(df_inc)} sources.")
            ctx.append(f"Average income: ₹{avg_income:.2f}")

            # Net Balance
            if df_exp is not None and not df_exp.empty:
                net_balance = earned - df_exp["Amount"].sum()
                ctx.append(f"Net balance: ₹{net_balance:.2f}")

        # Analytics Summary
        if analytics_data:
            trend_value = analytics_data.get("trend", 1)
            trend_status = "increasing" if trend_value > 1.1 else "stable" if trend_value > 0.9 else "decreasing"
            ctx.append(f"Spending patterns: peak on {analytics_data.get('peak_day', 'weekdays')}, "
                       f"trend: {trend_status}, top category: {analytics_data.get('top_category', 'miscellaneous')}.")

        return " ".join(ctx)

    def _live_price(self, symbol):
        """Fetch live stock/crypto price"""
        try:
            tk = yf.Ticker(symbol)
            df = tk.history(period="1d", interval="1m")
            if df.empty:
                return f"❌ *{symbol.upper()}*: no recent trades."
            last = df.iloc[-1]
            change_pct = (last.Close - last.Open) / last.Open * 100
            return f"📈 *{symbol.upper()}*\nPrice: **${last.Close:.2f}**\nChange: **{change_pct:+.2f}%**"
        except Exception as e:
            return f"⚠ *{symbol}*: {e}"

    # --- Main Method ---
    def answer(self, question, df_exp=None, df_inc=None, analytics_data=None):
        """Answer user queries; fetch price or AI financial advice"""
        question_clean = question.strip()
        symbol_match = re.search(r"\b([A-Z]{2,5})\b", question_clean.upper())

        # If user asks for price
        if "price" in question_clean.lower() and symbol_match:
            return self._live_price(symbol_match.group(1))

        # Build user financial context
        context = self._format_financial_summary(df_exp, df_inc, analytics_data)

        # Missing API Key
        if not self.api_key:
            return "🤖 API Key missing! Please add your OpenRouter API key in Streamlit secrets."

        # System + User Messages
        messages = [
            {
                "role": "system",
                "content": (
                    "You are SynBot, a knowledgeable financial AI assistant for NeuroBux. "
                    "Analyze spending patterns, give budgeting advice, investment tips, and goal motivation. "
                    "Be friendly, concise, and clear with occasional emojis."
                )
            },
            {
                "role": "user",
                "content": f"Question: {question_clean}\n\nUser's Financial Context: {context}"
            }
        ]

        return self._call_openrouter_api(messages)

    # --- API Call Helper ---
    def _call_openrouter_api(self, messages):
        """Send chat request to OpenRouter API and handle errors"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://neurobux-qvmhjhksxa8xchafukx9ng.streamlit.app/",
            "X-Title": "NeuroBux Finance Tracker"
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": "openai/gpt-3.5-turbo",
                    "messages": messages,
                    "max_tokens": 500,
                    "temperature": 0.7,
                    "top_p": 0.9
                },
                timeout=30
            )

            error_msgs = {
                401: "🔑 Authentication Failed! Check your API key.",
                429: "⏳ Rate Limit Exceeded! Try again later.",
                403: "🚫 Access Forbidden! Model permission issue."
            }
            if response.status_code in error_msgs:
                return error_msgs[response.status_code]

            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()

        except requests.exceptions.Timeout:
            return "⏰ Request Timeout! Please try again."
        except requests.exceptions.ConnectionError:
            return "🌐 Connection Error! Check internet."
        except requests.exceptions.HTTPError as e:
            return f"🤖 API Error! HTTP {response.status_code}: {response.text[:100]}..."
        except (KeyError, IndexError):
            return "🤖 Invalid Response Format!"
        except Exception as e:
            return f"🤖 Unexpected Error: {str(e)[:100]}..."

# --- Smart Budget Advisor ---
class SmartBudgetAdvisor:
    def __init__(self, analyzer):
        self.analyzer = analyzer

    def generate_budget_insights(self, user_data, patterns):
        """Generate personalized budget recommendations"""
        insights = []

        # Spending trend check
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
                'suggestion': "Great job! Allocate savings into emergency fund or investments."
            })

        # Top category advice
        top_category = patterns.get('top_category', 'N/A')
        if top_category != 'N/A':
            insights.append({
                'type': 'insight',
                'message': f"💡 Highest spending category: {top_category}",
                'suggestion': f"Use envelope budgeting for {top_category}, set monthly limits, and review weekly."
            })

        # Unusual expenses
        unusual = patterns.get('unusual_expenses', [])
        if unusual:
            count = len(unusual)
            insights.append({
                'type': 'alert',
                'message': f"⚠ {count} unusual expense{'s' if count > 1 else ''} detected",
                'suggestion': "Review these transactions; decide if one-time or require budget adjustments."
            })

        return insights
