"""
Sistema de Actualización Automática para ServitecManager
Permite cargar y aplicar paquetes de actualización sin reinstalar el programa
"""
import os
import json
import zipfile
import shutil
import hashlib
from datetime import datetime
from pathlib import Path

VERSION_ACTUAL = "1.0.0"
VERSION_FILE = "version.json"

class GestorActualizaciones:
    def __init__(self, ruta_base=None):
        self.ruta_base = ruta_base or os.path.dirname(os.path.abspath(__file__))
        self.ruta_updates = os.path.join(self.ruta_base, "updates")
        self.ruta_backup = os.path.join(self.ruta_base, "backups")
        self.version_file = os.path.join(self.ruta_base, VERSION_FILE)
        
        # Crear directorios necesarios
        os.makedirs(self.ruta_updates, exist_ok=True)
        os.makedirs(self.ruta_backup, exist_ok=True)
        
        # Cargar versión actual
        self.version_actual = self.obtener_version_actual()
    
    def obtener_version_actual(self):
        """Obtiene la versión actual del sistema"""
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('version', VERSION_ACTUAL)
            return VERSION_ACTUAL
        except:
            return VERSION_ACTUAL
    
    def guardar_version(self, version, cambios=""):
        """Guarda la versión actual en el archivo de versión"""
        data = {
            'version': version,
            'fecha_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cambios': cambios
        }
        try:
            with open(self.version_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar versión: {e}")
            return False
    
    def validar_paquete_actualizacion(self, ruta_paquete):
        """
        Valida que el paquete de actualización sea correcto
        Retorna: (válido: bool, mensaje: str, datos: dict)
        """
        if not os.path.exists(ruta_paquete):
            return False, "El archivo no existe", None
        
        if not ruta_paquete.endswith('.zip'):
            return False, "El paquete debe ser un archivo .zip", None
        
        try:
            with zipfile.ZipFile(ruta_paquete, 'r') as zip_ref:
                # Verificar que contenga update.json
                if 'update.json' not in zip_ref.namelist():
                    return False, "El paquete no contiene 'update.json'", None
                
                # Leer configuración de actualización
                with zip_ref.open('update.json') as f:
                    update_info = json.load(f)
                
                # Validar campos obligatorios
                campos_requeridos = ['version', 'descripcion', 'archivos']
                for campo in campos_requeridos:
                    if campo not in update_info:
                        return False, f"Falta el campo obligatorio: {campo}", None
                
                # Verificar que sea una versión más nueva
                if not self._es_version_mas_nueva(update_info['version']):
                    return False, f"La versión {update_info['version']} no es más nueva que la actual {self.version_actual}", None
                
                # Verificar que todos los archivos declarados existan en el zip
                for archivo in update_info['archivos']:
                    if archivo['ruta'] not in zip_ref.namelist():
                        return False, f"Archivo faltante en el paquete: {archivo['ruta']}", None
                
                return True, "Paquete válido", update_info
                
        except zipfile.BadZipFile:
            return False, "El archivo no es un ZIP válido", None
        except json.JSONDecodeError:
            return False, "El archivo update.json no es un JSON válido", None
        except Exception as e:
            return False, f"Error al validar paquete: {str(e)}", None
    
    def _es_version_mas_nueva(self, version_nueva):
        """Compara versiones en formato X.Y.Z"""
        try:
            v_actual = [int(x) for x in self.version_actual.split('.')]
            v_nueva = [int(x) for x in version_nueva.split('.')]
            
            for i in range(3):
                if v_nueva[i] > v_actual[i]:
                    return True
                elif v_nueva[i] < v_actual[i]:
                    return False
            return False  # Son iguales
        except:
            return True  # En caso de error, permitir actualización
    
    def crear_backup(self):
        """Crea un backup del sistema actual antes de actualizar"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_nombre = f"backup_v{self.version_actual}_{timestamp}"
        backup_path = os.path.join(self.ruta_backup, backup_nombre)
        
        try:
            os.makedirs(backup_path, exist_ok=True)
            
            # Archivos y carpetas a respaldar
            items_backup = [
                'ui',
                'database.py',
                'logic.py',
                'main.py',
                'pdf_generator_v2.py',
                'importer.py',
                VERSION_FILE
            ]
            
            for item in items_backup:
                origen = os.path.join(self.ruta_base, item)
                if os.path.exists(origen):
                    destino = os.path.join(backup_path, item)
                    if os.path.isdir(origen):
                        shutil.copytree(origen, destino, dirs_exist_ok=True)
                    else:
                        os.makedirs(os.path.dirname(destino), exist_ok=True)
                        shutil.copy2(origen, destino)
            
            # Guardar info del backup
            backup_info = {
                'version': self.version_actual,
                'fecha': timestamp,
                'ruta': backup_path
            }
            
            with open(os.path.join(backup_path, 'backup_info.json'), 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=4, ensure_ascii=False)
            
            return True, backup_path
            
        except Exception as e:
            return False, f"Error al crear backup: {str(e)}"
    
    def aplicar_actualizacion(self, ruta_paquete, callback_progreso=None):
        """
        Aplica una actualización desde un paquete ZIP
        callback_progreso: función(mensaje, porcentaje) para reportar progreso
        Retorna: (éxito: bool, mensaje: str)
        """
        def progreso(msg, pct=0):
            if callback_progreso:
                callback_progreso(msg, pct)
            print(f"[{pct}%] {msg}")
        
        # 1. Validar paquete
        progreso("Validando paquete de actualización...", 10)
        valido, mensaje, update_info = self.validar_paquete_actualizacion(ruta_paquete)
        
        if not valido:
            return False, mensaje
        
        progreso(f"Paquete válido - Versión {update_info['version']}", 20)
        
        # 2. Crear backup
        progreso("Creando backup del sistema actual...", 30)
        backup_ok, backup_path = self.crear_backup()
        
        if not backup_ok:
            return False, backup_path  # backup_path contiene el mensaje de error
        
        progreso(f"Backup creado en: {os.path.basename(backup_path)}", 40)
        
        # 3. Extraer y aplicar archivos
        progreso("Aplicando actualización...", 50)
        
        try:
            with zipfile.ZipFile(ruta_paquete, 'r') as zip_ref:
                total_archivos = len(update_info['archivos'])
                
                for idx, archivo_info in enumerate(update_info['archivos']):
                    ruta_archivo = archivo_info['ruta']
                    accion = archivo_info.get('accion', 'actualizar')
                    
                    # Calcular progreso (50% a 90%)
                    pct = 50 + int((idx / total_archivos) * 40)
                    progreso(f"Procesando: {ruta_archivo}", pct)
                    
                    destino = os.path.join(self.ruta_base, ruta_archivo)
                    
                    if accion == 'eliminar':
                        # Eliminar archivo
                        if os.path.exists(destino):
                            os.remove(destino)
                    
                    elif accion == 'actualizar' or accion == 'nuevo':
                        # Crear directorio si no existe
                        os.makedirs(os.path.dirname(destino), exist_ok=True)
                        
                        # Extraer archivo
                        with zip_ref.open(ruta_archivo) as source, open(destino, 'wb') as target:
                            shutil.copyfileobj(source, target)
            
            # 4. Actualizar versión
            progreso("Actualizando información de versión...", 95)
            self.guardar_version(update_info['version'], update_info['descripcion'])
            self.version_actual = update_info['version']
            
            progreso("Actualización completada exitosamente", 100)
            
            return True, f"Sistema actualizado a versión {update_info['version']}\n\nCambios:\n{update_info['descripcion']}\n\nSe recomienda reiniciar la aplicación."
            
        except Exception as e:
            # En caso de error, intentar restaurar backup
            progreso(f"Error durante actualización: {str(e)}", 0)
            self.restaurar_backup(backup_path)
            return False, f"Error al aplicar actualización: {str(e)}\n\nSe ha restaurado el backup automáticamente."
    
    def restaurar_backup(self, ruta_backup):
        """Restaura un backup en caso de error"""
        try:
            # Leer info del backup
            with open(os.path.join(ruta_backup, 'backup_info.json'), 'r', encoding='utf-8') as f:
                backup_info = json.load(f)
            
            # Restaurar archivos
            for item in os.listdir(ruta_backup):
                if item == 'backup_info.json':
                    continue
                
                origen = os.path.join(ruta_backup, item)
                destino = os.path.join(self.ruta_base, item)
                
                if os.path.isdir(origen):
                    if os.path.exists(destino):
                        shutil.rmtree(destino)
                    shutil.copytree(origen, destino)
                else:
                    shutil.copy2(origen, destino)
            
            # Restaurar versión
            self.version_actual = backup_info['version']
            self.guardar_version(self.version_actual, "Sistema restaurado desde backup")
            
            return True, "Backup restaurado correctamente"
            
        except Exception as e:
            return False, f"Error al restaurar backup: {str(e)}"
    
    def listar_backups(self):
        """Lista todos los backups disponibles"""
        backups = []
        
        if not os.path.exists(self.ruta_backup):
            return backups
        
        for carpeta in os.listdir(self.ruta_backup):
            ruta_info = os.path.join(self.ruta_backup, carpeta, 'backup_info.json')
            if os.path.exists(ruta_info):
                try:
                    with open(ruta_info, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                        info['nombre'] = carpeta
                        backups.append(info)
                except:
                    pass
        
        return sorted(backups, key=lambda x: x['fecha'], reverse=True)
    
    def obtener_historial_actualizaciones(self):
        """Obtiene el historial de actualizaciones aplicadas"""
        historial = []
        
        # Buscar en backups
        for backup in self.listar_backups():
            historial.append({
                'version': backup['version'],
                'fecha': backup['fecha'],
                'tipo': 'backup'
            })
        
        # Agregar versión actual
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    historial.insert(0, {
                        'version': data.get('version', VERSION_ACTUAL),
                        'fecha': data.get('fecha_actualizacion', 'Desconocida'),
                        'cambios': data.get('cambios', ''),
                        'tipo': 'actual'
                    })
        except:
            pass
        
        return historial


def crear_paquete_actualizacion(version, descripcion, archivos_modificados, ruta_salida):
    """
    Función auxiliar para crear paquetes de actualización
    
    Args:
        version: Versión del paquete (ej: "1.1.0")
        descripcion: Descripción de los cambios
        archivos_modificados: Lista de diccionarios con 'ruta' y 'accion'
        ruta_salida: Ruta donde guardar el paquete ZIP
    
    Ejemplo de archivos_modificados:
    [
        {'ruta': 'ui/pos.py', 'accion': 'actualizar'},
        {'ruta': 'ui/cash.py', 'accion': 'actualizar'},
        {'ruta': 'database.py', 'accion': 'actualizar'}
    ]
    """
    try:
        # Crear update.json
        update_info = {
            'version': version,
            'descripcion': descripcion,
            'fecha_creacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'archivos': archivos_modificados
        }
        
        # Crear el ZIP
        with zipfile.ZipFile(ruta_salida, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Agregar update.json
            zipf.writestr('update.json', json.dumps(update_info, indent=4, ensure_ascii=False))
            
            # Agregar archivos modificados
            base_path = os.path.dirname(os.path.abspath(__file__))
            for archivo in archivos_modificados:
                if archivo['accion'] != 'eliminar':
                    ruta_completa = os.path.join(base_path, archivo['ruta'])
                    if os.path.exists(ruta_completa):
                        zipf.write(ruta_completa, archivo['ruta'])
        
        return True, f"Paquete creado exitosamente: {ruta_salida}"
        
    except Exception as e:
        return False, f"Error al crear paquete: {str(e)}"


# Ejemplo de uso
if __name__ == "__main__":
    # Crear un paquete de ejemplo
    archivos = [
        {'ruta': 'ui/pos.py', 'accion': 'actualizar'},
        {'ruta': 'ui/cash.py', 'accion': 'actualizar'}
    ]
    
    crear_paquete_actualizacion(
        version="1.0.1",
        descripcion="- Corrección de bugs en POS\n- Mejoras en módulo de caja",
        archivos_modificados=archivos,
        ruta_salida="update_v1.0.1.zip"
    )
