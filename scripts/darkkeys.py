import numpy as np, glob, sys
from PIL import Image
from scipy import ndimage as nd
KG=38.0; BLUE=np.array([8,102,255],float)
src=sorted(glob.glob('/home/claude/kf/fr*.png')); out='/home/claude/kf/out'
import os; os.makedirs(out,exist_ok=True)
for i,f in enumerate(src):
    a=np.asarray(Image.open(f).convert('RGB')).astype(float)
    # dark = invert luminance, keep hue (same as CSS invert + hue-rotate 180)
    d=255-a; mx=d.max(2,keepdims=True); mn=d.min(2,keepdims=True)
    lum=d.mean(2,keepdims=True)
    # hue-rotate 180 on an inverted image ~ swap chroma sign around luminance
    dark=np.clip(2*lum-d,0,255)
    sat=a.max(2)-a.min(2)
    strong=(a[...,2]-a[...,0]>90)&(a[...,2]-a[...,1]>60); bluish=nd.binary_dilation(strong,iterations=2)&(a[...,2]-a[...,0]>12)
    al=np.clip((255-a[...,0])/247.0,0,1)[...,None]
    H=318
    L=a[:H].mean(2)
    fillpix=(L>=244.5)&(L<=251.5)&(sat[:H]<12)
    v=L[(L>244.5)&(L<254.5)&(sat[:H]<10)]
    mode=248.0; fa=1.0
    if v.size>2000:
        h,e=np.histogram(v,bins=np.arange(244.5,255,1)); mode=float(e[np.argmax(h)]+.5); fa=float(np.clip((255-mode)/7,0,1))
    m248=np.abs(L-mode)<=1.2
    starts=[];ends=[];rows=[]
    for y in range(H):
        row=m248[y]
        if row.sum()<40: continue
        d=np.diff(np.r_[0,row.astype(int),0]); st=np.nonzero(d==1)[0]; en=np.nonzero(d==-1)[0]
        k=np.argmax(en-st)
        if en[k]-st[k]>=40: rows.append(y); starts.append(st[k]); ends.append(en[k]-1)
    W=a.shape[1]; panel=np.zeros((H,W),bool)
    if len(rows)>8:
        L_=np.array(ends)-np.array(starts); keep=L_>=0.85*np.percentile(L_,90)
        rr=np.array(rows)[keep]; y0,y1=rr.min()-3,rr.max()+9
        x0=int(np.median(np.array(starts)[keep]))-4; x1=int(np.median(np.array(ends)[keep]))
        if (x1-x0)>60 and (y1-y0)>40:
            yy,xx=np.mgrid[0:H,0:W]
            r=max(4,min(12,(x1-x0)*12/280))
            cx=np.clip(xx,x0+r,x1-r); cy=np.clip(yy,y0+r,y1-r)
            panel=(((xx-cx)**2+(yy-cy)**2)<=r*r)&(xx>=x0)&(xx<=x1)&(yy>=y0)&(yy<=y1)
    res=dark.copy(); R=res[:H]
    # remove the old clipped glow outside the panel
    R[(~panel)&(sat[:H]<25)&(L>150)&(L<253)]=0
    P=panel[...,None]
    kg=KG*fa; R[:]=np.where(P, kg+R*(1-kg/255), R)
    full=np.vstack([panel,np.zeros((a.shape[0]-H,a.shape[1]),bool)])
    bg=np.where(full[...,None],KG*fa,0.0)
    blue=bg*(1-al)+BLUE*al
    res=np.where(bluish[...,None],blue,res)
    Image.fromarray(np.clip(res,0,255).astype(np.uint8)).save(f'{out}/{os.path.basename(f)}')
print('ok')
