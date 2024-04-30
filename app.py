import json
import time

import hydralit_components as hc
import pandas as pd
import plotly.express as px
import snowflake.connector as sf
import streamlit as st
import yfinance as yf
from babel.numbers import format_currency
from openpyxl import Workbook, load_workbook
from streamlit_lottie import st_lottie
from yahooquery import Ticker
import requests
from bs4 import BeautifulSoup

from streamlit_authentication import authenticate
from functions import *


def filter_companies(pair):
    print(pair)
    key, value = pair
    if value is None:
        return False
    return True


def get_company_list():
    f = open("companies.json", "r")
    companies = json.load(f)
    # print(companies)

    return companies


# Function to fetch company data from Yahoo Finance


def get_company_data(ticker, start_date, end_date):
    try:
        company = yf.Ticker(ticker)
        data = company.history(start=start_date, end=end_date)
        return data
    except:
        return None


def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


lottie_analysis = load_lottiefile("lottiefiles/analysis.json")
lottie_hello = load_lottiefile("lottiefiles/hello.json")

st.set_page_config(
    page_title="FA",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded",
)

hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
header{visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# ---Side-Bar----

with st.sidebar:
    st_lottie(lottie_hello, loop=True, key=None, height=320, width=320)
    st.write(
        """
    Hey 👋🏻there. I aDeborah Fuyiwa, a final year forensic auditing student at the Harare Institute of Technology. I am passionate about forensic auditing and data analysis. I am currently working on a project that involves the analysis of financial statements using the Beneish Model and Dechow F Score model. I am excited to share my project with you. Feel free to reach out to me on [LinkedIn](https://www.linkedin.com/in/deborah-fuyiwa-8b7b2b1b7/).
    """
    )
    st.write("---")
    st.write("#### About📍")
    st.write(
        """
        This web app is designed to analyze the quality of financial statements using the Beneish Model. The Beneish Model is a statistical model that uses financial ratios to detect earnings manipulation. The model uses eight financial ratios to determine the likelihood of earnings manipulation. The Dechow F-Score is also used to analyze the quality of financial statements. The Dechow F-Score uses four financial ratios to determine the likelihood of earnings manipulation. The web app uses data from Yahoo Finance to calculate the financial ratios and the Beneish M-Score. The web app also calculates the Dechow F-Score and its components. The web app is designed to help users analyze the quality of financial statements and detect earnings manipulation. 
    """
    )

pd.set_option("mode.chained_assignment", None)


st.title(
    "Analyzing the Quality of Financial Statements using Beneish Model and Dechow F Score"
)


# Sidebar to select or enter a company
st.sidebar.title("Select a Company")
companies = get_company_list()
ticker_lookup = {name: ticker for ticker, name in companies.items()}

selected_company = st.selectbox("Select a company", ticker_lookup)


if selected_company:
    ticker = ticker_lookup[selected_company]
    comp = yf.Ticker(ticker)

    st.write(f" #### Company Name - {selected_company}\n #### Symbol - {ticker}")

    with hc.HyLoader("Now doing loading", hc.Loaders.standard_loaders, index=[3, 0, 5]):
        time.sleep(5)

    incomeStatement = comp.income_stmt
    balanceSheet = comp.balance_sheet
    cashFlow = comp.cashflow

    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)

    if incomeStatement.empty or balanceSheet.empty or cashFlow.empty:
        st.error("No data available for the selected company.")
        st.stop()

    # Income Statement
    incomeStatement = incomeStatement[incomeStatement.columns[0:2]]
    incomeStatement.columns = ["2022", "2021"]
    incomeStatement = incomeStatement.fillna(0).astype(float)

    # Balance Sheet
    balanceSheet = balanceSheet[balanceSheet.columns[0:2]]
    balanceSheet.columns = ["2022", "2021"]
    balanceSheet = balanceSheet.fillna(0).astype(float)

    # Cash Flow
    cashFlow = cashFlow[cashFlow.columns[0:2]]
    cashFlow.columns = ["2022", "2021"]
    cashFlow.dropna()
    # print(balanceSheet)

    if (
        "Gross Profit" not in incomeStatement.index
        or "Current Liabilities" not in balanceSheet.index
        or "Current Assets" not in balanceSheet.index
    ):
        st.error("No data available for the selected company.")
        st.stop()

    # COGS = Revenue  - GrossProfit
    cogs22 = (
        incomeStatement.at["Total Revenue", "2022"]
        - incomeStatement.at["Gross Profit", "2022"]
    )
    cogs21 = (
        incomeStatement.at["Total Revenue", "2021"]
        - incomeStatement.at["Gross Profit", "2021"]
    )

    # COGS = pd.Series(data={'2022': cogs22, '2021': cogs21},
    #                  name='Cost of Goods Sold')
    incomeStatement.loc["Cost of Goods Sold"] = [cogs22, cogs21]

    # long term Debt

    if "Long Term Debt And Capital Lease Obligation" not in balanceSheet.index:
        ld22 = (
            balanceSheet.at["Total Liab", "2022"]
            - balanceSheet.at["Total Current Liabilities", "2022"]
            - balanceSheet.at["Other Liab", "2022"]
        )
        ld21 = (
            balanceSheet.at["Total Liab", "2021"]
            - balanceSheet.at["Total Current Liabilities", "2021"]
            - balanceSheet.at["Other Liab", "2021"]
        )
        balanceSheet.loc["Long Term Debt"] = [ld22, ld21]

    if "Long Term Investments" not in balanceSheet.index:
        li22 = balanceSheet.at["Common Stock", "2022"]
        li21 = balanceSheet.at["Common Stock", "2021"]

        balanceSheet.loc["Long Term Investments"] = [li22, li21]

    if "Net PPE" not in balanceSheet.index:
        pp22 = balanceSheet.at["Machinery Furniture Equipment", "2022"]
        pp21 = balanceSheet.at["Machinery Furniture Equipment", "2021"]

        balanceSheet.loc["Net PPE"] = [pp22, pp21]

    # Extracting the statements

    df = incomeStatement.loc[
        [
            "Total Revenue",
            "Cost of Goods Sold",
            "Selling General And Administration",
            "Net Income Continuous Operations",
        ]
    ]

    df2 = balanceSheet.loc[
        [
            "Receivables",
            "Current Assets",
            "Net PPE",
            "Long Term Investments",
            "Total Assets",
            "Current Liabilities",
            "Long Term Debt And Capital Lease Obligation",
        ]
    ]
    df3 = cashFlow.loc[["Depreciation And Amortization", "Operating Cash Flow"]]

    data = pd.concat([df, df2, df3])
    data = data.reindex(
        [
            "Total Revenue",
            "Cost of Goods Sold",
            "Selling General And Administration",
            "Depreciation And Amortization",
            "Net Income Continuous Operations",
            "Receivables",
            "Current Assets",
            "Net PPE",
            "Long Term Investments",
            "Total Assets",
            "Current Liabilities",
            "Long Term Debt And Capital Lease Obligation",
            "Operating Cash Flow",
        ]
    )
    data.index = [
        "Revenue",
        "Cost of Goods Sold",
        "Selling, General & Admin.Expense",
        "Depreciation",
        "Net Income from Continuing Operations",
        "Accounts Receivables",
        "Current Assets",
        "Property, Plant & Equipment",
        "Securities",
        "Total Assets",
        "Current Liabilities",
        "Total Long-term Debt",
        "Cash Flow from Operations",
    ]

    data.fillna(0, inplace=True)

    data1 = data.copy()
    data1["2022"] = data1["2022"].apply(
        lambda x: format_currency(x, format=None, currency="USD", locale="en_US")
    )
    data1["2021"] = data1["2021"].apply(
        lambda x: format_currency(x, format=None, currency="USD", locale="en_US")
    )

    # Data Particulars

    st.subheader("Data Particulars")
    st.dataframe(data1)

    # for 1 (index=5) from the standard loader group
    with hc.HyLoader("Now doing loading", hc.Loaders.standard_loaders, index=5):
        time.sleep(5)

    data2 = {
        "Financial Ratios Indexes": [
            "Day Sales in Receivables Index(DSRI)",
            "Gross Margin Index(GMI)",
            "Asset Quality Index(AQI)",
            "Sales Growth Index(SGI)",
            "Depreciation Index(DEPI)",
            "Selling, General, & Admin. Expenses Index(SGAI)",
            "Leverage Index(LVGI)",
            "Total Accruals to Total Assets(TATA)",
        ],
        "Index": [
            DSRI(data),
            GMI(data),
            AQI(data),
            SGI(data),
            DEPI(data),
            SGAI(data),
            LVGI(data),
            TATA(data),
        ],
    }

    ratios = pd.DataFrame(data2)
    ratios.set_index("Financial Ratios Indexes", inplace=True, drop=True)

    # Financial Ratios

    st.write(" ### Financial Ratio Indexes")
    st.dataframe(ratios)
    # print(type(ratios["Index"]))
    temp_ratios = ratios.copy()
    temp_ratios.index.name = "Ratios"
    temp_ratios["Ratios"] = temp_ratios.index
    temp_ratios = temp_ratios.reset_index(drop=True)
    temp_ratios.columns = ["Ratios", "Index"]

    # The Line Chart using Plotly
    fig = px.line(
        temp_ratios,  # Data Frame
        x="Index",  # Columns from the data frame
        y="Ratios",
        title="Financial Ratio Indexes",
    )
    fig.update_traces(line_color="blue")

    with st.container():
        st.plotly_chart(fig)

    # Beneish M Score
    m_score = BeneishMScore(
        DSRI(data),
        GMI(data),
        AQI(data),
        SGI(data),
        DEPI(data),
        SGAI(data),
        LVGI(data),
        TATA(data),
    )
    if m_score < -2.22:
        res = "##### Company is not likely to manipulate their earnings"
        st.write(f"##### M- Score = {round(m_score,2)}")
        st.write(f"{res}")
        # print(res)
    else:
        res = " ##### Company is not likely to manipulate their earnings"
        st.write(f"##### M- Score = {round(m_score,2)}")
        st.write(f"{res}")

    f_score = calculate_dechow_f_score(data, "2021", "2022")
    start_year = "2021"
    end_year = "2022"

    rsst = calculate_rsst(data, start_year, end_year)
    delta_rec = calculate_delta_rec(data, start_year, end_year)
    delta_inv = calculate_delta_inv(data, start_year, end_year)
    soft_assets = calculate_soft_assets(data, end_year)
    delta_cash_sales = calculate_delta_cash_sales(data, start_year, end_year)
    delta_roa = calculate_delta_roa(data, start_year, end_year)
    issue_indicator = calculate_issue_indicator(data, start_year, end_year)

    f_score_data = {
        "F-Score Components": [
            "RSST Accruals",
            "Change in Receivables",
            "Change in Inventory",
            "Soft Assets",
            "Change in Cash Sales",
            "Change in ROA",
            "Issue Indicator",
        ],
        "Values": [
            rsst,
            delta_rec,
            delta_inv,
            soft_assets,
            delta_cash_sales,
            delta_roa,
            issue_indicator,
        ],
    }

    # Create the DataFrame
    f_score_df = pd.DataFrame(f_score_data)
    f_score_df.set_index("F-Score Components", inplace=True, drop=True)

    # Display the Dechow F-Score and its components in Streamlit
    with st.container():
        st.header("Dechow F-Score Analysis")
        st.write(
            "This section displays the Dechow F-Score and its components for the period 2021 to 2022."
        )
        st.dataframe(f_score_df)

        # Prepare the data for the line chart
        temp_f_score_df = f_score_df.copy()
        temp_f_score_df.index.name = "Components"
        temp_f_score_df["Components"] = temp_f_score_df.index
        temp_f_score_df = temp_f_score_df.reset_index(drop=True)
        temp_f_score_df.columns = ["Components", "Values"]

        # The Line Chart using Plotly
        fig = px.line(
            temp_f_score_df,  # Data Frame
            x="Components",  # Columns from the data frame
            y="Values",
            title="Dechow F-Score Components",
        )
        fig.update_traces(line_color="blue")
        st.plotly_chart(fig)

    st.write(f"##### F - Score = {round(f_score, 2)}")
