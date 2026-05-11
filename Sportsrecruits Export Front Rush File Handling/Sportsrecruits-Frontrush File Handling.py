"""
Sportsrecruits-Front Rush File Handling.py
version 1.0.0
Created by Robert Cilino
May 2026

Future updates:
- Using a csv to create a dictionary for the dataframes to make column name changes instead of hard-coding each column change.
- Add new columns if Sportsrecruits includes more in the future.
- Add output file name handling for Gender based on incoming file name.

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

print('Be well, do well.')

# List imported modules
modulenames = set(sys.modules) & set(globals())
allmodules = [sys.modules[name] for name in modulenames]
print(f'Modules imported: {modulenames}')

# Clear dataframe lists
try:
    dataframes.clear()
    print(dataframes)
    print('List "dataframes" cleared')
except NameError: 
    print('No list "dataframes" exists')

# List files in directory
print('Our subdirectories are:')
p = Path('./')
for subdir in p.iterdir():
    if subdir.is_dir():
        print(subdir)

print('The un-converted exports available are:')
for file_path in os.scandir('Sportsrecruits Exports/'):
    if file_path.is_file():
        print(file_path.name)
        
# Specify where files from Sportsrecruits will live for processing
exports_folder_path = r'For Processing-Sportsrecruits Exports/'

# Create list "dataframes", if exists clears list "dataframes"
dataframes = []

# Gather list of CSVs from directory
for filename in os.listdir(exports_folder_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(exports_folder_path, filename)
        df = pd.read_csv(file_path)
        # Passthrough Gender from file name into new column
        if fnmatch.fnmatch(filename, '*Women*'):
             df['Gender :: General'] = 'Female'
            Gender = 'Female'
        if fnmatch.fnmatch(filename, '* Men*'):
             df['Gender :: General'] = 'Male'
            Gender = 'Male'
        if not fnmatch.fnmatch(filename,'* Men*'):
            Gender = 'NoGender'
        Coach = df['Followed By Coach'].iloc[0]
        dataframes.append(df)

# Create empty dataframe to be filled as each row is edited in the dataframes 'df' that are in the list 'dataframes'
df_combined = pd.DataFrame()
print(output_File)

# Process Sportsrecruits export file data to match Front Rush expectations
for df in dataframes:
    # Convert Phone to string to preserve nulls and reformat later, removing leading +1 if it contains it
    df['Phone'] = df['Phone'].astype("string")
    
    # Concatenate Guardian Name fields, rename to Guardian Name, delete Guardian Last Name
    df['Guardian First Name'] = df['Guardian First Name'] + ' ' + df['Guardian Last Name']
    df.rename({'Guardian First Name': 'Guardian Name'}, axis=1, inplace=True)

    # Format Phone columns, shorten and remove leading +1 from phone numbers if exist
    df['Phone'] = df['Phone'].str.replace(r'1(.{11,})', r'\1', regex=True)

    # Copy Phone, rename both columns for Cell Phone Number and Contact Number
    df['Contact Number :: General'] = df['Phone']
    df.rename({'Phone': 'Cell Phone Number :: General'}, axis=1, inplace=True)
    
    # Copy Class Year, add "Fall"
    df['Entry Term :: General'] = df['Class Year'].astype(str)
    df['Entry Term :: General'] = ('Fall ' + df['Entry Term :: General'])
    
    # Reformat Weight values and rename
    df['Weight'] = df['Weight'].str.replace(' lbs', '')
    df.rename({'Weight': 'Weight :: Athletic'}, axis=1, inplace=True)
    
    # Reformat Height values and rename
    def fmt(m):
        f = int(m.group(1))
        i = int(m.group(2))
        return f'{f} Feet {i:02} Inches'

    df['Height'] = df['Height'].str.replace(r'(\d+)\'(\d+)"', fmt, regex=True)
    df.rename({'Height': 'Height :: Athletic'}, axis=1, inplace=True)
    
    # Delete unused column names
    df.drop(columns=['Guardian Last Name'], axis=1, inplace =True)
    df.drop(columns=['University Committed to'], axis=1, inplace =True)
    df.drop(columns=['Position'], axis=1, inplace =True)
    df.drop(columns=['GPA Unrestricted'], axis=1, inplace =True)
    df.drop(columns=['GPA Scale'], axis=1, inplace =True)
    df.drop(columns=['Program Notes'], axis=1, inplace =True)
    df.drop(columns=['Declared Interest On'], axis=1, inplace =True)
    df.drop(columns=['Followed By Coach'], axis=1, inplace =True)
    
    # Insert new columns
    df.insert(23,'Student Type ::  General', 'First Year')
    
    # Rename columns
    df.rename({'First Name': 'Legal First Name :: General'}, axis=1, inplace=True)
    df.rename({'Last Name': 'Last Name :: General'}, axis=1, inplace=True)
    df.rename({'Class Year': 'Class Year :: General'}, axis=1, inplace=True)
    df.rename({'Guardian Name': 'Parent/Guardian 1 Name :: Background'}, axis=1, inplace=True)
    df.rename({'Guardian Email Address': 'Parent/Guardian 1 Email Address :: Background'}, axis=1, inplace=True)
    df.rename({'Email Address': 'Email Address :: General'}, axis=1, inplace=True)
    df.rename({'Recruit Profile': 'Recruiting Website :: General'}, axis=1, inplace=True)
    df.rename({'GPA': 'GPA :: Academic'}, axis=1, inplace=True)
    df.rename({'ACT': 'ACT :: Academic'}, axis=1, inplace=True)
    df.rename({'SAT Math': 'SAT Math :: Academic'}, axis=1, inplace=True)
    df.rename({'SAT Reading and Writing': 'SAT Reading and Writing :: Academic'}, axis=1, inplace=True)
    df.rename({'SAT Math and Reading and Writing': 'SAT Total :: Academic'}, axis=1, inplace=True)
    df.rename({'NCAA Number': 'NCAA ID :: General'}, axis=1, inplace=True)
    df.rename({'High School': 'High School :: Academic'}, axis=1, inplace=True)
    df.rename({'Club Name': 'Club Team Name (if applicable) :: Athletic'}, axis=1, inplace=True)
    df.rename({'Intended Major': 'Intended Major :: Academic'}, axis=1, inplace=True)
    df.rename({'City': 'City :: General'}, axis=1, inplace=True)
    df.rename({'State': 'State :: General'}, axis=1, inplace=True)
    df.rename({'Country': 'Country :: General'}, axis=1, inplace=True)
    df.rename({'Source': '3rd Party Source :: General'}, axis=1, inplace=True)

    # Add all rows in dataframes in List "dataframes" to df_combined which does not exist in a list
    df_combined = pd.concat([df_combined, df], ignore_index=True)
    
# Export to CSV, removing <NA> and NaN values using na_rep='', and also removing the first column showing line/row number using index=False
output_File = str('Output-FrontRush Import Files/Front Rush Import--' + Coach + '--' + datetime.now().strftime("%Y%m%d-%H.%M.%S") + '.csv')

try:
    df_combined.to_csv(output_File, sep=',', na_rep='', index=False)
    print('File Exported, check output folder')
    print('You will need to make edits to incorrectly spelled School names, or remove data from that column before sending to Front Rush, manually adding school information to Front Rush')
except:
    print('Issue exporting file')
    
# End of script