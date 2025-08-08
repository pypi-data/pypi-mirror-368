# -*- coding: utf-8 -*-

"""
Main module.

"""

import datetime
from urllib.request import urlopen
import zipfile
import os
from os.path import join, isfile
from typing import Union

import pandas as pd

from solvency2_data.util import get_config
from solvency2_data.scraping import eiopa_link

countries_list = [
    "Euro",
    "Austria",
    "Belgium",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Iceland",
    "Ireland",
    "Italy",
    "Latvia",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Netherlands",
    "Norway",
    "Poland",
    "Portugal",
    "Romania",
    "Russia",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden",
    "Switzerland",
    "United Kingdom",
    "Australia",
    "Brazil",
    "Canada",
    "Chile",
    "China",
    "Colombia",
    "Hong Kong",
    "India",
    "Japan",
    "Malaysia",
    "Mexico",
    "New Zealand",
    "Singapore",
    "South Africa",
    "South Korea",
    "Taiwan",
    "Thailand",
    "Turkey",
    "United States",
]

currencies = [
    "EUR",
    "BGN",
    "HRK",
    "CZK",
    "DKK",
    "HUF",
    "LIC",
    "PLN",
    "NOK",
    "RON",
    "RUB",
    "SEK",
    "CHF",
    "GBP",
    "AUD",
    "BRL",
    "CAD",
    "CLP",
    "CNY",
    "COP",
    "HKD",
    "INR",
    "JPY",
    "MYR",
    "MXN",
    "NZD",
    "SGD",
    "ZAR",
    "KRW",
    "TWD",
    "THB",
    "TRY",
    "USD",
]


def RFR_reference_date(input_date: str = None, cache: dict = {}) -> dict:
    """
    Calculates the reference date based on the input date or the current date.
    If no input date is provided or if the input date is in the future,
    it defaults to the current date. If the current date is before the 5th of the month,
    it sets the reference date to the last day of the previous month.
    Otherwise, it sets the reference date to the next day after the input date.

    Args:
        input_date (str, optional): The input date in the format "%Y-%m-%d".
            Defaults to None, which means the current date is used.
        cache (dict, optional): A dictionary to store the calculated reference date.
            Defaults to an empty dictionary.

    Returns:
        dict: A dictionary containing the input date and the reference date.
            The input date is stored under the key "input_date" in the format "%Y-%m-%d".
            The reference date is stored under the key "reference_date" in the format "%Y%m%d".
    """
    if input_date is not None:
        reference_date = datetime.datetime.strptime(input_date, "%Y-%m-%d")
    else:
        reference_date = None

    if (reference_date is None) or (reference_date > datetime.datetime.today()):
        reference_date = datetime.datetime.today()

        if reference_date.day < 5:
            reference_date = reference_date.replace(day=1) - datetime.timedelta(days=1)
    else:
        reference_date = reference_date + datetime.timedelta(days=1)

    # to do : check if end of month
    reference_date = reference_date.replace(day=1) - datetime.timedelta(days=1)

    cache["input_date"] = reference_date.strftime("%Y-%m-%d")
    cache["reference_date"] = cache["input_date"].replace("-", "")

    return cache


