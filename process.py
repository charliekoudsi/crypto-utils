import pandas as pd
import numpy as np
import requests
from pykalman import KalmanFilter

def process(asset_x, asset_y, asset_x_file, asset_y_file, mode='normal'):
    x_mult = _get_mult(asset_x)
    y_mult = _get_mult(asset_y)

    x = pd.read_csv(asset_x_file)
    y = pd.read_csv(asset_y_file)

    x.columns = ['time', 'x']
    y.columns = ['time', 'y']

    x.time = pd.to_datetime(x.time)
    y.time = pd.to_datetime(y.time)

    quotes = x.merge(y, on='time')
    if mode == 'normal':
        _process_normal(quotes)
        quotes = quotes.iloc[9650:]
    else:
        _process_kalman(quotes)
        quotes = quotes.iloc[1000:]
    
    quotes = quotes[['time', 'x', 'y', 'z']]
    return quotes

def _process_normal(quotes):
    quotes['alpha'], quotes['beta'] = _get_regression(quotes)
    quotes['spread'] = quotes.y - quotes.beta * quotes.x - quotes.alpha
    quotes['stdev'] = quotes.expanding().spread.std()
    quotes['z'] = quotes['spread']/quotes['stdev']

def _process_kalman(df):
    kf1 = KalmanFilter(transition_matrices = [1],
                  observation_matrices = [1],
                  initial_state_mean = 0,
                  initial_state_covariance = 1,
                  observation_covariance=1,
                  transition_covariance=.01)
    x_state_means, _ = kf1.filter(df.x.values)
    y_state_means, _ = kf1.filter(df.y.values)
    df['smooth_x'] = x_state_means
    df['smooth_y'] = y_state_means
    obs_mat = np.vstack([df.smooth_x,
                            np.ones(df.smooth_x.shape)]).T[:, np.newaxis]
    
    delta = 1e-5
    trans_cov = delta / (1 - delta) * np.eye(2)
    kf2 = KalmanFilter(n_dim_obs=1, n_dim_state=2,
                    initial_state_mean=np.zeros(2),
                    initial_state_covariance=np.ones((2, 2)),
                    transition_matrices=np.eye(2),
                    observation_matrices=obs_mat,
                    observation_covariance=1.0,
                    transition_covariance=trans_cov)
    reg_state, _ = kf2.filter(df.smooth_y.values)
    df['beta'], df['alpha'] = reg_state[:,0], reg_state[:,1]
    df['new_x'] = df['smooth_x'] * df['beta'] + df['alpha']
    df['spread'] = df['smooth_y'] - df['new_x']
    df['stdev'] = df.expanding().spread.std()
    df['z'] = df['spread']/df['stdev']


def _get_regression(df):
    window = 8650
    a = np.array([np.nan] * len(df))
    b = [np.nan] * len(df)  # If betas required.
    y_ = df.y.values
    x_ = df[['x']].assign(constant=1).values
    for n in range(window, len(df)):
        y = y_[(n - window):n]
        X = x_[(n - window):n]
        # betas = Inverse(X'.X).X'.y
        betas = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(y)
        b[n] = betas.tolist()[0]
        a[n] = betas.tolist()[1]  # If betas required.
    return (a, b)


def _get_mult(name):
    req = requests.get(f'https://ftx.com/api/markets/{name}-perp').json()['result']
    return req['ask']/req['bid']