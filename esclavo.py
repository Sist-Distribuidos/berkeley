import socket
import time
import json
import sys

# Configuración desde argumentos
if len(sys.argv) != 3:
    print("Uso: python esclavo.py <PUERTO> <OFFSET_SEGUNDOS>")
    print("Ejemplo: python esclavo.py 5001 -3")
    sys.exit(1)

PUERTO = int(sys.argv[1])
OFFSET = int(sys.argv[2])  # Offset simulado respecto a la hora real
PUERTO_MAESTRO = 5000

def hora_local():
    """Simula el reloj del esclavo con un offset fijo."""
    return time.time() + OFFSET

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", PUERTO))
    print(f"[ESCLAVO puerto {PUERTO}] Iniciado con offset de {OFFSET:+d}s respecto a la hora real")
    print(f"[ESCLAVO] Esperando solicitudes del maestro...\n")

    ajuste_acumulado = 0  # Para ir aplicando los ajustes sucesivos

    while True:
        data, addr = sock.recvfrom(1024)
        if data == b"TIME?":
            # Responder con la hora local actual (ya con ajustes acumulados)
            hora_actual = hora_local() + ajuste_acumulado
            respuesta = json.dumps({"hora": hora_actual}).encode()
            sock.sendto(respuesta, addr)
            print(f"[ESCLAVO] Solicitud recibida. Hora enviada: {hora_actual:.3f}")
        else:
            try:
                msg = json.loads(data.decode())
                if "ajuste" in msg:
                    delta = msg["ajuste"]
                    ajuste_acumulado += delta
                    print(f"[ESCLAVO] Ajuste recibido: {delta:+.3f}s. Nuevo offset total aplicado: {ajuste_acumulado:+.3f}s")
                    print(f"[ESCLAVO] Mi hora ahora es: {hora_local() + ajuste_acumulado:.3f}\n")
            except json.JSONDecodeError:
                pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[ESCLAVO] Finalizado.")