# requires these installs once
# pip install yfinance
# pip install PyPortfolioOpt
# pip install seaborn
# pip install scikit-learn

import sys

import yfinance as yf
from pypfopt import EfficientFrontier, objective_functions
from pypfopt import black_litterman, risk_models
from pypfopt import BlackLittermanModel #, plotting
from pypfopt import DiscreteAllocation
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def visualize_correlations(S):
    sns.heatmap(S.corr(), cmap='coolwarm').set_title('Stock return correlations');
    plt.show()
    plt.clf()

def visualize_market_implied_prior_returns(market_prior):
    market_prior.plot(kind='barh', title='Market Implied Prior Returns', figsize=(10,5));
    plt.show()
    plt.clf()

def visualize_posterior_views(rets_df):
    # column chart of Prior, Posterior, and Views
    rets_df.plot(kind='bar', title='Prior, Posterior, and Views', figsize=(12,8));
    plt.show()
    plt.clf()

def visualize_posterior_covariances(S_bl):
    sns.heatmap(S_bl.cov(), cmap='coolwarm').set_title('Black Litterman Covariances');
    plt.show()
    plt.clf()

def visualize_stock_final_weights(weights):
    pd.Series(weights).plot.pie(figsize=(6,6));
    plt.show()
    plt.clf()

def ComputePortfolioWeights(symbols, viewdict, confidences, start_date, end_date):

    # Step 1: Get Prices
    # download stock prices from Yahoo Finance
    portfolio = yf.download(symbols,start_date,end_date)['Adj Close']
    
    # get S&P500 ETF benchmark from Yahoo Finance
    market_prices = yf.download('SPY', start_date, end_date)['Adj Close']
    
    # get market cap for each stock in portfolio (will be needed for Black Litterman)
    mcaps = {}
    for t in symbols:
        stock = yf.Ticker(t)
        mcaps[t] = stock.info['marketCap']

    # Step 2: Compute Priors
    # calculate variance-covariance matrix (S) and implied risk aversion (delta) to get implied market returns
    # Ledoit-Wolf is a form of shrinkage for covariance matrix
    S = risk_models.CovarianceShrinkage(portfolio).ledoit_wolf()    
    delta = black_litterman.market_implied_risk_aversion(market_prices)
    #visualize_correlations(S)

    # compute market-implied prior returns
    market_prior = black_litterman.market_implied_prior_returns(mcaps, delta, S)
    #visualize_market_implied_prior_returns(market_prior)

    # Step 3: Integrate Views
    # Idzorek's method: specify a list of percentage confidences (high = high confidence) 
    
    # compute market-implied prior returns
    bl = BlackLittermanModel(S, pi=market_prior, market_caps=mcaps, risk_aversion=delta, absolute_views=viewdict, omega="idzorek", view_confidences=confidences)
    
    # Step 4: Calculate Posterior Return Estimates    
    # posterior estimate of returns
    ret_bl = bl.bl_returns()

    # visualize how posterior estimate of returns compares to the prior and user views:
    rets_df = pd.DataFrame([market_prior, ret_bl, pd.Series(viewdict)], index=['Prior','Posterior','Views']).T
    #visualize_posterior_views(rets_df)
    
    # compute posterior covariances
    S_bl = bl.bl_cov()
    #visualize_posterior_covariances(S_bl)

    # Step 5: Compute Portfolio Allocation Weights
    ef = EfficientFrontier(ret_bl, S_bl)
    ef.add_objective(objective_functions.L2_reg)
    ef.max_sharpe() # maximize Sharpe Ratio
    
    weights = ef.clean_weights()
    #visualize_stock_final_weights(weights)

    #print(ef.portfolio_performance(verbose=True, risk_free_rate=0.009))

    plt.show()
    return weights

# Format Inputs
tickers = (sys.argv[1]).split(",")
expectedIn = (sys.argv[2]).split(",")
expected = {}
for i in range(len(tickers)):
    expected[tickers[i]] = float(expectedIn[i])
confidences = (sys.argv[3]).split(",")
for i in range(len(confidences)):
    confidences[i] = float(confidences[i])

# Test User inputs
#tickers = ['AAPL','MSFT','META','AMZN','XOM','UNH','JNJ','V','HD','C']
#expected = {'AAPL':0.10,'MSFT':0.10,'META':0.05,'AMZN':0.12,'XOM':-0.30,'UNH':0.00,'JNJ':0.05,'V':0.11,'HD':0.10,'C':-0.2}
#confidences = [0.6,0.4,0.2,0.5, 0.7,0.8,0.7,0.5,0.1,0.4] # create confidence intervals

weights = ComputePortfolioWeights(tickers,expected,confidences,'2018-01-01','2023-11-30')

# Format output for js handling
output = " "
for x in weights:
    output += (str(weights[x]) + " ")
print(output)