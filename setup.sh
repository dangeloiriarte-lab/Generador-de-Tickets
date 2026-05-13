#!/bin/bash
echo "============================================"
echo "  Generador de Tickets - Setup Inicial"
echo "============================================"
echo ""

echo "[1/4] Instalando dependencias..."
pip install -r requirements.txt --quiet
echo "  Dependencias instaladas."
echo ""

echo "[2/4] Creando migraciones..."
python manage.py makemigrations --quiet 2>/dev/null
echo "  Migraciones creadas."
echo ""

echo "[3/4] Aplicando migraciones a la base de datos..."
python manage.py migrate
echo ""

echo "[4/4] Creando superusuario..."
python manage.py createsuperuser
echo ""

echo "============================================"
echo "  Configuracion completa!"
echo "============================================"
echo ""
echo "Para iniciar el servidor ejecuta:"
echo "  python manage.py runserver"
echo ""
echo "Luego visita http://localhost:8000"
echo ""
echo "NOTA: Despues de crear el superusuario, asignale"
echo "el grupo 'Administrador' desde /admin/ o ejecuta:"
echo ""
echo "  python manage.py shell"
echo "  >>> from django.contrib.auth.models import User, Group"
echo "  >>> user = User.objects.get(username='TU_USUARIO')"
echo "  >>> user.groups.add(Group.objects.get(name='Administrador'))"
echo "  >>> user.save()"
echo ""
