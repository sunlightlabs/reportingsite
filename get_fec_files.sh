datadir='outside_spending/data'

for year in '12'
do
    echo "Getting files for: $year"
    
    # Master candidates file -- includes *all* candidates
    curl -o $datadir/$year/cn$year.zip ftp://ftp.fec.gov/FEC/cn$year.zip 
    unzip -o $datadir/$year/cn$year.zip -d $datadir/$year

    # Master committee file -- includes *all* committees
    curl -o $datadir/$year/cm$year.zip ftp://ftp.fec.gov/FEC/cm$year.zip
    unzip -o $datadir/$year/cm$year.zip -d $datadir/$year
    
    # Electioneering communications: 
    curl -o $datadir/$year/ec_exp_20$year.csv ftp://ftp.fec.gov/FEC/ec_exp_20$year.csv
    
    #Independent expenditures
    curl -o $datadir/$year/IndependentExpenditure_$year.csv "http://www.fec.gov/data/IndependentExpenditure.do?format=csv&election_yr=20$year"
    

done

# outside_spending/data/12/:
# cn12.zip          foiacm.dta
# cm12.zip          foiacn.dta

