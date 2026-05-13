import hashlib
from pathlib import Path
from django.shortcuts import render
from django.urls import resolve, Resolver404
from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent.parent


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Referrer-Policy'] = 'same-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response


class FileIntegrityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not self._should_check(request):
            return self.get_response(request)

        data_file = Path(__file__).resolve().parent / '.ownership_data.json'
        if not data_file.exists():
            return self.get_response(request)

        try:
            import json
            data = json.loads(data_file.read_text())
        except (json.JSONDecodeError, OSError):
            return self.get_response(request)

        stored_sig = data.get('signature', '')
        stored_manifest_sig = data.get('manifest_signature', '')
        verified_at = data.get('verified_at', '')

        if not stored_sig or not stored_manifest_sig:
            return self.get_response(request)

        if not verified_at:
            return self.get_response(request)

        enc_file = Path(__file__).resolve().parent / 'ownership.enc'
        manifest_file = Path(__file__).resolve().parent / 'manifest.enc'

        if not enc_file.exists() or not manifest_file.exists():
            return self._compromised_response(request)

        try:
            current_sig = hashlib.sha256(enc_file.read_bytes()).hexdigest()
            current_manifest_sig = hashlib.sha256(manifest_file.read_bytes()).hexdigest()

            if current_sig != stored_sig or current_manifest_sig != stored_manifest_sig:
                return self._compromised_response(request)
        except OSError:
            return self._compromised_response(request)

        return self.get_response(request)

    def _should_check(self, request):
        protected_prefixes = [
            '/dashboard', '/tickets/', '/reportes', '/mi-panel',
            '/notificaciones/', '/auditoria/', '/gestion-usuarios',
        ]
        path = request.path_info
        for prefix in protected_prefixes:
            if path.startswith(prefix):
                return True
        return False

    def _compromised_response(self, request):
        from django.contrib.auth import logout
        logout(request)
        return render(
            request,
            'tickets/compromised.html',
            {'mensaje': 'La integridad del sistema ha sido comprometida. Contacte al administrador.'},
            status=403
        )
