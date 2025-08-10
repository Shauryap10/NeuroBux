import re
import requests
import yfinance as yf
import streamlit as st

class SynBot:
def init(self):
    self.api_key = st.secrets.get("openrouter_api_key", None)
    self.base_url = "https://openrouter.ai/api/v1"

def _live_price(self, symbol):  
    try:  
        tk = yf.Ticker(symbol)  
        df = tk.history(period="1d", interval="1m")  
        if df.empty:  
            return f"❌ *{symbol.upper()}*: no recent trades."  
        last = df.iloc[-1]  
        chg = (last.Close - last.Open) / last.Open * 100  
        return f"📈 *{symbol.upper()}\nPrice: **${last.Close:.2f}\nChange: **{chg:+.2f}%*"  
    except Exception as e:  
        return f"⚠ *{symbol}*: {e}"  

def answer(self, question, df_exp=None, df_inc=None, analytics_data=None):  
    q = question.strip()  
    symbol_kw = re.search(r"\b([A-Z]{2,5})\b", q.upper())  
    if "price" in q.lower() and symbol_kw:  
        return self._live_price(symbol_kw.group(1))  

    # Build comprehensive context from user's financial data  
    ctx = ""  
    if df_exp is not None and not df_exp.empty:  
        spent = df_exp["Amount"].sum()  
        try:  
            top_category = df_exp.groupby("Category")["Amount"].sum().idxmax()  
            category_spending = df_exp.groupby("Category")["Amount"].sum().to_dict()  
            avg_expense = df_exp["Amount"].mean()  
            expense_count = len(df_exp)  
            ctx += f"Financial Summary: Total spent ₹{spent:.2f} across {expense_count} transactions. "  
            ctx += f"Top spending category: {top_category}. Average expense: ₹{avg_expense:.2f}. "  
            ctx += f"Category breakdown: {category_spending}. "  
        except Exception:  
            ctx += f"Total spent: ₹{spent:.2f}. "  

    if df_inc is not None and not df_inc.empty:  
        earned = df_inc["Amount"].sum()  
        avg_income = df_inc["Amount"].mean()  
        income_count = len(df_inc)  
        ctx += f"Total income: ₹{earned:.2f} from {income_count} sources. Average income: ₹{avg_income:.2f}. "  

        # Calculate net balance if both exist  
        if df_exp is not None and not df_exp.empty:  
            net_balance = earned - df_exp["Amount"].sum()  
            ctx += f"Net balance: ₹{net_balance:.2f}. "  

    # Add analytics context if available  
    if analytics_data:  
        patterns_context = f"Spending patterns: peak spending on {analytics_data.get('peak_day', 'weekdays')}, "  
        patterns_context += f"trend: {'increasing' if analytics_data.get('trend', 1) > 1.1 else 'stable' if analytics_data.get('trend', 1) > 0.9 else 'decreasing'}, "  
        patterns_context += f"primary category: {analytics_data.get('top_category', 'miscellaneous')}. "  
        ctx += patterns_context  

    # Enhanced system prompt for better financial advice  
    messages = [  
        {  
            "role": "system",   
            "content": """You are SynBot, a knowledgeable financial AI assistant for the NeuroBux finance tracker.   
            Your role is to provide helpful, practical financial advice based on the user's expense and income data.  
              
            Key responsibilities:  
            1. Analyze spending patterns and provide personalized budgeting advice  
            2. Offer money-saving tips and financial planning suggestions  
            3. Help users understand their financial habits and trends  
            4. Provide encouragement and motivation for financial goals  
            5. Answer questions about personal finance, investments, and money management  
              
            Communication style:  
            - Be friendly, supportive, and conversational  
            - Provide detailed, actionable advice with specific recommendations  
            - Use clear explanations that anyone can understand  
            - Include relevant examples when helpful  
            - Use emojis occasionally for engagement, but focus on valuable content  
            - Keep responses informative yet concise (2-4 sentences typically)  
              
            Financial expertise areas:  
            - Budgeting and expense tracking  
            - Saving strategies and emergency funds  
            - Debt management and reduction  
            - Investment basics and planning  
            - Financial goal setting and achievement  
              
            Always base your advice on the provided financial data when available."""  
        },  
        {"role": "user", "content": f"Question: {q}\n\nUser's Financial Context: {ctx}".strip()}  
    ]  

    if not self.api_key:  
        return "🤖 API Key missing! Please add your OpenRouter API key to Streamlit secrets to enable the AI coach."  

    try:  
        # Corrected headers for OpenRouter API  
        headers = {  
            "Authorization": f"Bearer {self.api_key}",  
            "Content-Type": "application/json",  
            "HTTP-Referer": "https://neurobux-qvmhjhksxa8xchafukx9ng.streamlit.app/",  
            "X-Title": "NeuroBux Finance Tracker"  
        }  

        # Use the correct endpoint  
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

        # Better error handling  
        if response.status_code == 401:  
            return "🔑 *Authentication Failed!* Your OpenRouter API key is invalid or expired. Please check your OpenRouter account and update the key in Streamlit secrets."  
        elif response.status_code == 429:  
            return "⏳ *Rate Limit Exceeded!* Please wait a moment before making another request."  
        elif response.status_code == 403:  
            return "🚫 *Access Forbidden!* Your API key may not have permission to access this model."  

        response.raise_for_status()  
        return response.json()["choices"][0]["message"]["content"].strip()  

    except requests.exceptions.ConnectionError:  
        return "🌐 *Connection Error!* Please check your internet connection and try again."  
    except requests.exceptions.Timeout:  
        return "⏰ *Request Timeout!* The AI service is taking too long to respond. Please try again."  
    except requests.exceptions.HTTPError as e:  
        return f"🤖 *API Error!* HTTP {response.status_code}: {response.text[:100]}..."  
    except KeyError:  
        return "🤖 *Invalid Response!* The AI service returned an unexpected response format."  
    except Exception as e:  
        return f"🤖 *Unexpected Error!* {str(e)[:100]}... Please try again or contact support."

