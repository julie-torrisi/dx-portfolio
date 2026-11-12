import sys,re
p=sys.argv[1]; s=open(p,encoding='utf-8').read()
start=s.index('<section data-pass class="slide title-open"')
end=s.index('</section>',start)+len('</section>')
blk=s[start:end]
assert 'Experiences, systems, AI across global platforms' in blk and s.count('class="slide title-open"')==1
open('archive/title-open-cut-2026-11-12.html','w',encoding='utf-8').write(blk+'\n')
s=s[:start]+s[end:].lstrip('\n')
open(p,'w',encoding='utf-8').write(s)
