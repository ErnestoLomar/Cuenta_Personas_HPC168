import serial
import sys
import time as tm
import traceback
import os
from time import strftime
from PyQt5.QtCore import QThread
import ntplib
from datetime import datetime
import subprocess

direccion_actual = os.getcwd().replace("\\", "/")
direccion_db = direccion_actual + "/CP/db/"
direccion_internet = direccion_actual + "/CP/internet/"
direccion_tcp = direccion_actual + "/CP/tcp/"
direccion_threads = direccion_actual + "/CP/threads/"
direccion_utils = direccion_actual + "/CP/utils/"

sys.path.insert(1, f'{direccion_db}')
sys.path.insert(1, f'{direccion_internet}')
sys.path.insert(1, f'{direccion_tcp}')
sys.path.insert(1, f'{direccion_threads}')
sys.path.insert(1, f'{direccion_utils}')


from cuenta_personas_db import obtener_cuentap_delantero_ultimo, guardar_cuentap_delantero, obtener_cuentap_delantero_no_enviados, obtener_cuentap_trasero_no_enviados, actualizar_cuentap_delantero
from comand import Principal_Modem
import actualizar_hora
import hilo_enviar_datos
from azure import LeerAzureWorker
from revisar_obst import RevisarObst

destination = "INTERNET"

#Creamos un objeto de la clase Principal_Modem
modem = Principal_Modem()

