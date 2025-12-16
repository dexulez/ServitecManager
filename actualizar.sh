#!/bin/bash
# Script de actualización para Linux/Mac

clear
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║        🔄 ACTUALIZAR SERVITEC MANAGER DESDE GITHUB        ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo ""

echo "[1/5] 📥 Descargando últimos cambios desde GitHub..."
echo "────────────────────────────────────────────────────────────"
git pull origin main
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ ERROR: No se pudo actualizar desde GitHub"
    echo "   Verifique su conexión a internet o que el repositorio esté configurado"
    echo ""
    read -p "Presione ENTER para continuar..."
    exit 1
fi
echo "✅ Código actualizado correctamente"
echo ""
echo ""

echo "[2/5] 🔧 Aplicando migración de base de datos..."
echo "────────────────────────────────────────────────────────────"
cd servitec_manager
python3 migrar_descuento.py
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  ADVERTENCIA: La migración reportó un problema"
    echo "   Sin embargo, continuaremos con la actualización..."
    echo ""
fi
cd ..
echo ""
echo ""

echo "[3/5] 🗑️  Limpiando caché antiguo..."
echo "────────────────────────────────────────────────────────────"
if [ -d "servitec_manager/__pycache__" ]; then
    rm -rf "servitec_manager/__pycache__"
    echo "✅ Caché de Python limpiado"
fi
if [ -d "servitec_manager/ui/__pycache__" ]; then
    rm -rf "servitec_manager/ui/__pycache__"
    echo "✅ Caché de UI limpiado"
fi
echo ""
echo ""

echo "[4/5] 📦 Verificando dependencias..."
echo "────────────────────────────────────────────────────────────"
cd servitec_manager
python3 -c "import customtkinter, reportlab, pandas, openpyxl, pdfplumber" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Faltan algunas dependencias, instalando..."
    pip3 install -r requirements.txt --quiet
    if [ $? -ne 0 ]; then
        echo "❌ Error al instalar dependencias"
        echo "   Por favor ejecute: pip3 install -r requirements.txt"
        cd ..
        read -p "Presione ENTER para continuar..."
        exit 1
    fi
    echo "✅ Dependencias instaladas"
else
    echo "✅ Todas las dependencias están instaladas"
fi
cd ..
echo ""
echo ""

echo "[5/5] 🚀 Iniciando ServitecManager..."
echo "────────────────────────────────────────────────────────────"
echo ""
sleep 2
cd servitec_manager
python3 main.py
cd ..

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ ERROR: La aplicación se cerró con errores"
    echo "   Revise los mensajes de error anteriores"
    echo ""
    read -p "Presione ENTER para continuar..."
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║            ✅ ACTUALIZACIÓN COMPLETADA                     ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
