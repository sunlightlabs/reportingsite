from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from outside_spending.models import *

competitive_races = [
["AZ", "H", "01", "", "Toss Up"],
["AZ", "H", "02", "Y", "Lean Democratic"],
["AZ", "H", "09", "", "Lean Democratic"],
["AZ", "S", "", "", "Toss Up"],
["CA", "H", "07", "", "Toss Up"],
["CA", "H", "09", "", "Toss Up"],
["CA", "H", "10", "Y", "Toss Up"],
["CA", "H", "24", "", "Lean Democratic"],
["CA", "H", "26", "", "Lean Democratic"],
["CA", "H", "36", "", "Toss Up"],
["CA", "H", "41", "", "Lean Democratic"],
["CA", "H", "52", "", "Toss Up"],
["CO", "H", "03", "Y", "Lean Republican"],
["CO", "H", "06", "Y", "Toss Up"],
["CO", "H", "07", "", "Lean Democratic"],
["CT", "S", "", "", "Toss Up"],
["CT", "H", "05", "", "Toss Up"],
["FL", "S", "", "", "Lean Democratic"],
["FL", "H", "02", "Y", "Lean Republican"],
["FL", "H", "10", "Y", "Lean Republican"],
["FL", "H", "18", "Y", "Toss Up"],
["FL", "H", "26", "Y", "Lean Democratic"],
["GA", "H", "12", "", "Toss Up"],
["HI", "S", "", "", "Lean Democratic"],
["IL", "H", "10", "Y", "Toss Up"],
["IL", "H", "11", "", "Lean Democratic"],
["IL", "H", "12", "", "Toss Up"],
["IL", "H", "13", "", "Toss Up"],
["IL", "H", "17", "Y", "Toss Up"],
["IN", "H", "08", "Y", "Lean Republican"],
["IN", "S", "", "", "Toss Up"],
["IA", "H", "03", "", "Lean Republican"],
["IA", "H", "04", "", "Lean Republican"],
["KY", "H", "06", "", "Toss Up"],
["MA", "H", "06", "", "Lean Republican"],
["MA", "S", "", "", "Toss Up"],
["ME", "S", "", "", "Toss Up"],
["MI", "H", "01", "Y", "Toss Up"],
["MI", "H", "11", "", "Lean Republican"],
["MN", "H", "06", "", "Lean Republican"],
["MN", "H", "08", "Y", "Toss Up"],
["MT", "S", "", "", "Toss Up"],
["NE", "S", "", "", "Lean Republican"],
["NV", "S", "", "", "Toss Up"],
["NV", "H", "03", "Y", "Lean Republican"],
["NV", "H", "04", "", "Toss Up"],
["NC", "H", "07", "", "Toss Up"],
["NH", "H", "01", "Y", "Toss Up"],
["NH", "H", "02", "", "Lean Democratic"],
["NJ", "H", "03", "Y", "Lean Republican"],
["NM", "S", "", "", "Lean Democratic"],
["NY", "H", "01", "", "Lean Democratic"],
["NY", "H", "18", "Y", "Toss Up"],
["NY", "H", "19", "Y", "Toss Up"],
["NY", "H", "21", "Y", "Lean Democratic"],
["NY", "H", "24", "Y", "Lean Democratic"],
["NY", "H", "27", "Y", "Lean Republican"],
["ND", "S", "", "", "Toss Up"],
["OH", "S", "", "", "Lean Democratic"],
["OH", "H", "06", "Y", "Toss Up"],
["OH", "H", "16", "Y", "Lean Republican"],
["PA", "S", "", "", "Lean Democratic"],
["PA", "H", "08", "Y", "Lean Republican"],
["PA", "H", "12", "", "Toss Up"],
["RI", "H", "01", "", "Toss Up"],
["TN", "H", "04", "Y", "Lean Republican"],
["TX", "H", "14", "", "Lean Republican"],
["TX", "H", "23", "Y", "Toss Up"],
["UT", "H", "04", "", "Toss Up"],
["VA", "S", "", "", "Toss Up"],
["WI", "S", "", "", "Toss Up"],
["WI", "H", "07", "Y", "Lean Republican"],
["WA", "H", "01", "", "Lean Democratic"]]


def join_fecid_values(cand_dict):
    result = []
    for i in cand_dict:
        result.append(i['fec_id'])
    return result

