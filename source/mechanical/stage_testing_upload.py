"""Upload only this mod's existing verified build to /testing, with pinned host key."""
from pathlib import Path
import hashlib, json, os, socket, uuid, zipfile
import paramiko

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT.parents[1] / 'Testing_local/FS25_PX150XL.zip'
REMOTE = '/testing/FS25_PX150XL.zip'
PIN = 'c86a73d27b4a323a048b5ba6831dc815'
PASSWORD = os.environ.get('FS25_SFTP_PASSWORD', '').strip()
if not PASSWORD:
    raise SystemExit('FS25_SFTP_PASSWORD is not available; no connection attempted.')
manifest = json.loads((ROOT / 'source/mechanical/local_build_manifest.json').read_text())
digest = hashlib.sha256(LOCAL.read_bytes()).hexdigest()
assert digest == manifest['sha256']
assert manifest['version'] == '2.4.0.0'
with zipfile.ZipFile(LOCAL) as archive:
    assert archive.testzip() is None

def remote_hash(sftp, name):
    sha = hashlib.sha256()
    with sftp.open(name, 'rb') as file:
        while data := file.read(1024*1024):
            sha.update(data)
    return sha.hexdigest()

transport = None
sftp = None
temporary = '/testing/.FS25_PX150XL.zip.upload-' + uuid.uuid4().hex
pending = False
try:
    transport = paramiko.Transport(socket.create_connection(('lux.cloudtb.com',22), timeout=30))
    transport.get_security_options().key_types = ['ecdsa-sha2-nistp521']
    transport.start_client(timeout=30)
    key = transport.get_remote_server_key()
    if key.get_name() != 'ecdsa-sha2-nistp521' or key.get_fingerprint().hex() != PIN:
        raise RuntimeError('SERVER HOST KEY MISMATCH: stopped before authentication/upload.')
    transport.auth_password('christopher', PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.get_channel().settimeout(60)
    sftp.stat('/testing')
    pending = True
    sftp.put(str(LOCAL), temporary, confirm=True)
    assert remote_hash(sftp, temporary) == digest, 'Temporary upload SHA-256 mismatch'
    sftp.posix_rename(temporary, REMOTE)
    pending = False
    final_hash = remote_hash(sftp, REMOTE)
    assert final_hash == digest, 'Final remote SHA-256 mismatch'
    report = {'version':manifest['version'], 'destination':REMOTE, 'bytes':sftp.stat(REMOTE).st_size,
              'sha256':final_hash, 'hostKeyVerified':True, 'validation':'temporary upload and final renamed file both SHA-256 readback matched local ZIP'}
    (ROOT / 'source/mechanical/testing_upload_manifest.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
finally:
    if pending and sftp:
        try: sftp.remove(temporary)
        except OSError: pass
    if sftp: sftp.close()
    if transport: transport.close()
