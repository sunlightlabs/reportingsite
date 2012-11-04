# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Scrape_Time'
        db.create_table('outside_spending_scrape_time', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('run_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('outside_spending', ['Scrape_Time'])

        # Adding model 'Filing_Scrape_Time'
        db.create_table('outside_spending_filing_scrape_time', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('run_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('outside_spending', ['Filing_Scrape_Time'])

        # Adding model 'Candidate'
        db.create_table('outside_spending_candidate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cycle', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('fec_id', self.gf('django.db.models.fields.CharField')(max_length=9, blank=True)),
            ('fec_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('party', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('office', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('seat_status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('candidate_status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('state_address', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('district', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('state_race', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('campaign_com_fec_id', self.gf('django.db.models.fields.CharField')(max_length=9, blank=True)),
        ))
        db.send_create_signal('outside_spending', ['Candidate'])

        # Adding model 'Committee'
        db.create_table('outside_spending_committee', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('fec_id', self.gf('django.db.models.fields.CharField')(max_length=9, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100, db_index=True)),
            ('party', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('treasurer', self.gf('django.db.models.fields.CharField')(max_length=38, null=True, blank=True)),
            ('street_1', self.gf('django.db.models.fields.CharField')(max_length=34, null=True, blank=True)),
            ('street_2', self.gf('django.db.models.fields.CharField')(max_length=34, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=18, null=True, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=9, null=True, blank=True)),
            ('state_race', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('designation', self.gf('django.db.models.fields.CharField')(max_length=1, null=True)),
            ('ctype', self.gf('django.db.models.fields.CharField')(max_length=1, null=True)),
            ('tax_status', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('filing_frequency', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('interest_group_cat', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('connected_org_name', self.gf('django.db.models.fields.CharField')(max_length=65, blank=True)),
            ('candidate_id', self.gf('django.db.models.fields.CharField')(max_length=9, blank=True)),
            ('candidate_office', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('is_superpac', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('is_hybrid', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('is_nonprofit', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('related_candidate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['outside_spending.Candidate'], null=True)),
        ))
        db.send_create_signal('outside_spending', ['Committee'])

        # Adding model 'Committee_Overlay'
        db.create_table('outside_spending_committee_overlay', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('committee_master_record', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['outside_spending.Committee'], null=True)),
            ('cycle', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('fec_id', self.gf('django.db.models.fields.CharField')(max_length=9, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100, db_index=True)),
            ('party', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('treasurer', self.gf('django.db.models.fields.CharField')(max_length=38, null=True, blank=True)),
            ('street_1', self.gf('django.db.models.fields.CharField')(max_length=34, null=True, blank=True)),
            ('street_2', self.gf('django.db.models.fields.CharField')(max_length=34, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=18, null=True, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=9, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('connected_org_name', self.gf('django.db.models.fields.CharField')(max_length=65, blank=True)),
            ('filing_frequency', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('candidate_id', self.gf('django.db.models.fields.CharField')(max_length=9, blank=True)),
            ('candidate_office', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('profile_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('supporting', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('superpac_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('has_contributions', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('total_contributions', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('total_unitemized', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('has_electioneering', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('has_independent_expenditures', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('total_indy_expenditures', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('ie_support_dems', self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=19, decimal_places=2)),
            ('ie_oppose_dems', self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=19, decimal_places=2)),
            ('ie_support_reps', self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=19, decimal_places=2)),
            ('ie_oppose_reps', self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=19, decimal_places=2)),
            ('total_presidential_indy_expenditures', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('total_electioneering', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('cash_on_hand', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('cash_on_hand_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('is_superpac', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('is_hybrid', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('is_c4', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('is_noncommittee', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('is_labor_related', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('is_business', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('org_status', self.gf('django.db.models.fields.CharField')(max_length=31, null=True, blank=True)),
            ('political_orientation', self.gf('django.db.models.fields.CharField')(max_length=1, null=True)),
            ('political_orientation_verified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('designation', self.gf('django.db.models.fields.CharField')(max_length=1, null=True)),
            ('ctype', self.gf('django.db.models.fields.CharField')(max_length=1, null=True)),
        ))
        db.send_create_signal('outside_spending', ['Committee_Overlay'])

        # Adding unique constraint on 'Committee_Overlay', fields ['cycle', 'fec_id']
        db.create_unique('outside_spending_committee_overlay', ['cycle', 'fec_id'])

        # Adding model 'Candidate_Overlay'
        db.create_table('outside_spending_candidate_overlay', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cycle', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('fec_id', self.gf('django.db.models.fields.CharField')(max_length=9, blank=True)),
            ('fec_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('party', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('office', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('seat_status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('candidate_status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('state_address', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('district', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('state_race', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('campaign_com_fec_id', self.gf('django.db.models.fields.CharField')(max_length=9, blank=True)),
            ('crp_id', self.gf('django.db.models.fields.CharField')(max_length=9, null=True, blank=True)),
            ('crp_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('td_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('transparencydata_id', self.gf('django.db.models.fields.CharField')(default='', max_length=40, null=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('total_expenditures', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('expenditures_supporting', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('expenditures_opposing', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('electioneering', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
        ))
        db.send_create_signal('outside_spending', ['Candidate_Overlay'])

        # Adding model 'Expenditure'
        db.create_table('outside_spending_expenditure', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cycle', self.gf('django.db.models.fields.CharField')(max_length=4, null=True)),
            ('image_number', self.gf('django.db.models.fields.BigIntegerField')()),
            ('line_hash', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('raw_committee_id', self.gf('django.db.models.fields.CharField')(max_length=9, null=True)),
            ('committee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['outside_spending.Committee_Overlay'], null=True)),
            ('payee', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('expenditure_purpose', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('expenditure_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('expenditure_amount', self.gf('django.db.models.fields.DecimalField')(max_digits=19, decimal_places=2)),
            ('support_oppose', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('election_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('candidate_name', self.gf('django.db.models.fields.CharField')(max_length=90, null=True, blank=True)),
            ('raw_candidate_id', self.gf('django.db.models.fields.CharField')(max_length=9, null=True)),
            ('candidate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['outside_spending.Candidate_Overlay'], null=True, blank=True)),
            ('candidate_party_affiliation', self.gf('django.db.models.fields.CharField')(max_length=10, null=True)),
            ('office', self.gf('django.db.models.fields.CharField')(max_length=1, null=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('district', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('transaction_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('receipt_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('filing_number', self.gf('django.db.models.fields.IntegerField')()),
            ('amendment', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('race', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('pdf_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('committee_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('superceded_by_amendment', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('amends_earlier_filing', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('amended_by', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('amends_filing', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('process_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('filing_source', self.gf('django.db.models.fields.CharField')(max_length=7, null=True, blank=True)),
            ('superceded_by_f3x', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('superceding_f3x', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('memo_code', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('memo_text_description', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('outside_spending', ['Expenditure'])

        # Adding unique constraint on 'Expenditure', fields ['filing_number', 'transaction_id']
        db.create_unique('outside_spending_expenditure', ['filing_number', 'transaction_id'])

        # Adding model 'Transparency_Crosswalk'
        db.create_table('outside_spending_transparency_crosswalk', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
            ('entity_type', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('td_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('td_id', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('fec_candidate_id', self.gf('django.db.models.fields.CharField')(max_length=9)),
            ('crp_candidate_id', self.gf('django.db.models.fields.CharField')(max_length=9)),
        ))
        db.send_create_signal('outside_spending', ['Transparency_Crosswalk'])

        # Adding model 'Pac_Candidate'
        db.create_table('outside_spending_pac_candidate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('committee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['outside_spending.Committee_Overlay'])),
            ('candidate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['outside_spending.Candidate_Overlay'])),
            ('support_oppose', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('total_ind_exp', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('total_ec', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
        ))
        db.send_create_signal('outside_spending', ['Pac_Candidate'])

        # Adding model 'Race_Aggregate'
        db.create_table('outside_spending_race_aggregate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('office', self.gf('django.db.models.fields.CharField')(max_length=1, null=True)),
            ('district', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('expenditures_supporting', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('expenditures_opposing', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('total_ind_exp', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('total_ec', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
        ))
        db.send_create_signal('outside_spending', ['Race_Aggregate'])

        # Adding model 'State_Aggregate'
        db.create_table('outside_spending_state_aggregate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('expenditures_supporting_president', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('expenditures_opposing_president', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('total_pres_ind_exp', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('expenditures_supporting_house', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('expenditures_opposing_house', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('total_house_ind_exp', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('expenditures_supporting_senate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('expenditures_opposing_senate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('total_senate_ind_exp', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('total_ind_exp', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('recent_ind_exp', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('recent_pres_exp', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('total_ec', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
        ))
        db.send_create_signal('outside_spending', ['State_Aggregate'])

        # Adding model 'President_State_Pac_Aggregate'
        db.create_table('outside_spending_president_state_pac_aggregate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('committee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['outside_spending.Committee_Overlay'])),
            ('candidate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['outside_spending.Candidate_Overlay'])),
            ('support_oppose', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('expenditures', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
            ('recent_expenditures', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2)),
        ))
        db.send_create_signal('outside_spending', ['President_State_Pac_Aggregate'])

        # Adding model 'Contribution'
        db.create_table('outside_spending_contribution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('line_type', self.gf('django.db.models.fields.CharField')(max_length=7)),
            ('from_amended_filing', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('committee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['outside_spending.Committee_Overlay'], null=True)),
            ('committee_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('fec_committeeid', self.gf('django.db.models.fields.CharField')(max_length=9)),
            ('filing_number', self.gf('django.db.models.fields.IntegerField')()),
            ('transaction_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('back_ref_tran_id', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('back_ref_sked_name', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('entity_type', self.gf('django.db.models.fields.CharField')(max_length=5, blank=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('contrib_org', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('contrib_last', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('contrib_first', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('contrib_middle', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('contrib_prefix', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('contrib_suffix', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('contrib_street_1', self.gf('django.db.models.fields.CharField')(max_length=34, blank=True)),
            ('contrib_street_2', self.gf('django.db.models.fields.CharField')(max_length=34, blank=True)),
            ('contrib_city', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('contrib_state', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('contrib_zip', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('contrib_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('contrib_amt', self.gf('django.db.models.fields.DecimalField')(max_digits=19, decimal_places=2)),
            ('contrib_agg', self.gf('django.db.models.fields.DecimalField')(max_digits=19, decimal_places=2)),
            ('contrib_purpose', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('contrib_employer', self.gf('django.db.models.fields.CharField')(max_length=38, blank=True)),
            ('contrib_occupation', self.gf('django.db.models.fields.CharField')(max_length=38, blank=True)),
            ('memo_agg_item', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('memo_text_descript', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('superceded_by_amendment', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('amends_earlier_filing', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('amended_by', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('original', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('outside_spending', ['Contribution'])

        # Adding model 'Electioneering_94'
        db.create_table('outside_spending_electioneering_94', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('can_id', self.gf('django.db.models.fields.CharField')(max_length=9)),
            ('can_name', self.gf('django.db.models.fields.CharField')(max_length=127)),
            ('imageno', self.gf('django.db.models.fields.BigIntegerField')()),
            ('ele_yr', self.gf('django.db.models.fields.IntegerField')()),
            ('receipt_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('can_off', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('can_state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('transaction_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('filing_number', self.gf('django.db.models.fields.IntegerField')()),
            ('ele_typ', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('group_id', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('fec_id', self.gf('django.db.models.fields.CharField')(max_length=9)),
            ('br_tran_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('amnd_ind', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('superceded_by_amendment', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('candidate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['outside_spending.Candidate_Overlay'], null=True)),
        ))
        db.send_create_signal('outside_spending', ['Electioneering_94'])

        # Adding unique constraint on 'Electioneering_94', fields ['filing_number', 'transaction_id']
        db.create_unique('outside_spending_electioneering_94', ['filing_number', 'transaction_id'])

        # Adding model 'Electioneering_93'
        db.create_table('outside_spending_electioneering_93', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('exp_amo', self.gf('django.db.models.fields.DecimalField')(max_digits=19, decimal_places=2)),
            ('imageno', self.gf('django.db.models.fields.BigIntegerField')()),
            ('ele_yr', self.gf('django.db.models.fields.IntegerField')()),
            ('receipt_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('spe_nam', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('payee', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('purpose', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('exp_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('transaction_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('filing_number', self.gf('django.db.models.fields.IntegerField')()),
            ('ele_typ', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('group_id', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('fec_id', self.gf('django.db.models.fields.CharField')(max_length=9)),
            ('br_tran_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('amnd_ind', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('superceded_by_amendment', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('committee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['outside_spending.Committee_Overlay'], null=True)),
        ))
        db.send_create_signal('outside_spending', ['Electioneering_93'])

        # Adding unique constraint on 'Electioneering_93', fields ['filing_number', 'transaction_id']
        db.create_unique('outside_spending_electioneering_93', ['filing_number', 'transaction_id'])

        # Adding M2M table for field target on 'Electioneering_93'
        db.create_table('outside_spending_electioneering_93_target', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('electioneering_93', models.ForeignKey(orm['outside_spending.electioneering_93'], null=False)),
            ('electioneering_94', models.ForeignKey(orm['outside_spending.electioneering_94'], null=False))
        ))
        db.create_unique('outside_spending_electioneering_93_target', ['electioneering_93_id', 'electioneering_94_id'])

        # Adding model 'F3X_Summary'
        db.create_table('outside_spending_f3x_summary', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filing_number', self.gf('django.db.models.fields.IntegerField')()),
            ('amended', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('committee_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('fec_id', self.gf('django.db.models.fields.CharField')(max_length=9)),
            ('address_change', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('street_1', self.gf('django.db.models.fields.CharField')(max_length=34, blank=True)),
            ('street_2', self.gf('django.db.models.fields.CharField')(max_length=34, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('coverage_from_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('coverage_to_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('coh_begin', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2, blank=True)),
            ('total_receipts', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2, blank=True)),
            ('total_disbursements', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2, blank=True)),
            ('coh_close', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2, blank=True)),
            ('itemized', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2, blank=True)),
            ('unitemized', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2, blank=True)),
            ('debts_owed', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2, blank=True)),
            ('total_sched_e', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2, blank=True)),
            ('ytd_total_receipts', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2, blank=True)),
            ('ytd_total_disbursements', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2, blank=True)),
            ('ytd_sched_e', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2, blank=True)),
            ('superceded_by_amendment', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('amends_earlier_filing', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('amended_by', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('original', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('outside_spending', ['F3X_Summary'])

        # Adding model 'unprocessed_filing'
        db.create_table('outside_spending_unprocessed_filing', (
            ('fec_id', self.gf('django.db.models.fields.CharField')(max_length=9)),
            ('committee_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('filing_number', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('form_type', self.gf('django.db.models.fields.CharField')(max_length=7)),
            ('filed_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('coverage_from_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('coverage_to_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('process_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('is_superpac', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('filing_is_parsed', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
        ))
        db.send_create_signal('outside_spending', ['unprocessed_filing'])

        # Adding model 'processing_memo'
        db.create_table('outside_spending_processing_memo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=127)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('outside_spending', ['processing_memo'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Electioneering_93', fields ['filing_number', 'transaction_id']
        db.delete_unique('outside_spending_electioneering_93', ['filing_number', 'transaction_id'])

        # Removing unique constraint on 'Electioneering_94', fields ['filing_number', 'transaction_id']
        db.delete_unique('outside_spending_electioneering_94', ['filing_number', 'transaction_id'])

        # Removing unique constraint on 'Expenditure', fields ['filing_number', 'transaction_id']
        db.delete_unique('outside_spending_expenditure', ['filing_number', 'transaction_id'])

        # Removing unique constraint on 'Committee_Overlay', fields ['cycle', 'fec_id']
        db.delete_unique('outside_spending_committee_overlay', ['cycle', 'fec_id'])

        # Deleting model 'Scrape_Time'
        db.delete_table('outside_spending_scrape_time')

        # Deleting model 'Filing_Scrape_Time'
        db.delete_table('outside_spending_filing_scrape_time')

        # Deleting model 'Candidate'
        db.delete_table('outside_spending_candidate')

        # Deleting model 'Committee'
        db.delete_table('outside_spending_committee')

        # Deleting model 'Committee_Overlay'
        db.delete_table('outside_spending_committee_overlay')

        # Deleting model 'Candidate_Overlay'
        db.delete_table('outside_spending_candidate_overlay')

        # Deleting model 'Expenditure'
        db.delete_table('outside_spending_expenditure')

        # Deleting model 'Transparency_Crosswalk'
        db.delete_table('outside_spending_transparency_crosswalk')

        # Deleting model 'Pac_Candidate'
        db.delete_table('outside_spending_pac_candidate')

        # Deleting model 'Race_Aggregate'
        db.delete_table('outside_spending_race_aggregate')

        # Deleting model 'State_Aggregate'
        db.delete_table('outside_spending_state_aggregate')

        # Deleting model 'President_State_Pac_Aggregate'
        db.delete_table('outside_spending_president_state_pac_aggregate')

        # Deleting model 'Contribution'
        db.delete_table('outside_spending_contribution')

        # Deleting model 'Electioneering_94'
        db.delete_table('outside_spending_electioneering_94')

        # Deleting model 'Electioneering_93'
        db.delete_table('outside_spending_electioneering_93')

        # Removing M2M table for field target on 'Electioneering_93'
        db.delete_table('outside_spending_electioneering_93_target')

        # Deleting model 'F3X_Summary'
        db.delete_table('outside_spending_f3x_summary')

        # Deleting model 'unprocessed_filing'
        db.delete_table('outside_spending_unprocessed_filing')

        # Deleting model 'processing_memo'
        db.delete_table('outside_spending_processing_memo')


    models = {
        'outside_spending.candidate': {
            'Meta': {'object_name': 'Candidate'},
            'campaign_com_fec_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'candidate_status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'cycle': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'fec_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'fec_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'office': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'party': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'seat_status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'state_address': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'state_race': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'})
        },
        'outside_spending.candidate_overlay': {
            'Meta': {'object_name': 'Candidate_Overlay'},
            'campaign_com_fec_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'candidate_status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'crp_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'}),
            'crp_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'cycle': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'electioneering': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'expenditures_opposing': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'expenditures_supporting': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'fec_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'fec_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'office': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'party': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'seat_status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'state_address': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'state_race': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'td_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'total_expenditures': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'transparencydata_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'null': 'True'})
        },
        'outside_spending.committee': {
            'Meta': {'object_name': 'Committee'},
            'candidate_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'candidate_office': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '18', 'null': 'True', 'blank': 'True'}),
            'connected_org_name': ('django.db.models.fields.CharField', [], {'max_length': '65', 'blank': 'True'}),
            'ctype': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'designation': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'fec_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'filing_frequency': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest_group_cat': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'is_hybrid': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_nonprofit': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_superpac': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'party': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'related_candidate': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['outside_spending.Candidate']", 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'state_race': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'street_1': ('django.db.models.fields.CharField', [], {'max_length': '34', 'null': 'True', 'blank': 'True'}),
            'street_2': ('django.db.models.fields.CharField', [], {'max_length': '34', 'null': 'True', 'blank': 'True'}),
            'tax_status': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'treasurer': ('django.db.models.fields.CharField', [], {'max_length': '38', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'})
        },
        'outside_spending.committee_overlay': {
            'Meta': {'ordering': "('-total_indy_expenditures',)", 'unique_together': "(('cycle', 'fec_id'),)", 'object_name': 'Committee_Overlay'},
            'candidate_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'candidate_office': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'cash_on_hand': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'cash_on_hand_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '18', 'null': 'True', 'blank': 'True'}),
            'committee_master_record': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['outside_spending.Committee']", 'null': 'True'}),
            'connected_org_name': ('django.db.models.fields.CharField', [], {'max_length': '65', 'blank': 'True'}),
            'ctype': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'cycle': ('django.db.models.fields.IntegerField', [], {}),
            'designation': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'fec_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'filing_frequency': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'has_contributions': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'has_electioneering': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'has_independent_expenditures': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ie_oppose_dems': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'ie_oppose_reps': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'ie_support_dems': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'ie_support_reps': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'is_business': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_c4': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_hybrid': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_labor_related': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_noncommittee': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'is_superpac': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'org_status': ('django.db.models.fields.CharField', [], {'max_length': '31', 'null': 'True', 'blank': 'True'}),
            'party': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'political_orientation': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'political_orientation_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'profile_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'street_1': ('django.db.models.fields.CharField', [], {'max_length': '34', 'null': 'True', 'blank': 'True'}),
            'street_2': ('django.db.models.fields.CharField', [], {'max_length': '34', 'null': 'True', 'blank': 'True'}),
            'superpac_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'supporting': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'total_contributions': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_electioneering': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_indy_expenditures': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_presidential_indy_expenditures': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_unitemized': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'treasurer': ('django.db.models.fields.CharField', [], {'max_length': '38', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'})
        },
        'outside_spending.contribution': {
            'Meta': {'ordering': "('-contrib_amt',)", 'object_name': 'Contribution'},
            'amended_by': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'amends_earlier_filing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'back_ref_sked_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'back_ref_tran_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'committee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['outside_spending.Committee_Overlay']", 'null': 'True'}),
            'committee_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'contrib_agg': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '2'}),
            'contrib_amt': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '2'}),
            'contrib_city': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'contrib_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'contrib_employer': ('django.db.models.fields.CharField', [], {'max_length': '38', 'blank': 'True'}),
            'contrib_first': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'contrib_last': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'contrib_middle': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'contrib_occupation': ('django.db.models.fields.CharField', [], {'max_length': '38', 'blank': 'True'}),
            'contrib_org': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'contrib_prefix': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'contrib_purpose': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'contrib_state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'contrib_street_1': ('django.db.models.fields.CharField', [], {'max_length': '34', 'blank': 'True'}),
            'contrib_street_2': ('django.db.models.fields.CharField', [], {'max_length': '34', 'blank': 'True'}),
            'contrib_suffix': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'contrib_zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'entity_type': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'fec_committeeid': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'filing_number': ('django.db.models.fields.IntegerField', [], {}),
            'from_amended_filing': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_type': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'memo_agg_item': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'memo_text_descript': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'original': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'superceded_by_amendment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'outside_spending.electioneering_93': {
            'Meta': {'unique_together': "(('filing_number', 'transaction_id'),)", 'object_name': 'Electioneering_93'},
            'amnd_ind': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'br_tran_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'committee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['outside_spending.Committee_Overlay']", 'null': 'True'}),
            'ele_typ': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'ele_yr': ('django.db.models.fields.IntegerField', [], {}),
            'exp_amo': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '2'}),
            'exp_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'fec_id': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'filing_number': ('django.db.models.fields.IntegerField', [], {}),
            'group_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imageno': ('django.db.models.fields.BigIntegerField', [], {}),
            'payee': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'purpose': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'receipt_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'spe_nam': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'superceded_by_amendment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'target': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['outside_spending.Electioneering_94']", 'null': 'True', 'symmetrical': 'False'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'outside_spending.electioneering_94': {
            'Meta': {'unique_together': "(('filing_number', 'transaction_id'),)", 'object_name': 'Electioneering_94'},
            'amnd_ind': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'br_tran_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'can_id': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'can_name': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'can_off': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'can_state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'candidate': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['outside_spending.Candidate_Overlay']", 'null': 'True'}),
            'ele_typ': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'ele_yr': ('django.db.models.fields.IntegerField', [], {}),
            'fec_id': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'filing_number': ('django.db.models.fields.IntegerField', [], {}),
            'group_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imageno': ('django.db.models.fields.BigIntegerField', [], {}),
            'receipt_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'superceded_by_amendment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'outside_spending.expenditure': {
            'Meta': {'ordering': "('-expenditure_date',)", 'unique_together': "(('filing_number', 'transaction_id'),)", 'object_name': 'Expenditure'},
            'amended_by': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'amendment': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'amends_earlier_filing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'amends_filing': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'candidate': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['outside_spending.Candidate_Overlay']", 'null': 'True', 'blank': 'True'}),
            'candidate_name': ('django.db.models.fields.CharField', [], {'max_length': '90', 'null': 'True', 'blank': 'True'}),
            'candidate_party_affiliation': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'committee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['outside_spending.Committee_Overlay']", 'null': 'True'}),
            'committee_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'cycle': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'election_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'expenditure_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '2'}),
            'expenditure_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'expenditure_purpose': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'filing_number': ('django.db.models.fields.IntegerField', [], {}),
            'filing_source': ('django.db.models.fields.CharField', [], {'max_length': '7', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_number': ('django.db.models.fields.BigIntegerField', [], {}),
            'line_hash': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'memo_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'memo_text_description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'office': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'payee': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pdf_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'process_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'race': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'raw_candidate_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True'}),
            'raw_committee_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True'}),
            'receipt_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'superceded_by_amendment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'superceded_by_f3x': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'superceding_f3x': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'support_oppose': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'outside_spending.f3x_summary': {
            'Meta': {'object_name': 'F3X_Summary'},
            'address_change': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'amended': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'amended_by': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'amends_earlier_filing': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'coh_begin': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'coh_close': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'committee_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'coverage_from_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'coverage_to_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'debts_owed': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'fec_id': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'filing_number': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'itemized': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'original': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'street_1': ('django.db.models.fields.CharField', [], {'max_length': '34', 'blank': 'True'}),
            'street_2': ('django.db.models.fields.CharField', [], {'max_length': '34', 'blank': 'True'}),
            'superceded_by_amendment': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'total_disbursements': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'total_receipts': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'total_sched_e': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'unitemized': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'ytd_sched_e': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'ytd_total_disbursements': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'ytd_total_receipts': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'outside_spending.filing_scrape_time': {
            'Meta': {'object_name': 'Filing_Scrape_Time'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'run_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'outside_spending.pac_candidate': {
            'Meta': {'ordering': "('-total_ind_exp',)", 'object_name': 'Pac_Candidate'},
            'candidate': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['outside_spending.Candidate_Overlay']"}),
            'committee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['outside_spending.Committee_Overlay']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'support_oppose': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'total_ec': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_ind_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'})
        },
        'outside_spending.president_state_pac_aggregate': {
            'Meta': {'object_name': 'President_State_Pac_Aggregate'},
            'candidate': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['outside_spending.Candidate_Overlay']"}),
            'committee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['outside_spending.Committee_Overlay']"}),
            'expenditures': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recent_expenditures': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'support_oppose': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'outside_spending.processing_memo': {
            'Meta': {'object_name': 'processing_memo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'outside_spending.race_aggregate': {
            'Meta': {'ordering': "('-total_ind_exp',)", 'object_name': 'Race_Aggregate'},
            'district': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'expenditures_opposing': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'expenditures_supporting': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'office': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'total_ec': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_ind_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'})
        },
        'outside_spending.scrape_time': {
            'Meta': {'object_name': 'Scrape_Time'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'run_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'outside_spending.state_aggregate': {
            'Meta': {'object_name': 'State_Aggregate'},
            'expenditures_opposing_house': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'expenditures_opposing_president': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'expenditures_opposing_senate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'expenditures_supporting_house': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'expenditures_supporting_president': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'expenditures_supporting_senate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recent_ind_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'recent_pres_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'total_ec': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_house_ind_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_ind_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_pres_ind_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_senate_ind_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'})
        },
        'outside_spending.transparency_crosswalk': {
            'Meta': {'object_name': 'Transparency_Crosswalk'},
            'crp_candidate_id': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'entity_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'fec_candidate_id': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'td_id': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'td_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        'outside_spending.unprocessed_filing': {
            'Meta': {'object_name': 'unprocessed_filing'},
            'committee_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'coverage_from_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'coverage_to_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'fec_id': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'filed_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'filing_is_parsed': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'filing_number': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'form_type': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'is_superpac': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'process_time': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['outside_spending']
