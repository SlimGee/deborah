import numpy as np


def DSRI(df):
    return (df.at["Accounts Receivables", "2022"] / df.at["Revenue", "2022"]) / (
        df.at["Accounts Receivables", "2021"] / df.at["Revenue", "2021"]
    )


def GMI(df):
    return (
        (df.at["Revenue", "2021"] - df.at["Cost of Goods Sold", "2021"])
        / df.at["Revenue", "2021"]
    ) / (
        (df.at["Revenue", "2022"] - df.at["Cost of Goods Sold", "2022"])
        / df.at["Revenue", "2022"]
    )


def AQI(df):
    AQI_t1 = (
        1
        - (
            df.at["Current Assets", "2022"]
            + df.at["Property, Plant & Equipment", "2022"]
            + df.at["Securities", "2022"]
        )
    ) / df.at["Total Assets", "2022"]
    AQI_t2 = (
        1
        - (
            df.at["Current Assets", "2021"]
            + df.at["Property, Plant & Equipment", "2021"]
            + df.at["Securities", "2021"]
        )
    ) / df.at["Total Assets", "2021"]
    return AQI_t1 / AQI_t2


def SGI(df):
    return df.at["Revenue", "2022"] / df.at["Revenue", "2021"]


def DEPI(df):
    DEPI_t1 = df.at["Depreciation", "2021"] / (
        df.at["Depreciation", "2021"] + df.at["Property, Plant & Equipment", "2021"]
    )
    DEPI_t2 = df.at["Depreciation", "2022"] / (
        df.at["Depreciation", "2022"] + df.at["Property, Plant & Equipment", "2022"]
    )
    return DEPI_t1 / DEPI_t2


def SGAI(df):
    return (
        df.at["Selling, General & Admin.Expense", "2022"] / df.at["Revenue", "2022"]
    ) / (df.at["Selling, General & Admin.Expense", "2021"] / df.at["Revenue", "2021"])


def LVGI(df):
    return (
        (df.at["Current Liabilities", "2022"] + df.at["Total Long-term Debt", "2022"])
        / df.at["Total Assets", "2022"]
    ) / (
        (df.at["Current Liabilities", "2021"] + df.at["Total Long-term Debt", "2021"])
        / df.at["Total Assets", "2021"]
    )


def TATA(df):
    return (
        df.at["Net Income from Continuing Operations", "2022"]
        - df.at["Cash Flow from Operations", "2022"]
    ) / df.at["Total Assets", "2022"]


def BeneishMScore(dsri, gmi, aqi, sgi, depi, sgai, lvgi, tata):
    return (
        -4.84
        + 0.92 * dsri
        + 0.528 * gmi
        + 0.404 * aqi
        + 0.892 * sgi
        + 0.115 * depi
        - 0.172 * sgai
        + 4.679 * tata
        - 0.327 * lvgi
    )


# Calculate the components of the Dechow F-Score
def calculate_rsst(data, start_year, end_year):
    delta_wc = (
        data.loc["Current Assets", end_year] - data.loc["Current Assets", start_year]
    ) - (
        data.loc["Current Liabilities", end_year]
        - data.loc["Current Liabilities", start_year]
    )
    delta_nco = (
        data.loc["Depreciation", end_year] - data.loc["Depreciation", start_year]
    )
    delta_fin = 0  # Assuming no change in financial assets
    avg_total_assets = (
        data.loc["Total Assets", end_year] + data.loc["Total Assets", start_year]
    ) / 2
    rsst = (delta_wc + delta_nco + delta_fin) / avg_total_assets
    return rsst


def calculate_delta_rec(data, start_year, end_year):
    delta_rec = (
        data.loc["Accounts Receivables", end_year]
        - data.loc["Accounts Receivables", start_year]
    )
    avg_total_assets = (
        data.loc["Total Assets", end_year] + data.loc["Total Assets", start_year]
    ) / 2
    delta_rec_ratio = delta_rec / avg_total_assets
    return delta_rec_ratio


def calculate_delta_inv(data, start_year, end_year):
    delta_inv = (
        data.loc["Current Assets", end_year]
        - data.loc["Accounts Receivables", end_year]
    ) - (
        data.loc["Current Assets", start_year]
        - data.loc["Accounts Receivables", start_year]
    )
    avg_total_assets = (
        data.loc["Total Assets", end_year] + data.loc["Total Assets", start_year]
    ) / 2
    delta_inv_ratio = delta_inv / avg_total_assets
    return delta_inv_ratio


def calculate_soft_assets(data, end_year):
    total_assets = data.loc["Total Assets", end_year]
    property_plant_equipment = data.loc["Property, Plant & Equipment", end_year]
    cash_and_cash_equivalents = (
        data.loc["Current Assets", end_year]
        - data.loc["Accounts Receivables", end_year]
    )
    soft_assets = (
        total_assets - property_plant_equipment - cash_and_cash_equivalents
    ) / total_assets
    return soft_assets


def calculate_delta_cash_sales(data, start_year, end_year):
    sales = data.loc["Revenue", end_year]
    sales_prev = data.loc["Revenue", start_year]
    delta_rec = (
        data.loc["Accounts Receivables", end_year]
        - data.loc["Accounts Receivables", start_year]
    )
    avg_total_assets = (
        data.loc["Total Assets", end_year] + data.loc["Total Assets", start_year]
    ) / 2
    delta_cash_sales = ((sales - sales_prev) - delta_rec) / avg_total_assets
    return delta_cash_sales


def calculate_delta_roa(data, start_year, end_year):
    earnings_curr = data.loc["Net Income from Continuing Operations", end_year]
    earnings_prev = data.loc["Net Income from Continuing Operations", start_year]
    total_assets_curr = data.loc["Total Assets", end_year]
    total_assets_prev = data.loc["Total Assets", start_year]
    roa_curr = earnings_curr / total_assets_curr
    roa_prev = earnings_prev / total_assets_prev
    delta_roa = roa_curr - roa_prev
    return delta_roa


def calculate_issue_indicator(data, start_year, end_year):
    return 1


# Calculate the Dechow F-Score
def calculate_dechow_f_score(data, start_year, end_year):
    rsst = calculate_rsst(data, start_year, end_year)
    delta_rec = calculate_delta_rec(data, start_year, end_year)
    delta_inv = calculate_delta_inv(data, start_year, end_year)
    soft_assets = calculate_soft_assets(data, end_year)
    delta_cash_sales = calculate_delta_cash_sales(data, start_year, end_year)
    delta_roa = calculate_delta_roa(data, start_year, end_year)
    issue_indicator = calculate_issue_indicator(data, start_year, end_year)

    f_score = (
        -7.893
        + 0.79 * rsst
        + 2.518 * delta_rec
        + 1.191 * delta_inv
        + 1.979 * soft_assets
        + 0.171 * delta_cash_sales
        - 0.032 * delta_roa
        + 1.02 * issue_indicator
    )

    probability_value = np.exp(f_score) / (1 + np.exp(f_score))
    unconditional_probability = 0.0037
    f_score = probability_value / unconditional_probability

    return f_score
