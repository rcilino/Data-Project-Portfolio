#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""
Sportsrecruits-Front Rush File Handling.py
version 1.2.5
Created by Robert Cilino

Be good, do good, go Bills.
Be well, do well.

Changelog:
version 1.2.5
May 26, 2026
- Changed file path handling to use os.getcwd() to handle running the .py file portably from the unzipped file in the repository.

version 1.2.4
May 22, 2026
- Added better handling for culling past students to include current month and year compared to Class Year.
- Added a debug switch via variable and if statements, mainly used to stop renaming and moving source files.
- Improved Gender field handling based on source file name using case-insensitive matching.
- Improved file rename and move handling.
- Coach variable created blank to forego file errors.

version 1.2.3
May 21, 2026
- Added Source :: General field to input "SportsRecruits"
- Added Coach Comment :: General field to input "SportsRecruits" which is used in the messaging "Add Recipients" section to easily filter based on source.

version 1.2.2
May 20, 2026
- Clean input and match Sportsrecruits expectations imported dictionary of ISO3166 country codes/names.
- Remove State field value if country is not 'United States' or 'Canada', matching Sportsrecruits expectations.

version 1.2.1
May 19, 2026
- Formatting Phone columns as "xxx.xxx.xxxx".
- Removing utf-8 accent characters from Name fields.

version 1.2.0
May 14, 2026
- A 2nd Front Rush upload file to add Parent/Guardians into the Contacts section of Front Rush is now created upon completion.
- Reorganized export field column delete/rename section to combine dataframes in list before manipulating.
- Capitalized Recruit First and Last Name, no longer assuming intent.
- Capitalized Parent First and Last Name, no longer assuming intent.

version 1.1.1
May 12, 2026
- Rows where 'Class Year' is lower than current year are now removeds.
- Exception handling added to check first for files in Sportsrecruits exports folder /For Processing-Sportsrecruits Export/

version 1.1.0
May 10, 2026
- Added try/except in most locations.
- Processed files are now renamed to note their completion.
- Processed files are now moved to /For Processing-Sportsrecruits Export/Completed Processing

version 1.0.0
May 9, 2026

Future updates:
- Create a dictionary for column name changes instead of hard-coding each.
- Add new columns if Sportsrecruits includes more in the future.
    - Athlete Sex/Gender
    - Parent/Guardian 2 Name
    - Parent/Guardian 2 Email Address
    - Parent/Guardian 2 Phone Number
    - Club Team Name
    - Club Coach Name
    - Club Coach Email
    - Club Coach Phone
    - High School Team Name
    - High School Coach Name
    - High School Coach Email
    - High School Coach Phone

