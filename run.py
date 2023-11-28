import pandas as pd
import ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from binance import Client
apikey = 'TaTUeZHEGREyyZK1GpRJlEeLOIZbgfpwZ8tjNR4wVJB8IZKh8mHtVEclaateunJr'
secretkey = 'v6kpZIN5uyWmmQIIjF5b9lsMjDLWRhGhnWzX5JCaLtjo3TiZhQbjO73s7A2VyU4e'
client = Client(apikey,secretkey)

def getdata(symbol, start, timeframe):
    frame = pd.DataFrame(client.get_historical_klines(symbol, timeframe, start))
    frame = frame[[0,1,2,3,4]]
    frame.columns = ['Date', 'Open', 'High', 'Low', 'Close']
    frame.Date = pd.to_datetime(frame.Date, unit='ms')
    frame.set_index('Date', inplace=True)
    frame = frame.astype(float)
    return frame
results = []
symbols = ['WINGUSDT', 'BNBUSDT', 'ETHUSDT', 'LTCUSDT']
timeframes = ['1m', '5m', '15m']

for symbol in symbols:
    for timeframe in timeframes:
        df = getdata(symbol, '2023-01-01', timeframe)
        class DataTrader(Strategy):
            def init(self):
                close = self.data.Close
                self.macd = self.I(ta.trend.macd, pd.Series(close))
                self.macd_signal = self.I(ta.trend.macd_signal, pd.Series(close))
                self.ema_100 = self.I(ta.trend.ema_indicator, pd.Series(close), window=100)

            def next(self):
                price = self.data.Close
                if crossover(self.macd, self.macd_signal) and price > self.ema_100:
                    sl = price * 0.945
                    tp = price * 1.12
                    self.buy(sl=sl, tp=tp)
        bt = Backtest(df,DataTrader, cash=10000, commission=0.0015)
        output = bt.run()
        result = {
            'Symbol': symbol,
            'Timeframe': timeframe,
            'Duration': output['Duration'],
            'Equity Peak [$]': output['Equity Peak [$]'],
            'Return [%]': output['Return [%]'],
            'Max. Drawdown [%]': output['Max. Drawdown [%]'],
            '# Trades': output['# Trades'],
            'Win Rate [%]': output['Win Rate [%]']
        }
        results.append(result)

df_results = pd.DataFrame(results)
df_results.to_csv('resu.csv', index=False)
print(df_results)

