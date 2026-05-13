import os
import json
import base64
import hashlib
from pathlib import Path

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


BASE_DIR = Path(__file__).resolve().parent.parent
OWNERSHIP_ENC = BASE_DIR / 'tickets' / 'ownership.enc'
MANIFEST_ENC = BASE_DIR / 'tickets' / 'manifest.enc'
OWNERSHIP_DATA = BASE_DIR / 'tickets' / '.ownership_data.json'
OWNERSHIP_MESSAGE = "Autores Materiales e Intelectuales de este proyecto son el Ing. D'angelo Iriarte y el Ing. Jonathan Vargas"

SALT = b'ticket_ownership_salt_v1'


def _derive_key(passphrase: str) -> bytes:
    if not CRYPTOGRAPHY_AVAILABLE:
        raise ImportError('La librería "cryptography" no está instalada. Ejecuta: pip install cryptography')
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode('utf-8')))
    return key


def encrypt_message(message: str, passphrase: str) -> str:
    key = _derive_key(passphrase)
    f = Fernet(key)
    token = f.encrypt(message.encode('utf-8'))
    return token.decode('utf-8')


def decrypt_message(ciphertext: str, passphrase: str) -> str:
    key = _derive_key(passphrase)
    f = Fernet(key)
    plaintext = f.decrypt(ciphertext.encode('utf-8'))
    return plaintext.decode('utf-8')


def generate_file_manifest(base_dir: Path) -> dict:
    manifest = {}
    extensions = ('.py', '.html', '.css', '.js', '.sql', '.sh', '.txt', '.md', '.yml', '.yaml', '.cfg', '.ini', '.conf')
    exclude_dirs = {'.venv', '__pycache__', '.git', '.vscode', 'pdf_cache', 'staticfiles', '.git'}
    exclude_files = {'db.sqlite3', 'ownership.enc', 'manifest.enc', '.ownership_data.json', '.env'}

    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file in exclude_files:
                continue
            if file.endswith('.pyc'):
                continue
            ext = Path(file).suffix
            if ext not in extensions and not file.endswith('.py'):
                continue
            filepath = Path(root) / file
            try:
                rel_path = str(filepath.relative_to(base_dir))
                file_hash = hashlib.sha256(filepath.read_bytes()).hexdigest()
                manifest[rel_path] = file_hash
            except (OSError, ValueError):
                continue

    return manifest


def verify_file_integrity(manifest: dict, base_dir: Path) -> tuple:
    modified = []
    missing = []
    for rel_path, expected_hash in manifest.items():
        filepath = base_dir / rel_path
        if not filepath.exists():
            missing.append(rel_path)
            continue
        try:
            current_hash = hashlib.sha256(filepath.read_bytes()).hexdigest()
            if current_hash != expected_hash:
                modified.append(rel_path)
        except OSError:
            modified.append(rel_path)
    return modified, missing


def save_ownership_data(signature: str, manifest_signature: str, verified_at: str = ''):
    data = {
        'signature': signature,
        'manifest_signature': manifest_signature,
        'verified_at': verified_at,
    }
    OWNERSHIP_DATA.parent.mkdir(parents=True, exist_ok=True)
    OWNERSHIP_DATA.write_text(json.dumps(data, indent=2))


def load_ownership_data() -> dict:
    if not OWNERSHIP_DATA.exists():
        return {}
    try:
        return json.loads(OWNERSHIP_DATA.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def is_ownership_configured() -> bool:
    return OWNERSHIP_ENC.exists() and MANIFEST_ENC.exists()


def hash_file(filepath: Path) -> str:
    if not filepath.exists():
        return ''
    return hashlib.sha256(filepath.read_bytes()).hexdigest()
