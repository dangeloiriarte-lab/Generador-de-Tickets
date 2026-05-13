# Generador de Tickets de Soporte Técnico v4.2

Sistema web para gestión de tickets de soporte técnico con tres tipos de usuarios:
- **Usuario común**: Accede al formulario público para reportar fallas (sin login)
- **Técnico**: Inicia sesión, atiende incidencias, cambia estados y genera reportes
- **Administrador**: Inicia sesión, gestiona técnicos, asigna tickets y genera reportes

## Requisitos

- Python 3.10+
- MariaDB 10.5+

## Instalación

### 1. Clonar el repositorio

```bash
git clone <repo>
cd "generador de ticket V-4.1 HIBRIDO"
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configurar MariaDB

Crear la base de datos en MariaDB:

```bash
mariadb -u root -p
```

```sql
CREATE DATABASE tickets_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'root'@'localhost' IDENTIFIED BY '';
GRANT ALL PRIVILEGES ON tickets_db.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

> Si tu MariaDB tiene contraseña, actualiza `PASSWORD` en `config/settings.py`.

### 4. Ejecutar migraciones

```bash
python manage.py migrate
```

### 5. Crear superusuario (Administrador)

```bash
python manage.py createsuperuser
```

Después de crear el superusuario, asignarle el grupo "Administrador":

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User, Group
user = User.objects.get(username='tu_usuario')
admin_group = Group.objects.get(name='Administrador')
user.groups.add(admin_group)
user.is_staff = True
user.is_superuser = True
user.save()
exit()
```

### 6. Crear técnicos

Inicia sesión como administrador y ve a "Usuarios" para crear técnicos, o:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User, Group
tecnico = User.objects.create_user('tecnico1', password='password123')
grupo_tecnico = Group.objects.get(name='Tecnico')
tecnico.groups.add(grupo_tecnico)
tecnico.save()
exit()
```

## Ejecutar el servidor

```bash
python manage.py runserver
```

## Desplegar en red local 

```bash
.\run.bat
```

Abrir en el navegador: `http://localhost:8000`

## Funcionalidades

- **Modo oscuro** con persistencia en localStorage
- **Notificaciones en tiempo real** con sonido personalizable
- **Gráficos SVG** generados del lado del servidor (donut, barras verticales y horizontales)
- **Exportación a PDF** con ReportLab (lista de tickets y detalle individual)
- **Exportación a Excel (.xlsx)** con openpyxl — estilos, colores y auto-filtro
- **Filtros combinados** desde gráficos (click en segmentos/barras)
- **Panel responsive** adaptado a dispositivos móviles
- **Manual de usuario** integrado en la app

## Estructura de URLs

| URL | Descripción | Acceso |
|-----|-------------|--------|
| `/` | Formulario público de tickets | Público |
| `/ticket/<id>/exito/` | Confirmación de ticket creado | Público |
| `/login/` | Inicio de sesión | Staff |
| `/dashboard/` | Panel de tickets | Staff |
| `/ticket/<id>/` | Detalle de ticket | Staff |
| `/reportes/` | Reportes y estadísticas | Staff |
| `/gestion-usuarios/` | Gestión de usuarios | Administrador |
| `/admin/` | Panel admin de Django | Administrador |

## Estructura del Proyecto

```
generador-de-ticket/
├── config/                  # Configuración Django
│   ├── settings.py          # Ajustes (DB MariaDB, apps)
│   ├── urls.py              # Rutas principales
│   └── wsgi.py
├── tickets/                 # App de tickets
│   ├── models.py            # Modelo Ticket
│   ├── views.py             # Vistas (CRUD, dashboard, reportes, PDF, Excel)
│   ├── forms.py             # Formularios
│   ├── chart_utils.py       # Generación de gráficos SVG
│   ├── urls.py
│   ├── admin.py
│   └── templates/tickets/   # Plantillas HTML
├── accounts/                # App de autenticación
│   ├── views.py             # Login, logout, gestión usuarios
│   ├── urls.py
│   └── templates/accounts/  # Plantillas HTML
├── static/
│   ├── css/style.css        # Estilos personalizados
│   └── js/                  # JavaScript (Chart.js, datalabels)
├── templates/
│   └── base.html            # Plantilla base
├── pdf_cache/               # Caché de PDFs generados
├── requirements.txt
└── manage.py
```
