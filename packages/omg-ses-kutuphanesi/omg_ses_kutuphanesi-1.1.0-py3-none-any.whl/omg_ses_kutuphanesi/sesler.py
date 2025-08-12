import os
import pygame
import time

base_path = os.path.dirname(__file__)

def omg_orijinal():
   pygame.init()
   pygame.mixer.init()
   ses_dosyasi = os.path.join(base_path, "ses.wav")
   pygame.mixer.music.load(ses_dosyasi)
   pygame.mixer.music.play()  
   time.sleep(4)
   
def omg_kesik():
   pygame.init()
   pygame.mixer.init()
   ses_dosyasi = os.path.join(base_path, "omg-duz.wav")
   pygame.mixer.music.load(ses_dosyasi)
   pygame.mixer.music.play()  
   time.sleep(7)
   
def omg_yankili():
   pygame.init()
   pygame.mixer.init()
   ses_dosyasi = os.path.join(base_path, "omg-yankılı.wav")
   pygame.mixer.music.load(ses_dosyasi)
   pygame.mixer.music.play()  
   time.sleep(10)
