# Qrew_find_vlc.py
"""Centralized VLC library management and import handling"""

import os
import platform
import subprocess
import sys
import ctypes
from typing import Optional, Dict, Any

# Global VLC module reference
_vlc_module = None
_vlc_status = {
    "checked": False,
    "available": False,
    "error_message": None,
    "backend": "subprocess",  # Default fallback
}


def get_vlc_module():
    """
    Get the VLC module if available, None otherwise.
    This is the single point of VLC import for the entire application.
    """
    global _vlc_module, _vlc_status

    if not _vlc_status["checked"]:
        _check_and_import_vlc()

    return _vlc_module


def get_vlc_status() -> Dict[str, Any]:
    """Get the current VLC status including availability and any error messages"""
    global _vlc_status

    if not _vlc_status["checked"]:
        _check_and_import_vlc()

    return _vlc_status.copy()


def _check_and_import_vlc():
    """
    Internal function to check VLC availability and import if possible.
    Sets up the global _vlc_module and _vlc_status.
    """
    global _vlc_module, _vlc_status

    _vlc_status["checked"] = True

    # First, try to find VLC libraries
    lib_dir = find_vlc_lib_dir()

    if not lib_dir:
        # Check if VLC executable exists for subprocess fallback
        vlc_exe = _find_vlc_executable()  # You need to add this function

        if not vlc_exe:
            _vlc_status["available"] = False
            _vlc_status["error_message"] = {
                "title": "VLC Not Found<br>",
                "text": "Neither VLC libraries nor VLC application were found.<br>"
                "Please install VLC from https://www.videolan.org/",
            }
            _vlc_status["backend"] = None  # No backend available
            return

        _vlc_status["available"] = False
        _vlc_status["error_message"] = {
            "title": "VLC Libraries Not Found<br>",
            "text": "VLC libraries were not found in standard locations.<br>"
            "You can set the PATH environment variable to point to the VLC directory.<br>"
            "Playback will fall back to using the VLC application if available.",
        }
        _vlc_status["backend"] = "subprocess"
        return

    # Set up environment
    if not _setup_vlc_environment(lib_dir):
        return

    # Try to import vlc
    try:
        import vlc

        _vlc_module = vlc
        _vlc_status["available"] = True
        _vlc_status["backend"] = "libvlc"
        print(
            f"OK: VLC module imported successfully (version: {vlc.libvlc_get_version().decode()})"
        )
    except ImportError as e:
        _vlc_status["available"] = False
        _vlc_status["error_message"] = {
            "title": "VLC Import Error",
            "text": f"Failed to import python-vlc module: {e}<br><br>Falling back to VLC application.",
        }
        _vlc_status["backend"] = "subprocess"
        print(f"ERROR: Failed to import vlc: {e}")


