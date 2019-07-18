import os
import sys
import re
import subprocess

# Replaces a <old> with <new> <occurence> times starting from the right side of the string
def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

# installs <package> on the system
def install(package):
    """Function enables the script to install beautifulsoup and the xml parser if it is not already installed on the users computer.
    """
    try:
        subprocess.call([sys.executable, "-m", "pip", "install", "--user", package])
        print('pip')
    except:
        subprocess.call([sys.executable, "-m", "easy_install", "--user", package])
        print('easy')

# install beautifulsoup4, soupsieve and the xml parser
try:
    # try to install bs4 and the parsers
    install('beautifulsoup4')
    install('soupsieve')
    install('lxml')
except:
    # try again if there is an error
    install('beautifulsoup4')
    install('soupsieve')
    install('lxml')

from bs4 import BeautifulSoup

def parse_freshbook(workbook):
    """This function takes in a newly created tableau workbook that has been connected to the schema in snowflake that they would like the
    tableau workbooks to be connected to.
    """

    # open the workbook and parse it with beautiful soup
    with open(workbook, 'r') as wkbk:
        soup = BeautifulSoup(wkbk, "lxml-xml")

    try:
        federated = soup.datasource['name']
        snowflake = soup.datasource.find('named-connection')['name']
        caption = soup.datasource['caption']
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
        print('The tableau workbook is not connected to a snowflake schema. Please ensure that you have connected to the\
Warehouse, Database, and the Schema that contains your Salesforce data.')
        sys.exit()
    return federated, snowflake, caption, schema, connection
    

 
def fivetran_shift(name):
    """Takes a name and returns it in a fivetran column format
    """
    # Replace international characters with similar ASCII characters
    name = name.strip()

    # // The Han-Latin transliteration introduces a ' ' character after a '.' character
    name = name.replace(". ", ".")
    pe = re.compile("[^\\w\\d'\"]")
    # // Replace all illegal characters
    name = pe.sub("_", name.strip())

    # split on capital letters and numbers
    name = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', re.sub('([0-9]+)', r' \1 ', name))).split()
    
    # join on underscore
    name = '_'.join(name)
    # // Convert to lower_case and get rid of trailing apostrophe
    name = name[:].lower()

    w = re.compile("[\\w_]")

    # // Require that it start with a word character
    if not name == '' and w.match(name) is None:
         name = "_" + name

    # get rid of any double underscores if any
    name = re.sub('([_]+)', '_', name)
    return name


