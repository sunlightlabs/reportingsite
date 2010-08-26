from django.conf.urls.defaults import *

from ie.feeds import CommitteeFeed

urlpatterns = patterns('',

#    url(r'^candidate/(?P<candidate_slug>[-\w]+)/(?P<committee_slug>[-\w]+)',
#        'ie.views.expenditures_by_committee_for_candidate',
#        name='ie_expenditures_by_committee_for_candidate'
#        ),
#
#    url(r'^candidate/(?P<candidate_slug>[-\w]+)',
#        'ie.views.candidate_detail',
#        name='ie_candidate_detail'
#        ),
#
#    url(r'^candidate',
#        'ie.views.candidate_list',
#        name='ie_candidate_list',
#        ),
#
#    url(r'^committee/(?P<committee_slug>[-\w]+)',
#        'ie.views.committee_detail',
#        name='ie_committee_detail'
#        ),
#
#    url(r'^committee',
#        'ie.views.committee_list',
#        name='ie_committee_list'
#        ),
#
#    url(r'^committee',
#        'ie.views.committee_list',
#        name='ie_committee_list'
#        ),
#
#    url(r'^payee/(?P<payee_slug>[-\w]+)',
#        'ie.views.payee_detail',
#        name='ie_payee_detail'
#        ),
#
#    url(r'^payee',
#        'ie.views.payee_list',
#        name='ie_payee_list'
#        ),

    url(r'^feed/csv', 
        'ie.views.new_committees_csv',
        name='ie_new_committees_csv'
        ),

    url(r'^feed',
        CommitteeFeed(),
        name='ie_new_committee_feed'
        ),


#    url(r'^',
#        'ie.views.index',
#        name='ie_index'
#        ),

    )
