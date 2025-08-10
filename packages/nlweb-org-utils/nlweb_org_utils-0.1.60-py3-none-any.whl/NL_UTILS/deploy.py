# USAGE: python3 playbooks/deploy.py

#!/usr/bin/env python3
import re, subprocess, sys, shutil, pathlib, time

# --- Config ---
PACKAGE_NAME = "nlweb-org-utils"   # project.name in pyproject.toml
IMPORT_CHECK  = "import NL_UTILS.hello"
HELLO_PATHS = [
    pathlib.Path("hello.py"),
    pathlib.Path("src/NL_UTIL/hello.py"),
]
PYPROJECT = pathlib.Path("pyproject.toml")
DIST_DIR = pathlib.Path("dist")

RETRY_ATTEMPTS = 6        # total tries incl. first install (e.g., ~1 minute of retries)
RETRY_DELAY_SEC = 10      # seconds between retries (with countdown)

# --- Utils ---
def read(path): return path.read_text(encoding="utf-8")
def write(path, s): path.write_text(s, encoding="utf-8")

def sh(*args):
    print("+", " ".join(args))
    subprocess.check_call(args)

def bump_patch(v: str) -> str:
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", v.strip())
    if not m: raise ValueError(f"Version not semver patch format: {v}")
    major, minor, patch = map(int, m.groups())
    return f"{major}.{minor}.{patch+1}"

def update_pyproject():
    txt = read(PYPROJECT)
    m = re.search(r'(?m)^\s*version\s*=\s*"([^"]+)"\s*$', txt)
    if not m: raise RuntimeError("version not found in pyproject.toml")
    old = m.group(1)
    new = bump_patch(old)
    txt = txt[:m.start(1)] + new + txt[m.end(1):]
    write(PYPROJECT, txt)
    print(f"[version] {old} -> {new} in pyproject.toml")
    return old, new

def update_hello(new_version: str):
    hello_path = next((p for p in HELLO_PATHS if p.exists()), None)
    if not hello_path:
        raise Exception("[warn] hello.py not found; skipping hello() string sync")
        return
    txt = read(hello_path)
    # Replace 'version X.Y.Z' inside return string, if present
    new_txt, n = re.subn(
        r'(return\s+".*?version\s+)(\d+\.\d+\.\d+)(!?"\))',
        rf"\g<1>{new_version}\g<3>",
        txt,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if n == 0:
        # Fallback: replace first X.Y.Z in file
        new_txt, n = re.subn(r'(\d+\.\d+\.\d+)', new_version, txt, count=1)
    if n > 0:
        write(hello_path, new_txt)
        print(f"[hello.py] synced embedded version -> {new_version}")
    else:
        print("[warn] did not update hello.py (pattern not found)")

def ensure_tools():
    sh(sys.executable, "-m", "pip", "install", "--upgrade", "build", "twine")

def clean_dist():
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
        print("[clean] removed dist/")

def build():
    sh(sys.executable, "-m", "build")

def upload_testpypi():
    sh("twine", "upload", "--verbose", 
       #"--repository", "testpypi", 
       "dist/*")

def countdown(seconds: int, prefix: str = "Waiting"):
    for i in range(seconds, 0, -1):
        print(f"{prefix}: {i}s", end="\r", flush=True)
        time.sleep(1)
    print(" " * 40, end="\r")

def installed_version(pkg: str) -> str | None:
    try:
        # Python 3.8+: importlib.metadata
        try:
            from importlib.metadata import version, PackageNotFoundError  # type: ignore
        except Exception:  # pragma: no cover
            from importlib_metadata import version, PackageNotFoundError  # backport
        return version(pkg)
    except Exception:
        return None

def pip_install_from_testpypi():
    sh(sys.executable, "-m", "pip", "install", "--no-cache-dir", "--force-reinstall",
       #"-i", "https://test.pypi.org/simple/", 
       PACKAGE_NAME)

def run_import_check():
    sh(sys.executable, "-c", IMPORT_CHECK)

def main():
    if not PYPROJECT.exists():
        print("pyproject.toml not found. Run from the project root.")
        sys.exit(1)

    old, new = update_pyproject()
    update_hello(new)

    ensure_tools()
    clean_dist()
    build()
    upload_testpypi()

    print("\nUpload complete!")
    print(f"Target version: {new}")
    print("Next: install & test in 10 seconds...\n")
    countdown(10, prefix="Starting")

    # Try initial install + check, then retries if mismatch
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        print(f"[attempt {attempt}/{RETRY_ATTEMPTS}] Installing from TestPyPI…")
        pip_install_from_testpypi()

        iv = installed_version(PACKAGE_NAME)
        print(f"Installed version detected: {iv!r}")

        if iv == new:
            print("[ok] Installed version matches uploaded version.")
            run_import_check()
            break

        if attempt < RETRY_ATTEMPTS:
            print(f"[wait] Version {iv!r} != {new!r}. "
                  f"Repository index may not be consistent yet.")
            countdown(RETRY_DELAY_SEC, prefix=f"Retrying in")
        else:
            print(f"[fail] Gave up after {RETRY_ATTEMPTS} attempts. "
                  f"Installed {iv!r}, expected {new!r}.")
            sys.exit(2)

if __name__ == "__main__":
    main()
