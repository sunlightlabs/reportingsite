from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse

from buckley.models import *


class SimpleTest(TestCase):

    fixtures = ['buckley.json', ]
    urls = 'buckley.urls'

    def setUp(self):
        self.client = Client()

    def test_homepage(self):
        response = self.client.get(reverse('buckley_index'))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['object_list'][0]._meta.module_name, 'expenditure')

    def test_committee_list(self):
        response = self.client.get(reverse('buckley_committee_list'))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['object_list'][0]._meta.module_name, 'committee')

    def test_candidate_list(self):
        response = self.client.get(reverse('buckley_candidate_list'))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['object_list'][0]._meta.module_name, 'candidate')

    def test_payee_list(self):
        response = self.client.get(reverse('buckley_payee_list'))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['object_list'][0]._meta.module_name, 'payee')

    def test_payee_detail(self):
        payee_slugs = Payee.objects.values_list('slug', flat=True).distinct()
        for slug in payee_slugs:
            response = self.client.get(reverse('buckley_payee_detail', kwargs={'slug': slug}))
            self.failUnlessEqual(response.status_code, 200)
            self.failUnlessEqual(response.context['object'].slug, slug)
            self.failUnlessEqual(response.context['object']._meta.module_name, 'payee')

    def test_candidate_detail(self):
        candidate_slugs = Candidate.objects.values_list('slug', flat=True).distinct()
        for slug in candidate_slugs:
            response = self.client.get(reverse('buckley_candidate_detail', kwargs={'slug': slug}))
            self.failUnlessEqual(response.status_code, 200)
            self.failUnlessEqual(response.context['object'].slug, slug)
            self.failUnlessEqual(response.context['object']._meta.module_name, 'candidate')

    def test_committee_detail(self):
        committee_slugs = Committee.objects.values_list('slug', flat=True).distinct()
        for slug in committee_slugs:
            response = self.client.get(reverse('buckley_committee_detail', kwargs={'slug': slug}))
            self.failUnlessEqual(response.status_code, 200)
            self.failUnlessEqual(response.context['object'].slug, slug)
            self.failUnlessEqual(response.context['object']._meta.module_name, 'committee')

    def test_expenditure_detail(self):
        expenditures = Expenditure.objects.all()
        for expenditure in expenditures:
            committee_slug = expenditure.committee.slug
            response = self.client.get(reverse('buckley_expenditure_detail', 
                                               kwargs={'committee_slug': committee_slug,
                                                       'object_id': str(expenditure.id), }
                                                )
                                            )
            self.failUnlessEqual(response.status_code, 200)
            self.failUnlessEqual(response.context['object'].committee.slug, committee_slug)
            self.failUnlessEqual(response.context['object']._meta.module_name, 'expenditure')

    def test_candidate_committee_detail(self):
        expenditures = Expenditure.objects.exclude(candidate__slug='no-candidate-listed'
                ).values_list('committee__slug', 'candidate__slug').order_by('?')[:100]
        for committee_slug, candidate_slug in expenditures:
            response = self.client.get(reverse('buckley_committee_candidate_detail',
                                               kwargs={'committee_slug': committee_slug,
                                                       'candidate_slug': candidate_slug, }
                                                )
                                            )
            self.failUnlessEqual(response.status_code, 200)
            self.failUnlessEqual(response.context['committee'].slug, committee_slug)
            self.failUnlessEqual(response.context['candidate'].slug, candidate_slug)
