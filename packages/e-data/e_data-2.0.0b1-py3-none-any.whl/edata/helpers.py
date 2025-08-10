"""A module for edata helpers."""

import logging
from datetime import datetime
from typing import Any, Dict

from edata.connectors.datadis import DatadisConnector
from edata.const import ATTRIBUTES
from edata.models.pricing import PricingRules
from edata.services.billing import BillingService
from edata.services.consumption import ConsumptionService
from edata.services.contract import ContractService
from edata.services.maximeter import MaximeterService
from edata.services.supply import SupplyService

_LOGGER = logging.getLogger(__name__)


def acups(cups):
    """Print an abbreviated and anonymized CUPS."""
    return cups[-5:]


class EdataHelper:
    """Main EdataHelper class using service-based architecture."""

    def __init__(
        self,
        datadis_username: str,
        datadis_password: str,
        cups: str,
        datadis_authorized_nif: str | None = None,
        pricing_rules: PricingRules | None = None,
        storage_dir_path: str | None = None,
        enable_smart_fetch: bool = True,
    ) -> None:
        """Initialize EdataHelper with service-based architecture.

        Args:
            datadis_username: Datadis username
            datadis_password: Datadis password
            cups: CUPS identifier
            datadis_authorized_nif: Optional authorized NIF
            pricing_rules: Pricing configuration
            storage_dir_path: Directory for database and cache storage
            enable_smart_fetch: Enable smart fetching in datadis connector
        """
        self._cups = cups
        self._scups = acups(cups)
        self._authorized_nif = datadis_authorized_nif
        self._storage_dir = storage_dir_path
        self.pricing_rules = pricing_rules

        # Initialize summary attributes
        self.summary: Dict[str, Any] = {}
        for attr in ATTRIBUTES:
            self.summary[attr] = None

        # For backward compatibility, alias 'attributes' to 'summary'
        self.attributes = self.summary

        # Determine if using PVPC pricing
        self.enable_billing = pricing_rules is not None
        if self.enable_billing:
            self.is_pvpc = not all(
                getattr(pricing_rules, x, None) is not None
                for x in ("p1_kwh_eur", "p2_kwh_eur", "p3_kwh_eur")
            )
        else:
            self.is_pvpc = False

        # Create shared Datadis connector
        self._datadis_connector = DatadisConnector(
            username=datadis_username,
            password=datadis_password,
            enable_smart_fetch=enable_smart_fetch,
            storage_path=storage_dir_path,
        )

        # Initialize services with dependency injection
        self._supply_service = SupplyService(
            datadis_connector=self._datadis_connector,
            storage_dir=storage_dir_path,
        )

        self._contract_service = ContractService(
            datadis_connector=self._datadis_connector,
            storage_dir=storage_dir_path,
        )

        self._consumption_service = ConsumptionService(
            datadis_connector=self._datadis_connector,
            storage_dir=storage_dir_path,
        )

        self._maximeter_service = MaximeterService(
            datadis_connector=self._datadis_connector,
            storage_dir=storage_dir_path,
        )

        if self.enable_billing:
            self._billing_service = BillingService(storage_dir=storage_dir_path)

        _LOGGER.info(f"EdataHelper initialized for CUPS {self._scups}")

    @property
    def datadis_connector(self) -> DatadisConnector:
        """Get the shared Datadis connector instance."""
        return self._datadis_connector

    async def update(
        self,
        date_from: datetime = datetime(1970, 1, 1),
        date_to: datetime = datetime.today(),
    ):
        """Update all data and calculate summary attributes.

        Args:
            date_from: Start date for data updates
            date_to: End date for data updates
            incremental_update: Whether to update incrementally (deprecated, ignored)
        """
        _LOGGER.info(
            f"{self._scups}: Starting update from {date_from.date()} to {date_to.date()}"
        )

        try:
            # Step 1: Update supplies
            _LOGGER.info(f"{self._scups}: Updating supplies")
            supply_result = await self._supply_service.update_supplies(
                authorized_nif=self._authorized_nif
            )

            if not supply_result["success"]:
                _LOGGER.error(
                    f"{self._scups}: Failed to update supplies: {supply_result.get('error', 'Unknown error')}"
                )
                return False

            # Validate that our CUPS exists
            if not await self._supply_service.validate_cups(self._cups):
                _LOGGER.error(f"{self._scups}: CUPS not found in account")
                return False

            _LOGGER.info(f"{self._scups}: CUPS validated successfully")

            # Get supply information
            supply = await self._supply_service.get_supply_by_cups(self._cups)
            if not supply:
                _LOGGER.error(f"{self._scups}: Could not retrieve supply details")
                return False

            distributor_code = supply.distributor_code
            point_type = supply.point_type

            _LOGGER.info(
                f"{self._scups}: Supply dates from {supply.date_start.date()} to {supply.date_end.date()}"
            )

            # Adjust date range to supply validity period
            effective_start = max(date_from, supply.date_start)
            effective_end = min(date_to, supply.date_end)

            # Step 2: Update contracts
            _LOGGER.info(f"{self._scups}: Updating contracts")
            contract_result = await self._contract_service.update_contracts(
                cups=self._cups,
                distributor_code=distributor_code,
                authorized_nif=self._authorized_nif,
            )

            if not contract_result["success"]:
                _LOGGER.warning(
                    f"{self._scups}: Contract update failed: {contract_result.get('error', 'Unknown error')}"
                )

            # Step 3: Update consumptions in monthly chunks
            _LOGGER.info(f"{self._scups}: Updating consumptions")
            consumption_result = (
                await self._consumption_service.update_consumption_range_by_months(
                    cups=self._cups,
                    distributor_code=distributor_code,
                    start_date=effective_start,
                    end_date=effective_end,
                    measurement_type="0",
                    point_type=point_type,
                    authorized_nif=self._authorized_nif,
                )
            )

            if not consumption_result["success"]:
                _LOGGER.warning(f"{self._scups}: Consumption update failed")

            # Step 4: Update maximeter data
            _LOGGER.info(f"{self._scups}: Updating maximeter")
            maximeter_result = (
                await self._maximeter_service.update_maxpower_range_by_months(
                    cups=self._cups,
                    distributor_code=distributor_code,
                    start_date=effective_start,
                    end_date=effective_end,
                    authorized_nif=self._authorized_nif,
                )
            )

            if not maximeter_result["success"]:
                _LOGGER.warning(f"{self._scups}: Maximeter update failed")

            # Step 5: Update PVPC prices if needed
            if self.enable_billing and self.is_pvpc:
                _LOGGER.info(f"{self._scups}: Updating PVPC prices")
                try:
                    pvpc_result = await self._billing_service.update_pvpc_prices(
                        start_date=effective_start,
                        end_date=effective_end,
                        is_ceuta_melilla=False,  # Default to Peninsula
                    )

                    if not pvpc_result["success"]:
                        _LOGGER.warning(
                            f"{self._scups}: PVPC price update failed: {pvpc_result.get('error', 'Unknown error')}"
                        )

                except Exception as e:
                    _LOGGER.warning(
                        f"{self._scups}: PVPC price update failed with exception: {str(e)}"
                    )

            # Step 6: Update billing costs if pricing rules are defined
            if self.enable_billing and self.pricing_rules:
                _LOGGER.info(f"{self._scups}: Updating billing costs")
                try:
                    billing_result = await self._billing_service.update_missing_costs(
                        cups=self._cups,
                        pricing_rules=self.pricing_rules,
                        start_date=effective_start,
                        end_date=effective_end,
                        is_ceuta_melilla=False,
                        force_recalculate=False,
                    )

                    if not billing_result["success"]:
                        _LOGGER.warning(
                            f"{self._scups}: Billing cost update failed: {billing_result.get('error', 'Unknown error')}"
                        )

                except Exception as e:
                    _LOGGER.warning(
                        f"{self._scups}: Billing cost update failed with exception: {str(e)}"
                    )

            # Step 7: Calculate summary attributes
            _LOGGER.info(f"{self._scups}: Calculating summary attributes")
            await self._calculate_summary_attributes()

            _LOGGER.info(f"{self._scups}: Update completed successfully")
            return True

        except Exception as e:
            _LOGGER.error(f"{self._scups}: Update failed with exception: {str(e)}")
            return False

    async def _calculate_summary_attributes(self):
        """Calculate summary attributes from all services."""

        # Reset all attributes
        for attr in ATTRIBUTES:
            self.summary[attr] = None

        try:
            # Get supply summary
            supply_summary = await self._supply_service.get_supply_summary(self._cups)
            self.summary.update(supply_summary)

            # Get contract summary
            contract_summary = await self._contract_service.get_contract_summary(
                self._cups
            )
            self.summary.update(contract_summary)

            # Get consumption summary
            consumption_summary = (
                await self._consumption_service.get_consumption_summary(self._cups)
            )
            self.summary.update(consumption_summary)

            # Get maximeter summary
            maximeter_summary = await self._maximeter_service.get_maximeter_summary(
                self._cups
            )
            self.summary.update(maximeter_summary)

            # Get billing summary if enabled
            if self.enable_billing and self.pricing_rules and self._billing_service:
                billing_summary = await self._billing_service.get_billing_summary(
                    cups=self._cups,
                    pricing_rules=self.pricing_rules,
                    is_ceuta_melilla=False,
                )
                self.summary.update(billing_summary)

            # Round numeric values to 2 decimal places for consistency
            for key, value in self.summary.items():
                if isinstance(value, float):
                    self.summary[key] = round(value, 2)

            _LOGGER.debug(f"{self._scups}: Summary attributes calculated successfully")

        except Exception as e:
            _LOGGER.error(
                f"{self._scups}: Error calculating summary attributes: {str(e)}"
            )
