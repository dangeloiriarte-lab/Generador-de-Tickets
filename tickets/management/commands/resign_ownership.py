import json
import datetime
from django.core.management.base import BaseCommand, CommandError
from tickets.security_utils import (
    decrypt_message, encrypt_message, generate_file_manifest,
    save_ownership_data, hash_file,
    OWNERSHIP_ENC, MANIFEST_ENC, OWNERSHIP_MESSAGE, BASE_DIR
)


class Command(BaseCommand):
    help = 'Re-firma el manifest después de cambios legítimos en el código'

    def add_arguments(self, parser):
        parser.add_argument(
            '--passphrase',
            type=str,
            help='Passphrase para descifrar (omitir para ingreso interactivo)',
        )

    def handle(self, *args, **options):
        if not OWNERSHIP_ENC.exists():
            raise CommandError(
                'El sistema de autoría no está configurado.\n'
                'Ejecuta primero: python manage.py setup_ownership'
            )

        passphrase = options.get('passphrase')
        if not passphrase:
            import getpass
            passphrase = getpass.getpass('Introduce tu passphrase: ')

        self.stdout.write('Verificando identidad...')
        try:
            encrypted_message = OWNERSHIP_ENC.read_text()
            decrypted_message = decrypt_message(encrypted_message, passphrase)
        except Exception:
            raise CommandError('❌ Passphrase incorrecta.')

        if decrypted_message != OWNERSHIP_MESSAGE:
            if not self._confirm('⚠️  El mensaje no coincide. ¿Re-firmar de todas formas?'):
                return

        self.stdout.write(self.style.SUCCESS(f'  ✓ Identidad verificada: "{decrypted_message}"'))

        self.stdout.write('Regenerando manifest con archivos actuales...')
        new_manifest = generate_file_manifest(BASE_DIR)
        self.stdout.write(f'  → {len(new_manifest)} archivos indexados')

        self.stdout.write('Cifrando nuevo manifest...')
        new_manifest_json = json.dumps(new_manifest, indent=2, sort_keys=True)
        encrypted_manifest = encrypt_message(new_manifest_json, passphrase)
        MANIFEST_ENC.write_text(encrypted_manifest)

        signature = hash_file(OWNERSHIP_ENC)
        manifest_signature = hash_file(MANIFEST_ENC)
        verified_at = datetime.datetime.now().isoformat()
        save_ownership_data(signature, manifest_signature, verified_at)

        self.stdout.write()
        self.stdout.write(self.style.SUCCESS('✅ MANIFEST ACTUALIZADO Y RE-FIRMADO correctamente.'))
        self.stdout.write(self.style.SUCCESS(f'   Última verificación: {verified_at}'))
        self.stdout.write()
        self.stdout.write(self.style.WARNING('Recuerda ejecutar "verify_ownership" periódicamente para verificar integridad.'))