"""

print('File opened - importing packages, clearing lists and dataframes.')


# In[2]:


##### Debug switch
# Variable 'On' or 'Off' used in if statements for source file rename and source file move
# When Debug is 'On' the if statements will not allow the source file rename or file move
# This allows multiple runs without needing to comment/uncomment numerous lines, and without renaming and moving source files
Debug = 'Off'
print(f'Debug status is: {Debug}\n')

# Debug switch will stay on in the .ipnyb for writing but switched off for .py exports.


# In[3]:


# Import required modules
import sys
import os as os
import pathlib
import fnmatch
import csv
import pandas as pd
from datetime import datetime
import gc
import unicodedata
import requests
import numpy as np

# List imported modules
modulenames = set(sys.modules) & set(globals())
allmodules = [sys.modules[name] for name in modulenames]
print(f'Modules imported: {modulenames}\n')

# Set dataframe display option to display "all" rows
pd.set_option('display.max_rows', 1000)


# In[4]:


# Clear dataframe lists.
# Can be used for testing, but clears all data from dataframes to not interfere with the upcoming run.
try:
    print('The current dataframes in memory are:')
    get_ipython().run_line_magic('who', 'DataFrame')
    print()
except:
    print('%whos DataFrame did not execute properly')
    
try:
    dataframes.clear()
    print(dataframes)
    print('List "dataframes" cleared')
except NameError: 
    print('No list "dataframes" exists, moving on.')

try:
    del df_combined # Delete dataframe
    print('df_combined dataframe cleared')
except NameError:
    print('No dataframe "df_combined" exists, moving on.')

try:
    del df_parentcontacts # Delete dataframe
    print('df_parentcontacts dataframe cleared')
except NameError:
    print('No dataframe "df_parentcontacts" exists, moving on.')
 
try:
    del df_parentnamesdata # Delete dataframe
    print('df_parentnamesdata dataframe cleared')
except NameError:
    print('No dataframe "df_parentnamesdata" exists, moving on.')

try:
    del dict_countries # Delete dictionary
    print('dict_countries dictionary cleared')
except NameError:
    print('No dictionary "dict_countries" exists, moving on.')

print()
try:
    gc.collect() # Memory garbage collection
    print('gc.collect() ran successfully, garbage collected')
except:
    print('Issue running gc.collect()\n')


# In[5]:


# Create dictionary of Country Codes and Full Names
# Credit arturictus/carlopires/ISO-3166-Countries-with-Regional-Codes
url_ISO3166_country_csv = "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/refs/heads/master/slim-2/slim-2.csv"
#print(url_ISO3166_country_csv.text)

# Create dictionary
try:
    dict_countries = pd.read_csv(url_ISO3166_country_csv, keep_default_na=False, na_values=['_'], usecols=range(2), index_col=1, skiprows=0).T.to_dict('records')[0]
    print('Dictionary "dict_countries" created\n')
except:
    print('Issue creating Dictionary "dict_countries\n')


# In[6]:


# Use for testing
# List files in directory
#print('Our subdirectories are:')
#p = Path('./')
#for subdir in p.iterdir():
#    if subdir.is_dir():
#        print(subdir)


# In[7]:


# Specify where files from Sportsrecruits will live for processing and be moved after processing, and export files will be generated.
dir_home_path = os.getcwd()
processing_source_path = dir_home_path + "/{}".format('For Processing-Sportsrecruits Exports')
# Specify destination path for processed files
processed_dest_path = dir_home_path + "/{}".format('For Processing-Sportsrecruits Exports/Completed Processing')
# Specify destination path for exported files
export_dest_path = dir_home_path + "/{}".format('Output-FrontRush Import Files')

# List files in directory. listdir counts subdirectories as well, that's why the test is > 1
if len(os.listdir(processing_source_path)) > 1:
     print('The un-converted Sportsrecruits exports available are:')
     for file_path in os.scandir(processing_source_path):
        print(file_path.name)
else:
     print('No Sportsrecruits export files were found.')


# In[8]:


# Create list "dataframes", if exists clears list "dataframes"
dataframes = []

# Create variable for use in exported file name
Coach = ''  

# Print status update for user.
print('File conversion process beginning.')

# Gather list of CSVs from directory and load CSV data into dataframes df
try:
    for filename in os.listdir(processing_source_path):
        if filename.endswith(".csv"):
            source_path = os.path.join(processing_source_path, filename)
            df = pd.read_csv(source_path)
            df['Gender :: General'] = '' # Create blank column for Gender BEFORE adding data from filename
            # Passthrough Gender from file name into new column
            if fnmatch.fnmatch(filename.casefold(), '*women*'):
                df['Gender :: General'] = 'Female'
                Gender = 'Female' # Creates variable for us in exported file name if desired
            if fnmatch.fnmatch(filename.casefold(), '* men*'):
                df['Gender :: General'] = 'Male'
                Gender = 'Male' # Creates variable for us in exported file name if desired
            if fnmatch.fnmatch(filename.casefold(), '*female*'):
                df['Gender :: General'] = 'Female'
                Gender = 'Female' # Creates variable for us in exported file name if desired
            if fnmatch.fnmatch(filename.casefold(), '* male*'):
                df['Gender :: General'] = 'Male'
                Gender = 'Male' # Creates variable for us in exported file name if desired
            else:
                Gender = 'NoGender' # Creates variable for us in exported file name if desired
            Coach = df['Followed By Coach'].iloc[0] # Create variable for use in exported file name
            dataframes.append(df) 
    print('\nFiles loaded successfully.\n')
except:
    print('\nFiles not loaded successfully.\n')
    raise KeyboardInterrupt

if Coach == '':
   print('No file loaded, Coach variable left blank.\n')
else:
    print(f'Coach variable filled with "{Coach}" from "Followed By Coach" column.\n')

# Use for testing
#print(df.attrs)
#print(df.info())


# In[9]:


# Create empty dataframe to be filled as each row is edited in the dataframes 'df' that are in the list 'dataframes'
df_combined = pd.DataFrame()

# Combine data from the dataframes in the list
try:
    for df in dataframes:
        # Add all rows in dataframes in List "dataframes" to df_combined which does not exist in a list
        df_combined = pd.concat([df_combined, df], ignore_index=True)
    print('CSVs loaded into [df] now loaded into df_combined\n')
except:
    print('Issue loading CSVs loaded into [df] into df_combined\n')
    raise KeyboardInterrupt


# In[10]:


## Replace 'Country' 2-digit codes to full name
# Create replace function - searches dictionary and returns country name
def country_alpha2_to_name(x,my_dict):
    if x in my_dict.keys():
        return my_dict[x]
    else:
        return x #Assuming that you won't change the value if not in the dict

try:  
    df_combined['Country'] = df_combined['Country'].apply(lambda x: country_alpha2_to_name(x,dict_countries)) # Use replace function
    df_combined['Country'] = df_combined['Country'].str.replace('United States of America','United States') # Fit Sportsrecruits expected name for 'United States'
    df_combined['Country'] = np.where(df_combined['Country'].isna() & df_combined['State'].notnull(), 'United States', df_combined['Country']) # Insert 'United States' when State is filled in but Country is null, otherwise just leave the value from ['Country']
    df_combined['State'] = np.where(np.logical_or(df_combined['Country']=='United States',df_combined['Country']=='Canada',df_combined['Country'].notnull()), df_combined['State'], np.nan) # Insert null/nan in State when Country is not United States or Canada
    print('Handling for all Country and State fields completed\n')
except:
    print('Issue running some of all Country and State field operations\n')


# In[11]:


##### Manipulate export columns to match Front Rush expectations
try:
    # Remove characters from name fields
    df_combined['First Name'] = df_combined['First Name'].str.normalize('NFKD').str.encode('ascii',errors='ignore').str.decode('utf-8')
    df_combined['Last Name'] = df_combined['Last Name'].str.normalize('NFKD').str.encode('ascii',errors='ignore').str.decode('utf-8')
    df_combined['Guardian First Name'] = df_combined['Guardian First Name'].str.normalize('NFKD').str.encode('ascii',errors='ignore').str.decode('utf-8')
    df_combined['Guardian First Name'] = df_combined['Guardian Last Name'].str.normalize('NFKD').str.encode('ascii',errors='ignore').str.decode('utf-8')
    
    # Remove rows from past years. 
    df_combined = df_combined[df_combined['Class Year'] >= int(datetime.now().year)]
    #df_combined = np.where(int(datetime.now().month >= 9), df_combined[df_combined['Class Year'] >= int(datetime.now().year)], df_combined)
    
    # It doesn't handle current year but we can delete those at a later date.
    # It also means that the Front Rush import may include duplicates.
    # Front Rush imports match for duplicate entries, this is based on name and contact information, so if any of that changed a duplicate record will be created.
    # If that has not changed then the file upload to Front Rush will update those records.
    
    # Convert Phone number, removing leading +1 if it contains it, formatting as "xxx.xxx.xxxx"
    df_combined['Phone'] = df_combined['Phone'].astype("string") # Convert to String
    df_combined['Phone'] = df_combined['Phone'].str.replace(r'1(.{11,})', r'\1', regex=True) # shorten and remove leading +1 from phone numbers if exist,
    df_combined['Phone'] = df_combined['Phone'].str[:3] + "." + df_combined['Phone'].str[3:6] + "." + df_combined['Phone'].str[6:10] # Format as "xxx.xxx.xxxx"
    
    # Concatenate Guardian Name fields, rename to Guardian Name, delete Guardian Last Name
    df_combined['Guardian First Name'] = df_combined['Guardian First Name'] + ' ' + df_combined['Guardian Last Name']
    df_combined.rename({'Guardian First Name': 'Guardian Name'}, axis=1, inplace=True)
    
    # Copy Phone, rename both columns for Cell Phone Number and Contact Number
    df_combined['Contact Number :: General'] = df_combined['Phone']
    df_combined.rename({'Phone': 'Cell Phone Number :: General'}, axis=1, inplace=True)
    
    # Copy Class Year, add "Fall"
    df_combined['Entry Term :: General'] = df_combined['Class Year'].astype(str)
    df_combined['Entry Term :: General'] = ('Fall ' + df_combined['Entry Term :: General'])
    
    # Reformat Weight values and rename
    df_combined['Weight'] = df_combined['Weight'].str.replace(' lbs', '')
    df_combined.rename({'Weight': 'Weight :: Athletic'}, axis=1, inplace=True)
    
    # Reformat Height values and rename
    def fmt_ht(h):
        f = int(h.group(1))
        i = int(h.group(2))
        return f'{f} Feet {i:02} Inches'
    df_combined['Height'] = df_combined['Height'].str.replace(r'(\d+)\'(\d+)"', fmt_ht, regex=True)
    df_combined.rename({'Height': 'Height :: Athletic'}, axis=1, inplace=True)
    
    # Delete unused column names
    df_combined.drop(columns=['Guardian Last Name'], axis=1, inplace =True)
    df_combined.drop(columns=['University Committed to'], axis=1, inplace =True)
    df_combined.drop(columns=['GPA Unrestricted'], axis=1, inplace =True)
    df_combined.drop(columns=['GPA Scale'], axis=1, inplace =True)
    df_combined.drop(columns=['Program Notes'], axis=1, inplace =True)
    df_combined.drop(columns=['Declared Interest On'], axis=1, inplace =True)
    df_combined.drop(columns=['Followed By Coach'], axis=1, inplace =True)
    
    # Capitalize name fields
    df_combined['First Name'] = df_combined['First Name'].str.title()
    df_combined['Last Name'] = df_combined['Last Name'].str.title()
    
    # Insert new columns
    df_combined.insert(23,'Student Type ::  General', 'First Year')
    df_combined['Coach Comment :: General'] = df_combined['Source'] # Uses the exported 'Source' field as input for new field 'Comment'
    
    # Rename columns
    df_combined.rename({'First Name': 'Legal First Name :: General'}, axis=1, inplace=True)
    df_combined.rename({'Last Name': 'Last Name :: General'}, axis=1, inplace=True)
    df_combined.rename({'Class Year': 'Class Year :: General'}, axis=1, inplace=True)
    df_combined.rename({'Guardian Name': 'Parent/Guardian 1 Name :: Background'}, axis=1, inplace=True)
    df_combined.rename({'Guardian Email Address': 'Parent/Guardian 1 Email Address :: Background'}, axis=1, inplace=True)
    df_combined.rename({'Email Address': 'Email Address :: General'}, axis=1, inplace=True)
    df_combined.rename({'Recruit Profile': 'Recruiting Website :: General'}, axis=1, inplace=True)
    df_combined.rename({'GPA': 'GPA :: Academic'}, axis=1, inplace=True)
    df_combined.rename({'ACT': 'ACT :: Academic'}, axis=1, inplace=True)
    df_combined.rename({'SAT Math': 'SAT Math :: Academic'}, axis=1, inplace=True)
    df_combined.rename({'SAT Reading and Writing': 'SAT Reading and Writing :: Academic'}, axis=1, inplace=True)
    df_combined.rename({'SAT Math and Reading and Writing': 'SAT Total :: Academic'}, axis=1, inplace=True)
    df_combined.rename({'NCAA Number': 'NCAA ID :: General'}, axis=1, inplace=True)
    df_combined.rename({'High School': 'High School :: Academic'}, axis=1, inplace=True)
    df_combined.rename({'Club Name': 'Club Team Name (if applicable) :: Athletic'}, axis=1, inplace=True)
    df_combined.rename({'Intended Major': 'Intended Major :: Academic'}, axis=1, inplace=True)
    df_combined.rename({'City': 'City :: General'}, axis=1, inplace=True)
    df_combined.rename({'State': 'State :: General'}, axis=1, inplace=True)
    df_combined.rename({'Country': 'Country :: General'}, axis=1, inplace=True)
    df_combined.rename({'Source': 'Source :: General'}, axis=1, inplace=True)
    df_combined.rename({'Position': 'Position :: Athletic'}, axis=1, inplace=True)
    
    ##### Manipulate export columns for Contact file (Recruit Parents)
    # Create new dataframe to create Parent information for upload into Contacts
    df_parentcontacts = df_combined.copy(deep=True)
    # Start manipulating parent contact columns
    df_parentcontacts['Child First Name :: General'] = df_parentcontacts['Legal First Name :: General']
    df_parentcontacts['Child Last Name :: General'] = df_parentcontacts['Last Name :: General']
    # Handle Parent name by creating new dataframe df_parentnamesof split names then adding back to df_parentcontacts
    df_parentnamesdata = df_parentcontacts['Parent/Guardian 1 Name :: Background'].str.split(' ', n=1, expand=True) # Split First name by first space
    df_parentcontacts.drop(columns=['Last Name :: General'], axis=1, inplace=True) # Drop first to avoid conflicts later
    df_parentnamesdata['First Name :: General'] = df_parentnamesdata[0]
    df_parentnamesdata['Last Name :: General'] = df_parentnamesdata[1]
    df_parentcontacts['First Name :: General'] = df_parentnamesdata['First Name :: General'] 
    df_parentcontacts['Last Name :: General'] = df_parentnamesdata['Last Name :: General'] 
    df_parentcontacts.drop(columns=['Parent/Guardian 1 Name :: Background'], axis=1, inplace=True)
    df_parentcontacts['First Name :: General'] = df_parentcontacts['First Name :: General'].str.title() # Capitalize all strings delimited by space
    df_parentcontacts['Last Name :: General'] = df_parentcontacts['Last Name :: General'].str.title() # Capitalize all strings delimited by space
    # Move Parent Name columns to first positions
    df_parentcontacts.insert(0, 'Last Name :: General', df_parentcontacts.pop('Last Name :: General'))
    df_parentcontacts.insert(0, 'First Name :: General', df_parentcontacts.pop('First Name :: General'))
    # Continue handling parent contact data fields
    df_parentcontacts['Contact Type :: General'] = 'Recruit Parent'
    df_parentcontacts.drop(columns=['Email Address :: General'], axis=1, inplace=True)
    df_parentcontacts.rename({'Parent/Guardian 1 Email Address :: Background': 'Email Address :: General'}, axis=1, inplace=True)
    df_parentcontacts.rename({'Class Year :: General': 'Child Class Year :: General'}, axis=1, inplace=True)
    df_parentcontacts.drop(columns=['Legal First Name :: General'], axis=1, inplace=True)
    df_parentcontacts.drop(columns=['Recruiting Website :: General'], axis=1, inplace=True)
    df_parentcontacts.drop(columns=['GPA :: Academic'], axis=1, inplace=True)
    df_parentcontacts.drop(columns=['ACT :: Academic'], axis=1, inplace=True)
    df_parentcontacts.drop(columns=['SAT Math :: Academic'], axis=1, inplace=True)
    df_parentcontacts.drop(columns=['SAT Reading and Writing :: Academic'], axis=1, inplace=True)
    df_parentcontacts.drop(columns=['SAT Total :: Academic'], axis=1, inplace=True)
    df_parentcontacts.drop(columns=['NCAA ID :: General'], axis=1, inplace=True)
    df_parentcontacts.drop(columns=['High School :: Academic'], axis=1, inplace=True)
    df_parentcontacts.drop(columns=['Club Team Name (if applicable) :: Athletic'], axis=1, inplace=True)
    df_parentcontacts.drop(columns=['Intended Major :: Academic'], axis=1, inplace=True)
    df_parentcontacts.drop(columns=['Gender :: General'], axis=1, inplace=True)
    df_parentcontacts.drop(columns=['Height :: Athletic'], axis=1, inplace=True)
    df_parentcontacts.drop(columns=['Weight :: Athletic'], axis=1, inplace=True)
    df_parentcontacts.drop(columns=['Country :: General'], axis=1, inplace=True)
    df_parentcontacts.drop(columns=['Entry Term :: General'], axis=1, inplace=True)
    df_parentcontacts.drop(columns=['Position :: Athletic'], axis=1, inplace=True)

    # Print column manipulation success
    print('All data field changes successful\n')
except:
    print('Some of all data field changes unsuccessful\n')
    
# Use for testing
#df_combined.info()
#display(df_combined)


# In[12]:


# Create file names for export files
output_RecruitFile = str(export_dest_path + '/Front Rush Import-Recruit--' + Coach + '--' + datetime.now().strftime("%Y%m%d-%H.%M.%S") + '.csv')
output_ParentContactFile = str(export_dest_path + '/Front Rush Import-ParentContact--' + Coach + '--' + datetime.now().strftime("%Y%m%d-%H.%M.%S") + '.csv')

# Export parent file to Output folder
try:
    df_parentcontacts.to_csv(output_ParentContactFile, sep=',', na_rep='', index=False)
    print('Parent Contact File Exported, check output folder.')
    print('Parent rows with missing names are not removed, check your file to determine what you want to do with those rows.')
    # Rename and move processed Sportrecruits export files
except:
    print('Issue exporting parent contact file')   

# Export recruit file to CSV, removing <NA> and NaN values using na_rep='', and also removing the first column showing line/row number using index=False
try:
    df_combined.to_csv(output_RecruitFile, sep=',', na_rep='', index=False)
    print('\nRecruit File Exported, check output folder.')
    print('You will need to make edits to incorrectly spelled School names, or remove data from that column before sending to Front Rush, manually adding school information to Front Rush.\n')
except:
    print('\nIssue creating export CSV file.')
    raise KeyboardInterrupt

# Export recruit file to Output folder
##### Debug switch, Try this source file rename and move if Debug variable named at top of file is 'Off'
if Debug == 'Off': ##### Debug switch
    # find files in folder
    for filename in os.listdir(processing_source_path):
        if filename.endswith(".csv"):
            source_path = os.path.join(processing_source_path, filename)
            # Rename source file
            try:
                processed_filename = 'processed-'+filename  # Adds "processed" to name for files to be moved
                dest_path = os.path.join(processed_dest_path, processed_filename) # Creates full destination path for processed source files
                print(f'File renamed: "{processed_filename}"')
            except:
                print(f'Issue renaming file: "{filename}"')
            # Move procesed file  
            try:
                os.rename(source_path, dest_path) # Move processed files
                print(f'Processed Sportsrecruits file "{processed_filename}" moved to /For Processing-Sportsrecruits Exports/Completed Exports.\n')
            except: 
                print(f'\nFile move failed for "{processed_filename}"\n')
                raise KeyboardInterrupt                         
else:
    print('Debug mode on, source files not moved')

# Reclaim used memory, not trusting Python or JupyterLab to do so.
try:
    gc.collect() # Memory garbage collection
    print('gc.collect() ran successfully, garbage collected')
except:
    print('Issue running gc.collect()')


# In[ ]:




