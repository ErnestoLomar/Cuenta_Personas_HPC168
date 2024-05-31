import traceback
from PyQt5.QtCore import QObject, pyqtSignal
import os
from PIL import Image
import numpy as np
import sys
from time import strftime
import time
from uuid import uuid4
from ftplib import FTP
import requests
import base64
import urllib.parse

direccion_actual = os.getcwd().replace("\\", "/")
direccion_db = direccion_actual + "/CP/db/"

sys.path.insert(1, f'{direccion_db}')

from obstruccion_db import guardar_incidencia

# Credenciales FTP
cuenta_azure = "account"
usuario_FTP_azure = "Abraham"
contra_FTP_azure = "May0admin2022*"
host_FTP_azure = "20.106.77.209"
ubicacion = "/incidenciasCP/"

class RevisarObst(QObject):
    
    try:
        finished = pyqtSignal()
        progress = pyqtSignal(str)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        
    def __init__(self):
        super().__init__()
        
    def is_camera_obstructed(self, frame, threshold=800):
        """
        Determina si la cámara está obstruida calculando la varianza de la imagen.
        
        :param frame: El cuadro de video actual.
        :param threshold: El umbral de varianza por debajo del cual se considera que la cámara está obstruida.
        :return: True si la cámara está obstruida, False en caso contrario.
        """
        # Convertir el cuadro a escala de grises
        gray = frame.convert('L')
        
        # Convertir la imagen a un array de numpy
        gray_array = np.array(gray)
        
        # Calcular la varianza de la imagen
        variance = np.var(gray_array)
        
        #print("Varianza: ", variance)
        #print("Threshold: ", threshold)
        
        # Si la varianza es menor que el umbral, la cámara está obstruida
        if variance < threshold:
            return True
        else:
            return False
        
    def imagen_a_base64(self,ruta_imagen):
        """
        Convierte una imagen en su representación en base64.
        
        :param ruta_imagen: La ruta de la imagen que se desea convertir.
        :return: La representación en base64 de la imagen como una cadena de texto.
        """
        with open(ruta_imagen, 'rb') as imagen:
            imagen_base64 = base64.b64encode(imagen.read()).decode('utf-8')
        return imagen_base64
        
    def capture_frame(self):
        """
        Captura un cuadro de la cámara y lo devuelve como una imagen PIL.
        """
        # Dependiendo del entorno, puedes usar diferentes formas de capturar la imagen
        # Por ejemplo, aquí se usa fswebcam para capturar una imagen desde la cámara
        os.system("fswebcam -r 640x480 --jpeg 85 webcam.jpg")
        frame = Image.open("webcam.jpg")
        return frame
            
    def upload_to_ftp(self, filename):
        
        ftp = FTP(host_FTP_azure)
        ftp.login(user=usuario_FTP_azure, passwd=contra_FTP_azure)
        
        # Cambiar a la ubicación especificada
        ftp.cwd(ubicacion)
        
        with open(filename, 'rb') as file:
            ftp.storbinary(f'STOR {filename}', file)
        
        ftp.quit()

    def enviar_imagen(self, imagen):
        url = "https://api.ultramsg.com/instance86058/messages/image"

        token = "9i54mzthuwqrnksu"
        to = "120363046588394028@g.us"  
        image_path = "/home/pi/" + str(imagen)
        caption = "⚠️Imagen Capturada⚠️\n *Cuenta Personas Obstruido* "
        
        if os.path.exists(image_path):
            
            print("Si existe la imagen")
                
            imagen_base64 = self.imagen_a_base64(imagen)
            img_bas64 = urllib.parse.quote_plus(imagen_base64)
            #print(img_bas64)

            payload =f"token={token}&to={to}&image={img_bas64}&caption={caption}"
            payload = payload.encode('utf8').decode('iso-8859-1')
            headers = {'content-type': 'application/x-www-form-urlencoded'}

            response = requests.request("POST", url, data=payload, headers=headers)

            print("WHATS: ", response.text)
        else:
            print("No existe la imagen: ", image_path)
        
        
    def run(self):
        
        while True:
            # Capturar un cuadro del video
            frame = self.capture_frame()
            
            # Verificar si la cámara está obstruida
            if self.is_camera_obstructed(frame):
                print("Cámara obstruida")
                
                folio_viaje = "NO"
                if folio_viaje == 'NO':
                    fecha = time.strftime("%Y%m%d")
                    folio_viaje = fecha + '9999'
                fecha = time.strftime("%Y%m%d%H%M%S")
                
                # Generar un nombre de archivo único
                unique_id = uuid4().hex
                img_filename = f"{unique_id[24:]}.png"
                
                # Guardar el frame como una imagen
                frame.save(img_filename)
                
                # Subir la imagen al servidor FTP (Implementar esta función según sea necesario)
                self.upload_to_ftp(img_filename)
                
                # Guardar la incidencia con el nombre de la imagen (Implementar esta función según sea necesario)
                guardar_incidencia(folio_viaje, 22000, fecha, "22.1397", "-101.0327", 0.0, img_filename)

                # Enviar imagen a WhatsApp (Implementar esta función según sea necesario)
                self.enviar_imagen(img_filename)

            # Esperar un poco antes de capturar el siguiente cuadro
            #time.sleep(1)