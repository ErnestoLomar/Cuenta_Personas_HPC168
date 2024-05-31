import RPi.GPIO as GPIO
import serial
import time
import subprocess
import logging
from PyQt5.QtWidgets import QMessageBox
import os
import sys

direccion_actual = os.getcwd().replace("\\", "/")
direccion_utils = direccion_actual + "/CP/utils/"

sys.path.insert(1, f'{direccion_utils}')

import variables_globales

#Librerias propias
#   from asistencia import VentanaAsistencia

#Variables globales de comandos AT
EncenderGPS = "AT+QGPS=1"+"\r\n"
ApagarGPS = "AT+QGPSEND"+"\r\n"
Coordenadas = "AT+QGPSLOC=2"+"\r\n"
AT = "AT"+"\r\n"

#Variables globales
Latitud = ""
Longitud = ""
Hora = ""
Fecha = ""
Vel = ""
errores = ['ErIn', 'TrEm', 'ErTr', 'EmEr']

try:
    ser = serial.Serial('/dev/S0', 115200, timeout=1)
except Exception as e:
    print("\x1b[1;31;47m"+"comand.py, linea 48, Error al abrir el puerto serial: "+str(e)+'\033[0;m')
    logging.info(e)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(31, GPIO.OUT)
class Principal_Modem:

    global ser
    global Obtener_Coordenadas
    global Tam

    global Comunicacion_Minicom

    def Comunicacion_Minicom():
        try:
            ser.flushInput()
            ser.flushOutput()
            global Latitud, Longitud, Hora, Fecha, Vel
            comando = Coordenadas
            ser.write(comando.encode())
            ser.readline()
            Aux = ser.readline()
            Tam = len(Aux.decode())
            if Tam > 27:
                Cortada = Aux.decode()
                aux1 = Cortada.split(",")
                Hora = aux1[0].split(" ")
                Fecha = aux1[9]
                Vel = aux1[7]
                Latitud = aux1[1]
                Longitud = aux1[2]
                return {
                    "fecha": Fecha,
                    "hora": Hora,
                    "longitud": Longitud,
                    "latitud": Latitud,
                    "velocidad": Vel
                }
            else:
                #print("\x1b[1;33m"+"Ha ocurrido un el error" + Aux.decode() + "Se reintentara recibir datos del GPS")
                return {
                    "error": Aux.decode(),
                }
        except Exception as e:
            print("\x1b[1;31;47m"+"comand.py, linea 123, Error al enviar el comando: "+str(e)+'\033[0;m')
            logging.info(e)
            return {
                "error": e
            }

    def conex_3g(self):
        try:
            ser.flushInput()
            ser.flushOutput()
            res_conex_3g = self.do_command("AT+QINISTAT")
            return res_conex_3g.decode()
        except Exception as e:
            print("\x1b[1;31;47m"+"comand.py, linea 144: "+str(e)+'\033[0;m')
            logging.info(e)

    def signal_3g(self):
        try:
            comando = self.do_command("AT+CSQ").decode()
            if(not comando.startswith("+CSQ: ")):
                return -1
            comando = comando.replace("+CSQ: ", "")
            comando = comando.rstrip("\r\n")
            comando = comando[:-3]
            respuesta = float(comando)
            return respuesta
        except Exception as e:
            print("\x1b[1;31;47m"+"comand.py, linea 157: "+str(e)+'\033[0;m')
            logging.info(e)

    def abrir_puerto(self):
        try:
            time.sleep(0.0001)
            ser.flushInput()
            ser.flushOutput()
            time.sleep(0.0001)
            # variables de prueba
            tcp = "\"TCP\""
            # identifica el envio por tcp
            ip = "\"20.106.77.209\""
            # ip publica o URL del servidor
            #print("qi open")
            # comando at, formato de envio, direciion ip o url, puerto del servidor, puerto por defecto del quectel, parametro de envio por push
            comando = "AT+QIOPEN=1,0,"+tcp+","+ip+",8170,0,1\r\n"
            ser.write(comando.encode())
            print(ser.readline())
            Aux = ser.readline()
            print(Aux.decode())
            ser.readline()
            ser.readline()
        except Exception as e:
            print("\x1b[1;31;47m"+"comand.py, linea 180: "+str(e)+'\033[0;m')
            logging.info(e)
            
    def reconectar_gps(self):
        print("#####################################")
        print(ser.readline())
        print(ser.readline())
        print("Procedemos a iniciar sesión del GPS")
        ser.flushInput()
        ser.flushOutput()
        comando = "AT+QGPS=1\r\n"
        ser.readline()
        ser.write(comando.encode())
        print(ser.readline())
        time.sleep(2)
        respuesta = ser.readline()
        print("Respuesta: "+str(respuesta))
        respuesta = ser.readline()
        print("Respuesta: "+str(respuesta))
        respuesta = ser.readline()
        print("Respuesta: "+str(respuesta))
        print("#####################################")
        
        ser.flushInput()
        ser.flushOutput()
        comando = "AT+QGPS=1\r\n"
        ser.readline()
        ser.write(comando.encode())
        print(ser.readline())
        time.sleep(2)
        respuesta = ser.readline()
        print("Respuesta: "+str(respuesta))
        respuesta = ser.readline()
        print("Respuesta: "+str(respuesta))
        respuesta = ser.readline()
        print("Respuesta: "+str(respuesta))
        print("#####################################")

    def mandar_datos(self, Trama):
        try:
            if int(variables_globales.signal) > 2:
                time.sleep(0.0001)
                
                ser.flushInput()
                ser.flushOutput()
                
                byte = len(Trama)
                comando = "AT+QISEND=0,"+str(byte)+"\r\n"
                ser.write(comando.encode())
                
                i = 0
                j = 0
                
                while True:
                    i = i+1
                    Aux = ser.readline()
                    
                    if "\\x" not in str(Aux):
                        resultado = Aux.decode()
                        
                        if '>' in resultado:
                            time.sleep(0.0001)
                            
                            ser.flushInput()
                            ser.flushOutput()
                            
                            ser.write(Trama.encode())
                            
                            while True:
                                Aux = ser.readline()
                                
                                if "\\x" not in str(Aux):
                                    resultado = Aux.decode()
                                    
                                    if 'OK' in resultado:
                                        print("\x1b[1;32m"+"Se envio correctamente el dato con SEND OK")
                                        print("\x1b[1;32m"+str(Aux.decode()))
                                        break
                                    elif 'ERROR' in resultado or 'FAIL' in resultado:
                                        print("\x1b[1;33m"+"La trama no se pudo enviar: "+str(resultado))
                                        return {
                                            "enviado": False
                                        }
                                else:
                                    print("Existen datos basura en la lectura del serial: ", Aux)
                                    
                                if j == 10:
                                    return {
                                        "enviado": False
                                    }
                                    
                                j = j+1
                            break
                        elif 'ERROR' in resultado or i == 10:
                            print("\x1b[1;33m"+"Error al ejecutar el comando AT+QISEND")
                            print("\x1b[1;33m"+str(Aux.decode()))
                            return {
                                "enviado": False
                            }
                    elif i == 10:
                        print("\x1b[1;33m"+"Se recibe basura en el serial, no se envía el dato")
                        return {
                            "enviado": False
                        }
                    else:
                        print("Existen datos basura en la lectura del serial: ", Aux)

                if Trama == "quit":
                    #variables_globales.conexion_servidor = "SI"
                    return {
                        "enviado": True
                    }
                # recibir datos del servidor
                time.sleep(0.0001)
                ser.flushInput()
                ser.flushOutput()
                #comando = "AT+QIRD=0,300\r\n"
                #ser.write(comando.encode())
                i = 0
                logging.info("Esperando respuesta del servidor...")
                print("\x1b[1;32m"+"Esperando respuesta del servidor...")
                
                while True:
                    Aux = ser.readline()
                    if "\\x" not in str(Aux):
                        resultado = Aux.decode()
                        logging.info(resultado)
                        print("\x1b[1;32m"+"Leyendo: "+str(resultado))
                        if 'QIURC:' in resultado or 'RC' in resultado or 'IURC' in resultado or "recv" in resultado:
                            pass
                        else:
                            if Aux != b'\r\n' and Aux != b'':
                                if any(error in resultado for error in errores):
                                    return {"enviado": False}
                                elif "SKT" in resultado:
                                    print("\x1b[1;32m"+"Dato registrado en el servidor")
                                    print("\x1b[1;32m"+"Respondio: "+resultado)
                                    logging.info("El servidor recibio el dato")
                                    logging.info("El servidor respondio: "+resultado)
                                    return {
                                        "enviado": True,
                                        "accion": resultado
                                    }
                    if i == 20:
                        return {
                            "enviado": False
                        }
                    i = i+1
            else:
                print("\x1b[1;33m"+"#############################################")
                print("\x1b[1;33m"+"No hay suficiante señal celular para enviar datos, pero se hara otro intento en 10 segundos")
                print("\x1b[1;33m"+"#############################################")
                time.sleep(10)
                if int(variables_globales.signal) > 2:
                    print("\x1b[1;32m"+"#############################################")
                    print("\x1b[1;32m"+"Se recupero la señal despues de 10 segundos")
                    print("\x1b[1;32m"+"#############################################")
                    self.mandar_datos(Trama)
                else:
                    print("\x1b[1;33m"+"#############################################")
                    print("\x1b[1;33m"+"No hay suficiante señal celular para enviar datos, se acumuló otro intento")
                    print("\x1b[1;33m"+"#############################################")
                    return {
                        "enviado": False
                    }
        except Exception as e:
            print("\x1b[1;31;47m"+"comand.py, linea 238: "+str(e)+'\033[0;m')
            logging.info(e)
            return {
                "enviado": False
            }

    def cerrar_socket(self):
        try:
            self.mandar_datos('quit')
            time.sleep(0.001)
            comando = "AT+QICLOSE=1\r\n"  # cierra conexion con el servidor - Modificado de "AT+QICLOSE=0\r\n" a "AT+QICLOSE=1\r\n"
            ser.write(comando.encode())
            print(ser.readline())
            Aux = ser.readline()
            print(Aux.decode())
        except Exception as e:
            print("comand.py, linea 251: "+str(e))
            logging.info(e)

    def reiniciar_QUEQTEL(self):
        try:
            print("\x1b[1;32m"+"#####################################")
            ser.flushInput()
            ser.flushOutput()
            comando = "AT+QPOWD\r\n"
            ser.readline()
            ser.write(comando.encode())
            time.sleep(1)
            print(ser.readline())
            respuesta = ser.readline()
            if 'OK' in respuesta.decode():
                i = 0
                while True:
                    res = ser.readline()
                    i = i + 1
                    time.sleep(1)
                    if 'RDY' in res.decode():
                        break
                    elif i == 20:
                        #Aqui ira la parte donde se reiniciara el modulo por GPIO
                        GPIO.output(31, True)
                        time.sleep(1)
                        GPIO.output(31, False)
                        i = 0
                        while True:
                            res = ser.readline()
                            i = i + 1
                            time.sleep(1)
                            if 'RDY' in res.decode():
                                break
                            elif i == 20:
                                logging.info('Reiniciando la RASPBERRY')
                                print("\x1b[1;31;47m"+"Reiniciando la RASPBERRY......"+'\033[0;m')
                                resultado = "REINICIANDO DISPOSITIVO"
                                mensaje = QMessageBox()
                                mensaje.setIcon(QMessageBox.Info)
                                mensaje.about(self, "AVISO", f"AVISO: {resultado}")
                                time.sleep(5)
                                subprocess.run("sudo reboot", shell=True)
                        break
                ser.flushInput()
                ser.flushOutput()
            else:
                print("\x1b[1;31;47m"+"No se pudo inicializar AT+QPOWD"+'\033[0;m')
                print(respuesta)
                time.sleep(2)
            print("#####################################")
        except Exception as e:
            print("\x1b[1;31;47m"+"comand.py, linea 311: "+str(e)+'\033[0;m')
            logging.info(e)

    def inicializar_configuraciones_quectel(self):
        ###########################
        ######   Ernesto   ########
        ###########################
        try:
            print("\x1b[1;32m"+"#####################################")
            ser.readline()
            ser.readline()
            ser.flushInput()
            ser.flushOutput()
            comando = "AT+CPIN?\r\n"
            ser.write(comando.encode())
            i = 0
            while True:    
                respuesta = ser.readline()
                print(respuesta.decode())
                if 'READY' in respuesta.decode() or 'OK' in respuesta.decode():
                    ser.flushInput()
                    ser.flushOutput()
                    break
                elif i == 5 or 'ERROR' in respuesta.decode():
                    print("\x1b[1;33m"+"No se pudo inicializar AT+CPIN")
                    time.sleep(1)
                    break
                i = i + 1
                time.sleep(.5)
            print("\x1b[1;32m"+"#####################################\n")
            
            comando = "AT+CREG?\r\n"
            ser.readline()
            ser.write(comando.encode())
            i = 0
            while True:    
                respuesta = ser.readline()
                print(respuesta.decode())
                if ',1' in respuesta.decode() or ',5' in respuesta.decode() or 'OK' in respuesta.decode():
                    ser.flushInput()
                    ser.flushOutput()
                    break
                elif i == 5 or 'ERROR' in respuesta.decode():
                    print("No se pudo inicializar AT+CREG?")
                    time.sleep(.5)
                    break
                i = i + 1
                time.sleep(1)
            print("\x1b[1;32m"+"#####################################\n")
            
            ser.flushInput()
            ser.flushOutput()
            comando = "AT+CGREG?\r\n"
            ser.readline()
            ser.write(comando.encode())
            i = 0
            while True:    
                respuesta = ser.readline()
                print(respuesta.decode())
                if ',1' in respuesta.decode() or ',5' in respuesta.decode() or 'OK' in respuesta.decode():
                    ser.flushInput()
                    ser.flushOutput()
                    break
                elif i == 5 or 'ERROR' in respuesta.decode():
                    print("\x1b[1;33m"+"No se pudo inicializar AT+CGREG?")
                    time.sleep(.5)
                    break
                i = i + 1
                time.sleep(1)
            print("\x1b[1;32m"+"#####################################\n")

            ser.flushInput()
            ser.flushOutput()
            comando = "AT+QICSGP=1,1,\"internet.itelcel.com\",\"\",\"\",1\r\n"
            ser.readline()
            ser.write(comando.encode())
            i = 0
            while True:    
                respuesta = ser.readline()
                print(respuesta.decode())
                if 'OK' in respuesta.decode():
                    ser.flushInput()
                    ser.flushOutput()
                    break
                elif i == 10 or 'ERROR' in respuesta.decode():
                    print("\x1b[1;33m"+"No se pudo inicializar AT+QICSGP")
                    time.sleep(1)
                    break
                i = i + 1
                time.sleep(1)
            print("\x1b[1;32m"+"#####################################\n")

            ser.flushInput()
            ser.flushOutput()
            comando = "AT+QIACT=1\r\n"
            ser.readline()
            ser.write(comando.encode())
            i = 0
            while True:
                respuesta = ser.readline()
                print(respuesta.decode())
                if 'OK' in respuesta.decode():
                    ser.flushInput()
                    ser.flushOutput()
                    break
                elif i == 10 or 'ERROR' in respuesta.decode():
                    print("\x1b[1;33m"+"No se pudo inicializar AT+QIACT=1")
                    time.sleep(1)
                    break
                i = i + 1
                time.sleep(1)
            print("\x1b[1;32m"+"#####################################")
        except Exception as e:
            print("\x1b[1;31;47m"+"FTP.py, linea 171, Error al inicializar SIM: "+str(e)+'\033[0;m')
            logging.info(e)
        ###########################
        ###########################

    def reiniciar_configuracion_quectel(self):
        try:
            time.sleep(0.001)
            comando = "AT+QIDEACT=1\r\n"
            ser.write(comando.encode())
            print(ser.readline())
            Aux = ser.readline()
            print(Aux.decode())
            self.inicializar_configuraciones_quectel()
        except Exception as e:
            print("\x1b[1;31;47m"+"comand.py, linea 251: "+str(e)+'\033[0;m')
            logging.info(e)