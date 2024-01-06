# requires these installs once
# pip install yfinance

import sys

import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score

def predict_binary(train, test, predictors, model):
    model.fit(train[predictors], train['Target'])
    preds = model.predict(test[predictors]) # generate predictions 0 or 1
    preds = pd.Series(preds, index=test.index, name='Predictions') # convert to series from array
    combined = pd.concat([test['Target'], preds], axis=1) # combine actual values with predicted values
    return combined

def predict_proba(train, test, predictors, model):
    model.fit(train[predictors], train['Target'])
    # instead of 0 or 1, "proba" returns probability of going up or down
    preds = model.predict_proba(test[predictors])[:,1]
    
    # set custom threshold: requires higher confidence (60%) that the change will be positive
    # this way we will reduce the number of trades
    preds[preds >= 0.6] = 1 
    preds[preds < 0.6] = 0
    
    preds = pd.Series(preds, index=test.index, name='Predictions') # convert to series from array
    combined = pd.concat([test['Target'], preds], axis=1) # combine actual values with predicted values
    return combined

def backtest(data, model, predictors, start=2500, step=250, IsBinary=False):
    all_predictions = []

    for i in range(start, data.shape[0], step):
        train = data.iloc[0:i].copy()
        test = data.iloc[i:(i+step)].copy()
        if IsBinary: predictions = predict_binary(train, test, predictors, model)
        else: predictions = predict_proba(train, test, predictors, model)
        all_predictions.append(predictions)
    return pd.concat(all_predictions)

def func_random_forest(symbol, start_date, end_date, first_model_obs, step, n_estimators, min_samples_split, random_state, IsBinary):
    
    # get S&P500 ETF benchmark from Yahoo Finance
    sp500 = yf.download(symbol, start_date, end_date)
    
    # Create target for predictions: positive change (1) or negative (0)
    sp500['Close_next_day'] = sp500['Adj Close'].shift(-1)
    sp500 = sp500[sp500['Close_next_day'].notnull()]
    sp500['Target'] = (sp500['Close_next_day'] > sp500['Adj Close']).astype(int)

    # create new predictions by computing return and trend over various rolling windows such as 2 days, 5 days, etc.
    horizons = [2,5,60,250,1000]
    predictors = []
    
    for horizon in horizons:
        # compute rolling average of prices
        rolling_averages = sp500.rolling(horizon).mean()
    
        # compute return over the rolling window
        ratio_column = f"Close_Ratio_{horizon}"
        sp500[ratio_column] = sp500['Close'] / rolling_averages['Close']
    
        # compute the sum of the Target to represent the trend
        trend_column = f"Trend_{horizon}"
        sp500[trend_column] = sp500.shift(1).rolling(horizon).sum()['Target']
    
        # add return and trend to new predictors
        predictors += [ratio_column, trend_column]
    
    # remove missing rows
    sp500 = sp500.dropna()

    # Random Forest Classifier
    model = RandomForestClassifier(n_estimators=n_estimators, min_samples_split=min_samples_split, random_state=random_state)

    # compute predictions
    predictions = backtest(sp500, model, predictors)
    
    # measure the accuracy of the model: ranges from 0.0 to 1.0
    print("Accuracy of predictions:", precision_score(predictions['Target'], predictions['Predictions']).round(2))

    # number of days
    print("Fraction of positive and negative days: \n", (predictions['Target'].value_counts() / predictions.shape[0]).round(2))
    print("Number of predicted positive and negative days: \n", predictions['Predictions'].value_counts())    

# format Inputs
symbol = sys.argv[1]
start_date = sys.argv[2]
end_date = sys.argv[3]
first_model_obs = int(sys.argv[4])
step = int(sys.argv[5])
n_estimators = int(sys.argv[6])
min_samples_split = int(sys.argv[7])

print(sys.argv)

# always same
IsBinary = False # predict binary (0 or 1) or probability of positive or negative change
random_state = 1 # set random state at 1 to ensure the model can be replicated (the same random numbers would be produced if the model runs again)

# test User Inputs
#symbol = '^HSI'
#start_date = '2003-01-02'
#end_date = '2023-12-31'
#first_model_obs = 2500 # measured in days; ~ 10 years
#step = 250 # measured in days; ~ for each year
#n_estimators = 200 # number of decision trees; higher number improves the model to certain degree but runs longer
#min_samples_split = 50 # protect from overfitting by setting min_samples_split at 50; high is less accurate but smaller chance of overfitting

# run the function
func_random_forest(symbol, start_date, end_date, first_model_obs, step, n_estimators, min_samples_split, random_state, IsBinary)

