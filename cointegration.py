import pandas as pd
import numpy as np
from statsmodels.regression.linear_model import OLS
from statsmodels.tsa.tsatools import lagmat, add_trend
from statsmodels.tsa.adfvalues import mackinnonp


class Tester:
    def __init__(self):
        pass

    def _adf(self, ts, maxlag=1):
        """
        Augmented Dickey-Fuller unit root test
        """
        # make sure we are working with an array, convert if necessary
        ts = np.asarray(ts)
        
        # Get the dimension of the array
        nobs = ts.shape[0]
            
        # Calculate the discrete difference
        tsdiff = np.diff(ts)
        
        # Create a 2d array of lags, trim invalid observations on both sides
        tsdall = lagmat(tsdiff[:, None], maxlag, trim='both', original='in')
        # Get dimension of the array
        nobs = tsdall.shape[0] 
        
        # replace 0 xdiff with level of x
        tsdall[:, 0] = ts[-nobs - 1:-1]  
        tsdshort = tsdiff[-nobs:]
        
        # Calculate the linear regression using an ordinary least squares model    
        results = OLS(tsdshort, add_trend(tsdall[:, :maxlag + 1], 'c')).fit()
        adfstat = results.tvalues[0]
        
        # Get approx p-value from a precomputed table (from stattools)
        pvalue = mackinnonp(adfstat, 'c', N=1)
        # print(results.summary())
        return pvalue
 
    def _cadf(self, x, y):
        """
        Returns the result of the Cointegrated Augmented Dickey-Fuller Test
        """
        # Calculate the linear regression between the two time series
        ols_result = OLS(x, y).fit()
        # print(ols_result)
        # Augmented Dickey-Fuller unit root test
        return self._adf(ols_result.resid)
    
    def test(self, file1, file2):
        '''
        Runs an Augmented Dickey-Fuller Test to determine if
        two assets are cointegrated.

        A low p-value (< 0.01) indicates that there is 
        potentially a pairs-trading opportunity.

        Inputs:
            file1 (string): a filename corresponding to scraped data
            file2 (string): a filename corresponding to scraped(data)

        Outputs:
            p-value (float): The probability that the pair is not cointegrated
        '''
        df1 = pd.read_csv(file1)
        df1.time = pd.to_datetime(df1.time)
        df1.columns = ['time', 'x']

        df2 = pd.read_csv(file2)
        df2.time = pd.to_datetime(df2.time)
        df2.columns = ['time', 'y']

        df = df1.merge(df2, on='time')
        return self._cadf(df.x, df.y)

