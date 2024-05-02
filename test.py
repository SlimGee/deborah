from typing import Dict
import yfinance as yf
import json
import os
import re


def remap_dict_to_json_compatible_dict(dic):
    remapped = {}
    for key in dic:
        if isinstance(dic[key], dict):
            remapped[key] = remap_dict_to_json_compatible_dict(dic[key])
        else:
            remapped[key] = str(dic[key])

    return remapped


def save_df_to_json(df, filename):
    df_dict = df.to_dict()
    remaped_df_dict = {}
    for key in df_dict:
        remaped_df_dict[key.year] = df_dict[key]

    real_dict = remap_dict_to_json_compatible_dict(remaped_df_dict)

    with open(filename, "w") as f:
        json.dump(real_dict, f)


p = open("companies.json", "r")
companies = json.load(p)

for ticker, company in companies.items():
    try:
        ticker = yf.Ticker(ticker)
        print(company.replace("/", "_"))

        income_statement = ticker.income_stmt
        cash_flow = ticker.cashflow
        balance_sheet = ticker.balance_sheet
        os.mkdir("data/" + company.replace("/", "_"))
        save_df_to_json(
            income_statement,
            "data/" + company.replace("/", "_") + "/income_statement.json",
        )
        save_df_to_json(
            cash_flow, "data/" + company.replace("/", "_") + "/cash_flow.json"
        )
        save_df_to_json(
            balance_sheet, "data/" + company.replace("/", "_") + "/balance_sheet.json"
        )
    except Exception as e:
        print(e)
        continue
