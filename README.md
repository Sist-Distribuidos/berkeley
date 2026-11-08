# Sincronización de Relojes con el Algoritmo de Berkeley

## Descripción
Implementación del algoritmo de Berkeley para sincronización interna de relojes en un sistema distribuido de 3 nodos (1 maestro + 2 esclavos), utilizando sockets UDP en Python. Cada nodo simula un reloj con un offset distinto respecto a la hora real, lo que permite observar cómo los relojes convergen al promedio calculado por el coordinador.

## Teoría
El algoritmo de Berkeley es un método de **sincronización interna**: no se asume que ningún nodo posea la hora "verdadera" (no hay fuente UTC externa). Sus fases son:

1. Un **coordinador (maestro)** hace polling periódico a los esclavos.
2. Cada esclavo responde con su hora local.
3. El maestro estima la hora de cada esclavo considerando el tiempo de ida y vuelta (RTT/2) y calcula el **promedio** de todas las horas, incluida la suya.
4. Opcionalmente se aplica un **promedio tolerante a fallos (fault-tolerant average)**: se descartan los valores demasiado alejados de la mediana para tolerar relojes defectuosos.
5. El maestro envía a cada nodo (y a sí mismo) el **ajuste (delta)** que debe aplicar para alinearse con el promedio.

## Estructura del proyecto
- `maestro.py` — Nodo coordinador: realiza el polling, estima las horas, calcula el promedio y envía los ajustes.
- `esclavo.py` — Nodo esclavo: responde con su hora local y aplica los ajustes recibidos.
- `README.md` — Este documento.

## Requisitos
- Python 3.6 o superior.
- Sin dependencias externas (solo librería estándar: `socket`, `time`, `json`, `statistics`).

## Ejecución
Abrir 3 terminales en la carpeta del proyecto.

Terminal 1 — Esclavo 1 (reloj atrasado 3 segundos):

    python esclavo.py 5001 -3

Terminal 2 — Esclavo 2 (reloj adelantado 7 segundos):

    python esclavo.py 5002 7

Terminal 3 — Maestro (reloj adelantado 5 segundos):

    python maestro.py

En la terminal del maestro, presionar ENTER para iniciar cada ronda de sincronización. Ctrl+C para salir.

Nota: para ejecutarlo en máquinas distintas de la misma red, editar la lista `ESCLAVOS` en `maestro.py` con las IP de los esclavos. Los esclavos no requieren configuración adicional porque responden a la dirección de la que recibieron la solicitud.

## Salida esperada (ejemplo)
En el maestro:

    [MAESTRO] Mi hora local: 1731234567.123
    [MAESTRO] Esclavo ('127.0.0.1', 5001): hora=1731234564.120, RTT=1.2ms, estimado=1731234564.121
    [MAESTRO] Esclavo ('127.0.0.1', 5002): hora=1731234574.125, RTT=0.8ms, estimado=1731234574.126
    [MAESTRO] Fault-tolerant average aplicado. Promedio: 1731234568.456
    [MAESTRO] Mi ajuste: +1.333s
    [MAESTRO] Enviado a ('127.0.0.1', 5001): ajuste de +4.335s
    [MAESTRO] Enviado a ('127.0.0.1', 5002): ajuste de -5.670s

Después de la ronda, los 3 relojes quedan alineados al mismo valor (el promedio).

## Consideraciones de diseño
- Los relojes se simulan con un offset fijo sobre `time.time()`, lo que permite verificar la sincronización.
- El maestro estima la hora de cada esclavo como `hora_esclavo + RTT/2` (estimación tipo Cristian).
- El fault-tolerant average descarta el valor más alejado de la mediana cuando hay 3 o más muestras.
- Los ajustes son acumulativos en los esclavos (`ajuste_acumulado`), de modo que rondas sucesivas refinan la sincronización.
- La comunicación usa datagramas UDP con mensajes JSON: `TIME?` (polling), `{"hora": ...}` (respuesta) y `{"ajuste": ...}` (corrección).

## Referencias
- Coulouris, G., Dollimore, J., Kindberg, T. y Blair, G. *Distributed Systems: Concepts and Design*, 5ª edición. Capítulo 14 (Time and Global States), Sección 14.3.3 (algoritmo de Berkeley).
- Tanenbaum, A. S. y van Steen, M. *Distributed Systems: Principles and Paradigms*, 4ª edición. Capítulo 8 (sincronización de relojes).
- Gusella, R. y Zatti, S. (1989). *The accuracy of clock synchronization achieved by TEMPO in Berkeley UNIX 4.3BSD*. IEEE Transactions on Software Engineering.

## Autores

Guido, Mariano. Haffner, Ignacio. Ruano, Leandro Fidel. Román Haunau, Oscar
