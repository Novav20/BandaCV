#!/bin/bash

# --- Configuración ---
BOARD_FQBN="arduino:avr:uno"
SKETCH_DIR="arduino_code/"

# --- Detección Automática de Puerto ---
echo "Detectando puerto del Arduino..."
PORT=$(arduino-cli board list --format json | jq -r '.detected_ports[] | select(.matching_boards[].fqbn=="'$BOARD_FQBN'") | .port.address')

if [ -z "$PORT" ]; then
    echo "Error: No se pudo encontrar un Arduino conectado con FQBN '$BOARD_FQBN'. Asegúrate de que esté conectado y que el FQBN sea correcto."
    arduino-cli board list # Muestra los dispositivos conectados para ayudar a depurar
    exit 1
fi

echo "Arduino encontrado en el puerto: $PORT"

# --- Comandos ---
echo "Compilando sketch..."
arduino-cli compile --fqbn $BOARD_FQBN $SKETCH_DIR

# Revisa si la compilación fue exitosa antes de cargar
if [ $? -eq 0 ]; then
    echo "Compilación exitosa. Cargando en $PORT..."
    arduino-cli upload -p $PORT --fqbn $BOARD_FQBN $SKETCH_DIR
else
    echo "Error de compilación. Carga cancelada."
fi
