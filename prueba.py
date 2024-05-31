from PIL import Image
import numpy as np
import time
from uuid import uuid4
import os

def is_camera_obstructed(frame, threshold=800):
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

def capture_frame():
    """
    Captura un cuadro de la cámara y lo devuelve como una imagen PIL.
    """
    # Dependiendo del entorno, puedes usar diferentes formas de capturar la imagen
    # Por ejemplo, aquí se usa fswebcam para capturar una imagen desde la cámara
    os.system("fswebcam -r 640x480 --jpeg 85 -D 1 webcam.jpg")
    frame = Image.open("webcam.jpg")
    return frame

def run():
    while True:
        # Capturar un cuadro del video
        frame = capture_frame()
        
        # Verificar si la cámara está obstruida
        if is_camera_obstructed(frame):
            print("Cámara obstruida")
            
            folio_viaje = "NO"
            if folio_viaje == 'NO':
                fecha = time.strftime("%Y%m%d")
                folio_viaje = fecha + '9999'
            fecha = time.strftime("%Y%m%d%H%M%S")
            
            # Generar un nombre de archivo único
            unique_id = uuid4().hex
            img_filename = f"{unique_id[17:]}.png"
            
            # Guardar el frame como una imagen
            frame.save(img_filename)
            
            # Subir la imagen al servidor FTP (Implementar esta función según sea necesario)
            upload_to_ftp(img_filename)
            
            # Guardar la incidencia con el nombre de la imagen (Implementar esta función según sea necesario)
            guardar_incidencia(folio_viaje, 21000, fecha, "22.1397", "-101.0327", 0.0, img_filename)

            # Enviar imagen a WhatsApp (Implementar esta función según sea necesario)
            enviar_imagen(img_filename)

        # Esperar un poco antes de capturar el siguiente cuadro
        time.sleep(1)

def upload_to_ftp(filename):
    # Implementa la lógica para subir el archivo al servidor FTP
    pass

def guardar_incidencia(folio_viaje, code, fecha, lat, lon, value, img_filename):
    # Implementa la lógica para guardar la incidencia
    pass

def enviar_imagen(img_filename):
    # Implementa la lógica para enviar la imagen a WhatsApp
    pass

if __name__ == "__main__":
    run()