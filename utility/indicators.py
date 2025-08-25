import pandas as pd
import numpy as np
from typing import Dict, Optional, Any

class CrossoverDetector:
    """
    Detects crossovers between two series and provides optional volatility filtering.
    """
    def __init__(self, settings: Dict[str, Any], adx_indicator: Optional[Any] = None):
        self.crossover_enabled = settings.get("crossover_enabled", True)
        self.volatility_filter_enabled = settings.get("volatility_filter_enabled", True)
        self.adx_threshold = settings.get("adx_threshold", 18)
        self.lookback_period = settings.get("lookback_period", 5)
        self.adx_indicator = adx_indicator
        self.crossovers = []

    def detect(self, df: pd.DataFrame, series1_name: str, series2_name: str, type: str):
        if not self.crossover_enabled:
            return

        series1 = df[series1_name]
        series2 = df[series2_name]
        
        if type == "supertrend":
            bullish_crossover = (series1.shift(1) == False) & (series1 == True)
            bearish_crossover = (series1.shift(1) == True) & (series1 == False)
        else:
            bullish_crossover = (series1.shift(1) < series2.shift(1)) & (series1 > series2)
            bearish_crossover = (series1.shift(1) > series2.shift(1)) & (series1 < series2)

        adx_values = df['ADX'] if 'ADX' in df.columns and self.volatility_filter_enabled else None

        for i in range(len(df)):
            signal = None
            if bullish_crossover.iloc[i]:
                signal = 'BULLISH'
            elif bearish_crossover.iloc[i]:
                signal = 'BEARISH'

            if signal:
                adx_value = adx_values.iloc[i] if adx_values is not None else None
                if not self.volatility_filter_enabled or (adx_value is not None and adx_value > self.adx_threshold):
                    self.crossovers.append({
                        "type": signal,
                        "index": df.index[i],
                        "price": df['close'].iloc[i],
                        "adx_value": adx_value
                    })

    def get_latest(self) -> Optional[Dict[str, Any]]:
        if not self.crossovers:
            return None
        
        latest_crossover = self.crossovers[-1]
        
        # Check if the latest crossover is within the lookback period
        if self.lookback_period is not None:
            latest_crossover_index = self.crossovers[-1]['index']
            if isinstance(latest_crossover_index, (int, np.integer)):
                 # Assuming integer-based indexing
                if latest_crossover_index < len(self.crossovers) - self.lookback_period:
                    return None
            else: # Assuming datetime-based indexing
                # This part would need a reference to the full dataframe index, 
                # which is complex to handle here.
                # A simpler approach is to check from the end of the list.
                pass

        return latest_crossover

class ADX:

    def __init__(self, adx_period=14, crossover_settings: Optional[Dict[str, Any]] = None):

        self.adx_period  = adx_period
        self.initial_run = True
        self.need_recalc = False
        self.crossover_detector = CrossoverDetector(crossover_settings or {}, self) if crossover_settings else None
        pass

    def calculate(self, df):
        df = df.copy()
        current_index = len(df)

        if self.initial_run or self.need_recalc:
            self.previous_index = current_index
            self.initial_run = False
            high = df['high']
            low = df['low']
            close = df['close']

            # Calculate directional movements
            plus_dm  = high.diff()
            minus_dm = low.diff()

            plus_dm  = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0)
            minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0)

            # Calculate True Range (TR)
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.DataFrame([tr1, tr2, tr3]).max()

            # Smooth the values
            tr_smooth = pd.Series(tr).rolling(window=self.adx_period).sum()
            plus_di = 100 * pd.Series(plus_dm).rolling(window=self.adx_period).sum() / tr_smooth
            minus_di = 100 * pd.Series(minus_dm).rolling(window=self.adx_period).sum() / tr_smooth

            # Calculate ADX
            dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
            adx = dx.rolling(window=self.adx_period).mean()
            plus_di, minus_di, adx = df.index, df.index, df.index

            df['+DI'] = plus_di
            df['-DI'] = minus_di
            df['ADX'] = adx

            if self.crossover_detector:
                self.crossover_detector.detect(df, '+DI', '-DI', 'dmi')

            return  df['+DI'], df['-DI'], df['ADX']
        else:
            start_idx = max(self.previous_index - self.adx_period + 1, 0)
            window_df = df.iloc[start_idx:current_index]

            high = window_df['high']
            low = window_df['low']
            close = window_df['close']

            # Calculate directional movements
            plus_dm = high.diff()
            minus_dm = low.diff()

            plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0)
            minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0)

            # Calculate True Range (TR)
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.DataFrame([tr1, tr2, tr3]).max()

            # Smooth the values
            tr_smooth = pd.Series(tr).rolling(window=self.adx_period).sum()
            plus_di = 100 * pd.Series(plus_dm).rolling(window=self.adx_period).sum() / tr_smooth
            minus_di = 100 * pd.Series(minus_dm).rolling(window=self.adx_period).sum() / tr_smooth

            # Calculate ADX
            dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
            adx = dx.rolling(window=self.adx_period).mean()

            df.update({'+DI': plus_di})
            df.update({'-DI': minus_di})
            df.update({'ADX': adx})

            if self.crossover_detector:
                self.crossover_detector.detect(df, '+DI', '-DI', 'dmi')

            return df['+DI'], df['-DI'], df['ADX']

    def get_latest_crossover(self) -> Optional[Dict[str, Any]]:
        if self.crossover_detector:
            return self.crossover_detector.get_latest()
        return None



