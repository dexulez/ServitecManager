#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar clientes en la base de datos
"""
import sqlite3

DB_PATH = "SERVITEC_TEST_OPTIMIZED.DB"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("\n" + "="*80)
print("CLIENTES EN BASE DE DATOS")
print("="*80)

cursor.execute("SELECT id, cedula, nombre, telefono FROM clientes ORDER BY id")
clientes = cursor.fetchall()

print(f"\nTotal clientes: {len(clientes)}\n")
for c in clientes:
    print(f"ID: {c[0]:3d} | Cédula: {c[1]:20s} | Nombre: {c[2]:30s} | Tel: {c[3]}")

print("\n" + "="*80)
print("ÓRDENES Y SUS CLIENTES")
print("="*80)

cursor.execute("""
    SELECT o.id, o.cliente_id, c.nombre, o.equipo 
    FROM ordenes o 
    LEFT JOIN clientes c ON o.cliente_id = c.id 
    ORDER BY o.id DESC 
    LIMIT 5
""")
ordenes = cursor.fetchall()

print(f"\nÚltimas 5 órdenes:\n")
for o in ordenes:
    cliente_info = o[2] if o[2] else "⚠️ CLIENTE NO ENCONTRADO"
    print(f"Orden #{o[0]} | Cliente ID: {o[1]} | Cliente: {cliente_info} | Equipo: {o[3]}")

print("\n" + "="*80)

conn.close()
