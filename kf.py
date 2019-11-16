"""
## Clean up task:
* each row has multiple readings (timestamp). Want to pick the highest value for each day.
* Some rows have lots of records (long stays)
* interested in only first 7 days
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


# Read input
xlsx = pd.ExcelFile('./kGFR_file2.xlsx')
df = pd.read_excel(xlsx, 'Wide_GFR_PT_ID', index_col = None, na_values=['.']) #nrows = 10

df.shape
df.head()

# The basic structure that gets repeated
df.iloc[0,0:50]
"""
###### BASIC ######
pt_nmb                                            **            
date_of_birth_v2                                  **
date_of_icu_admission_v2         2015-08-31 00:00:00
age years                                    16.0795
date_of_icu_discharge_v2         2015-09-02 00:00:00
icu_length_of_stay_v2                              3
date_of_hospital_discharge_v2    2015-09-04 00:00:00
hospital_length_of_stay_v2                         5
gender_v1                                          1
height_v2                                      
weight_v2                                    53.4995
sepsis_v2                                          0
oncololgy_v2                                       0
tbi_diagnosis                                      0
respiratory_failure_diagno                         0
history_of_transplant_v2                           0
PRISM 3 Score                                     11
true baseline_creatinine_v2                      NaN
Cr calc or true                                    0
estimate cr                                 0.541161
estimated CrCl                                   126
baseline eGFR                                    126
need_for_pressors_v2                               0
vasopressor_days_v2                              NaN
mortality_v2                                       0
mech_vent_v2                                       0
length_of_mechanical_venti_v2                    NaN

#### Lab values and dates #############
LAB_VALUE_1                                     2.41
Cr/base ratio                                4.45339
AKI Day 1                                          3
LAB_VALUE_2                                     2.22
SPECIMN_TAKEN_TIME_1              31AUG2015:03:50:00
SPECIMN_TAKEN_TIME_2              31AUG2015:05:35:00
delta_cr_2                                      0.19
delta_time_2_hrs                               -1.75
delta time 1                                    1.75
delta GFR in 24 2                           -2.60571
LAB_VALUE_3                                     2.25
SPECIMN_TAKEN_TIME_3              31AUG2015:06:30:00
delta_gfr_3                                    -0.03
delta_time_3_hrs                           -0.916667
Unnamed: 41                                 0.916667
total time 2                                 2.66667
time 2                                         26.25
Day 2 cr                                        1.07
delta GFR in 24 3                           0.785455
delta_time_3_days                         -0.0381944
LAB_VALUE_4                                     2.42
SPECIMN_TAKEN_TIME_4              31AUG2015:07:30:00
delta_gfr_4                                    -0.17
######### Repeat pattern ############# 
time 3                                 NaN
day 3 cr                               NaN
delta_time_4_hrs                        -1
Unnamed: 53                              1
total time 3                       3.66667
delta GFR in 24 4                     4.08
delta_time_4_days               -0.0416667
LAB_VALUE_5                           1.85
SPECIMN_TAKEN_TIME_5    31AUG2015:08:30:00
delta_gfr_5                           0.57
delta_time_5_hrs                        -1
Unnamed: 61                              1
total time 4                       4.66667
delta GFR in 24 5                   -13.68
delta_time_5_days               -0.0416667
LAB_VALUE_6                           1.67
SPECIMN_TAKEN_TIME_6    31AUG2015:10:30:00
delta_gfr_6                           0.18
delta_time_6_hrs                        -2
Unnamed: 69                              2
total time 5                       6.66667
delta GFR in 24 6                    -2.16
delta_time_6_days               -0.0833333
LAB_VALUE_7                           1.85
SPECIMN_TAKEN_TIME_7    31AUG2015:12:10:00
delta_gfr_7                          -0.18
delta_time_7_hrs                  -1.66667
Unnamed: 77                        8.33333
delta GFR in 24 7                    2.592
delta_time_7_days               -0.0694444
LAB_VALUE_8                            1.9
SPECIMN_TAKEN_TIME_8    31AUG2015:14:00:00
delta_gfr_8                          -0.05
delta_time_8_hrs                  -1.83333
Unnamed: 84                        10.1667
delta GFR in 24 8                 0.654545
delta_time_8_days               -0.0763889
LAB_VALUE_9                              2
SPECIMN_TAKEN_TIME_9    31AUG2015:16:00:00
delta_gfr_9                           -0.1
...
...
...

