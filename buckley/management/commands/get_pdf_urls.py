import socket
import time

from django.core.management.base import NoArgsCommand

from buckley.models import Expenditure


socket.setdefaulttimeout(60)


class Command(NoArgsCommand):
    help = "Look for PDF URLs of expenditures"
    requires_model_validation = False

    def handle_noargs(self, **options):
        image_numbers = Expenditure.objects.order_by('-image_number').filter(pdf_url='').values_list('image_number', flat=True).distinct()

        for image_number in image_numbers:
            expenditures = Expenditure.objects.filter(image_number=image_number)
            try:
                pdf_url = expenditures[0].get_pdf_url()
            except urllib2.URLError:
                continue

            if pdf_url:
                print pdf_url
                expenditures.update(pdf_url=pdf_url)

            time.sleep(.25)
