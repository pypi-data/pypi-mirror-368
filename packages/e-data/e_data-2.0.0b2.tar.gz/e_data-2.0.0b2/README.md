[![Downloads](https://pepy.tech/badge/e-data)](https://pepy.tech/project/e-data)
[![Downloads](https://pepy.tech/badge/e-data/month)](https://pepy.tech/project/e-data)
[![Downloads](https://pepy.tech/badge/e-data/week)](https://pepy.tech/project/e-data)

# python-edata

Este paquete proporciona herramientas para la descarga de tus datos de consumo eléctrico (desde Datadis.es) y su posterior procesado. La motivación principal es que conocer el consumo puede ayudarnos a reducirlo, e incluso a elegir una tarifa que mejor se adapte a nuestras necesidades. A día de hoy sus capacidades de facturación (€) son limitadas, soporta PVPC (según disponibilidad de datos de REData) y tarificación fija por tramos. Es el corazón de la integración [homeassistant-edata](https://github.com/uvejota/homeassistant-edata).

_**Esta herramienta no mantiene ningún tipo de vinculación con los proveedores de datos anteriormente mencionados, simplemente consulta la información disponible y facilita su posterior análisis.**_

## Instalación

Puedes instalar la última versión estable mediante:

``` bash
pip install e-data
```

Si quieres probar la versión `dev` o contribuir a su desarrollo, clona este repositorio e instala manualmente las dependencias:

``` bash
make install-dev
```

## Estructura

El paquete utiliza una **arquitectura basada en servicios** con los siguientes módulos:

* **Conectores** (módulo `connectors`), para definir los métodos de consulta a los diferentes proveedores: Datadis y REData.
* **Modelos** (módulo `models`), que definen las estructuras de datos usando Pydantic v2 para validación robusta. Incluye modelos para suministros, contratos, consumos, maxímetro, precios y base de datos.
* **Servicios** (módulo `services`), que implementan la lógica de negocio para cada dominio: gestión de suministros, contratos, consumos, maxímetro, facturación y base de datos SQLite.
* **Helper principal** (`helpers.py`), que orquesta todos los servicios y proporciona una interfaz simplificada. El `EdataHelper` permite descargar y procesar datos automáticamente, calculando más de 40 atributos de resumen.

Estos módulos corresponden a la siguiente estructura del paquete:

```
edata/
    · __init__.py
    · const.py                  # Constantes y definiciones de atributos
    · utils.py                  # Utilidades generales
    · helpers.py                # Helper principal (EdataHelper)
    · connectors/
        · __init__.py
        · datadis.py           # Conector API Datadis
        · redata.py            # Conector API REData (PVPC)
    · models/
        · __init__.py
        · base.py              # Modelos base con Pydantic
        · supply.py            # Modelo de suministros
        · contract.py          # Modelo de contratos
        · consumption.py       # Modelo de consumos
        · maximeter.py         # Modelo de maxímetro
        · pricing.py           # Modelo de reglas de precios
        · database.py          # Modelos para SQLite
    · services/
        · __init__.py
        · database.py          # Servicio de base de datos SQLite
        · supply.py            # Gestión de suministros
        · contract.py          # Gestión de contratos
        · consumption.py       # Gestión de consumos
        · maximeter.py         # Gestión de maxímetro
        · billing.py           # Gestión de facturación
    · scripts/
        · __init__.py
        · dump.py              # Script interactivo de descarga
```

## Script interactivo

El paquete incluye un script interactivo que facilita la descarga inicial de datos:

```bash
# Ejecutar el script interactivo
python -m edata.scripts.dump

# Con directorio personalizado
python -m edata.scripts.dump --storage-dir /ruta/personalizada
```

Este script te guiará paso a paso para:
1. Configurar credenciales de Datadis
2. Seleccionar el suministro a procesar
3. Definir el rango de fechas
4. Descargar y almacenar todos los datos

## Ejemplo de uso

Partimos de que tenemos credenciales en Datadis.es. Algunas aclaraciones:
* No es necesario solicitar API pública en el registro (se utilizará la API privada habilitada por defecto)
* El username suele ser el NIF del titular
* Copie el CUPS de la web de Datadis, algunas comercializadoras adhieren caracteres adicionales en el CUPS mostrado en su factura.
* La herramienta acepta el uso de NIF autorizado para consultar el suministro de otro titular.

``` python
import asyncio
from datetime import datetime
import json

# importamos el modelo de reglas de tarificación
from edata.models.pricing import PricingRules
# importamos el helper principal
from edata.helpers import EdataHelper
# importamos utilidades para serialización
from edata import utils

# Preparar reglas de tarificación (si se quiere)
PRICING_RULES_PVPC = PricingRules(
    p1_kw_year_eur=30.67266,
    p2_kw_year_eur=1.4243591,
    meter_month_eur=0.81,
    market_kw_year_eur=3.113,
    electricity_tax=1.0511300560,
    iva_tax=1.05,
    # podemos rellenar los siguientes campos si quisiéramos precio fijo (y no pvpc)
    p1_kwh_eur=None,
    p2_kwh_eur=None,
    p3_kwh_eur=None,
)

async def main():
    # Instanciar el helper
    # 'datadis_authorized_nif' permite indicar el NIF de la persona que nos autoriza a consultar su CUPS.
    # 'storage_dir_path' permite especificar dónde almacenar la base de datos local
    edata = EdataHelper(
                "datadis_user",
                "datadis_password",
                "cups",
                datadis_authorized_nif=None,
                pricing_rules=PRICING_RULES_PVPC, # si se le pasa None, no aplica tarificación
                storage_dir_path=None, # por defecto usa ./edata.storage/
            )

    # Solicitar actualización de todo el histórico (los datos se almacenan en SQLite)
    success = await edata.update(date_from=datetime(1970, 1, 1), date_to=datetime.today())
    
    if success:
        # Imprimir atributos resumen calculados
        print("Atributos calculados:")
        for key, value in edata.attributes.items():
            if value is not None:
                print(f"  {key}: {value}")
        
        # Los datos se almacenan automáticamente en la base de datos SQLite
        # ubicada en edata.storage/edata.db (por defecto)
        print(f"\nDatos almacenados en la base de datos local")
    else:
        print("Error durante la actualización de datos")

# Ejecutar el ejemplo
if __name__ == "__main__":
    asyncio.run(main())
```

## Contribuir

Este proyecto está en desarrollo activo. Las contribuciones son bienvenidas:

1. Fork del repositorio
2. Crear una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit de tus cambios: `git commit -am 'Añadir nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear un Pull Request

## Licencia

Este proyecto está licenciado bajo GPLv3. Ver el archivo [LICENSE](LICENSE) para más detalles.
