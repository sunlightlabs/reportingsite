from django.db import models
from django.db import connection
import datetime
import re
from django.contrib import admin

"""Recovery Explorer by Luke Rosiak for the Sunlight Foundation March 2010. To update with the latest data from Recovery.gov's download center:
http://www.recovery.gov/FAQ/Pages/DownloadCenter.aspx National Cumulative Summary
1) copy the millions_record table's structure and drop the primary key and award_date_new fields
2) import the raw CSV
3) add the primary key and the award_date_new field, updating the latter from award_date"""

class Record(models.Model):

    award_key = models.IntegerField()
    recipient_role = models.CharField(max_length=4)
    version_flag = models.CharField(max_length=4)
    status = models.CharField(max_length=4)
    active_flag = models.CharField(max_length=4)
    agency_reviewed_flag = models.CharField(max_length=4)
    prime_reviewed_flag = models.CharField(max_length=4)
    correction_flag = models.CharField(max_length=2)
    funding_agency_cd = models.CharField(max_length=7)
    funding_agency_name = models.CharField(max_length=255)
    awarding_agency_cd = models.CharField(max_length=7)
    awarding_agency_name = models.CharField(max_length=255)
    funding_tas = models.CharField(max_length=10)
    tas_sub_account = models.CharField(max_length=10)
    fiscal_year = models.IntegerField()
    fiscal_qtr = models.IntegerField()
    recipient_duns_number = models.IntegerField()
    sub_duns_number = models.IntegerField()
    recipient_namee = models.CharField(max_length=255)
    recipient_zip_code = models.CharField(max_length=10)
    recipient_state = models.CharField(max_length=2, db_column='recipient_statee')
    award_number = models.CharField(max_length=30, db_column='award_numbere')
    order_number = models.CharField(max_length=30)
    sub_award_number = models.CharField(max_length=30)
    cfda_number = models.CharField(max_length=30)
    recipient_cong_dist = models.IntegerField()
    recipient_account_number = models.CharField(max_length=30)
    final_report = models.CharField(max_length=1)
    input_type = models.CharField(max_length=4)
    input_version = models.CharField(max_length=5)
    award_type = models.CharField(max_length=10)
    award_date = models.CharField(max_length=20)
    award_description  = models.TextField()
    award_amount = models.FloatField()
    local_amount = models.FloatField()
    project_name = models.CharField(max_length=255)
    project_description  = models.TextField()
    project_status = models.CharField(max_length=255)
    job_creation  = models.TextField()
    number_of_jobs = models.FloatField()
    total_fed_arra_received = models.FloatField()
    total_fed_arra_exp = models.FloatField()
    total_infrastructure_exp = models.FloatField()
    infrastrucutre_rationale  = models.TextField()
    pop_st_address_1 = models.CharField(max_length=255)
    pop_st_address_2 = models.CharField(max_length=255)
    pop_state_cd = models.CharField(max_length=2)
    pop_country_cd = models.CharField(max_length=10)
    pop_city= models.CharField(max_length=255)
    pop_postal_cd = models.CharField(max_length=10)
    pop_cong_dist = models.CharField(max_length=4)
    prime_recipient_highcomp_rpt_app_flag = models.CharField(max_length=255)
    recipient_officer_1 = models.CharField(max_length=255)
    recipient_officer_2 = models.CharField(max_length=255)
    recipient_officer_3 = models.CharField(max_length=255)
    recipient_officer_4 = models.CharField(max_length=255)
    recipient_officer_5 = models.CharField(max_length=255)
    recipient_officer_totalcomp_1 = models.FloatField()
    recipient_officer_totalcomp_2 = models.FloatField()
    recipient_officer_totalcomp_3 = models.FloatField()
    recipient_officer_totalcomp_4 = models.FloatField()
    recipient_officer_totalcomp_5 = models.FloatField()
    total_number_small_subaward = models.FloatField()
    total_amount_small_subaward = models.FloatField()
    total_number_small_subaward_indiv = models.FloatField()
    total_amount_small_subaward_indiv = models.FloatField()
    total_number_small_subaward_vend = models.FloatField()
    total_amount_small_subaward_vend = models.FloatField()
    govt_contract_office_cd = models.CharField(max_length=2)
    govt_office_name = models.CharField(max_length=255)
    infrastructure_contact_nm = models.CharField(max_length=255)
    infrastructure_contact_email = models.CharField(max_length=255)
    infrastructure_contact_phone = models.CharField(max_length=255)
    infrastructure_contact_phone_ext = models.CharField(max_length=255)
    infrastructure_st_address_1 = models.CharField(max_length=255)
    infrastructure_st_address_2 = models.CharField(max_length=255)
    infrastructure_st_address_3 = models.CharField(max_length=255)
    infrastructure_city = models.CharField(max_length=255)
    infrastructure_state_cd = models.CharField(max_length=2)
    infrastructure_postal_cd = models.CharField(max_length=10)
    activity_code = models.CharField(max_length=20)
    project_activity_desc = models.TextField()
    activity_code_2 = models.CharField(max_length=20)
    activity_code_3 = models.CharField(max_length=20)
    activity_code_4 = models.CharField(max_length=20)
    activity_code_5 = models.CharField(max_length=20)
    activity_code_6 = models.CharField(max_length=20)
    activity_code_7 = models.CharField(max_length=20)
    activity_code_8 = models.CharField(max_length=20)
    activity_code_9 = models.CharField(max_length=20)
    activity_code_10 = models.CharField(max_length=20)
    late_submission_flag = models.CharField(max_length=2)
    late_submission_justification  = models.TextField()
    tmsp_last_updt = models.CharField(max_length=255)
    tmsp_created = models.CharField(max_length=255)
    award_date_new = models.DateField()

    def __unicode__(self):
        return self.project_name