def RFR_dict(input_date: str = None, cache: dict = {}) -> dict:
    """
    Generates a dictionary containing filenames based on the reference date
    and other data derived from it.

    Args:
        input_date (str, optional): The input date in the format "%Y-%m-%d".
            Defaults to None, which means the current date is used.
        cache (dict, optional): A dictionary to store intermediate and final results.
            Defaults to an empty dictionary.

    Returns:
        dict: A dictionary containing generated filenames and other data.
            The dictionary includes the following keys:
                - "input_date": The input date in the format "%Y-%m-%d".
                - "reference_date": The reference date in the format "%Y%m%d".
                - "name_excelfile": The filename for the EIOPA RFR term structures Excel file.
                - "name_excelfile_spreads": The filename for the EIOPA RFR PD Cod Excel file.
                - "name_excelfile_sw_parameters": The filename for the EIOPA QB SW Excel file.
                - "name_excelfile_va_portfolios": The filename for the EIOPA VA portfolios Excel file.
    """
    cache = RFR_reference_date(input_date, cache)
    cache["name_excelfile"] = (
        "EIOPA_RFR_" + cache["reference_date"] + "_Term_Structures" + ".xlsx"
    )
    cache["name_excelfile_spreads"] = (
        "EIOPA_RFR_" + cache["reference_date"] + "_PD_Cod" + ".xlsx"
    )
    cache["name_excelfile_sw_parameters"] = (
        "EIOPA_RFR_" + cache["reference_date"] + "_Qb_SW" + ".xlsx"
    )
    cache["name_excelfile_va_portfolios"] = (
        "EIOPA_RFR_" + cache["reference_date"] + "_VA_portfolios" + ".xlsx"
    )
    return cache


def download_RFR(input_date: str = None, cache: dict = {}) -> dict:
    """
    Downloads EIOPA RFR (Risk-Free Rate) files for a given date and saves them locally.

    Args:
        input_date (str, optional): The input date in the format "%Y-%m-%d".
            Defaults to None, which means the current date is used.
        cache (dict, optional): A dictionary to store intermediate and final results.
            Defaults to an empty dictionary.

    Returns:
        dict: A dictionary containing information about the downloaded files and paths.
            The dictionary includes the following keys:
                - "input_date": The input date in the format "%Y-%m-%d".
                - "reference_date": The reference date in the format "%Y%m%d".
                - "name_excelfile": The filename for the downloaded EIOPA RFR term structures Excel file.
                - "name_excelfile_spreads": The filename for the downloaded EIOPA RFR PD Cod Excel file.
                - "url": The URL from which the files were downloaded.
                - "name_zipfile": The name of the downloaded zip file.
                - "path_excelfile": The path where the Excel files are saved.
                - "path_zipfile": The path where the zip file is saved.
    """
    cache = RFR_dict(input_date, cache)

    name_excelfile = None
    name_excelfile_spreads = None
    name_excelfile_sw_parameters = None
    name_excelfile_va_portfolios = None

    for file in os.listdir(cache["path_excelfile"]):
        if file.lower() == cache["name_excelfile"].lower():
            cache["name_excelfile"] = name_excelfile = file
        if file.lower() == cache["name_excelfile_spreads"].lower():
            cache["name_excelfile_spreads"] = name_excelfile_spreads = file
        if file.lower() == cache["name_excelfile_sw_parameters"].lower():
            cache["name_excelfile_sw_parameters"] = name_excelfile_sw_parameters = file
        if file.lower() == cache["name_excelfile_va_portfolios"].lower():
            cache["name_excelfile_va_portfolios"] = name_excelfile_va_portfolios = file

    if name_excelfile is None or name_excelfile_spreads is None:
        # determine correct url and zipfile
        cache["url"] = eiopa_link(
            cache["input_date"], data_type="rfr", proxies=cache.get("proxies", None)
        )
        cache["name_zipfile"] = os.path.basename(cache["url"]).split("filename=")[-1]

        # download file
        request = urlopen(cache["url"], cache.get("proxies", None))

        # save zip-file
        output = open(join(cache["path_zipfile"], cache["name_zipfile"]), "wb")
        output.write(request.read())
        output.close()

        name_excelfile = None
        name_excelfile_spreads = None
        name_excelfile_sw_parameters = None
        name_excelfile_va_portfolios = None
        zip_ref = zipfile.ZipFile(join(cache["path_zipfile"], cache["name_zipfile"]))
        for idx, name in enumerate(zip_ref.namelist()):
            if name.lower() == cache["name_excelfile"].lower():
                cache["name_excelfile"] = name_excelfile = name
            if name.lower() == cache["name_excelfile_spreads"].lower():
                cache["name_excelfile_spreads"] = name_excelfile_spreads = name
            if name.lower() == cache["name_excelfile_sw_parameters"].lower():
                cache["name_excelfile_sw_parameters"] = name_excelfile_sw_parameters = (
                    name
                )
            if name.lower() == cache["name_excelfile_va_portfolios"].lower():
                cache["name_excelfile_va_portfolios"] = name_excelfile_va_portfolios = (
                    name
                )
        if name_excelfile is not None:
            zip_ref.extract(name_excelfile, cache["path_excelfile"])
        if name_excelfile_spreads is not None:
            zip_ref.extract(name_excelfile_spreads, cache["path_excelfile"])
        if name_excelfile_sw_parameters is not None:
            zip_ref.extract(name_excelfile_sw_parameters, cache["path_excelfile"])
        if name_excelfile_va_portfolios is not None:
            zip_ref.extract(name_excelfile_va_portfolios, cache["path_excelfile"])
        zip_ref.close()

        # remove zip file
        # os.remove(cache['path_zipfile'] + cache["name_zipfile"])

    return cache


