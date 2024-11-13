from pandas import DataFrame, errors
import version5.financial_functions as ff
import C_S_E.spf_old as psf
from typing import Tuple

def main():
    #Paths:
    path_Data_base = 'C:/Users/dl/Desktop/cse/cse_data'
    path_saving_folder = 'C:/Users/dl/Desktop/cse/analysis'


    '''Clean Data'''
    #Access the files and rename them to ticker's name.
    f_files = psf.get_files_in_folder(path_Data_base)
    print(f_files)







#Rename price column into Adj close.
#Do cleaning, (format, missing values...)





'''Analyze Data'''
'''Save Data'''


if __name__ == "__main__":
    main()
