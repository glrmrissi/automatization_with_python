import asyncio
import tkinter as tk
from threading import Thread, Event
import pyautogui
import pyperclip
import keyboard
import traceback
import csv

stop_event = Event()

#                                                        _____
#                                                    -__/_____\__-
# -------------------------------------------------<>   /-----\
# Funções principais                                |  d|° _ °|p //=======-       --→
# -------------------------------------------------<>   \__-__/  ||┘
2
                                                        
lines = []
current_index = 0 
situacao_do_simples = None
ultimo_cnpj = None

def load_cnpjs():
    global lines
    with open('arquivos/cnpjs.csv') as f:
        lines = f.readlines()

def copy_cnpj():
    global current_index, lines, ultimo_cnpj

    if not lines:   
        load_cnpjs()

    if current_index >= len(lines):
        current_index = 0 

    line = lines[current_index].strip()
    clean_line = line.split('"')

    if len(clean_line) > 1:
        ultimo_cnpj = clean_line[1]
        pyperclip.copy(clean_line[1])
        print(f"🍀 CNPJ {current_index+1}: {clean_line[1]} copiado")
    else:
        print(f"🟥 Linha {current_index+1} inválida:", line)

    current_index += 1
    
    
    
def salvar_resultado(cnpj, situacao):
    with open("arquivos/resultados.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([cnpj, situacao])
    print(f"✅ Salvo: {cnpj}, {situacao}")
    
    
async def play_deleted():
    global situacao_do_simples, ultimo_cnpj
    
    while not stop_event.is_set():
        try:
            icon = None
            try:
                icon = pyautogui.locateCenterOnScreen("imgs/image.png", confidence=0.8)
            except pyautogui.ImageNotFoundException:
                pass

            if icon:
                copy_cnpj()
                print(f"☑️ Ícone principal encontrado em: {icon}")
                x, y = icon
                pyautogui.click(x, y + 25)
                await asyncio.sleep(0.1)
                pyautogui.hotkey('ctrl', 'v')
                print("↩️ CTRL + V")

            consultar = None
            try:
                consultar = pyautogui.locateCenterOnScreen("imgs/consultar.png", confidence=0.9)
            except pyautogui.ImageNotFoundException:
                pass

            if consultar:
                print("☑️ Ícone de consultar encontrado")
                pyautogui.click(consultar)
                await asyncio.sleep(0.1)
                
            cnpj_not_found = None
            try:
                cnpj_not_found = pyautogui.locateCenterOnScreen("imgs/cnpj_not_found.png", confidence=0.9)
            except pyautogui.ImageNotFoundException:
                pass
            
            cnpj_field = None
            if(cnpj_not_found):
                print("🟥 CNPJ NOT FOUND ")
                try:
                    cnpj_field = pyautogui.locateCenterOnScreen("imgs/imagea.png", confidence=0.8)
                    if (cnpj_field):
                        copy_cnpj()
                        print(f"☑️ Ícone principal encontrado em: {cnpj_field}")
                        x, y = cnpj_field
                        pyautogui.click(x, y + 25)
                        pyautogui.hotkey('ctrl', 'a')
                        pyautogui.press('backspace')
                        await asyncio.sleep(0.1)
                        pyautogui.hotkey('ctrl', 'v')
                        print("CTRL + V")
                except pyautogui.ImageNotFoundException:
                    pass
                
            situation_simple_false = None
            situation_simple_true = None
            back_image = None
            
            try:
                situation_simple_false = pyautogui.locateCenterOnScreen("imgs/situacaodesimples.png")
                print(f"☑️ Icone de situação do simples encontrado {situation_simple_false}")
            except pyautogui.ImageNotFoundException:
                pass
            
            if(situation_simple_false):
                situacao_do_simples = False
                print(f"💭 Situação do simples é {situacao_do_simples}")
                try:
                    back_image = pyautogui.locateCenterOnScreen("imgs/icon_voltar.png")
                    print(f"☑️Ícone voltar encontrado em {back_image}")
                except pyautogui.ImageNotFoundException:
                    pass
            
            try:
                situation_simple_true = pyautogui.locateCenterOnScreen("imgs/optante_simples.png")
                print(f"☑️Ícone de situação do simples encontrado {situation_simple_false}")
            except pyautogui.ImageNotFoundException:
                pass
            
            if(situation_simple_true):
                situacao_do_simples = True
                print(f"Situação do simples é {situacao_do_simples}")
                try:
                    back_image = pyautogui.locateCenterOnScreen("imgs/icon_voltar.png")
                    print(f"☑️Icone voltar encontrado em {back_image}")
                except pyautogui.ImageNotFoundException:
                    pass
            
            if situacao_do_simples is True:
                print("💚 True")
                salvar_resultado(ultimo_cnpj, situacao_do_simples)
                situacao_do_simples = None 
            elif situacao_do_simples is False:
                print("❤️ False")
                salvar_resultado(ultimo_cnpj, situacao_do_simples)
                situacao_do_simples = None
            else:
                print("🔁 Not Found")
                    
            
            if(back_image):
                print(f"☑️Ícone principal encontrado em: {back_image}")
                x, y = back_image
                pyautogui.click(x, y)
                
            await asyncio.sleep(0.2)  # evita loop 100% CPU
        except Exception:
            print("Erro inesperado em play_deleted:")
            traceback.print_exc()
            await asyncio.sleep(0.5)

# -------------------------------------------------<>
# Gerenciamento de tasks                            |
# -------------------------------------------------<>

loop = asyncio.new_event_loop()

def run_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()

Thread(target=run_loop, daemon=True).start()

def start_play():
    stop_event.clear()
    fut = asyncio.run_coroutine_threadsafe(play_deleted(), loop)
    print("🍏 Play iniciado")

def stop_play():
    stop_event.set()
    print("🍎 Play parado")

def listen_hotkey():
    keyboard.add_hotkey('ctrl+0', stop_play)
    keyboard.wait()

Thread(target=listen_hotkey, daemon=True).start()

# -------------------------------------------------<>
# Tkinter                                           |
# -------------------------------------------------<>
root = tk.Tk()
root.title("Controlador Play/Stop")

btn_play = tk.Button(root, text="Play", command=start_play, bg="green", fg="white", font=("Arial", 16))
btn_play.pack(padx=15, pady=10)

btn_stop = tk.Button(root, text="Stop", command=stop_play, bg="red", fg="white", font=("Arial", 16))
btn_stop.pack(padx=15, pady=10)

root.mainloop()
