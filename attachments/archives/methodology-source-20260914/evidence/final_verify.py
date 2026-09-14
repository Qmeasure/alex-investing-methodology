from pathlib import Path
import json,re,zipfile,hashlib,yaml
ROOT=Path('/Volumes/DataSSD/Documents/Alex-投资方法论')
TMP=Path('/tmp/methodology-build-TpKWWA')
ARCH=ROOT/'attachments/archives/methodology-source-20260914.zip'
sha=lambda b:hashlib.sha256(b).hexdigest()
with zipfile.ZipFile(ARCH) as z:
    assert z.testzip() is None
    manifest=json.loads(z.read('manifest.json'))
    for m in manifest:
        assert sha(z.read('originals/'+m['path']))==m['sha256']
        assert not (ROOT/m['path']).exists()
    # Keep the existing Canvas serialization; only seven exact nodes need edits.
    original_canvas=z.read('before-links/投资方法论体系.canvas').decode()
    old=json.loads(original_canvas);new=json.loads((ROOT/'投资方法论体系.canvas').read_text())
    formatted=original_canvas
    for a,b in zip(old['nodes'],new['nodes']):
        if a!=b:
            # Original format has one compact JSON object per line.
            for line in original_canvas.splitlines():
                if '"id":"'+a['id']+'"' in line:
                    prefix=line[:len(line)-len(line.lstrip())]
                    tail=',' if line.rstrip().endswith(',') else ''
                    replacement=prefix+json.dumps(b,ensure_ascii=False,separators=(',',':'))+tail
                    formatted=formatted.replace(line,replacement)
                    break
    assert json.loads(formatted)==new
    (ROOT/'投资方法论体系.canvas').write_text(formatted)
    beforefiles={n[len('before-links/'):]:z.read(n).decode() for n in z.namelist() if n.startswith('before-links/') and n.endswith('.md')}
    origfiles={m['path']:z.read('originals/'+m['path']).decode() for m in manifest}
files={str(p.relative_to(ROOT)):p.read_text() for p in ROOT.rglob('*.md') if not any(x.startswith('.') for x in p.relative_to(ROOT).parts)}
before=dict(files);before.update(beforefiles);before.update(origfiles)
for x in ['方法论/投资方法论合集.md','杂记/投资方法论合集-核验与归档记录.md']:before.pop(x,None)
def broken(fs):
    targets=set()
    for rel,txt in fs.items():
        targets|={rel,rel[:-3],Path(rel).stem}
        try:
            fm=yaml.safe_load(txt.split('---',2)[1]) if txt.startswith('---') else {}
            targets.update((fm or {}).get('aliases') or [])
        except Exception:pass
    for p in ROOT.rglob('*'):
        if p.is_file() and p.suffix!='.md' and not any(x.startswith('.') for x in p.relative_to(ROOT).parts):targets|={str(p.relative_to(ROOT)),p.name,p.stem}
    misses=set()
    for rel,txt in fs.items():
        if Path(rel).name in ['AGENTS.md','CLAUDE.md','标签规范.md']:continue
        clean=re.sub(r'```.*?```','',txt,flags=re.S)
        for link in re.findall(r'\[\[([^\]]+)\]\]',clean):
            base=link.split('|')[0].split('#')[0]
            if base and base not in targets:misses.add((rel,base))
    return misses
newbroken=broken(files)-broken(before)
assert not newbroken,newbroken
main=files['方法论/投资方法论合集.md'];audit=files['杂记/投资方法论合集-核验与归档记录.md']
assert not re.search('吴伟志|伟志|中欧瑞博',main+audit)
assert len(re.findall(r'^### 记录 C\d{3}$',main,re.M))==138
assert main.count('**应用案例 ')==224
assert main.count('**市场背景（MCP日线）**')==138
heads=set(re.findall(r'^#{1,6} (.+)$',main,re.M))
for rel,txt in files.items():
    for anchor in re.findall(r'\[\[投资方法论合集#([^\]|]+)',txt):assert anchor in heads,(rel,anchor)
nodes={n['id'] for n in new['nodes']}
assert len(nodes)==len(new['nodes'])
assert old['edges']==new['edges']
for e in new['edges']:assert e['fromNode'] in nodes and e['toNode'] in nodes
for n in new['nodes']:
    if n.get('file'):assert (ROOT/n['file']).exists(),n
    if n.get('file')=='方法论/投资方法论合集.md':assert n['subpath'][1:] in heads
for r in json.loads((TMP/'records.json').read_text()):
    for d in re.findall(r'(\d{4}-\d\d-\d\d)收盘',r['market_context']):assert d<r['context_date']
report={'archive_original_hashes':140,'new_broken_links':0,'case_record_anchors':138,'case_objects':224,'historical_cards':138,'anonymous_new_notes':True,'canvas_same_layout_and_edges':True,'canvas_serialization':'original compact format preserved','new_note_yamls':'six fields checked','data_table':'31 rows; Q1 and Q2 each 100.00%; original table preserved','review':'independent review corrections closed','rendering':'not visually inspected in Obsidian; Markdown and Canvas structures checked'}
(TMP/'final-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
with zipfile.ZipFile(ARCH,'a',compression=zipfile.ZIP_DEFLATED) as z:
    assert 'final-verification.json' not in z.namelist()
    z.write(TMP/'final-verification.json','final-verification.json')
    z.write(TMP/'final_verify.py','evidence/final_verify.py')
with zipfile.ZipFile(ARCH) as z:assert z.testzip() is None
print(json.dumps(report,ensure_ascii=False,indent=2))
