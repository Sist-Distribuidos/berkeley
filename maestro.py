import socket
import time
import json
import statistics

# Configuración
PUERTO_MAESTRO = 5000
ESCLAVOS = [("127.0.0.1", 5001), ("127.0.0.1", 5002)]  # IPs y puertos de los esclavos
OFFSET_LOCAL = 5  # El maestro cree que son las X+5 segundos respecto a la hora real

def hora_local_maestro():
    """Simula el reloj del maestro con un offset fijo."""
    return time.time() + OFFSET_LOCAL

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", PUERTO_MAESTRO))
    sock.settimeout(2)

    print(f"[MAESTRO] Iniciado en puerto {PUERTO_MAESTRO}")
    print(f"[MAESTRO] Mi reloj local tiene offset de +{OFFSET_LOCAL}s respecto a la hora real\n")

    while True:
        input("Presiona ENTER para iniciar una ronda de sincronización (Ctrl+C para salir)...")
        tiempos_estimados = []
        ajustes = {}

        # 1. El maestro incluye su propia hora
        t_maestro = hora_local_maestro()
        print(f"\n[MAESTRO] Mi hora local: {t_maestro:.3f}")
        tiempos_estimados.append(t_maestro)

        # 2. Polling a cada esclavo
        for esclavo in ESCLAVOS:
            t0 = time.time()
            sock.sendto(b"TIME?", esclavo)
            try:
                data, _ = sock.recvfrom(1024)
                t1 = time.time()
                respuesta = json.loads(data.decode())
                t_esclavo = respuesta["hora"]
                rtt = t1 - t0
                # Estimación: hora del esclavo + RTT/2 (como en Cristian)
                t_estimado = t_esclavo + rtt / 2
                print(f"[MAESTRO] Esclavo {esclavo}: hora={t_esclavo:.3f}, RTT={rtt*1000:.1f}ms, estimado={t_estimado:.3f}")
                tiempos_estimados.append(t_estimado)
                ajustes[esclavo] = t_estimado
            except socket.timeout:
                print(f"[MAESTRO] Esclavo {esclavo} no respondió (timeout)")

        if len(tiempos_estimados) < 2:
            print("[MAESTRO] No hay suficientes respuestas. Abortando ronda.")
            continue

        # 3. Cálculo del promedio (fault-tolerant: descartamos valores extremos si hay >=3)
        if len(tiempos_estimados) >= 3:
            # Fault-tolerant average: descartar el valor más alejado de la mediana
            mediana = statistics.median(tiempos_estimados)
            filtrados = sorted(tiempos_estimados, key=lambda x: abs(x - mediana))[:-1]
            promedio = statistics.mean(filtrados)
            print(f"[MAESTRO] Fault-tolerant average aplicado. Promedio: {promedio:.3f}")
        else:
            promedio = statistics.mean(tiempos_estimados)
            print(f"[MAESTRO] Promedio calculado: {promedio:.3f}")

        # 4. Calcular y enviar ajustes
        ajuste_maestro = promedio - t_maestro
        print(f"[MAESTRO] Mi ajuste: {ajuste_maestro:+.3f}s")

        for esclavo, t_est in ajustes.items():
            delta = promedio - t_est
            mensaje = json.dumps({"ajuste": delta}).encode()
            sock.sendto(mensaje, esclavo)
            print(f"[MAESTRO] Enviado a {esclavo}: ajuste de {delta:+.3f}s")

        print("\n--- Ronda completada ---\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[MAESTRO] Finalizado.")