from pathlib import Path
import json, re, hashlib, zipfile, datetime, collections, math, sys

ROOT=Path('/Volumes/DataSSD/Documents/Alex-投资方法论')
TMP=Path('/tmp/methodology-build-TpKWWA')
MAIN='投资方法论合集'
AUDIT=MAIN+'-核验与归档记录'
ARCHIVE=ROOT/'attachments/archives/methodology-source-20260914.zip'
records=sum([json.loads((TMP/f'extract-{s}.json').read_text()) for s in ['early','middle','recent']],[])
records.sort(key=lambda x:(x['date'],x['file']))
originals=sorted((ROOT/'方法论').glob('伟志思考-*.md'))
assert len(originals)==140
articles={p.name:p for p in originals if not p.stem.endswith('索引')}
assert len(records)==138 and len({r['file'] for r in records})==138
assert set(articles)=={r['file'] for r in records}
texts={p.name:p.read_text() for p in originals}
sha=lambda b:hashlib.sha256(b).hexdigest()
anonym=lambda s:re.sub('吴伟志|伟志思考|中欧瑞博|伟志|瑞博','案例记录',s)
data={}
checks={}
for name in ['sse','sse50','chinext']:
    raw=json.loads((TMP/f'{name}.json').read_text()); rows=raw['rows']
    for r in rows:
        r['day']=datetime.datetime.fromtimestamp(r['timestamp']/1000,datetime.timezone(datetime.timedelta(hours=8))).date().isoformat()
        assert all(math.isfinite(r[k]) and r[k]>0 for k in ['open','close','high','low'])
        assert r['low']<=min(r['open'],r['close'])<=max(r['open'],r['close'])<=r['high']
    assert len({r['day'] for r in rows})==len(rows)
    rows.sort(key=lambda r:r['day']); data[name]=rows
    checks[name]={'rows':len(rows),'first':rows[0]['day'],'last':rows[-1]['day'],'duplicates':0,'invalid_ohlc':0}
def close(name,day): return next(r['close'] for r in data[name] if r['day']==day)
def pct(a,b): return (b/a-1)*100
def context(day):
    result=[]
    for name,label in [('sse','上证指数'),('sse50','上证50'),('chinext','创业板指')]:
        rows=[r for r in data[name] if r['day']<day]
        assert len(rows)>21
        r=rows[-1]; ret=pct(rows[-22]['close'],r['close'])
        result.append(f'{label} {r["close"]:.2f}点（{r["day"]}收盘，较21个交易日前{ret:+.2f}%）')
    return '；'.join(result)+'。'

# Primary grouping uses methodological subject, never source publication order.
groups=[('估值与商业质量','估值|回报|成长|商业|公司优先|增长|微观|长期持有|供应链'),
        ('政策、债务与信用传导','政策|利率|信用|债务|资产负债|宏观|事件'),
        ('周期阶段与预期差','周期|底部|预期|逆向|情绪|第二层|催化剂|牛市'),
        ('供需、拥挤与市场结构','供需|资金供|拥挤|基金流|被动|质押|分部|结构|景气|AI'),
        ('仓位、杠杆与退出纪律','仓位|杠杆|风险|危机|交易纪律|资本配置|永久|一次性|资金边界'),
        ('策略适配与组合管理','策略|风格|组合|投资体系|四维|确定|多变量'),
        ('心理、预测与证据质量','.*')]
for n,r in enumerate(records,1):
    r['id']=f'C{n:03d}'
    r['group']=next(g for g,pat in groups if re.search(pat,r['themes'][0]))
    signatures=[]
    for line in texts[r['file']].split('## 相关')[0].splitlines():
        if len(line)>70 or line.startswith('date:') or '日期' in line: continue
        if not re.match(r'^(?:>\s*——|#{2,6}\s*|吴伟志|20\d{2}年)',line.strip()): continue
        m=re.search(r'(20\d{2})[年/.-](\d{1,2})[月/.-](\d{1,2})',line)
        if m: signatures.append(datetime.date(*map(int,m.groups())).isoformat())
    signatures=sorted(set(signatures))
    assert len(signatures)<=1,(r['file'],signatures)
    r['written_date']=signatures[0] if signatures else None
    r['context_date']=min(r['date'],r['written_date']) if r['written_date'] else r['date']
    r['market_context']=context(r['context_date'])
