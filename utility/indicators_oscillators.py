import pandas as pd
import numpy as np

class Oscillator:
    def __init__(self, dataframe):
        self.df = dataframe

    def rsi_14(self):
        delta = self.df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.df['RSI_14'] = 100 - (100 / (1 + rs))
        return self.df['RSI_14']

    def stochastic_k_14_3_3(self):
        low_min = self.df['low'].rolling(window=14).min()
        high_max = self.df['high'].rolling(window=14).max()
        self.df['%K'] = 100 * (self.df['close'] - low_min) / (high_max - low_min)
        self.df['%D'] = self.df['%K'].rolling(window=3).mean()
        return self.df[['%K', '%D']]

    def cci_20(self):
        tp = (self.df['high'] + self.df['low'] + self.df['close']) / 3
        sma = tp.rolling(window=20).mean()
        mean_dev = (tp - sma).abs().rolling(window=20).mean()
        self.df['CCI_20'] = (tp - sma) / (0.015 * mean_dev)
        return self.df['CCI_20']

    def adx_14(self):
        plus_dm = self.df['high'].diff()
        minus_dm = self.df['low'].diff()
        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
        minus_dm = -minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
        tr = pd.concat([
            self.df['high'] - self.df['low'],
            abs(self.df['high'] - self.df['close'].shift()),
            abs(self.df['low'] - self.df['close'].shift())
        ], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean()
        plus_di = (plus_dm.rolling(window=14).mean() / atr) * 100
        minus_di = (minus_dm.rolling(window=14).mean() / atr) * 100
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        self.df['ADX_14'] = dx.rolling(window=14).mean()
        return self.df['ADX_14']

    def calculate_dmi(self, period=14):

        if not isinstance(period, int) or period <= 0:
          raise ValueError(f"The period must be a positive integer. period value:- {period}")

        high = self.df['high']
        low = self.df['low']
        close = self.df['close']

        # Calculate price moves
        up_move = high.diff()
        down_move = low.diff().abs()

        # Calculate directional movements
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (low.shift(1) > low), down_move, 0.0)

        # True Range (TR)
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Average True Range (ATR)
        atr = tr.rolling(window=period).sum()

        # +DI and -DI
        plus_di = 100 * pd.Series(plus_dm).rolling(window=period).sum() / atr
        minus_di = 100 * pd.Series(minus_dm).rolling(window=period).sum() / atr

        # DX and ADX
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        adx = dx.rolling(window=period).mean()

        dmi = plus_di - minus_di
        # Create DataFrame with the results
        # dmi_df = pd.DataFrame({'+DI': plus_di, '-DI': minus_di, 'ADX': adx})
        self.df['DMI'] = pd.DataFrame({'DMI': dmi})

        return self.df['DMI']

    def awesome_oscillator(self):
        median_price = (self.df['high'] + self.df['low']) / 2
        self.df['AO'] = median_price.rolling(window=5).mean() - median_price.rolling(window=34).mean()
        return self.df['AO']

    def momentum_10(self):
        self.df['Momentum_10'] = self.df['close'].diff(periods=10)
        return self.df['Momentum_10']

    def macd_12_26(self):
        short_ema = self.df['close'].ewm(span=12, adjust=False).mean()
        long_ema = self.df['close'].ewm(span=26, adjust=False).mean()
        self.df['MACD'] = short_ema - long_ema
        self.df['Signal_Line'] = self.df['MACD'].ewm(span=9, adjust=False).mean()
        return self.df[['MACD', 'Signal_Line']]

    def stochastic_rsi(self):
        rsi = self.rsi_14()
        rsi_min = rsi.rolling(window=14).min()
        rsi_max = rsi.rolling(window=14).max()
        self.df['Stoch_RSI'] = (rsi - rsi_min) / (rsi_max - rsi_min)
        return self.df['Stoch_RSI']

    def williams_percent_r(self):
        high_max = self.df['high'].rolling(window=14).max()
        low_min = self.df['low'].rolling(window=14).min()
        self.df['%R'] = -100 * ((high_max - self.df['close']) / (high_max - low_min))
        return self.df['%R']

    def bull_bear_power(self):
        ema = self.df['close'].ewm(span=13, adjust=False).mean()
        self.df['Bull_Power'] = self.df['high'] - ema
        self.df['Bear_Power'] = self.df['low'] - ema
        return self.df[['Bull_Power', 'Bear_Power']]

    def ultimate_oscillator(self):
        min_prev_close_or_low = pd.concat([self.df['low'], self.df['close'].shift()], axis=1).min(axis=1)
        bp = self.df['close'] - min_prev_close_or_low
        tr = pd.concat([
            self.df['high'] - self.df['low'],
            abs(self.df['high'] - self.df['close'].shift()),
            abs(self.df['low'] - self.df['close'].shift())
        ], axis=1).max(axis=1)
        avg7 = bp.rolling(window=7).sum() / tr.rolling(window=7).sum()
        avg14 = bp.rolling(window=14).sum() / tr.rolling(window=14).sum()
        avg28 = bp.rolling(window=28).sum() / tr.rolling(window=28).sum()
        self.df['UO'] = (4 * avg7 + 2 * avg14 + avg28) / 7 * 100
        return self.df['UO']

