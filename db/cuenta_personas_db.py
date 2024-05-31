import sqlite3
import traceback
import os
import sys

direccion_actual = os.getcwd().replace("\\", "/")
direccion_db = direccion_actual + "/CP/db/"

sys.path.insert(1, f'{direccion_db}')

URI = "/home/pi/CP/db/cuenta_personas.db"

tabla_delantero = '''CREATE TABLE IF NOT EXISTS cuentap_delantero (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folio_viaje VARCHAR(15),
        unidad INT,
        fechayhora VARCHAR(15),
        subida INT,
        bajada INT,
        latitud VARCHAR(20),
        longitud VARCHAR(20),
        velocidad VARCHAR(20),
        check_servidor VARCHAR(10) default 'NO'
)'''

tabla_trasero = '''CREATE TABLE IF NOT EXISTS cuentap_trasero (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folio_viaje VARCHAR(15),
        unidad INT,
        fechayhora VARCHAR(15),
        subida INT,
        bajada INT,
        latitud VARCHAR(20),
        longitud VARCHAR(20),
        velocidad VARCHAR(20),
        check_servidor VARCHAR(10) default 'NO'
)'''

def crear_tabla_cuentap_delantero():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute(tabla_delantero)
    except Exception as e:
        print("Error al crear la tabla de cuentap_delantero: "+str(e))
        print(traceback.format_exc())

def crear_tabla_cuentap_trasero():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute(tabla_trasero)
    except Exception as e:
        print("Error al crear la tabla de cuentap_trasero: "+str(e))
        print(traceback.format_exc())

def guardar_cuentap_delantero(folio_viaje,unidad,fechayhora,subida,bajada,latitud,longitud,velocidad):
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("INSERT INTO cuentap_delantero (folio_viaje,unidad,fechayhora,subida,bajada,latitud,longitud,velocidad) VALUES (?,?,?,?,?,?,?,?)", (folio_viaje,unidad,fechayhora,subida,bajada,latitud,longitud,velocidad))
        con.commit()
    except Exception as e:
        print("Error al guardar la cuenta de personas delantero: "+str(e))
        print(traceback.format_exc())

def guardar_cuentap_trasero(folio_viaje,unidad,fechayhora,subida,bajada,latitud,longitud,velocidad):
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("INSERT INTO cuentap_trasero (folio_viaje,unidad,fechayhora,subida,bajada,latitud,longitud,velocidad) VALUES (?,?,?,?,?,?,?,?)", (folio_viaje,unidad,fechayhora,subida,bajada,latitud,longitud,velocidad))
        con.commit()
    except Exception as e:
        print("Error al guardar la cuenta de personas trasero: "+str(e))
        print(traceback.format_exc())

def actualizar_cuentap_delantero(id,check_servidor):
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("UPDATE cuentap_delantero SET check_servidor = ? WHERE id = ?", (check_servidor, id))
        con.commit()
        return True
    except Exception as e:
        print("Error al actualizar la cuenta de personas delantero: "+str(e))
        print(traceback.format_exc())
        return False

def actualizar_cuentap_trasero(id,check_servidor):
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("UPDATE cuentap_trasero SET check_servidor = ? WHERE id = ?", (check_servidor, id))
        con.commit()
    except Exception as e:
        print("Error al actualizar la cuenta de personas trasero: "+str(e))
        print(traceback.format_exc())

def obtener_cuentap_delantero_no_enviados():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT * FROM cuentap_delantero WHERE check_servidor = 'NO' LIMIT 1")
        return cur.fetchone()
    except Exception as e:
        print("Error al obtener la cuenta de personas delantero: "+str(e))
        print(traceback.format_exc())
        return []

def obtener_cuentap_trasero_no_enviados():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT * FROM cuentap_trasero WHERE check_servidor = 'NO' LIMIT 1")
        return cur.fetchone()
    except Exception as e:
        print("Error al obtener la cuenta de personas trasero: "+str(e))
        print(traceback.format_exc())
        return []

def obtener_cuentap_delantero_ultimo():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT * FROM cuentap_delantero order by id desc LIMIT 1")
        return cur.fetchone()
    except Exception as e:
        print("Error al obtener la cuenta de personas delantero: "+str(e))
        print(traceback.format_exc())
        return None

def obtener_cuentap_trasero_ultimo():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT * FROM cuentap_trasero order by id desc LIMIT 1")
        return cur.fetchone()
    except Exception as e:
        print("Error al obtener la cuenta de personas trasero: "+str(e))
        print(traceback.format_exc())
        return None
    
def crear_tablas():
    crear_tabla_cuentap_delantero()
    crear_tabla_cuentap_trasero()