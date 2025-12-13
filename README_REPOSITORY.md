# ServitecManager - Sistema de Gestión Completo

## 📋 Descripción
ServitecManager es un sistema de gestión integral desarrollado en Python con CustomTkinter para el manejo de servicios técnicos, inventario, ventas y administración.

## ✨ Características Principales
- **Gestión de Inventario**: Control de productos, repuestos y servicios
- **Sistema POS**: Punto de venta completo con múltiples métodos de pago
- **Gestión de Órdenes**: Seguimiento completo del flujo de trabajo
- **Caja y Turnos**: Manejo de arqueos y control de efectivo
- **Reportes Avanzados**: Análisis de ventas y rendimiento
- **Historial Completo**: Seguimiento de todas las transacciones
- **Sistema Multiusuario**: Diferentes roles y permisos
- **Cache Inteligente**: Sistema optimizado para alto rendimiento
- **Limpieza Automática**: Auto-limpieza de cache al iniciar

## 🚀 Características Técnicas
- **Python 3.13** con CustomTkinter para interfaz moderna
- **Base de datos SQLite** con optimizaciones WAL y MMAP
- **Cache en memoria** para operaciones 100x más rápidas
- **Sistema de backup** automático
- **Docker ready** para despliegue
- **API REST** para integraciones externas

## 🛠️ Instalación

### Requisitos
- Python 3.13+
- Dependencias listadas en `requirements.txt`

### Instalación Rápida
```bash
# Clonar el repositorio
git clone [URL_DEL_REPOSITORIO]
cd ServitecManager

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python servitec_manager/main.py
```

### Con Docker
```bash
# Construir la imagen
docker build -t servitecmanager .

# Ejecutar el contenedor
docker run -d -p 8000:8000 servitecmanager
```

## 📁 Estructura del Proyecto
```
ServitecManager/
├── servitec_manager/           # Código principal
│   ├── ui/                     # Interfaces de usuario
│   ├── database.py             # Gestión de base de datos
│   ├── logic.py                # Lógica de negocio
│   ├── main.py                 # Punto de entrada
│   └── ...
├── requirements.txt            # Dependencias
├── README.md                   # Este archivo
└── docker-compose.yml         # Configuración Docker
```

## 🎯 Módulos Principales
- **Dashboard**: Panel principal con métricas
- **POS/Ventas**: Sistema de punto de venta
- **Inventario**: Gestión de productos y stock
- **Taller**: Órdenes de servicio y seguimiento
- **Caja**: Manejo de turnos y arqueos
- **Reportes**: Análisis y estadísticas
- **Administración**: Configuración del sistema

## 💡 Funcionalidades Destacadas
- ✅ **Auto-limpieza de cache** al iniciar
- ✅ **Interfaz moderna** con CustomTkinter
- ✅ **Base de datos optimizada** con índices y WAL
- ✅ **Sistema de backup** automático
- ✅ **Multiusuario** con roles
- ✅ **Reportes PDF** personalizables
- ✅ **Importación Excel** masiva
- ✅ **API REST** integrada
- ✅ **Docker ready**

## 🔧 Configuración
El sistema incluye configuración automática, pero puedes personalizar:
- Configuración de empresa en la interfaz de administración
- Parámetros de base de datos en `database.py`
- Configuración de cache en `cache_manager.py`

## 📊 Rendimiento
- **Cache inteligente**: Reduce consultas DB en 90%
- **Optimizaciones WAL**: Escrituras 3x más rápidas
- **Índices automáticos**: Consultas optimizadas
- **Limpieza automática**: Previene errores de cache

## 🤝 Contribución
Las contribuciones son bienvenidas. Para contribuir:
1. Fork del repositorio
2. Crear rama para tu feature
3. Commit de cambios
4. Push a la rama
5. Crear Pull Request

## 📝 Licencia
Este proyecto está bajo licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte
Para soporte técnico o consultas:
- Crear issue en GitHub
- Revisar documentación en `/docs`
- Consultar README específicos de cada módulo

## 🔄 Actualizaciones Recientes
- ✅ Sistema de limpieza automática de cache
- ✅ Optimización del layout de caja
- ✅ Mejoras en el historial editable
- ✅ Corrección de bugs en el sistema de estados
- ✅ Configuración Docker completa

---

**ServitecManager** - Tu solución completa para gestión de servicios técnicos 🛠️