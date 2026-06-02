import re, sys
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
from collections import OrderedDict

ics = sys.argv[1] if len(sys.argv)>1 else '/tmp/pc_cal.ics'
out = sys.argv[2] if len(sys.argv)>2 else 'calendar.png'
raw = open(ics, encoding='utf-8').read().replace('\r\n','\n')
raw = re.sub(r'\n[ \t]', '', raw)
events=[]; cur=None
for line in raw.split('\n'):
    if line=='BEGIN:VEVENT': cur={}
    elif line=='END:VEVENT':
        if cur: events.append(cur); cur=None
    elif cur is not None:
        k,_,v=line.partition(':'); kk=k.split(';')[0]
        if kk=='SUMMARY': cur['s']=v
        elif kk=='DTSTART': cur['start']=v
        elif kk=='DTEND': cur['end']=v
def to_cr(dt):
    m=re.match(r'(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z?',dt)
    if not m:
        m2=re.match(r'(\d{4})(\d{2})(\d{2})',dt); y,mo,d=[int(x) for x in m2.groups()]; return datetime(y,mo,d)
    y,mo,d,h,mi,s=[int(x) for x in m.groups()]
    return datetime(y,mo,d,h,mi)-timedelta(hours=6)
evs=sorted([(to_cr(e['start']), to_cr(e['end']), e.get('s','event')) for e in events], key=lambda x:x[0])
weeks=OrderedDict()
for st,en,s in evs: weeks.setdefault(st.isocalendar()[1],[]).append((st,en,s))

def font(sz,bold=False):
    paths=(['/System/Library/Fonts/Supplemental/Arial Bold.ttf'] if bold else ['/System/Library/Fonts/Supplemental/Arial.ttf'])+['/System/Library/Fonts/Helvetica.ttc']
    for p in paths:
        try: return ImageFont.truetype(p,sz)
        except: pass
    return ImageFont.load_default()

W=1480; H=240+len(weeks)*300
img=Image.new('RGB',(W,H),'#ffffff'); d=ImageDraw.Draw(img)
ORANGE='#F09433'; DARK='#222'; GRAY='#8a8a8a'; CREAM='#fff3e3'
d.text((60,46),'Producer Camp — Schedule',font=font(54,True),fill=DARK)
d.text((62,116),'Auto-generated from the shared Google Calendar · times in Costa Rica (GMT-6)',font=font(22),fill=GRAY)
d.text((62,150),'Updated '+datetime.now().strftime('%b %-d, %Y'),font=font(18),fill=GRAY)
DOW=['MON','TUE','WED','THU','FRI','SAT','SUN']
y=205
for i,(wk,items) in enumerate(weeks.items(),1):
    d0=items[0][0]; d1=items[-1][0]
    d.text((60,y),f'Week {i} · {d0.strftime("%b %-d")}–{d1.strftime("%-d, %Y")}',font=font(30,True),fill=DARK)
    y+=52; x=60; cw=262; gap=18
    for j,(st,en,s) in enumerate(items,1):
        d.rounded_rectangle([x,y,x+cw,y+178],radius=16,fill=ORANGE)
        d.text((x+18,y+16),DOW[st.weekday()],font=font(22,True),fill=CREAM)
        d.text((x+16,y+40),st.strftime('%-d'),font=font(46,True),fill='#ffffff')
        d.text((x+18,y+106),f'Day {j}',font=font(28,True),fill='#ffffff')
        t=f'{st.strftime("%-I:%M")}–{en.strftime("%-I:%M %p").lower()}'
        d.text((x+18,y+142),t,font=font(20),fill=CREAM)
        x+=cw+gap
    y+=232
img.save(out)
print('rendered', img.size, '->', out)
