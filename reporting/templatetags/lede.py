from django import template
import re

register = template.Library()



def cleantags(value):
    BR_RE = re.compile(r'<br(.*?)>', re.I)
    P_RE = re.compile(r'</?p>', re.I)
    SPAN_RE = re.compile(r'</?span(.*?)>')
    value = BR_RE.sub('\n', value)
    value = P_RE.sub('\n', value)
    value = SPAN_RE.sub('', value)
    return value

@register.filter(name='grafs')
def grafs(post, num): 
    grafs = cleantags( post.content.strip() ).split('\n')
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
        return excerpt + readmore 
    grafs = cleantags( post.content.strip() ).split('\n') 
    newg = []
    for g in grafs:
        if g.strip():
            newg.append( g )
    lede = '<p>'+striptags(newg[0])+'</p>'
    if lede and len(newg)>1:
        lede = lede + readmore
    return lede



@register.filter(name='body')
def body(post): 
    grafs = cleantags( post.content ).split('\n') 
    newg = []
    for g in grafs:
        if g.strip():
            newg.append('<p>'+g+'</p>')
            if len(newg)==2 and post.pullquote:
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
