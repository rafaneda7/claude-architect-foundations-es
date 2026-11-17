#!/usr/bin/env python3
"""Auditoría heurística de seguridad y tamaño antes de publicar.
No imprime valores de secretos, solo rutas de archivos a revisar.
"""
from pathlib import Path
import json,re,subprocess
ROOT=Path(__file__).resolve().parents[1]
SKIP={'.venv','venv','.git','__pycache__','.history','.pytest_cache','.ipynb_checkpoints'}
TOKENS=[re.compile(rb'sk-ant-[A-Za-z0-9_-]{18,}'),re.compile(rb'ghp_[A-Za-z0-9]{30,}')]
found=[]
for p in ROOT.rglob('*'):
    if not p.is_file() or SKIP.intersection(p.relative_to(ROOT).parts):continue
    relative=p.relative_to(ROOT)
    if p.stat().st_size>5_000_000:
        found.append((str(relative),'mayor que 5 MB'))
    if p.name in ('.env','config.py'):
        found.append((str(relative),'configuración local: revisar Git tracking'))
    if p.suffix=='.ipynb':
        try:
            doc=json.loads(p.read_text(encoding='utf-8-sig'))
            outputs=sum(len(c.get('outputs',[])) for c in doc.get('cells',[]) if c.get('cell_type')=='code')
            if outputs:found.append((str(relative),f'{outputs} resultados almacenados en notebook'))
        except Exception:
            found.append((str(relative),'notebook no legible como JSON'))
    if p.suffix in ('.py','.md','.json','.ipynb','.txt','.env') or p.name=='config.py':
        if p.stat().st_size>2_000_000:continue
        try:
            data=p.read_bytes()
            if any(rx.search(data) for rx in TOKENS):
                found.append((str(relative),'posible clave de acceso en texto'))
        except OSError:pass
print('AUDITORÍA INFORMATIVA: no modifica archivos ni imprime secretos')
for item in found: print('-',*item,sep='  ')
if not found:print('No se encontraron alertas heurísticas. No garantiza ausencia de secretos.')
else:print(f'Alertas para revisión manual: {len(found)}')
