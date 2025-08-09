# src/CTPv/wx_helper.py
import platform
import subprocess
import sys
import importlib

def get_wxpython_url():
    try:
        with open('/etc/os-release', 'r') as f:
            for line in f:
                if line.startswith('VERSION_ID'):
                    ver_id = line.split('=')[1].strip().strip('"')
                    major_minor = ver_id.split('.')[:2]
                    major, minor = int(major_minor[0]), int(major_minor[1])

                    # Round down to nearest .04 LTS
                    if minor < 4:
                        # Use previous major's .04 (e.g., 23.02 → 22.04)
                        lts_version = f"{major - 1}.04"
                    else:
                        # Round down to .04 of current major (e.g., 20.10 → 20.04)
                        lts_version = f"{major}.04"

                    # Known supported wxPython LTS versions (as of 2024)
                    supported = ["18.04", "20.04", "22.04", "24.04", "25.04", "26.04", "27.04", "28.04"]

                    # Use latest supported if our computed one isn't available
                    if lts_version not in supported:
                        # Find latest supported <= major version
                        candidates = [
                            v for v in supported
                            if int(v.split('.')[0]) <= major
                        ]
                        if not candidates:
                            return None  # Too old
                        lts_version = max(candidates)  # e.g., "22.04"

                    return f"https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-{lts_version}"
    except Exception as e:
        print(f"Could not detect OS version: {e}")
        return None
    return None

def ensure_wxpython():
    try:
        import wx
        return True
    except ImportError:
        print("wxPython not found. Attempting to install...")

    system = platform.system().lower()

    if system == "linux":
        url = get_wxpython_url()
        if url:
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "-U",
                    "-f", url,
                    "wxPython"
                ])
                print("wxPython installed successfully.")
                return True
            except subprocess.CalledProcessError:
                print(f"Failed to install wxPython from {url}")
                suggest_manual_install()
                return False
        else:
            print("No compatible wxPython wheel URL found for this Linux version.")
            suggest_manual_install()
            return False

    elif system in ["windows", "darwin"]:
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-U", "wxPython"
            ])
            print("wxPython installed successfully.")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install wxPython via pip.")
            suggest_manual_install()
            return False
    else:
        print(f"Unsupported OS: {system}")
        suggest_manual_install()
        return False


def get_ubuntu_version():
    try:
        with open('/etc/os-release') as f:
            for line in f:
                if line.startswith("VERSION_ID"):
                    return line.split("=")[1].strip().strip('"')
    except Exception:
        pass
    return None


def suggest_manual_install():
    system = platform.system().lower()
    if system == "linux":
        print("Please install wxPython manually using:")
        print("  pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython")
        print("Replace 'ubuntu-20.04' with your version if needed.")
    else:
        print("Please run: pip install -U wxPython")


# Optional: auto-run on import
if __name__ == "__main__":
    ensure_wxpython()