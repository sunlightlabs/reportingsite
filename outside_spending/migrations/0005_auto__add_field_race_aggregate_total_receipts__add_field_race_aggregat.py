# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Race_Aggregate.total_receipts'
        db.add_column('outside_spending_race_aggregate', 'total_receipts', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2), keep_default=False)

        # Adding field 'Race_Aggregate.general_ies'
        db.add_column('outside_spending_race_aggregate', 'general_ies', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2), keep_default=False)

        # Adding field 'Race_Aggregate.total_receipts_gen_candidates'
        db.add_column('outside_spending_race_aggregate', 'total_receipts_gen_candidates', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2), keep_default=False)

        # Adding field 'Race_Aggregate.percent_outside'
        db.add_column('outside_spending_race_aggregate', 'percent_outside', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2), keep_default=False)

        # Adding field 'Race_Aggregate.total_pro_dem_general'
        db.add_column('outside_spending_race_aggregate', 'total_pro_dem_general', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2), keep_default=False)

        # Adding field 'Race_Aggregate.total_pro_rep_general'
        db.add_column('outside_spending_race_aggregate', 'total_pro_rep_general', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2), keep_default=False)

        # Adding field 'Race_Aggregate.winner'
        db.add_column('outside_spending_race_aggregate', 'winner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['outside_spending.Candidate_Overlay'], null=True), keep_default=False)

        # Adding field 'Race_Aggregate.is_freshman'
        db.add_column('outside_spending_race_aggregate', 'is_freshman', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True), keep_default=False)

        # Adding field 'Race_Aggregate.cook_rating'
        db.add_column('outside_spending_race_aggregate', 'cook_rating', self.gf('django.db.models.fields.CharField')(max_length=31, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Race_Aggregate.total_receipts'
        db.delete_column('outside_spending_race_aggregate', 'total_receipts')

        # Deleting field 'Race_Aggregate.general_ies'
        db.delete_column('outside_spending_race_aggregate', 'general_ies')

        # Deleting field 'Race_Aggregate.total_receipts_gen_candidates'
        db.delete_column('outside_spending_race_aggregate', 'total_receipts_gen_candidates')

        # Deleting field 'Race_Aggregate.percent_outside'
        db.delete_column('outside_spending_race_aggregate', 'percent_outside')

        # Deleting field 'Race_Aggregate.total_pro_dem_general'
        db.delete_column('outside_spending_race_aggregate', 'total_pro_dem_general')

        # Deleting field 'Race_Aggregate.total_pro_rep_general'
        db.delete_column('outside_spending_race_aggregate', 'total_pro_rep_general')

        # Deleting field 'Race_Aggregate.winner'
        db.delete_column('outside_spending_race_aggregate', 'winner_id')

        # Deleting field 'Race_Aggregate.is_freshman'
        db.delete_column('outside_spending_race_aggregate', 'is_freshman')

        # Deleting field 'Race_Aggregate.cook_rating'
        db.delete_column('outside_spending_race_aggregate', 'cook_rating')


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
            'cand_cand_contrib': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'cand_cand_loans': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'cand_debts_owed_by': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'cand_ending_cash': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'cand_ici': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'cand_is_gen_winner': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'cand_report_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'cand_total_disbursements': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'cand_ttl_ind_contribs': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'cand_ttl_receipts': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
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
            'is_general_candidate': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
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
            'cook_rating': ('django.db.models.fields.CharField', [], {'max_length': '31', 'null': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'expenditures_opposing': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'expenditures_supporting': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'general_ies': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_freshman': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'office': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'percent_outside': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'total_ec': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_ind_exp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_pro_dem_general': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_pro_rep_general': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_receipts': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'total_receipts_gen_candidates': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2'}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['outside_spending.Candidate_Overlay']", 'null': 'True'})
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