# TODO: Create the function that parses an xml or twb file and writes a new one that is connected to snowflake
def modify_xml(workbook):
    """Take a Tableau workbook that is connected to a Fivetran Table and Salesforce
    and fixes the column names
    """
    # create a variable to hold the lines of the file
    statement = []
    # open the workbook in a readable format and read each line
    with open(workbook, 'r') as fp:
        soup = BeautifulSoup(fp, "lxml-xml")

    # end is the length of the salesforce link that is in the tabelau salesforce starters
    try:
        old_caption = soup.datasource['caption'].encode('ascii','ignore')
        old_federated = soup.datasource['name'].encode('ascii','ignore')
        old_snowflake = soup.datasource.find('named-connection')['name'].encode('ascii','ignore')
    except:
        
        old_caption = soup.find_all('datasource')[1]['caption'].encode('ascii','ignore')
        old_federated = soup.find_all('datasource')[1]['name'].encode('ascii','ignore')
        old_snowflake = soup.find_all('datasource')[1].find('named-connection')['name'].encode('ascii','ignore')
    
    print(old_caption, old_federated, old_snowflake)
    
    
    with open(workbook, 'r') as wkbk:
        
        line = wkbk.readline()

        while line:
            if old_caption in line:
                line = line.replace(old_caption, new_caption)
            # replace the old_federated links with the new ones. It is possible that the old_snowflake link and the old_federated link are the same so only replace the federated 
            # link when it is not a relation connection tag as those tags are where the snowflake links go.
            if old_federated in line and "<relation connection='" not in line:
                line = line.replace(old_federated, federated_connection)
            # STEPS
            # TODO: Change the datasource to the federated snowflake link
            # TODO: Change named-connection to the snowflake link
            if "connection class=" in line:  
                statement.append(connection)
                line = wkbk.readline()
                line = wkbk.readline()
                line = wkbk.readline()
                line = wkbk.readline()
                line = wkbk.readline()
                line = wkbk.readline()        
            # TODO: Change all relation connections to the snowflake link and the table names to snowflake tables
            elif "<relation connection='" in line:
                if old_snowflake in line:
                    line = line.replace(old_snowflake, snowflake_connection)
                table_index = line.index('table=\'[')
                table_index += 8
                table_name, rest = line[table_index:].split(']')
                table = fivetran_shift(table_name).upper()
                line = rreplace(line, table_name, main_schema + '].[' + table, 1)
                # print(line)
                # These are the tables that do not have 'IsDeleted' fields in salesforce. We want all the fields that do have 'IsDeleted' to be a custom query that filters out the deleted fields
                if table not in ['APEX_CLASS', 'CASE_STATUS', 'CASE_TEAM_MEMBER', 'CASE_TEAM_ROLE', 'CASE_TEAM_TEMPLATE', 'CASE_TEAM_TEMPLATE_MEMBER', 'CASE_TEAM_TEMPLATE_RECORD', \
                    'EMAIL_TEMPLATE', 'GROUP', 'GROUP_MEMBER', 'LEAD_STATUS', 'LOGIN_HISTORY', 'OPPORTUNITY_STAGE', 'PARTNER_ROLE', 'PERIOD', 'RECORD_TYPE', 'TASK_PRIORITY', 'TASK_STATUS', \
                        'TERRITORY_2', 'USER', 'USER_ROLE', 'USER_TERRITORY_2_ASSOCIATION']:
                    table_index = line.index('table=\'[')
                    line = line[:table_index] + "type='text'>SELECT *&#10;FROM " + main_schema + "." + table + "&#10;WHERE NOT IS_DELETED</relation>"                   
                statement.append(line)
                line = wkbk.readline()

            # TODO: change the join expressions to refer to the correct columns
            elif 'expression op=\'[' in line:
                front, back = line.split("'[")
                table, back = back.split('].[')
                column, back = back.split(']')
                line = rreplace(line, column, fivetran_shift(column).upper(), 1)  
                statement.append(line)
                line = wkbk.readline()

            # TODO: Change the map values to the correct table names
            elif '<map key' in line:
                value_index = line.index('value=\'')
                value_index += 8
                map_part, value_part = line[:value_index], line[value_index:]
                table, value = value_part.split('].[')
                column, rest = value.split(']')
                # print(table, column)
                line = rreplace(line, column, fivetran_shift(column).upper(), 1)
                statement.append(line)
                line = wkbk.readline()
            # Problem with top accounts that needed to be changed. Add a ZEROIFNULL to expected amount so that null values dont break the workbook when in live mode.
            elif ('calculation' in line or 'groupfilter' in line ) and '[Expected Amount]' in line:
                line = line.replace('[Expected Amount]', 'ZN([Expected Amount])')
                statement.append(line)
                line = wkbk.readline()
            # ensure that extract enabled is false so that the workbook is automatically in live mode once connected. If it is already in live mode then the exception should
            # run because true will not be in the line. This should never be the case but just in case
            elif '<extract' in line:
                try:
                    line = line.replace('true', 'false')
                    statement.append(line)
                    line = wkbk.readline()
                except ValueError:
                    statement.append(line)
                    line = wkbk.readline()
            else:
                statement.append(line)
                line = wkbk.readline()

        # rewrite the tableau workbook with the lines in the statement list
        new_file = os.path.basename(workbook).split('.')
        new_file = new_file[0] + '_tmp.twb'
        with open(new_file, 'w') as f:
            for item in statement:
                f.write(item)
        
        # go back to the main directory
        os.chdir('../')


if __name__ == "__main__":
    new_workbook = './LogInToSnowflake.twb'
    federated_connection, snowflake_connection, new_caption, main_schema, connection = parse_freshbook(new_workbook)
    # print(connection)

    for wkbk in os.listdir('./Workbooks'):
        if '.xml' in wkbk or '.twb'  in wkbk:
            os.chdir('./Workbooks')
            print(wkbk)
            modify_xml(os.getcwd() + '/' + wkbk)
            print(wkbk.split('.')[0] + '.twb has been ported.')
        else:
            print(wkbk, 'is not in a proper format. Please ensure that this is the correct file and if it is then ensure that the file extension is *.twb or *.xml')