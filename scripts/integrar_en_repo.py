#!/usr/bin/env python3
"""Integra este paquete en un repositorio existente sin sobrescribir archivos.

El análisis predeterminado es --dry-run. Solo --apply escribe cambios.
"""
import argparse, re, shutil, hashlib
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[1]


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):
            h.update(chunk)
    return h.digest()


def target_for(source, dest):
    rel=source.relative_to(SOURCE)
    if rel.parts[0] != 'Checkpoints' or len(rel.parts)<3:
        return dest/rel
    m=re.match(r'Dia_0?([1-8])(?:_|$)',rel.parts[1],flags=re.I)
    if not m:return dest/rel
    day=int(m.group(1))
    cp=dest/'Checkpoints'
    candidates=sorted(p for p in cp.iterdir() if p.is_dir() and re.match(fr'Dia_0?{day}(?:_|$)',p.name,re.I)) if cp.exists() else []
    # No rename and no duplicate day folder if a matching existing one exists
    folder=candidates[0] if candidates else cp/rel.parts[1]
    return folder.joinpath(*rel.parts[2:])


def run():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dest',type=Path,required=True,help='Raíz del proyecto claude_architect')
    ap.add_argument('--apply',action='store_true',help='Copia faltantes, sin sobrescribir')
    opts=ap.parse_args()
    dest=opts.dest.expanduser().resolve()
    if dest==SOURCE.resolve():
        ap.error('La fuente ya es el destino; no hay integración que ejecutar.')
    if not dest.is_dir():
        ap.error(f'No existe el directorio destino: {dest}')
    stats={'nuevos':0,'identicos':0,'conflictos':0}
    for source in sorted(p for p in SOURCE.rglob('*') if p.is_file()):
        if '.git' in source.parts or '__pycache__' in source.parts or source.name.endswith('.pyc'):
            continue
        # El manifiesto describe la fuente; las herramientas de integración no se copian sobre el propio destino.
        target=target_for(source,dest)
        if target.exists():
            if sha(source)==sha(target):
                stats['identicos']+=1
            else:
                stats['conflictos']+=1
                print(f'CONFLICTO (no sobrescrito): {target}')
            continue
        stats['nuevos']+=1
        print(('COPIAR' if opts.apply else 'NUEVO (simulación)')+f': {target}')
        if opts.apply:
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,target)
    print('\nResumen:',stats)
    if stats['conflictos']:
        print('Revisa los conflictos manualmente; no se ha borrado ni reemplazado contenido.')
    if not opts.apply:
        print('Ejecuta otra vez con --apply para copiar únicamente los archivos nuevos.')

if __name__=='__main__':run()
