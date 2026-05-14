"""
Sportsrecruits-Front Rush File Handling.py
version 1.2.0
Created by Robert Cilino
May 2026

version 1.2.0
- A 2nd Front Rush upload file to add Parent/Guardians into the Contacts section of Front Rush is now created upon completion.
- Reorganized export field column delete/rename section to combine dataframes in list before manipulating.
- Capitalized Recruit First and Last Name, no longer assuming intent.
- Capitalized Parent First and Last Name, no longer assuming intent.

version 1.1.1
- Rows where 'Class Year' is lower than current year are now removeds.
- Exception handling added to check first for files in Sportsrecruits exports folder /For Processing-Sportsrecruits Export/

version 1.1.0
- Added try/except in most locations.
- Processed files are now renamed to note their completion.
- Processed files are now moved to /For Processing-Sportsrecruits Export/Completed Processing

Future updates:
- Using a csv to create a dictionary for the dataframes to make column name changes instead of hard-coding each column change.
- Add new columns if Sportsrecruits includes more in the future.

Be well, do well.
"""

import sys
import os as os
from pathlib import Path
import fnmatch
import csv
import pandas as pd
import logging
from datetime import datetime
import gc

# List imported modules
modulenames = set(sys.modules) & set(globals())
allmodules = [sys.modules[name] for name in modulenames]
print(f'Modules imported: {modulenames}')

# Clear dataframe lists
try:
    dataframes.clear()
    print(dataframes)
    gc.collect() # Memory garbage collection
    print('List "dataframes" cleared')
#    logging.info('List "dataframes" cleared')
except NameError: 
    print('No list "dataframes" exists, moving on.')
#    logging.info('No list "dataframes" exists')

try:
    del df_combined # Delete dataframe
    cg.collect() # Memory garbage collection
    print('df_combined cleared')
except NameError:
    print('No dataframe "df_combined" exists, moving on.')

try:
    del df_parentcontacts # Delete dataframe
    cg.collect() # Memory garbage collection
    print('df_parentcontacts cleared')
except NameError:
    print('No dataframe "df_parentcontacts" exists, moving on.')

try:
    del df_parentnamesdata # Delete dataframe
    cg.collect() # Memory garbage collection
    print('df_parentnamesdata cleared')
except NameError:
    print('No dataframe "df_parentnamesdata" exists, moving on.')
    
# Specify where files from Sportsrecruits will live for processing
processing_source_path = r'For Processing-Sportsrecruits Exports/'
processed_dest_path = r'For Processing-Sportsrecruits Exports/Completed Processing/'

# List files in directory. listdir counts subdirectories as well, that's why the test is > 1
if len(os.listdir(processing_source_path)) > 1:
     print('The un-converted Sportsrecruits exports available are:')
     for file_path in os.scandir(processing_source_path):
        print(file_path.name)
else:
     print('No Sportsrecruits export files were found.')
     
# Create list "dataframes", if exists clears list "dataframes"
dataframes = []

# Create empty dataframe to be filled as each row is edited in the dataframes 'df' that are in the list 'dataframes'
df_combined = pd.DataFrame()

# Gather list of CSVs from directory and load CSV data into dataframes df
try:
    for filename in os.listdir(processing_source_path):
        if filename.endswith(".csv"):
            source_path = os.path.join(processing_source_path, filename)
            df = pd.read_csv(source_path)
            # Passthrough Gender from file name into new column
            if fnmatch.fnmatch(filename, '*Women*'):
                df['Gender :: General'] = 'Female'
                Gender = 'Female' # Creates variable for us in exported file name if desired
            if fnmatch.fnmatch(filename, '* Men*'):
                df['Gender :: General'] = 'Male'
                Gender = 'Male' # Creates variable for us in exported file name if desired
            if not fnmatch.fnmatch(filename,'* Men*'):
                Gender = 'NoGender' # Creates variable for us in exported file name if desired
            Coach = df['Followed By Coach'].iloc[0] # Create variable for use in exported file name
            dataframes.append(df) 
    print('Files loaded successfully.')
except:
    print('Files not loaded successfully.')
    raise KeyboardInterrupt

# Use for testing
#print(df.attrs)
#print(df.info())

