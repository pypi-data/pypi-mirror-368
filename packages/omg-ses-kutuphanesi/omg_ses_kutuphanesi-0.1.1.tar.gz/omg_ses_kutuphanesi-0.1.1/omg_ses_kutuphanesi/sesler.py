import pygame

def omg_kesik():
   pygame.init()
   pygame.mixer.init()
   ses_dosyasi = "ses.wav"
   pygame.mixer.music.load(ses_dosyasi)
   pygame.mixer.music.play()   
 

def omg_orijinal():
   pygame.init()
   pygame.mixer.init()
   ses_dosyasi = "omg-duz.wav"
   pygame.mixer.music.load(ses_dosyasi)
   pygame.mixer.music.play()  