class Stochastic_Oscillator:

    def __init__(self, k_period=7, k_smooth=3, d_period=3, crossover_settings: Optional[Dict[str, Any]] = None, adx_indicator: Optional[ADX] = None):

        self.k_period = k_period
        self.k_smooth = k_smooth
        self.d_period = d_period
        self.initial_run = True
        self.need_recalc = False
        self.crossover_detector = CrossoverDetector(crossover_settings or {}, adx_indicator) if crossover_settings else None

    def calculate(self, df):

        df = df.copy()
        current_index = len(df)

        if self.initial_run or self.need_recalc:
            self.previous_index = current_index
            self.initial_run = False

            low_min = df['low'].rolling(window=self.k_period).min()
            high_max = df['high'].rolling(window=self.k_period).max()

            # Raw %K
            percent_k = 100 * (df['close'] - low_min) / (high_max - low_min)

            # Smoothed %K (Fast %D)
            percent_k_smoothed = percent_k.rolling(window=self.k_smooth).mean()

            # Smoothed %D (Slow %D)
            percent_d = percent_k_smoothed.rolling(window=self.d_period).mean()
            percent_k_smoothed.index = df.index
            percent_d.index = df.index

            df['%K'] = percent_k_smoothed
            df['%D'] = percent_d

            if self.crossover_detector:
                self.crossover_detector.detect(df, '%K', '%D', 'stochastic')

            return  df['%K'], df['%D']

        else:
            start_idx = max(self.previous_index - self.k_period + 1, 0)
            window_df = df.iloc[start_idx:current_index]

            low_min = window_df['low'].rolling(window=self.k_period).min()
            high_max = window_df['high'].rolling(window=self.k_period).max()

            # Raw %K
            percent_k = 100 * (window_df['close'] - low_min) / (high_max - low_min)

            # Smoothed %K (Fast %D)
            percent_k_smoothed = percent_k.rolling(window=self.k_smooth).mean()

            # Smoothed %D (Slow %D)
            percent_d = percent_k_smoothed.rolling(window=self.d_period).mean()


            df.update({'%K': percent_k_smoothed})
            df.update({'%D': percent_d})

            if self.crossover_detector:
                self.crossover_detector.detect(df, '%K', '%D', 'stochastic')

            return df['%K'], df['%D']
        
    def get_latest_crossover(self) -> Optional[Dict[str, Any]]:
        if self.crossover_detector:
            return self.crossover_detector.get_latest()
        return None
        