# Combine data from the dataframes in the list
for df in dataframes:
    # Add all rows in dataframes in List "dataframes" to df_combined which does not exist in a list
    df_combined = pd.concat([df_combined, df], ignore_index=True)

##### Manipulate export columns to match Front Rush expectations
# Remove rows from past years. 
df_combined = df_combined[df_combined['Class Year'] >= int(datetime.now().year)]
# It doesn't handle current year but we can delete those at a later date.
# It also means that the Front Rush import may include duplicates.
# Front Rush imports match for duplicate entries, this is based on name and contact information, so if any of that changed a duplicate record will be created.
# If that has not changed then the file upload to Front Rush will update those records.

# Convert Phone to string to preserve nulls and reformat later, removing leading +1 if it contains it
df_combined['Phone'] = df_combined['Phone'].astype("string")

# Concatenate Guardian Name fields, rename to Guardian Name, delete Guardian Last Name
df_combined['Guardian First Name'] = df_combined['Guardian First Name'] + ' ' + df_combined['Guardian Last Name']
df_combined.rename({'Guardian First Name': 'Guardian Name'}, axis=1, inplace=True)

# Format Phone columns, shorten and remove leading +1 from phone numbers if exist
df_combined['Phone'] = df_combined['Phone'].str.replace(r'1(.{11,})', r'\1', regex=True)
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
def fmt(m):
    f = int(m.group(1))
    i = int(m.group(2))
    return f'{f} Feet {i:02} Inches'

df_combined['Height'] = df_combined['Height'].str.replace(r'(\d+)\'(\d+)"', fmt, regex=True)
df_combined.rename({'Height': 'Height :: Athletic'}, axis=1, inplace=True)

# Delete unused column names
df_combined.drop(columns=['Guardian Last Name'], axis=1, inplace =True)
df_combined.drop(columns=['University Committed to'], axis=1, inplace =True)
df_combined.drop(columns=['Position'], axis=1, inplace =True)
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
df_combined.rename({'Source': '3rd Party Source :: General'}, axis=1, inplace=True)


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

# Use for testing
#df_combined.info()
#display(df_combined)

# Create file names for export files
output_RecruitFile = str('Output-FrontRush Import Files/Front Rush Import-Recruit--' + Coach + '--' + datetime.now().strftime("%Y%m%d-%H.%M.%S") + '.csv')
output_ParentContactFile = str('Output-FrontRush Import Files/Front Rush Import-ParentContact--' + Coach + '--' + datetime.now().strftime("%Y%m%d-%H.%M.%S") + '.csv')

# Export files to CSV, removing <NA> and NaN values using na_rep='', and also removing the first column showing line/row number using index=False
try:
    # Export parent file to Output folder
    try:
        df_parentcontacts.to_csv(output_ParentContactFile, sep=',', na_rep='', index=False)
        print('Parent Contact File Exported, check output folder.')
        print('Parent rows with missing names are not removed, check your file to determine what you want to do with those rows.')
        # Rename and move processed Sportrecruits export files
    except:
        print('Issue exporting parent contact file')   
         
    # Export recruit file to Output folder
    try:
        df_combined.to_csv(output_RecruitFile, sep=',', na_rep='', index=False)
        print('\nRecruit File Exported, check output folder.')
        print('You will need to make edits to incorrectly spelled School names, or remove data from that column before sending to Front Rush, manually adding school information to Front Rush.')
        try:
        # find files in folder
            for filename in os.listdir(processing_source_path):
                source_path = os.path.join(processing_source_path, filename)
                dest_path = os.path.join(processed_dest_path, 'processed-'+filename) # Adds "processed" to name for files to be moved
                if filename.endswith(".csv"):
                    try:
                        # Move file
                        os.rename(source_path, dest_path)
                        os.newline()
                        print('Processed Sportsrecruits files moved to /For Processing-Sportsrecruits Exports/Completed Exports.')
                    except: 
                        print('\nProcessed file move failed.')
                        raise KeyboardInterrupt
        except:
            print('\nIssue exporting recruit file')
                        
    except: 
        print('\nIssue reading processed files for move, NOT moving the files.')
        raise KeyboardInterrupt
except:
    print('\nIssue creating export CSV file.')
    raise KeyboardInterrupt

