from django.core.management.base import BaseCommand, CommandError

from outside_spending.models import Committee, Committee_Overlay

from outside_spending.management.commands.overlay_utils import overwrite_committee_overlay


class Command(BaseCommand):
    args = '<cycle>'
    help = "Populate the committees table from the committee master file. Use a 2-digit cycle"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        committees = Committee_Overlay.objects.all()
        for committee in committees:
            overwrite_committee_overlay(committee.fec_id, 2012)
        