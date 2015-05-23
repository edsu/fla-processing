#!/usr/bin/env python

"""
Reads original Excel spreadsheets from various authors and builds 
one new master Excel file.
"""

import sys
import openpyxl
import unicodecsv

columns = [
    "collection",
    "filename",
    "page numbers",
    "pages in document",
    "main title",
    "sub title",
    "alt title",
    "descriptive title",
    "author",
    "publication",
    "volume",
    "issue/number",
    "date (month.day/season)",
    "year",
    "publisher",
    "publisher location",
    "subjects"
]


def write_master():
    csv = unicodecsv.writer(sys.stdout)
    csv.writerow(columns)
    write_spreadsheet(csv, "spreadsheets/British Spreadsheet--Jennie.xlsx", british_jennie)
    write_spreadsheet(csv, "spreadsheets/Nick British scans.xlsx", british_nick)
    write_spreadsheet(csv, "spreadsheets/Irish Drama Database.xlsx", irish_drama)
    write_spreadsheet(csv, "spreadsheets/Master Conrad Spreadsheet-Final 5-16(PM).xlsx", conrad)
    write_spreadsheet(csv, "spreadsheets/Master RAI Database.FINAL.xlsx", rai)


def write_spreadsheet(csv, filename, row_reader):
    old_sheet = openpyxl.load_workbook(filename).worksheets[0]
    seen_header = False
    last_subject = None
    for row in old_sheet.rows:

        if not seen_header:
            seen_header = True
            continue

        new_row = row_reader(row)

        # if there isn't a filename we don't put it in the spreadsheet
        if new_row[1] == None:
            continue

        if new_row[16] in (None, "--", "-"):
            new_row[16] = last_subject

        csv.writerow(new_row)

        last_subject = new_row[16]


"""
British Spreadsheet--Jennie.xlsx (many columns after primary authors blank)
1 unique id
2 file name
3 page numbers
4 pages in document
5 main title
6 sub title
7 alt title
8 descriptive title
9 author
10 placement in source
11 publication
12 volume
13 issue/number
14 part
15 date (month.day/season)
16 year
17 publisher
18 publisher location
19 document type (empty)
20 primary author
21 source
22 date acquired
23 location acquired
24 medium acquired
25 call number
26 supplemental to
27 supplementary documents
28 british or american
"""

def british_jennie(row):
    return [
        "britishj",     # collection
      	row[1].value,  # filename
        row[2].value,  # page numbers
        row[3].value,  # pages in document
        row[4].value,  # main title
        row[5].value,  # sub title
        row[6].value,  # alt title
        row[7].value,  # descriptive title
        row[8].value,  # author
        row[10].value, # publication
    	row[11].value, # volume
        row[12].value, # issue/number
        row[14].value, # date (month.day/season)
    	row[15].value, # year
    	row[16].value, # publisher
    	row[17].value, # publisher location
        row[19].value  # subject(s)
    ]

"""
Nick British scans.xlsx
1 file name
2 page numbers
3 pages in document
4 main title
5 sub title
6 alt title
7 descriptive title
8 author
9 placement in source
10 publication
11 volume
12 issue/number
13 date (month.day)
14 year
15 document type (empty)
16 source database
17 date acquired
18 medium acquired
19 picture
20 picture description
21 supplemental to
22 supplementary documents
23 plain text
24 rescan

1 Unique Identifier,
2 File Name,
3 Page #(s),
4 Pages in Document
5 Main Title
6 Sub Title
7 Alt Title
8 Descriptive Title
9 Author
10 Placement in Source
11 Publication
12 Volume
13 Issue/Number
14 Date (Month.Day/Season)
15 Year
16 Publisher
17 Publisher Location
18 Document Type/Genre
19 Source (Database, archive, etc.)
20 Date Acquired
21 Location Acquired
22 Medium Acquired
23 Call Number
24 Picture (Y/N)
25 Picture Description
26 Supplemental to:
27 Supplementary Documents
28 Plain text OCR file name
29 Plain PDF OCR file name
30 PDF/A underlaid text OCR file name
31 British or American (A or B)
32 Spellings of authors' names
33 Authors principally at issue
34 Secondary authors at issue
35 Sentiment analysis, part 1
36 Sentiment analysis, part 2
37 Works mentioned? (Y/N)
38 National idenfication (Y/N)
39 Style as issue (Y/N)
40 Author's biography (Y/N)
41 Apparent gender of article writer (M/F/U)
42 Foreign place names (Y/N)
43 Gender as issue (Y/N)
44 Race as issue (Y/N)
45 Socioeconomic class as issue (Y/N)
46 Military as issue (Y/N)
47 America invoked: similarity (Y/N)
48 Notes
49 Rescan?
"""

