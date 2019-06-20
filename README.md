////////////////////////////////////////////////////////////////// Prerequisites //////////////////////////////////////////////////////////////////

1. Python 2 installed(already installed on Mac OSX)

    -If you are having trouble with this step, visit: https://www.python.org/downloads/

  
///////////////////////////////////////////////////////////// Tableau Workbook Setup /////////////////////////////////////////////////////////////

1. Open the Tableau Workbook called "LogInToSnowFlake.twb".

2. Connect to Snowflake Datasource.

3. Select the Warehouse, Database, and Schema that contains your Salesforce tables and then save the workbook. DO NOT CHANGE THE NAME OF THIS WORKBOOK!

4. Open the command line("Command + Space" for Mac Users) and navigate to this directory.

5. Run the command "python wkbk_conversion.py".

6. For each workbook in the "Workbooks" directory, open it and it will prompt you to log in to your Snowflake datasource.

7. Done! You are now connected to your Salesforce data via a live connection to your Snowflake warehouse.


