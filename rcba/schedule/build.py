import json
d=open('data.json').read();e=open('engine.js').read();u=open('ui.html').read()
u=u.replace('/*DATA*/',d).replace('/*ENGINE*/',e)
open('page.html','w').write(u);print(len(u))
