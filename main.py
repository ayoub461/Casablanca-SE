import pandas as pd
import spf_old as psfo
import Support_funct as psf
import financial_functions as ff
import ff_old as ffo

def main():
    #Paths:
    path_Data_base = 'C:/Users/dl/Desktop/cse/cse_data'
    path_saving_folder = 'C:/Users/dl/Desktop/cse/analysis'

    recapitulative = {}

    '''Clean Data'''
    #Access the files and rename them to ticker's name.
    f_files = psf.get_files_in_folder(path_Data_base)
    
    
    if not f_files:
        print("No files found in the specified folder.")
        return
    
    for file in f_files :
        #rename file's names
        file_path, file_ext = psf.rename_file(path_Data_base, file)
        stock_name = file

        #Rename price column into Adj close.
        file_read0 = psfo.read_file(file_path)
        file_read1 = file_read0.iloc[:,:2]
        file_read2 = file_read1.rename(columns={'Price': stock_name})

        #set Date in Date fonmat        
        file_read2['Date'] = pd.to_datetime(file_read2["Date"])
        
        #formating data:
        file_read3 = psf.prepare_date(file_read2) 
        file_read3 = psf.set_closing_prices(file_read3, column_name=stock_name)


        '''Analyze Data'''        
        #Daily return
        portfolio, file_read4 = ff.calculate_daily_returns(file_read3)

        portfolio_sector0, df_sector_DL, df_sector_DL0 = ff.market_DR()
        

        M_excpected_return, beta = ff.calculate_beta(stock_name, df_sector_DL,file_read4 )

        medaf = ff.medaf(M_excpected_return, beta)
        risk = ff.risk_stock(file_read4)
        
        #Cumulative return
        file_read5, total_CR = ff.calculate_cumulative_returns(file_read4)
        number_ofDays = psf.days_number(file_read5)
        annulized_return = ff.annualized_return(total_CR, number_ofDays)
        
        #portfolio, beta, medaf, risk, Cumulative return, annulized return
        
        recapitulative[stock_name] = {**portfolio, **beta, **medaf, **risk,  **total_CR, **annulized_return}
        
            
    recapitulative_df = pd.DataFrame.from_dict(recapitulative, orient='index')
    recapitulative_df.to_csv(f'{path_saving_folder}/recapitulative.csv')

if __name__ == "__main__":
    main()