def read_spreads(xls: pd.ExcelFile, cache: dict = {}) -> dict:
    """
    Reads financial and non-financial fundamental spreads from an Excel file and stores them in a dictionary.

    Args:
        xls (pd.ExcelFile): An ExcelFile object containing the spreadsheets.
        cache (dict, optional): A dictionary to store the read spreadsheets.
            Defaults to an empty dictionary.

    Returns:
        dict: A dictionary containing the read spreadsheets.
            The dictionary includes the following keys:
                - "financial fundamental spreads": A dictionary containing financial spreadsheets
                    for different currencies.
                - "non-financial fundamental spreads": A dictionary containing non-financial spreadsheets
                    for different currencies.
            Each sub-dictionary contains DataFrames with financial or non-financial spreads
            for the respective currencies.
    """
    cache["financial fundamental spreads"] = {}
    for name in currencies:
        if name in xls.sheet_names:
            df = pd.read_excel(
                io=xls,
                sheet_name=name,
                header=1,
                usecols="W:AC",
                nrows=30,
                skiprows=8,
                names=[0, 1, 2, 3, 4, 5, 6],
            )
            df.index = range(1, 31)
            cache["financial fundamental spreads"][name] = df

    cache["non-financial fundamental spreads"] = {}
    for name in currencies:
        if name in xls.sheet_names:
            df = pd.read_excel(
                io=xls,
                sheet_name=name,
                header=1,
                usecols="W:AC",
                nrows=30,
                skiprows=48,
                names=[0, 1, 2, 3, 4, 5, 6],
            )
            df.index = range(1, 31)
            cache["non-financial fundamental spreads"][name] = df

    return cache


def read_govies(xls, cache: dict = {}) -> dict:
    """
    Reads central government fundamental spreads from an Excel file and stores them in a dictionary.

    Args:
        xls : An object representing the Excel file.
        cache (dict, optional): A dictionary to store the read spreadsheets.
            Defaults to an empty dictionary.

    Returns:
        dict: A dictionary containing the read spreadsheets.
            The dictionary includes the following keys:
                - "central government fundamental spreads": A DataFrame containing central government spreads.
            The DataFrame includes spreads for various financial attributes indexed by dates.
    """
    cache["central government fundamental spreads"] = None
    for name in ["FS_Govts"]:
        if name in xls.sheet_names:
            df = pd.read_excel(
                io=xls,
                sheet_name=name,
                usecols="B:AF",
                nrows=53,
                index_col=0,
                skiprows=9,
            )
            # This line introduces a dependency on the spots
            # df.index = cache['RFR_spot_no_VA'].columns
            cache["central government fundamental spreads"] = df.T

    return cache


