import keyboard
import mouse
from mouse import ButtonEvent, play, MoveEvent
import random
from skimage.metrics import structural_similarity as ssim
import clipboard

'''
keyboard.wait('w')
mouse_events = []
mouse.hook(mouse_events.append)

keyboard.wait('w')

mouse.unhook(mouse_events.append)

print(mouse_events)
'''


import cv2
import numpy as np
import pyautogui
import time
import matplotlib.pyplot as plt
import pickle
from MovementsRecorded import reloads, BuyActions1, BuyActions2, BuyActions3, TabOuiActions, SellActions1, SellActions2, SellActions3, AfterSellActions

global prix_data
global lots
global inventaire
global stock


# Fonction pour capturer une partie de l'écran
def capture_screen(region=None):
    screenshot = pyautogui.screenshot(region=region)
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    return screenshot


# Fonction pour détecter un objet à partir de plusieurs modèles
def detect_object(image, templates):
    gray_image = image
    best_match = None
    best_score = 0
    best_template_name = None

    for template_name, template in templates.items():
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(gray_image, template_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)

        if max_val > best_score:
            best_score = max_val
            best_match = template
            best_template_name = template_name

    return best_template_name if best_score >= 0.75 else None

def DiffImages(img1, img2):
    score, diff = ssim(img1, img2, full=True)
    if score > 0.99:
        return False
    return True
def GetPrix(prix_data):
    # Définir la région de l'écran à capturer (x, y, largeur, hauteur)
    regions = [
        [(968, 267, 8, 20), (976, 267, 8, 20), (984, 267, 9, 20), (994, 267, 8, 20), (1002, 267, 8, 20),
         (1010, 267, 8, 20)],
        [(968, 312, 8, 20), (976, 312, 8, 20), (984, 312, 9, 20), (994, 312, 8, 20), (1002, 312, 8, 20),
         (1010, 312, 8, 20)],
        [(968, 358, 8, 20), (976, 358, 8, 20), (984, 358, 9, 20), (994, 358, 8, 20), (1002, 358, 8, 20),
         (1010, 358, 8, 20)]
    ]
    nombre = ''
    nombres = []
    for i in range(len(regions)):
        for region in regions[i]:
            screen_image = capture_screen(region)

            # Détecter l'objet
            detected_object = detect_object(screen_image, templates)

            if detected_object:
                nombre += str(detected_object)
        if nombre != '':
            nombres.append(int(nombre))
        elif nombre == '' and prix_data != []:
            print(f'prix mal pris {i + 1}')
            nombres.append(prix_data[i-1][i])
        elif nombre == '' and prix_data == []:
            print(f'prix mal pris {i + 1}')
            nombres.append(0)
        nombre = ''
    return nombres

def MouseMovementsPlay(mouse_events):
    start_time = mouse_events[0].time
    for event in mouse_events:
        wait_time = event.time - start_time
        time.sleep(max(0, wait_time))
        start_time = event.time
        if isinstance(event, MoveEvent):
            mouse.move(event.x, event.y, absolute=True, duration=0)
        elif isinstance(event, ButtonEvent):
            if event.event_type == "down":
                mouse.press(button=event.button)
            elif event.event_type == "up":
                mouse.release(button=event.button)

def SellAction(prix_vente, lot):
    clipboard.copy(str(prix_vente))
    print(f"mise en vente de {int(inventaire['objet']/lots[lot])} lots à {prix_vente} kamas")
    if lot == '1':
        MouseMovementsPlay(random.choice(SellActions1))
    elif lot == '2':
        MouseMovementsPlay(random.choice(SellActions2))
    else:
        MouseMovementsPlay(random.choice(SellActions3))
    inventaire['objet'] -= lots[lot]
    time.sleep(0.7)
    screen_image = capture_screen((750,386,400,300))
    detected_object = detect_object(screen_image, tab_oui_temp)
    if detected_object:
        MouseMovementsPlay(random.choice(TabOuiActions))
    for i in range(int(inventaire['objet']/lots[lot])-1):
        inventaire['objet'] -= lots[lot]
        mouse.click()
        time.sleep(0.7)
        screen_image = capture_screen((750,386,400,300))
        detected_object = detect_object(screen_image, tab_oui_temp)
        if detected_object:
            MouseMovementsPlay(random.choice(TabOuiActions))
    inventaire['prix'] = 0
    MouseMovementsPlay(random.choice(AfterSellActions))


