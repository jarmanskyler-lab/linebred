import pandas as pd, json, sys, math
sys.setrecursionlimit(300000)
SRC="/mnt/user-data/outputs/hereford_pedigree_database.xlsx"
df=pd.read_excel(SRC,sheet_name="Animals")

def s(v):
    if pd.isna(v): return None
    t=str(v).strip()
    return t if t else None
def norm(v):
    t=s(v)
    return None if t is None else " ".join(t.upper().split())

rows=[]
for _,r in df.iterrows():
    n=norm(r['Animal Name'])
    if not n: continue
    reg=s(r['Registration Number'])
    if reg and reg.endswith('.0'): reg=reg[:-2]
    rows.append(dict(
        name=n, sire=norm(r['Sire']), dam=norm(r['Dam']), regNum=reg,
        birthDate=s(r['Birth Date']), sex=s(r['Sex']),
        semen=(s(r['Frozen Semen Available']) or "").lower().startswith('y'),
        living=(s(r['Currently in Living Herd']) or "").lower().startswith('y'),
        status=s(r['Breeding Status']), notes=s(r['Notes']),
    ))
names={r['name'] for r in rows}
# dedupe: keep first
seen=set(); uniq=[]
for r in rows:
    if r['name'] in seen: continue
    seen.add(r['name']); uniq.append(r)
rows=uniq
print("animals:",len(rows))

PARENT={r['name']:( r['sire'] if r['sire'] in names else None,
                    r['dam']  if r['dam']  in names else None) for r in rows}

# break cycles (back-edges) iteratively
color={n:0 for n in PARENT}
removed=[]
for root in PARENT:
    if color[root]!=0: continue
    stack=[[root,list(PARENT[root]),0]]; color[root]=1
    while stack:
        node,kids,i=stack[-1]
        if i>=len(kids):
            color[node]=2; stack.pop()
            if stack: stack[-1][2]+=1
            continue
        p=kids[i]
        if p is None: stack[-1][2]+=1; continue
        c=color.get(p,2)
        if c==1:
            removed.append((node,'sire' if i==0 else 'dam',p))
            a,b=PARENT[node]
            PARENT[node]=(None,b) if i==0 else (a,None)
            stack[-1][2]+=1; continue
        if c==0:
            color[p]=1; stack.append([p,list(PARENT[p]),0]); continue
        stack[-1][2]+=1
print("cycle back-edges removed:",len(removed))
for t in removed: print("   ",t)

# topological depth (iterative)
depth={}
for start in PARENT:
    if start in depth: continue
    st=[start]
    while st:
        n=st[-1]
        if n in depth: st.pop(); continue
        a,b=PARENT[n]
        need=[p for p in (a,b) if p is not None and p not in depth]
        if need: st.extend(need); continue
        depth[n]=1+max(depth.get(a,0),depth.get(b,0)); st.pop()

order=sorted(PARENT, key=lambda n: depth[n])

# Meuwissen-Luo style: inbreeding via recursive kinship with memo, computed in depth order
memo={}
def kin(a,b):
    if a is None or b is None: return 0.0
    if depth[a]<depth[b]: a,b=b,a
    k=(a,b)
    v=memo.get(k)
    if v is not None: return v
    sa,da=PARENT[a]
    v=0.5*(1.0+kin(sa,da)) if a==b else 0.5*(kin(sa,b)+kin(da,b))
    memo[k]=v; return v

F={}
for n in order:
    a,b=PARENT[n]
    F[n]=kin(a,b)
print("COI computed for",len(F),"animals; memo entries",len(memo))

# blood % and occurrences to the two founders (iterative accumulation, depth-ordered)
def blood_to(target):
    val={}
    for n in order:
        if n==target: val[n]=1.0; continue
        a,b=PARENT[n]
        val[n]=0.5*(val.get(a,0.0)+val.get(b,0.0))
    return val
def occ_to(target):
    val={}
    for n in order:
        if n==target: val[n]=1; continue
        a,b=PARENT[n]
        val[n]=val.get(a,0)+val.get(b,0)
    return val

T77="MARK DONALD 77"; T43="MCK DONALD DHU 43"
b77=blood_to(T77) if T77 in PARENT else {}
b43=blood_to(T43) if T43 in PARENT else {}
o77=occ_to(T77) if T77 in PARENT else {}
o43=occ_to(T43) if T43 in PARENT else {}
print("77 in db:",T77 in PARENT," 43 in db:",T43 in PARENT)

# generations of known ancestry above each animal (subject = 0)
gens={}
for n in order:
    a,b=PARENT[n]
    ga = -1 if a is None else gens.get(a,-1)
    gb = -1 if b is None else gens.get(b,-1)
    gens[n]=0 if (a is None and b is None) else 1+max(ga,gb)

out=[]
for r in rows:
    n=r['name']
    rec={"n":n}
    # Use the cycle-broken parent map, not the raw columns. The raw columns contain
    # 11 pedigree loops (an animal that is its own ancestor); shipping those makes the
    # app's recursive COI walk run forever. The severed links are listed in
    # payload["cyclesRemoved"] so they stay traceable and can be fixed in the master.
    ps, pd_ = PARENT[n]
    if ps: rec["s"]=ps
    if pd_: rec["d"]=pd_
    if r['sire'] and not ps: rec["sRaw"]=r['sire']
    if r['dam'] and not pd_: rec["dRaw"]=r['dam']
    if r['regNum']: rec["r"]=r['regNum']
    if r['birthDate']: rec["b"]=str(r['birthDate'])[:10]
    if r['sex']: rec["x"]=r['sex']
    if r['semen']: rec["sem"]=1
    if r['living']: rec["liv"]=1
    if r['status']: rec["st"]=r['status']
    if r['notes']: rec["note"]=r['notes']
    rec["coi"]=round(100*F.get(n,0.0),4)
    rec["b77"]=round(100*b77.get(n,0.0),4)
    rec["b43"]=round(100*b43.get(n,0.0),4)
    rec["o77"]=o77.get(n,0)
    rec["o43"]=o43.get(n,0)
    rec["gen"]=gens.get(n,0)
    out.append(rec)

payload={"version":1,"generated":pd.Timestamp.utcnow().isoformat(),
         "count":len(out),"targets":[T77,T43],
         "cyclesRemoved":[{"animal":a,"field":f,"was":p} for a,f,p in removed],
         "animals":out}
with open("/home/claude/site_build/dist/data.json","w") as fh:
    json.dump(payload,fh,separators=(",",":"))
print("wrote data.json")
# sanity
for a in ["JH MARK M440 ET","MARK DONALD M694","SB DONALD 120","BB MARK DONALD 386","MCK DONALD DHU 43","MARK DONALD 77"]:
    if a in F:
        print(f"  {a:<22} COI {100*F[a]:8.4f}%  b77 {100*b77.get(a,0):7.3f}%  b43 {100*b43.get(a,0):7.3f}%  gen {gens[a]}")