class Command(BaseCommand):
    help = "Sums superpac stuff"
    requires_model_validation = False


    def handle(self, *args, **options):
        
        all_ies = Expenditure.objects.filter(superceded_by_amendment=False)
        all_gen_ies = all_ies.filter(election_type='G')
        
        for race in competitive_races:
            
            state = race[0]
            office = race[1]
            district = race[2]
            rating = race[4]
                        
            print "\n\nHandling %s %s %s - rated: %s" % (state, office, district, rating)
            try:
                if office=='S':
                    this_race_aggregate = Race_Aggregate.objects.get(state=state, office=office)
                else:
                    this_race_aggregate = Race_Aggregate.objects.get(state=state, office=office, district=district)
            except Race_Aggregate.DoesNotExist:
                continue
            
            general_candidates = None
            all_candidates = None
            if office == 'S':
                print "Got senate race"
                general_candidates = Candidate_Overlay.objects.filter(office = office, state_race=state, is_general_candidate = True )
                all_candidates = Candidate_Overlay.objects.filter(office = office, state_race=state)
            else:
                general_candidates = Candidate_Overlay.objects.filter(office = office, state_race=state, district=district, is_general_candidate = True )
                all_candidates = Candidate_Overlay.objects.filter(office = office, district=district, state_race=state)
            
            general_id_list = join_fecid_values(general_candidates.values('fec_id'))
            all_id_list = join_fecid_values(all_candidates.values('fec_id'))
            
            total_ies = all_ies.filter(candidate__fec_id__in=all_id_list).aggregate(total=Sum('expenditure_amount'))['total']
            total_receipts = all_candidates.aggregate(total=Sum('cand_ttl_receipts'))['total']
            
            general_ies = all_gen_ies.filter(candidate__fec_id__in=general_id_list).aggregate(total=Sum('expenditure_amount'))['total']
            total_receipts_gen_candidates = general_candidates.aggregate(total=Sum('cand_ttl_receipts'))['total'] or 0
            

            
            pro_dem_general = all_gen_ies.filter(candidate__fec_id__in=general_id_list, candidate__party__in=('DEM', 'IND'), support_oppose='S').aggregate(total=Sum('expenditure_amount'))['total'] or 0
            anti_rep_general = all_gen_ies.filter(candidate__fec_id__in=general_id_list, candidate__party='REP', support_oppose='O').aggregate(total=Sum('expenditure_amount'))['total'] or 0
            total_pro_dem_general = pro_dem_general + anti_rep_general
            
            pro_rep_general = all_gen_ies.filter(candidate__fec_id__in=general_id_list, candidate__party='REP', support_oppose='S').aggregate(total=Sum('expenditure_amount'))['total'] or 0
            anti_dem_general = all_gen_ies.filter(candidate__fec_id__in=general_id_list, candidate__party__in=('DEM', 'IND'), support_oppose='O').aggregate(total=Sum('expenditure_amount'))['total'] or 0
            total_pro_rep_general = pro_rep_general + anti_dem_general
            
            print "Total ies %s total spent %s general ies %s total spent gen candidates (including primary): %s total_gen_pro_dem %s total_gen_pro_rep %s" % (total_ies, total_receipts, general_ies, total_receipts_gen_candidates, total_pro_dem_general, total_pro_rep_general)
            
            
            
            this_race_aggregate.total_receipts = total_receipts
            this_race_aggregate.general_ies = general_ies
            this_race_aggregate.total_receipts_gen_candidates = total_receipts_gen_candidates
            if (total_receipts and this_race_aggregate.total_ind_exp):
                this_race_aggregate.percent_outside = 100 * (this_race_aggregate.total_ind_exp / total_receipts)
            this_race_aggregate.total_pro_dem_general = total_pro_dem_general
            this_race_aggregate.total_pro_rep_general = total_pro_rep_general
            if race[4]=='Y':
                this_race_aggregate.is_freshman = True
            this_race_aggregate.cook_rating = rating
            
            this_race_aggregate.save()
            
            num_gen_candidates = len(general_id_list)
            if num_gen_candidates != 2:
                print "Not 2 candidates found!!"
                
            for can in general_candidates:
                print "Found candidate %s %s total_spent: %s" % (can.party, can, can.cand_total_disbursements)
                if can.cand_is_gen_winner and not this_race_aggregate.winner:
                    this_race_aggregate.winner = can
                    this_race_aggregate.save()
                
            