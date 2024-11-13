from numpy import cov, var, nan
from pandas import DataFrame, to_datetime, concat, Series, to_numeric
from typing import Union, Tuple
from datetime import datetime, timedelta
import spf_old as psfo
import Support_funct as psf
import numpy as np
import numpy_financial as npf
import math

'''
def recap_portfolio(beta:dict, medaf:dict, risk:dict, annulized_return:dict, total_CR:dict)->DataFrame:
    
    #Set up dictionary
    kies_list = list(df_dictnary.keys())

    recap = DataFrame()
    recap["return"] = [df_dictnary[key] for key in kies_list]
    recap["Medaf"] = [medaf_return[key] for key in medaf_return.keys()]
    recap["Risk"] = [risk_dict[risk] for risk in risk_dict.keys()]
    recap["5-y annualized"] = [five_year_annualized[stock] for stock in five_year_annualized.keys()]
    recap["5-y Beta"] = [beta_results[beta] for beta in beta_results.keys()]
    
    
    if len(weights) == len(recap):
        recap["Weight"] = weights
    else:
        raise ValueError("Length of the list does not match the number of rows in the DataFrame.")
    
    recap.index=kies_list
    recapt = recap.T

    return recapt
'''

def annualized_return(totals_Cu_Rre: dict, number_days: int) -> dict:
    
    # Use exact division instead of rounding
    y = 252 / number_days
    annualized_return = {}

    for name in totals_Cu_Rre.keys():
        total_return = totals_Cu_Rre[name] / 100  # Convert percentage to decimal

        name_apt = f"Annualized Return"

        if total_return <= -1:  # Check for more than 100% loss (avoid invalid computation)
            annualized_return[name_apt] = nan
        else:
            part1 = 1 + total_return
            part2 = math.pow(part1, y)
            part3 = part2 - 1
            
            # Store result only if valid
            annualized_return[name_apt] = part3 * 100  # Convert back to percentage
    
    return annualized_return


def calculate_cumulative_returns(file_read4: DataFrame) -> Tuple[DataFrame,dict]:
    cumulative_columns = {}
    #storing the total of cumulativre retunrs
    totals = {}
    names = []
    for key in file_read4.columns:
        if "_DR" in key:
            adj_key = key.replace("_DR","")
            cumulative_name = f"{adj_key}_CR"
            
            cumulative_returns = ((1 + file_read4[key] / 100).cumprod() - 1)*100
            cumulative_columns[cumulative_name] = cumulative_returns
            
            name = "Cumulative Return"
            totals[name] =  cumulative_columns[cumulative_name].iloc[-1]
            names.append(name)

    cumulative_df = DataFrame(cumulative_columns)
    
    # Insert cumulative return columns next to their corresponding daily return columns
    result_df = file_read4.copy()
    for key in file_read4.columns:
        if "_DR" in key:
            adj_key = key.replace("_DR","")
            col_index = result_df.columns.get_loc(key) + 1
            cumulative_name = f"{adj_key}_CR"
            result_df.insert(col_index, cumulative_name, cumulative_df[cumulative_name])
    
    result_df.dropna(inplace=True)
    return (result_df, totals)
    

def risk_stock(df_daily_return: DataFrame) -> dict:

    risk_dict = {}
    for cols in df_daily_return.columns:
        if "_DR" in cols:
            risk_dict["Volatility"] = df_daily_return[cols].std()

    return risk_dict


def medaf(portfolio_sector: dict, beta_results: dict, rf=0.0434) -> dict:
    try:
        medaf_dict = {}
        
        rm = portfolio_sector["Expected return"]

        beta = beta_results["Beta"]
        
        # Calculate the risk premium (market return - risk-free rate)
        risk_prime = rm - rf

        # Calculate CAPM for each beta
        market_risk_prime = risk_prime * beta
        medaf_value = market_risk_prime + rf  # CAPM formula: rf + beta * (rm - rf)
        
        medaf_dict["CAPM"] = medaf_value  # Store in dict with stock name as key

        return medaf_dict

    except Exception as e:
        raise Exception(f"General Error while calculating MEDAF: {e}")