class CuentaPersonas():
    
    def __init__(self) -> None:
        
        super().__init__()
        self.run_detect_obst()
        
        try:
            ############# Conectándonos al cuenta personas #############
            try:
                self.ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

                if (self.ser.is_open):
                    print("Conexion establecida en /dev/ttyUSB0")
                else:
                    print("Conexion fallida /dev/ttyUSB0")
            except Exception as e:
                print(e)
                try:
                    self.ser = serial.Serial('/dev/ttyUSB1', 115200, timeout=1)

                    if (self.ser.is_open):
                        print("Conexion establecida en /dev/ttyUSB1")
                    else:
                        print("Conexion fallida /dev/ttyUSB1")
                except Exception as ex:
                    print(e)
            ############################################################
            
        except Exception as e:
            print(f'Error en la conexión a Azure: ' + str(e))
            print(traceback.print_exc())
    
    def run_send_data_tcp(self):
        try:
            self.thread = QThread()
            self.worker = hilo_enviar_datos.EnviarDatos()
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.progress.connect(self.report_progress_tcp)
            self.thread.start()
        except Exception as e:
            print("Error al iniciar el hilo de enviar datos TCP: " + str(e))
            print(traceback.print_exc())
        
    #leer la tarjeta
    def report_progress_tcp(self):
        try:
            pass
        except Exception as e:
            print(traceback.print_exc())

    def run_send_data_internet(self):
        try:
            self.azureThread = QThread()
            self.azureWorker = LeerAzureWorker()
            self.azureWorker.moveToThread(self.azureThread)
            self.azureThread.started.connect(self.azureWorker.run)
            self.azureWorker.finished.connect(self.azureThread.quit)
            self.azureWorker.finished.connect(self.azureWorker.deleteLater)
            self.azureThread.finished.connect(self.azureThread.deleteLater)
            self.azureWorker.progress.connect(self.report_progress_internet)
            self.azureThread.start()
        except Exception as e:
            print("Error en la clase Main ejecutando Azure: " + str(e))
            print(traceback.format_exc())
            
    def report_progress_internet(self, res: str):
        try:
            print("Progreso de Azure: " + res)
        except Exception as e:
            print("Error en la clase Main reportando progreso de Azure: " + str(e))
            print(traceback.format_exc())
            
    def run_detect_obst(self):
        try:
            self.obstThread = QThread()
            self.obstWorker = RevisarObst()
            self.obstWorker.moveToThread(self.obstThread)
            self.obstThread.started.connect(self.obstWorker.run)
            self.obstWorker.finished.connect(self.obstThread.quit)
            self.obstWorker.finished.connect(self.obstWorker.deleteLater)
            self.obstThread.finished.connect(self.obstThread.deleteLater)
            self.obstWorker.progress.connect(self.report_progress_detect_obst)
            self.obstThread.start()
        except Exception as e:
            print("Error en la clase Main obst: " + str(e))
            print(traceback.format_exc())
            
    def report_progress_detect_obst(self, res: str):
        try:
            pass
        except Exception as e:
            print("Error en la clase Main obst: " + str(e))
            print(traceback.format_exc())
            
            
    def revisar_cuentapersonas(self):
        ####################### cuenta personas delantero #######################
        try:
            folio_viaje = "NO"
            if folio_viaje == 'NO':
                fecha = strftime("%Y%m%d")
                folio_viaje = fecha + '9999'
            fecha = strftime("%Y%m%d%H%M%S")
            subida=0
            bajada=0

            ### DATOS Cuenta Personas ###
            data = bytearray(45)
            k, ID_H, ID_D, CM_H, CM_D, LEN_H, LEN_D, DATA1UP_D, DATA1DW_D, CHK_ARD_D = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            correct_set = False
            CHK_ARD_H_LSB = bytearray(2)
            CHK_HPC_H_LSB = bytearray(2)

            # Se prepara el espacio para los 45 datos que abarca la trama; se configuran a un valor inicial de 0x77
            data = [0x77] * 45
            # print(data)
            
            # Definir la trama de datos como una cadena de bytes
            frame = bytes([0x02, 0x30, 0x30, 0x30, 0x31, 0x31, 0x33, 0x30, 0x30, 0x31, 0x34, 0x03])
            
            self.ser.write(frame)

            self.ser.flush()
            
            print("\033[;36m"+"Ya se escribio la indicacion en el serial")

            # Despliega aviso hacia la PC
            #print("Finaliza transmisión.")
        
            # Despliega aviso hacia la PC
            print("\033[;36m"+"Comienza recepción...")

            # Llena los datos en el arreglo
            for k in range(1, 45):
                data[k] = format(int.from_bytes(self.ser.read(), byteorder='big'), 'X')

            # while ser.in_waiting:
            print("\033[;36m"+"Entro")

            # Elimina el primer dato del array
            data.pop(0)
            #print(data)
            # Leer el primer byte y verificar si es STX (0x02)
            #print(data[0])
            if data[0] != '2':
                print("El comienzo de la trama de datos STX es diferente al esperado. Se procede a esperar el siguiente dato.")
            # else:
            #     for k in range(1, 45):
            #         data[k] = format(int.from_bytes(ser.read(), byteorder='big'), 'X')

            # Despliega aviso hacia la PC
            #print("Finaliza recepción.")

            correct_set = True
            for k in range(44):
                #print(data[k])
                if data[k] == 0xFF:
                    print(" <-- Este dato es incorrecto.")
                    correct_set = False
                if data[k] == 0x77:
                    print("  <-- Este dato ni siquiera fue modificado con respecto a su valor inicial.")
                    correct_set = False

            if correct_set == False:
                print(": ", data[0])
                print("Los datos son erróneos. Se procede a descartar la trama de datos.")
            else:
                print("\033[;36m"+"Entra a la validacion de datos")
                # Leer el ultimo byte y verificar si es ETX (0x03)
                if data[43] != '3':
                    print("El final de la trama de datos ETX es diferente al esperado. Se procede a descartar la trama de datos.")
                else:
                    ID_H = (int(data[1], 16)-48)*1000 + (int(data[2], 16)-48)*100 + (int(data[3], 16)-48)*10 + int(data[4], 16)-48
                    ID_D = (int(data[1], 16)-48)*4096 + (int(data[2], 16)-48)*256 + (int(data[3], 16)-48)*16 + int(data[4], 16)-48
                    CM_H = (int(data[5], 16)-48)*10 + int(data[6], 16)-48
                    CM_D = (int(data[5], 16)-48)*16 + int(data[6], 16)-48
                    LEN_H = (int(data[7], 16)-48)*10 + int(data[8], 16)-48
                    LEN_D = (int(data[7], 16)-48)*16 + int(data[8], 16)-48
                    
                    if (LEN_D != 16):
                        print("Los datos del conteo de pasajeros no vienen separados en dos grupos de 8 bytes. Se procede a descartar la trama de datos.")
                    else:
                        if (CM_H != 93):
                            print(
                                "El comando CM no es 0x39 0x33; no es el valor que se esperaba. Se procede a descartar la trama de datos.")
                        else:
                            if (LEN_H != 10):
                                print(
                                    "La longitud LEN no es 0x31 0x30; no es el valor que se esperaba. Se procede a descartar la trama de datos.")
                            else:
                                if (data[25] != '30' or data[26] != '30' or data[27] != '30' or data[28] != '30' or data[29] != '30' or data[30] != '30' or data[31] != '30' or data[32] != '30' or
                                        data[33] != '30' or data[34] != '30' or data[35] != '30' or data[36] != '30' or data[37] != '30' or data[38] != '30' or data[39] != '30' or data[40] != '30'):
                                    print(
                                        "El DATA2 está conformado por valores diferentes a 0x30; no es lo que se esperaba. Se procede a descartar la trama de datos.")
                                else:
                                    if (data[9] != '30' or data[10] != '30' or data[11] != '30' or data[12] != '30'):
                                        print(
                                            "El número de pasajeros que han subido a la unidad sobrepasa la cantidad de 65535 personas. Se procede a descartar la trama de datos.")
                                    else:
                                        if (data[17] != '30' or data[18] != '30' or data[19] != '30' or data[20] != '30'):
                                            print(
                                                "El número de pasajeros que han subido a la unidad sobrepasa la cantidad de 65535 personas. Se procede a descartar la trama de datos.")
                                        else:
                                            DATA1UP_D = 0
                                            if data[13] > '39':
                                                DATA1UP_D += (int(data[13],16)-48-7)*4096
                                            else:
                                                DATA1UP_D += (int(data[13],16)-48)*4096
                                            if data[14] > '39':
                                                DATA1UP_D += (int(data[14],16)-48-7)*256
                                            else:
                                                DATA1UP_D += (int(data[14],16)-48)*256
                                            if data[15] > '39':
                                                DATA1UP_D += (int(data[15],16)-48-7)*16
                                            else:
                                                DATA1UP_D += (int(data[15],16)-48)*16
                                            if data[16] > '39':
                                                DATA1UP_D += int(data[16],16)-48-7
                                            else:
                                                DATA1UP_D += int(data[16],16)-48
                                                DATA1DW_D = 0
                                            if data[21] > '39':
                                                DATA1DW_D += (int(data[21],16)-48-7)*4096
                                            else:
                                                DATA1DW_D += (int(data[21],16)-48)*4096
                                            if data[22] > '39':
                                                DATA1DW_D += (int(data[22],16)-48-7)*256
                                            else:
                                                DATA1DW_D += (int(data[22],16)-48)*256
                                            if data[23] > '39':
                                                DATA1DW_D += (int(data[23],16)-48-7)*16
                                            else:
                                                DATA1DW_D += (int(data[23],16)-48)*16
                                            if data[24] > '39':
                                                DATA1DW_D += int(data[24],16)-48-7
                                            else:
                                                DATA1DW_D += int(data[24],16)-48


            ### DATOS Cuenta Personas ###
            datos_db = obtener_cuentap_delantero_ultimo()

            if datos_db is None:
                # guardar datos sin comparar ya que es el primer registro
                guardar_cuentap_delantero(folio_viaje,21000, fecha, subida, bajada,"","","")
            
            else:

                subida_anterior = datos_db[4]
                bajada_anterior = datos_db[5]
                
                subida = DATA1UP_D
                bajada = DATA1DW_D

                if subida_anterior != subida or bajada_anterior != bajada:
                    print("Acaba de cambiar los datos del cuenta personas: ", "SUB-A: ", subida_anterior, ", SUB: ", subida, ", BAJ-A: ", bajada_anterior, ", BAJ: ", bajada)
                    guardar_cuentap_delantero(folio_viaje,21000, fecha, subida, bajada,"22.1397","-101.0327","")
        
            tm.sleep(1)
        except Exception as e:
            print("Error en el hilo de cuenta personas: "+str(e))
            print(traceback.print_exc())
        
    def run(self):
        
        if destination == "TCP":
            self.run_send_data_tcp()
        elif destination == "INTERNET":
            self.run_send_data_internet()

        while True:
            
            print("\033[;36m"+"Dentro del hilo del cuenta personas")
            
            try:
                self.revisar_cuentapersonas()
                
            except Exception as e:
                print(f'Error en la conexión a Azure: ' + str(e))
                print(traceback.print_exc())
                
