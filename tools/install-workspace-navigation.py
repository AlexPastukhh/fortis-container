#!/usr/bin/env python3
"""Update only managed navigation blocks; preserve other workspace instructions."""
import argparse
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[1]
BEGIN='<!-- FORTIS-USE-CASES:BEGIN -->'
END='<!-- FORTIS-USE-CASES:END -->'

def replace(text,body):
    block=BEGIN+'\n'+body.rstrip()+'\n'+END
    if BEGIN in text or END in text:
        assert text.count(BEGIN)==text.count(END)==1, 'ambiguous managed markers'
        a=text.index(BEGIN);b=text.index(END,a)+len(END)
        return text[:a]+block+text[b:]
    if not text:return block+'\n'
    first,separator,rest=text.partition('\n')
    return first+'\n\n'+block+'\n'+rest if separator else text+'\n\n'+block+'\n'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workspace',type=Path,default=Path('/workspace/repo'))
    p.add_argument('--check',action='store_true');args=p.parse_args()
    assert args.workspace.is_dir() and (SOURCE/'docs/use-cases/README.md').is_file()
    navigation=('## Навигация по юзкейсам\n\n'
        +'Общая документация ведётся через [реестр контейнера]('
        +str(SOURCE/'docs/use-cases/README.md')+').\n'
        +'Общие Docker/GitHub/AI правила — здесь; Gateway/Provider/Mirror UI и '
        +'предметные UC — в локальных реестрах по ссылкам.\n'
        +'Сначала прочитай `/workspace/repo/AGENTS.md`. Источник проекции: `'+str(SOURCE)+'`.\n'
        +'Использовать принятый primary main; временный linked source сохранять, пока на него есть ссылки.\n'
        +'**Каждый новый чат:** учти исходное сообщение, прочитай короткий вход '
        +'реестра; **всю таблицу читать или просматривать не нужно**. '
        +'Обязательно прочитай полностью '
        +'[UC-CONT-002 — Docker → GitHub → CI → Windows/Mirror]('
        +str(SOURCE/'docs/use-cases/delivery.md')+'#uc-cont-002) и '
        +'[UC-CONT-003 — GitHub только через typed Gateway-клиент]('
        +str(SOURCE/'docs/use-cases/delivery.md')+'#uc-cont-003). '
        +'Контекст repo или работа без него — UC-CONT-001; остальные UC по задаче. Перед GitHub-эффектом проверь '
        +'live capabilities; при отсутствии scope — STOP / [UC-CONT-018]('
        +str(SOURCE/'docs/use-cases/delivery.md')+'#uc-cont-018).')
    bodies={'README.md':navigation,'AGENTS.md':(SOURCE/'workspace/AGENTS.md').read_text()}
    changed=[]
    for name,body in bodies.items():
        target=args.workspace/name
        assert not target.is_symlink(), 'symlink target denied'
        old=target.read_text() if target.exists() else ''
        new=replace(old,body)
        if new!=old:
            changed.append(name)
            if not args.check:target.write_text(new)
    if args.check and changed:raise SystemExit('stale navigation: '+', '.join(changed))
    print('WORKSPACE_NAVIGATION_PASS')

if __name__=='__main__':main()