def BuyAction(prix_achat, iterations, lot, stock):
    if iterations > 0:
        NewPrice = []
        if lot == '1':
            MouseMovementsPlay(random.choice(BuyActions1))
        elif lot == '2':
            MouseMovementsPlay(random.choice(BuyActions2))
        elif lot == '3':
            MouseMovementsPlay(random.choice(BuyActions3))
        time.sleep(3)
        screen_image = capture_screen((750,386,400,300))
        detected_object = detect_object(screen_image, tab_oui_temp)
        if detected_object:
            MouseMovementsPlay(random.choice(TabOuiActions))
        time.sleep(1)
        Newstock = capture_screen((1248, 179, 59, 59))
        time.sleep(0.5)
        NewPrice = GetPrix(NewPrice)
        diff = DiffImages(stock, Newstock)
        if NewPrice[int(lot)-1] != 0 and NewPrice[int(lot)-1] <= prix_achat and diff:
            stock = Newstock
            inventaire['objet'] += lots[lot]
            inventaire['prix'] += NewPrice[int(lot)-1]
            print(f"Achat d'un lot de {lots[lot]} au prix de {NewPrice[int(lot)-1]}")
            BuyAction(NewPrice[int(lot)-1], iterations - 1, lot, stock)
        elif NewPrice[int(lot)-1] != 0 and NewPrice[int(lot)-1] <= prix_achat and not diff:
            print(f"Achat d'un lot de {lots[lot]} au prix de {NewPrice[int(lot)-1]} /!\ raté")
            print("Nouvelle tentative d'achat")
            BuyAction(NewPrice[int(lot)-1], iterations-1, lot, stock)
        elif NewPrice[int(lot)-1] != 0 and NewPrice[int(lot)-1] > prix_achat and not diff:
            print(f"Achat d'un lot de {lots[lot]} au prix de {NewPrice[int(lot)-1]} /!\ raté")
            print("Prix de nouveau au dessus du prix souhaité pas de nouvelle tentative")
        elif NewPrice[int(lot)-1] != 0 and NewPrice[int(lot)-1] > prix_achat and diff:
            stock = Newstock
            inventaire['objet'] += lots[lot]
            inventaire['prix'] += NewPrice[int(lot)-1]
            print(f"Achat d'un lot de {lots[lot]} au prix de {NewPrice[int(lot)-1]}")
            print("Prix de nouveau au dessus du prix souhaité pas de nouvelle tentative")

def main():
    print("Positionnez vous dans l'hdv avec l'item en première position, si ce n'est pas le cas relancez")
    print("Si vous avez déjà vendu l'item quittez et revenez dans l'hdv")
    print("/!\ Vous devez être en plein écran fenêtré et résolution de l'écran 1920x1080")
    prix_data = []

    repeat = int((input("Nombre de minutes à activer le bot : ")))
    prix_achat = int((input("Prix d'achat minimum du lot : ")))
    lot = str(input("Quel lot prendre 1 = 1; 2 = 10; 3 = 100 : "))
    prix_max_achat = int(input("Prix maximum d'achat de lots en une fois (10% de vos kamas est recommendé) "))
    prix_vente = int(input("Prix de vente : "))
    iterations = int(prix_max_achat/prix_achat)

    if iterations > 950:
        iterations = 950
    '''
    Gestion d erreus à implémenter
    '''


    try:
        for i in range(repeat):
            prix_data.append(GetPrix(prix_data))
            print(prix_data[i], ' repeat :', i+1)
            if prix_data[i][int(lot)-1] <= prix_achat:
                inventaire['objet'] += lots[lot]
                inventaire['prix'] += prix_data[i][int(lot)-1]
                print(f"Achat d'un lot de {lots[lot]} au prix de {prix_data[i][int(lot)-1]}")
                BuyAction(prix_data[i][int(lot)-1], iterations, lot, stock)
            if inventaire['objet'] != 0:
                SellAction(prix_vente, lot)
            if i != repeat - 1:
                time.sleep(17)
                MouseMovementsPlay(random.choice(reloads))
                if inventaire["objet"] != 0:
                    print(f'stock actuel : {inventaire["objet"]}, prix moyen du lot {round((inventaire["prix"]/inventaire["objet"])*lots[lot], 2)}')
                else:
                    print('stock actuel : 0')
                time.sleep(2)

    except KeyboardInterrupt:
        print("Interruption détectée. Fermeture du programme...")

    finally:
        # Tracer les courbes
        plt.figure(figsize=(10, 6))
        if prix_data:
            prix1 = [prix[0] for prix in prix_data]
            prix2 = [prix[1] for prix in prix_data]
            prix3 = [prix[2] for prix in prix_data]
            temps = list(range(len(prix_data)))

            plt.plot(temps, prix1, label='Prix 1', marker='o')
            plt.plot(temps, prix2, label='Prix 2', marker='o')
            plt.plot(temps, prix3, label='Prix 3', marker='o')

            plt.title('Évolution des Prix au Fil du Temps')
            plt.xlabel('Temps')
            plt.ylabel('Prix')
            plt.legend()
            plt.grid(True)
            plt.show()


if __name__ == "__main__":
    lots = {'1': 1, '2': 10, '3': 100}
    inventaire = {'objet': 0, 'prix': 0}
    stock = capture_screen((1248, 179, 59, 59))
    # Charger les images modèles
    templates = {
        '0': cv2.imread('Dofus nombres/Dofus_0.png'),
        '1': cv2.imread('Dofus nombres/Dofus_1.png'),
        '2': cv2.imread('Dofus nombres/Dofus_2.png'),
        '3': cv2.imread('Dofus nombres/Dofus_3.png'),
        '4': cv2.imread('Dofus nombres/Dofus_4.png'),
        '5': cv2.imread('Dofus nombres/Dofus_5.png'),
        '6': cv2.imread('Dofus nombres/Dofus_6.png'),
        '7': cv2.imread('Dofus nombres/Dofus_7.png'),
        '8': cv2.imread('Dofus nombres/Dofus_8.png'),
        '9': cv2.imread('Dofus nombres/Dofus_9.png'),
    }

    tab_oui_temp = {
        'Oui': cv2.imread('Block_Oui.png')
    }
    main()
