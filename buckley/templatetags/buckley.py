from django import template

register = template.Library()


@register.filter
def committee_candidate_money(committee, candidate):
    return committee.money_spent_on_candidate(candidate)
