from django import template
import re

register = template.Library()


@register.filter(name='grafs')
def grafs(post, num): 
    grafs = post.content.strip().split('<p>') 
    newg = []
    for g in grafs:
        if g:
            new = g.replace('</p>','').replace('<p>','').strip('<br><br>').split('<br><br>')
            for n in new:
                if n.strip():
                    newg.append('<p>'+n.strip()+'</p>')
    lede = ''.join(newg[:num]) 
    if len(newg)>num:
        lede = '<p>' + lede +  ' </p><a class="readMoreFeature" href="' + post.get_absolute_url() + '">Read all about it</a>'  
    return lede


@register.filter(name='lede')
def lede(post): 
    from django.template.defaultfilters import striptags
    readmore = ' <a class="continueReading" href="' + post.get_absolute_url() + '">Read all about it</a>'  
    excerpt = striptags(post.excerpt).strip()
    if excerpt:
        return excerpt + readmore 
    grafs = post.content.strip().split('<p>') 
    newg = []
    for g in grafs:
        if g.strip():
            new = g.replace('</p>','').replace('<p>','').split('<br><br>')
            for n in new:
                if n.strip():
                    newg.append(n.strip())
    lede = striptags(newg[0])
    print newg
    if lede and len(newg)>1:
        lede = lede + readmore
    return lede



@register.filter(name='body')
def body(value): 
    grafs = value.content.strip().split('<p>') 
    newg = []
    for g in grafs:
        if g:
            new = g.replace('</p>','').replace('<p>','').split('<br><br>')
            for n in new:
                if n.strip():
                    newg.append('<p>'+n.strip()+'</p>')
                    if len(newg)==2 and value.pullquote:
                        newg.append('<div class="pullquote">'+value.pullquote+'</div>')
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
