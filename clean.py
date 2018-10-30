import csv
from bs4 import BeautifulSoup
import pandas as pd


url = "https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/744680/CSV.csv/preview"
for i, df in enumerate(pd.read_html(url)):
    df.to_csv('data_new.csv')

data = pd.read_csv('data_new.csv', sep=',')
print(data.head(10))