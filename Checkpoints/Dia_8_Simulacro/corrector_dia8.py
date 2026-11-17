"""Corrector offline del simulacro CCAR-F (60 preguntas originales).

Uso: python corrector_dia8.py respuestas.json
     python corrector_dia8.py respuestas.json --export resultados.json
No utiliza la API ni necesita dependencias externas.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def cargar_banco(path: Path | None = None) -> list[dict]:
    archivo = path or BASE / 'banco_preguntas.json'
    datos = json.loads(archivo.read_text(encoding='utf-8'))
    preguntas = datos['questions']
    if len(preguntas) != 60 or {p['number'] for p in preguntas} != set(range(1, 61)):
        raise ValueError('El banco debe contener exactamente las preguntas 1–60.')
    return preguntas


def validar_respuestas(data: dict, preguntas: list[dict]) -> dict[str, str]:
    if not isinstance(data, dict):
        raise TypeError('El archivo debe contener un objeto JSON con claves "1" a "60".')
    if set(data) != {str(p['number']) for p in preguntas}:
        raise ValueError('Las respuestas deben incluir exactamente las claves "1" a "60".')
    salida = {}
    for numero, valor in data.items():
        if not isinstance(valor, str):
            raise ValueError(f'Respuesta {numero}: debe ser texto A, B, C, D o vacío.')
        valor = valor.strip().upper()
        if valor not in {'', 'A', 'B', 'C', 'D'}:
            raise ValueError(f'Respuesta {numero}: opción inválida {valor!r}.')
        salida[numero] = valor
    return salida


def corregir(respuestas: dict, preguntas: list[dict]) -> dict:
    datos = validar_respuestas(respuestas, preguntas)
    por_dominio = defaultdict(lambda: {'aciertos': 0, 'total': 0, 'porcentaje': 0.0})
    por_escenario = defaultdict(lambda: {'aciertos': 0, 'total': 0, 'porcentaje': 0.0})
    errores = []
    pendientes = []
    aciertos = 0
    for p in preguntas:
        n = str(p['number'])
        r = datos[n]
        dom = por_dominio[p['domain']]
        sc = por_escenario[p['scenario']]
        dom['total'] += 1
        sc['total'] += 1
        if not r:
            pendientes.append(p['number'])
        elif r == p['answer']:
            aciertos += 1
            dom['aciertos'] += 1
            sc['aciertos'] += 1
        else:
            errores.append({
                'pregunta': p['number'], 'escenario': p['scenario'],
                'dominio': p['domain'], 'tu_respuesta': r,
                'correcta': p['answer'], 'explicacion': p['explanation'],
                'confusion': p['pitfall'],
            })
    for group in (por_dominio, por_escenario):
        for item in group.values():
            item['porcentaje'] = round(item['aciertos'] / item['total'] * 100, 1)
    prioridad = sorted(por_dominio, key=lambda d: (por_dominio[d]['porcentaje'], d))
    return {
        'aciertos': aciertos,
        'total': len(preguntas),
        'porcentaje': round(aciertos / len(preguntas) * 100, 1),
        'completo': len(pendientes) == 0,
        'pendientes': pendientes,
        'por_dominio': dict(por_dominio),
        'por_escenario': dict(por_escenario),
        'prioridad_repaso': prioridad,
        'errores': errores,
        'aviso': 'Nota didáctica: no es convertible a la puntuación oficial escalada 100–1000.',
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Corrige el examen CCAR-F Día 8 sin API.')
    parser.add_argument('archivo', nargs='?', default='respuestas.json', help='JSON con claves 1..60 y letras A-D')
    parser.add_argument('--export', help='Ruta JSON opcional para exportar resultados')
    args = parser.parse_args()
    archivo = Path(args.archivo)
    if not archivo.exists():
        archivo = BASE / args.archivo
    preguntas = cargar_banco()
    respuestas = json.loads(archivo.read_text(encoding='utf-8'))
    r = corregir(respuestas, preguntas)
    print(f'ACIERTO: {r["aciertos"]}/{r["total"]} ({r["porcentaje"]} %)')
    if not r['completo']:
        print(f'ATENCIÓN: hay {len(r["pendientes"])} preguntas sin contestar.')
    print('\nPOR DOMINIO:')
    for d, c in r['por_dominio'].items():
        print(f'  {d}: {c["aciertos"]}/{c["total"]} ({c["porcentaje"]} %)')
    print('\nPRIORIDAD DE REPASO:', ' → '.join(r['prioridad_repaso']))
    if r['errores']:
        print('\nERRORES Y JUSTIFICACIONES:')
        for err in r['errores']:
            print(f'  P{err["pregunta"]} ({err["dominio"]}): {err["tu_respuesta"]} → {err["correcta"]}: {err["explicacion"]}')
    print('\n' + r['aviso'])
    if args.export:
        Path(args.export).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
        print('Resultados exportados:', args.export)


if __name__ == '__main__':
    main()
