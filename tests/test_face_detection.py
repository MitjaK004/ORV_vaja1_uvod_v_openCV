import pytest
import cv2
import numpy as np
from src.face_detection import (
    zmanjsaj_sliko,
    izrezi_del_slike,
    prestej_piklse_z_barvo_koze,
    doloci_barvo_koze,
    obdelaj_sliko_s_skatlami
)

@pytest.fixture
def testna_slika():
    # Ustvarimo testno sliko z različnimi barvami
    slika = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Dodamo območje "kože" (oranžne barve)
    slika[20:40, 30:70] = [0, 100, 200]  # BGR format
    
    # Dodamo nekaj šuma
    slika[60:80, 10:90] = np.random.randint(0, 255, (20, 80, 3), dtype=np.uint8)
    
    return slika

@pytest.fixture
def barva_koze():
    # Definiramo območje barve kože
    return (np.array([0, 90, 190]), np.array([10, 110, 210]))

def test_zmanjsaj_sliko(testna_slika):
    nova_slika = zmanjsaj_sliko(testna_slika, 50, 50)
    assert nova_slika.shape == (50, 50, 3)
    assert nova_slika.dtype == np.uint8

def test_izrezi_del_slike(testna_slika):
    izrez = izrezi_del_slike(testna_slika, 30, 20, 40, 20)
    assert izrez.shape == (20, 40, 3)
    # Preverimo, da smo res izrezali območje z "kožo"
    assert np.all(izrez[0, 0] == [0, 100, 200])

def test_prestej_piklse_z_barvo_koze(testna_slika, barva_koze):
    # Testno območje z znano količino "kože"
    obmocje_koze = testna_slika[20:40, 30:70]
    stevilo = prestej_piklse_z_barvo_koze(obmocje_koze, barva_koze)
    assert stevilo == 20 * 40  # Vse točke naj bi bile "koža"
    
    # Test na celotni sliki
    stevilo = prestej_piklse_z_barvo_koze(testna_slika, barva_koze)
    assert 20 * 40 <= stevilo <= 20 * 40 + 100  # Dovolimo nekaj šuma

def test_doloci_barvo_koze(testna_slika):
    # Testiramo na območju, ki vsebuje samo "kožo"
    barva = doloci_barvo_koze(testna_slika, (30, 20), (70, 40))
    
    # Preverimo, da so vrnjene barve v pričakovanem območju
    assert 0 <= barva[0][0] <= 10
    assert 90 <= barva[0][1] <= 110
    assert 190 <= barva[0][2] <= 210
    assert 0 <= barva[1][0] <= 10
    assert 90 <= barva[1][1] <= 110
    assert 190 <= barva[1][2] <= 210

def test_obdelaj_sliko_s_skatlami(testna_slika, barva_koze):
    rezultat = obdelaj_sliko_s_skatlami(testna_slika.copy(), 10, 10, barva_koze)
    
    # Preverimo obliko rezultata
    assert len(rezultat) == 10  # 100/10 = 10 vrstic
    assert len(rezultat[0]) == 10  # 100/10 = 10 stolpcev
    
    # Preverimo, da je območje z kožo zaznano
    # Koža je v vrsticah 2-4 (20-40px) in stolpcih 3-7 (30-70px)
    assert rezultat[2][3] > 0
    assert rezultat[3][5] > 0
    assert rezultat[4][6] > 0
    
    # Preverimo, da so nekožna območja približno 0
    assert rezultat[0][0] == 0
    assert rezultat[7][8] == 0

def test_obdelaj_sliko_s_skatlami_rectangles(testna_slika, barva_koze):
    # Naredimo kopijo, da lahko preverimo, če so pravokotniki narisani
    slika_kopija = testna_slika.copy()
    obdelaj_sliko_s_skatlami(slika_kopija, 10, 10, barva_koze)
    
    # Preverimo, da je vsaj en piksel rdeče barve (pravokotnik)
    assert np.any(slika_kopija[:, :, 2] == 255)  # Rdeči kanal
