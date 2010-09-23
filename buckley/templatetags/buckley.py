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

@register.filter
def total_support_by_election_type(candidate, election_type):
    if not election_type:
        return candidate.total_supporting()
    if election_type == 'primary':
        return candidate.total_by_election_type('P', 'S')
    if election_type == 'general':
        return candidate.total_by_election_type('G', 'S')
    else:
        return candidate.total_by_election_type('O', 'S')


@register.filter
def total_opposition_by_election_type(candidate, election_type):
    if not election_type:
        return candidate.total_opposing()
    if election_type == 'primary':
        return candidate.total_by_election_type('P', 'O')
    if election_type == 'general':
        return candidate.total_by_election_type('G', 'O')
    else:
        return candidate.total_by_election_type('O', 'O')


