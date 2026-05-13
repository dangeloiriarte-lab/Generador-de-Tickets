from functools import wraps
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.core.cache import cache
from tickets.views import _registrar_auditoria


def rate_limit_login(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if request.method == 'POST':
            ip = request.META.get('REMOTE_ADDR', '')
            key = f'login_attempts_{ip}'
            attempts = cache.get(key, 0)
            if attempts >= 5:
                _registrar_auditoria(request, None, 'LOGIN_FAILED', 'Sesión', detalles=f'Rate limit excedido - IP: {ip}')
                messages.error(request, 'Demasiados intentos. Espera 60 segundos antes de intentar de nuevo.')
                return render(request, 'accounts/login.html')
            response = view_func(request, *args, **kwargs)
            if request.user.is_authenticated:
                cache.delete(key)
            else:
                cache.set(key, attempts + 1, 60)
            return response
        return view_func(request, *args, **kwargs)
    return _wrapped


@rate_limit_login
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.groups.exists():
                login(request, user)
                _registrar_auditoria(request, user, 'LOGIN', 'Sesión', detalles=f'Inicio de sesión exitoso - {user.get_full_name() or user.username}')
                return redirect('dashboard')
            else:
                _registrar_auditoria(request, None, 'LOGIN_FAILED', 'Sesión', detalles=f'Intento fallido - usuario: {username} (sin permisos)')
                messages.error(request, 'Este usuario no tiene permisos asignados.')
        else:
            _registrar_auditoria(request, None, 'LOGIN_FAILED', 'Sesión', detalles=f'Intento fallido - usuario: {username}')
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    _registrar_auditoria(request, request.user, 'LOGOUT', 'Sesión', detalles=f'Cierre de sesión - {request.user.get_full_name() or request.user.username}')
    logout(request)
    return redirect('landing')


def is_admin(user):
    return user.is_authenticated and user.groups.filter(name='Administrador').exists()


@login_required
@user_passes_test(is_admin)
def gestion_usuarios(request):
    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'crear':
            username = request.POST.get('username')
            password = request.POST.get('password')
            grupo = request.POST.get('grupo')
            nombre_completo = request.POST.get('nombre_completo', '').strip()
            first_name = nombre_completo.split(' ', 1)[0] if nombre_completo else ''
            last_name = nombre_completo.split(' ', 1)[1] if ' ' in nombre_completo else ''

            if User.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya existe.')
            else:
                user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
                grupo_obj = Group.objects.get(name=grupo)
                user.groups.add(grupo_obj)
                _registrar_auditoria(request, request.user, 'CREAR', 'Usuario', id_objeto=user.pk, detalles=f'Creó el usuario "{username}" con rol {grupo}')
                messages.success(request, f'Usuario "{username}" creado correctamente.')

        elif accion == 'eliminar':
            user_id = request.POST.get('user_id')
            user = User.objects.get(pk=user_id)
            if user != request.user:
                nombre = user.username
                nombre_completo_usr = user.get_full_name() or user.username
                _registrar_auditoria(request, request.user, 'ELIMINAR', 'Usuario', id_objeto=user_id, detalles=f'Eliminó al usuario "{nombre}" ({nombre_completo_usr})')
                user.delete()
                messages.success(request, f'Usuario "{nombre}" eliminado.')
            else:
                messages.error(request, 'No puedes eliminar tu propio usuario.')

        elif accion == 'editar':
            user_id = request.POST.get('user_id')
            username = request.POST.get('username', '').strip()
            grupo = request.POST.get('grupo', '').strip()
            nombre_completo = request.POST.get('nombre_completo', '').strip()
            first_name = ''
            last_name = ''
            if nombre_completo:
                parts = nombre_completo.split(' ', 1)
                first_name = parts[0]
                last_name = parts[1] if len(parts) > 1 else ''
            user = User.objects.get(pk=user_id)
            if username:
                if User.objects.exclude(pk=user_id).filter(username=username).exists():
                    messages.error(request, f'El nombre de usuario "{username}" ya existe.')
                else:
                    user.username = username
            if grupo:
                user.groups.clear()
                grupo_obj = Group.objects.get(name=grupo)
                user.groups.add(grupo_obj)
            if nombre_completo:
                user.first_name = first_name
                user.last_name = last_name
            user.save()
            _registrar_auditoria(request, request.user, 'EDITAR', 'Usuario', id_objeto=user_id, detalles=f'Editó al usuario "{username or user.username}" - rol: {grupo}')
            messages.success(request, f'Usuario actualizado correctamente.')

        elif accion == 'cambiar_password':
            user_id = request.POST.get('user_id')
            password = request.POST.get('password')
            user = User.objects.get(pk=user_id)
            nombre_usr = user.get_full_name() or user.username
            user.set_password(password)
            user.save()
            _registrar_auditoria(request, request.user, 'CAMBIAR_PASSWORD', 'Usuario', id_objeto=user_id, detalles=f'Cambió la contraseña del usuario "{nombre_usr}"')
            messages.success(request, f'Contraseña actualizada correctamente.')

        return redirect('gestion_usuarios')

    usuarios = User.objects.filter(groups__isnull=False).exclude(pk=request.user.pk).prefetch_related('groups')
    grupos = Group.objects.filter(name__in=['Administrador', 'Tecnico'])

    context = {
        'usuarios': usuarios,
        'grupos': grupos,
    }
    return render(request, 'accounts/gestion_usuarios.html', context)
