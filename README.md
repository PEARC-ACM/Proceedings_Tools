#
# Overview
#
Converts EasyChair accepted paper information into ACM Proceedings Enhanced CSV format

Requires two EasyChair information exports

#
# Generating EasyChair metadata
#

A) ACM Data

# Click on “Premium”->”ACM data download”
# Assign a “Kind” to all the papers

Use "Full Papers" for full papers
Use "Full Papers" for short papers
Use "Tutorials" for Workshops
Use "WIP .." for Colocated events
ONLY "Full Papers" and "Extended Abstracts" will be included in the proceedings CSV file

# Click “Download”
# Upload downloaded file to Google Folder
# Convert ACM XML to JSON using https://codebeautify.org/xmltojson or a similar tool/service


B) Reviewing Data

# NOTE: This procedure only works if you download more than one track, because EasyChair excludes the Track column
#       when only onen track is downloaded

# Click on “Status”
# Click top right “Reviewing data in Excel”
# Select relevant track(s) and the Decision “ACCEPT”
# Click “Download”
# Upload downloaded file to Google Folder
# Open uploaded file with Google docs
# Download at CSV
# Upload downloaded file for the "Submissions" tab to Google Folder



#
# Convert EasyChair metadata
# Inputs:
#   "-ea": EasyChair ACM data
#   "-er": EasyChair Reviewing data
#

./bin/easychair_acm_data_convert.py \
   -ea ~/Downloads/PEARC\'22_ACM_data_2022-03-28.json \
   -er ~/Downloads/PEARC\'22_review_summary_2022-03-28_1648478445.xlsx\ -\ Submissions.csv \
   >~/Downloads/PEARC\'22_ACM_data_2022-03-28_proceedings.csv

./bin/easychair_acm_data_convert.py \
   -ea ~/Downloads/PEARC\'22_ACM_data_2022-05-01.json \
   -er ~/Downloads/PEARC\'22_review_summary_2022-05-01_1651437089.xlsx\ -\ Submissions.csv \
   >~/Downloads/PEARC\'22_ACM_data_2022-05-01_proceedings.csv