def _setup_vlc_environment(lib_dir: str) -> bool:
    """Set up environment for VLC library loading"""
    system = platform.system()

    try:
        if system == "Windows":
            # Windows-specific setup
            lib_dir = os.path.normpath(lib_dir)

            # Add to DLL search path (Python 3.8+)
            try:
                os.add_dll_directory(lib_dir)
            except (AttributeError, OSError):
                pass

            # Add to PATH
            os.environ["PATH"] = lib_dir + os.pathsep + os.environ.get("PATH", "")

            # Set plugin path
            plugin_path = os.path.join(lib_dir, "plugins")
            if os.path.isdir(plugin_path):
                os.environ["VLC_PLUGIN_PATH"] = plugin_path
                print(f"SUCCESS: Set VLC_PLUGIN_PATH to {plugin_path}")

            # Test load the DLL
            dll_path = os.path.join(lib_dir, "libvlc.dll")
            if os.path.exists(dll_path):
                # Check Python architecture before loading
                python_arch = "64-bit" if sys.maxsize > 2**32 else "32-bit"
                print(f"Python architecture: {python_arch}")

                try:
                    ctypes.CDLL(dll_path)
                    print(f"SUCCESS: Successfully loaded {dll_path} with ctypes")
                    # Clear PYTHON_VLC_LIB_PATH if it points to a directory
                    # (python-vlc expects a file path here, not a directory)
                    if "PYTHON_VLC_LIB_PATH" in os.environ and os.path.isdir(
                        os.environ["PYTHON_VLC_LIB_PATH"]
                    ):
                        del os.environ["PYTHON_VLC_LIB_PATH"]
                    return True
                except (OSError, TypeError) as e:
                    print(f"FAILED: Failed to load libvlc.dll: {e}")
                    _handle_dll_load_error(dll_path, e)
                    return False

        elif system == "Darwin":
            # macOS setup
            os.environ["DYLD_LIBRARY_PATH"] = (
                lib_dir + os.pathsep + os.environ.get("DYLD_LIBRARY_PATH", "")
            )
            plugin_path = os.path.join(lib_dir, "..", "plugins")
            if os.path.isdir(plugin_path):
                os.environ["VLC_PLUGIN_PATH"] = plugin_path
                print(f"✅ Set VLC_PLUGIN_PATH to {plugin_path}")
            # Pre-load libvlccore.dylib - often required on macOS
            try:
                core_path = os.path.join(lib_dir, "libvlccore.dylib")
                if os.path.exists(core_path):
                    ctypes.CDLL(core_path)
                    print(f"✅ Pre-loaded {core_path}")
            except Exception as e:
                print(f"❌ Failed to pre-load libvlccore.dylib: {e}")

        elif system == "Linux":
            # Linux setup
            os.environ["LD_LIBRARY_PATH"] = (
                lib_dir + os.pathsep + os.environ.get("LD_LIBRARY_PATH", "")
            )

            # Find plugins
            for plugin_path in [
                os.path.join(lib_dir, "vlc/plugins"),
                "/usr/lib/x86_64-linux-gnu/vlc/plugins",
                "/usr/lib/vlc/plugins",
            ]:
                if os.path.isdir(plugin_path):
                    os.environ["VLC_PLUGIN_PATH"] = plugin_path
                    print(f"✅ Set VLC_PLUGIN_PATH to {plugin_path}")
                    break

        return True

    except (OSError, EnvironmentError, TypeError, AttributeError, ValueError) as e:
        global _vlc_status
        _vlc_status["error_message"] = {
            "title": "VLC Setup Error",
            "text": f"Failed to set up VLC environment: {e}",
        }
        return False


def _handle_dll_load_error(dll_path: str, error: Exception):
    """Handle DLL loading errors with architecture detection"""
    global _vlc_status

    error_message = f"Failed to load libvlc.dll: {error}"

    # Check architecture mismatch
    python_arch = "64-bit" if sys.maxsize > 2**32 else "32-bit"

    try:
        import struct

        with open(dll_path, "rb") as f:
            f.seek(0x3C)
            pe_offset = struct.unpack("<I", f.read(4))[0]
            f.seek(pe_offset + 4)
            machine_type = struct.unpack("<H", f.read(2))[0]
            vlc_arch = "64-bit" if machine_type == 0x8664 else "32-bit"
            print(f"VLC architecture: {vlc_arch}")

            if python_arch != vlc_arch:
                arch_message = f"Architecture mismatch: Python is {python_arch} but VLC is {vlc_arch}"
                print(f"FAILED: {arch_message}")
                error_message += f"<br><br>Architecture mismatch: Python is {python_arch} but VLC is {vlc_arch}"
                error_message += f"<br><br>Please install {python_arch} version of VLC."
    except (OSError, struct.error, ValueError) as e:
        print(f"Could not determine DLL architecture: {e}")
        pass

    _vlc_status["error_message"] = {"title": "VLC Library Error", "text": error_message}
    _vlc_status["backend"] = "subprocess"