class Oscillator_Status:
    @staticmethod
    def get_status(value, indicator, prev_value=None):
        if indicator == 'RSI_14':
            if value > 70:
                return 'Sell'
            elif value < 30:
                return 'Buy'
            else:
                return 'Neutral'

        elif indicator == '%K':
            if value > 80:
                return 'Sell'
            elif value < 20:
                return 'Buy'
            else:
                return 'Neutral'

        elif indicator == 'CCI_20':
            if value > 100:
                return 'Sell'
            elif value < -100:
                return 'Buy'
            else:
                return 'Neutral'

        elif indicator == 'Stoch_RSI':
            if value > 0.8:
                return 'Sell'
            elif value < 0.2:
                return 'Buy'
            else:
                return 'Neutral'

        elif indicator == '%R':
            if value > -20:
                return 'Sell'
            elif value < -80:
                return 'Buy'
            else:
                return 'Neutral'

        elif indicator == 'Bull_Power' or indicator == 'Bear_Power':
            if abs(value) < 0.05:
                return 'Neutral'
            elif value > 0:
                return 'Buy'
            else:
                return 'Sell'

        elif indicator == 'UO':
            if value > 70:
                return 'Sell'
            elif value < 30:
                return 'Buy'
            else:
                return 'Neutral'

        elif indicator == 'MACD':
            if np.isclose(value, 0, atol=0.02):
                return 'Neutral'
            return 'Buy' if value > 0 else 'Sell'

        elif indicator == 'DMI':
            if np.isclose(value, 0, atol=0.0001):
                return 'Neutral'
            if prev_value is not None and value > prev_value:
                return 'Buy'
            elif prev_value is not None and value < prev_value:
                return 'Sell'
            return 'Neutral'

        return 'Neutral'

    @staticmethod
    def dmi_status(dmi_df):


        # print(df.index[-1])

        # latest_idx = df.index[-1]
        # prev_idx = df.index[-2]
        # dmi_df = dmi_df.iloc[-2:]
        curr_value = (dmi_df['DMI'].values)[-1]
        prev_value = (dmi_df['DMI'].values)[-2]
        # curr_value = dmi_df.loc[-1, '+DI'] - dmi_df.loc[-1, '-DI']
        # prev_value = dmi_df.loc[-2, '+DI'] - dmi_df.loc[-2, '-DI']

        if np.isclose(curr_value, 0, atol=0.0001):
                return 'Neutral'
        elif curr_value > prev_value:
            return 'Buy'
        else:
            return 'Sell'



