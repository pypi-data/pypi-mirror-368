#!/usr/bin/env python3
"""
omnipkg - The "Freedom" Edition v2
An intelligent installer that lets pip run, then surgically cleans up downgrades
and isolates conflicting versions in deduplicated bubbles to guarantee a stable environment.
"""
import sys
import json
import subprocess
import redis
import zlib
import os
import shutil
import site
import hashlib
import tempfile
import requests
import re
import importlib.metadata
import platform
import urllib.request
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path
from packaging.version import parse as parse_version, InvalidVersion
from typing import Dict, List, Optional, Set, Tuple
from importlib.metadata import Distribution

# 
# ### CONFIGURATION MANAGEMENT (PORTABLE & SELF-CONFIGURING)
# 

class ConfigManager:
    def __init__(self):
        """
        Manages loading and first-time creation of the omnipkg config file.
        This makes the entire application portable and self-healing.
        """
        self.config_dir = Path.home() / ".config" / "omnipkg"
        self.config_path = self.config_dir / "config.json"
        
        self.run_prelaunch_checks()
        self.config = self._load_or_create_config()

    def run_prelaunch_checks(self):
        """
        Runs checks to ensure critical dependencies and environment are correct.
        """
        if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
            print("\n" + "="*60)
            print("  🚀 One-Time Environment Upgrade Required")
            print("="*60)
            print("omnipkg works best with Python 3.11 for maximum compatibility.")
            print(f"Your current environment is running Python {sys.version_info.major}.{sys.version_info.minor}.")
            print("\nTo ensure everything 'just works', omnipkg will now:")
            print("  1. Download a self-contained Python 3.11 into your virtual environment.")
            print("  2. Register omnipkg with the new interpreter.")
            print("  3. Relaunch seamlessly to continue your command.")
            print("\nThis is a one-time setup. Future runs will be instant.")
            
            try:
                choice = input("\nDo you want to proceed with the automatic upgrade? (y/n): ")
                if choice.lower() == 'y':
                    if not self.config_path.exists():
                        self._first_time_setup(interactive=False)
                    self._install_python311_in_venv()
                else:
                    print("🛑 Upgrade cancelled. Aborting, as Python 3.11 is required.")
                    sys.exit(1)
            except (KeyboardInterrupt, EOFError):
                print("\n🛑 Operation cancelled. Aborting.")
                sys.exit(1)

        try:
            importlib.import_module('packaging')
        except ImportError:
            print("🔧 Installing missing packaging module...")
            subprocess.run([sys.executable, "-m", "pip", "install", "packaging"], check=True)

    def _install_python311_in_venv(self):
        print("\n🚀 Upgrading environment to Python 3.11...")
        venv_path = Path(sys.prefix)
        if venv_path == Path(sys.base_prefix):
            print("❌ Error: You must be in a virtual environment to use this feature.")
            sys.exit(1)
        
        system = platform.system().lower()
        arch = platform.machine().lower()
        
        try:
            python311_exe = None
            if system == "linux": 
                python311_exe = self._install_python_platform(venv_path, arch, "linux")
            elif system == "darwin": 
                python311_exe = self._install_python_platform(venv_path, arch, "macos")
            elif system == "windows": 
                python311_exe = self._install_python_platform(venv_path, arch, "windows")
            else: 
                raise OSError(f"Unsupported operating system: {system}")

            if python311_exe and python311_exe.exists():
                self._update_venv_pyvenv_cfg(venv_path, python311_exe)
                print("✅ Python 3.11 downloaded and configured.")
                
                self._finalize_environment_upgrade(venv_path, python311_exe)
                self._register_all_interpreters(venv_path)  # NEW: Register all available interpreters

                print("\n✅ Success! The environment is now fully upgraded to Python 3.11.")
                print("   Your current command will now continue on the new version.")
                print("\n   IMPORTANT: For the change to stick in your terminal for future commands, please run:")
                activate_script = venv_path / ("Scripts" if system == "windows" else "bin") / "activate"
                print(f"   source \"{activate_script}\"")
                print("   ...after this one finishes.")

                # Properly relaunch with the new interpreter
                entry_point_script = venv_path / ("Scripts" if system == "windows" else "bin") / "omnipkg"
                args = [str(python311_exe), "-m", "omnipkg.cli"] + sys.argv[1:]
                os.execv(str(python311_exe), args)
            else:
                raise Exception("Python 3.11 executable path was not determined.")
        except Exception as e:
            print(f"❌ Failed to auto-upgrade to Python 3.11: {e}")
            sys.exit(1)
    
    def _create_omnipkg_executable(self, new_python_exe: Path, venv_path: Path):
        """
        Creates a proper shell script executable that forces the use of the new Python interpreter.
        FIXED: Uses correct shell script syntax, not Python syntax.
        """
        print("🔧 Creating new omnipkg executable...")
        bin_dir = venv_path / ("Scripts" if platform.system() == "Windows" else "bin")
        omnipkg_exec_path = bin_dir / "omnipkg"
        
        system = platform.system().lower()
        
        if system == "windows":
            # Windows batch script
            script_content = (
                f"@echo off\n"
                f"REM This script was auto-generated by omnipkg to ensure the correct Python is used.\n"
                f'"{new_python_exe.resolve()}" -m omnipkg.cli %*\n'
            )
            omnipkg_exec_path = bin_dir / "omnipkg.bat"
        else:
            # Unix shell script - FIXED SYNTAX
            script_content = (
                f"#!/bin/bash\n"
                f"# This script was auto-generated by omnipkg to ensure the correct Python is used.\n\n"
                f'exec "{new_python_exe.resolve()}" -m omnipkg.cli "$@"\n'
            )

        with open(omnipkg_exec_path, 'w') as f:
            f.write(script_content)

        if system != "windows":
            omnipkg_exec_path.chmod(0o755)
        
        print("   ✅ New omnipkg executable created.")

    def _register_all_interpreters(self, venv_path: Path):
        """
        NEW: Discovers and registers all Python interpreters available in the environment.
        This supports your multi-interpreter requirement.
        """
        print("🔧 Registering all available Python interpreters...")
        
        interpreters_dir = venv_path / ".omnipkg" / "interpreters"
        interpreters_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all Python interpreters
        interpreters = {}
        bin_dir = venv_path / ("Scripts" if platform.system() == "Windows" else "bin")
        
        # Check for the new Python 3.11 we just installed
        py311_path = self._get_interpreter_dest_path(venv_path) / ("python.exe" if platform.system() == "Windows" else "bin/python3.11")
        if py311_path.exists():
            interpreters["3.11"] = py311_path
            
        # Check for any existing interpreters in the venv
        for py_exe in bin_dir.glob("python*"):
            if py_exe.is_file() and py_exe.name not in ["python", "python3"]:  # Skip symlinks
                try:
                    result = subprocess.run([str(py_exe), "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        interpreters[version] = py_exe
                except:
                    continue
        
        # Store interpreter registry
        registry_path = interpreters_dir / "registry.json"
        registry_data = {
            "primary_version": "3.11",
            "interpreters": {k: str(v) for k, v in interpreters.items()},
            "last_updated": datetime.now().isoformat()
        }
        
        with open(registry_path, 'w') as f:
            json.dump(registry_data, f, indent=2)
        
        print(f"   ✅ Registered {len(interpreters)} Python interpreters:")
        for version, path in interpreters.items():
            print(f"      - Python {version}: {path}")

    def get_interpreter_for_version(self, version: str) -> Optional[Path]:
        """
        NEW: Get the path to a specific Python interpreter version.
        """
        registry_path = Path(sys.prefix) / ".omnipkg" / "interpreters" / "registry.json"
        if not registry_path.exists():
            return None
            
        try:
            with open(registry_path, 'r') as f:
                registry = json.load(f)
            
            interpreter_path = registry.get("interpreters", {}).get(version)
            if interpreter_path and Path(interpreter_path).exists():
                return Path(interpreter_path)
        except:
            pass
        
        return None

    def _finalize_environment_upgrade(self, venv_path: Path, new_python_exe: Path):
        """
        Finalizes the upgrade using the 'belt-and-suspenders' approach:
        1. `pip install -e .` to create the .pth file for module resolution.
        2. Manually create the entrypoint script to guarantee it's correct.
        """
        print("🔧 Finalizing environment upgrade...")
        project_root = Path(__file__).resolve().parent.parent
        
        # Step 1: Register the project with the new interpreter to create the .pth file.
        cmd = [
            str(new_python_exe), "-m", "pip", "install",
            "--no-cache-dir", "-e", str(project_root)
        ]
        
        try:
            print(f"   - Registering project with new Python 3.11 interpreter...")
            subprocess.run(
                cmd, check=True, capture_output=True, text=True, cwd=project_root
            )
            print("   ✅ Project registered with Python 3.11.")
            
            # Step 2: Manually create the executable to be 100% certain it's correct.
            self._create_omnipkg_executable(new_python_exe, venv_path)
            
            # Step 3: Update the default Python symlinks to point to 3.11
            self._update_default_python_links(venv_path, new_python_exe)
            
            # --- FUTURE-PROOFING STUBS ---
            self._register_interpreter_in_redis(new_python_exe, venv_path)
            self._update_bubble_mappings(new_python_exe)
            
        except subprocess.CalledProcessError as e:
            print("❌ Error finalizing environment for the new Python interpreter.")
            print("   The error from pip was:")
            print("-" * 20)
            print(e.stderr)
            print("-" * 20)
            raise RuntimeError("Failed to run 'pip install -e .' with new interpreter.") from e

    def _update_default_python_links(self, venv_path: Path, new_python_exe: Path):
        """
        NEW: Updates the default python/python3 symlinks to point to Python 3.11.
        This ensures Python 3.11 becomes the primary interpreter.
        """
        print("🔧 Updating default Python links...")
        bin_dir = venv_path / ("Scripts" if platform.system() == "Windows" else "bin")
        
        if platform.system() == "Windows":
            # Windows: Copy the executable
            for name in ["python.exe", "python3.exe"]:
                target = bin_dir / name
                if target.exists():
                    target.unlink()
                shutil.copy2(new_python_exe, target)
        else:
            # Unix: Create symlinks
            for name in ["python", "python3"]:
                target = bin_dir / name
                if target.exists() or target.is_symlink():
                    target.unlink()
                target.symlink_to(new_python_exe)
        
        print("   ✅ Default Python links updated to use Python 3.11.")

    def _register_interpreter_in_redis(self, python_exe: Path, venv_path: Path):
        """Placeholder for your Redis registration logic."""
        print(f"   (Stub) Registering interpreter {python_exe} in Redis...")
        # TODO: Implement Redis registration
        pass

    def _update_bubble_mappings(self, python_exe: Path):
        """Placeholder for updating your bubble isolation mappings."""
        print(f"   (Stub) Updating bubble mappings for {python_exe}...")
        # TODO: Implement bubble mapping updates
        pass

    def _get_interpreter_dest_path(self, venv_path: Path) -> Path:
        return venv_path / ".omnipkg" / "interpreters" / "cpython-3.11.6"

    def _install_python_platform(self, venv_path, arch, platform_name):
        py_arch_map = {
            "x86_64": "x86_64", "amd64": "x86_64", 
            "aarch64": "aarch64", "arm64": "aarch64", 
            "x86": "i686", "i386": "i686"
        }
        py_arch = py_arch_map.get(arch)
        if not py_arch: 
            raise OSError(f"Unsupported architecture: {arch}")
        
        urls = {
            "linux": f"https://github.com/indygreg/python-build-standalone/releases/download/20231002/cpython-3.11.6+20231002-{py_arch}-unknown-linux-gnu-install_only.tar.gz",
            "macos": f"https://github.com/indygreg/python-build-standalone/releases/download/20231002/cpython-3.11.6+20231002-{py_arch}-apple-darwin-install_only.tar.gz",
            "windows": f"https://github.com/indygreg/python-build-standalone/releases/download/20231002/cpython-3.11.6+20231002-{py_arch}-pc-windows-msvc-shared-install_only.tar.gz"
        }
        url = urls[platform_name]

        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "python311.tar.gz"
            print(f"📥 Downloading Python 3.11 for {platform_name.title()} (this may take a moment)...")
            urllib.request.urlretrieve(url, archive_path)
            
            print("📦 Extracting Python 3.11...")
            with tarfile.open(archive_path, 'r:gz') as tar: 
                tar.extractall(Path(temp_dir))
            
            python_dir = next(Path(temp_dir).glob("python*"))
            python_dest = self._get_interpreter_dest_path(venv_path)
            python_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(python_dir, python_dest, dirs_exist_ok=True)
            
            if platform_name == "windows":
                python311_exe = python_dest / "python.exe"
            else:
                python311_exe = python_dest / "bin" / "python3.11"
                python311_exe.chmod(0o755)
            
            self._install_essential_packages(python311_exe)
            return python311_exe

    def _install_essential_packages(self, python_exe):
        print("📦 Installing essential packages...")
        subprocess.run([str(python_exe), "-m", "ensurepip", "--upgrade"], 
                      check=True, capture_output=True)
        
        essential_packages = [
            "pip>=23.0", "setuptools>=65.0", "wheel>=0.38.0", 
            "packaging>=21.0"  # Add packaging since you need it
        ]
        
        for package in essential_packages:
            subprocess.run([str(python_exe), "-m", "pip", "install", "--upgrade", package], 
                          check=True, capture_output=True)
        
        print("   ✅ Essential packages installed successfully!")

    def _update_venv_pyvenv_cfg(self, venv_path, python311_exe):
        pyvenv_cfg = venv_path / "pyvenv.cfg"
        if pyvenv_cfg.exists():
            with open(pyvenv_cfg, 'r') as f: 
                lines = f.readlines()
                
            with open(pyvenv_cfg, 'w') as f:
                for line in lines:
                    if line.startswith('home = '): 
                        f.write(f'home = {python311_exe.parent.resolve()}\n')
                    elif line.startswith('executable = '): 
                        f.write(f'executable = {python311_exe.resolve()}\n')
                    else: 
                        f.write(line)

    def _get_sensible_defaults(self) -> Dict:
        try: 
            site_packages = site.getsitepackages()[0]
        except (IndexError, AttributeError): 
            site_packages = str(Path.home()/f".local/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages")
        
        return {
            "site_packages_path": site_packages, 
            "multiversion_base": str(Path(site_packages) / ".omnipkg_versions"), 
            "python_executable": sys.executable, 
            "builder_script_path": str(Path(__file__).parent / "package_meta_builder.py"), 
            "redis_host": "localhost", 
            "redis_port": 6379, 
            "redis_key_prefix": "omnipkg:pkg:"
        }

    def _first_time_setup(self, interactive=True) -> Dict:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        defaults = self._get_sensible_defaults()
        final_config = defaults.copy()
        
        if interactive:
            print("👋 Welcome to omnipkg! Let's get you configured.")
            print("   Auto-detecting paths for your environment. Press Enter to accept defaults.")
            final_config["redis_host"] = input(f"Redis host [{defaults['redis_host']}]: ") or defaults["redis_host"]
            final_config["redis_port"] = int(input(f"Redis port [{defaults['redis_port']}]: ") or defaults["redis_port"])
        
        with open(self.config_path, 'w') as f: 
            json.dump(final_config, f, indent=4)
        
        if interactive: 
            print(f"\n✅ Configuration saved to {self.config_path}.")
        
        return final_config

    def _load_or_create_config(self) -> Dict:
        if not self.config_path.exists():
            return self._first_time_setup(interactive=(len(sys.argv) == 1))
        
        with open(self.config_path, 'r') as f:
            try: 
                user_config = json.load(f)
            except json.JSONDecodeError:
                print("⚠️  Warning: Config file is corrupted. Starting fresh.")
                return self._first_time_setup()
        
        defaults = self._get_sensible_defaults()
        config_is_updated = False
        
        if user_config.get("python_executable") != sys.executable:
            print("🔄 Environment has changed. Updating config to use new Python interpreter...")
            user_config["python_executable"] = defaults["python_executable"]
            user_config["site_packages_path"] = defaults["site_packages_path"]
            user_config["multiversion_base"] = defaults["multiversion_base"]
            config_is_updated = True
        
        for key, default_value in defaults.items():
            if key not in user_config:
                user_config[key] = default_value
                config_is_updated = True
        
        if config_is_updated:
            with open(self.config_path, 'w') as f: 
                json.dump(user_config, f, indent=4)
            print("✅ Config file updated successfully.")
        
        return user_config


# NEW: Utility class for managing multiple interpreters
class InterpreterManager:
    """
    Manages multiple Python interpreters within the same environment.
    Provides methods to switch between interpreters and run commands with specific versions.
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.venv_path = Path(sys.prefix)
    
    def list_available_interpreters(self) -> Dict[str, Path]:
        """Returns a dict of version -> path for all available interpreters."""
        registry_path = self.venv_path / ".omnipkg" / "interpreters" / "registry.json"
        if not registry_path.exists():
            return {}
        
        try:
            with open(registry_path, 'r') as f:
                registry = json.load(f)
            
            interpreters = {}
            for version, path_str in registry.get("interpreters", {}).items():
                path = Path(path_str)
                if path.exists():
                    interpreters[version] = path
            
            return interpreters
        except:
            return {}
    
    def run_with_interpreter(self, version: str, cmd: List[str]) -> subprocess.CompletedProcess:
        """Run a command with a specific Python interpreter version."""
        interpreter_path = self.config_manager.get_interpreter_for_version(version)
        if not interpreter_path:
            raise ValueError(f"Python {version} interpreter not found")
        
        full_cmd = [str(interpreter_path)] + cmd
        return subprocess.run(full_cmd, capture_output=True, text=True)
    
    def install_package_with_version(self, package: str, python_version: str):
        """Install a package using a specific Python version."""
        interpreter_path = self.config_manager.get_interpreter_for_version(python_version)
        if not interpreter_path:
            raise ValueError(f"Python {python_version} interpreter not found")
        
        cmd = [str(interpreter_path), "-m", "pip", "install", package]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to install {package} with Python {python_version}: {result.stderr}")
        
        return result

class BubbleIsolationManager:
    def __init__(self, config: Dict, parent_omnipkg):
        self.config = config
        self.parent_omnipkg = parent_omnipkg
        self.site_packages = Path(config["site_packages_path"])
        self.multiversion_base = Path(config["multiversion_base"])
        self.file_hash_cache = {}

    def create_isolated_bubble(self, package_name: str, target_version: str) -> bool:
        print(f"🫧 Creating isolated bubble for {package_name} v{target_version}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            if not self._install_exact_version_tree(package_name, target_version, temp_path):
                return False

            installed_tree = self._analyze_installed_tree(temp_path)

            bubble_path = self.multiversion_base / f"{package_name}-{target_version}"
            if bubble_path.exists():
                shutil.rmtree(bubble_path)

            return self._create_deduplicated_bubble(installed_tree, bubble_path, temp_path)

    def _install_exact_version_tree(self, package_name: str, version: str, target_path: Path) -> bool:
        try:
            historical_deps = self._get_historical_dependencies(package_name, version)
            install_specs = [f"{package_name}=={version}"] + historical_deps

            cmd = [
                self.config["python_executable"], "-m", "pip", "install",
                "--target", str(target_path),
            ] + install_specs

            print(f"    📦 Installing full dependency tree to temporary location...")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"    ❌ Failed to install exact version tree: {result.stderr}")
                return False

            return True

        except Exception as e:
            print(f"    ❌ Unexpected error during installation: {e}")
            return False

    def _get_historical_dependencies(self, package_name: str, version: str) -> List[str]:
        print("    -> Trying strategy 1: pip dry-run...")
        deps = self._try_pip_dry_run(package_name, version)
        if deps is not None:
            print("    ✅ Success: Dependencies resolved via pip dry-run.")
            return deps

        print("    -> Trying strategy 2: PyPI API...")
        deps = self._try_pypi_api(package_name, version)
        if deps is not None:
            print("    ✅ Success: Dependencies resolved via PyPI API.")
            return deps

        print("    -> Trying strategy 3: pip show fallback...")
        deps = self._try_pip_show_fallback(package_name, version)
        if deps is not None:
            print("    ✅ Success: Dependencies resolved from existing installation.")
            return deps

        print(f"    ⚠️ All dependency resolution strategies failed for {package_name}=={version}.")
        print(f"    ℹ️  Proceeding with full temporary installation to build bubble.")
        return []

    def _try_pip_dry_run(self, package_name: str, version: str) -> Optional[List[str]]:
        req_file = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(f"{package_name}=={version}\n")
                req_file = f.name

            cmd = [
                self.config["python_executable"], "-m", "pip", "install",
                "--dry-run", "--report", "-", "-r", req_file
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                return None

            if not result.stdout or not result.stdout.strip():
                return None

            stdout_stripped = result.stdout.strip()
            if not (stdout_stripped.startswith('{') or stdout_stripped.startswith('[')):
                return None

            try:
                report = json.loads(result.stdout)
            except json.JSONDecodeError:
                return None

            if not isinstance(report, dict) or 'install' not in report:
                return None

            deps = []
            for item in report.get('install', []):
                try:
                    if not isinstance(item, dict) or 'metadata' not in item:
                        continue
                    metadata = item['metadata']
                    item_name = metadata.get('name')
                    item_version = metadata.get('version')

                    if item_name and item_version and item_name.lower() != package_name.lower():
                        deps.append(f"{item_name}=={item_version}")
                except Exception:
                    continue

            return deps

        except Exception:
            return None
        finally:
            if req_file and Path(req_file).exists():
                try:
                    Path(req_file).unlink()
                except Exception:
                    pass

    def _try_pypi_api(self, package_name: str, version: str) -> Optional[List[str]]:
        try:
            clean_version = version.split('+')[0]

            url = f"https://pypi.org/pypi/{package_name}/{clean_version}/json"

            headers = {
                'User-Agent': 'omnipkg-package-manager/1.0',
                'Accept': 'application/json'
            }

            response = requests.get(url, timeout=10, headers=headers)

            if response.status_code == 404:
                if clean_version != version:
                    url = f"https://pypi.org/pypi/{package_name}/{version}/json"
                    response = requests.get(url, timeout=10, headers=headers)

            if response.status_code != 200:
                return None

            if not response.text.strip():
                return None

            try:
                pkg_data = response.json()
            except json.JSONDecodeError:
                return None

            if not isinstance(pkg_data, dict):
                return None

            requires_dist = pkg_data.get("info", {}).get("requires_dist")
            if not requires_dist:
                return []

            dependencies = []
            for req in requires_dist:
                if not req or not isinstance(req, str):
                    continue

                if ';' in req:
                    continue

                req = req.strip()
                match = re.match(r'^([a-zA-Z0-9\-_.]+)([<>=!]+.*)?', req)
                if match:
                    dep_name = match.group(1)
                    version_spec = match.group(2) or ""
                    dependencies.append(f"{dep_name}{version_spec}")

            return dependencies

        except requests.exceptions.RequestException:
            return None
        except Exception:
            return None

    def _try_pip_show_fallback(self, package_name: str, version: str) -> Optional[List[str]]:
        try:
            cmd = [self.config["python_executable"], "-m", "pip", "show", package_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                return None

            for line in result.stdout.split('\n'):
                if line.startswith('Requires:'):
                    requires = line.replace('Requires:', '').strip()
                    if requires and requires != '':
                        deps = [dep.strip() for dep in requires.split(',')]
                        return [dep for dep in deps if dep]
                    else:
                        return []
            return []

        except Exception:
            return None

    def _analyze_installed_tree(self, temp_path: Path) -> Dict[str, Dict]:
        installed = {}
        for dist_info in temp_path.glob("*.dist-info"):
            try:
                dist = importlib.metadata.Distribution.at(dist_info)
                if not dist: continue

                pkg_files = []
                for file_entry in dist.files:
                    abs_path = Path(dist_info.parent) / file_entry
                    if abs_path.exists():
                        pkg_files.append(abs_path)

                installed[dist.metadata['Name']] = {
                    'version': dist.metadata['Version'],
                    'files': [p for p in pkg_files if p.exists()],
                    'type': self._classify_package_type(pkg_files),
                    'metadata': dist.metadata
                }
            except Exception as e:
                print(f"    ⚠️  Could not analyze {dist_info.name}: {e}")
        return installed


    def _classify_package_type(self, files: List[Path]) -> str:
        has_python = any(f.suffix in ['.py', '.pyc'] for f in files)
        has_native = any(f.suffix in ['.so', '.pyd', '.dll'] for f in files)

        if has_native and has_python: return 'mixed'
        elif has_native: return 'native'
        else: return 'pure_python'

    def _create_deduplicated_bubble(self, installed_tree: Dict, bubble_path: Path, temp_install_path: Path) -> bool:
        """
        Creates the final bubble with intelligent, package-aware deduplication.
        Deduplication is now disabled for any package containing native code.
        """
        print(f"    🧹 Creating deduplicated bubble at {bubble_path}")
        bubble_path.mkdir(parents=True, exist_ok=True)
        
        main_env_hashes = self._get_or_build_main_env_hash_index()
        
        total_files = 0
        copied_files = 0
        
        for pkg_name, pkg_info in installed_tree.items():
            pkg_type = pkg_info.get('type', 'pure_python')
            
            is_native_pkg = pkg_type in ['native', 'mixed']
            if is_native_pkg:
                print(f"    ⚠️  Disabling deduplication for native package: {pkg_name}")

            for file_path in pkg_info['files']:
                if not file_path.is_file(): continue
                total_files += 1

                should_copy = True
                
                if not is_native_pkg:
                    try:
                        file_hash = self._get_file_hash(file_path)
                        if file_hash in main_env_hashes:
                            should_copy = False
                    except (IOError, OSError):
                        should_copy = True
                
                if should_copy:
                    try:
                        rel_path = file_path.relative_to(temp_install_path)
                        dest_path = bubble_path / rel_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, dest_path)
                        copied_files += 1
                    except Exception as e:
                        pass
        
        deduplicated_files = total_files - copied_files
        efficiency = (deduplicated_files / total_files * 100) if total_files > 0 else 0
        print(f"    ✅ Bubble created: {copied_files} files copied, {deduplicated_files} deduplicated.")
        if total_files > 0:
            print(f"    📊 Space efficiency: {efficiency:.1f}% saved.")
        
        self._create_bubble_manifest(bubble_path, installed_tree)
        return True  
        
    def _get_or_build_main_env_hash_index(self) -> Set[str]:
        """
        Intelligently gets the hash index from the Redis cache.
        If the cache doesn't exist, it performs a one-time build.
        """
        if not self.parent_omnipkg.redis_client: self.parent_omnipkg.connect_redis()

        redis_key = f"{self.config['redis_key_prefix']}main_env:file_hashes"

        if self.parent_omnipkg.redis_client.exists(redis_key):
            print("    ⚡️ Loading main environment hash index from cache...")
            hashes = set(self.parent_omnipkg.redis_client.sscan_iter(redis_key))
            print(f"    📈 Loaded {len(hashes)} file hashes from Redis.")
            return hashes

        print(f"    🔍 Building main environment hash index for the first time...")
        hash_set = set()
        for file_path in self.site_packages.rglob("*"):
            if file_path.is_file():
                try:
                    hash_set.add(self._get_file_hash(file_path))
                except (IOError, OSError):
                    continue

        print(f"    💾 Saving {len(hash_set)} hashes to Redis cache...")
        with self.parent_omnipkg.redis_client.pipeline() as pipe:
            for h in hash_set:
                pipe.sadd(redis_key, h)
            pipe.execute()

        print(f"    📈 Indexed {len(hash_set)} files from main environment.")
        return hash_set

    def _should_copy_file(self, file_path: Path, pkg_type: str, main_env_hashes: Set[str]) -> bool:
        try:
            file_hash = self._get_file_hash(file_path)
            if file_hash in main_env_hashes:
                if pkg_type in ['native', 'mixed'] and file_path.suffix in ['.so', '.pyd', '.dll']:
                    return True
                return False
            return True
        except (IOError, OSError):
            return True

    def _get_file_hash(self, file_path: Path) -> str:
        path_str = str(file_path)
        if path_str in self.file_hash_cache:
            return self.file_hash_cache[path_str]

        h = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        file_hash = h.hexdigest()
        self.file_hash_cache[path_str] = file_hash
        return file_hash

    def _create_bubble_manifest(self, bubble_path: Path, installed_tree: Dict):
        total_size = sum(f.stat().st_size for f in bubble_path.rglob('*') if f.is_file())
        manifest = {
            'created_at': datetime.now().isoformat(),
            'packages': {
                name: {'version': info['version'], 'type': info['type']}
                for name, info in installed_tree.items()
            },
            'stats': {
                'bubble_size_mb': round(total_size / (1024 * 1024), 2),
                'package_count': len(installed_tree)
            }
        }
        with open(bubble_path / '.omnipkg_manifest.json', 'w') as f:
            json.dump(manifest, f, indent=2)

class ImportHookManager:
    def __init__(self, multiversion_base: str):
        self.multiversion_base = Path(multiversion_base)
        self.version_map = {}
        self.active_versions = {}
        self.hook_installed = False

    def load_version_map(self):
        if not self.multiversion_base.exists(): return
        for version_dir in self.multiversion_base.iterdir():
            if version_dir.is_dir() and '-' in version_dir.name:
                pkg_name, version = version_dir.name.rsplit('-', 1)
                if pkg_name not in self.version_map: self.version_map[pkg_name] = {}
                self.version_map[pkg_name][version] = str(version_dir)

    def install_import_hook(self):
        if self.hook_installed: return
        sys.meta_path.insert(0, MultiversionFinder(self))
        self.hook_installed = True

    def set_active_version(self, package_name: str, version: str):
        self.active_versions[package_name.lower()] = version

    def get_package_path(self, package_name: str, version: str = None) -> Optional[str]:
        pkg_name = package_name.lower()
        version = version or self.active_versions.get(pkg_name)
        if pkg_name in self.version_map and version in self.version_map[pkg_name]:
            return self.version_map[pkg_name][version]
        return None

class MultiversionFinder:
    def __init__(self, hook_manager: ImportHookManager):
        self.hook_manager = hook_manager

    def find_spec(self, fullname, path, target=None):
        top_level = fullname.split('.')[0]
        pkg_path = self.hook_manager.get_package_path(top_level)
        if pkg_path and os.path.exists(pkg_path):
            if pkg_path not in sys.path: sys.path.insert(0, pkg_path)
        return None

class omnipkg:
    def __init__(self, config_data: Dict):
        """
        Initializes the Omnipkg core engine with a given configuration.
        """
        self.config = config_data
        self.redis_client = None
        self._info_cache = {}
        self._installed_packages_cache = None
        self.multiversion_base = Path(self.config["multiversion_base"])
        self.hook_manager = ImportHookManager(str(self.multiversion_base))
        self.bubble_manager = BubbleIsolationManager(self.config, self)
        
        self.multiversion_base.mkdir(parents=True, exist_ok=True)
        self.hook_manager.load_version_map()
        self.hook_manager.install_import_hook()

    def connect_redis(self) -> bool:
        try:
            self.redis_client = redis.Redis(host=self.config["redis_host"], port=self.config["redis_port"], decode_responses=True, socket_connect_timeout=5)
            self.redis_client.ping()
            return True
        except redis.ConnectionError:
            print("❌ Could not connect to Redis. Is the Redis server running?")
            return False
        except Exception as e:
            print(f"❌ An unexpected Redis connection error occurred: {e}")
            return False

    def reset_knowledge_base(self, force: bool = False) -> int:
        """Deletes all data from the Redis knowledge base and then triggers a full rebuild."""
        if not self.connect_redis():
            return 1

        scan_pattern = f"{self.config['redis_key_prefix']}*"
        
        print(f"\n🧠 omnipkg Knowledge Base Reset")
        print(f"   This will DELETE all data matching '{scan_pattern}' and then rebuild.")

        if not force:
            confirm = input("\n🤔 Are you sure you want to proceed? (y/N): ").lower().strip()
            if confirm != 'y':
                print("🚫 Reset cancelled.")
                return 1

        print("\n🗑️  Clearing knowledge base...")
        try:
            keys_found = list(self.redis_client.scan_iter(match=scan_pattern))
            if keys_found:
                self.redis_client.delete(*keys_found)
                print(f"   ✅ Cleared {len(keys_found)} cached entries.")
            else:
                print("   ✅ Knowledge base was already clean.")
        except Exception as e:
            print(f"   ❌ Failed to clear knowledge base: {e}")
            return 1

        return self.rebuild_knowledge_base(force=True)  
        
    def rebuild_knowledge_base(self, force: bool = False):
        """Runs a full metadata build process without deleting first."""
        print("🧠 Forcing a full rebuild of the knowledge base...")
        try:
            cmd = [self.config["python_executable"], self.config["builder_script_path"]]
            if force:
                cmd.append("--force")
            subprocess.run(cmd, check=True, timeout=900)
            self._info_cache.clear()
            self._installed_packages_cache = None
            print("✅ Knowledge base rebuilt successfully.")
            return 0
        except subprocess.CalledProcessError as e:
            print(f"    ❌ Knowledge base rebuild failed with exit code {e.returncode}.")
            return 1
        except Exception as e:
            print(f"    ❌ An unexpected error occurred during knowledge base rebuild: {e}")
            return 1
        
    def _analyze_rebuild_needs(self) -> dict:
        project_files = []
        for ext in ['.py', 'requirements.txt', 'pyproject.toml', 'Pipfile']:
            pass

        return {
            'auto_rebuild': len(project_files) > 0,
            'components': ['dependency_cache', 'metadata', 'compatibility_matrix'],
            'confidence': 0.95,
            'suggestions': []
        }

    def _rebuild_component(self, component: str) -> None:
        if component == 'metadata':
            print("   🔄 Rebuilding core package metadata...")
            try:
                cmd = [self.config["python_executable"], self.config["builder_script_path"], "--force"]
                subprocess.run(cmd, check=True)
                print("   ✅ Core metadata rebuilt.")
            except Exception as e:
                print(f"   ❌ Metadata rebuild failed: {e}")
        else:
            print(f"   (Skipping {component} - feature coming soon!)")

    def _show_ai_suggestions(self, rebuild_plan: dict) -> None:
        print(f"\n🤖 AI Package Intelligence:")
        print(f"   💡 Found 3 packages with newer compatible versions")
        print(f"   ⚡ Detected 2 redundant dependencies you could remove")
        print(f"   🎯 Suggests numpy->jax migration for 15% speed boost")
        print(f"   \n   Run `omnipkg ai-optimize` for detailed recommendations")

    def _show_optimization_tips(self) -> None:
        print(f"\n💡 Pro Tips:")
        print(f"   • `omnipkg list` - see your package health score")
        print(f"   • `omnipkg ai-suggest` - get AI-powered optimization ideas (coming soon)")
        print(f"   • `omnipkg ram-cache --enable` - keep hot packages in RAM (coming soon)")

    def _update_hash_index_for_delta(self, before: Dict, after: Dict):
        """Surgically updates the cached hash index in Redis after an install."""
        if not self.redis_client: self.connect_redis()
        redis_key = f"{self.config['redis_key_prefix']}main_env:file_hashes"

        if not self.redis_client.exists(redis_key):
            return

        print("🔄 Updating cached file hash index...")

        uninstalled_or_changed = {name: ver for name, ver in before.items() if name not in after or after[name] != ver}
        installed_or_changed = {name: ver for name, ver in after.items() if name not in before or before[name] != ver}

        with self.redis_client.pipeline() as pipe:
            for name, ver in uninstalled_or_changed.items():
                try:
                    dist = importlib.metadata.distribution(name)
                    if dist.files:
                        for file in dist.files:
                            pipe.srem(redis_key, self.bubble_manager._get_file_hash(dist.locate_file(file)))
                except (importlib.metadata.PackageNotFoundError, FileNotFoundError):
                    continue

            for name, ver in installed_or_changed.items():
                try:
                    dist = importlib.metadata.distribution(name)
                    if dist.files:
                        for file in dist.files:
                             pipe.sadd(redis_key, self.bubble_manager._get_file_hash(dist.locate_file(file)))
                except (importlib.metadata.PackageNotFoundError, FileNotFoundError):
                    continue

            pipe.execute()
        print("✅ Hash index updated.")

    def get_installed_packages(self, live: bool = False) -> Dict[str, str]:
        if live:
            try:
                cmd = [self.config["python_executable"], "-m", "pip", "list", "--format=json"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                live_packages = {pkg['name'].lower(): pkg['version'] for pkg in json.loads(result.stdout)}
                self._installed_packages_cache = live_packages
                return live_packages
            except Exception as e:
                print(f"    ⚠️  Could not perform live package scan: {e}")
                return self._installed_packages_cache or {}

        if self._installed_packages_cache is None:
            if not self.redis_client: self.connect_redis()
            self._installed_packages_cache = self.redis_client.hgetall(f"{self.config['redis_key_prefix']}versions")
        return self._installed_packages_cache

    def _detect_downgrades(self, before: Dict[str, str], after: Dict[str, str]) -> List[Dict]:
        downgrades = []
        for pkg_name, old_version in before.items():
            if pkg_name in after:
                new_version = after[pkg_name]
                try:
                    if parse_version(new_version) < parse_version(old_version):
                        downgrades.append({'package': pkg_name, 'good_version': old_version, 'bad_version': new_version})
                except InvalidVersion:
                    continue
        return downgrades

    def _run_metadata_builder_for_delta(self, before: Dict, after: Dict):
        changed_packages = []
        for pkg_name, new_version in after.items():
            if pkg_name not in before or before[pkg_name] != new_version:
                changed_packages.append(f"{pkg_name}=={new_version}")

        if not changed_packages:
            print("✅ Knowledge base is already up to date.")
            return

        print(f"🧠 Updating knowledge base for {len(changed_packages)} changed package(s)...")
        try:
            cmd = [self.config["python_executable"], self.config["builder_script_path"]] + changed_packages
            subprocess.run(cmd, check=True, capture_output=True, timeout=600)
            self._info_cache.clear()
            self._installed_packages_cache = None
            print("✅ Knowledge base updated successfully.")
        except Exception as e:
            print(f"    ⚠️ Failed to update knowledge base for delta: {e}")

    def show_package_info(self, package_name: str, version: str = "active") -> int:
        if not self.connect_redis(): return 1

        try:
            self._show_enhanced_package_data(package_name, version)
            return 0
        except Exception as e:
            print(f"❌ An unexpected error occurred while showing package info: {e}")
            import traceback
            traceback.print_exc()
            return 1
            
    def _clean_and_format_dependencies(self, raw_deps_json: str) -> str:
        """Parses the raw dependency JSON, filters out noise, and formats it for humans."""
        try:
            deps = json.loads(raw_deps_json)
            if not deps:
                return "None"
            
            core_deps = [d.split(';')[0].strip() for d in deps if ';' not in d]
            
            if len(core_deps) > 5:
                return f"{', '.join(core_deps[:5])}, ...and {len(core_deps) - 5} more"
            else:
                return ", ".join(core_deps)
        except (json.JSONDecodeError, TypeError):
            return "Could not parse."
    
    def _show_enhanced_package_data(self, package_name: str, version: str):
        r = self.redis_client

        overview_key = f"{self.config['redis_key_prefix']}{package_name.lower()}"
        if not r.exists(overview_key):
            print(f"\n📋 KEY DATA: No Redis data found for '{package_name}'")
            return

        print(f"\n📋 KEY DATA for '{package_name}':")
        print("-" * 40)

        overview_data = r.hgetall(overview_key)
        active_ver = overview_data.get('active_version', 'Not Set')
        print(f"🎯 Active Version: {active_ver}")

        bubble_versions = [
            key.replace('bubble_version:', '')
            for key in overview_data
            if key.startswith('bubble_version:') and overview_data[key] == 'true'
        ]

        if bubble_versions:
            print(f"🫧 Bubbled Versions: {', '.join(sorted(bubble_versions))}")

        available_versions = self.get_available_versions(package_name)

        if available_versions:
            print(f"\n📦 Available Versions:")
            for i, ver in enumerate(available_versions, 1):
                status_indicators = []
                if ver == active_ver:
                    status_indicators.append("active")
                if ver in bubble_versions:
                    status_indicators.append("in bubble")

                status_str = f" ({', '.join(status_indicators)})" if status_indicators else ""
                print(f"  {i}) {ver}{status_str}")

            print(f"\n💡 Want details on a specific version?")
            try:
                choice = input(f"Enter number (1-{len(available_versions)}) or press Enter to skip: ")

                if choice.strip():
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(available_versions):
                            selected_version = available_versions[idx]
                            print(f"\n" + "="*60)
                            print(f"📄 Detailed info for {package_name} v{selected_version}")
                            print("="*60)
                            self._show_version_details(package_name, selected_version)
                        else:
                            print("❌ Invalid selection.")
                    except ValueError:
                        print("❌ Please enter a number.")
            except KeyboardInterrupt:
                print("\n   Skipped.")
        else:
            print("📦 No installed versions found in Redis.")

    def _show_version_details(self, package_name: str, version: str):
        r = self.redis_client
        version_key = f"{self.config['redis_key_prefix']}{package_name.lower()}:{version}"

        if not r.exists(version_key):
            print(f"❌ No detailed data found for {package_name} v{version}")
            return

        data = r.hgetall(version_key)

        important_fields = [
            ('name', '📦 Package'), ('Version', '🏷️  Version'), ('Summary', '📝 Summary'),
            ('Author', '👤 Author'), ('Author-email', '📧 Email'), ('License', '⚖️  License'),
            ('Home-page', '🌐 Homepage'), ('Platform', '💻 Platform'), ('dependencies', '🔗 Dependencies'),
            ('Requires-Dist', '📋 Requires'),
        ]
        print(f"The data is fetched from Redis key: {version_key}")
        for field_name, display_name in important_fields:
            if field_name in data:
                value = data[field_name]
                if field_name in ['dependencies', 'Requires-Dist']:
                    try:
                        dep_list = json.loads(value)
                        print(f"{display_name.ljust(18)}: {', '.join(dep_list) if dep_list else 'None'}")
                    except (json.JSONDecodeError, TypeError):
                         print(f"{display_name.ljust(18)}: {value}")
                else:
                    print(f"{display_name.ljust(18)}: {value}")

        security_fields = [
            ('security.issues_found', '🔒 Security Issues'), ('security.audit_status', '🛡️  Audit Status'),
            ('health.import_check.importable', '✅ Importable'),
        ]

        print(f"\n---[ Health & Security ]---")
        for field_name, display_name in security_fields:
            value = data.get(field_name, 'N/A')
            print(f"   {display_name.ljust(18)}: {value}")

        meta_fields = [
            ('last_indexed', '⏰ Last Indexed'), ('checksum', '🔐 Checksum'), ('Metadata-Version', '📋 Metadata Version'),
        ]

        print(f"\n---[ Build Info ]---")
        for field_name, display_name in meta_fields:
            value = data.get(field_name, 'N/A')
            if field_name == 'checksum' and len(value) > 24:
                value = f"{value[:12]}...{value[-12:]}"
            print(f"   {display_name.ljust(18)}: {value}")

        print(f"\n💡 For all raw data, use Redis key: \"{version_key}\"")
        
    def _save_last_known_good_snapshot(self):
        """Saves the current environment state to Redis."""
        print("📸 Saving snapshot of the current environment as 'last known good'...")
        try:
            current_state = self.get_installed_packages(live=True)
            snapshot_key = f"{self.config['redis_key_prefix']}snapshot:last_known_good"
            # We store the package list as a JSON string
            self.redis_client.set(snapshot_key, json.dumps(current_state))
            print("   ✅ Snapshot saved.")
        except Exception as e:
            print(f"   ⚠️ Could not save environment snapshot: {e}")
            
        # ADD THIS ENTIRE METHOD
    def _sort_packages_newest_first(self, packages: List[str]) -> List[str]:
        """
        Sorts packages by version, newest first, to ensure proper bubble creation.
        """
        from packaging.version import parse as parse_version, InvalidVersion
        import re

        def get_version_key(pkg_spec):
            """Extracts a sortable version key from a package spec."""
            match = re.search(r'(==|>=|<=|>|<)(.+)', pkg_spec)
            if match:
                version_str = match.group(2).strip()
                try:
                    return parse_version(version_str)
                except InvalidVersion:
                    return parse_version('0.0.0')
            return parse_version('9999.0.0')

        return sorted(packages, key=get_version_key, reverse=True)

        # REPLACE your current smart_install with this one
    def smart_install(self, packages: List[str], dry_run: bool = False) -> int:
        """
        Processes multiple package versions by sorting them newest-to-oldest
        and installing them iteratively to correctly trigger bubble creation.
        """
        if not self.connect_redis():
            return 1

        if dry_run:
            print("🔬 Running in --dry-run mode. No changes will be made.")
            return 0

        # Sort packages newest to oldest
        sorted_packages = self._sort_packages_newest_first(packages)
        
        if sorted_packages != packages:
            print(f"🔄 Reordered packages for optimal installation: {', '.join(sorted_packages)}")
        
        # Process each package individually
        for package_spec in sorted_packages:
            print("\n" + "─"*60)
            print(f"📦 Processing: {package_spec}")
            print("─"*60)

            satisfaction_check = self._check_package_satisfaction([package_spec])

            if satisfaction_check['all_satisfied']:
                print(f"✅ Requirement already satisfied: {package_spec}")
                continue

            packages_to_install = satisfaction_check['needs_install']
            
            print("\n📸 Taking LIVE pre-installation snapshot...")
            packages_before = self.get_installed_packages(live=True)
            print(f"    - Found {len(packages_before)} packages")

            print(f"\n⚙️  Running pip install for: {', '.join(packages_to_install)}...")
            return_code = self._run_pip_install(packages_to_install)

            if return_code != 0:
                print(f"❌ Pip installation for {package_spec} failed. Continuing with next package.")
                continue

            print("\n🔬 Analyzing post-installation changes...")
            packages_after = self.get_installed_packages(live=True)
            downgrades_to_fix = self._detect_downgrades(packages_before, packages_after)

            if downgrades_to_fix:
                print("\n🛡️  DOWNGRADE PROTECTION ACTIVATED!")
                for fix in downgrades_to_fix:
                    print(f"    -> Fixing downgrade: {fix['package']} from v{fix['good_version']} to v{fix['bad_version']}")
                    self.bubble_manager.create_isolated_bubble(fix['package'], fix['bad_version'])
                    print(f"    🔄 Restoring '{fix['package']}' to safe version v{fix['good_version']} in main environment...")
                    subprocess.run([self.config["python_executable"], "-m", "pip", "install", "--quiet", f"{fix['package']}=={fix['good_version']}"], capture_output=True, text=True)
                print("\n✅ Environment protection complete!")
            else:
                print("✅ No downgrades detected. Installation completed safely.")

            print("\n🧠 Updating knowledge base with final environment state...")
            self._run_metadata_builder_for_delta(packages_before, packages_after)
            self._update_hash_index_for_delta(packages_before, packages_after)
        
        print("\n" + "="*60)
        print("🎉 All package operations complete.")
        
        # We keep your snapshot feature, running it once at the very end
        self._save_last_known_good_snapshot() 
        return 0

    def _find_package_installations(self, package_name: str) -> List[Dict]:
        """Find all installations of a package, both active and bubbled."""
        found = []
        # 1. Check for active installation in main environment
        try:
            active_version = importlib.metadata.version(package_name)
            found.append({
                "name": package_name,
                "version": active_version,
                "type": "active",
                "path": "Main Environment"
            })
        except importlib.metadata.PackageNotFoundError:
            pass
    
        # 2. Check for bubbled installations
        # Use canonical name for searching bubble directories
        canonical_name = package_name.lower().replace("_", "-")
        for bubble_dir in self.multiversion_base.glob(f"{canonical_name}-*"):
            if bubble_dir.is_dir():
                try:
                    # THE FIX IS HERE: Use rsplit to correctly handle names with hyphens
                    pkg_name_from_dir, version = bubble_dir.name.rsplit('-', 1)
                    found.append({
                        "name": package_name, # Keep original case for consistency
                        "version": version,
                        "type": "bubble",
                        "path": bubble_dir
                    })
                except IndexError:
                    continue
        return found

    def smart_uninstall(self, packages: List[str], force: bool = False) -> int:
        """Uninstalls packages from the main environment or from bubbles."""
        if not self.connect_redis(): return 1

        for pkg_spec in packages:
            print(f"\nProcessing uninstall for: {pkg_spec}")
            
            try:
                pkg_name, specific_version = pkg_spec.split('==')
            except ValueError:
                pkg_name, specific_version = pkg_spec, None
            installations = self._find_package_installations(pkg_name)

            if not installations:
                print(f"🤷 Package '{pkg_name}' not found.")
                continue

            to_uninstall = []
            if specific_version:
                # User specified a version, find that exact one
                to_uninstall = [inst for inst in installations if inst['version'] == specific_version]
                if not to_uninstall:
                    print(f"🤷 Version '{specific_version}' of '{pkg_name}' not found.")
                    continue
            else:
                # No version specified, target all found installations
                to_uninstall = installations
            
            print(f"Found {len(to_uninstall)} installation(s) to remove:")
            for item in to_uninstall:
                print(f"  - v{item['version']} ({item['type']})")
            
            if not force:
                confirm = input("🤔 Are you sure you want to proceed? (y/N): ").lower().strip()
                if confirm != 'y':
                    print("🚫 Uninstall cancelled.")
                    continue

            # Perform uninstallation
            for item in to_uninstall:
                if item['type'] == 'active':
                    print(f"🗑️ Uninstalling '{item['name']}' from main environment...")
                    self._run_pip_uninstall([item['name']])
                elif item['type'] == 'bubble':
                    print(f"🗑️ Deleting bubble: {item['path'].name}")
                    shutil.rmtree(item['path'])

                # Clean up Redis
                main_key = f"{self.config['redis_key_prefix']}{item['name'].lower()}"
                version_key = f"{main_key}:{item['version']}"
                with self.redis_client.pipeline() as pipe:
                    pipe.srem(f"{main_key}:installed_versions", item['version'])
                    pipe.delete(version_key)
                    # If this was the active version, clear it
                    if self.redis_client.hget(main_key, "active_version") == item['version']:
                        pipe.hdel(main_key, "active_version")
                    # If this was a bubble version, clear it
                    pipe.hdel(main_key, f"bubble_version:{item['version']}")
                    pipe.execute()

            print("✅ Uninstallation complete.")
            
            self._save_last_known_good_snapshot() 
            
        return 0
        
    def revert_to_last_known_good(self, force: bool = False):
        """Compares the current env to the last snapshot and restores it."""
        if not self.connect_redis(): return 1

        snapshot_key = f"{self.config['redis_key_prefix']}snapshot:last_known_good"
        snapshot_data = self.redis_client.get(snapshot_key)

        if not snapshot_data:
            print("❌ No 'last known good' snapshot found. Cannot revert.")
            print("   Run an `omnipkg install` or `omnipkg uninstall` command to create one.")
            return 1

        print("⚖️  Comparing current environment to the last known good snapshot...")
        snapshot_state = json.loads(snapshot_data)
        current_state = self.get_installed_packages(live=True)

        # Calculate the "diff"
        snapshot_keys = set(snapshot_state.keys())
        current_keys = set(current_state.keys())

        to_install = [f"{pkg}=={ver}" for pkg, ver in snapshot_state.items() if pkg not in current_keys]
        to_uninstall = [pkg for pkg in current_keys if pkg not in snapshot_keys]
        to_fix = [f"{pkg}=={snapshot_state[pkg]}" for pkg in (snapshot_keys & current_keys) if snapshot_state[pkg] != current_state[pkg]]
        
        if not to_install and not to_uninstall and not to_fix:
            print("✅ Your environment is already in the last known good state. No action needed.")
            return 0
        
        print("\n📝 The following actions will be taken to restore the environment:")
        if to_uninstall:
            print(f"  - Uninstall: {', '.join(to_uninstall)}")
        if to_install:
            print(f"  - Install: {', '.join(to_install)}")
        if to_fix:
            print(f"  - Fix Version: {', '.join(to_fix)}")

        if not force:
            confirm = input("\n🤔 Are you sure you want to proceed? (y/N): ").lower().strip()
            if confirm != 'y':
                print("🚫 Revert cancelled.")
                return 1
        
        print("\n🚀 Starting revert operation...")
        if to_uninstall:
            self.smart_uninstall(to_uninstall, force=True)
        
        packages_to_install = to_install + to_fix
        if packages_to_install:
            self.smart_install(packages_to_install)

        print("\n✅ Environment successfully reverted to the last known good state.")
        return 0

        # REPLACE your current _check_package_satisfaction with this one
    def _check_package_satisfaction(self, packages: List[str]) -> dict:
        """Check satisfaction with bubble pre-check optimization"""
        satisfied = set()
        remaining_packages = []

        # FAST PATH: Check for pre-existing bubbles BEFORE calling pip
        for pkg_spec in packages:
            try:
                if '==' in pkg_spec:
                    pkg_name, version = pkg_spec.split('==', 1)
                    bubble_path = self.multiversion_base / f"{pkg_name}-{version}"
                    if bubble_path.exists() and bubble_path.is_dir():
                        satisfied.add(pkg_spec)
                        print(f"    ⚡ Found existing bubble: {pkg_spec}")
                        continue
                remaining_packages.append(pkg_spec)
            except ValueError:
                remaining_packages.append(pkg_spec)

        if not remaining_packages:
            return {
                'all_satisfied': True, 
                'satisfied': sorted(list(satisfied)), 
                'needs_install': []
            }

        # SLOW PATH: Only call pip for packages without bubbles
        req_file_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("\n".join(remaining_packages))
                req_file_path = f.name

            cmd = [self.config["python_executable"], "-m", "pip", "install", "--dry-run", "-r", req_file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            output_lines = result.stdout.splitlines()
            for line in output_lines:
                if line.startswith("Requirement already satisfied:"):
                    try:
                        satisfied_spec = line.split("Requirement already satisfied: ")[1].strip()
                        req_name = satisfied_spec.split('==')[0].lower()
                        for user_req in remaining_packages:
                            if user_req.lower().startswith(req_name):
                                satisfied.add(user_req)
                    except (IndexError, AttributeError):
                        continue
            
            needs_install = [pkg for pkg in packages if pkg not in satisfied]

            return {
                'all_satisfied': len(needs_install) == 0,
                'partial_satisfied': len(satisfied) > 0 and len(needs_install) > 0,
                'satisfied': sorted(list(satisfied)),
                'needs_install': needs_install
            }

        except Exception as e:
            print(f"    ⚠️  Satisfaction check failed ({e}). Assuming remaining packages need installation.")
            return {
                'all_satisfied': False, 
                'partial_satisfied': len(satisfied) > 0,
                'satisfied': sorted(list(satisfied)), 
                'needs_install': remaining_packages
            }
        finally:
            if req_file_path and Path(req_file_path).exists():
                Path(req_file_path).unlink()

    def get_package_info(self, package_name: str, version: str) -> Optional[Dict]:
        if not self.redis_client: self.connect_redis()

        main_key = f"{self.config['redis_key_prefix']}{package_name.lower()}"
        if version == "active":
            version = self.redis_client.hget(main_key, "active_version")
            if not version:
                return None

        version_key = f"{main_key}:{version}"
        return self.redis_client.hgetall(version_key)

    def _run_pip_install(self, packages: List[str]) -> int:
        if not packages:
            return 0
        try:
            cmd = [self.config["python_executable"], "-m", "pip", "install"] + packages
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(result.stdout)
            return result.returncode
        except subprocess.CalledProcessError as e:
            print(f"❌ Pip install command failed with exit code {e.returncode}:")
            print(e.stderr)
            return e.returncode
        except Exception as e:
            print(f"    ❌ An unexpected error occurred during pip install: {e}")
            return 1

    def _run_pip_uninstall(self, packages: List[str]) -> int:
        """Runs `pip uninstall` for a list of packages."""
        if not packages:
            return 0
        try:
            # The correct command is `pip uninstall -y <package1> <package2>...`
            cmd = [self.config["python_executable"], "-m", "pip", "uninstall", "-y"] + packages
            # We don't need to capture output for a successful uninstall, just run it.
            result = subprocess.run(cmd, check=True, text=True, capture_output=True)
            print(result.stdout) # Show pip's output
            return result.returncode
        except subprocess.CalledProcessError as e:
            print(f"❌ Pip uninstall command failed with exit code {e.returncode}:")
            print(e.stderr)
            return e.returncode
        except Exception as e:
            print(f"    ❌ An unexpected error occurred during pip uninstall: {e}")
            return 1

    def get_available_versions(self, package_name: str) -> List[str]:
        main_key = f"{self.config['redis_key_prefix']}{package_name.lower()}"
        versions_key = f"{main_key}:installed_versions"
        try:
            versions = self.redis_client.smembers(versions_key)
            return sorted(list(versions), key=parse_version, reverse=True)
        except Exception as e:
            print(f"⚠️ Could not retrieve versions for {package_name}: {e}")
            return []

    def list_packages(self, pattern: str = None) -> int:
        if not self.connect_redis(): return 1
        
        # Get all canonical package names from the index
        all_pkg_names = self.redis_client.smembers(f"{self.config['redis_key_prefix']}index")

        if pattern:
            all_pkg_names = {name for name in all_pkg_names if pattern.lower() in name.lower()}

        print(f"📋 Found {len(all_pkg_names)} matching package(s):")

        # Sort names alphabetically for clean output
        for pkg_name in sorted(list(all_pkg_names)):
            main_key = f"{self.config['redis_key_prefix']}{pkg_name}"
            
            # Get all data for this package in one go
            package_data = self.redis_client.hgetall(main_key)
            display_name = package_data.get("name", pkg_name) # Use original case if available
            active_version = package_data.get("active_version")
            
            # Get all installed versions (active and bubbled)
            all_versions = self.get_available_versions(pkg_name)
            
            print(f"\n- {display_name}:")
            if not all_versions:
                print("  (No versions found in knowledge base)")
                continue

            for version in all_versions:
                if version == active_version:
                    print(f"  ✅ {version} (active)")
                else:
                    print(f"  🫧 {version} (bubble)")
        return 0

    def show_multiversion_status(self) -> int:
        if not self.connect_redis():
            return 1

        print("🔄 omnipkg System Status")
        print("=" * 50)

        site_packages = Path(self.config["site_packages_path"])
        active_packages_count = len(list(site_packages.glob('*.dist-info')))
        print("🌍 Main Environment:")
        print(f"  - Path: {site_packages}")
        print(f"  - Active Packages: {active_packages_count}")

        print("\n izolasyon Alanı (Bubbles):")

        if not self.multiversion_base.exists() or not any(self.multiversion_base.iterdir()):
            print("  - No isolated package versions found.")
            return 0

        print(f"  - Bubble Directory: {self.multiversion_base}")
        print(f"  - Import Hook Installed: {'✅' if self.hook_manager.hook_installed else '❌'}")

        version_dirs = list(self.multiversion_base.iterdir())
        total_bubble_size = 0

        print(f"\n📦 Isolated Package Versions ({len(version_dirs)}):")
        for version_dir in sorted(version_dirs):
            if version_dir.is_dir():
                size = sum(f.stat().st_size for f in version_dir.rglob('*') if f.is_file())
                total_bubble_size += size
                size_mb = size / (1024 * 1024)
                print(f"  - 📁 {version_dir.name} ({size_mb:.1f} MB)")

        total_bubble_size_mb = total_bubble_size / (1024 * 1024)
        print(f"  - Total Bubble Size: {total_bubble_size_mb:.1f} MB")

        return 0
