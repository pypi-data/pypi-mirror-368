#!/usr/bin/env python3

from fire import Fire
import os
from cmd_ai import config # , key_enter, topbar, unitname
import pandas as pd
import datetime as dt

def show_budget( budget):
    print()
    if os.path.exists(  os.path.expanduser(config.CONFIG['pricelog'] ) ):
        # dateparse = lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
        df = pd.read_csv( os.path.expanduser(config.CONFIG['pricelog']) ,
                          delim_whitespace=True,
                          names = ['date','time', 'in','out','price']
                         )#, parse_dates=['datetime'], date_parser=dateparse)

        df['datetime'] = pd.to_datetime(df.date)
        df['year'] = pd.to_datetime(df.date).apply(lambda x:x.year)
        df['month'] = pd.to_datetime(df.date).apply(lambda x:x.month)
        df['price'] = df['price'].clip(lower=0.01)
        #df.index = df['datetime']
        #df['priced'] = df.groupby(df['datetime'])['price'].sum()
        #print(df)
        df1 = df.groupby('month', sort=False).agg({'datetime':'last','price':'sum'})# , 'in':'sum','out':'sum'
        #df1 = df1.groupby('month', sort=False).agg({'datetime':'last','price':'sum'})# , 'in':'sum','out':'sum'
        #print(df1)
        # first by mothn
        df = df.groupby('datetime',sort=False).agg({'price':'sum', 'in':'sum','out':'sum','year':'first','month':'first'})

        if budget:
            print("____________________________________Grouped by month:")
            print(df1)#.iloc[-30:-1,:]  )
        nowmonth = dt.datetime.now().month
        dfnow = df.loc[ df['month']== nowmonth ]
        if len(dfnow)>0:
            print("____________________________________ This month:")
            print( dfnow)#.iloc[-30:-1,:]  )
        print("____________________________________")

if __name__=="__main__":
    Fire(main)
