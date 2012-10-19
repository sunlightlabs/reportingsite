import datetime

janfirst2012 = datetime.date(2012,1,1)
oneweek = datetime.timedelta(days=7)
oneday = datetime.timedelta(days=1)

def summarize_monthly(summed_queryset, end_date, include_end_month=False, start_year=2011):
    #print monthly_data
    month_hash = {}
    monthly_list = []
    # crazy utc month numbering runs from 0 to 11
    for month in summed_queryset:
        this_month = {
        'month':int(month[1])-1,
        'year':month[0],
        'data':month[2]/1000000
        }
        key = "%s-%s" % (month[0], int(month[1]-1))
        #print key
        month_hash[key]=this_month

    # make key list
    this_month = 0
    this_year = start_year

    if not end_date:
        end_date = datetime.datetime.today()

    # Again, using utc month numbering runs from 0 to 11    
    final_month = int(end_date.strftime("%m")) 
    final_year = int(end_date.strftime("%Y"))
    if include_end_month:
        final_month += 1

    keylist = []
    while (this_year*12+this_month < final_year*12+final_month-1):
        this_key = "%s-%s" % (this_year, this_month)
        keylist.append(this_key)
        this_month += 1
        if (this_month==12):
            this_year += 1
            this_month = 0
    #print "keylist is: %s from end date: %s " % (keylist, end_date)

    for key in (keylist):
        try:
            monthly_list.append(month_hash[key])
            #print "trying key %s" % key
        except KeyError:
            date_string = key.split("-")
            monthly_list.append({
                'month':int(date_string[1]),
                'year':date_string[0],
                'data':0
            })
    return monthly_list


def get_utc_date_from_2012_week_num(weeknum):
    last_day_of_week = janfirst2012 + weeknum*oneweek - oneday
    return [last_day_of_week.month-1, last_day_of_week.day]
    print weeknum, last_day_of_week

def summarize_weekly(summed_queryset):
    # start in week 9
    weekly_list = []
    for week in summed_queryset:
        [utc_month, day] = get_utc_date_from_2012_week_num(week[1])
        weekly_list.append({
        'year':2012,
        'month':utc_month,
        'day':day,
        'data':week[2]/1000000,
        })
    return weekly_list