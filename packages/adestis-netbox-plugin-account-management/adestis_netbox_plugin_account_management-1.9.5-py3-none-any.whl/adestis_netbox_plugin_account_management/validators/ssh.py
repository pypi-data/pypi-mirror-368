import paramiko
import paramiko.pkey


def validate_ssh_key(key: str) -> bool:
    try:
        paramiko.pkey.PublicBlob.from_string(key)
        return True
    except Exception as e:
        return False
