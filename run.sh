#!/bin/bash
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "Iniciando Generador de Tickets..."
echo "Servidor local: http://127.0.0.1:8035"
echo "Red local:     http://$LOCAL_IP:8035"
echo "Presiona Ctrl+C para detener."
echo ""
python manage.py runserver 0.0.0.0:8035
