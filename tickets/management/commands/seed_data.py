from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import timedelta
import random
from tickets.models import Ticket, Tipificacion


AREAS = [
    'Corporación Caracas Productiva', 'Consultoría Jurídica', 'Secretaría',
    'Auditoria Interna', 'Despacho', 'Producción y Gestión de Espacios Agricolas',
    'Mercado', 'Oficina de atención al ciudadano', 'Gestión Administrativa',
    'Planificación y Presupuesto', 'Talento Humano', 'Tecnología', 'Estacionamiento'
]

SOLICITANTES = [
    ('María Rodríguez', 'maria@correo.com'), ('Pedro López', 'pedro@correo.com'),
    ('Luisa Fernández', 'luisa@correo.com'), ('José Hernández', 'jose@correo.com'),
    ('Carmen Pérez', 'carmen@correo.com'), ('Jorge Sánchez', 'jorge@correo.com'),
    ('Rosa Martínez', 'rosa@correo.com'), ('Luis González', 'luis@correo.com'),
    ('Ana Castillo', 'ana@correo.com'), ('Carlos Mendoza', 'carlos@correo.com'),
    ('Sofía Rivas', 'sofia@correo.com'), ('Diego Torres', 'diego@correo.com'),
    ('Valentina Ruiz', 'valentina@correo.com'), ('Andrés Mora', 'andres@correo.com'),
    ('Gabriela Silva', 'gabriela@correo.com'), ('Fernando Díaz', 'fernando@correo.com'),
    ('Isabel Medina', 'isabel@correo.com'), ('Ricardo Vargas', 'ricardo@correo.com'),
    ('Patricia Rojas', 'patricia@correo.com'), ('Miguel Ángel Paz', 'miguel@correo.com'),
]

DESCRIPCIONES_HARDWARE = [
    'Monitor no enciende, no muestra imagen',
    'Teclado no responde, varias teclas atascadas',
    'Mouse óptico no funciona correctamente, cursor salta',
    'CPU no arranca, no se escucha el ventilador',
    'Impresora no imprime, muestra error de papel atascado',
    'Disco duro hace ruidos extraños, posible falla mecánica',
    'Batería del portátil no carga, solo funciona enchufado',
    'Pantalla del portátil tiene líneas verticales',
    'Escáner no detecta el documento',
    'Cable de red dañado, conector roto',
    'Fuente de poder quemada, no da señal de vida',
    'Memoria RAM defectuosa, pantallazos azules',
]

DESCRIPCIONES_SOFTWARE = [
    'Windows no actualiza, error 0x80070002',
    'Office no abre, se cierra inesperadamente',
    'El sistema contable no genera reportes',
    'Navegador lento, tarda en cargar páginas',
    'Antivirus bloquea aplicaciones del sistema',
    'Correo electrónico no envía archivos adjuntos',
    'Error al imprimir desde Excel, formato incorrecto',
    'El programa de nómina no calcula correctamente',
    'No se puede acceder al sistema de expedientes',
    'El módulo de facturación se congela',
    'Error al actualizar el sistema operativo',
    'Base de datos del sistema de inventario corrupta',
]

DESCRIPCIONES_RED = [
    'No hay conexión a internet en todo el piso',
    'La red WiFi es muy lenta, señal intermitente',
    'No se puede acceder a los recursos compartidos',
    'El switch del departamento no funciona',
    'Cableado de red dañado, pérdida de paquetes',
    'No se asignan IPs por DHCP en el rango .100-.200',
    'El servidor de archivos no responde desde ayer',
    'Configuración de VPN falla al conectar',
    'El router del segundo piso se reinicia solo',
    'Puertos del patch panel sin funcionar',

]

DESCRIPCIONES_OTRO = [
    'Solicitud de instalación de software especializado',
    'Se requiere una extensión eléctrica adicional',
    'Cambio de puesto de trabajo a otra oficina',
    'Se solicita la creación de un nuevo usuario',
    'Asignación de equipo nuevo para nuevo empleado',
    'Se necesita trasladar el CPU a otra ubicación',
    'Instalación de punto de red adicional',
    'Configuración de escritorio remoto',
    'Se solicita mantenimiento preventivo',
    'Necesito respaldo de información urgente',
]

TIPOS = ['hardware', 'software', 'red', 'otro']
DESCRIPCIONES = {
    'hardware': DESCRIPCIONES_HARDWARE,
    'software': DESCRIPCIONES_SOFTWARE,
    'red': DESCRIPCIONES_RED,
    'otro': DESCRIPCIONES_OTRO,
}

ESTADOS = ['abierto', 'en_proceso', 'pendiente', 'resuelto']


