import os


dir_name = "arquivos"
path = os.path.join(dir_name)

os.makedirs(path, exist_ok=True)

print("Pasta '% s' criada" % dir_name)

with open('arquivos/result.txt', 'w') as f:
    f.write('result')

# f = open('cnpjs.csv', 'r')
# content = f.read()
# print(content)

lines = []
with open('arquivos/result.txt') as f:
    lines = f.readlines()

count = 0

for line in lines:
    count += 1
    print(f'linha {count}: {line}')


import asyncio
import pyautogui

async def localizar_icones():
    try:
        iconsimples = await asyncio.to_thread(
            pyautogui.locateCenterOnScreen, "imgs/optante_simples.png", confidence=0.9
        )
        icon_optante = await asyncio.to_thread(
            pyautogui.locateCenterOnScreen, "imgs/situacaodesimples.png", confidence=0.9
        )

        if iconsimples:
            print("Ícone 'optante_simples' encontrado:", iconsimples)
            return iconsimples
        elif icon_optante:
            print("Ícone 'situacaodesimples' encontrado:", icon_optante)
            return icon_optante
        else:
            print("Nenhum ícone encontrado.")
            return None

    except Exception as e:
        print("Erro ao localizar ícones:", e)
        return None
