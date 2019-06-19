import os
import sys
from bs4 import BeautifulSoup
import re

def parse_freshbook(workbook) -> tuple:
    """This function takes in a newly created tableau workbook that has been connected to the schema in snowflake that they would like the
    salesforce notebooks to be connected to.
    """
    items = []

    print(os.getcwd())
    with open(workbook, 'r') as wkbk:
        soup = BeautifulSoup(wkbk, "lxml-xml")

    try:
        federated = soup.datasource['name']
        snowflake = soup.datasource.find('named-connection')['name']
        connection = soup.datasources.prettify()
        connection = connection.split('\n')
        for i in range(len(connection)):
            connection[i] = '   ' + connection[i]
        connection[7] = connection[7] + '\n'
        connection = '\n'.join(connection[2:8])
    except:
        print('The tableau workbook is not connected to a snowflake datasource.')
        sys.exit()
    try:
        schema = soup.datasource.connection.connection['schema']
    except:
        print('The tableau workbook is not connected to a snowflake schema. Please ensure that you have connected to a\
Warehouse, Database, and the Schema that contains your Salesforce information.')
        sys.exit()
    return federated, snowflake, schema, connection
    

 
def fivetran_shift(name: str) -> str:
    """Takes a name and returns it in a fivetran column format
    """
    # Replace international characters with similar ASCII characters
    name = ascii(name.strip())

    # // The Han-Latin transliteration introduces a ' ' character after a '.' character
    name = name.replace(". ", ".")
    pe = re.compile("[^\\w\\d'\"]")
    # // Replace all illegal characters
    name = pe.sub("_", name.strip())

    # split on capital letters
    name = "_".join(re.findall("[A-Z0-9][^A-Z0-9]*", name))
    # // Convert to lower_case and get rid of trailing apostrophe
    name = name[:-1].lower()

    w = re.compile("[\\w_]")

    # // Require that it start with a word character
    if not name == '' and w.match(name) is None:
         name = "_" + name

    return name


# TODO: Create the function that parses an xml or twb file and writes a new one that is connected to snowflake
def modify_xml(workbook) -> None:
    """Take a Tableau workbook that is connected to a Fivetran Table and Salesforce
    and fixes the column names
    """
    # create a variable to hold the lines of the file
    statement = []
    # open the workbook in a readable format and read each line
    with open(workbook, 'r') as fp:
        soup = BeautifulSoup(fp, "lxml-xml")

    end = len(soup.find_all('datasource')[1]['name'])
    
    with open(workbook, 'r') as wkbk:
        
        line = wkbk.readline()

        while line:
            # STEPS
            # TODO: Change the datasource to the federated snowflake link
            # TODO: Change named-connection to the snowflake link
            if "datasource caption=" in line and 'inline=' in line and 'salesforce' in line:                
                statement.append(datasource)
                line = wkbk.readline()
                statement.append(connection)
                line = wkbk.readline()
                line = wkbk.readline()
                line = wkbk.readline()
                line = wkbk.readline()
                line = wkbk.readline()
                line = wkbk.readline()
            elif 'salesforce.' in line:
                while 'salesforce.' in line:
                    sf_index = line.index('salesforce.')
                    if 'login.salesforce.com' in line:
                        sf_index -= 6
                        end_index = line.index('\' ')
                        line = line[:sf_index] + 'Snowflake (Salesforce)' + line[end_index:]
                        sf_index = line.index("name='salesforce.") + 6
                        end_index = sf_index + end
                        line = line[:sf_index] + federated_connection + line[end_index:]
                        
                    # TODO: Change all relation connections to the snowflake link and the table names to snowflake tables
                    elif "<relation connection='" in line:
                        table_index = line.index('table=\'[')
                        table_index += 8
                        table_name, rest = line[table_index:].split(']')
                        table_name = main_schema + '].[' + fivetran_shift(table_name).upper() + ']'
                        line = ''.join([line[:table_index], table_name, rest])
                        connection_index = line.index('=\'') + 2
                        end_index = line.index('\' name')
                        line = line[:connection_index] + snowflake_connection + line[end_index:]
                        # print(line)
                    else:
                        end_index = sf_index + end
                        line = line[:sf_index] + federated_connection + line[end_index:]
                statement.append(line)
                line = wkbk.readline()

            # TODO: change the join expressions to refer to the correct columns
            elif 'expression op=\'[' in line:
                front, back = line.split("'[")
                table, back = back.split('].[')
                column, back = back.split(']')
                reference = table
                column = fivetran_shift(column).upper()  
                back = ']'.join([column, back])  
                back = '].['.join([table, back])   
                line = "'[".join([front, back]) 
                statement.append(line)
                line = wkbk.readline()

            # TODO: Change the map values to the correct table names
            elif '<map key' in line:
                value_index = line.index('value=\'')
                value_index += 8
                map_part, value_part = line[:value_index], line[value_index:]
                table, value = value_part.split('].[')
                column, rest = value.split(']')
                reference = table
                # print(table, column)
                column = fivetran_shift(column).upper()
                value = ']'.join([column, rest])
                value_part = '].['.join([table, value])
                statement.append(''.join([map_part, value_part]))
                line = wkbk.readline()
            # Problem with top accounts that needed to be changed. Add a ZEROIFNULL to expected amount so that null values dont break the workbook when in live mode.
            elif ('calculation' in line or 'groupfilter' in line )and '[Expected Amount]' in line:
                expected_amount_index = line.index('[Expected Amount]')
                end_index = expected_amount_index + len('[Expected Amount]')
                line = line[:expected_amount_index] + 'ZN([Expected Amount])' + line[end_index:]
                statement.append(line)
                line = wkbk.readline()
            # ensure that extract enabled is false so that the workbook is automatically in live mode once connected. If it is already in live mode then the exception should
            # run because true will not be in the line.
            elif '<extract' in line:
                try:
                    enabled_index = line.index('true')
                    end_index = enabled_index + len('true')
                    line = line[:enabled_index] + 'false' + line[end_index:]
                    statement.append(line)
                    line = wkbk.readline()
                except ValueError:
                    statement.append(line)
                    line = wkbk.readline()
            else:
                statement.append(line)
                line = wkbk.readline()

        
        with open(workbook, 'w', newline='') as f:
            for item in statement:
                f.write(item)

        new_name = os.path.basename(workbook).split('.')
        new_name = new_name[0] + '.twb'
        os.rename(workbook, new_name)
        
        os.chdir('../')

new_workbook = './LogInToSnowflake.twb'
federated_connection, snowflake_connection, main_schema, connection = parse_freshbook(new_workbook)
datasource = "    <datasource caption='" + main_schema + "' inline='true' name='" + federated_connection + "' version='18.1'>\n"

if __name__ == "__main__":
    for wkbk in os.listdir('./Workbooks'):
        print(os.getcwd())
        if wkbk != '.DS_Store':
            os.chdir('./Workbooks')
            modify_xml(os.getcwd() + '/' + wkbk)