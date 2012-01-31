datadir='rebuckley/data'
for year in '12'
do
    echo "Getting files for: $year"
    
    #Independent expenditures
    curl -o $datadir/$year/IndependentExpenditure_$year.csv "http://www.fec.gov/data/IndependentExpenditure.do?format=csv&election_yr=20$year"

done