#!/usr/bin/env bash
set -e

# Asegurar que ruff y xsdata en .venv/Scripts o PATH estén disponibles
export PATH="$(pwd)/../.venv/Scripts:$(pwd)/.venv/Scripts:$PATH"

echo "Generando clases UBL 2.1 con xsdata a partir de xsd/maindoc/UBL-Invoice-2.1.xsd..."
xsdata generate xsd/maindoc/UBL-Invoice-2.1.xsd --package abc_cpe.ubl_generado --structure-style namespaces

echo "Generación completada exitosamente. NO editar los archivos generados en abc_cpe/ubl_generado."
