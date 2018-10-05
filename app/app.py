from flask import Flask, render_template, Markup, redirect
import json
import requests
import datetime
import plotly
import csv
import os
import tablib
import plotly.graph_objs as go
import csv
from bs4 import BeautifulSoup

import pandas as pd
from plotly.offline import plot
from plotly.graph_objs import Scatter

app = Flask(__name__)


@app.route('/')
def index():
    df = pd.read_csv('data_date.csv', sep=',')

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

    data = [trace1, trace2]
    layout = go.Layout(
    showlegend=True,
    xaxis=dict(
        type='category',
    ),
    yaxis=dict(
        type='linear',
        range=[1, 150],
        dtick=20,
        ticksuffix='p'
    ))
    fig = dict(data=data, layout=layout)
    # a = py.plot(data, output_type='div')
    a = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')

    # stats
    l = len(df['PumpPriceP'])
    this_week = df['PumpPriceP'][(l - 1)]

    return render_template('index.html', a=Markup(a), this_week=this_week)


dataset = tablib.Dataset()
with open(os.path.join(os.path.dirname(__file__),'data_new.csv')) as f:
    dataset.csv = f.read()


@app.route('/update')
def update():
    url = "https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/744680/CSV.csv/preview"
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
        with open('data_clean.csv','w') as outputfile:
            wtr = csv.writer(outputfile)
            for row in rdr:
                try:
                    if int(row[0]) >= 1:
                        wtr.writerow((row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
                except ValueError:
                    print("Removed: " + str(row))

    return render_template('clean.html')


# Reformat date and set Headers
@app.route('/date')
def date():
    with open('data_clean.csv', 'r') as inputfile:
        rdr = csv.reader(inputfile)
        with open('data_date.csv', 'w') as outputfile:
            wtr = csv.writer(outputfile)
            for row in rdr:
                try:
                    date_format = datetime.datetime.strptime(row[0], '%d/%m/%Y').strftime('%Y-%m-%d')
                    wtr.writerow((date_format, row[1], row[2], row[3], row[4], row[5], row[6]))

                except ValueError:
                    wtr.writerow(("Date", "PumpPriceP", "PumpPriceD", "DutyP", "DutyD", "VatP", "VatD"))

        return render_template('date.html')


if __name__ == '__main__':
    app.run()


# Title, Axis labels/Key



# Run clean to get update, then app.py 
# Inflation adjusted
# overlay oil price
