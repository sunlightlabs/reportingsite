from django import template
import re

register = template.Library()


@register.filter(name='cleantags')
def cleantags(value): #split on newline
    BR_RE = re.compile(r'<br(.*?)>', re.I)
    P_RE = re.compile(r'</?p>', re.I)
    SPAN_RE = re.compile(r'</?span(.*?)>')
    value = BR_RE.sub('\n', value)
    value = P_RE.sub('\n', value)
    value = SPAN_RE.sub('', value)
    return value

@register.filter(name='fixtags')
def fixtags(value): #split on p tag
    BR_RE = re.compile(r'<br(.*?)>', re.I)
    P_RE = re.compile(r'</?p>', re.I)
    SPAN_RE = re.compile(r'</?span(.*?)>')
    value = BR_RE.sub('<p>', value)
    value = P_RE.sub('<p>', value)
    value = SPAN_RE.sub('<p>', value)
    return value

@register.filter(name='grafs')
def grafs(post, num): 
    grafs = fixtags( post.content.strip() ).split('<p>')
    newg = []
    for g in grafs:
        if g.strip():
            newg.append('<p>'+g+'</p>')
    lede = ''.join(newg[:num]) 
    if len(newg)>num:
        lede = lede + '<a class="readMoreFeature" href="' + post.get_absolute_url() + '">Read all about it</a>'  
    return lede


@register.filter(name='lede')
def lede(post): 
    from django.template.defaultfilters import striptags
    readmore = ' <a class="continueReading" href="' + post.get_absolute_url() + '">Read all about it</a>'  
    excerpt = striptags(post.excerpt)
    if excerpt:
        return '<p>'+excerpt+'</p>' + readmore 
    grafs = fixtags( post.content.strip() ).split('<p>') 
    newg = []
    for g in grafs:
        if g.strip():
            newg.append( g )
    lede = ''
    if len(newg)>0:
        lede = '<p>'+striptags(newg[0])+'</p>'
    if lede and len(newg)>1:
        lede = lede + readmore
    return lede



@register.filter(name='body')
def body(post): 
    grafs = fixtags( post.content ).split('<p>') 
    newg = []
    for g in grafs:
        if g.strip():
            newg.append('<p>'+g+'</p>')
            if len(newg)==4 and post.pullquote:
                newg.append('<div class="pullquote">'+post.pullquote+'</div>')
    lede = ''.join(newg) 
    return lede


@register.filter(name='sentence')
def sentence(value): 
    sens = re.split('[.?!] ', value)
    s = sens[0]
    i=1
    while len(sens)>i and len(s+sens[i])<300:
        s = s+'. '+sens[i]
        i = i+1
    return s+'.'



@register.filter(name='feedclean')
def feedclean(st): 
    return st.encode('UTF-8').replace("&amp;",'').replace('&#','')


@register.filter(name='twitter_link')
def twitter_link(s): 
    r1 = r"(\b(http|https)://([-A-Za-z0-9+&@#/%?=~_()|!:,.;]*[-A-Za-z0-9+&@#/%=~_()|]))"
    r2 = r"((^|\b)www\.([-A-Za-z0-9+&@#/%?=~_()|!:,.;]*[-A-Za-z0-9+&@#/%=~_()|]))"
    return re.sub(r2,r'<a rel="nofollow" target="_blank" href="http://\1">\1</a>',re.sub(r1,r'<a target="_blank" href="\1">\1</a>',s))


