"""
Setup script para crear instalador de ServitecManager
Usa cx_Freeze para generar un instalador MSI para Windows
"""
import sys
from cx_Freeze import setup, Executable

# Dependencias que deben incluirse
build_exe_options = {
    "packages": [
        "customtkinter",
        "reportlab",
        "matplotlib",
        "tkcalendar",
        "PIL",
        "pandas",
        "openpyxl",
        "pdfplumber",
        "tkinter",
        "sqlite3",
        "datetime",
        "os",
        "shutil",
        "json",
        "threading",
        "zipfile",
        "hashlib",
        "calendar"
    ],
    "include_files": [
        ("servitec_manager/assets/", "assets/"),
        ("servitec_manager/version.json", "version.json"),
    ],
    "excludes": ["test", "unittest", "setuptools"],
    "include_msvcr": True,
    "optimize": 2,
}

# Opciones para el instalador MSI
bdist_msi_options = {
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\ServitecManager",
    "upgrade_code": "{12345678-1234-1234-1234-123456789012}",
    "all_users": True,
    "install_icon": None,
    "summary_data": {
        "author": "ServitecManager Team",
        "comments": "Sistema Profesional de Gestión de Servicios Técnicos",
        "keywords": "servicio técnico, gestión, reparaciones"
    },
}

# Configuración del ejecutable con acceso directo
shortcut_table = [
    (
        "DesktopShortcut",                      # Shortcut ID
        "DesktopFolder",                         # Directorio de destino
        "ServitecManager",                       # Nombre del acceso directo
        "TARGETDIR",                             # Componente
        "[TARGETDIR]ServitecManager.exe",       # Target
        None,                                    # Arguments
        "Sistema de Gestión de Servicios Técnicos",  # Descripción
        None,                                    # Hotkey
        None,                                    # Icon
        None,                                    # IconIndex
        None,                                    # ShowCmd
        "TARGETDIR"                              # WkDir
    ),
    (
        "ProgramMenuShortcut",                   # Shortcut ID
        "ProgramMenuFolder",                     # Directorio de destino
        "ServitecManager",                       # Nombre del acceso directo
        "TARGETDIR",                             # Componente
        "[TARGETDIR]ServitecManager.exe",       # Target
        None,                                    # Arguments
        "Sistema de Gestión de Servicios Técnicos",  # Descripción
        None,                                    # Hotkey
        None,                                    # Icon
        None,                                    # IconIndex
        None,                                    # ShowCmd
        "TARGETDIR"                              # WkDir
    ),
]

# Agregar tabla de accesos directos a las opciones MSI
msi_data = {
    "Shortcut": shortcut_table
}

bdist_msi_options["data"] = msi_data

# Configuración del ejecutable
# Para cx_Freeze 7.x con Python 3.13, usar None para GUI
base = None

executables = [
    Executable(
        "servitec_manager/main.py",
        base=base,
        target_name="ServitecManager.exe",
        shortcut_name="ServitecManager",
        shortcut_dir="DesktopFolder",
    )
]

setup(
    name="ServitecManager",
    version="1.1.0",
    description="Sistema de Gestión de Servicios Técnicos",
    author="ServitecManager Team",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
    executables=executables,
)
