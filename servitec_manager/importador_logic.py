"""
MÓDULO IMPORTADOR INTELIGENTE
Importación de datos desde Excel, CSV y PDF
Validación inteligente e inserción en base de datos
"""


class IMPORTADOR_DATOS:
    """Importador inteligente de múltiples formatos de datos"""
    
    def __init__(self, db_gestor, logic_gestor):
        """
        Args:
            db_gestor: Instancia GESTOR_BASE_DATOS
            logic_gestor: Instancia GESTOR_LOGICA
        """
        self.db = db_gestor
        self.logic = logic_gestor
        self.errores = []
        self.advertencias = []
        self.registros_procesados = 0
        self.registros_saltados = 0
        
    # --- 1. IMPORTACIÓN DE ARCHIVOS ---
    
    def IMPORTAR_ARCHIVO(self, ruta_archivo):
        """Importa archivo según su extensión"""
        self.errores = []
        self.advertencias = []
        self.registros_procesados = 0
        self.registros_saltados = 0
        
        if not os.path.exists(ruta_archivo):
            self.errores.append(f"Archivo no encontrado: {ruta_archivo}")
            return False
            
        ext = Path(ruta_archivo).suffix.lower()
        
        try:
            if ext == ".xlsx" or ext == ".xls":
                return self.IMPORTAR_EXCEL(ruta_archivo)
            elif ext == ".csv":
                return self.IMPORTAR_CSV(ruta_archivo)
            else:
                self.errores.append(f"Formato no soportado: {ext}")
                return False
        except Exception as e:
            self.errores.append(f"Error al importar archivo: {str(e)}")
            return False
    
    def IMPORTAR_EXCEL(self, ruta_archivo):
        """Importa datos desde Excel (órdenes, clientes, productos)"""
        try:
            df = pd.read_excel(ruta_archivo)
            self.advertencias.append(f"Archivo cargado: {len(df)} filas detectadas")
            
            # Detectar tipo de datos a importar según columnas
            columnas = df.columns.str.upper().tolist()
            
            if "CLIENTE" in columnas or "RUT" in columnas:
                return self._IMPORTAR_CLIENTES_EXCEL(df)
            elif "EQUIPO" in columnas or "MARCA" in columnas:
                return self._IMPORTAR_ORDENES_EXCEL(df)
            elif "PRODUCTO" in columnas or "PRECIO" in columnas:
                return self._IMPORTAR_INVENTARIO_EXCEL(df)
            else:
                self.errores.append("No se pudo determinar el tipo de datos a importar")
                return False
                
        except Exception as e:
            self.errores.append(f"Error en lectura de Excel: {str(e)}")
            return False
    
    def IMPORTAR_CSV(self, ruta_archivo):
        """Importa datos desde CSV"""
        try:
            df = pd.read_csv(ruta_archivo, encoding='utf-8')
            
            # Detectar tipo de datos
            columnas = df.columns.str.upper().tolist()
            
            if "CLIENTE" in columnas or "RUT" in columnas:
                return self._IMPORTAR_CLIENTES_EXCEL(df)
            elif "EQUIPO" in columnas or "MARCA" in columnas:
                return self._IMPORTAR_ORDENES_EXCEL(df)
            else:
                self.errores.append("Formato de CSV no reconocido")
                return False
                
        except Exception as e:
            self.errores.append(f"Error en lectura de CSV: {str(e)}")
            return False
    
    # --- 2. IMPORTACIÓN DE CLIENTES ---
    
    def _IMPORTAR_CLIENTES_EXCEL(self, df):
        """Importa clientes desde DataFrame"""
        try:
            df.columns = df.columns.str.upper()
            
            # Mapeo flexible de columnas
            col_rut = self._ENCONTRAR_COLUMNA(df, ["RUT", "CÉDULA", "ID_CLIENTE"])
            col_nombre = self._ENCONTRAR_COLUMNA(df, ["NOMBRE", "CLIENTE", "NOMBRE_CLIENTE"])
            col_telefono = self._ENCONTRAR_COLUMNA(df, ["TELÉFONO", "TELEFONO", "FONO"])
            col_email = self._ENCONTRAR_COLUMNA(df, ["EMAIL", "CORREO", "MAIL"])
            col_ciudad = self._ENCONTRAR_COLUMNA(df, ["CIUDAD", "LOCALIDAD"])
            
            for idx, row in df.iterrows():
                try:
                    rut = str(row[col_rut]).strip() if col_rut else ""
                    nombre = str(row[col_nombre]).strip() if col_nombre else "SIN NOMBRE"
                    telefono = str(row[col_telefono]).strip() if col_telefono else ""
                    email = str(row[col_email]).strip() if col_email else ""
                    ciudad = str(row[col_ciudad]).strip() if col_ciudad else ""
                    
                    # Validaciones
                    if not rut or rut.upper() == "NAN":
                        self.advertencias.append(f"Fila {idx+1}: RUT vacío, SALTADA")
                        self.registros_saltados += 1
                        continue
                    
                    # Verificar si cliente existe
                    existe = self.db.fetch_one(
                        "SELECT id FROM clientes WHERE rut = ?", 
                        (rut,)
                    )
                    
                    if existe:
                        self.advertencias.append(f"Cliente {rut} ya existe, ACTUALIZADO")
                        self.db.execute(
                            "UPDATE clientes SET nombre=?, telefono=?, email=?, ciudad=?, fecha_actualizacion=? WHERE rut=?",
                            (nombre, telefono, email, ciudad, datetime.now(), rut)
                        )
                    else:
                        self.db.execute(
                            "INSERT INTO clientes (rut, nombre, telefono, email, ciudad, fecha_creacion) VALUES (?, ?, ?, ?, ?, ?)",
                            (rut, nombre, telefono, email, ciudad, datetime.now())
                        )
                        self.registros_procesados += 1
                        
                except Exception as e:
                    self.advertencias.append(f"Fila {idx+1}: Error - {str(e)}")
                    self.registros_saltados += 1
            
            self.db.commit()
            self.advertencias.append(f"Importación completada: {self.registros_procesados} nuevos, {self.registros_saltados} saltados")
            return True
            
        except Exception as e:
            self.errores.append(f"Error en importación de clientes: {str(e)}")
            return False
    
    # --- 3. IMPORTACIÓN DE ÓRDENES ---
    
    def _IMPORTAR_ORDENES_EXCEL(self, df):
        """Importa órdenes desde DataFrame"""
        try:
            df.columns = df.columns.str.upper()
            
            col_cliente = self._ENCONTRAR_COLUMNA(df, ["CLIENTE", "RUT_CLIENTE"])
            col_equipo = self._ENCONTRAR_COLUMNA(df, ["EQUIPO", "TIPO"])
            col_marca = self._ENCONTRAR_COLUMNA(df, ["MARCA", "FABRICANTE"])
            col_modelo = self._ENCONTRAR_COLUMNA(df, ["MODELO", "VERSION"])
            col_falla = self._ENCONTRAR_COLUMNA(df, ["FALLA", "PROBLEMA", "DESCRIPCIÓN"])
            col_presupuesto = self._ENCONTRAR_COLUMNA(df, ["PRESUPUESTO", "PRECIO", "VALOR"])
            col_estado = self._ENCONTRAR_COLUMNA(df, ["ESTADO", "STATUS"])
            
            for idx, row in df.iterrows():
                try:
                    cliente_ref = str(row[col_cliente]).strip() if col_cliente else ""
                    equipo = str(row[col_equipo]).strip() if col_equipo else "EQUIPO"
                    marca = str(row[col_marca]).strip() if col_marca else ""
                    modelo = str(row[col_modelo]).strip() if col_modelo else ""
                    falla = str(row[col_falla]).strip() if col_falla else "SIN DESCRIPCIÓN"
                    
                    try:
                        presupuesto = float(str(row[col_presupuesto]).replace("$", "").replace(".", "").replace(",", ".")) if col_presupuesto else 0
                    except:
                        presupuesto = 0
                    
                    estado = str(row[col_estado]).strip().upper() if col_estado else "PENDIENTE"
                    
                    # Validar cliente
                    cliente = self.db.fetch_one(
                        "SELECT id FROM clientes WHERE rut = ? OR nombre LIKE ?",
                        (cliente_ref, f"%{cliente_ref}%")
                    )
                    
                    if not cliente:
                        self.advertencias.append(f"Fila {idx+1}: Cliente no encontrado ({cliente_ref}), SALTADA")
                        self.registros_saltados += 1
                        continue
                    
                    # Insertar orden
                    self.db.execute(
                        "INSERT INTO ordenes (cliente_id, tipo, marca, modelo, observacion, presupuesto, estado, fecha) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (cliente[0], equipo, marca, modelo, falla, presupuesto, estado, datetime.now())
                    )
                    self.registros_procesados += 1
                    
                except Exception as e:
                    self.advertencias.append(f"Fila {idx+1}: Error - {str(e)}")
                    self.registros_saltados += 1
            
            self.db.commit()
            self.advertencias.append(f"Importación de órdenes completada: {self.registros_procesados} nuevas")
            return True
            
        except Exception as e:
            self.errores.append(f"Error en importación de órdenes: {str(e)}")
            return False
    
    # --- 4. IMPORTACIÓN DE INVENTARIO ---
    
    def _IMPORTAR_INVENTARIO_EXCEL(self, df):
        """Importa productos/inventario desde DataFrame"""
        try:
            df.columns = df.columns.str.upper()
            
            col_producto = self._ENCONTRAR_COLUMNA(df, ["PRODUCTO", "NOMBRE", "ARTÍCULO"])
            col_precio = self._ENCONTRAR_COLUMNA(df, ["PRECIO", "VALOR", "COSTO"])
            col_cantidad = self._ENCONTRAR_COLUMNA(df, ["CANTIDAD", "STOCK", "EXISTENCIA"])
            col_categoria = self._ENCONTRAR_COLUMNA(df, ["CATEGORÍA", "CATEGORIA", "TIPO"])
            
            for idx, row in df.iterrows():
                try:
                    producto = str(row[col_producto]).strip() if col_producto else ""
                    
                    if not producto or producto.upper() == "NAN":
                        self.registros_saltados += 1
                        continue
                    
                    try:
                        precio = float(str(row[col_precio]).replace("$", "").replace(".", "").replace(",", ".")) if col_precio else 0
                    except:
                        precio = 0
                    
                    try:
                        cantidad = int(str(row[col_cantidad]).replace(".", "").replace(",", ".")) if col_cantidad else 0
                    except:
                        cantidad = 0
                    
                    categoria = str(row[col_categoria]).strip() if col_categoria else "GENERAL"
                    
                    # Verificar si existe
                    existe = self.db.fetch_one(
                        "SELECT id FROM inventario WHERE nombre = ?",
                        (producto,)
                    )
                    
                    if existe:
                        self.db.execute(
                            "UPDATE inventario SET precio=?, cantidad=?, categoria=? WHERE nombre=?",
                            (precio, cantidad, categoria, producto)
                        )
                    else:
                        self.db.execute(
                            "INSERT INTO inventario (nombre, precio, cantidad, categoria) VALUES (?, ?, ?, ?)",
                            (producto, precio, cantidad, categoria)
                        )
                        self.registros_procesados += 1
                        
                except Exception as e:
                    self.advertencias.append(f"Fila {idx+1}: Error - {str(e)}")
                    self.registros_saltados += 1
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.errores.append(f"Error en importación de inventario: {str(e)}")
            return False
    
    # --- 5. UTILIDADES ---
    
    def _ENCONTRAR_COLUMNA(self, df, nombres_posibles):
        """Busca columna en DataFrame con nombres flexibles"""
        for col in df.columns:
            if col.upper() in [n.upper() for n in nombres_posibles]:
                return col
        return None
    
    def OBTENER_REPORTE_IMPORTACION(self):
        """Retorna reporte detallado de la importación"""
        return {
            "registros_procesados": self.registros_procesados,
            "registros_saltados": self.registros_saltados,
            "total": self.registros_procesados + self.registros_saltados,
            "errores": self.errores,
            "advertencias": self.advertencias
        }