"""


# length of hospital stay in days
df['hospital_length_of_stay_v2'].describe()

"""
count    1000.000000
mean       16.153000
std        21.598428
min         3.000000
25%         6.000000
50%         9.000000
75%        17.000000
max       346.000000
"""

# Just testing above by self: Not difference of 1 day in each case! 
(df.date_of_hospital_discharge_v2 - df.date_of_icu_admission_v2).describe()
"""
count                       1000
mean     15 days 03:40:19.200000
std      21 days 14:21:44.161222
min              2 days 00:00:00
25%              5 days 00:00:00
50%              8 days 00:00:00
75%             16 days 00:00:00
max            345 days 00:00:00

"""

"""
Why the difference? (exactly by 1 day)? 
Because they are counting calendar days, not days completed. Admitted on 3rd, discharged on 5th is a 3-day stay, not a 2-day (5-3) one. 
"""

# Example, pt row 13
df.loc[13,'date_of_hospital_discharge_v2'] - df.loc[13,'date_of_icu_admission_v2'] #i.e. Timestamp('2015-11-11 00:00:00') - Timestamp('2015-11-06 00:00:00')
# Timedelta('5 days 00:00:00')
df.loc[13,'hospital_length_of_stay_v2']
# 6 # integer



## Creating new vals

# Parsing time: 03SEP2015:04:55:00
# %d 0-padded date
# %b month
# %Y year xxxx
# %H %M %S

#using python datetime (from datetime, i.e. datetime.datetime) or see import above
datetime.strptime('03SEP2015:04:55:00', '%d%b%Y:%H:%M:%S')

#time deltas
timeDiff = datetime.strptime('04SEP2015:12:55:00', '%d%b%Y:%H:%M:%S') - datetime.strptime('03SEP2015:05:15:30', '%d%b%Y:%H:%M:%S')
# datetime.timedelta(1, 27570)

timeDiff > timedelta(hours=24)
# True
timeDiff > timedelta(hours=36)
# False


# If numpy version is needed
#np.datetime64(datetime.strptime('03SEP2015:04:55:00', '%d%b%Y:%H:%M:%S'))
#np.timedelta64(timeDiff, 'h')
#numpy.timedelta64(31,'h') # a diff of 31 hours

## Max values
## Find the number of days, limit to 7
## For each day: 0-6, find the max value and the time stamp


## Initialize columns for max lab readings and timestamps for up to 7 days
# df['Max_Lab_Val_1'] = df.apply(lambda _: '', axis=1)
# df['Max_Lab_Val_TS_1'] = df.apply(lambda _: '', axis=1)
# df['Max_Lab_Val_2'] = df.apply(lambda _: '', axis=1)
# df['Max_Lab_Val_TS_2'] = df.apply(lambda _: '', axis=1)
# df['Max_Lab_Val_3'] = df.apply(lambda _: '', axis=1)
# df['Max_Lab_Val_TS_3'] = df.apply(lambda _: '', axis=1)
# df['Max_Lab_Val_4'] = df.apply(lambda _: '', axis=1)
# df['Max_Lab_Val_TS_4'] = df.apply(lambda _: '', axis=1)
# df['Max_Lab_Val_5'] = df.apply(lambda _: '', axis=1)
# df['Max_Lab_Val_TS_5'] = df.apply(lambda _: '', axis=1)
# df['Max_Lab_Val_6'] = df.apply(lambda _: '', axis=1)
# df['Max_Lab_Val_TS_6'] = df.apply(lambda _: '', axis=1)
# df['Max_Lab_Val_7'] = df.apply(lambda _: '', axis=1)
# df['Max_Lab_Val_TS_7'] = df.apply(lambda _: '', axis=1)

# One shot addition of new columns for readings (7 days) instead of above
numdays = list('1234567')
newCols = [] #initialize
emptyVals = []
for d in numdays:
    newCols.append('Max_Lab_Val_'+d)
    emptyVals.append('')
    newCols.append('Max_Lab_Val_TS_'+d)
    emptyVals.append('')    
#create the new columns, initialized to ''
df[newCols] = df.apply(lambda _ : pd.Series(emptyVals,index=newCols) ,axis=1)
# Add in the initial specimen time
df['Specimen_1_TS'] = df.apply(lambda _: '', axis=1) #this one simply to store the string as a timestamp (for use in excel)


 #test for missing specimens
df[pd.isna(df.SPECIMN_TAKEN_TIME_1)==True].shape[0] # should be 0 i.e. not missing. Should exist for all rows   

for row in range(1047): #(1047 rows in file)
    #print('\n\n\n\nFor row ' + str(row))
    #day first specimen taken, which may not be the same as admission
    df.loc[row, 'Specimen_1_TS'] = datetime.strptime(df.loc[row, 'SPECIMN_TAKEN_TIME_1'],'%d%b%Y:%H:%M:%S')
    # initialize
    first_specimen_time = datetime.strptime(df.loc[row, 'SPECIMN_TAKEN_TIME_1'], '%d%b%Y:%H:%M:%S')
    #define a variable to keep track of latest value seen
    last_spec_time = first_specimen_time #for now this is just the specimen 1 time 
    last_specimen_index = 1 #readings are 1-indexed, not 0-indexed
    #collect max values for up to the first 7 days of admission
    for days in range(7):
        #tsList = [] # collection of lab value readings that fit time range in the while loop
        maxRead = 0 # init max reading for each day to 0
        #print('Day '+ str(days + 1)) #for testing
        while last_spec_time.date() == first_specimen_time.date()+timedelta(days=1)*days:
            if last_specimen_index <21: #'21' => columns beyond lab reading 21 deleted from second version of data set (file2.xlsx)
                specTime = df.loc[row, 'SPECIMN_TAKEN_TIME_'+str(last_specimen_index)]
                if pd.isna(specTime): # no such timestamp
                    #print('breaking away') #for testing
                    break
                elif pd.notna(specTime): #there is a reading
                    last_spec_time = datetime.strptime(specTime , '%d%b%Y:%H:%M:%S')
                    #update current max
                    tmpMax = df.loc[row,'LAB_VALUE_'+str(last_specimen_index)]
                    if tmpMax > maxRead:
                        maxRead = tmpMax
                        df.loc[row,'Max_Lab_Val_'+str(days+1)] = maxRead
                        df.loc[row,'Max_Lab_Val_TS_'+str(days+1)] = last_spec_time
                        #tsList.append(df.loc[row,'LAB_VALUE_'+str(last_specimen_index)])
                        #tsList #for testing
                last_specimen_index += 1
                tmptime = df.loc[row, 'SPECIMN_TAKEN_TIME_'+str(last_specimen_index)]
                if pd.notna(tmptime):
                    last_spec_time = datetime.strptime(df.loc[row, 'SPECIMN_TAKEN_TIME_'+str(last_specimen_index)], '%d%b%Y:%H:%M:%S')
                else:
                    break
            else:
                #print('Index exceed 21')
                break


##Testing
df.loc[33:37, ['SPECIMN_TAKEN_TIME_1','LAB_VALUE_1',
             'SPECIMN_TAKEN_TIME_2','LAB_VALUE_2',
             'SPECIMN_TAKEN_TIME_3','LAB_VALUE_3',
             'SPECIMN_TAKEN_TIME_4','LAB_VALUE_4',
             'SPECIMN_TAKEN_TIME_5','LAB_VALUE_5',
             'SPECIMN_TAKEN_TIME_6','LAB_VALUE_6',
             'SPECIMN_TAKEN_TIME_7','LAB_VALUE_7',
             'SPECIMN_TAKEN_TIME_8','LAB_VALUE_8',
             'SPECIMN_TAKEN_TIME_9','LAB_VALUE_9',
             'SPECIMN_TAKEN_TIME_10','LAB_VALUE_10',
             'SPECIMN_TAKEN_TIME_11','LAB_VALUE_11',
             'SPECIMN_TAKEN_TIME_12','LAB_VALUE_12',
             'SPECIMN_TAKEN_TIME_13','LAB_VALUE_13',
             'SPECIMN_TAKEN_TIME_14','LAB_VALUE_14',
             'SPECIMN_TAKEN_TIME_15','LAB_VALUE_15',
             'Max_Lab_Val_TS_1' ,'Max_Lab_Val_1', 
             'Max_Lab_Val_TS_2' ,'Max_Lab_Val_2',
             'Max_Lab_Val_TS_3' ,'Max_Lab_Val_3', 
             'Max_Lab_Val_TS_4' ,'Max_Lab_Val_4', 
             'Max_Lab_Val_TS_5' ,'Max_Lab_Val_5',
             'Max_Lab_Val_TS_6' ,'Max_Lab_Val_6', 
             'Max_Lab_Val_TS_7' ,'Max_Lab_Val_7' ]].T





# Export to excel
df.to_excel('./outputFile.xlsx')