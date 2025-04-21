from yahooquery import search
import streamlit as st
import yfinance as yf

# Set USD to INR conversion rate
USD_TO_INR = 83.0

# Function to get the ticker symbol from a stock name
def get_ticker_from_name(name):
    result = search(name)
    if "quotes" in result and len(result["quotes"]) > 0:
        return result["quotes"][0]["symbol"]
    return None

# Function to fetch stock data using yfinance
def fetch_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="max")
    if hist.empty:
        return None
    creation_date = hist.index[0].date()
    initial_price = hist["Open"].iloc[0]
    current_price = hist["Close"].iloc[-1]
    owner = "Public/Institutional Investors"
    return {
        "creation_date": creation_date,
        "initial_price": initial_price,
        "current_price": current_price,
        "owner": owner,
        "history": hist
    }

# Function to provide buy recommendation based on short-term and long-term moving averages
def should_buy(stock_data):
    hist = stock_data["history"]
    short_ma = hist["Close"].rolling(window=20).mean()
    long_ma = hist["Close"].rolling(window=50).mean()
    return "✅ Recommendation: Buy" if short_ma.iloc[-1] > long_ma.iloc[-1] else "❌ Recommendation: Don't Buy"

# Function to dynamically update the input box border color
def update_input_box_border(valid):
    color = "#28a745" if valid else "#dc3545"  # Green for valid, red for invalid
    st.markdown(
        f"""
        <style>pytho 
        .stTextInput > div > input {{
            border: 2px solid {color};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# Streamlit UI setup
st.set_page_config(page_title="Stock Info", layout="centered")
st.title("📊 Stock Info & Recommendation App (USD ➝ INR)")

st.markdown("### Try typing names like: `Apple`, `Tesla`, `Microsoft`, `Google`, `Amazon`")

# Input field for company name
company_input = st.text_input("🔍 Enter Company Name:")

# If the user enters a company name
if company_input:
    with st.spinner("Finding ticker and fetching data..."):
        ticker = get_ticker_from_name(company_input)
        
        # Update input box color based on stock ticker validity
        if ticker:
            update_input_box_border(valid=True)  # Green if ticker found
            st.success(f"✅ Found Ticker: `{ticker}`")
            data = fetch_stock_data(ticker)
            if data:
                inr_initial = data["initial_price"] * USD_TO_INR
                inr_current = data["current_price"] * USD_TO_INR

                st.subheader(f"📄 Details for: {ticker}")
                st.write(f"**Creation Date:** {data['creation_date']}")
                st.write(f"**Initial Price:** ₹{inr_initial:.2f} (USD ${data['initial_price']:.2f})")
                st.write(f"**Current Price:** ₹{inr_current:.2f} (USD ${data['current_price']:.2f})")
                st.write(f"**Owner:** {data['owner']}")

                trend = "📈 Trending Up" if data["current_price"] > data["initial_price"] else "📉 Trending Down"
                st.markdown(f"### {trend}")

                recommendation = should_buy(data)
                st.markdown(f"### {recommendation}")

                st.line_chart(data["history"]["Close"])
            else:
                st.error("❌ Data fetch failed for the selected ticker.")
        else:
            update_input_box_border(valid=False)  # Red if no ticker found
            st.error("❌ No matching stock ticker found for the given name.")
