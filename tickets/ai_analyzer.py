import re


PATTERNS = [
    {
        'keywords': [
            'no enciende', 'no prende', 'pantalla negra', 'sin luz', 'no da video',
            'no da imagen', 'no arranca', 'no bootea', 'no carga', 'muerto',
            'queda negro', 'pantalla en negro', 'no funciona el monitor', 'cpu no enciende',
            'equipo no enciende', 'computadora no enciende', 'pc no enciende',
        ],
        'label': 'Fallo de encendido',
        'suggestion': 'El equipo podría tener una falla en la fuente de poder, la placa madre o el cable de alimentación. Se recomienda verificar conexiones eléctricas y probar con otro cargador/fuente.',
        'tipo_falla': 'hardware',
    },
    {
        'keywords': [
            'lento', 'tarda', 'congela', 'se traba', 'no responde', 'congelado',
            'se queda pegado', 'anda lento', 'muy lento', 'demora', 'tarda mucho',
            'va lento', 'funciona lento', 'esta lento', 'se pone lento',
            'se congela', 'se queda congelado', 'tarda en abrir', 'tarda en cargar',
            'no responde', 'deja de responder', 'no responde el mouse',
        ],
        'label': 'Rendimiento lento',
        'suggestion': 'Podría deberse a falta de memoria RAM, disco duro saturado, exceso de programas iniciando con el sistema, o presencia de malware. Se sugiere liberar espacio y ejecutar un análisis de rendimiento.',
        'tipo_falla': 'software',
    },
    {
        'keywords': [
            'internet', 'wifi', 'red', 'conexión', 'conectividad', 'no navega',
            'sin red', 'desconectado', 'cable de red', 'no hay internet',
            'no tengo internet', 'sin internet', 'no conecta', 'no se conecta',
            'falla la conexion', 'problema de internet', 'internet lento',
            'no agarra internet', 'no funciona internet', 'wifi no funciona',
            'red no disponible', 'sin conexion', 'desconectado de la red',
        ],
        'label': 'Problema de red',
        'suggestion': 'Posible falla en la configuración de red, controladores de WiFi, o problema con el router/switch. Se recomienda verificar conexión, reiniciar el equipo de red y revisar configuración IP.',
        'tipo_falla': 'red',
    },
    {
        'keywords': [
            'correo', 'email', 'outlook', 'no envía', 'no recibe', 'bandeja',
            'no envia correo', 'no recibe correo', 'correo no funciona',
            'outlook no abre', 'no puedo enviar correo', 'no puedo recibir correo',
            'problema con el correo', 'falla el correo', 'bandeja de entrada',
            'no me llegan correos', 'no envio correos',
        ],
        'label': 'Problema de correo',
        'suggestion': 'Podría deberse a configuración incorrecta de la cuenta, contraseña vencida, buzón lleno, o problemas con el servidor de correo. Verificar credenciales y espacio en buzón.',
        'tipo_falla': 'software',
    },
    {
        'keywords': [
            'impresora', 'imprimir', 'no imprime', 'atascada', 'sin tinta',
            'toner', 'cartucho', 'la impresora', 'impresion', 'no imprime nada',
            'impresora no funciona', 'problema con la impresora',
            'falla la impresora', 'no quiere imprimir', 'se atasco',
            'no imprime bien', 'imprime mal', 'impresora offline',
        ],
        'label': 'Fallo de impresión',
        'suggestion': 'Posible atasco de papel, falta de tinta/tóner, controladores desactualizados, o la impresora está en estado offline. Revisar cola de impresión y estado del dispositivo.',
        'tipo_falla': 'hardware',
    },
    {
        'keywords': [
            'virus', 'malware', 'antivirus', 'infección', 'popup', 'publicidad',
            'ransomware', 'spyware', 'troyano', 'esta infectado',
            'tiene virus', 'virus detectado', 'antivirus detecto',
        ],
        'label': 'Posible infección de malware',
        'suggestion': 'Se recomienda ejecutar un análisis completo con el antivirus, aislar el equipo de la red y verificar procesos sospechosos en el administrador de tareas.',
        'tipo_falla': 'software',
    },
    {
        'keywords': [
            'actualización', 'update', 'windows update', 'parche', 'actualizar',
            'actualizando', 'se esta actualizando', 'problema de actualizacion',
            'error de actualizacion', 'no se actualiza', 'no actualiza',
        ],
        'label': 'Problema con actualizaciones',
        'suggestion': 'Las actualizaciones pendientes o fallidas pueden causar conflictos. Verificar Windows Update, reiniciar el equipo y aplicar las actualizaciones pendientes manualmente.',
        'tipo_falla': 'software',
    },
    {
        'keywords': [
            'sonido', 'audio', 'no se escucha', 'parlante', 'audífono', 'altavoz',
            'sin sonido', 'no hay sonido', 'no tiene sonido', 'problema de sonido',
            'falla el audio', 'bocina', 'no funcionan los parlantes',
        ],
        'label': 'Fallo de audio',
        'suggestion': 'Posible problema con controladores de audio, dispositivo en silencio, o salida de audio incorrecta. Revisar mezclador de volumen y administrador de dispositivos.',
        'tipo_falla': 'hardware',
    },
    {
        'keywords': [
            'usb', 'puerto', 'no reconoce', 'periférico', 'mouse', 'teclado',
            'cámara', 'camara', 'no detecta', 'no funciona el puerto',
            'puerto usb', 'no reconoce el usb', 'teclado no funciona',
            'mouse no funciona', 'no funciona el mouse', 'no funciona el teclado',
        ],
        'label': 'Fallo de periféricos',
        'suggestion': 'Podría ser un problema de controladores, puerto USB dañado, o el dispositivo requiere reinicio. Probar en otro puerto y verificar el administrador de dispositivos.',
        'tipo_falla': 'hardware',
    },
    {
        'keywords': [
            'pantalla azul', 'blue screen', 'bsod', 'crash', 'reinicia solo',
            'se apaga', 'se reinicia', 'se reinicia solo', 'se apaga solo',
            'pantalla de la muerte', 'error critico', 'se bloquea',
            'la pc se reinicia', 'el equipo se reinicia', 'reinicio inesperado',
        ],
        'label': 'Fallo crítico del sistema',
        'suggestion': 'Pantallazos azules pueden indicar falla de hardware (RAM, disco duro) o controladores corruptos. Revisar código de error y realizar diagnóstico de memoria.',
        'tipo_falla': 'hardware',
    },
    {
        'keywords': [
            'programa', 'aplicación', 'software', 'no abre', 'error al abrir',
            'falla', 'se cierra', 'no se abre', 'no puede abrir', 'se cierra solo',
            'error al iniciar', 'no inicia', 'la aplicacion no abre',
            'el programa no abre', 'error en el programa',
        ],
        'label': 'Fallo de aplicación',
        'suggestion': 'Posible corrupción de archivos de programa, falta de permisos, o conflicto con otras aplicaciones. Reinstalar la aplicación o ejecutar como administrador.',
        'tipo_falla': 'software',
    },
    {
        'keywords': [
            'contraseña', 'clave', 'password', 'acceso', 'login', 'no puedo entrar',
            'bloqueado', 'no me deja entrar', 'no puedo acceder', 'se me olvido la contraseña',
            'olvide la contraseña', 'cuenta bloqueada', 'usuario bloqueado',
            'no puedo iniciar sesion', 'error de inicio de sesion',
        ],
        'label': 'Problema de acceso',
        'suggestion': 'Podría deberse a contraseña olvidada, cuenta bloqueada por intentos fallidos, o problema con el directorio activo. Restablecer contraseña o verificar con el administrador del sistema.',
        'tipo_falla': 'software',
    },
    {
        'keywords': [
            'office', 'word', 'excel', 'powerpoint', 'archivo', 'documento',
            'no guarda', 'no se guarda', 'no puedo guardar', 'error al guardar',
            'archivo corrupto', 'no abre el archivo', 'documento no se abre',
            'excel no abre', 'word no abre', 'office no funciona',
        ],
        'label': 'Problema con Office/documentos',
        'suggestion': 'Posible archivo corrupto, licencia vencida, o problemas con la suite de Office. Intentar abrir en modo seguro, reparar la instalación o recuperar versión anterior.',
        'tipo_falla': 'software',
    },
    {
        'keywords': [
            'no funciona', 'falla', 'problema', 'error', 'dañado', 'roto',
            'esta malo', 'no sirve', 'dejo de funcionar', 'presenta falla',
        ],
        'label': 'Reporte de falla general',
        'suggestion': 'Se requiere revisión técnica para determinar la causa del problema. Verificar el equipo y realizar pruebas de diagnóstico para identificar el componente o servicio afectado.',
        'tipo_falla': 'otro',
    },
    {
        'keywords': [
            'solicitud', 'solicito', 'requiero', 'necesito', 'instalación',
            'instalar', 'mantenimiento', 'configuración', 'configurar',
            'creación', 'crear', 'asignación', 'trasladar', 'cambio',
            'respaldo', 'copia de seguridad', 'nuevo usuario',
        ],
        'label': 'Solicitud de servicio',
        'suggestion': 'El usuario solicita un servicio administrativo o técnico. Se recomienda contactar al solicitante para coordinar los detalles y programar la ejecución del servicio solicitado.',
        'tipo_falla': 'otro',
    },
]


def analizar(texto):
    if not texto:
        return None
    texto_lower = texto.lower()
    detectados = {}
    for patron in PATTERNS:
        for kw in patron['keywords']:
            if kw in texto_lower:
                slug = patron['tipo_falla']
                if slug and slug not in detectados:
                    detectados[slug] = {
                        'label': patron['label'],
                        'suggestion': patron['suggestion'],
                    }
                break
    if not detectados:
        return {
            'label': 'Solicitud de servicio',
            'suggestion': 'El usuario ha reportado una incidencia. Se recomienda contactar al solicitante para obtener más detalles, revisar el equipo y determinar las acciones necesarias para resolver el problema.',
            'tipo_falla': 'otro',
            'tipos_detectados': ['otro'],
        }
    slugs = list(detectados.keys())
    primero = slugs[0]
    return {
        'label': detectados[primero]['label'],
        'suggestion': detectados[primero]['suggestion'],
        'tipo_falla': primero,
        'tipos_detectados': slugs,
        'labels': {s: detectados[s]['label'] for s in slugs},
    }