class ATRBands:

    def __init__(self, atr_period=7, atr_multiplier=2.3 ):
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier

        self.need_recalc = False
        self.initial_run = True


    def calculate(self, df):

        df_calc = df.copy()

        current_index = len(df)

        if not all(col in df.columns for col in ['high', 'low', 'close']) or len(df) < self.atr_period:
            return pd.Series(index=df.index, dtype=float)

        if self.initial_run or self.need_recalc:
            self.previous_index = current_index

            hl2 = (df_calc['high'] + df_calc['low']) / 2

            high_low = df_calc['high'] - df_calc['low']
            high_close_prev = (df_calc['high'] - df_calc['close'].shift(1)).abs()
            low_close_prev = (df_calc['low'] - df_calc['close'].shift(1)).abs()

            tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
            # df_calc['tr'] = tr

            atr = tr.ewm(alpha=1 / self.atr_period, adjust=False, min_periods=self.atr_period).mean()
            df_calc['atr_value'] = atr

            df_calc['upperband'] = hl2 + (self.atr_multiplier * atr)

            df_calc['lowerband'] = hl2 - (self.atr_multiplier * atr)


            # debug_print(f"ATR calculated for period {self.atr_period}.")

            return df_calc['atr_value'], df_calc['upperband'], df_calc['lowerband']

        else:

            start_idx = max(self.previous_index - self.atr_period + 1, 0)
            window_df = df_calc.iloc[start_idx:current_index]

            high_low = window_df['high'] - window_df['low']
            high_close_prev = (window_df['high'] - window_df['close'].shift(1)).abs()
            low_close_prev = (window_df['low'] - window_df['close'].shift(1)).abs()

            hl2 = (window_df['high'] + window_df['low']) / 2

            tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
            atr = tr.ewm(alpha=1 / self.atr_period, adjust=False, min_periods=self.atr_period).mean()

            upperband_value  = hl2 + (self.atr_multiplier * atr)
            lowerband_value  = hl2 - (self.atr_multiplier * atr)

            # df_calc['high_close_prev']
            # df_calc['low_close_prev']
            # df_calc['high_low']

            # df_calc.update({'high_close_prev': high_close_prev})
            # df_calc.update({'low_close_prev': low_close_prev})
            # df_calc.update({'high_low': high_low})
            # df_calc.update({'tr': tr})
            df_calc.update({'atr_value': atr})
            df_calc.update({'upperband': upperband_value})
            df_calc.update({'lowerband': lowerband_value})
            return df_calc['atr_value'], df_calc['upperband'], df_calc['lowerband']



class SupertrendIndicator:

    def __init__(self, name="ST", period=10, multiplier=3.0, crossover_settings: Optional[Dict[str, Any]] = None, adx_indicator: Optional[ADX] = None):

        self.suptertrend_period = period
        self.atr_multiplier = multiplier
        self.need_recalc = False
        self.initial_run = True
        self.crossover_detector = CrossoverDetector(crossover_settings or {}, adx_indicator) if crossover_settings else None
        pass


    def calculate(self, df):
        if not all(col in df.columns for col in ['high', 'low', 'close']):
            raise ValueError(f"{self.name}: OHLC columns ('high', 'low', 'close') required.")

        df = df.copy()
        current_index = len(df)
        hl2 = (df['high'] + df['low']) / 2

        if self.initial_run or self.need_recalc:

            self.previous_index = current_index
            self.initial_run = False
            high_low = df['high'] - df['low']
            high_close_prev = (df['high'] - df['close'].shift(1)).abs()
            low_close_prev = (df['low'] - df['close'].shift(1)).abs()
            df['high_close_prev'] = high_close_prev
            df['low_close_prev'] = low_close_prev
            df['high_low'] = high_low

            tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)

            atr = tr.ewm(alpha=1 / self.suptertrend_period, adjust=False, min_periods=self.suptertrend_period).mean()

            upperband = hl2 + (self.atr_multiplier * atr)
            lowerband = hl2 - (self.atr_multiplier * atr)

            supertrend = pd.Series([np.nan] * len(df))
            direction  = pd.Series([True] * len(df))

            for i in range(self.suptertrend_period, len(df)):

                if df['close'][i] > upperband.iloc[i - 1]:
                    supertrend.iloc[i] = lowerband.iloc[i]
                    direction.iloc[i]  = True
                elif df['close'][i] < lowerband.iloc[i - 1]:
                    supertrend.iloc[i] = upperband.iloc[i]
                    direction.iloc[i]  = False
                else:
                    supertrend.iloc[i] = supertrend.iloc[i - 1]
                    direction.iloc[i]  = direction.iloc[i - 1]

            supertrend, direction = df.index, df.index
            df['supetrend'] = supertrend #pd.Series(supertrend)
            df['direction'] = direction  #pd.Series(direction)

            if self.crossover_detector:
                self.crossover_detector.detect(df, 'direction', None, 'supertrend')

            return  df['supetrend'], df['direction']

        else:
            pass
            start_idx = max(self.previous_index - self.suptertrend_period + 1, 0)
            window_df = df.iloc[start_idx:current_index]  # 15 (last calcted 14) -> 16 : 16-5 +1 = 11 10 ->
            hl2 = (window_df['high'] + window_df['low']) / 2
            atr = window_df['high'].combine(window_df['low'], max) - window_df['low'].combine(window_df['high'], min)
            atr = atr.rolling(window=self.suptertrend_period).mean()

            upperband = hl2 + (self.atr_multiplier * atr)
            lowerband = hl2 - (self.atr_multiplier * atr)

            supertrend = pd.Series([np.nan] * len(window_df))
            direction  = pd.Series([True] * len(window_df))  # True = Bullish, False = Bearish

            # resume_index = self.suptertrend_period if self.initial_run or self.need_recalc else self.resume_index

            for i in range(self.suptertrend_period, len(window_df)):

                if window_df['close'][i] > upperband.iloc[i - 1]:
                    supertrend.iloc[i] = lowerband.iloc[i]
                    direction.iloc[i] = True
                elif window_df['close'][i] < lowerband.iloc[i - 1]:
                    supertrend.iloc[i] = upperband.iloc[i]
                    direction.iloc[i] = False
                else:
                    supertrend.iloc[i] = supertrend.iloc[i - 1]
                    direction.iloc[i]  = direction.iloc[i - 1]
                pass

            # df.update({'atr': atr})
            df.update({'supetrend': pd.Series(supertrend)})
            df.update({'direction': pd.Series(direction)})

            if self.crossover_detector:
                self.crossover_detector.detect(df, 'direction', None, 'supertrend')

            return df['supetrend'], df['direction']
        
    def get_latest_crossover(self) -> Optional[Dict[str, Any]]:
        if self.crossover_detector:
            return self.crossover_detector.get_latest()
        return None
        pass