class Command(BaseCommand):
    help = 'Llena la base de datos con datos de ejemplo'

    def handle(self, *args, **options):
        self.stdout.write('Poblando base de datos con datos de ejemplo...')

        tecnicos = User.objects.filter(groups__name='Tecnico').order_by('id')
        admin = User.objects.filter(groups__name='Administrador').first()

        if not tecnicos:
            self.stdout.write(self.style.WARNING('No hay técnicos. Creando usuarios...'))
            grupo_tec = Group.objects.get(name='Tecnico')
            grupo_admin = Group.objects.get(name='Administrador')

            admin = User.objects.create_user(
                username='admin', password='admin123',
                first_name='Administrador', last_name='Principal',
                is_superuser=True, is_staff=True
            )
            admin.groups.add(grupo_admin)
            admin.save()

            t1 = User.objects.create_user(
                username='tecnico1', password='tecnico123',
                first_name='Carlos', last_name='García'
            )
            t1.groups.add(grupo_tec)
            t1.save()

            t2 = User.objects.create_user(
                username='tecnico2', password='tecnico123',
                first_name='Ana', last_name='Martínez'
            )
            t2.groups.add(grupo_tec)
            t2.save()

            t3 = User.objects.create_user(
                username='tecnico3', password='tecnico123',
                first_name='Roberto', last_name='Hernández'
            )
            t3.groups.add(grupo_tec)
            t3.save()

            tecnicos = User.objects.filter(groups__name='Tecnico').order_by('id')

        existing = Ticket.objects.count()
        if existing > 0:
            self.stdout.write(self.style.WARNING(f'Ya existen {existing} tickets. Eliminando...'))
            Ticket.objects.all().delete()

        now = timezone.now()
        tickets_creados = 0

        for i in range(80):
            solicitante, contacto = random.choice(SOLICITANTES)
            area = random.choice(AREAS)
            tipo = random.choice(TIPOS)
            descripcion = random.choice(DESCRIPCIONES[tipo])

            days_ago = random.randint(0, 60)
            hours_ago = random.randint(0, 23)
            created = now - timedelta(days=days_ago, hours=hours_ago)

            peso_estados = {
                'abierto': 0.25 if days_ago < 15 else 0.05,
                'en_proceso': 0.30 if days_ago < 30 else 0.10,
                'pendiente': 0.15 if days_ago < 45 else 0.20,
                'resuelto': 0.30 if days_ago > 0 else 0.65,
            }
            estados_ponderados = []
            for est, peso in peso_estados.items():
                estados_ponderados.extend([est] * int(peso * 20))
            estado = random.choice(estados_ponderados)

            notas = ''
            if estado == 'en_proceso':
                notas = random.choice([
                    'Se está revisando el equipo en sitio. Pendiente diagnóstico.',
                    'Técnico asignado. Se contactó al usuario para agendar visita.',
                    'En espera de autorización para proceder con la reparación.',
                    'Se identificó la falla. Se requiere repuesto.',
                ])
            elif estado == 'pendiente':
                notas = random.choice([
                    'Esperando llegada del repuesto solicitado al proveedor.',
                    'Pendiente de respuesta del usuario para continuar.',
                    'Se requiere autorización del jefe de departamento.',
                    'En espera de actualización del fabricante del software.',
                ])
            elif estado == 'resuelto':
                notas = random.choice([
                    'Se reemplazó la pieza dañada. Equipo funcionando correctamente.',
                    'Se actualizó el software al último parche disponible.',
                    'Se configuró correctamente la red. Usuario verifica conexión.',
                    'Se reinstaló el sistema operativo y se restauraron los datos.',
                    'Se realizó el mantenimiento preventivo. Equipo optimizado.',
                ])

            tecnico = None
            if estado != 'abierto':
                tecnico = random.choice(tecnicos)
                if estado == 'resuelto' and created < now - timedelta(days=1):
                    pass

            updated = created + timedelta(
                hours=random.randint(1, 48),
                minutes=random.randint(0, 59)
            )
            if updated > now:
                updated = now

            ticket = Ticket.objects.create(
                solicitante=solicitante,
                contacto=contacto,
                descripcion=descripcion,
                direccion_area=area,
                estado=estado,
                tecnico_asignado=tecnico,
                notas=notas,
                fecha_creacion=created,
                fecha_actualizacion=updated,
            )
            tip_obj = Tipificacion.objects.filter(slug=tipo).first()
            if tip_obj:
                ticket.tipificaciones.add(tip_obj)
            tickets_creados += 1

        self.stdout.write(self.style.SUCCESS(
            f'✓ {tickets_creados} tickets creados exitosamente.'
        ))
        self.stdout.write(self.style.SUCCESS(
            '✓ Usuarios disponibles: admin (admin123), tecnico1/tecnico2/tecnico3 (tecnico123)'
        ))
