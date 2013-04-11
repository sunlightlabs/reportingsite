## These are hacked up to be run locally!!!

envdir=/Users/jfenton/reporting/reporting-env/bin
datadir=/Users/jfenton/reporting/reportingsitenew/reportingsite/outside_spending_2014/data
managedir=/Users/jfenton/reporting/reportingsitenew/reportingsite

for year in '14'
do
    echo "Getting files for: $year"
    
    ## Master candidates file -- includes *all* candidates
    
    #curl -o $datadir/$year/cn$year.zip ftp://ftp.fec.gov/FEC/20$year/cn$year.zip 
    #unzip -o $datadir/$year/cn$year.zip -d $datadir/$year

    #sleep 1
    
    ## Master committee file -- includes *all* committees
    #curl -o $datadir/$year/cm$year.zip ftp://ftp.fec.gov/FEC/20$year/cm$year.zip
    #unzip -o $datadir/$year/cm$year.zip -d $datadir/$year  

done

source $envdir/activate
$managedir/manage.py pop_committees 14
$managedir/manage.py pop_candidates 14
