import traceback
from PyQt5.QtCore import QObject, pyqtSignal
import time
import os
import sys

direccion_actual = os.getcwd().replace("\\", "/")
direccion_db = direccion_actual + "/CP/db/"
direccion_tcp = direccion_actual + "/CP/tcp/"

sys.path.insert(1, f'{direccion_db}')
sys.path.insert(1, f'{direccion_tcp}')

from comand import Principal_Modem
from cuenta_personas_db import obtener_cuentap_delantero_no_enviados, actualizar_cuentap_delantero

#Creamos un objeto de la clase Principal_Modem
modem = Principal_Modem()

class EnviarDatos(QObject):
    
    try:
        finished = pyqtSignal()
        progress = pyqtSignal(str)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        
    def __init__(self):
        super().__init__()
        modem.abrir_puerto()
        
    def run(self):
        self.mandar_datos_cuentap_delantero()
        time.sleep(1)
    
    
    def calcular_checksum(self, trama):
        checksum = 0
        for char in trama:
            checksum += ord(char)
        return str(checksum)[-3:]
    
    def mandar_datos_cuentap_delantero(self):
        try:
            datos_cuentap_delantero_no_enviados = obtener_cuentap_delantero_no_enviados()
            
            if datos_cuentap_delantero_no_enviados is not None:
                
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
                    
                    result = modem.mandar_datos(trama)
                    enviado = result['enviado']

                    if enviado == True:
                        try:
                            
                            checksum_socket_t4 = str(result["accion"]).replace("SKT","")[:3]
                            #print("El checksum t4 es: ", checksum_socket_t4)
                            
                            if checksum_socket_t4 in checksum_cuentapD:
                                
                                done = actualizar_cuentap_delantero(id_cuentapD, "OK")
                                
                                if done:
                                    print("\x1b[1;32m"+"#############################################")
                                    print("\x1b[1;32m"+"Trama de fin de viaje enviada")
                                    print("\x1b[1;32m"+"#############################################")
                                else:
                                    print("\x1b[1;31;47m"+"#############################################"+'\033[0;m')
                                    print("\x1b[1;31;47m"+"CheckServidor no modificado"+'\033[0;m')
                                    print("\x1b[1;31;47m"+"#############################################"+'\033[0;m')
                                self.realizar_accion(result)
                            else:
                                print("\x1b[1;31;47m"+"El checksum no coincide"+'\033[0;m')
                        except Exception as e:
                            print("LeerMinicom.py, linea 376: "+str(e))
                    else:
                        print("\x1b[1;31;47m"+"#############################################"+'\033[0;m')
                        print("\x1b[1;31;47m"+"Trama de fin de viaje no enviada"+'\033[0;m')
                        print("\x1b[1;31;47m"+"#############################################"+'\033[0;m')
                    self.reeconectar_socket(enviado)
                    
                except Exception as e:
                    print(str(e))
                    print(traceback.format_exc())
        except Exception as e:
            print(str(e))
            print(traceback.format_exc())