def british_nick(row):
    subjects = row[32].value
    if subjects and row[33].value:
        subjects += " ; " + row[33].value
    return [
        "british",     # collection
        row[1].value,  # filename
        row[2].value,  # page numbers
        row[3].value,  # pages in document
        row[4].value,  # main title
        row[5].value,  # sub title
        row[6].value,  # alt title
        row[7].value,  # descriptive title
        row[8].value,  # author
        row[10].value, # publication
        row[11].value, # volume
        row[12].value, # issue/number
        row[13].value, # date (month.day/season)
        row[14].value, # year
        row[15].value, # publisher
        row[16].value, # publisher location
        subjects       # subject(s)
    ]

"""
Irish Drama Database.xlsx
1 unique id
2 file name
3 page numbers
4 pages in document
5 main title
6 sub title
7 alt title
8 descriptive title
9 author
10 placement in source
11 publication
12 volume
13 issue/number
14 date (month.day)
15 year
16 publisher
17 publisher location
18 document type
19 primary author(s) semicolon delimited
20 source database
21 date acquired
22 location acquired
23 medium acquired
24 call number
"""

def irish_drama(row):
    return [
        "irish-drama", # collection
        row[1].value,  # filename
        row[2].value,  # page numbers
        row[3].value,  # pages in document
        row[4].value,  # main title
        row[5].value,  # sub title
        row[6].value,  # alt title
        row[7].value,  # descriptive title
        row[8].value,  # author
        row[10].value, # publication
        row[11].value, # volume
        row[12].value, # issue/number
        row[13].value, # date (month.day/season)
        row[14].value, # year
        row[15].value, # publisher
        row[16].value, # publisher location
        row[18].value  # subject(s)
    ]

"""
Master Conrad Spreadsheet-Final 5-1 .xlsx
1 unique id
2 file name
3 page numbers
4 pages in document
5 main title
6 sub title
7 alt title
8 descriptive title
9 author
10 placement in source
11 publication
12 volume
13 issue
14 date (month.day/season)
15 year
16 publisher
17 publisher location
18 type (review, essay, etc)
19 picture
20 picture description
21 british (a) or american (b)
22 author at issue
23 secondary authors at issue
24 notes
25 primary descriptor
"""

def conrad(row):
    subjects = []
    if row[21].value:
        subjects.append(row[21].value)
    if row[22].value:
        secondary = row[22].value
        # can have multiple names, separeated by commas
        if ',' in secondary:
            subjects += [s.strip() for s in secondary.split(',')]
        else:
            subjects.append(secondary)
    subjects = ' ; '.join(subjects)
    return [
        "conrad",      # collection
        row[1].value,  # filename
        row[2].value,  # page numbers
        row[3].value,  # pages in document
        row[4].value,  # main title
        row[5].value,  # sub title
        row[6].value,  # alt title
        row[7].value,  # descriptive title
        row[8].value,  # author
        row[10].value, # publication
        row[11].value, # volume
        row[12].value, # issue/number
        row[13].value, # date (month.day/season)
        row[14].value, # year
        row[15].value, # publisher
        row[16].value, # publisher location
        subjects       # subjects
    ]

"""
Master RAI Database.xlsx
1 unique id
2 file name
3 page numbers
4 pages in document
5 main title
6 sub title
7 alt title
8 descriptive title
9 author
10 placement in source
11 publication
12 volume
13 issue number
14 part
15 date (month.day)
16 year
17 type
18 primary author(s) semicolon delimited
19 source database/archive
20 date acquired
21 location acquired
22 medium acquired
23 call number
24 british or american
"""

def rai(row):
    return [
        "russian",     # collection
        row[1].value,  # filename
        row[2].value,  # page numbers
        row[3].value,  # pages in document
        row[4].value,  # main title
        row[5].value,  # sub title
        row[6].value,  # alt title
        row[7].value,  # descriptive title
        row[8].value,  # author
        row[10].value, # publication
        row[11].value, # volume
        row[12].value, # issue/number
        row[14].value, # date (month.day/season)
        row[15].value, # year
        row[16].value, # publisher
        row[17].value, # publisher location
        row[19].value  # subject(s)
    ]


write_master()
