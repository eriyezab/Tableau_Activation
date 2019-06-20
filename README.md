<<<<<<< HEAD
////////////////////////////////////////////////////////////////// Prerequisites //////////////////////////////////////////////////////////////////

1. Python 2 installed(already installed on Mac OSX)

    -If you are having trouble with this step, visit: https://www.python.org/downloads/

  
///////////////////////////////////////////////////////////// Tableau Workbook Setup /////////////////////////////////////////////////////////////

1. Open the Tableau Workbook called "LogInToSnowFlake.twb".

2. Connect to Snowflake Datasource.

3. Select the Warehouse, Database, and Schema that contains your Salesforce tables and then save the workbook. DO NOT CHANGE THE NAME OF THIS WORKBOOK!

IF ON MAC:

    4. Right-click "wkbk_conversion.py" and hover over "Open With" and click "Python Launcher"

IF NOT ON MAC:

    4. Open the command line and navigate to this directory via the terminal.

    4.5. Run the command "python wkbk_conversion.py".

5. If 'ImportError: No such module as bs4" occurs, simply repeat step 4.

6. For each workbook in the "Workbooks" directory, open it and it will prompt you to log in to your Snowflake datasource.

7. Done! You are now connected to your Salesforce data via a live connection to your Snowflake warehouse.
=======
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


>>>>>>> 7a24d5670b98b1e72a350cc0e4799f7c8c87b701
