import cv2 as cv
import numpy as np
from scipy import stats
from numpy.lib.stride_tricks import sliding_window_view

slika = None
tocki = []
rezem = False

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

            if rez[j][i] > int((stev_vrstic * stev_stolpcev) * 0.72):
                row = j * visina_skatle
                col = i * sirina_skatle

                cv.rectangle(
                    slika,
                    (col, row),
                    (col + sirina_skatle, row + visina_skatle),
                    (0, 0, 255),
                    2
                )
    return rez

def prestej_piklse_z_barvo_koze(slika, barva_koze) -> int:
    mask = cv.inRange(slika, barva_koze[0], barva_koze[1])
    return np.count_nonzero(mask == 255)

def doloci_barvo_koze(slika,levo_zgoraj,desno_spodaj) -> tuple:
    x1, y1 = levo_zgoraj
    x2, y2 = desno_spodaj

    obmocje = izrezi_del_slike(slika, x1+2, y1+2, x2-x1-3, y2-y1-3)

    for i in obmocje:
        print("")
        for j in i:
            print(j, end="")

    povp_barva = np.mean(obmocje, axis=(0, 1))
    std_odkl = np.std(obmocje, axis=(0, 1))
    modus = stats.mode(obmocje, axis=0).mode

    print("")
    print("povp_barva: ", povp_barva, ", std_odkl: ", std_odkl)
    print("modus: ", modus[0])

    bgr_tupli = [tuple(barva) for barva in obmocje]

    enolicne_barve, kolicine = np.unique(bgr_tupli, return_counts=True, axis=0)

    modus1 = enolicne_barve[np.argmax(kolicine)]

    toleranca = 0.1 * std_odkl

    barva_nizka = np.array([np.clip(povp_barva[0] - toleranca[0]), np.clip(povp_barva[1] - toleranca[1]), np.clip(povp_barva[2] - toleranca[2])],
                          dtype=np.uint8)
    barva_visoka = np.array([np.clip(povp_barva[0] + toleranca[0]), np.clip(povp_barva[1] + toleranca[1]), np.clip(povp_barva[2] + toleranca[2])],
                          dtype=np.uint8)

    print("barva_nizka: ", barva_nizka, ", barva visoka: ", barva_visoka)

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

def sledi_obrazu_v_realnem_casu(barva_koze, kamera, sirina_skatle, visina_skatle):
    while True:
        ret, slika = kamera.read()
        if not ret:
            break

        obdelaj_sliko_s_skatlami(slika, sirina_skatle, visina_skatle, barva_koze)

        cv.imshow("Slika", slika)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    kamera.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    kamera = cv.VideoCapture(0)
    ret, slika = kamera.read()

    visina_skatle = slika.shape[0] // 8
    sirina_skatle = slika.shape[1] // 8

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

        sledi_obrazu_v_realnem_casu(barva_koze, kamera, sirina_skatle, visina_skatle)

        cv.imshow('Slika', slika)
        cv.waitKey(0)
        kamera.release()
        cv.destroyAllWindows()
    pass

    #Pripravi kamero

    #Zajami prvo sliko iz kamere

    #Izračunamo barvo kože na prvi sliki

    #Zajemaj slike iz kamere in jih obdeluj     
    
    #Označi območja (škatle), kjer se nahaja obraz (kako je prepuščeno vaši domišljiji)
        #Vprašanje 1: Kako iz števila pikslov iz vsake škatle določiti celotno območje obraza (Floodfill)?
        #Vprašanje 2: Kako prešteti število ljudi?

        #Kako velikost prebirne škatle vpliva na hitrost algoritma in točnost detekcije? Poigrajte se s parametroma velikost_skatle
        #in ne pozabite, da ni nujno da je škatla kvadratna.

#         cv.rectangle(image, tocki[0], tocki[1], (0, 255, 0), 2)
#         cv.imshow("Image", image)