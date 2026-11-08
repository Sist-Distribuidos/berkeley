# Algoritmo de Berkeley - Sincronización de Relojes

## Descripción
Implementación del algoritmo de Berkeley para sincronización interna de relojes en un sistema distribuido de 3 nodos (1 maestro + 2 esclavos), utilizando sockets UDP en Python.

## Teoría
El algoritmo de Berkeley (Coulouris, Cap. 14.3.3) es un método de **sincronización interna**:
- Un coordinador hace polling periódico a los esclavos
- Cada esclavo responde con su hora local
- El maestro estima las horas usando RTT/2 y calcula el promedio
- Envía a cada nodo el ajuste (delta) necesario para alinearse
- Incluye **fault-tolerant average** para tolerar relojes defectuosos

## Estructura
- `maestro.py` - Nodo coordinador
- `esclavo.py` - Nodo esclavo (ejecutar 2 veces con distintos offsets)

## Ejecución
Abrir 3 terminales:

**Esclavo 1** (offset -3s):
```bash
python esclavo.py 5001 -3
