#!/usr/bin/env python3
"""
Script interactivo para hacer un dump completo de un CUPS a una base de datos.
"""

import argparse
import asyncio
import getpass
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from edata.connectors.datadis import DatadisConnector
from edata.const import DEFAULT_STORAGE_DIR
from edata.helpers import EdataHelper
from edata.services.database import SupplyModel as DbSupply
from edata.services.supply import SupplyService

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

_LOGGER = logging.getLogger(__name__)


class DumpSupply:
    """Clase para hacer dump interactivo completo de un CUPS."""

    def __init__(self, storage_dir: Optional[str] = None):
        """Inicializar el dumper interactivo."""
        self.storage_dir = storage_dir or DEFAULT_STORAGE_DIR
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.authorized_nif: Optional[str] = None
        self.connector: Optional[DatadisConnector] = None
        self.supplies: List[DbSupply] = []

    def get_credentials(self) -> bool:
        """Obtener credenciales del usuario de forma interactiva."""
        print("\n🔐 Configuración de credenciales Datadis")
        print("=" * 50)

        try:
            self.username = input("📧 Usuario Datadis: ").strip()
            if not self.username:
                print("❌ El usuario es obligatorio")
                return False
            print(self.username)

            self.password = getpass.getpass("🔑 Contraseña Datadis: ").strip()
            if not self.password:
                print("❌ La contraseña es obligatoria")
                return False
            print(self.password)

            nif_input = input(
                "🆔 NIF autorizado (opcional, Enter para omitir): "
            ).strip()
            self.authorized_nif = nif_input if nif_input else None

            return True

        except KeyboardInterrupt:
            print("\n❌ Operación cancelada por el usuario")
            return False
        except Exception as e:
            print(f"❌ Error obteniendo credenciales: {e}")
            return False

    async def test_connection(self) -> bool:
        """Probar la conexión con Datadis."""
        print("\n🧪 Probando conexión con Datadis...")

        try:
            # Verificar que tenemos credenciales
            if not self.username or not self.password:
                print("❌ Credenciales no disponibles")
                return False

            self.connector = DatadisConnector(self.username, self.password)

            # Probar autenticación
            token_result = await self.connector.login()
            if not token_result:
                print("❌ Error de autenticación. Verifica tus credenciales.")
                return False

            print("✅ Conexión exitosa con Datadis")
            return True

        except Exception as e:
            print(f"❌ Error conectando con Datadis: {e}")
            return False

    async def fetch_supplies(self) -> bool:
        """Obtener y mostrar los suministros disponibles."""
        print("\n📋 Obteniendo suministros disponibles...")

        try:
            # Verificar que tenemos credenciales
            if not self.username or not self.password:
                print("❌ Credenciales no disponibles")
                return False

            supplies_service = SupplyService(
                DatadisConnector(
                    username=self.username,
                    password=self.password,
                    storage_path=self.storage_dir,
                ),
                storage_dir=self.storage_dir,
            )

            # Actualizar supplies
            result = await supplies_service.update_supplies(
                authorized_nif=self.authorized_nif
            )
            if not result["success"]:
                print(
                    f"❌ Error obteniendo suministros: {result.get('error', 'Error desconocido')}"
                )
                return False

            # Obtener todos los supplies desde la base de datos
            self.supplies = await supplies_service.get_supplies()

            if not self.supplies:
                print("❌ No se encontraron suministros en tu cuenta")
                return False

            print(f"✅ Encontrados {len(self.supplies)} suministros")
            return True

        except Exception as e:
            print(f"❌ Error obteniendo suministros: {e}")
            return False

    def display_supplies_menu(self) -> Optional[DbSupply]:
        """Mostrar menú de suministros y obtener selección."""
        print("\n🏠 Selecciona un suministro para procesar:")
        print("=" * 70)

        for i, supply in enumerate(self.supplies, 1):
            # Mostrar información del suministro
            cups_short = supply.cups[-10:] if len(supply.cups) > 10 else supply.cups
            address = supply.address or "Dirección no disponible"
            if len(address) > 40:
                address = address[:40] + "..."

            print(f"{i:2d}. CUPS: {cups_short} | {address}")
            print(
                f"     📍 {supply.municipality or 'N/A'}, {supply.province or 'N/A'} ({supply.postal_code or 'N/A'})"
            )
            print(
                f"     📊 Tipo: {supply.point_type} | Distribuidor: {supply.distributor or 'N/A'}"
            )
            print(
                f"     📅 Válido: {supply.date_start.date()} - {supply.date_end.date()}"
            )
            print()

        try:
            selection = input(
                f"Selecciona un suministro (1-{len(self.supplies)}) o 'q' para salir: "
            ).strip()

            if selection.lower() == "q":
                return None

            index = int(selection) - 1
            if 0 <= index < len(self.supplies):
                return self.supplies[index]
            else:
                print(
                    f"❌ Selección inválida. Debe estar entre 1 y {len(self.supplies)}"
                )
                return self.display_supplies_menu()

        except ValueError:
            print("❌ Por favor introduce un número válido")
            return self.display_supplies_menu()
        except KeyboardInterrupt:
            print("\n❌ Operación cancelada")
            return None

    def get_date_range(self) -> tuple[datetime, datetime]:
        """Obtener rango de fechas del usuario."""
        print("\n📅 Configuración de fechas")
        print("=" * 30)
        print("Deja en blanco para usar valores por defecto (últimos 2 años)")

        try:
            date_from_str = input(
                "📅 Fecha inicio (YYYY-MM-DD) [Enter = 2 años atrás]: "
            ).strip()
            date_to_str = input("📅 Fecha fin (YYYY-MM-DD) [Enter = hoy]: ").strip()

            date_from = None
            date_to = None

            if date_from_str:
                try:
                    date_from = datetime.strptime(date_from_str, "%Y-%m-%d")
                except ValueError:
                    print(
                        "❌ Formato de fecha inicio inválido, usando valor por defecto"
                    )

            if date_to_str:
                try:
                    date_to = datetime.strptime(date_to_str, "%Y-%m-%d")
                except ValueError:
                    print("❌ Formato de fecha fin inválido, usando valor por defecto")

            # Valores por defecto
            if date_from is None:
                date_from = datetime.now() - timedelta(days=730)
            if date_to is None:
                date_to = datetime.now()

            print(f"📊 Período seleccionado: {date_from.date()} a {date_to.date()}")
            return date_from, date_to

        except KeyboardInterrupt:
            print("❌ Usando valores por defecto")
            default_from = datetime.now() - timedelta(days=730)
            default_to = datetime.now()
            return default_from, default_to

    async def dump_selected_supply(
        self, supply: DbSupply, date_from: datetime, date_to: datetime
    ) -> bool:
        """Hacer dump completo de un suministro seleccionado."""
        print(f"🚀 Iniciando dump para CUPS {supply.cups[-10:]}")
        print("=" * 50)

        try:
            # Verificar que tenemos credenciales
            if not self.username or not self.password:
                print("❌ Credenciales no disponibles")
                return False

            # Crear EdataHelper para este CUPS
            helper = EdataHelper(
                datadis_username=self.username,
                datadis_password=self.password,
                cups=supply.cups,
                datadis_authorized_nif=self.authorized_nif,
                storage_dir_path=self.storage_dir,
            )

            print(f"📅 Período: {date_from.date()} a {date_to.date()}")
            print("⏳ Descargando datos... (esto puede tomar varios minutos)")

            # Actualizar todos los datos
            result = await helper.update(date_from=date_from, date_to=date_to)

            if not result:
                print("❌ Error durante la descarga de datos")
                return False

            print("✅ Datos descargados correctamente")

            # Mostrar estadísticas
            await self.display_final_statistics(helper)

            return True

        except Exception as e:
            print(f"❌ Error durante el dump: {e}")
            return False

    async def display_final_statistics(self, helper: EdataHelper):
        """Mostrar estadísticas finales del dump."""
        print("📊 Estadísticas del dump completado:")
        print("=" * 50)

        summary = helper.attributes

        print(f"🏠 CUPS: {summary.get('cups', 'N/A')}")

        # Información de contrato
        if summary.get("contract_p1_kW") is not None:
            print(
                f"⚡ Potencia contratada P1: {summary.get('contract_p1_kW', 'N/A')} kW"
            )
        if summary.get("contract_p2_kW") is not None:
            print(
                f"⚡ Potencia contratada P2: {summary.get('contract_p2_kW', 'N/A')} kW"
            )

        # Información de consumo
        if summary.get("yesterday_kWh") is not None:
            print(f"📈 Consumo ayer: {summary.get('yesterday_kWh', 'N/A')} kWh")
        if summary.get("month_kWh") is not None:
            print(f"📈 Consumo mes actual: {summary.get('month_kWh', 'N/A')} kWh")
        if summary.get("last_month_kWh") is not None:
            print(
                f"📈 Consumo mes anterior: {summary.get('last_month_kWh', 'N/A')} kWh"
            )

        # Información de potencia máxima
        if summary.get("max_power_kW") is not None:
            print(
                f"🔋 Potencia máxima registrada: {summary.get('max_power_kW', 'N/A')} kW"
            )

        # Información de costes (si está disponible)
        if summary.get("month_€") is not None:
            print(f"💰 Coste mes actual: {summary.get('month_€', 'N/A')} €")
        if summary.get("last_month_€") is not None:
            print(f"💰 Coste mes anterior: {summary.get('last_month_€', 'N/A')} €")

        print(f"\n💾 Datos almacenados en: {self.storage_dir}")

    async def run_interactive_session(self) -> bool:
        """Ejecutar sesión interactiva completa."""
        print("🏠 Extractor interactivo de datos eléctricos")
        print("=" * 50)
        print(
            "Este script te ayudará a extraer todos los datos de tu suministro eléctrico"
        )
        print()

        try:
            # 1. Obtener credenciales
            if not self.get_credentials():
                return False

            # 2. Probar conexión
            if not await self.test_connection():
                return False

            # 3. Obtener suministros
            if not await self.fetch_supplies():
                return False

            # 4. Mostrar menú y seleccionar suministro
            selected_supply = self.display_supplies_menu()
            if not selected_supply:
                print("👋 Operación cancelada")
                return False

            print(
                f"\n✅ Seleccionado: {selected_supply.cups[-10:]} - {selected_supply.address or 'Sin dirección'}"
            )

            # 5. Configurar fechas
            date_from, date_to = self.get_date_range()

            # 6. Ejecutar dump
            success = await self.dump_selected_supply(
                selected_supply, date_from, date_to
            )

            if success:
                print("\n🎉 ¡Dump completado exitosamente!")
                print("Todos los datos han sido almacenados en la base de datos local.")

            return success

        except KeyboardInterrupt:
            print("\n\n👋 Operación cancelada por el usuario")
            return False
        except Exception as e:
            print(f"\n❌ Error durante la sesión interactiva: {e}")
            return False


async def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Extractor interactivo de datos eléctricos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplo de uso:

  # Modo interactivo
  python -m edata.scripts.dump

  # Con directorio personalizado
  python -m edata.scripts.dump --storage-dir /ruta/datos
        """,
    )

    parser.add_argument(
        "--storage-dir",
        default=".",
        help="Directorio de almacenamiento (por defecto: directorio actual)",
    )

    args = parser.parse_args()

    # Crear dumper
    dumper = DumpSupply(storage_dir=args.storage_dir)

    # Ejecutar modo interactivo
    success = await dumper.run_interactive_session()

    if success:
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