def read_ltas(xls, cache: dict = {}) -> dict:
    """
    Reads ltas data from an Excel file and stores them in a dictionary.

    Args:
        xls : An object representing the Excel file.
        cache (dict, optional): A dictionary to store the read spreadsheets.
            Defaults to an empty dictionary.

    Returns:
        dict: A dictionary containing the read spreadsheets.
            The dictionary includes the following keys:
                - "LTAS_Govts": A DataFrame containing LTAS government bonds
                - "LTAS_Corps": A DataFrame containing LTAS corporate bonds
            The DataFrame includes spreads for various financial attributes indexed by dates.
    """
    for name in ["LTAS_Corps", "LTAS_Govts"]:
        cache[name] = None
        if name in xls.sheet_names:
            df = pd.read_excel(
                io=xls,
                sheet_name=name,
                usecols="B:AF",
                nrows=53,
                index_col=0,
                skiprows=9,
            )
            cache[name] = df.T

    return cache


def read_sw_parameters(xls, cache: dict = {}) -> dict:
    """
    Reads smith wilson parameters from an Excel file and stores them in a dictionary.

    Args:
        xls : An object representing the Excel file.
        cache (dict, optional): A dictionary to store the read spreadsheets.
            Defaults to an empty dictionary.

    Returns:
        dict: A dictionary containing the read spreadsheets.
            The dictionary includes the following keys:
                - "sw parameters": A DataFrame containing central government spreads.
            The DataFrame includes the smith wilson parameters
    """
    for name in ["SW_Qb_no_VA", "SW_Qb_with_VA"]:
        if name in xls.sheet_names:
            cache[name] = dict()
            df = pd.read_excel(
                io=xls,
                sheet_name=name,
                skiprows=9,
            )
            for idx, col in enumerate(df.columns):
                if "Unnamed" not in col:
                    sw_parameters = pd.DataFrame(
                        data=df.iloc[:, idx],
                    ).dropna()
                    if len(sw_parameters.index) > 0:
                        sw_parameters.index = df.iloc[:, idx - 1].dropna()
                    else:
                        # Fix for 2023-6-30 where column names of SW_Qb_with_VA are not aligned
                        sw_parameters = pd.DataFrame(
                            data=df.iloc[:, idx - 1],
                        ).dropna()
                        sw_parameters.index = df.iloc[:, idx - 2].dropna()
                    sw_parameters.index.name = None

                    sw_parameters.columns = ["value"]
                    cache[name][col] = sw_parameters

    return cache


def read_va_portfolios(xls, cache: dict = {}) -> dict:
    """
    Reads va portfolios from an Excel file and stores them in a dictionary.

    Args:
        xls : An object representing the Excel file.
        cache (dict, optional): A dictionary to store the read spreadsheets.
            Defaults to an empty dictionary.

    Returns:
        dict: A dictionary containing the read spreadsheets.
            The dictionary includes the following keys:
                - "va portfolios": A DataFrame containing central government spreads.
            The DataFrame includes the smith wilson parameters
    """
    cache["va portfolios"] = dict()
    for name in ["VA_Currency_Weights", "VA_National_Weights"]:
        if name in xls.sheet_names:
            df = pd.read_excel(
                io=xls,
                sheet_name=name,
                usecols="B:D",
                nrows=53,
                skiprows=9,
            )
            df_va = pd.DataFrame(
                index=df["Unnamed: 1"],
                columns=["Central Govts", "Other assets"],
                data=df[["Unnamed: 2", "Unnamed: 3"]].values,
            )
            df_va.index.name = "currency"
            cache["va portfolios"][name] = df_va

    for name in [
        "VA_C_Govts_Comp",
        "VA_C_Govts_Dur",
        "VA_N_Govts_Comp",
        "VA_N_Govts_Dur",
    ]:
        if name in xls.sheet_names:
            df = pd.read_excel(
                io=xls,
                sheet_name=name,
                nrows=53,
                index_col=1,
                skiprows=9,
            )
            if "Unnamed: 0" in df.columns:
                del df["Unnamed: 0"]
            cache["va portfolios"][name] = df.fillna(0)

    for name in [
        "VA_C_Corps_Comp",
        "VA_C_Corps_Dur",
        "VA_N_Corps_Comp",
        "VA_N_Corps_Dur",
    ]:
        if name in xls.sheet_names:
            df = pd.read_excel(
                io=xls,
                sheet_name=name,
                usecols="B:P",
                nrows=53,
                index_col=0,
                skiprows=9,
            )
            cache["va portfolios"][name] = df.fillna(0)

    return cache


