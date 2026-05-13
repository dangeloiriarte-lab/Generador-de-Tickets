import json
import datetime
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from tickets.security_utils import (
    decrypt_message, generate_file_manifest, verify_file_integrity,
    load_ownership_data, save_ownership_data, hash_file,
    OWNERSHIP_ENC, MANIFEST_ENC, OWNERSHIP_MESSAGE, BASE_DIR
)


class Command(BaseCommand):
    help = 'Verifica la autoría del proyecto e integridad de archivos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--passphrase',
            type=str,
            help='Passphrase para descifrar (omitir para ingreso interactivo)',
        )

    def handle(self, *args, **options):
        if not OWNERSHIP_ENC.exists() or not MANIFEST_ENC.exists():
            raise CommandError(
                'El sistema de autoría no está configurado.\n'
                'Ejecuta primero: python manage.py setup_ownership'
            )

        passphrase = options.get('passphrase')
        if not passphrase:
            import getpass
            passphrase = getpass.getpass('Introduce tu passphrase: ')

        paso = 0
        total = 4

        paso += 1
        self.stdout.write(f'[{paso}/{total}] Descifrando mensaje de autoría...')
        try:
            encrypted_message = OWNERSHIP_ENC.read_text()
            decrypted_message = decrypt_message(encrypted_message, passphrase)
        except Exception:
            raise CommandError('❌ Passphrase incorrecta o archivo de autoría corrupto.')

        if decrypted_message != OWNERSHIP_MESSAGE:
            self.stdout.write(self.style.WARNING('⚠️  El mensaje descifrado no coincide con el esperado.'))
            self.stdout.write(f'  Esperado: {OWNERSHIP_MESSAGE}')
            self.stdout.write(f'  Obtenido: {decrypted_message}')
            if not self._confirm('¿Continuar de todas formas?'):
                return

        self.stdout.write(self.style.SUCCESS(f'  ✓ Mensaje: "{decrypted_message}"'))

        paso += 1
        self.stdout.write(f'[{paso}/{total}] Descifrando manifest de archivos...')
        try:
            encrypted_manifest = MANIFEST_ENC.read_text()
            manifest_json = decrypt_message(encrypted_manifest, passphrase)
            stored_manifest = json.loads(manifest_json)
        except Exception:
            raise CommandError('❌ No se pudo descifrar el manifest. ¿Passphrase correcta pero archivo corrupto?')

        self.stdout.write(f'  → {len(stored_manifest)} archivos en el manifest')

        paso += 1
        self.stdout.write(f'[{paso}/{total}] Verificando integridad de archivos...')
        modified, missing = verify_file_integrity(stored_manifest, BASE_DIR)

        if missing:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Archivos faltantes: {len(missing)}'))
            for f in missing[:10]:
                self.stdout.write(f'    - {f}')
            if len(missing) > 10:
                self.stdout.write(f'    ... y {len(missing) - 10} más')

        if modified:
            self.stdout.write(self.style.ERROR(f'  ❌ Archivos modificados: {len(modified)}'))
            for f in modified[:10]:
                self.stdout.write(f'    - {f}')
            if len(modified) > 10:
                self.stdout.write(f'    ... y {len(modified) - 10} más')

        all_ok = not modified and not missing
        if all_ok:
            self.stdout.write(self.style.SUCCESS('  ✓ Todos los archivos intactos'))
        else:
            self.stdout.write()
            self.stdout.write(self.style.WARNING('Si los cambios fueron legítimos, ejecuta:'))
            self.stdout.write(self.style.WARNING('  python manage.py resign_ownership'))

        paso += 1
        self.stdout.write(f'[{paso}/{total}] Actualizando registro de verificación...')
        signature = hash_file(OWNERSHIP_ENC)
        manifest_signature = hash_file(MANIFEST_ENC)
        verified_at = datetime.datetime.now().isoformat()
        save_ownership_data(signature, manifest_signature, verified_at)

        self.stdout.write()
        if all_ok:
            self.stdout.write(self.style.SUCCESS('✅ AUTORÍA VERIFICADA. Eres el propietario legítimo.'))
            self.stdout.write(self.style.SUCCESS(f'   Última verificación: {verified_at}'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  VERIFICACIÓN COMPLETADA CON ADVERTENCIAS.'))
            self.stdout.write(self.style.WARNING('   Revisa los archivos marcados arriba.'))
