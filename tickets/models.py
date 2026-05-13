from django.db import models
from django.contrib.auth.models import User


class Tipificacion(models.Model):
    slug = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Tipificación'
        verbose_name_plural = 'Tipificaciones'
        ordering = ['slug']

    def __str__(self):
        return self.nombre


class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    mensaje = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True)
    leido = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return self.mensaje


class NotificacionUsuario(models.Model):
    solicitante = models.CharField(max_length=150)
    direccion_area = models.CharField(max_length=150)
    mensaje = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True)
    leido = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return self.mensaje


class Configuracion(models.Model):
    clave = models.CharField(max_length=100, unique=True)
    valor = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.clave}: {self.valor}'


class Ticket(models.Model):
    ESTADO_CHOICES = [
        ('abierto', 'Abierto'),
        ('en_proceso', 'En proceso'),
        ('pendiente', 'Pendiente'),
        ('resuelto', 'Resuelto'),
    ]

    TIPO_FALLA_CHOICES = [
        ('hardware', 'Hardware'),
        ('software', 'Software'),
        ('red', 'Red'),
        ('otro', 'Solicitud de servicio'),
    ]

    solicitante = models.CharField(max_length=150, verbose_name='Nombre del solicitante')
    contacto = models.CharField(max_length=150, verbose_name='Email/Contacto')
    tipo_falla = models.CharField(max_length=20, choices=TIPO_FALLA_CHOICES, blank=True, null=True, default='otro', verbose_name='Tipo de falla')
    tipificaciones = models.ManyToManyField('Tipificacion', blank=True, verbose_name='Tipificación')
    descripcion = models.TextField(verbose_name='Descripción detallada')
    direccion_area = models.CharField(max_length=150, verbose_name='Dirección/Área')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='abierto', verbose_name='Estado')
    tecnico_asignado = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_asignados',
        verbose_name='Técnico asignado',
    )
    notas = models.TextField(blank=True, default='', verbose_name='Notas de seguimiento')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última actualización')

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'

    def __str__(self):
        return f'Ticket #{self.pk} - {self.solicitante}'

    @property
    def codigo(self):
        return f'TKT-{self.pk:04d}'

    @property
    def nombre_tecnico(self):
        if self.tecnico_asignado:
            return self.tecnico_asignado.get_full_name() or self.tecnico_asignado.username
        return 'Sin asignar'

    @property
    def nombres_tipificacion(self):
        nombres = [t.nombre for t in self.tipificaciones.all()]
        return ', '.join(nombres) if nombres else 'Sin definir'


class AuditLog(models.Model):
    ACCIONES = [
        ('LOGIN', 'Inicio de sesión'),
        ('LOGIN_FAILED', 'Intento fallido de inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
        ('ACCESO', 'Acceso al panel'),
        ('CREAR', 'Creación'),
        ('EDITAR', 'Edición'),
        ('ELIMINAR', 'Eliminación'),
        ('CAMBIAR_PASSWORD', 'Cambio de contraseña'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Usuario')
    nombre_completo = models.CharField(max_length=200, verbose_name='Nombre completo')
    accion = models.CharField(max_length=50, choices=ACCIONES, verbose_name='Acción')
    modelo = models.CharField(max_length=100, verbose_name='Modelo afectado')
    id_objeto = models.IntegerField(null=True, blank=True, verbose_name='ID del objeto')
    detalles = models.TextField(blank=True, verbose_name='Detalles')
    direccion_ip = models.CharField(max_length=45, verbose_name='Dirección IP')
    direccion_area = models.CharField(max_length=150, blank=True, default='', verbose_name='Dirección/Departamento')
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha/Hora')

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Registro de auditoría'
        verbose_name_plural = 'Registros de auditoría'

    def __str__(self):
        return f'{self.nombre_completo} - {self.get_accion_display()} - {self.fecha.strftime("%d/%m/%Y %H:%M")}'
