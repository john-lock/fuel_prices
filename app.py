from flask import Flask, render_template, Markup
import requests
import datetime
import plotly
import csv
import os
import re
import tablib
import plotly.graph_objs as go
from bs4 import BeautifulSoup
import pandas as pd
from plotly.offline import plot
from plotly.graph_objs import Scatter

app = Flask(__name__)


@app.route('/')
def index():
    df = pd.read_csv('data_inflation.csv', sep=',')

    trace1 = Scatter(
        x=df['Date'],
        y=df['PumpPriceD'],
        name="Petrol Price",
        fill="tozeroy")

    trace2 = Scatter(
        x=df['Date'],
        y=df['DutyP'],
        name="Duty rate(pence/litre)",
        fill="tozeroy")

    trace3 = Scatter(
        x=df['Date'],
        y=df['inflation'],
        name="Inflation",
        yaxis='y2')

    data = [trace1, trace2, trace3]
    layout = go.Layout(
    title='UK Fuels Prices 2006-present',
    showlegend=True,
    xaxis=dict(
        type='category',
    ),
    yaxis=dict(
        type='linear',
        title='Price per litre',
        range=[1, 150],
        dtick=20,
        ticksuffix='p'
    ),
    yaxis2=dict (
        overlaying='y',
        title='Inflation rate',
        side='right',
        showgrid=False,
        ticksuffix='%'))
    fig = dict(data=data, layout=layout)
    # a = py.plot(data, output_type='div')
    a = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')

    # stats
    table_len = len(df['PumpPriceP'])
    this_week = df['PumpPriceP'][(table_len - 1)]
    last_week = df['PumpPriceP'][(table_len - 2)]
    change = float(this_week) - float(last_week)
    week_change = change / float(last_week) * 100
    print(week_change)

    return render_template('index.html', a=Markup(a), this_week=this_week, week_change=week_change, last_week=last_week)


dataset = tablib.Dataset()
with open(os.path.join(os.path.dirname(__file__), 'data_new.csv')) as f:
    dataset.csv = f.read()


@app.route('/update')
def update():
    base_url = 'https://www.gov.uk/government/statistical-data-sets/oil-and-petroleum-products-weekly-statistics'
    page = requests.get(base_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    section = soup.find_all('div', class_='attachment-details')
    pattern = re.compile(r'[\/]\w+[\/]\w+[\/]\w+[\/]\w+[\/]\w+[\/]\w+[\/]\d+[\/][C][S][V][.][c][s][v][\/]')
    extra_url_raw = pattern.findall(str(section))
    extra_url = (", ".join(extra_url_raw))
    url = 'https://www.gov.uk' + extra_url + "preview"
    for i, df in enumerate(pd.read_html(url)):
        df.to_csv('data_new.csv')

    raw_data = pd.read_csv('data_new.csv', sep=',')
    data = raw_data.tail()
    return render_template('update.html', data=data)


@app.route('/clean')
def clean():
    # Remove blank columns
    with open('data_new.csv', 'r') as inputfile:
        rdr = csv.reader(inputfile)
        with open('data_clean.csv', 'w') as outputfile:
            wtr = csv.writer(outputfile)
            for row in rdr:
                try:
                    if int(row[0]) >= 1:
                        wtr.writerow((row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
                except ValueError:
                    print("Removed: " + str(row))

    return render_template('clean.html')


# Reformat date and set Headers, Add inflation
@app.route('/date')
def date():
    with open('data_clean.csv', 'r') as inputfile:
        rdr = csv.reader(inputfile)
        with open('data_date.csv', 'w') as outputfile:
            wtr = csv.writer(outputfile)
            # reformat date
            for row in rdr:
                try:
                    date_format = datetime.datetime.strptime(row[0], '%d/%m/%Y').strftime('%Y-%m-%d')
                    wtr.writerow((date_format, row[1], row[2], row[3], row[4], row[5], row[6]))

                except ValueError:
                    wtr.writerow(("Date", "PumpPriceP", "PumpPriceD", "DutyP", "DutyD", "VatP", "VatD"))

        return render_template('date.html')


@app.route('/inflation')
def inflation():
    url = 'https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/l55o/mm23'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    data = []
    index_infl_start = 0
    table = soup.find_all('tr')
    for tr in table:
        td = tr.find_all('td')
        # Find index of where relevent inflation dates start (2006 JAN)
        if '2006 JAN' in str(td):
            index_infl_start = table.index(tr)
        data.append(td)
    inflation_data = data[int(index_infl_start):]

    # convert to clean array list (['MM/YYYY'],[Inflation rate])
    inflation_data_clean = []
    for x in inflation_data:
        inflation_data_clean.append(str(x))
    finaldata = []
    month_dict = {"JAN": "01",
                  "FEB": "02",
                  "MAR": "03",
                  "APR": "04",
                  "MAY": "05",
                  "JUN": "06",
                  "JUL": "07",
                  "AUG": "08",
                  "SEP": "09",
                  "OCT": "10",
                  "NOV": "11",
                  "DEC": "12"}
    for i in inflation_data_clean:
        year = i[5:9]
        month_raw = i[10:13]
        month = month_dict[month_raw]
        inflation = (i[24:27])
        item = [[year + '-' + month], [inflation]]
        finaldata.append(item)

    # add inflation to relevent column
    with open('data_date.csv', 'r') as inputfile:
        rdr = csv.reader(inputfile)
        with open('data_inflation.csv', 'w') as outputfile:
            wtr = csv.writer(outputfile)
            for row in rdr:
                if row[0][0] != str(2):
                    row.append("inflation")
                    wtr.writerow(row)
                else:
                    date = row[0][0:7]
                    for x in finaldata:
                        if date in x[0]:
                            infl = (str(x[1]))
                            infl_rate = infl[2:5]
                            row.append(infl_rate)
                            wtr.writerow(row)
    return render_template('date.html', data=finaldata)


if __name__ == '__main__':
    app.run()


# Title, Axis labels/Key

# Run clean to get update, then app.py 
# Inflation adjusted

