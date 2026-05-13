from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime
import random
from tickets.models import Ticket, Tipificacion


AREAS = [
    'Corporación Caracas Productiva', 'Consultoría Jurídica', 'Secretaría',
    'Auditoria Interna', 'Despacho', 'Producción y Gestión de Espacios Agricolas',
    'Mercado', 'Oficina de atención al ciudadano', 'Gestión Administrativa',
    'Planificación y Presupuesto', 'Talento Humano', 'Tecnología', 'Estacionamiento',
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
    ('Laura Campos', 'laura@correo.com'), ('David Rincón', 'david@correo.com'),
    ('Elena Suárez', 'elena@correo.com'), ('Mario Blanco', 'mario@correo.com'),
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

NOTAS_POR_ESTADO = {
    'en_proceso': [
        'Se está revisando el equipo en sitio. Pendiente diagnóstico.',
        'Técnico asignado. Se contactó al usuario para agendar visita.',
        'En espera de autorización para proceder con la reparación.',
        'Se identificó la falla. Se requiere repuesto.',
    ],
    'pendiente': [
        'Esperando llegada del repuesto solicitado al proveedor.',
        'Pendiente de respuesta del usuario para continuar.',
        'Se requiere autorización del jefe de departamento.',
        'En espera de actualización del fabricante del software.',
    ],
    'resuelto': [
        'Se reemplazó la pieza dañada. Equipo funcionando correctamente.',
        'Se actualizó el software al último parche disponible.',
        'Se configuró correctamente la red. Usuario verifica conexión.',
        'Se reinstaló el sistema operativo y se restauraron los datos.',
        'Se realizó el mantenimiento preventivo. Equipo optimizado.',
    ],
}

TECNICO_WEIGHTS = []


def crear_ticket(fecha, tecnicos, tipificaciones_map):
    solicitante, contacto = random.choice(SOLICITANTES)
    area = random.choice(AREAS)
    tipo = random.choice(TIPOS)
    descripcion = random.choice(DESCRIPCIONES[tipo])

    now = timezone.now()
    days_since_created = (now - fecha).days

    if days_since_created > 180:
        estado = random.choice(['resuelto'] * 8 + ['pendiente'] * 1 + ['en_proceso'] * 1)
    elif days_since_created > 60:
        estado = random.choice(['resuelto'] * 6 + ['pendiente'] * 2 + ['en_proceso'] * 1 + ['abierto'] * 1)
    elif days_since_created > 20:
        estado = random.choice(['resuelto'] * 4 + ['en_proceso'] * 3 + ['pendiente'] * 2 + ['abierto'] * 1)
    else:
        estado = random.choice(['abierto'] * 3 + ['en_proceso'] * 3 + ['pendiente'] * 2 + ['resuelto'] * 2)

    notas = ''
    if estado in NOTAS_POR_ESTADO:
        notas = random.choice(NOTAS_POR_ESTADO[estado])

    tecnico = None
    if estado != 'abierto':
        tecnico = random.choice(TECNICO_WEIGHTS)

    horas_diff = random.randint(1, 72)
    updated = fecha + timedelta(hours=horas_diff, minutes=random.randint(0, 59))
    if updated > now:
        updated = now

    ticket = Ticket.objects.create(
        solicitante=solicitante,
        contacto=contacto,
        tipo_falla=tipo,
        descripcion=descripcion,
        direccion_area=area,
        estado=estado,
        tecnico_asignado=tecnico,
        notas=notas,
    )

    Ticket.objects.filter(pk=ticket.pk).update(
        fecha_creacion=fecha,
        fecha_actualizacion=updated,
    )

    if tipo in tipificaciones_map:
        ticket.tipificaciones.add(tipificaciones_map[tipo])

    return ticket


class Command(BaseCommand):
    help = 'Agrega tickets de ejemplo para los años 2024, 2025 y 2026'

    def handle(self, *args, **options):
        global TECNICO_WEIGHTS

        tecnicos = list(User.objects.filter(groups__name='Tecnico').order_by('id'))
        if not tecnicos:
            self.stdout.write(self.style.ERROR('No hay técnicos en el sistema.'))
            return

        self.stdout.write(f'Técnicos encontrados: {len(tecnicos)}')
        for t in tecnicos:
            self.stdout.write(f'  - {t.get_full_name() or t.username} (ID: {t.id})')

        tech1, tech2 = tecnicos[0], tecnicos[1]
        TECNICO_WEIGHTS = [tech1] * 6 + [tech2] * 4

        tipificaciones = {t.slug: t for t in Tipificacion.objects.all()}

        total_antes = Ticket.objects.count()
        now = timezone.now()
        creados = 0

        periodos = [
            ('2024', datetime(2024, 1, 1, tzinfo=timezone.get_current_timezone()),
             datetime(2024, 12, 31, tzinfo=timezone.get_current_timezone()), 18),
            ('2025', datetime(2025, 1, 1, tzinfo=timezone.get_current_timezone()),
             datetime(2025, 12, 31, tzinfo=timezone.get_current_timezone()), 30),
            ('2026-actual', datetime(2026, 1, 1, tzinfo=timezone.get_current_timezone()),
             now, 22),
        ]

        for anno, inicio, fin, cantidad in periodos:
            total_dias = (fin - inicio).days
            if total_dias < 0:
                total_dias = 0
            for _ in range(cantidad):
                if total_dias > 0:
                    dias_random = random.randint(0, total_dias)
                else:
                    dias_random = 0
                horas_random = random.randint(0, 23)
                minutos_random = random.randint(0, 59)
                fecha = inicio + timedelta(days=dias_random, hours=horas_random, minutes=minutos_random)
                if fecha > now:
                    fecha = now
                crear_ticket(fecha, tecnicos, tipificaciones)
                creados += 1

        total_despues = Ticket.objects.count()

        self.stdout.write(self.style.SUCCESS(f'\n=> {creados} tickets de ejemplo creados:'))
        self.stdout.write(f'   - 2024: 18 tickets')
        self.stdout.write(f'   - 2025: 30 tickets')
        self.stdout.write(f'   - 2026: 22 tickets')
        self.stdout.write(f'   - Distribución desigual entre técnicos')
        self.stdout.write(f'\n✓ Total en BD: {total_antes} → {total_despues} tickets.')
