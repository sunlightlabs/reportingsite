--
SET foreign_key_checks = 0;
drop table rebuckley_candidate;
drop table rebuckley_committee;
drop table rebuckley_contribution;
drop table rebuckley_expenditure_electioneering_candidates;
drop table rebuckley_expenditure;
drop table rebuckley_ieonlycommittee;
SET foreign_key_checks = 1;


-- drop everything! 
SET foreign_key_checks = 0;
drop table rebuckley_candidate;
drop table rebuckley_committee;
drop table rebuckley_contribution;
drop table rebuckley_expenditure_electioneering_candidates;
drop table rebuckley_expenditure;
drop table rebuckley_ieonlycommittee;
drop table rebuckley_f3x_summary;
drop table rebuckley_pac_candidate;
drop table rebuckley_president_state_pac_aggregate;
drop table rebuckley_race_aggregate;
drop table rebuckley_state_aggregate;
drop table rebuckley_candidate_overlay;
drop table rebuckley_committee_overlay;
drop table rebuckley_transparency_crosswalk;
SET foreign_key_checks = 1;


SET foreign_key_checks = 0;
drop table rebuckley_contribution;
drop table rebuckley_expenditure_electioneering_candidates;
drop table rebuckley_expenditure;
drop table rebuckley_ieonlycommittee;
SET foreign_key_checks = 1;


SET foreign_key_checks = 0;
drop table rebuckley_committee;
SET foreign_key_checks = 1;


SET foreign_key_checks = 0;
drop table rebuckley_expenditure;
SET foreign_key_checks = 1;


SET foreign_key_checks = 0;
drop table rebuckley_candidate;
SET foreign_key_checks = 1;


-----
-- For outside_spending iteration
SET foreign_key_checks = 0;
drop table outside_spending_scrape_time;
drop table outside_spending_committee;
drop table outside_spending_committee_overlay;
drop table outside_spending_candidate;
drop table outside_spending_candidate_overlay;
drop table outside_spending_filing_header;
drop table outside_spending_filing_rows;


drop table  outside_spending_expenditure;
drop table outside_spending_transparency_crosswalk;
drop table outside_spending_pac_candidate;
drop table outside_spending_race_aggregate;
drop table outside_spending_state_aggregate;
drop table outside_spending_president_state_pac_aggregate;
drop table outside_spending_contribution;
drop table outside_spending_electioneering_93;

SET foreign_key_checks = 1;