def medaf2(portfolio_sector : dict, beta_results : dict, portfolio : dict, file: str, rf= 0.0434) -> dict:

    try :
        medaf_dict = {}

        for value in portfolio_sector.values():
            rm = portfolio_sector[value]              
            
        risk_prime = rm - rf

        for beta in beta_results.values:
            beta = beta_results[beta]
        market_risk_prime = risk_prime * beta
        medaf = market_risk_prime + rf
        medaf_dict[file] = medaf

        return medaf_dict
    
    except Exception as e:
        raise e(f"General Error while calculating MEDAF : {e}") 
    
                

def calculate_beta(stock, market_closing_df: DataFrame, stocks_closing_df: DataFrame) -> Tuple[float,dict]:
    
    beta_result = {}
    M_excpected_return = {}
    # Clean stock daily return data frame
    stocks_closing_df_copy = stocks_closing_df.copy()

    # Keep only stock daily return columns (_DR)
    for stock_dropped in stocks_closing_df_copy.columns:
        if "_DR" not in stock_dropped:
            stocks_closing_df_copy.drop(columns=stock_dropped, axis=1, inplace=True)
        
    # Merge stock and market dataframes on Date (index) with 'inner' join
    merged_df = stocks_closing_df_copy.join(market_closing_df, how='inner') 
    
    # Drop rows with NaN values after the merge
    merged_df.dropna(inplace=True)

    # Extract the stock and market returns columns
    stock_name = f'{stock}_DR'

    stock_returns = merged_df[stock_name].values
    market_returns = merged_df['masi_M_DR'].values
    
    # Calculate covariance and variance using NumPy
    covariance_matrix = np.cov(stock_returns, market_returns, ddof=0, rowvar=False)
    
    covariance = ((covariance_matrix[0, 1]))  # Covariance between stock and market returns
    variance = np.var(market_returns, ddof=0)  # Variance of the market returns
    
    beta = covariance / variance if variance != 0 else np.nan
            
    beta_result["Beta"] = beta
    M_excpected_return["Expected return"] = merged_df["masi_M_DR"].mean()

    return (M_excpected_return, beta_result)





def market_DR()-> Tuple [dict, DataFrame, DataFrame]:

    file_path = "C:/Users/dl/Desktop/cse/masi data/masi.csv"
        
    #read secctor file
    file_read0 = psfo.read_file(file_path)
    
    file_read1 = file_read0.iloc[:,:2]
    file_read2 = file_read1.rename(columns={'Price': 'masi_M'})

    #set Date in Date fonmat  
    file_read2['Date'] = to_datetime(file_read2["Date"]).dt.date
    #formating data:
    file_read3 = psf.prepare_date(file_read2) 
    file_read4 = psf.set_closing_prices(file_read3,column_name="masi_M")

    #clean the coloumn
    file_read4.dropna(inplace=True)

    #calculate daily return for each coloumn 
    portfolio_sector0, df_sector_DL0 = calculate_daily_returns(file_read4)
    portfolio_sector, df_sector_DL = calculate_daily_returns(file_read4, new= True)
    
    return (portfolio_sector0, df_sector_DL, df_sector_DL0)


def calculate_daily_returns(closing_df : DataFrame, new : bool = False)-> Tuple[dict, DataFrame]:
    print(closing_df)
    portfolio = {}
    new_df = DataFrame()
    for key in closing_df.columns:
        if key == "Date":
            continue
        return_name = f"{key}_DR"
        if new == False : 
            closing_df[return_name] = closing_df[key].pct_change().shift(-1) * 100
            
            closing_df.drop(closing_df[return_name].index[-1], inplace=True)
            portfolio["Expected return"] = closing_df[return_name].mean()
            closing_df.dropna(inplace=True)
            new_df = closing_df

        elif new == True : 
            if "_DR" in key :
                pass
            else :
                new_df[return_name] = closing_df[key].pct_change().shift(-1) * 100
                new_df.drop(new_df[return_name].index[-1], inplace=True)
                new_df[return_name] = to_numeric(new_df[return_name])
                portfolio["Expected return"] = new_df[return_name].mean()
                
    
    new_df.dropna(inplace=True) 

    return (portfolio, new_df)
