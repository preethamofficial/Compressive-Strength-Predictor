import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM

def run_ann(data, num_predictions):
    window_size = 3
    X, y = [], []
    for i in range(len(data) - window_size):
        X.append(data[i:i+window_size])
        y.append(data[i+window_size])
    X = np.array(X).reshape(-1, window_size, 1)
    y = np.array(y)
    model = Sequential()
    model.add(LSTM(32, activation='relu', input_shape=(window_size,1)))
    model.add(Dense(16, activation='relu'))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=200, verbose=0)
    predictions = []
    last_seq = data[-window_size:].reshape(1, window_size, 1)
    for _ in range(num_predictions):
        next_val = model.predict(last_seq, verbose=0)
        predictions.append(next_val[0,0])
        last_seq = np.append(last_seq[:,1:,:], [[next_val]], axis=1)
    return predictions

def predict_future(values, n):
    """
    values: 1D array-like of past CTM floats
    n: number of future predictions to produce
    Returns a plain Python list of n floats.
    Strategy: linear trend fit if >=2 points, otherwise repeat last value.
    """
    vals = np.asarray(values, dtype=float)
    if n <= 0:
        return []
    if vals.size == 0:
        return [0.0] * n
    if vals.size == 1:
        return [float(vals[0])] * n

    # use linear regression on indices -> values
    x = np.arange(vals.size)
    try:
        p = np.polyfit(x, vals, 1)
        slope, intercept = p[0], p[1]
        last_idx = vals.size - 1
        preds = [(slope * (last_idx + i + 1) + intercept) for i in range(n)]
    except Exception:
        # fallback: use average difference
        diffs = np.diff(vals)
        avg_diff = float(np.mean(diffs)) if diffs.size > 0 else 0.0
        last = float(vals[-1])
        preds = [last + avg_diff * (i + 1) for i in range(n)]

    return [float(x) for x in preds]

# alias for compatibility with views that try .predict(...)
def predict(values, n=None):
    # if n not provided, return single-step prediction
    if n is None:
        n = 1
    return predict_future(values, int(n))