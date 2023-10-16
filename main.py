import asyncio
import websockets
import numpy as np
import cv2
from mss import mss
from PIL import Image
import pytesseract
import pyautogui
import time
import tracemalloc
import re

mensagem_enviada = False
messagem = ""
texto = ''
texto_anterior = ''
texto_anterior_num = ''
saldo_anterior = ''
mon = {'left': 1066, 'top': 786, 'width': 930, 'height': 20}
saldo = {'left': 715, 'top': 284, 'width': 70, 'height': 50}
novo_array_de_inteiros = []
array_antigo = []
apostado = False
flag = False
cor_apostada = ''
qd_apostado = []
lin_apostada = []
numgan = 0
numero = 0
passou = False
output_message = ""

tempo_ultimo_resultado = time.time()

prim_qd = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
sec_qd = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
ter_qd = [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]

red = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
black = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]

prim_lin = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
sec_lin = [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]
ter_lin = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]

tracemalloc.start()


async def verificar_aposta(cor, qd, linha, venc, websocket):
    if (apostado == True):
        output_message = ""

        numero = venc

        ganhador_quadrantes = []

        if numero in prim_qd:
            ganhador_quadrantes.append("Primeiro Quadrante")
        elif numero in sec_qd:
            ganhador_quadrantes.append("Segundo Quadrante")
        elif numero in ter_qd:
            ganhador_quadrantes.append("Terceiro Quadrante")
        else:
            ganhador_quadrantes.append("Quadrante Desconhecido")

        ganhador_cores = []

        if numero in red:
            ganhador_cores.append("Vermelho")
        elif numero in black:
            ganhador_cores.append("Preto")
        else:
            ganhador_cores.append("Cor Desconhecida")

        ganhador_linhas = []

        if numero in prim_lin:
            ganhador_linhas.append("Primeira Linha")
        elif numero in sec_lin:
            ganhador_linhas.append("Segunda Linha")
        elif numero in ter_lin:
            ganhador_linhas.append("Terceira Linha")
        else:
            ganhador_linhas.append("Linha Desconhecida")


        output_message = "📝 ---- Resultado da aposta anterior: ---- 📝\n\n"
        output_message += f"Número Sorteado: {venc}\n"
        output_message += "Infos:\n"
        output_message += f" Linha: {ganhador_linhas[0]}\n"
        if ganhador_cores[0] == "Preto":
            output_message += f" Cor: {ganhador_cores[0]} ⬛\n"
        elif ganhador_cores[0] == "Vermelho":
            output_message += f" Cor: {ganhador_cores[0]} 🟥\n"
        output_message += f" Quadrante: {ganhador_quadrantes[0]}\n\n"
        output_message += "Ganhos:\n"


        if ganhador_linhas[0] in linha:
            output_message += " Acertou a linha ✅\n"
        if ganhador_cores[0] == cor:
            output_message += " Acertou a cor ✅\n"
        if ganhador_quadrantes[0] in qd:
            output_message += " Acertou o quadrante ✅\n"
        if (
                not (ganhador_linhas[0] in linha) and
                not (ganhador_cores[0] == cor_apostada) and
                not (ganhador_quadrantes[0] in qd)
        ):
            output_message += " Aposta perdida! 🥺\n"

        await websocket.send(output_message)


