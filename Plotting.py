import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from Contract_Calculation_Payoff import trade1, trade2

def plot_variance_swap(trade, underlying_label, rolling_window=30):
   
    
    # Ensure all metrics are computed
    trade.compute_payoff()  # Updates realized_variance, variance_strike, payoff, etc.

    
    # Extract and clean data
    df = trade.period_df.copy()
    df.dropna(subset=['LogReturn'], inplace=True)
    
    # (A) Compute rolling variance in bps (annualized):
    # rolling_variance = (rolling mean of squared log returns) * 252 * 10000
    df['SquaredLogReturn'] = df['LogReturn']**2
    df['RollingVariance'] = df['SquaredLogReturn'].rolling(rolling_window).mean() * 252 * 10000
    
    # Use trade's computed values directly:
    realized_var_bps = trade.realized_variance   
    strike_bps = trade.variance_strike              
    payoff_usd = trade.payoff                       
    
    # Prepare the figure with three subplots
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), dpi=100)
    plt.suptitle(f"{underlying_label} Variance Swap Analysis", fontsize=14, y=1.05)
    
    # 1) Rolling Variance Over Time
    ax0 = axes[0]
    ax0.plot(df[trade.date_column], df['RollingVariance'],
             marker='o', ms=4, linestyle='-', label=f"{rolling_window}-Day Rolling Variance")
    ax0.axhline(strike_bps, color='red', linestyle='--',
                label=f"Variance Strike: {strike_bps:.2f} bps")
    ax0.set_title("Rolling Variance Over Time")
    ax0.set_xlabel("Date")
    ax0.set_ylabel("Variance (bps)")
    ax0.grid(True, linestyle=':', alpha=0.7)
    y_max = max(df['RollingVariance'].max(), strike_bps) * 1.1
    ax0.set_ylim(0, y_max)
    ax0.legend(loc="best")
    ax0.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=6))
    ax0.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))


 
    # 2) Variance Swap Payoff (Bar Chart)
 
    ax1 = axes[1]
    ax1.bar(["Realized Var", "Variance Strike"],
            [realized_var_bps, strike_bps],
            color='steelblue')
    ax1.set_title("Variance Swap Payoff")
    ax1.set_ylabel("Variance (bps)")
    # Annotate the payoff (in USD)
    bar_ymax = max(realized_var_bps, strike_bps)
    ax1.text(0.5, bar_ymax * 0.5, f"Payoff = {payoff_usd:,.2f} USD",
             ha='center', va='center', fontsize=10,
             bbox=dict(facecolor='white', alpha=0.7))
    ax1.set_ylim(0, y_max)
    
    # 3) Log Returns Distribution

    ax2 = axes[2]
    sns.histplot(df['LogReturn'], bins=40, kde=True, ax=ax2, color='cadetblue')
    ax2.set_title("Log Returns Distribution")
    ax2.set_xlabel("Log Return")
    ax2.set_ylabel("Frequency")
    
    plt.tight_layout()
    plt.show()



#
# Example calls:
plot_variance_swap(trade1, "SPX", rolling_window=30)
plot_variance_swap(trade2, "NDX", rolling_window=30)