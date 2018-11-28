# Overview:
This application tracks the price of petrol in the UK dated back to 2006, updated based on official weekly data from gov.uk
Inflation data is used to put context to the changes, as well as a point of reference for prices changes being above or below inflation rate changes. 

A hosted version of this application can be found at: https://petrolprices.johnlock.nl/

# Installation steps:
- `git clone https://github.com/john-lock/Sentiment.git`
- Setup virtualenv with `virtualenv venv` and activate with `source venv/bin/activate`
Install the requirements with `pip install -r requirements.txt`
- Finally run the application with `flask run`

To manually update the data, with the application running visit:
`/update` for 
`/clean`
`/date`
(Note: these ought to be done together, in the given order, for desired update of fuel data.)

`/inflation` for inflation data update

# TODO:
- Update tests
- Move update function from cron job to celery task/s
- Use data already captured to: 1) predict future change 2) quantify the relationship with inflation (and possibly oil prices)
- Use NL data to create a version for the Netherlands

# Data Sources:
- For Inflation data: https://www.ons.gov.uk/economy/inflationandpriceindices/
- For Fuel price data: https://www.gov.uk/government/statistical-data-sets/oil-and-petroleum-products-weekly-statistics