async def aposta(novo_array_de_inteiros, websocket):
    global apostado
    aposta_qnt = 0
    global cor_apostada
    global qd_apostado
    global lin_apostada
    global messagem

    messagem = ""

    if len(novo_array_de_inteiros) == 12:

        tres_primeiros = novo_array_de_inteiros[:3]

        categorias_quadrantes = []

        for numero in tres_primeiros:
            if numero in prim_qd:
                categorias_quadrantes.append("Primeiro Quadrante")
            elif numero in sec_qd:
                categorias_quadrantes.append("Segundo Quadrante")
            elif numero in ter_qd:
                categorias_quadrantes.append("Terceiro Quadrante")
            else:
                categorias_quadrantes.append("Quadrante Desconhecido")

        categorias_cores = []

        for numero in tres_primeiros:
            if numero in red:
                categorias_cores.append("Vermelho")
            elif numero in black:
                categorias_cores.append("Preto")
            else:
                categorias_cores.append("Cor Desconhecida")

        categorias_linhas = []

        for numero in tres_primeiros:
            if numero in prim_lin:
                categorias_linhas.append("Primeira Linha")
            elif numero in sec_lin:
                categorias_linhas.append("Segunda Linha")
            elif numero in ter_lin:
                categorias_linhas.append("Terceira Linha")
            else:
                categorias_linhas.append("Linha Desconhecida")


        cor_apostada = ''
        qd_apostado = []
        lin_apostada = []
        await websocket.send("_________________________________________________")
        await websocket.send("\n👇🏼 👇🏼------ PRÓXIMA APOSTA ------ 👇🏼 👇🏼")


        if all(cor == "Vermelho" for cor in categorias_cores[:3]):
            messagem += "👉🏼 Apostar em Preto ⬛\n"
            cor_apostada = 'Preto'
            aposta_qnt += 1
        elif all(cor == "Preto" for cor in categorias_cores[:3]):
            messagem += "👉🏼 Apostar em Vermelho 🟥\n"
            cor_apostada = 'Vermelho'
            aposta_qnt += 1

        if all(quadrante == "Primeiro Quadrante" for quadrante in categorias_quadrantes[:3]):
            messagem += "👉🏼 Apostar no 2º e 3º Quadrantes \n"
            qd_apostado = ["Segundo Quadrante", "Terceiro Quadrante"]
            aposta_qnt += 1
        elif all(quadrante == "Segundo Quadrante" for quadrante in categorias_quadrantes[:3]):
            messagem += "👉🏼 Apostar no 1º e 3º Quadrantes \n"
            qd_apostado = ["Primeiro Quadrante", "Terceiro Quadrante"]
            aposta_qnt += 1
        elif all(quadrante == "Terceiro Quadrante" for quadrante in categorias_quadrantes[:3]):
            messagem += "👉🏼 Apostar no 1º e 2º Quadrantes \n"
            qd_apostado = ["Primeiro Quadrante", "Segundo Quadrante"]
            aposta_qnt += 1

        if all(linha == "Primeira Linha" for linha in categorias_linhas[:3]):
            messagem += "👉🏼 Apostar na 2ª e 3ª Linhas \n"
            lin_apostada = ["Segunda Linha", "Terceira Linha"]
            aposta_qnt += 1
        elif all(linha == "Segunda Linha" for linha in categorias_linhas[:3]):
            messagem += "👉🏼 Apostar na 1ª e 3ª Linhas \n"
            lin_apostada = ["Primeira Linha", "Terceira Linha"]
            aposta_qnt += 1
        elif all(linha == "Terceira Linha" for linha in categorias_linhas[:3]):
            messagem += "👉🏼 Apostar na 1ª e 2ª Linhas \n"
            lin_apostada = ["Primeira Linha", "Segunda Linha"]
            aposta_qnt += 1

        if (
                not all(cor == "Vermelho" for cor in categorias_cores[:3]) and
                not all(cor == "Preto" for cor in categorias_cores[:3]) and
                not all(quadrante == "Primeiro Quadrante" for quadrante in categorias_quadrantes[:3]) and
                not all(quadrante == "Segundo Quadrante" for quadrante in categorias_quadrantes[:3]) and
                not all(quadrante == "Terceiro Quadrante" for quadrante in categorias_quadrantes[:3]) and
                not all(linha == "Primeira Linha" for linha in categorias_linhas[:3]) and
                not all(linha == "Segunda Linha" for linha in categorias_linhas[:3]) and
                not all(linha == "Terceira Linha" for linha in categorias_linhas[:3])
        ):
            messagem += "❌ Não há dados suficientes para fazer uma aposta. \n"
            aposta_qnt = 0

        if aposta_qnt > 0:
            apostado = True
        else:
            apostado = False
    else:
        messagem += "⚠️ Leitura Incorreta! ⚠️\n"
        messagem += "⏰ Aguarde a próxima rodada para apostar!"
        apostado = False

    await websocket.send(messagem)


async def create_array(websocket, texto):
    array_resultante = texto.split()
    array_de_inteiros = []
    novo_elementos = []
    global array_antigo
    global passou
    passou = True

    for elemento in array_resultante:
        partes = re.split(r'[,:!?/`;]',
                          elemento.replace('(', '').replace(')', '').replace('{', '').replace('}', '').replace(
                              '[', '').replace(']', '').replace('°', ''))

        novo_elementos.extend(partes)

    for elementos in novo_elementos:
        try:
            numero = int(elementos)
            array_de_inteiros.append(numero)
        except ValueError:
            pass

    novo_array_de_inteiros = []

    for numero in array_de_inteiros:
        if numero > 36:
            numero_str = str(numero)
            partes = []

            i = 0
            while i < len(numero_str):
                parte = numero_str[i:i + 2]
                if int(parte) <= 36:
                    partes.append(int(parte))
                    i += 2
                else:
                    parte = numero_str[i:i + 1]
                    partes.append(int(parte))
                    i += 1

            novo_array_de_inteiros.extend(partes)
        else:
            novo_array_de_inteiros.append(numero)

    try:
        if len(novo_array_de_inteiros) == 12:
            venc = novo_array_de_inteiros[0]
            if apostado:
                await verificar_aposta(cor_apostada, qd_apostado, lin_apostada, venc, websocket)
    except:
        pass

    await aposta(novo_array_de_inteiros, websocket)

async def prin (websocket):

    global texto_anterior
    global output_message

    with mss() as sct:
        while True:
            screenShot = sct.grab(mon)
            img = Image.frombytes(
                'RGB',
                (screenShot.width, screenShot.height),
                screenShot.rgb,
            )

            # x, y = pyautogui.position()
            # print(f'Coordenadas do cursor: x={x}, y={y}')

            cv2.imshow('test', np.array(img))

            img_np = np.array(img)

            texto = pytesseract.image_to_string(img_np,
                                                config='--psm 7')

            if texto != texto_anterior:
                texto_anterior = texto
                tempo_ultimo_resultado = time.time()
                passou = False
                mensagem_enviada = False


            if time.time() - tempo_ultimo_resultado >= 4 and not passou and not mensagem_enviada:
                await create_array(websocket, texto_anterior)
                mensagem_enviada = True


            if cv2.waitKey(33) & 0xFF in (
                    ord('q'),
                    27,
            ):
                break

async def echo(websocket, path):
    while True:
        await prin(websocket)

start_server = websockets.serve(echo, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()