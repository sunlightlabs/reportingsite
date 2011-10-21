from django.core.management.base import NoArgsCommand, BaseCommand, CommandError

from buckley.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        dupes = {}
        for expenditure in Expenditure.objects.filter(payee__name__icontains='Mentzer Media Services'):
            e = Expenditure.objects.filter(candidate=expenditure.candidate,
                                           committee=expenditure.committee,
                                           expenditure_date=expenditure.expenditure_date,
                                           expenditure_amount=expenditure.expenditure_amount).exclude(filing_number=expenditure.filing_number)
            if e:
                d = []
                for i in e:
                    if round(i.expenditure_amount) == round(expenditure.expenditure_amount):
                        d.append(i)
                if d:
                    dupes[expenditure] = d

        for k, v in dupes.items():
            if Expenditure.objects.filter(pk=k.pk):
                for expenditure in v:
                    expenditure.delete()
