#!/bin/bash
NAME=reporting
PROJ=reportingsite

datadir=/projects/$NAME/src/$PROJ/outside_spending/data

for year in '14'
do
    echo "Getting files for: $year"
    
    # Master candidates file -- includes *all* candidates
    curl -o $datadir/$year/cn$year.zip ftp://ftp.fec.gov/FEC/20$year/cn$year.zip 
    unzip -o $datadir/$year/cn$year.zip -d $datadir/$year

    sleep 1
    
    # Master committee file -- includes *all* committees
    curl -o $datadir/$year/cm$year.zip ftp://ftp.fec.gov/FEC/20$year/cm$year.zip
    unzip -o $datadir/$year/cm$year.zip -d $datadir/$year  

done

source /projects/$NAME/virt/bin/activate
/projects/$NAME/src/$PROJ/manage.py pop_committees 14
/projects/$NAME/src/$PROJ/manage.py pop_candidates 14
