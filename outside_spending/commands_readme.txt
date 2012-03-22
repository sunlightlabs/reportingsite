# this probably needn't be a shell script anymore, but it's cut down from a much bigger one.

# Get the committee and candidate master files
source get_fec_files.sh

# read/update committee list
python manage.py pop_committees 12

# read/update candidates list
python manage.py pop_candidates 12

###

# update superpacs

python manage.py read_superpac_list

# set the hybrids (it's from a list)

python manage.py read_hybrid_list

---

# using old expenditures, and loading routines:

python manage.py pop_ie 12
python manage.py cull_amended
python manage.py attach_models
python manage.py fix_office
python manage.py calculate_sums
python manage.py make_candidate_pacs
python manage.py make_race_aggregates
python manage.py make_candidate_aggregates
python manage.py make_state_aggregates
python manage.py make_presidential_state_pac_aggregates

President_State_Pac_Aggregate

--> This still doesn't deal with EC aggregates!!!

---

python manage.py load_contribs
python manage.py  remove_duplicate_contribs
python manage.py attach_models
python manage.py set_contrib_flags


