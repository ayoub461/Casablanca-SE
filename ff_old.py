from yfinance import download
from numpy import cov, var, nan
from pandas import DataFrame, to_datetime, concat, Series
from typing import Union, Tuple
from datetime import datetime, timedelta
from spf_old import set_closing_prices


def medaf(portfolio_sector : dict, beta_results : dict, chosen_sectors_dict : dict, rf= 0.04) -> dict:
    try :
        medaf_dict = {}
        beta = 0
        for key in chosen_sectors_dict.keys():
            for sector in portfolio_sector.keys() :
                
                if key == sector : 
                    rm = portfolio_sector[key]                    
                    
                    risk_prime = rm - rf
                    
                    for i in range(len(chosen_sectors_dict[key])):
                        ticker = chosen_sectors_dict[key][i]
                        beta = beta_results[ticker]
                        market_risk_prime = risk_prime * beta
                        medaf = market_risk_prime + rf
                        medaf_dict[chosen_sectors_dict[key][i]] = medaf
                
                
                
        return medaf_dict
    except Exception as e:
        raise e(f"General Error while calculating MEDAF : {e}") 
    
                

def sharpe_Ratio():
    ...



"""Portfolio Optimization"""

def efficient_Frontier ():
    ...

def opt_portf() :
    ...














def market_DR(chosen_sectors_dict : dict)-> Tuple [dict, DataFrame, DataFrame]:

    df_sector_DL = DataFrame()

    chosen_sector = list(chosen_sectors_dict.keys())

    end_date = datetime.today()
    start_date = end_date - timedelta(days=5*365)
    
    for benchmark_symbol in chosen_sector:
        #download the index data
        benchmark_data = download(benchmark_symbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

        #Only adj close coloumn
        df_sector_DL = set_closing_prices(df_sector_DL, benchmark_data, benchmark_symbol)

    #clean the coloumn
        df_sector_DL.dropna(inplace=True)

    #calculate daily return for each coloumn 
    portfolio_sector0, df_sector_DL0 = calculate_daily_returns(df_sector_DL)
    portfolio_sector, df_sector_DL = calculate_daily_returns(df_sector_DL, new= True)

    return (portfolio_sector, df_sector_DL, df_sector_DL0)


def calculate_beta(market_closing_df: DataFrame, stocks_closing_df: DataFrame, 
                   chosen_sectors_dict: dict)-> dict:
    
    #Clean stock daily return data frame
    stocks_closing_df_copy = stocks_closing_df.copy()

    for stock_dropped in stocks_closing_df_copy.columns:
        if "_DR" not in stock_dropped:
            stocks_closing_df_copy.drop(columns=stock_dropped, axis=1, inplace=True)

    beta_results = {}

    min_date_market = to_datetime(market_closing_df.index).date.min()
    min_date_stocks = to_datetime(stocks_closing_df_copy.index).date.min()

    start_date = max(min_date_market,min_date_stocks)

    max_date_market = (to_datetime(market_closing_df.index).date).max()
    max_date_stock = (to_datetime(stocks_closing_df_copy.index).date).max()

    end_date = min(max_date_market, max_date_stock)

    # Step 3: Filter both DataFrames to this range
    market_closing_df_filtered = market_closing_df.loc[start_date:end_date]
    stocks_closing_df_filtered = stocks_closing_df_copy.loc[start_date:end_date]

    # Step 4: Handle missing values (e.g., drop rows with NaN values)
    market_closing_df_filtered = market_closing_df_filtered.dropna()
    stocks_closing_df_filtered = stocks_closing_df_filtered.dropna()

    sector_list = market_closing_df_filtered.columns.tolist()
    stocks_list = stocks_closing_df_filtered.columns.tolist()

    for sector in chosen_sectors_dict.keys():
        
        adj_sector_name = f"{sector}_DR"
        
        if adj_sector_name not in sector_list :
            raise KeyError("Secotr Ajd name not found")

        for stock in (chosen_sectors_dict[sector]):

            adj_stock_name = f"{stock}_DR"
            if adj_stock_name not in stocks_list :
                raise KeyError("Secotr Ajd name not found")

            # Align DataFrames to ensure they have the same dates
            combined = DataFrame.join(stocks_closing_df_filtered[adj_stock_name],market_closing_df_filtered[adj_sector_name])
            combined.dropna(inplace=True)

            # Step 5: Calculate correlation
             # Convert the DataFrame columns to NumPy arrays
            stock_returns = combined[adj_stock_name].values
            market_returns = combined[adj_sector_name].values
            
            # Calculate covariance and variance using NumPy
            covariance_matrix = cov(stock_returns, market_returns)
            covariance = covariance_matrix[0, 1]
            variance = var(market_returns)
            
            # Calculate beta
            beta = covariance / variance if variance != 0 else nan
            beta_results[stock] = beta

    return beta_results


"""Portfolio Calculations"""

def annulized_return(totals_Cu_Rre:dict,
                     number_days:int)->dict:
    
    y = round(365/number_days)
    five_year_annualized = {}

    for name in totals_Cu_Rre.keys():
        totals_CRre = (totals_Cu_Rre[name] / 100)

        name_apt = f"{name}_AR"
        if totals_CRre <= -1:  # Check for more than 100% loss
            five_year_annualized[name_apt] = nan

        else:
        
            part1 = 1 + totals_CRre
            part2 = pow(part1,y)
            part3 = part2-1
            
            
        five_year_annualized[name_apt] = part3 * 100
    
    return five_year_annualized



def recap_portfolio(df_dictnary: dict,
                        weights: list,
                            risk_dict: dict,
                            five_year_annualized: dict,
                              beta_results : dict,
                              medaf_return : dict)->DataFrame:
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



def calculate_cumulative_returns(closing_df: DataFrame) -> Tuple[DataFrame,dict]:
    cumulative_columns = {}
    #storing the total of cumulativre retunrs
    totals = {}
    names = []
    for key in closing_df.columns:
        if "_DR" in key:
            adj_key = key.replace("_DR","")
            cumulative_name = f"{adj_key}_CR"
            
            cumulative_returns = ((1 + closing_df[key] / 100).cumprod() - 1)*100
            cumulative_columns[cumulative_name] = cumulative_returns
            name = adj_key
            totals[name] =  cumulative_columns[cumulative_name].iloc[-1]
            names.append(name)

    cumulative_df = DataFrame(cumulative_columns)
    
    # Insert cumulative return columns next to their corresponding daily return columns
    result_df = closing_df.copy()
    for key in closing_df.columns:
        if "_DR" in key:
            adj_key = key.replace("_DR","")
            col_index = result_df.columns.get_loc(key) + 1
            cumulative_name = f"{adj_key}_CR"
            result_df.insert(col_index, cumulative_name, cumulative_df[cumulative_name])
    
    result_df.dropna(inplace=True)
    return (result_df, totals)
    

def risk_stock(df_daily_return: DataFrame) -> dict:
    risk_dict = {}
    return_columns = [col for col in df_daily_return.columns if '_DR' in col]
    stock_names = list(set(col.replace('_DR', '') for col in return_columns))    
    stock_return_columns = {name: [col for col in return_columns if col.startswith(name)] for name in stock_names}

    for name, cols in stock_return_columns.items():
        risk_dict[name] = df_daily_return[cols].std().mean()
    return risk_dict

    
def calculate_daily_returns(closing_df : DataFrame, new : bool = False)-> Tuple[dict, DataFrame]:
   
    portfolio = {}
    new_df = DataFrame()
    for key in closing_df.columns:
        if key == "Date":
            continue
        return_name = f"{key}_DR"
        if new == False : 
            closing_df[return_name] = closing_df[key].pct_change().shift(-1) * 100
            portfolio[key] = closing_df[return_name].mean()
            closing_df.dropna(inplace=True)
            new_df = closing_df

        elif new == True : 
            if "_DR" in key :
                pass
            else :
                new_df[return_name] = closing_df[key].pct_change().shift(-1) * 100
                portfolio[key] = new_df[return_name].mean()
    new_df.drop(new_df.index[-1], inplace=True)
    new_df.dropna(inplace=True)

    return (portfolio, new_df)


def stock_corr(
    stock_data: Union[DataFrame,list]
) ->DataFrame:
    try:
        if  isinstance(stock_data, DataFrame):
            combined_data = stock_data
        
        elif isinstance(stock_data, list) and  all(isinstance(item, (Series, DataFrame)) for item in stock_data):    
            combined_data = concat(stock_data, axis=1)
            
        else :
            raise TypeError("Invalid input type. Must be a DataFrame or list of Series/DataFrames.")
        
        correlation_matrix = combined_data.corr()
    except KeyError:
        raise KeyError("code 1")
    except Exception as e:
        raise Exception(f"{e}code 2")            

    return correlation_matrix



def calculate_correlation(closing_df : DataFrame)-> DataFrame:
    return_columns = []
    
    for name in closing_df.columns :
        if "_DR" in name:
            return_columns.append(closing_df[name])
    
    data_frame = stock_corr(return_columns)
    return data_frame
 

