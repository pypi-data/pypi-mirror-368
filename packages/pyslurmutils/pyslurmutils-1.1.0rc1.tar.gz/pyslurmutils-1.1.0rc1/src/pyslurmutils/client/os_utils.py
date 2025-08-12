import os


def chmod(path) -> None:
    try:
        original_umask = os.umask(0)
        return os.chmod(path, mode=0o777)
    finally:
        os.umask(original_umask)


def makedirs(dirname: str) -> None:
    try:
        original_umask = os.umask(0)
        return os.makedirs(dirname, mode=0o777, exist_ok=True)
    finally:
        os.umask(original_umask)


def nfs_cache_refresh(dirname) -> str:
    # _ = os.listdir(dirname)  # not enough
    # _ = subprocess.run(["ls", "-l", dirname], check=False, text=True, capture_output=True)
    with os.scandir(dirname) as it:
        for entry in it:
            _ = entry.stat()  # This forces a fresh stat call, similar to "ls -l"
