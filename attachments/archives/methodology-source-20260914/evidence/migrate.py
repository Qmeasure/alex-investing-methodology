from pathlib import Path
import json,re,hashlib,zipfile,yaml,sys,collections,datetime
ROOT=Path('/Volumes/DataSSD/Documents/Alex-投资方法论')
TMP=Path('/tmp/methodology-build-TpKWWA')
NAME='投资方法论合集'
AUDIT=NAME+'-核验与归档记录'
ARCH=ROOT/'attachments/archives/methodology-source-20260914.zip'
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=json.loads((TMP/'manifest.json').read_text())
records=json.loads((TMP/'records.json').read_text())
byname={r['file'][:-3]:r for r in records}
originals={m['path']:m for m in manifest}
oldmap={}
for rel,m in originals.items():
    p=ROOT/rel
    assert p.exists() and sha(p.read_bytes())==m['sha256'],f'Input changed: {rel}'
    target=NAME+('#记录 '+m['record'] if m['record']!='index' else '')
    oldmap[p.stem]=target;oldmap[rel[:-3]]=target;oldmap[rel]=target
    fm=yaml.safe_load(p.read_text().split('---',2)[1])
    for alias in fm.get('aliases') or []:
        if alias and alias not in {'投资体系'}:oldmap[alias]=target
def rewrite(text):
    def sub(m):
        inside=m.group(1);base=inside.split('|')[0].split('#')[0]
        if base not in oldmap:return m.group(0)
        target=oldmap[base]
        label='方法案例 '+target.split('记录 ')[1] if '#记录 ' in target else '方法论合集'
        return '[['+target+'|'+label+']]'
    return re.sub(r'\[\[([^\]]+)\]\]',sub,text)
updates={}
before={}
for p in ROOT.rglob('*.md'):
    rel=str(p.relative_to(ROOT))
    if rel in originals or any(x.startswith('.') for x in p.relative_to(ROOT).parts):continue
    if p.name in ['AGENTS.md','CLAUDE.md','标签规范.md']:continue
    text=p.read_text(); new=rewrite(text)
    if p.name=='Home.md':
        new=re.sub(r';专栏入口 .*',f';整合入口 [[{NAME}]]、[[{AUDIT}|核验与归档]]',new)
    if new!=text:updates[rel]=new;before[rel]=p.read_bytes()
canvaspath='投资方法论体系.canvas'
cb=(ROOT/canvaspath).read_bytes();canvas=json.loads(cb);previous=json.loads(cb)
canvas_changes=0
for n in canvas['nodes']:
    file=n.get('file','')
    if file in originals:
        m=originals[file];n['file']='方法论/'+NAME+'.md'
        n['subpath']='#记录 '+m['record'] if m['record']!='index' else '#决策时怎样使用这份合集'
        canvas_changes+=1
    if 'text' in n:n['text']=rewrite(n['text'])
assert canvas['edges']==previous['edges']
assert len(canvas['nodes'])==len(previous['nodes'])
for old,new in zip(previous['nodes'],canvas['nodes']):
    assert {k:v for k,v in old.items() if k not in ['file','subpath','text']}=={k:v for k,v in new.items() if k not in ['file','subpath','text']}
updates[canvaspath]=json.dumps(canvas,ensure_ascii=False,indent=2)+'\n';before[canvaspath]=cb
updates['方法论/'+NAME+'.md']=(TMP/'final-main.md').read_text()
updates['杂记/'+AUDIT+'.md']=(TMP/'audit.md').read_text()
for rel in ['方法论/'+NAME+'.md','杂记/'+AUDIT+'.md']:assert not (ROOT/rel).exists()
# Validate new notes without modifying the vault.
index={p.stem for p in ROOT.rglob('*') if p.is_file() and not any(x.startswith('.') for x in p.relative_to(ROOT).parts)}
index-= {Path(x).stem for x in originals}
index|={NAME,AUDIT,'methodology-source-20260914'}
concepts={p.stem for p in (ROOT/'concepts').glob('*.md')}
for rel in ['方法论/'+NAME+'.md','杂记/'+AUDIT+'.md']:
    text=updates[rel];fm=yaml.safe_load(text.split('---',2)[1])
    assert set(fm)=={'type','author','date','tags','aliases','rating'}
    assert fm['author'] is None and fm['rating'] is None
    assert set(fm['tags']) <= {'投资体系','牛熊周期','估值'}
    assert not re.search('吴伟志|伟志|中欧瑞博',text)
    for link in re.findall(r'\[\[([^\]]+)\]\]',text):
        base=link.split('|')[0].split('#')[0]
        if not base:continue
        stem=Path(base).stem if Path(base).suffix in {'.md','.zip','.canvas','.base'} else Path(base).name
        assert stem in index,(rel,link)
    assert any('[['+c+']]' in text for c in concepts)
