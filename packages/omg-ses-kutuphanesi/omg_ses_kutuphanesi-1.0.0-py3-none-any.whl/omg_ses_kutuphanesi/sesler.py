import pygame
import time

def omg_orijinal():
   pygame.init()
   pygame.mixer.init()
   ses_dosyasi = "ses.wav"
   pygame.mixer.music.load(ses_dosyasi)
   pygame.mixer.music.play()  
   time.sleep(4)
   
def omg_kesik():
   pygame.init()
   pygame.mixer.init()
   ses_dosyasi = "omg-duz.wav"
   pygame.mixer.music.load(ses_dosyasi)
   pygame.mixer.music.play()  
   time.sleep(7)
   
def omg_yankili():
   pygame.init()
   pygame.mixer.init()
   ses_dosyasi = "omg-yankılı.wav"
   pygame.mixer.music.load(ses_dosyasi)
   pygame.mixer.music.play()  
   time.sleep(10)