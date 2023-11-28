import pandas as pd
import ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import matplotlib.pyplot as plt
from binance import Client

apikey = 'TaTUeZHEGREyyZK1GpRJlEeLOIZbgfpwZ8tjNR4wVJB8IZKh8mHtVEclaateunJr'
secretkey = 'v6kpZIN5uyWmmQIIjF5b9lsMjDLWRhGhnWzX5JCaLtjo3TiZhQbjO73s7A2VyU4e'

client = Client(apikey, secretkey)

def get_data(symbol, start, timeframe):
    frame = pd.DataFrame(client.get_historical_klines(symbol, timeframe, start))
    frame = frame[[0, 1, 2, 3, 4]]
    frame.columns = ['Date', 'Open', 'High', 'Low', 'Close']
    frame.Date = pd.to_datetime(frame.Date, unit='ms')
    frame.set_index('Date', inplace=True)
    frame = frame.astype(float)
    return frame

results = []
symbol = 'BTCUSDT'
timeframe = '1h'

df = get_data(symbol, '2023-04-01', timeframe)


class DataTrader(Strategy):
    def init(self):
        close = self.data.Close
        self.ema_50 = self.I(ta.trend.ema_indicator, pd.Series(close), window=50)
        self.stochastic = self.I(ta.momentum.stoch, pd.Series(self.data.High),
                                 pd.Series(self.data.Low), pd.Series(self.data.Close))

    def next(self):
        price = self.data.Close[-1]
        if crossover(self.stochastic, 20) and price > self.ema_50[-1]:
            sl = self.data.Low[-2] - 20
            tp = price * 1.03
            self.buy(sl=sl, tp=tp)
        elif self.stochastic[-1] < 80 and self.stochastic[-2] >= 80 and price < self.ema_50[-1]:
            sl = self.data.High[-2] + 20
            tp = price *0.97
            self.sell(sl=sl, tp=tp)


bt = Backtest(df, DataTrader, cash=100000, commission=0.0015)
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

df_results = pd.DataFrame(output)
df_results.to_csv('test.csv', index=False)
print(df_results)

bt.plot()
