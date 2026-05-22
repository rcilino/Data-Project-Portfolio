# Sportsrecruits Export > Front Rush File Handling

Python script needs to run with two folders present:
- For Processing-Sportsrecruits Exports
- Output-FrontRush Import Files

All files and folder structure are present in the included zip file.

Import files need to be CSV, direct exports from Sportsrecruits should work properly without editing.

If the Gender column should be populated, include "Men", "Women", "Male", or "Female" in the Sportsrecruits export CSV file name.

## Changelog:
version 1.2.4
May 22, 2026
- Added better handling for culling past students to include current month and year compared to Class Year.
- Added a debug switch via variable and if statements, mainly used to stop renaming and moving source files.
- Improved Gender field handling based on source file name using case-insensitive matching.
- Improved file rename and move handling.

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