def read_spot(xls, cache: dict = {}) -> dict:
    """
    Reads various spot data from an Excel file and stores them in a dictionary.

    Args:
        xls : An object representing the Excel file.
        cache (dict, optional): A dictionary to store the read spot data.
            Defaults to an empty dictionary.

    Returns:
        dict: A dictionary containing the read spot data.
            The dictionary includes the following keys:
                - "meta": Metadata of the RFR (parameters)
                - "RFR_spot_with_VA": DataFrame containing spot data with VA.
                - "RFR_spot_no_VA": DataFrame containing spot data without VA.
                - "Spot_WITH_VA_shock_UP": DataFrame containing spot data with VA with UP shock.
                - "Spot_WITH_VA_shock_DOWN": DataFrame containing spot data with VA with DOWN shock.
                - "Spot_NO_VA_shock_UP": DataFrame containing spot data without VA with UP shock.
                - "Spot_NO_VA_shock_DOWN": DataFrame containing spot data without VA with DOWN shock.
    """
    for name in [
        "RFR_spot_no_VA",
        "RFR_spot_with_VA",
        "Spot_NO_VA_shock_UP",
        "Spot_NO_VA_shock_DOWN",
        "Spot_WITH_VA_shock_UP",
        "Spot_WITH_VA_shock_DOWN",
    ]:
        if name in xls.sheet_names:
            df = pd.read_excel(
                io=xls, sheet_name=name, header=1, nrows=158, index_col=1
            )
            # drop unnamed columns from the excel file
            for col in df.columns:
                if "Unnamed:" in col:
                    df = df.drop(col, axis=1)
            df.loc["VA"] = df.loc["VA"].infer_objects().fillna(0, inplace=False)
            df = df.iloc[8:]
            df.index.names = ["Duration"]
            cache[name] = df

    return cache


def read_meta(xls, cache: str = {}) -> dict:
    """
    Reads metadata from an Excel file and stores it in a dictionary.

    Args:
        xls : An object representing the Excel file.
        cache (dict, optional): A dictionary to store the read metadata.
            Defaults to an empty dictionary.

    Returns:
        dict: A dictionary containing the read metadata.
            The dictionary includes the following key:
                - "meta": DataFrame containing metadata.
            The DataFrame includes metadata indexed by "meta" and may include information
            such as headers, column descriptions, and other relevant details.
    """
    df_meta = pd.read_excel(
        xls, sheet_name="RFR_spot_with_VA", header=1, index_col=1, skipfooter=150
    )
    # drop unnamed columns from the excel file
    for col in df_meta.columns:
        if "Unnamed:" in col:
            df_meta = df_meta.drop(col, axis=1)

    df_meta.loc["VA"] = df_meta.loc["VA"].infer_objects().fillna(0, inplace=False)
    df_meta = df_meta.iloc[0:8]
    df_meta.index.names = ["meta"]
    df_meta.index = df_meta.index.fillna("Info")

    # Reference date is not strictly part of meta
    # df_append = pd.DataFrame(index=['reference date'],
    #                          columns=df_meta.columns)
    # # df_append.loc['reference date'] = cache["reference_date"]
    # df_meta = df_meta.append(df_append)

    cache["meta"] = df_meta

    return cache


