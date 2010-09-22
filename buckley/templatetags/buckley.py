from django import template

register = template.Library()


@register.filter
def committee_candidate_money(committee, candidate):
    return committee.money_spent_on_candidate(candidate)

@register.filter
def committee_candidate_support_money(committee, candidate):
    return committee.money_spent_on_candidate(candidate, 'S')

@register.filter
def committee_candidate_oppose_money(committee, candidate):
    return committee.money_spent_on_candidate(candidate, 'O')

@register.filter
def absolute_value(n):
    try:
        n = int(n)
    except ValueError:
        return n
    if n < 0:
        return str(n * -1)
    return n
