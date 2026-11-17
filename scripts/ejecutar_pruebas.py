#!/usr/bin/env python3
"""Ejecutar pruebas locales por día sin llamar a la API.

Usa el intérprete de Python activo y ejecuta cada suite con un cwd independiente.
"""
from pathlib import Path
import re, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'Checkpoints'
failures=[]
for day in range(1,9):
    options=sorted(p for p in BASE.iterdir() if p.is_dir() and re.match(fr'Dia_0?{day}(?:_|$)',p.name,re.I))
    if not options: continue
    p=options[0]
    if (p/'tests').is_dir():
        cmd=[sys.executable,'-m','unittest','discover','-s','tests','-v']
    elif (p/'test_agente_dia2.py').exists():
        cmd=[sys.executable,'-m','unittest','-v','test_agente_dia2']
    elif (p/'test_dia3.py').exists():
        cmd=[sys.executable,'-m','unittest','-v','test_dia3']
    else:
        print(f'Día {day}: sin pruebas automatizadas detectadas')
        continue
    print(f'\n=== Día {day}: {p.name} ===', flush=True)
    completed=subprocess.run(cmd,cwd=p,check=False)
    if completed.returncode:
        print(f'FALLO Día {day}: exit={completed.returncode}',file=sys.stderr)
        failures.append(day)
print('\nPruebas finalizadas.')
if failures:
    print('Días fallidos:',failures,file=sys.stderr)
    raise SystemExit(1)