def get_vlc_libraries():
    """Find VLC libraries for current platform to include in PyInstaller spec"""
    system = platform.system()
    binaries = []

    # Search environment variables first
    env_libs = find_vlc_from_env()
    for lib_path in env_libs:
        binaries.append((lib_path, "."))

    if system == "Windows":
        # Find Windows VLC location
        vlc_path = find_windows_vlc()
        if vlc_path:
            plugin_path = os.path.join(os.path.dirname(vlc_path), "plugins")
            binaries.append((vlc_path, "."))
            binaries.append(
                (os.path.join(os.path.dirname(vlc_path), "libvlccore.dll"), ".")
            )
            # Add plugins directory
            if os.path.exists(plugin_path):
                for root, _, files in os.walk(plugin_path):
                    for file in files:
                        if file.endswith(".dll"):
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(
                                os.path.dirname(full_path), os.path.dirname(plugin_path)
                            )
                            dest_dir = os.path.join("plugins", rel_path)
                            binaries.append((full_path, dest_dir))

    elif system == "Darwin":
        # macOS VLC location
        vlc_dir = "/Applications/VLC.app/Contents/MacOS"
        if os.path.exists(vlc_dir):
            lib_dir = os.path.join(vlc_dir, "lib")
            binaries.append((os.path.join(lib_dir, "libvlc.dylib"), "."))
            binaries.append((os.path.join(lib_dir, "libvlccore.dylib"), "."))
            # Add plugins directory
            plugins_dir = os.path.join(vlc_dir, "plugins")
            if os.path.exists(plugins_dir):
                for root, _, files in os.walk(plugins_dir):
                    for file in files:
                        if file.endswith(".dylib"):
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(
                                os.path.dirname(full_path), plugins_dir
                            )
                            dest_dir = os.path.join("plugins", rel_path)
                            binaries.append((full_path, dest_dir))

    elif system == "Linux":
        # Linux - try to find libvlc.so
        vlc_lib = find_linux_vlc()
        if vlc_lib:
            lib_dir = os.path.dirname(vlc_lib)
            vlc_core_lib = os.path.join(lib_dir, "libvlccore.so")
            if os.path.exists(vlc_core_lib):
                binaries.append((vlc_lib, "."))
                binaries.append((vlc_core_lib, "."))

            # Add plugins - common Linux paths
            plugins_dirs = [
                "/usr/lib/x86_64-linux-gnu/vlc/plugins",
                "/usr/lib/vlc/plugins",
                os.path.join(lib_dir, "vlc/plugins"),
            ]

            for plugins_dir in plugins_dirs:
                if os.path.exists(plugins_dir):
                    for root, _, files in os.walk(plugins_dir):
                        for file in files:
                            if file.endswith(".so"):
                                full_path = os.path.join(root, file)
                                rel_path = os.path.relpath(
                                    os.path.dirname(full_path), plugins_dir
                                )
                                dest_dir = os.path.join("plugins", rel_path)
                                binaries.append((full_path, dest_dir))
                    break  # Use first plugins directory found

    return binaries


def find_windows_vlc():
    """Find VLC executable on Windows"""
    try:
        import winreg

        for key in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                reg_key = winreg.OpenKey(key, r"Software\VideoLAN\VLC")
                install_dir = winreg.QueryValueEx(reg_key, "InstallDir")[0]
                vlc_exe = os.path.join(install_dir, "libvlc.dll")
                if os.path.exists(vlc_exe):
                    return vlc_exe
            except:
                pass
    except:
        pass

    # Try common locations
    common_locations = [
        os.path.join(
            os.environ.get("PROGRAMFILES", "C:\\Program Files"),
            "VideoLAN",
            "VLC",
            "libvlc.dll",
        ),
        os.path.join(
            os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
            "VideoLAN",
            "VLC",
            "libvlc.dll",
        ),
    ]

    for location in common_locations:
        if os.path.exists(location):
            return location

    return None