def actualizar_fecha_hora():
    
    try:
        # Especifica el servidor NTP al que te quieres conectar
        ntp_server = 'pool.ntp.org'

        # Conecta con el servidor NTP
        cliente_ntp = ntplib.NTPClient()
        respuesta_ntp = cliente_ntp.request(ntp_server)

        # Obtiene la fecha y hora del servidor NTP
        fecha_hora_servidor = datetime.fromtimestamp(respuesta_ntp.tx_time)

        # Formatea la fecha y hora
        formatted_date_time = fecha_hora_servidor.strftime("%Y-%m-%d %H:%M:%S")

        # Ejecuta el comando para actualizar la fecha y hora del sistema
        command = f"sudo date -s '{formatted_date_time}'"
        subprocess.call(command, shell=True)

        print(f"Fecha y hora actualizadas a: {formatted_date_time}")
        return True
    except Exception as e:
        print("No se pudo actualizar la hora del sistema")
        print(traceback.format_exc())
        return False
            
if __name__ == '__main__':
    
    if destination == "TCP":
        
        modem.reiniciar_configuracion_quectel()
        
        while True:
            if actualizar_hora.actualizar_hora():
                break
            print("################################################")
            tm.sleep(2)
        
    elif destination == "INTERNET":
        
        while True:
            done_date_hour = actualizar_fecha_hora()
            if done_date_hour:
                break
    
    cp = CuentaPersonas()
    cp.run()