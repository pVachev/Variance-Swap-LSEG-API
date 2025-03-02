import pandas as pd
import numpy as np
from LSEG_Fetch_Data import spx_data, ndx_data, start_date, end_date

class VarianceSwap:
    def __init__(self, underlying, df, date_column, value_column, start_date, maturity, N_vega, K_vol):
        
        # Parameters:
        #   underlying   : Name of the underlying index (e.g., 'SPX', 'NDX').
        #   df           : DataFrame containing the price data.
        #   date_column  : Name of the date column in the DataFrame.
        #   value_column : Name of the price column in the DataFrame.
        #   start_date   : Start date of the swap period (YYYY-MM-DD string).
        #   maturity     : Maturity date of the swap period (YYYY-MM-DD string).
        #   N_vega       : Vega notional (USD per volatility point).
        #   K_vol        : Strike volatility (in percentage points).
     
        self.underlying = underlying
        self.df = df
        self.date_column = date_column
        self.value_column = value_column
        self.start_date = pd.Timestamp(start_date)
        self.maturity = pd.Timestamp(maturity)
        self.N_vega = N_vega
        self.K_vol = K_vol
        

        self.num_days = None
        self.realized_variance = None
        self.variance_notional = None
        self.variance_strike = None
        self.payoff = None
        self.period_df = self.compute_period_df()
    
    def compute_period_df(self):
        #  this was computed separately in attempt to plot for the second trade without defining it separately 
        period_df = self.df[(self.df[self.date_column] >= self.start_date) & 
                            (self.df[self.date_column] <= self.maturity)].copy()
        period_df.sort_values(self.date_column, inplace=True)
        

        period_df['LogReturn'] = np.log(period_df[self.value_column] / period_df[self.value_column].shift(1))
        
        return period_df




    def compute_realized_variance(self):
        
        # Computes the annualized realized variance over the swap period.
        # Uses the formula:
        #     Realized Variance = (252 / N) * sum( (ln(S_i/S_(i-1)))^2 )
        
       
        # Filter data for the period [start_date, maturity] and sort by date
        period_df = self.df[(self.df[self.date_column] >= self.start_date) &
                            (self.df[self.date_column] <= self.maturity)].copy()
        period_df.sort_values(self.date_column, inplace=True)
        
        
        period_df['LogReturn'] = np.log(period_df[self.value_column] / period_df[self.value_column].shift(1))
        
        period_df.dropna(subset=['LogReturn'], inplace=True)
        
        self.num_days = len(period_df)
        self.realized_variance = (252 / self.num_days) * np.sum(period_df['LogReturn'] ** 2) * 10000 # multiplied by 10000 to get the rifht amount for realized variance 
        return self.realized_variance

    def compute_swap_parameters(self):
       
        # Computes the variance swap parameters:
        #   Variance notional: N_var = N_vega / (2 * K_vol)
        #   Variance strike:  K_var = (K_vol)^2
        
        self.variance_notional = self.N_vega / (2 * self.K_vol)
        self.variance_strike = self.K_vol ** 2
        return self.variance_notional, self.variance_strike

    def compute_payoff(self):
      
        # Computes the swap payoff:
        #     Payoff = Variance Notional * (Realized Variance - Variance Strike)
        
       
        if self.realized_variance is None:
            self.compute_realized_variance()
        if self.variance_notional is None or self.variance_strike is None:
            self.compute_swap_parameters()
        self.payoff = self.variance_notional * (self.realized_variance - self.variance_strike)
        return self.payoff

    def summary(self):

        # Print summary function 
    
        # Ensure all metrics are computed
        if self.payoff is None:
            self.compute_payoff()
        summary_str = (
            f"Underlying: {self.underlying}\n"
            f"Trade Period: {self.start_date.date()} to {self.maturity.date()} (Days used: {self.num_days})\n"
            f"Realized Variance: {self.realized_variance:.4f}\n"
            f"Variance Notional: {self.variance_notional:.2f} USD per variance point\n"
            f"Variance Strike: {self.variance_strike:.4f}\n"
            f"Payoff: {self.payoff:.2f} USD\n"
        )
        return summary_str


# Inputs



trade1 = VarianceSwap(
    underlying='SPX',
    df=spx_data,
    date_column='Date',
    value_column='.SPX',
    start_date=start_date,
    maturity=end_date,
    N_vega=100000,   # USD by default
    K_vol=21.85     # in percentage
)

trade2 = VarianceSwap(
    underlying='NDX',
    df=ndx_data,
    date_column='Date',
    value_column='.NDX',
    start_date=start_date,
    maturity=end_date,
    N_vega=65000,    # USD by default
    K_vol=19.65      # in percentage
)







print("=== Trade 1 (SPX) ===")
print(trade1.summary())

print("=== Trade 2 (NDX) ===")
print(trade2.summary())


