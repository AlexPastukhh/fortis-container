#!/usr/bin/env python3
"""Check unique registered goals, required sections and local Markdown targets."""
from pathlib import Path
import argparse
import re

ROOT=Path(__file__).resolve().parents[1]
CASES=ROOT/'docs/use-cases'
registry=(CASES/'README.md').read_text()
registered=re.findall(r'^\| (UC-CONT-\d{3}) \|',registry,re.M)
assert registered and len(registered)==len(set(registered)), 'duplicate registry IDs'
found=[]
for p in sorted(CASES.glob('*.md')):
    text=p.read_text()
    parts=re.split(r'^## (UC-CONT-\d{3})\s*$',text,flags=re.M)
    for n in range(1,len(parts),2):
        found.append(parts[n]);section=parts[n+1]
        for label in ('**Цель:**','**Как:**','**Готово:**'):
            assert label in section,(p.name,parts[n],label)
    for dest in re.findall(r'\]\(([^)]+)\)',text):
        if '://' in dest or dest.startswith('/'):continue
        path,_,anchor=dest.partition('#');target=p.parent/path if path else p
        assert target.is_file(),(p.name,dest)
        if anchor.startswith('uc-cont-'):
            assert (('## '+anchor.upper()) in target.read_text() or ('id="'+anchor+'"') in target.read_text()),(p.name,dest)
assert sorted(found)==sorted(registered), 'missing or duplicate case descriptions'

# Entrypoints must make both shared workflows mandatory. Reading the registry
# titles is sufficient; the rest of the detailed cases remain goal-dependent.
for entrypoint in (ROOT/'README.md', CASES/'README.md', ROOT/'workspace/AGENTS.md'):
    text=entrypoint.read_text()
    assert all(case in text for case in ('UC-CONT-002','UC-CONT-003')), (
        entrypoint,'mandatory delivery/Gateway orientation missing')
    assert 'обязатель' in text.lower(), (entrypoint,'required-read wording missing')
assert 'Не нужно читать или даже просматривать весь главный реестр' in registry, 'no-all-registry-read rule missing'
assert 'UC-CONT-024' in registry and 'UC-CONT-017' in registry, 'documentation UC missing'
assert (ROOT/'README.md').read_text().find('docs/use-cases/README.md') < 500, (
    'root README must link directly to the registry at the start')

# Check live local links across the active docs, not only the use-case pages.
# Cross-repository links must be explicit URLs, not relative paths which resolve
# differently from linked worktrees. Dated audits and archived files are not
# live navigation and retain their own historical provenance.
active=(ROOT/'README.md',*sorted((ROOT/'docs').glob('*.md')),
        *sorted(CASES.glob('*.md')))
for page in active:
    for dest in re.findall(r'\]\(([^)]+)\)',page.read_text()):
        if '://' in dest or dest.startswith('/') or dest.startswith('#'):
            continue
        target,_,_anchor=dest.partition('#')
        if not target:continue
        assert (page.parent/target).is_file(),(str(page.relative_to(ROOT)),dest)
print('USE_CASE_REGISTRY_PASS',len(registered))
print('DOCUMENTATION_ENTRYPOINTS_AND_LINKS_PASS')


# Optional, explicitly located project registries. No network, no guessing at
# other Git clones. In source-only CI this is omitted; integration jobs supply
# the actual linked worktree roots for all prepared local registries.
parser=argparse.ArgumentParser(description='Check central and explicitly supplied local UC registries')
parser.add_argument('--local-root',action='append',default=[],metavar='NAME=PATH')
args=parser.parse_args()
expected={'fortis-approvals':'UC-GW-', 'docke-windows-mirror':'UC-MIR-',
          'tunnel':'UC-TUN-', 'script-control-center':'UC-SCC-'}
for item in args.local_root:
    assert '=' in item, ('expected NAME=PATH',item)
    name,location=item.split('=',1)
    assert name in expected,('unknown local family',name)
    local=Path(location).resolve()
    index=local/'docs/use-cases/README.md'
    assert index.is_file(),('local registry missing',index)
    assert name in registry,('local registry not in central catalog',name)
    registered=re.findall(r'^\| (UC-[A-Z]+-\d{3}) \|',index.read_text(),re.M)
    assert registered and len(set(registered))==len(registered),(name,'duplicate/missing local IDs')
    assert all(x.startswith(expected[name]) for x in registered),(name,'wrong local ID prefix')
    found=[]
    for doc in sorted(index.parent.glob('*.md')):
        content=doc.read_text()
        pieces=re.split(r'^## (UC-[A-Z]+-\d{3})\s*$',content,flags=re.M)
        for i in range(1,len(pieces),2):
            found.append(pieces[i])
            for mark in ('**Когда:**','**Цель:**','**Как:**','**Готово:**'):
                assert mark in pieces[i+1],(name,doc.name,pieces[i],mark)
        for link in re.findall(r'\]\(([^)]+)\)',content):
            if link.startswith(('https:','http:','mailto:','/workspace/')):continue
            part,_,anchor=link.partition('#')
            target=doc.parent/part if part else doc
            assert target.is_file(),(name,doc.name,link)
            if anchor.startswith(expected[name].lower()):
                assert ('## '+anchor.upper()) in target.read_text(),(name,doc.name,link)
    assert sorted(found)==sorted(registered),(name,'registry/owners mismatch')
    assert 'docs/use-cases/README.md' in (local/'README.md').read_text(),(name,'README local registry link missing')
    print('LOCAL_REGISTRY_PASS',name,len(registered))
