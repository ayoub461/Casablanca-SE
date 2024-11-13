import os
from fractions import Fraction
import pandas as pd
from tabulate import tabulate
from typing import Union, Tuple
import itertools
from datetime import date




def days_number(df_cleaned: pd.DataFrame)->int:
    
    number_of_trading_days = len(df_cleaned)

    return number_of_trading_days


def set_closing_prices(df_file_read: pd.DataFrame, column_name: str = "Closing Price")-> pd.DataFrame:
    
    if not pd.api.types.is_datetime64_any_dtype(df_file_read.index):
        raise ValueError("Index must be of datetime type.")
    
    #df_filtered = df_file_read[df_file_read.index >= pd.Timestamp('2023, 1, 1')]

    #df_file_read = df_filtered
    df_file_read.loc[:,column_name] = df_file_read[column_name].replace(',', '', regex=True)
    df_file_read.loc[:,column_name] = pd.to_numeric(df_file_read[column_name])
    return df_file_read
    

def prepare_date(closing_df: pd.DataFrame)-> pd.DataFrame:

    try:
        
        closing_df['Date'] = pd.to_datetime(closing_df['Date'])
        closing_df.set_index("Date", inplace=True)
        closing_df.dropna(inplace=True)
    
    except Exception as e:
        raise RuntimeError(f"Error indexing Date or dropping NaN: {e}")
    return closing_df


def get_file_path(os_path: str,
                   file_input : str,
                     extension : str = "csv")-> str:
    extension = extension.strip().lower()
    if extension == "csv" :
        file_name_with_ext = f"{file_input}.csv"
    elif extension == "xlsx" :
        file_name_with_ext = f"{file_input}.xlsx"
    else :
        raise ValueError("Unsupported file extension. Supported extensions are 'csv' and 'xlsx'.")
    file_path = os.path.join(os_path,file_name_with_ext)
    return file_path


def rename_file(folder: str, file :str, to_remove= 'Historical Data')-> Tuple[str,str]:
    
    
    original_file = f"{file}.csv"

    name = file.replace(to_remove, "").strip()   
    new_name = f"{name}.csv"
    
    file_path = os.path.join(folder, original_file)

    
    new_file_path = os.path.join(folder, new_name)
    
    os.rename(file_path, new_file_path)
    
    return (new_file_path, new_name)


def get_files_in_folder(folder_path: str) -> list[str]:
    files_list = []
    try:
        # List all files in the specified folder
        for filename in os.listdir(folder_path):
            # Construct full file path
            file_path = os.path.join(folder_path, filename)
            # Check if it's a file (not a directory)
            if os.path.isfile(file_path):
                if ".csv" in filename:
                    filename = filename.replace(".csv","")
                    files_list.append(filename)
    except FileNotFoundError:
        print(f"Folder not found: {folder_path}")
    except PermissionError:
        print(f"Permission denied: {folder_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return files_list


