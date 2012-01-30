datadir='rebuckley/data'

for year in '10' '12'
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
    curl -o $datadir/$year/IndependentExpenditure_$year.csv http://www.fec.gov/data/IndependentExpenditure.do?format=csv&election_yr=20$year
    
    # Committee summary file -- only contains records from those that have filed a quarterly / monthly / annual report
    curl -o $datadir/$year/CommitteeSummary_$year.csv "http://www.fec.gov/data/CommitteeSummary.do?format=csv&election_yr=20$year"
    
    # Indepedent expenditure file
    curl -o $datadir/$year/CandidateSummary_$year.csv http://www.fec.gov/data/CandidateSummary.do?format=csv&election_yr=20$year

done

# The result should look like this:

# $ ls  buckley/data/10/ buckley/data/12/
# buckley/data/10/:
# CandidateSummary_10.csv		cn10.zip
# CommitteeSummary_10.csv		ec_exp_2010.csv
# IndependentExpenditure_10.csv	foiacm.dta
# cm10.zip			foiacn.dta
# 
# buckley/data/12/:
# CandidateSummary_12.csv		cn12.zip
# CommitteeSummary_12.csv		ec_exp_2012.csv
# IndependentExpenditure_12.csv	foiacm.dta
# cm12.zip			foiacn.dta