# prompt: Add a type instance check if it is 1d then use this :gain = pd.Series(gain).rolling(window=self.rsi_period).mean()
#             loss = pd.Series(loss).rolling(window=self.rsi_period).mean()
#    else use current approach `gain = pd.Series(gain[:, 0]).rolling(window=14).mean()
#   loss = pd.Series(loss[:, 0]).rolling(window=14).mean()`

# RSI
import numpy as np

class RSI:

    def __init__(self, rsi_period=14):

        self.initial_run = True
        self.need_recalc = False
        self.rsi_period  = rsi_period
        self.previous_index = 0

        pass

    def calculate(self, df_org):

        df = df_org.copy()
        current_index = len(df)
        if self.initial_run or self.need_recalc:
            self.previous_index = current_index
            self.initial_run = False

            delta = df['close'].diff()
            gain  = np.where(delta > 0, delta, 0)
            loss  = np.where(delta < 0, -delta, 0)

            # gain = pd.Series(gain).rolling(window=self.rsi_period).mean()
            # loss = pd.Series(loss).rolling(window=self.rsi_period).mean()

            # Check if gain and loss are 1-dimensional arrays
            gain = pd.Series(gain).rolling(window=self.rsi_period).mean()
            loss = pd.Series(loss).rolling(window=self.rsi_period).mean()
            # if len(gain.shape) == 1:
            #     gain = pd.Series(gain).rolling(window=self.rsi_period).mean()
            #     loss = pd.Series(loss).rolling(window=self.rsi_period).mean()
            # else:
            #     # Original approach for multi-dimensional arrays
            #     gain = pd.Series(gain[:, 0]).rolling(window=self.rsi_period).mean()
            #     loss = pd.Series(loss[:, 0]).rolling(window=self.rsi_period).mean()

            rs  = gain / loss
            rsi = 100 - (100 / (1 + rs))
            df['rsi'] = rsi
            rsi.index = df.index  # align index

            return rsi

        else:
            start_idx = max(self.previous_index - self.rsi_period + 1, 0)
            window_df = df.iloc[start_idx:current_index]
            delta = window_df['close'].diff()
            gain  = np.where(delta > 0, delta, 0)
            loss  = np.where(delta < 0, -delta, 0)

            gain = pd.Series(gain).rolling(window=self.rsi_period).mean()
            loss = pd.Series(loss).rolling(window=self.rsi_period).mean()
            # Check if gain and loss are 1-dimensional arrays
            # if len(gain.shape) == 1:
            #     gain = pd.Series(gain).rolling(window=self.rsi_period).mean()
            #     loss = pd.Series(loss).rolling(window=self.rsi_period).mean()

            # else:
            #     # Original approach for multi-dimensional arrays
            #     gain = pd.Series(gain[:, 0]).rolling(window=self.rsi_period).mean()
            #     loss = pd.Series(loss[:, 0]).rolling(window=self.rsi_period).mean()

            rs  = gain / loss
            rsi = 100 - (100 / (1 + rs))
            # rsi.reset_index(drop=True, inplace=True)
            # self.previous_index = current_index
            # self.need_recalc = False
            # rsi.index = df.index  # align index

            df.update({'rsi': rsi})
            return df['rsi']

#
