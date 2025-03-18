import cv2 as cv
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

slika = None
tocki = []
rezem = False

def zmanjsaj_sliko(slika, sirina, visina):
    '''Zmanjšaj sliko na velikost sirina x visina.'''
    pass

def izrezi_del_slike(slika, x, y, sirina, visina):
    return slika[y:y+visina, x:x+sirina]

def obdelaj_sliko_s_skatlami(slika, sirina_skatle, visina_skatle, barva_koze) -> list:
    visina, sirina, _ = slika.shape
    stev_vrstic = (visina // visina_skatle)
    stev_stolpcev = (sirina // sirina_skatle)
    rez = [[0 for _ in range(stev_stolpcev)] for _ in range(stev_vrstic)]
    for j in range(0, stev_vrstic):
        for i in range(0, stev_stolpcev):
            rez[j][i] = prestej_piklse_z_barvo_koze(izrezi_del_slike(slika, i*sirina_skatle, j*visina_skatle, sirina_skatle, visina_skatle), barva_koze)

            if rez[j][i] > 48:
                row = j * visina_skatle
                col = i * sirina_skatle

                cv.rectangle(
                    slika,
                    (col, row),
                    (col + sirina_skatle, row + visina_skatle),
                    (0, 0, 255),
                    2
                )
    '''Sprehodi se skozi sliko v velikosti škatle (sirina_skatle x visina_skatle) in izračunaj število pikslov kože v vsaki škatli.
    Škatle se ne smejo prekrivati!
    Vrne seznam škatel, s številom pikslov kože.
    Primer: Če je v sliki 25 škatel, kjer je v vsaki vrstici 5 škatel, naj bo seznam oblike
      [[1,0,0,1,1],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[1,0,0,0,1]]. 
      V tem primeru je v prvi škatli 1 piksel kože, v drugi 0, v tretji 0, v četrti 1 in v peti 1.'''
    return rez

def prestej_piklse_z_barvo_koze(slika, barva_koze) -> int:
    mask = cv.inRange(slika, barva_koze[0], barva_koze[1])
    return np.count_nonzero(mask == 255)

def doloci_barvo_koze(slika,levo_zgoraj,desno_spodaj) -> tuple:
    x1, y1 = levo_zgoraj
    x2, y2 = desno_spodaj

    obmocje = izrezi_del_slike(slika, x1, y1, x2, y2)

    povp_barva = np.mean(obmocje, axis=(0, 1))

    povp_barva = tuple(map(int, povp_barva))

    barva_nizka = np.array([max(povp_barva[0] - 40, 0), max(povp_barva[1] - 40, 0), max(povp_barva[2] - 40, 0)],
                          dtype=np.uint8)
    barva_visoka = np.array([min(povp_barva[0] + 40, 255), min(povp_barva[1] + 40, 255), min(povp_barva[2] + 40, 255)],
                          dtype=np.uint8)

    '''Ta funkcija se kliče zgolj 1x na prvi sliki iz kamere. 
    Vrne barvo kože v območju ki ga definira oklepajoča škatla (levo_zgoraj, desno_spodaj).
      Način izračuna je prepuščen vaši domišljiji.'''
    return (barva_nizka, barva_visoka)

def klikni_in_rezi(dogodek, x, y, zastavice, param):
    global tocki, rezem

    if dogodek == cv.EVENT_LBUTTONDOWN:
        tocki = [(x, y)]
        rezem = True

    elif dogodek == cv.EVENT_LBUTTONUP:
        tocki.append((x, y))
        rezem = False

        cv.rectangle(slika, tocki[0], tocki[1], (0, 255, 0), 2)
        cv.imshow("Slika", slika)

if __name__ == '__main__':
    kamera = cv.VideoCapture(0)
    ret, slika = kamera.read()

    visina_skatle = slika.shape[0] // 64
    sirina_skatle = slika.shape[1] // 64

    #barva1 = (186, 204, 246)
    #barva2 = (81, 81, 214)
    #barva_koze = np.array([barva2, barva1], dtype=np.uint8).reshape(2, 1, 3)
    # Preverimo, če je slika pravilno naložena
    if ret:
        cv.namedWindow("Slika")
        cv.setMouseCallback("Slika", klikni_in_rezi)

        while True:
            cv.imshow("Slika", slika)
            tipka = cv.waitKey(1) & 0xFF

            if tipka == ord("c"):
                break

        if len(tocki) == 2:
            levo_zgoraj = tocki[0]
            desno_spodaj = tocki[1]

            barva_koze = doloci_barvo_koze(slika, levo_zgoraj, desno_spodaj)

        else:
            print("Napaka")
            exit()

        rez = obdelaj_sliko_s_skatlami(slika, sirina_skatle, visina_skatle, barva_koze)
        for el0 in rez:
            print("")
            for el in el0:
                print(el, ", ", end="")
        cv.imshow('Slika', slika)
        # Počakamo na pritisk tipke
        cv.waitKey(0)
        # Zapremo vsa okna
        kamera.release()
        cv.destroyAllWindows()

    #Pripravi kamero

    #Zajami prvo sliko iz kamere

    #Izračunamo barvo kože na prvi sliki

    #Zajemaj slike iz kamere in jih obdeluj     
    
    #Označi območja (škatle), kjer se nahaja obraz (kako je prepuščeno vaši domišljiji)
        #Vprašanje 1: Kako iz števila pikslov iz vsake škatle določiti celotno območje obraza (Floodfill)?
        #Vprašanje 2: Kako prešteti število ljudi?

        #Kako velikost prebirne škatle vpliva na hitrost algoritma in točnost detekcije? Poigrajte se s parametroma velikost_skatle
        #in ne pozabite, da ni nujno da je škatla kvadratna.
    pass

#         cv.rectangle(image, tocki[0], tocki[1], (0, 255, 0), 2)
#         cv.imshow("Image", image)