byfile={r['file']:r for r in records}
kept={p.stem:p for p in (ROOT/'方法论').glob('*.md') if p not in originals}
directory=['| 方法主题 | 案例覆盖 |','| --- | --- |']
cards=[]
for group,_ in groups:
    rows=[r for r in records if r['group']==group]
    directory.append(f'| [[#{group}]] | '+ ' · '.join(f'[[#记录 {r["id"]}|{r["id"]}]]' for r in rows)+' |')
    cards.append(f'## {group}\n')
    for r in rows:
        dates=f'历史材料索引日期：{r["date"]}。'+(f'原落款日期：{r["written_date"]}；行情背景按两者较早日期之前选取，不把发布日期当决策日。' if r['written_date'] else '未见可单独确认的落款日，以索引日前行情作阅读背景，不视作精确决策日。')
        s=[f'### 记录 {r["id"]}',f'**方法问题：{anonym(" / ".join(r["themes"]))}**',dates,'**可复用规则**','\n'.join('- '+anonym(v) for v in r['principles'])]
        for i,c in enumerate(r['cases'],1):
            s.extend([f'**应用案例 {i}**',anonym(c['event']), '判断逻辑：'+anonym(c['reasoning']), '证据边界：'+anonym(c['limitation'])])
        if r.get('forecast'): s.append('**当时预测（不是现在的结论）**：'+anonym(r['forecast']))
        s.append('**市场背景（MCP日线）**：'+r['market_context'])
        s.append('口径：上述背景基准日前最近交易日；21个交易日变化仅作趋势背景，不等于自然月回报，不证明上述个股、操作或因果关系。落款日与索引日明显矛盾时，保留疑点，不自行断定哪一个是正确发表日。')
        corrections={
          '2016-05-03':'已完成算术核对：PE从11降至9倍下降18.18%，不是22%；EPS增长35%时股价回报为1.35×9/11−1=10.45%。历史个股价格表仍未核实复权口径。',
          '2017-07-31':'已完成算术核对：4037降至1641按原文取整输入计算为下降59.35%，不是69%。',
          '2020-01-02':'已核实：2019年美联储分别在7月31日、9月18日、10月30日降息，共三次，原稿“两次”有误。[7月决定](https://www.federalreserve.gov/newsevents/pressreleases/monetary20190731a.htm)、[9月决定](https://www.federalreserve.gov/monetarypolicy/files/monetary20190918a1.pdf)、[10月纪要](https://www.federalreserve.gov/monetarypolicy/fomcminutes20191030.htm)。',
          '2022-12-05':'已核实：中国成为WTO正式成员的日期为2001-12-11，原稿1999年说法不能沿用。[^wto]',
          '2023-01-03':'已核实：中国正式加入WTO为2001-12-11，不是2000年。[^wto]',
          '2023-06-05':'已核实：美联储创建于1913-12-23，因此1929年不存在美联储的说法错误。[^fed-history]'}
        if r['date'] in corrections: s.append('**本次核验修正**：'+corrections[r['date']])
        if r['date']=='2026-08-03':
            table='\n'.join(line for line in texts[r['file']].splitlines() if line.startswith('|'))
            assert len(table.splitlines())==33
            s.extend(['**配置图的完整结构化数据（31个行业）**','以下为原图转录，不是独立重建的基金持仓数据库。原图“持仓环比变动”列声称剔除股价影响，不能与两季度原始权重之差混用；本次没有取得该调整算法和基金样本，保留表头并标明未独立验证。',table,'表内没有各期时间戳的走势小图无法准确恢复逐期数据，不推造曲线。食品饮料平均配比11.00%的表头基期是2012年以来；正文另称2021年以来，两者冲突，以表头转录而不声称已核实统计口径。'])
        related=[]
        body=texts[r['file']].split('## 相关')[-1]
        for link in re.findall(r'\[\[([^\]]+)\]\]',body):
            target=link.split('|')[0].split('#')[0]
            if target in kept and target not in related: related.append(target)
        # Preserve reciprocal relationships only when the retained note really links back.
        related=[x for x in related if r['file'][:-3] in kept[x].read_text() and not re.search('吴伟志|伟志|中欧瑞博',x)]
        if related: s.append('相关互补材料：'+' · '.join(f'[[{x}]]' for x in related[:5])+'（沿用原稿已有的双向案例关系）。')
        cards.append('\n\n'.join(s)+'\n')

main=(TMP/'main.md').read_text()
values={'sse50_2021_drop':-pct(close('sse50','2021-02-10'),close('sse50','2021-03-15')),
        'sse_2014_rally':pct(close('sse','2014-11-21'),close('sse','2014-12-31')),
        'sse_2018_low':pct(close('sse','2018-11-02'),2440.91),
        'sse_2015_close_drop':-pct(close('sse','2015-06-12'),close('sse','2015-06-26')),
        'chinext_2022_spring':-pct(close('chinext','2022-03-16'),close('chinext','2022-04-27'))}
for k,v in values.items(): main=main.replace('{{'+k+'}}',f'{v:.2f}')
main=main.replace('{{CASE_DIRECTORY}}','\n'.join(directory)).replace('{{CASE_CARDS}}','\n'.join(cards))
main=main.replace('以下逐篇案例是上述主题的证据目录。','以下案例按方法主题归组，是上述主题的证据目录。')
main=main.replace('每条历史记录的行情卡取索引日期之前最近一个交易日，作为阅读背景，不将发布日期等同于实际决策日。','有可考落款日的行情卡取落款日与索引日较早者之前最近一个交易日；未见落款日才用索引日前行情作阅读背景，不将发布日期等同于实际决策日。')
main=main.replace('原文称2019降息两次待核，通常记录为三次；管理业绩仅自述。','原文称2019降息两次有误，本次官方核验为三次，具体决定链接见本条修正；管理业绩仍仅为自述。')
main=main.replace('## 历史案例与时点数据','## 案例的阅读口径\n\n以下七组案例按方法排列，保留历史日期和证据边界，不保留原日记标题、署名及逐月编排。')
assert '{{' not in main
assert not re.search('吴伟志|伟志|中欧瑞博',main)
(TMP/'final-main.md').write_text(main)
(TMP/'records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
(TMP/'data-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))

# Migration manifest includes exact provenance only inside the recoverable archive.
manifest=[]
for p in originals:
    r=byfile.get(p.name)
    manifest.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'bytes':len(p.read_bytes()),
      'record':r['id'] if r else 'index','date':r['date'] if r else '',
      'destination':'方法论/'+MAIN+'.md'+('#记录 '+r['id'] if r else ''),
      'source_urls':re.findall(r'https?://[^\s)\]>]+',p.read_text())})
(TMP/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps({'articles':len(records),'cases':sum(len(r['cases']) for r in records),'principles':sum(len(r['principles']) for r in records),'characters':len(main),'groups':collections.Counter(r['group'] for r in records),'market_checks':checks,'calculations':values},ensure_ascii=False,indent=2))