class SmartBudgetAdvisor:
def init(self, analyzer):
self.analyzer = analyzer

def generate_budget_insights(self, user_data, spending_patterns):  
    """Generate personalized budget recommendations"""  
    insights = []  

    # Analyze spending velocity  
    if spending_patterns['spending_trend'] > 1.2:  
        insights.append({  
            'type': 'warning',  
            'message': f"📈 Your spending increased by {(spending_patterns['spending_trend']-1)*100:.1f}% recently",  
            'suggestion': "Consider reviewing your recent purchases and setting daily spending limits for your top categories. Try implementing the 24-hour rule for non-essential purchases over ₹500."  
        })  
    elif spending_patterns['spending_trend'] < 0.8:  
        insights.append({  
            'type': 'positive',  
            'message': f"📉 Great job! Your spending decreased by {(1-spending_patterns['spending_trend'])*100:.1f}% recently",  
            'suggestion': "You're on the right track! Consider putting the money you've saved into an emergency fund or investment account."  
        })  

    # Category-specific insights  
    top_category = spending_patterns['top_category']  
    if top_category != 'N/A':  
        insights.append({  
            'type': 'insight',  
            'message': f"💡 Your highest spending category is {top_category}",  
            'suggestion': f"For {top_category}, try the envelope budgeting method: set a specific monthly limit and track it weekly. Look for alternatives or bulk buying opportunities to reduce costs."  
        })  

    # Unusual spending alerts  
    if spending_patterns['unusual_expenses']:  
        unusual_count = len(spending_patterns['unusual_expenses'])  
        insights.append({  
            'type': 'alert',  
            'message': f"⚠ Found {unusual_count} unusual expense{'s' if unusual_count > 1 else ''} in your recent transactions",  
            'suggestion': "Review these transactions to ensure they're accurate. If legitimate, consider if they represent one-time expenses or if you need to adjust your budget categories."  
        })  

    return insights

Can we simply this code and rewrite reducing complexity and without cutting any feature
