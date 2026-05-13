import os
import sys
import hashlib
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from tickets.security_utils import (
    encrypt_message, generate_file_manifest, save_ownership_data,
    OWNERSHIP_ENC, MANIFEST_ENC, OWNERSHIP_MESSAGE, BASE_DIR, hash_file
)


class Command(BaseCommand):
    help = 'Configura el sistema de verificación de autoría por primera vez'

    def add_arguments(self, parser):
        parser.add_argument(
            '--passphrase',
            type=str,
            help='Passphrase para cifrar (omitir para ingreso interactivo)',
        )

    def handle(self, *args, **options):
        if OWNERSHIP_ENC.exists():
            raise CommandError(
                'El sistema de autoría ya está configurado.\n'
                'Si deseas reconfigurarlo, primero elimina:\n'
                f'  {OWNERSHIP_ENC}\n'
                f'  {MANIFEST_ENC}\n'
                f'  y el archivo .ownership_data.json\n'
                'Luego ejecuta: python manage.py resign_ownership'
            )

        passphrase = options.get('passphrase')
        if not passphrase:
            passphrase = self._prompt_passphrase()

        self.stdout.write('Generando manifest de archivos...')
        manifest = generate_file_manifest(BASE_DIR)
        self.stdout.write(f'  → {len(manifest)} archivos indexados')

        self.stdout.write('Cifrando mensaje de autoría...')
        encrypted_message = encrypt_message(OWNERSHIP_MESSAGE, passphrase)
        OWNERSHIP_ENC.parent.mkdir(parents=True, exist_ok=True)
        OWNERSHIP_ENC.write_text(encrypted_message)
        self.stdout.write(f'  → Guardado en: {OWNERSHIP_ENC}')

        self.stdout.write('Cifrando manifest de archivos...')
        import json
        manifest_json = json.dumps(manifest, indent=2, sort_keys=True)
        encrypted_manifest = encrypt_message(manifest_json, passphrase)
        MANIFEST_ENC.write_text(encrypted_manifest)
        self.stdout.write(f'  → Guardado en: {MANIFEST_ENC}')

        signature = hash_file(OWNERSHIP_ENC)
        manifest_signature = hash_file(MANIFEST_ENC)
        import datetime
        verified_at = datetime.datetime.now().isoformat()
        save_ownership_data(signature, manifest_signature, verified_at)

        self.stdout.write()
        self.stdout.write(self.style.SUCCESS('✅ Sistema de autoría configurado correctamente.'))
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('Mensaje almacenado:'))
        self.stdout.write(self.style.SUCCESS(f'  "{OWNERSHIP_MESSAGE}"'))
        self.stdout.write()
        self.stdout.write(self.style.WARNING('GUARDA BIEN TU PASSPHRASE. Sin ella no podrás verificar la autoría.'))
        self.stdout.write()
        self.stdout.write('Comandos disponibles:')
        self.stdout.write('  python manage.py verify_ownership   → Verificar autoría')
        self.stdout.write('  python manage.py resign_ownership   → Re-firmar después de cambios legítimos')

    def _prompt_passphrase(self):
        import getpass
        while True:
            p1 = getpass.getpass('Crea una passphrase secreta: ')
            if len(p1) < 8:
                self.stdout.write(self.style.ERROR('La passphrase debe tener al menos 8 caracteres.'))
                continue
            p2 = getpass.getpass('Confirma la passphrase: ')
            if p1 != p2:
                self.stdout.write(self.style.ERROR('Las passphrases no coinciden. Intenta de nuevo.'))
                continue
            return p1
