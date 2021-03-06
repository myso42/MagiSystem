# -*- coding: utf-8 -*-
# ref: https://www.quantopian.com/posts/trend-follow-algo

if __name__ == '__main__':
    import sys
    sys.path.append("..")
    from pyalgotrade import bar
    from pyalgotrade import plotter
# 以上模块仅测试用
import numpy as np
import pandas as pd

from pyalgotrade import strategy
from pyalgotrade.broker.backtesting import TradePercentage
from pyalgotrade.broker.fillstrategy import DefaultStrategy
from pyalgotrade.technical import hurst_RS
from pyalgotrade.tushare import data_from_tushare
from tools.performance_analyzer import performance_analyzer


class HurstStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, lookback_periods,smin=2,smax=233,step=1):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__feed = feed
        self.__instrument = instrument
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__lookbackPeriods = lookback_periods
        self.__lookback_periods_array = np.asarray(range(lookback_periods))
        self.__hurst = hurst_RS.HurstExponent(self.__prices, self.__lookbackPeriods,smin,smax,step)
        self.__i=0
        self.__ERS = hurst_RS.ERS(smin,smax,step)
        self.__longPos = None
        self.__shortPos = None
        self.__loopsize = smax
        self.getBroker().setFillStrategy(DefaultStrategy(None))
        self.getBroker().setCommission(TradePercentage(0.001))
        self.__j=0



    def getDateTimeSeries(self,instrument=None):
        #if instrument is None:
        #   __dateTime = pd.DataFrame()
        #   for element in self.__instrument:
        #       __dateTime = __dateTime.append(self.__feed[element].getPriceDataSeries().getDateTimes())
        #   __dateTime = __dateTime.drop_duplicates([0])
        #   return __dateTime.values #此时返回的为二维数组
        return self.__feed[self.__instrument].getPriceDataSeries().getDateTimes()

    def onEnterOk(self, position):
        self.addInfo(position.getEntryOrder())

    def onExitOk(self, position):
        # execInfo = position.getEntryOrder().getExecutionInfo()
        strategy.BacktestingStrategy.onExitOk(self,position)
        # self.info("BUY at $%.2f" % (execInfo.getPrice()))
        if self.__longPos == position:
            self.__longPos = None
        elif self.__shortPos == position:
            self.__shortPos = None
        else:
            assert(False)

    def onEnterCanceled(self, position):
        # self.__position = None
        if self.__longPos == position:
            self.__longPos = None
        elif self.__shortPos == position:
            self.__shortPos = None
        else:
            assert(False)

    def onBars(self, bars):
        # wait for enough bars to be available to calc regression lines
          if self.__hurst[-1] is None:
            return
          if self.__i >=5:
              if self.__prices[-1]>self.__prices[-1*self.__loopsize] and self.__longPos != None:
                  self.__longPos.exitMarket()
                  self.info("LONG close at $%.2f at %s" % (bars[self.__instrument].getPrice(),bars[self.__instrument].getDateTime()))
                  self.__i=0
              elif self.__prices[-1]<self.__prices[-1*self.__loopsize] and self.__longPos == None:
                 shares = int(self.getBroker().getEquity()*0.9  / bars[self.__instrument].getPrice())
                 self.__longPos = self.enterLong(self.__instrument, shares)
                 self.info("LONG open at $%.2f at %s" % (bars[self.__instrument].getPrice(),bars[self.__instrument].getDateTime() ))
                 self.__i=0

          elif self.__j>=5:
              if self.__prices[-1]<self.__prices[-1*self.__loopsize] and self.__longPos != None:
                  self.__longPos.exitMarket()
                  self.info("LONG close at $%.2f at %s" % (bars[self.__instrument].getPrice(),bars[self.__instrument].getDateTime()))
                  self.__j=0


              elif self.__prices[-1]>self.__prices[-1*self.__loopsize] and self.__longPos == None:
                 shares = int(self.getBroker().getEquity()*0.9  / bars[self.__instrument].getPrice())
                 self.__longPos = self.enterLong(self.__instrument, shares)
                 self.info("LONG open at $%.2f at %s" % (bars[self.__instrument].getPrice(),bars[self.__instrument].getDateTime() ))
                 self.__j=0


          if self.__hurst[-1]<self.__ERS:
             self.__i= self.__i+1
          else:
              self.__i = 0
          if self.__hurst[-1]>self.__ERS:
             self.__j= self.__j+1
          else:
              self.__j = 0







if __name__ == "__main__":
    strat = HurstStrategy
    instrument = '000001'
    market = 'SH'
    fromDate = '2014-07-01 09:35'
    toDate ='2016-02-03 15:00'
    frequency = bar.Frequency.DAY
    plot = True
    source = 'csv'

    #############################################path set ############################33
    if frequency == bar.Frequency.MINUTE_FIVE:
        path = "..//histdata//min//"
    elif frequency == bar.Frequency.DAY:
        path = "..//histdata//day//"
    filepath = path + instrument + market + ".csv"

    #############################################don't change ############################33
    from pyalgotrade.barfeed.csvfeed import GenericBarFeed

    if source == 'tushare':
        #barfeed = dataframe_barfeed.Feed(frequency)
        #barfeed =TuShareLiveFeed(['zh500'],Frequency.MINUTE_FIVE, 10000, 0)       #10000代表数据最大个数，1代表提取前2天的数据，0代表提取昨天数据，实时回测必须于九点半前开启
        data_df = data_from_tushare.get_kdata_from_tushare(instrument, fromDate, toDate)
        #barfeed.addBarsFromDataFrame(instrument, data_df)
    else:
        barfeed = GenericBarFeed(frequency)
        barfeed.setDateTimeFormat('%Y/%m/%d %H:%M')
        barfeed.addBarsFromCSV(instrument, filepath)
    ############################################Run the strategy#########################
    strat1 = strat(barfeed, instrument,240)
    performanceAnalyzer = performance_analyzer.performanceDataSet(strat1)
    if plot:
        plt = plotter.StrategyPlotter(strat1, True, True, True)
    strat1.run()
    performanceAnalyzer.printPerformaceInfo()
    performanceAnalyzer.getReturnsTearSheet(live_start_date=None)
