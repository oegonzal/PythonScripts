
# OR you can do: # ! /usr/bin/env python
# and it will call the python listed first in you PATH variable!

# use conda install package_name to install new packages to conda

from setup import *
from yahoo_finance import Share
import time

print("Importing fetchData file...")

def getPendingPredictions(options):
    query="SELECT p.* FROM predictions p WHERE p.status = '" + options['status'] + "'"
    
    data = getQuery(query)

    updates = []

    # from datetime import date, timedelta
    # yesterday = date.today() - timedelta(1)
    # datetime.strptime(day_data['Date'], '%Y-%m-%d')
    # https://pypi.python.org/pypi/yahoo-finance
    # print(yahoo.get_historical('2017-04-27', '2017-05-03'))
    for row in data:
        id = row[0]
        prediction_start_date = row[2]
        prediction_end_date = row[6]
        stock_symbol = row[1]

        print(stock_symbol)
        
        today_date = datetime.today()
        prediction_price = row[4];
        
        
        stock = Share(stock_symbol)
        historical_data = stock.get_historical(prediction_start_date.strftime('%Y-%m-%d'), today_date.strftime('%Y-%m-%d'))

        successful_prediction = False
        for day_data in historical_data:
            if(prediction_price <= float(day_data['High']) and prediction_end_date <= today_date):
                successful_prediction = True
                updates.append(('Success', str(id)))
                break

        if(not successful_prediction and prediction_end_date < today_date):
            updates.append(('Failure', str(id)))
            
        time.sleep(1)

    print(updates)

    if(len(updates) > 0):
        success_query="UPDATE predictions SET status = '%s' WHERE id = '%s'"
        config = {
        'user': 'root',
        'password':'root',
        'host':'127.0.0.1',
        'database':'tradesDB'
        }
        conn = mysql.connector.connect(**config)

        c = conn.cursor()
        c.executemany(query, updates)

        print ("Number of rows updated:",  c.rowcount)
        
        conn.close()
        

def getQuery(query):
    config = {
        'user': 'root',
        'password':'root',
        'host':'127.0.0.1',
        'database':'tradesDB'
        }

    conn = mysql.connector.connect(**config)

    c = conn.cursor()
    
    c.execute('set autocommit=1')
    c.execute('set global max_allowed_packet=1073741824;')
    c.execute(query)

    data = c.fetchall()
    
    conn.close()
    return data

def constructYFURL(ticker,start_date,end_date,freq):
    #start_date = datetime.strptime(start_date,"%Y-%m-%d").date()
    #end_date = datetime.strptime(end_date,"%Y-%m-%d").date()

    s=ticker.replace("^","%5E")

    if start_date.month-1<10:
        a="0"+str(start_date.month-1)
    else:
        a=str(start_date.month-1)
    # a represents the month portion - however the month count starts from 0
    # Also the month always has 2 digits
    b=str(start_date.day)

    c=str(start_date.year)
    # b and c represent the day and year parts of the start date
    if end_date.month - 1 < 10:
        d = "0" + str(end_date.month - 1)
    else:
        d = str(end_date.month - 1)
    # similarly we have to set up the month part for the end date
    e=str(end_date.day)

    f=str(end_date.year)
    # e and f represent the day and year parts of the end date
    g=freq
    # g represents the frequency d = daily, w= weekly, m=monthly

    # Finally let's set up the URL

    yfURL = "http://real-chart.finance.yahoo.com/table.csv?s="+s+"&a="+a+"&b="+b+"&c="+c+"&d="+d+"&e="+e+"&f="+f+"&g="+g+"&ignore=.csv"
    return yfURL