def find_linux_vlc():
    """Find libvlc.so on Linux systems"""
    common_locations = [
        "/usr/lib/x86_64-linux-gnu/libvlc.so",
        "/usr/lib/libvlc.so",
        "/usr/local/lib/libvlc.so",
    ]

    for location in common_locations:
        if os.path.exists(location):
            return location

    # Try to find using ldconfig
    try:
        result = subprocess.run(["ldconfig", "-p"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "libvlc.so" in line:
                parts = line.split(" => ")
                if len(parts) >= 2:
                    lib_path = parts[1].strip()
                    if os.path.exists(lib_path):
                        return lib_path
    except:
        pass

    return None


def find_vlc_lib_dir() -> Optional[str]:
    """
    Return the directory containing the main VLC library for the current platform.
    Searches environment variables first, then standard locations.

    Windows: libvlc.dll
    macOS: libvlc.dylib
    Linux: libvlc.so

    Returns None if not found.
    """
    system = platform.system()

    # First check environment variables
    env_libs = find_vlc_from_env()
    if env_libs:
        # Return directory of first found library from environment
        return os.path.dirname(env_libs[0])

    # If not found in environment, check standard locations
    if system == "Windows":
        lib_path = find_windows_vlc()
    elif system == "Darwin":
        lib_path = os.path.join(
            "/Applications/VLC.app/Contents/MacOS/lib", "libvlc.dylib"
        )
        if not os.path.exists(lib_path):
            # Try alternate macOS locations
            common_mac_locations = [
                "/usr/local/lib/libvlc.dylib",
                os.path.expanduser(
                    "~/Applications/VLC.app/Contents/MacOS/lib/libvlc.dylib"
                ),
            ]
            for loc in common_mac_locations:
                if os.path.exists(loc):
                    lib_path = loc
                    break
            else:
                lib_path = None
    elif system == "Linux":
        lib_path = find_linux_vlc()
    else:
        lib_path = None

    if lib_path:
        return os.path.dirname(lib_path)
    return None


def find_vlc_from_env():
    """Search for VLC libraries using environment variables."""
    candidates = []
    env_vars = [
        "VLC_PLUGIN_PATH",
        "VLC_PATH",
        "PYTHON_VLC_LIB_PATH",
        "PATH",
        "Path",
        "LD_LIBRARY_PATH",
        "DYLD_LIBRARY_PATH",
    ]
    lib_names = {
        "Windows": ["libvlc.dll", "libvlccore.dll"],
        "Darwin": ["libvlc.dylib", "libvlccore.dylib"],
        "Linux": ["libvlc.so", "libvlccore.so"],
    }
    system = platform.system()
    for var in env_vars:
        paths = os.environ.get(var, "")
        for p in paths.split(os.pathsep):
            for lib in lib_names.get(system, []):
                lib_path = os.path.join(p, lib)
                if os.path.exists(lib_path):
                    candidates.append(lib_path)
    return candidates


def _find_vlc_executable() -> Optional[str]:
    """
    Comprehensive cross-platform VLC executable finder

    Returns:
        str: Path to VLC executable or 'vlc' if found in PATH
        None: If no VLC executable found
    """
    import shutil

    # Try PATH first (most reliable method)
    vlc_path = shutil.which("vlc")
    if vlc_path:
        return vlc_path

    system = platform.system()

    # Expanded macOS search paths
    if system == "Darwin":
        possible_paths = [
            "/Applications/VLC.app/Contents/MacOS/VLC",
            "/opt/homebrew/bin/vlc",
            "/usr/local/bin/vlc",
            "/Applications/VLC.app/Contents/MacOS/VLC.app/Contents/MacOS/VLC",
            os.path.expanduser("~/Applications/VLC.app/Contents/MacOS/VLC"),
            "/Applications/VLC.app/Contents/MacOS/VLC",
        ]

    # Expanded Windows search paths
    elif system == "Windows":
        possible_drives = ["C:", "D:"]
        possible_program_files = [
            os.environ.get("PROGRAMFILES", "C:\\Program Files"),
            os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
        ]
        possible_paths = []
        for drive in possible_drives:
            for pf in possible_program_files:
                possible_paths.extend(
                    [
                        rf"{pf}\VideoLAN\VLC\vlc.exe",
                        rf"{drive}\Program Files\VideoLAN\VLC\vlc.exe",
                        rf"{drive}\Program Files (x86)\VideoLAN\VLC\vlc.exe",
                    ]
                )

    # Expanded Linux search paths
    elif system == "Linux":
        possible_paths = [
            "/usr/bin/vlc",
            "/usr/local/bin/vlc",
            "/snap/bin/vlc",
            "/opt/vlc/bin/vlc",
            os.path.expanduser("~/.local/bin/vlc"),
        ]

    else:
        possible_paths = []

    # Additional PATH search
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    possible_paths.extend([os.path.join(path_dir, "vlc") for path_dir in path_dirs])

    # Check each possible path
    for p in possible_paths:
        # Expand user directory and normalize path
        full_path = os.path.abspath(os.path.expanduser(p))
        if os.path.exists(full_path) and os.access(full_path, os.X_OK):
            return full_path

    return None
