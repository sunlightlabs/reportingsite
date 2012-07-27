#!/bin/bash

# Save a copy of the database to a file named with the day of the week. Simpler than rotating logs - 
DAYOFWEEK=`date +%A`;
echo $DAYOFWEEK
BACKUPBASEDIR=/Users/jfenton/reporting/reportingsitenew/reportingsite/reporting/scripts

# just back up reporting on a daily basis
for PROJECT in 'reporting' 
do
    BACKUPFILENAME=$BACKUPBASEDIR/$PROJECT-$DAYOFWEEK.json;
    echo 'Now backing up to file:' $BACKUPFILENAME
    python /Users/jfenton/reporting/reportingsitenew/reportingsite/manage.py dumpdata --format=json $PROJECT > $BACKUPFILENAME
    python /Users/jfenton/reporting/reportingsitenew/reportingsite/reporting/scripts/backup_to_s3.py $PROJECT-$DAYOFWEEK.json
    
    # now send the file to the backup dir. 
    

done