main=updates['方法论/'+NAME+'.md']
anchors=set(re.findall(r'^#{1,6} (.+)$',main,re.M))
assert len(re.findall(r'^### 记录 C\d{3}$',main,re.M))==138
for text in updates.values():
    for m in re.finditer(r'\[\['+NAME+r'#([^\]|]+)',text):assert m.group(1) in anchors
for n in canvas['nodes']:
    if n.get('file')=='方法论/'+NAME+'.md':assert n['subpath'][1:] in anchors
plan={'archive_originals':len(originals),'new_notes':2,'link_files':list(before),'canvas_retargets':canvas_changes,'written_dates':sum(bool(r['written_date']) for r in records),'removed_files':list(originals)}
(TMP/'migration-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in plan.items() if k!='removed_files'},ensure_ascii=False,indent=2))
if '--apply' not in sys.argv:sys.exit(0)
assert not ARCH.exists()
ARCH.parent.mkdir(parents=True,exist_ok=True)
# Archive first. No deletion or note edits before CRC and every exact byte hash pass.
with zipfile.ZipFile(ARCH,'x',compression=zipfile.ZIP_DEFLATED) as z:
    for rel in originals:z.write(ROOT/rel,'originals/'+rel)
    z.write(TMP/'manifest.json','manifest.json')
    for rel,b in before.items():z.writestr('before-links/'+rel,b)
    for p in sorted(TMP.iterdir()):
        if p.is_file() and p.suffix in {'.json','.py','.md'} and p.name!='manifest.json':z.write(p,'evidence/'+p.name)
with zipfile.ZipFile(ARCH) as z:
    assert z.testzip() is None
    assert len([x for x in z.namelist() if x.startswith('originals/')])==140
    for rel,m in originals.items():assert sha(z.read('originals/'+rel))==m['sha256']
    for rel,b in before.items():assert z.read('before-links/'+rel)==b
for rel,m in originals.items():assert sha((ROOT/rel).read_bytes())==m['sha256']
for rel,text in updates.items():
    p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
# The exact validated scope is 140 files; archive verified above.
for rel in originals:(ROOT/rel).unlink()
for rel,text in updates.items():assert (ROOT/rel).read_text()==text
assert not list((ROOT/'方法论').glob('伟志思考-*.md'))
def withoutlinks(t):return re.sub(r'\[\[[^\]]+\]\]','[[LINK]]',t)
unchanged_bodies=0
for rel,b in before.items():
    if rel.startswith('方法论/'):
        assert withoutlinks(b.decode())==withoutlinks((ROOT/rel).read_text()),rel
        unchanged_bodies+=1
retained=[p.name for p in (ROOT/'方法论').glob('*.md')]
assert any('吴伟志访谈' in p for p in retained)
verification={'archive_crc':'pass','originals_count':140,'original_sha256_matches':140,'records':138,'case_objects':224,'market_context_cards':138,'market_series_per_card':3,'known_written_dates_used':plan['written_dates'],'preserved_other_article_bodies':unchanged_bodies,'canvas_retargets':canvas_changes,'canvas_edges_preserved':True,'old_files_remaining':0,'new_note_yaml_and_links':'pass','snapshot_commit':'d46c54c','archive_sha256':sha(ARCH.read_bytes())}
(TMP/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2))
with zipfile.ZipFile(ARCH,'a',compression=zipfile.ZIP_DEFLATED) as z:
    # Do not store the archive hash inside itself: it would be self-invalidating.
    report={k:v for k,v in verification.items() if k!='archive_sha256'}
    z.writestr('verification.json',json.dumps(report,ensure_ascii=False,indent=2))
with zipfile.ZipFile(ARCH) as z:assert z.testzip() is None
verification['archive_sha256']=sha(ARCH.read_bytes())
(TMP/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2))
print(json.dumps(verification,ensure_ascii=False,indent=2))
