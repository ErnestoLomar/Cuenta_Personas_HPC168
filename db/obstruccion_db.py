import sqlite3
import traceback
import os
import sys

direccion_actual = os.getcwd().replace("\\", "/")
direccion_db = direccion_actual + "/CP/db/"

sys.path.insert(1, f'{direccion_db}')

URI = "/home/pi/CP/db/incidencias.db"

tabla_incidencias = '''CREATE TABLE IF NOT EXISTS incidencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folio_viaje VARCHAR(15),
        unidad INT,
        fechayhora VARCHAR(15),
        latitud VARCHAR(20),
        longitud VARCHAR(20),
        velocidad VARCHAR(20),
        name_img VARCHAR(20),
        check_servidor VARCHAR(10) default 'NO'
)'''

def crear_tabla_incidencias():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute(tabla_incidencias)
    except Exception as e:
        print("Error al crear la tabla de incidencias: "+str(e))
        print(traceback.format_exc())

def guardar_incidencia(folio_viaje,unidad,fechayhora,latitud,longitud,velocidad,name_img):
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("INSERT INTO incidencias (folio_viaje,unidad,fechayhora,latitud,longitud,velocidad,name_img) VALUES (?,?,?,?,?,?,?)", (folio_viaje,unidad,fechayhora,latitud,longitud,velocidad,name_img))
        con.commit()
    except Exception as e:
        print("Error al guardar la incidencia: "+str(e))
        print(traceback.format_exc())

def actualizar_incidencia(id,check_servidor):
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("UPDATE incidencias SET check_servidor = ? WHERE id = ?", (check_servidor, id))
        con.commit()
        return True
    except Exception as e:
        print("Error al actualizar la incidencia: "+str(e))
        print(traceback.format_exc())
        return False

def obtener_incidencias_no_enviadas():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT * FROM incidencias WHERE check_servidor = 'NO' LIMIT 1")
        return cur.fetchone()
    except Exception as e:
        print("Error al obtener la incidencia: "+str(e))
        print(traceback.format_exc())
        return []

def obtener_ultima_incidencia():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT * FROM incidencias order by id desc LIMIT 1")
        return cur.fetchone()
    except Exception as e:
        print("Error al obtener la ultima incidencia: "+str(e))
        print(traceback.format_exc())
        return None
    
def crear_tablas():
    crear_tabla_incidencias()