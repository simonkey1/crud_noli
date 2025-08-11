"""
Herramienta para preparar la migración de índice único en Producto.codigo_barra.

Modos:
- clear_dups (default): Detecta códigos duplicados (no nulos/ni vacíos) y deja solo uno; al resto les pone NULL.
- clear_all: Pone todos los codigo_barra en NULL (útil si quieres empezar limpio).
- fill_auto: Rellena codigo_barra vacío/NULL o igual a '1' con un placeholder único 'SKU-{id}'.

Uso:
  python -m scripts.fix_barcode_duplicates --mode clear_dups
  python -m scripts.fix_barcode_duplicates --mode clear_all
  python -m scripts.fix_barcode_duplicates --mode fill_auto
"""
from sqlmodel import Session, select
from collections import defaultdict
from typing import Optional
import argparse

from db.database import engine
from models.models import Producto


def clear_duplicates(session: Session) -> int:
    """Deja un solo producto por codigo_barra; al resto los pone en NULL."""
    # Mapear codigo_barra -> lista de ids
    dups = defaultdict(list)
    productos = session.exec(select(Producto)).all()
    for p in productos:
        cb = (p.codigo_barra or '').strip()
        if cb:
            dups[cb].append(p)

    cambios = 0
    for cb, prods in dups.items():
        if len(prods) > 1:
            # Dejar el primero y limpiar los demás
            for p in prods[1:]:
                p.codigo_barra = None
                session.add(p)
                cambios += 1
    session.commit()
    return cambios


essential_values = {'', ' ', '1'}

def clear_all(session: Session) -> int:
    cambios = 0
    productos = session.exec(select(Producto)).all()
    for p in productos:
        if p.codigo_barra is not None:
            p.codigo_barra = None
            session.add(p)
            cambios += 1
    session.commit()
    return cambios


def fill_auto(session: Session) -> int:
    """Rellena codigo_barra vacío/NULL o con valores triviales ('1') como 'SKU-{id}'."""
    cambios = 0
    productos = session.exec(select(Producto)).all()
    for p in productos:
        val = (p.codigo_barra or '').strip()
        if (not val) or (val in essential_values):
            p.codigo_barra = f"SKU-{p.id}"
            session.add(p)
            cambios += 1
    session.commit()
    return cambios


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['clear_dups', 'clear_all', 'fill_auto'], default='clear_dups')
    args = parser.parse_args()

    with Session(engine) as session:
        if args.mode == 'clear_dups':
            changes = clear_duplicates(session)
            print(f"Duplicados limpiados (a NULL): {changes}")
        elif args.mode == 'clear_all':
            changes = clear_all(session)
            print(f"Códigos limpiados a NULL: {changes}")
        elif args.mode == 'fill_auto':
            changes = fill_auto(session)
            print(f"Códigos rellenados con placeholders: {changes}")


if __name__ == '__main__':
    main()
