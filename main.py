import json
import subprocess
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console
from collections import deque
from rich.align import Align
from rich.live import Live
import time
from datetime import datetime

layout = Layout()
console = Console()

PLUG_MAP = {
    "PLUGGED_AC": "PC ou outros dispositivos",
    "PLUGGED_USB": "Fonte de carregamento",
    "UNPLUGGED": "Em nenhum dispositivo"
}

        #------------Plug
def pluggado(dados):
    return PLUG_MAP.get(dados["plugged"], "Desconhecido")


def obter_dados():
    try:
        resultado_bateria = subprocess.run(
            ["termux-battery-status"],
            capture_output=True,
            text=True
        )
        resultado_wifi = subprocess.run(
            ["termux-wifi-connectioninfo"],
            capture_output=True,
            text=True
        )
        bateria = json.loads(resultado_bateria.stdout)
        wifi = json.loads(resultado_wifi.stdout)

        dados = bateria.copy()
        dados.update(wifi)

        return dados

    except Exception:
        return {"health": "sem informação", "level": 0, "voltage": 0, "current": -0, "temperature": 0, "plugged": "",
                "ip": "xxx.xxx.xxx.xx", "ssid": 0, "rssi": 0, "link_speed_mbps": 0}
    
#------------Grafico unicode def 

def gerar_sparkline(historico):
    blocos = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
    linha_grafico = ""
    for valor in historico:
        try:
            valor_numerico = float(valor)
        except (ValueError, TypeError):
            continue
        v = max(0, min(100, valor_numerico))
        indice = int((v / 100) * (len(blocos) - 1))
        linha_grafico += blocos[indice]
        
    return linha_grafico

ultimos_dados_vel = deque(maxlen=8)
ultimos_dados_rssi = deque(maxlen=8)

#------------Split, Separação

layout.split_column(
    Layout(name="header", size=3),
    Layout(name="body")
)
layout["body"].split_row(
    Layout(name="esquerda"),
    Layout(name="direita")
)
layout["esquerda"].split_column(
    Layout(name="saude", ratio = 2),
    Layout(name="level", ratio = 2),
    Layout(name="volt", ratio = 2),
    Layout(name="curry", ratio = 2),
    Layout(name="temp", ratio = 2),
    Layout(name="plug", ratio = 2)
)
layout["direita"].split_column(
    Layout(name="vel", ratio = 2),
    Layout(name="sinal", ratio = 2),
    Layout(name="conexao", ratio = 2),
            # Layout(name="44"),
    Layout(name="ip", ratio = 2)
)

with Live(layout, refresh_per_second=1):
    while True:

        agora = datetime.now()
        hora_formatada = agora.strftime("%H:%M")

        
        dados = obter_dados()

        saude = dados["health"]
        level = dados["level"]
        volt = dados["voltage"]
        curry = dados["current"]
        temp = dados["temperature"]

        ip = dados["ip"]
        conexao = dados["ssid"]
        sinal = dados["rssi"]
        vel = dados["link_speed_mbps"]
        plugado = pluggado(dados)

        #------------Graficos unicode 

        novo_valor_vel = vel / 10
        novo_valor_conexao = sinal * -1

        ultimos_dados_vel.append(novo_valor_vel)
        graficombps = gerar_sparkline(ultimos_dados_vel)

        ultimos_dados_rssi.append(novo_valor_conexao)
        graficorssi = gerar_sparkline(ultimos_dados_rssi)

        #------------Update
        layout["header"].update(
            Panel(Align.center(f"🔥 [on red]HEFESTO[/on red] 🔥 ° {hora_formatada} ° "))
        )

        #------------esquerda
        layout["saude"].update(
            f"Saúde da bateria;\n {saude}"
        )
        layout["level"].update(
            f"Porcentagem da bateria;\n {level}%"
        )
        layout["volt"].update(
            f"Voltagem da bateria;\n {volt/1000:.2f}V"
        )
        layout["curry"].update(
            f"Corrente da bateria;\n {curry/1000:.0f}mA"
        )
        layout["temp"].update(
            f"Temperatura do Serv.;\n {temp}°C"
        )
        layout["plug"].update(
            f"Plugado no...;\n {plugado}"
        )

        #------------DIreita
        layout["vel"].update(
            f"Megabits por segundo; {vel}Mbps\n\n {graficombps}"
        )
        layout["sinal"].update(
            f"Sinal atual do dispostivo; {sinal}\n\n {graficorssi}"
        )
        layout["conexao"].update(
            f"Conectado em;\n {conexao}"
        )
        layout["ip"].update(
            f"{ip}"
        )

        time.sleep(4)