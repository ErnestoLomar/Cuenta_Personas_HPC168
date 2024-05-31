import socket
from PyQt5.QtCore import QObject, pyqtSignal
import time as tm
import os
import sys
import traceback

direccion_actual = os.getcwd().replace("\\", "/")
direccion_db = direccion_actual + "/CP/db/"

sys.path.insert(1, f'{direccion_db}')

from cuenta_personas_db import obtener_cuentap_delantero_no_enviados, actualizar_cuentap_delantero
from obstruccion_db import obtener_incidencias_no_enviadas, actualizar_incidencia

class LeerAzureWorker(QObject):

    finished = pyqtSignal()
    progress = pyqtSignal(str)
    
    def __init__(self) -> None:
        
        super().__init__()
        
        try:
            # Definir las credenciales
            self.server = '20.106.77.209'
            self.port = 8170
            
        except Exception as e:
            print(f'Error en la conexión a Azure: ' + str(e))
            print(traceback.print_exc())
            
    def conectar_al_servidor(self, server, puerto):
        try:
            # Crear un objeto de socket
            cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Conectar al servidor
            cliente_socket.connect((server, puerto))

            # Si no se produce ninguna excepción, la conexión fue exitosa
            print("Conexión exitosa al servidor")
            return cliente_socket
        except Exception as e:
            print(f"Error al conectar al servidor: {str(e)}")
            print(traceback.print_exc())
            return None
        
    def verificar_conexion(self, cliente_socket):
        try:
            if cliente_socket is not None:
                mensaje_prueba = b"[ping,430]"
                cliente_socket.send(mensaje_prueba)

                # Esperar una pequeña respuesta
                respuesta = cliente_socket.recv(4)

                # Verificar si la respuesta es la esperada
                if respuesta == b"pong":
                    return True
                else:
                    raise Exception("Respuesta no válida")
            else:
                return False
        except Exception as e:
            print(f"Error al verificar conexión: {str(e)}")
            return False
        finally:
            # Restaurar el socket a su configuración original
            if cliente_socket is not None:
                cliente_socket.settimeout(None)
            else:
                return False
        
    def run(self):
        
        # Conectar al servidor
        self.cliente_socket = self.conectar_al_servidor(self.server, self.port)

        while True:
            
            try:
                
                if not self.verificar_conexion(self.cliente_socket):
                    
                    print("La conexión se ha perdido. Intentando reconectar...")
                    
                    if self.cliente_socket is not None:
                        self.cliente_socket.close()
                    
                    self.cliente_socket = self.conectar_al_servidor(self.server, self.port)
                    
                else:
            
                    self.enviar_proceso()
                    self.enviar_incidencia()
                    
                tm.sleep(0.5)
                    
            except Exception as e:
                print(f'Error en la conexión a Azure: ' + str(e))
                print(traceback.print_exc())
                
    def calcular_checksum(self, trama):
        checksum = 0
        for char in trama:
            checksum += ord(char)
        return str(checksum)[-3:]
                
    def enviar_proceso(self):
        
        datos_cuentap_delantero_no_enviados = obtener_cuentap_delantero_no_enviados()
        
        if datos_cuentap_delantero_no_enviados is None:

            print("No hay datos para enviar")
            return
                    
        if len(datos_cuentap_delantero_no_enviados) > 0:
                
            try:
            
                id_cuentapD = datos_cuentap_delantero_no_enviados[0]
                folio_viaje_cuentapD = datos_cuentap_delantero_no_enviados[1]
                unidad_cuentapD = datos_cuentap_delantero_no_enviados[2]
                fechayhora_cuentapD = datos_cuentap_delantero_no_enviados[3]
                subida_cuentapD = datos_cuentap_delantero_no_enviados[4]
                bajada_cuentapD = datos_cuentap_delantero_no_enviados[5]
                latitud_cuentapD = datos_cuentap_delantero_no_enviados[6]
                longitud_cuentapD = datos_cuentap_delantero_no_enviados[7]
                velocidad_cuentapD = datos_cuentap_delantero_no_enviados[8]
                check_servidor_cuentapD = datos_cuentap_delantero_no_enviados[9]
                
                trama = '2,D,'+str(id_cuentapD)+','+str(folio_viaje_cuentapD)+','+str(unidad_cuentapD)+','+str(fechayhora_cuentapD)+','+str(subida_cuentapD)+','+str(bajada_cuentapD)+','+str(latitud_cuentapD)+','+str(longitud_cuentapD)+','+str(velocidad_cuentapD)
                checksum_cuentapD = self.calcular_checksum(trama)
                trama = "["+trama+","+str(checksum_cuentapD)+"]"
                print("\033[4;35;47m"+"Trama 2CpD a enviar: "+trama+'\033[0;m')
                
                # Enviar los datos al servidor
                self.cliente_socket.sendall(trama.encode('utf-8'))
                
                print("\033[;32m"+f'Registro {id_cuentapD} enviado.')
                
                # Recibir la respuesta del servidor
                respuesta_servidor = self.cliente_socket.recv(1024).decode('utf-8')

                print(f'Respuesta del servidor para registro {id_cuentapD}: {respuesta_servidor}')
                
                if respuesta_servidor == 'SKTOK':
                    
                    self.done = actualizar_cuentap_delantero(id_cuentapD, "OK")
                
                    if self.done:
                        print("\033[;32m"+f'check_servidor de proceso {id_cuentapD} modificado a OK')
                    else:
                        print("\033[;31m"+f'check_servidor de proceso {id_cuentapD} no se pudo modificar')
                else:
                    print("\033[;31m"+f'Error en la respuesta del servidor para registro {id_cuentapD}: {respuesta_servidor}')
                
            except Exception as e:
                print("\033[;31m"+f'Error enviando registro: ' + str(e))
                print(traceback.print_exc())
        else:
            print("No hay datos pendientes por enviar...")
        
        tm.sleep(0.5)
        
    def enviar_incidencia(self):
        
        datos_incidencias_no_enviadas = obtener_incidencias_no_enviadas()
        
        if datos_incidencias_no_enviadas is None:

            print("No hay datos para enviar")
            return
                    
        if len(datos_incidencias_no_enviadas) > 0:
                
            try:
            
                id_incidenciaD = datos_incidencias_no_enviadas[0]
                folio_viaje_cuentapD = datos_incidencias_no_enviadas[1]
                unidad_cuentapD = datos_incidencias_no_enviadas[2]
                fechayhora_cuentapD = datos_incidencias_no_enviadas[3]
                latitud_cuentapD = datos_incidencias_no_enviadas[4]
                longitud_cuentapD = datos_incidencias_no_enviadas[5]
                velocidad_cuentapD = datos_incidencias_no_enviadas[6]
                name_img_cuentapD = datos_incidencias_no_enviadas[7]
                check_servidor_cuentapD = datos_incidencias_no_enviadas[8]
                
                trama = '3,D,'+str(id_incidenciaD)+','+str(folio_viaje_cuentapD)+','+str(unidad_cuentapD)+','+str(fechayhora_cuentapD)+','+str(latitud_cuentapD)+','+str(longitud_cuentapD)+','+str(velocidad_cuentapD)+","+str(name_img_cuentapD)
                checksum_cuentapD = self.calcular_checksum(trama)
                trama = "["+trama+","+str(checksum_cuentapD)+"]"
                print("\033[4;35;47m"+"Trama 3CpD a enviar: "+trama+'\033[0;m')
                
                # Enviar los datos al servidor
                self.cliente_socket.sendall(trama.encode('utf-8'))
                
                print("\033[;32m"+f'Registro {id_incidenciaD} enviado.')
                
                # Recibir la respuesta del servidor
                respuesta_servidor = self.cliente_socket.recv(1024).decode('utf-8')

                print(f'Respuesta del servidor para registro {id_incidenciaD}: {respuesta_servidor}')
                
                if respuesta_servidor == 'SKTOK':
                    
                    self.done = actualizar_incidencia(id_incidenciaD, "OK")
                
                    if self.done:
                        print("\033[;32m"+f'check_servidor de proceso {id_incidenciaD} modificado a OK')
                    else:
                        print("\033[;31m"+f'check_servidor de proceso {id_incidenciaD} no se pudo modificar')
                else:
                    print("\033[;31m"+f'Error en la respuesta del servidor para registro {id_incidenciaD}: {respuesta_servidor}')
                
            except Exception as e:
                print("\033[;31m"+f'Error enviando registro: ' + str(e))
                print(traceback.print_exc())
        else:
            print("No hay datos pendientes por enviar...")
        
        tm.sleep(0.5)