#Overview:
This application tracks the price of petrol in the UK dated back to 2006, updated based on official weekly data from gov.uk
Inflation data is used to put context to the changes, as well as a point of reference for prices changes being above or below inflation rate changes. 


#TODO:
- Move update function from cron job to celery tasks
- Use recent and historical data to offer a prediction based on price changes, and relationship to inflation

#Data Sources:
- www.gov.uk for fuel price and inflation data