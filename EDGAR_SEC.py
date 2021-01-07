# This script gets the EDGAR index file of today, or if not available the file uploaded the day before, and parse the txt files data into a csv file.
import datetime
today = datetime.date.today()
Date = today.strftime('%Y%m%d')
year = today.year
quarter = (today.month - 1) // 3 + 1
url = 'https://www.sec.gov/Archives/edgar/daily-index/{}/QTR{}/crawler.{}.idx'.format(year, quarter, Date)

from requests import get
response = get(url).text.splitlines()

# If the file of the day is not available yet, the data of the file uploaded the dey before is collected.
if response[0] == '<?xml version="1.0" encoding="UTF-8"?>':
    yesterday = today - datetime.timedelta(days=1)
    Date = yesterday.strftime('%Y%m%d')
    year = yesterday.year
    quarter = (yesterday.month - 1) // 3 + 1
    url = 'https://www.sec.gov/Archives/edgar/daily-index/{}/QTR{}/crawler.{}.idx'.format(year, quarter, Date)
    response = get(url).text.splitlines()



import pandas as pd
# create a data frame
df = pd.DataFrame(columns=['Company', 'Form Type', 'CIK', 'Date Filed', 'URL'])

FormType_loc = response[7].find('Form Type')
CIK_loc = response[7].find('CIK')
Date_loc = CIK_loc+7
URL_loc = CIK_loc+20

# Fill the dataframe with the relevant data of the index file
for i in range (10, len(response)):
    line = response[i]
    df = df.append({'Company': line[:FormType_loc].strip(), 'Form Type': line[FormType_loc:CIK_loc].strip() , 'CIK': line[CIK_loc:Date_loc].strip() , 'Date Filed': line[Date_loc:URL_loc].strip(), 'URL': line[URL_loc:].strip()}, ignore_index=True)


# Creat a dataframe to fill the data
df_main = pd.DataFrame([])

# Get the txt file
for t in range(1000, 1050):
    url = df.iloc[t,4][:-10]+'.txt'
    response = get(url).text
# Get the content of sec-header
    lines = response.splitlines()
    lines = list(filter(('').__ne__, lines))
    lines = lines[2:lines.index('</SEC-HEADER>')]

    Dict={}
    for i in range(1, len(lines)):

        Condition1 = lines[i].startswith('\t')
        Condition2 = lines[i].startswith('\t\t')
        if Condition1==False:
            j=i
            try:
                Dict[lines[i].split(':')[0]] = lines[i].split(':')[1].replace('\t', '', 3)
            except:
                pass
        else:
            lines[i] = lines[j].split(':')[0]+'_'+lines[i].replace('\t', '', 10)
            Dict[lines[i].split(':')[0].replace(' ', '_', 3)] = lines[i].split(':')[1]
    df_Detailed = pd.DataFrame.from_dict(Dict, orient='index').T
    df_main =  pd.concat([df_main, df_Detailed])

# convert the dataframe to a csv file
FileName = 'EDGAR_Filing_Details_'+Date+'.csv'
df_main.to_csv(FileName, index=False)