def read(input_date=None, path: str = None, proxies: Union[dict, None] = None) -> dict:
    """
    Reads data from Excel files and stores it in a dictionary.

    Args:
        input_date (str, optional): The input date in the format "%Y-%m-%d".
            Defaults to None, which means the current date is used.
        path (str, optional): The path to the directory containing Excel files.
            If None, it looks for .cfg files in the current directory or the package directory.
            Defaults to None.
        proxies: None or a dictionary of proxies to be used when downloading rates
            (None turns off proxies completely)

    Returns:
        dict: A dictionary containing the read data.
            The dictionary includes various keys storing downloaded files, metadata, spot data, spreadsheets, etc.
            - "meta": Metadata of the RFR (parameters)
            - "RFR_spot_with_VA": DataFrame containing spot data with VA.
            - "RFR_spot_no_VA": DataFrame containing spot data without VA.
            - "Spot_WITH_VA_shock_UP": DataFrame containing spot data with VA with UP shock.
            - "Spot_WITH_VA_shock_DOWN": DataFrame containing spot data with VA with DOWN shock.
            - "Spot_NO_VA_shock_UP": DataFrame containing spot data without VA with UP shock.
            - "Spot_NO_VA_shock_DOWN": DataFrame containing spot data without VA with DOWN shock.
            - "financial fundamental spreads": fundamental spreads (financial)
            - "non-financial fundamental spreads": fundamental spread (non-financial)
            - "central government fundamental spreads": fundamental spread (central government)
            - "LTAS_Govts": Long Term Average Spreads (government bonds) (DataFrame)
            - "LTAS_Corps": Long Term Average Spreads (corporate bonds) (DataFrame)
            - "SW_Qb_with_VA": Smith Wilson paramateres (with VA) (dictionary of DataFrames)
            - "SW_Qb_no_VA": Smith Wilson paramateres (without VA) (dictionary of DataFrames)
            - "va portfolios": VA portfolios (dictionary of DataFrames)
            - "path_zipfile": location of the zip file used (string)
            - "path_excelfile": location of the Excel file used (string)
            - "input_date": input date of the RFR (string)
            - "reference_date": date used for the RFR (string)
            - "name_excelfile": Name of the RFR Excel file used (string)
            - "name_excelfile_spreads": Name of the spreads Excel file used (string)
            - "name_excelfile_sw_parameters": Name of the SW parameters Excel file used (string)
            - "name_excelfile_va_portfolios": Name of the VA portfolios Excel file used (string)
    """
    if path is None:
        # look in current directory for .cfg file
        # if not exists then take the .cfg file in the package directory
        config = get_config().get("Directories")

        path_zipfile = config.get("zip_files")
        path_excelfile = config.get("excel_files")
    else:
        path_zipfile = path
        path_excelfile = path

    cache = {
        "path_zipfile": path_zipfile,
        "path_excelfile": path_excelfile,
    }
    if proxies is not None:
        cache["proxies"] = proxies

    # read RFR data
    cache = download_RFR(input_date, cache)
    excel_filename = join(cache["path_excelfile"], cache["name_excelfile"])
    xls = pd.ExcelFile(excel_filename, engine="openpyxl")
    cache = read_meta(xls, cache)
    cache = read_spot(xls, cache)
    xls.close()

    # read spreads data
    excel_filename = join(cache["path_excelfile"], cache["name_excelfile_spreads"])
    xls = pd.ExcelFile(excel_filename, engine="openpyxl")
    cache = read_spreads(xls, cache)
    cache = read_govies(xls, cache)
    cache = read_ltas(xls, cache)
    xls.close()

    # read sw parameters data if available
    excel_filename = join(
        cache["path_excelfile"], cache["name_excelfile_sw_parameters"]
    )
    if isfile(excel_filename):
        xls = pd.ExcelFile(excel_filename, engine="openpyxl")
        cache = read_sw_parameters(xls, cache)
        xls.close()

    # read va portfolio data if available
    excel_filename = join(
        cache["path_excelfile"], cache["name_excelfile_va_portfolios"]
    )
    if isfile(excel_filename):
        xls = pd.ExcelFile(excel_filename, engine="openpyxl")
        cache = read_va_portfolios(xls, cache)
        xls.close()

    return cache
