////////////////////// Prerequisites //////////////////////

1. Python3 installed

    -https://www.python.org/downloads/

2. BeautifulSoup4 installed

    -https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup

3. "lxml" parser installed

    -https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser

    
////////////////////// Tableau Workbook Setup //////////////////////

1. Open the Tableau Workbook called "LogInToSnowFlake.twb".

2. Connect to Snowflake Datasource.

3. Select the Warehouse, Database, and Schema that contains your Salesforce tables.

4. Open the command line and navigate to this directory.

5. Run the command "python3 twb_conversion.py".

6. For each workbook in the "Workbooks" directory, open and log in to your Snowflake datasource.

7. Done! You are now connected to your Salesforce data via a live connection to your Snowflake warehouse.


