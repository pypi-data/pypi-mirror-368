"""Billing service for managing energy prices and billing calculations."""

import contextlib
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from jinja2 import Environment

from edata.connectors.redata import REDataConnector
from edata.models.pricing import PricingAggregated, PricingData, PricingRules
from edata.services.database import PVPCPricesModel, get_database_service

_LOGGER = logging.getLogger(__name__)


class BillingService:
    """Service for managing energy pricing and billing data."""

    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize billing service.

        Args:
            storage_dir: Directory for database storage
        """
        self._redata = REDataConnector()
        self._storage_dir = storage_dir
        self._db_service = None

    async def _get_db_service(self):
        """Get database service, initializing if needed."""
        if self._db_service is None:
            self._db_service = await get_database_service(self._storage_dir)
        return self._db_service

    async def update_pvpc_prices(
        self, start_date: datetime, end_date: datetime, is_ceuta_melilla: bool = False
    ) -> Dict[str, Any]:
        """Update PVPC prices from REData API.

        Args:
            start_date: Start date for price data
            end_date: End date for price data
            is_ceuta_melilla: Whether to get prices for Ceuta/Melilla (True) or Peninsula (False)

        Returns:
            Dict with operation results and statistics
        """
        geo_id = 8744 if is_ceuta_melilla else 8741
        region = "Ceuta/Melilla" if is_ceuta_melilla else "Peninsula"

        _LOGGER.info(
            f"Updating PVPC prices for {region} from {start_date.date()} to {end_date.date()}"
        )

        # Determine actual start date based on existing data
        actual_start_date = start_date
        db_service = await self._get_db_service()
        last_price_record = await db_service.get_latest_pvpc_price(geo_id=geo_id)

        if last_price_record:
            # Start from the hour after the last price record
            actual_start_date = max(
                start_date, last_price_record.datetime + timedelta(hours=1)
            )
            _LOGGER.info(
                f"Found existing price data up to {last_price_record.datetime.date()}, fetching from {actual_start_date.date()}"
            )
        else:
            _LOGGER.info(
                f"No existing price data found for {region}, fetching all data"
            )

        # If actual start date is beyond end date, no new data needed
        if actual_start_date >= end_date:
            _LOGGER.info(f"No new price data needed for {region} (up to date)")
            return {
                "success": True,
                "region": region,
                "geo_id": geo_id,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "actual_start": actual_start_date.isoformat(),
                },
                "stats": {
                    "fetched": 0,
                    "saved": 0,
                    "updated": 0,
                    "skipped": "up_to_date",
                },
                "message": "Price data is up to date",
            }

        try:
            # Fetch price data from REData (only missing data)
            prices = await self._redata.get_realtime_prices(
                dt_from=actual_start_date,
                dt_to=end_date,
                is_ceuta_melilla=is_ceuta_melilla,
            )

            # Save to database
            saved_count = 0
            updated_count = 0

            for price in prices:
                price_dict = price.model_dump()
                price_dict["geo_id"] = geo_id

                # Check if price already exists for this specific datetime and geo_id
                existing = await db_service.get_pvpc_prices(
                    start_date=price.datetime, end_date=price.datetime, geo_id=geo_id
                )

                if existing:
                    updated_count += 1
                else:
                    saved_count += 1

                await db_service.save_pvpc_price(price_dict)

            result = {
                "success": True,
                "region": region,
                "geo_id": geo_id,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "actual_start": actual_start_date.isoformat(),
                },
                "stats": {
                    "fetched": len(prices),
                    "saved": saved_count,
                    "updated": updated_count,
                },
            }

            if actual_start_date > start_date:
                result["message"] = (
                    f"Fetched only missing price data from {actual_start_date.date()}"
                )

            _LOGGER.info(
                f"PVPC price update completed: {len(prices)} fetched, "
                f"{saved_count} saved, {updated_count} updated"
            )

            return result

        except Exception as e:
            _LOGGER.error(f"Error updating PVPC prices for {region}: {str(e)}")
            return {
                "success": False,
                "region": region,
                "geo_id": geo_id,
                "error": str(e),
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "actual_start": (
                        actual_start_date.isoformat()
                        if "actual_start_date" in locals()
                        else start_date.isoformat()
                    ),
                },
            }

    def get_custom_prices(
        self, pricing_rules: PricingRules, start_date: datetime, end_date: datetime
    ) -> List[PricingData]:
        """Calculate custom energy prices dynamically based on pricing rules.

        Args:
            pricing_rules: Custom pricing configuration
            start_date: Start date for price data
            end_date: End date for price data

        Returns:
            List of PricingData objects calculated on-the-fly
        """
        if pricing_rules.is_pvpc:
            raise ValueError("Use get_stored_pvpc_prices() for PVPC pricing rules")

        _LOGGER.info(
            f"Calculating custom prices from {start_date.date()} to {end_date.date()}"
        )

        try:
            # Import here to avoid circular imports
            from edata.utils import get_pvpc_tariff

            prices = []

            # Generate hourly prices based on custom rules
            current_dt = start_date
            while current_dt < end_date:
                # Determine tariff period for this hour
                tariff = get_pvpc_tariff(current_dt)

                # Get the appropriate price based on tariff period
                if tariff == "p1" and pricing_rules.p1_kwh_eur is not None:
                    price_eur_kwh = pricing_rules.p1_kwh_eur
                elif tariff == "p2" and pricing_rules.p2_kwh_eur is not None:
                    price_eur_kwh = pricing_rules.p2_kwh_eur
                elif tariff == "p3" and pricing_rules.p3_kwh_eur is not None:
                    price_eur_kwh = pricing_rules.p3_kwh_eur
                else:
                    # Skip if no price defined for this period
                    current_dt += timedelta(hours=1)
                    continue

                # Create PricingData object
                price_data = PricingData(
                    datetime=current_dt, value_eur_kwh=price_eur_kwh, delta_h=1.0
                )

                prices.append(price_data)
                current_dt += timedelta(hours=1)

            _LOGGER.info(f"Generated {len(prices)} custom price points")
            return prices

        except Exception as e:
            _LOGGER.error(f"Error calculating custom prices: {str(e)}")
            raise

    async def get_stored_pvpc_prices(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        geo_id: Optional[int] = None,
    ) -> List[PVPCPricesModel]:
        """Get stored PVPC prices from database.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            geo_id: Optional geographic filter

        Returns:
            List of PVPCPrices objects
        """
        db_service = await self._get_db_service()
        return await db_service.get_pvpc_prices(start_date, end_date, geo_id)

    async def get_prices(
        self,
        pricing_rules: PricingRules,
        start_date: datetime,
        end_date: datetime,
        is_ceuta_melilla: bool = False,
    ) -> Optional[List[PricingData]]:
        """Get prices automatically based on pricing rules configuration.

        Args:
            pricing_rules: Pricing configuration
            start_date: Start date for price data
            end_date: End date for price data
            is_ceuta_melilla: Whether to get PVPC prices for Ceuta/Melilla

        Returns:
            List of PricingData objects or None if missing required data
        """
        if pricing_rules.is_pvpc:
            # Get stored PVPC prices from database
            geo_id = 8744 if is_ceuta_melilla else 8741
            pvpc_prices = await self.get_stored_pvpc_prices(
                start_date, end_date, geo_id
            )

            # Return None if no PVPC prices found
            if not pvpc_prices:
                _LOGGER.warning(
                    f"No PVPC prices found for geo_id {geo_id} from {start_date.date()} to {end_date.date()}"
                )
                return None

            # Convert PVPCPrices to PricingData
            return [
                PricingData(
                    datetime=price.datetime,
                    value_eur_kwh=price.value_eur_kwh,
                    delta_h=price.delta_h,
                )
                for price in pvpc_prices
            ]
        else:
            # Check if custom pricing rules have required data
            if (
                pricing_rules.p1_kwh_eur is None
                and pricing_rules.p2_kwh_eur is None
                and pricing_rules.p3_kwh_eur is None
            ):
                _LOGGER.warning("No custom energy prices defined in pricing rules")
                return None

            # Calculate custom prices dynamically
            try:
                custom_prices = self.get_custom_prices(
                    pricing_rules, start_date, end_date
                )

                # Return None if no prices could be generated
                if not custom_prices:
                    _LOGGER.warning(
                        f"No custom prices could be generated for period {start_date.date()} to {end_date.date()}"
                    )
                    return None

                return custom_prices
            except Exception as e:
                _LOGGER.error(f"Error generating custom prices: {str(e)}")
                return None

    async def get_cost(
        self,
        cups: str,
        pricing_rules: PricingRules,
        start_date: datetime,
        end_date: datetime,
        is_ceuta_melilla: bool = False,
    ) -> PricingAggregated:
        """Get billing cost for a period based on pricing rules.

        First checks the billing table for existing data with the pricing rules hash.
        If not found, calls update_missing_costs to calculate and store the data.
        Then returns the aggregated cost from the billing table.

        Args:
            cups: CUPS identifier for consumption data
            pricing_rules: Pricing configuration
            start_date: Start date for cost calculation
            end_date: End date for cost calculation
            is_ceuta_melilla: Whether to use Ceuta/Melilla PVPC prices

        Returns:
            PricingAggregated object with cost breakdown for the period
        """
        _LOGGER.info(
            f"Getting cost for CUPS {cups} from {start_date.date()} to {end_date.date()}"
        )

        try:
            # Generate pricing configuration hash
            db_service = await self._get_db_service()
            pricing_config_hash = db_service.generate_pricing_config_hash(
                pricing_rules.model_dump()
            )

            # Check if billing data already exists by looking for the latest billing record
            latest_billing = await db_service.get_latest_billing(
                cups=cups, pricing_config_hash=pricing_config_hash
            )

            # Determine if we need to calculate missing costs
            needs_calculation = False
            actual_start_date = start_date

            if not latest_billing:
                # No billing data exists for this configuration
                needs_calculation = True
                _LOGGER.info(
                    f"No billing data found for hash {pricing_config_hash[:8]}..., calculating all costs"
                )
            elif latest_billing.datetime < end_date - timedelta(hours=1):
                # Billing data exists but is incomplete for the requested period
                needs_calculation = True
                actual_start_date = max(
                    start_date, latest_billing.datetime + timedelta(hours=1)
                )
                _LOGGER.info(
                    f"Found billing data up to {latest_billing.datetime.date()}, calculating from {actual_start_date.date()}"
                )

            # Calculate missing costs if needed
            if needs_calculation:
                update_result = await self.update_missing_costs(
                    cups,
                    pricing_rules,
                    actual_start_date,
                    end_date,
                    is_ceuta_melilla,
                    force_recalculate=False,
                )

                if not update_result["success"]:
                    _LOGGER.error(
                        f"Failed to update costs: {update_result.get('error', 'Unknown error')}"
                    )
                    return PricingAggregated(
                        datetime=start_date,
                        value_eur=0.0,
                        energy_term=0.0,
                        power_term=0.0,
                        others_term=0.0,
                        surplus_term=0.0,
                        delta_h=(end_date - start_date).total_seconds() / 3600,
                    )

            # Get the complete billing data for the requested period
            existing_billing = await db_service.get_billing(
                cups=cups,
                start_date=start_date,
                end_date=end_date,
                pricing_config_hash=pricing_config_hash,
            )

            # Aggregate the billing data
            total_value_eur = 0.0
            total_energy_term = 0.0
            total_power_term = 0.0
            total_others_term = 0.0
            total_surplus_term = 0.0
            total_hours = len(existing_billing)

            for billing in existing_billing:
                total_value_eur += billing.total_eur or 0.0
                total_energy_term += billing.energy_term or 0.0
                total_power_term += billing.power_term or 0.0
                total_others_term += billing.others_term or 0.0
                total_surplus_term += billing.surplus_term or 0.0

            result = PricingAggregated(
                datetime=start_date,
                value_eur=round(total_value_eur, 6),
                energy_term=round(total_energy_term, 6),
                power_term=round(total_power_term, 6),
                others_term=round(total_others_term, 6),
                surplus_term=round(total_surplus_term, 6),
                delta_h=total_hours,
            )

            _LOGGER.info(
                f"Cost calculation completed for CUPS {cups}: "
                f"€{total_value_eur:.2f} for {total_hours} hours"
            )

            return result

        except Exception as e:
            _LOGGER.error(f"Error getting cost for CUPS {cups}: {str(e)}")
            raise

    async def update_missing_costs(
        self,
        cups: str,
        pricing_rules: PricingRules,
        start_date: datetime,
        end_date: datetime,
        is_ceuta_melilla: bool = False,
        force_recalculate: bool = False,
    ) -> Dict[str, Any]:
        """Calculate and store billing costs in the database.

        Args:
            cups: CUPS identifier for consumption data
            pricing_rules: Pricing configuration
            start_date: Start date for cost calculation
            end_date: End date for cost calculation
            is_ceuta_melilla: Whether to use Ceuta/Melilla PVPC prices
            force_recalculate: If True, recalculate even if billing data exists

        Returns:
            Dict with operation results and statistics
        """
        _LOGGER.info(
            f"Updating costs for CUPS {cups} from {start_date.date()} to {end_date.date()}"
        )

        try:
            # Generate pricing configuration hash
            db_service = await self._get_db_service()
            pricing_config_hash = db_service.generate_pricing_config_hash(
                pricing_rules.model_dump()
            )

            # Get existing billing data if not forcing recalculation
            existing_billing = []
            if not force_recalculate:
                existing_billing = await db_service.get_billing(
                    cups=cups,
                    start_date=start_date,
                    end_date=end_date,
                    pricing_config_hash=pricing_config_hash,
                )

            # Create set of existing datetime for quick lookup
            existing_hours = {billing.datetime for billing in existing_billing}

            # Get consumption data
            consumptions = await db_service.get_consumptions(cups, start_date, end_date)
            if not consumptions:
                _LOGGER.warning(
                    f"No consumption data found for CUPS {cups} in the specified period"
                )
                return {
                    "success": False,
                    "error": "No consumption data found",
                    "cups": cups,
                    "period": {
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat(),
                    },
                }

            # Get contract data for power terms
            contracts = await db_service.get_contracts(cups)
            if not contracts:
                _LOGGER.warning(
                    f"No contract data found for CUPS {cups}, using defaults"
                )
                # Use default power values if no contracts found
                default_contract = {
                    "power_p1": 3.45,  # Default residential power
                    "power_p2": 3.45,
                    "date_start": start_date,
                    "date_end": end_date,
                }
                contracts = [type("MockContract", (), default_contract)()]

            # Get pricing data
            prices = await self.get_prices(
                pricing_rules, start_date, end_date, is_ceuta_melilla
            )
            if prices is None:
                _LOGGER.warning(
                    f"No pricing data available for CUPS {cups} in the specified period"
                )
                return {
                    "success": False,
                    "error": "No pricing data available",
                    "cups": cups,
                    "period": {
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat(),
                    },
                }

            # Create price lookup by datetime
            price_lookup = {price.datetime: price.value_eur_kwh for price in prices}

            # Build data structure similar to billing processor
            data = {}
            for consumption in consumptions:
                data[consumption.datetime] = {
                    "datetime": consumption.datetime,
                    "kwh": consumption.value_kwh,
                    "surplus_kwh": (
                        consumption.surplus_kwh
                        if hasattr(consumption, "surplus_kwh")
                        and consumption.surplus_kwh is not None
                        else 0
                    ),
                }

            # Add contract power data
            for contract in contracts:
                start_dt = getattr(contract, "date_start", start_date)
                end_dt = getattr(contract, "date_end", end_date)
                current = start_dt

                while current <= end_dt and current <= end_date:
                    if current in data:
                        data[current]["p1_kw"] = getattr(contract, "power_p1", 3.45)
                        data[current]["p2_kw"] = getattr(contract, "power_p2", 3.45)
                    current += timedelta(hours=1)

            # Add pricing data
            for dt, kwh_eur in price_lookup.items():
                if dt in data:
                    data[dt]["kwh_eur"] = kwh_eur

            # Prepare Jinja2 expressions for cost calculation
            env = Environment()
            energy_expr = env.compile_expression(
                f"({pricing_rules.energy_formula})|float"
            )
            power_expr = env.compile_expression(
                f"({pricing_rules.power_formula})|float"
            )
            others_expr = env.compile_expression(
                f"({pricing_rules.others_formula})|float"
            )
            surplus_expr = env.compile_expression(
                f"({pricing_rules.surplus_formula})|float"
            )
            main_expr = env.compile_expression(f"({pricing_rules.main_formula})|float")

            # Calculate and save costs for each hour
            saved_count = 0
            updated_count = 0
            skipped_count = 0

            for dt in sorted(data.keys()):
                # Skip if already exists and not forcing recalculation
                if not force_recalculate and dt in existing_hours:
                    skipped_count += 1
                    continue

                hour_data = data[dt]

                # Add pricing rules to hour data
                hour_data.update(pricing_rules.model_dump())

                # Import here to avoid circular imports
                from edata.utils import get_pvpc_tariff

                tariff = get_pvpc_tariff(hour_data["datetime"])

                # Set energy price if not already set
                if "kwh_eur" not in hour_data:
                    if tariff == "p1" and pricing_rules.p1_kwh_eur is not None:
                        hour_data["kwh_eur"] = pricing_rules.p1_kwh_eur
                    elif tariff == "p2" and pricing_rules.p2_kwh_eur is not None:
                        hour_data["kwh_eur"] = pricing_rules.p2_kwh_eur
                    elif tariff == "p3" and pricing_rules.p3_kwh_eur is not None:
                        hour_data["kwh_eur"] = pricing_rules.p3_kwh_eur
                    else:
                        continue  # Skip if no price available

                # Set surplus price based on tariff
                if tariff == "p1":
                    hour_data["surplus_kwh_eur"] = pricing_rules.surplus_p1_kwh_eur or 0
                elif tariff == "p2":
                    hour_data["surplus_kwh_eur"] = pricing_rules.surplus_p2_kwh_eur or 0
                elif tariff == "p3":
                    hour_data["surplus_kwh_eur"] = pricing_rules.surplus_p3_kwh_eur or 0

                # Calculate individual cost terms
                energy_term = 0.0
                power_term = 0.0
                others_term = 0.0
                surplus_term = 0.0

                with contextlib.suppress(Exception):
                    result = energy_expr(**hour_data)
                    energy_term = round(float(result), 6) if result is not None else 0.0

                    result = power_expr(**hour_data)
                    power_term = round(float(result), 6) if result is not None else 0.0

                    result = others_expr(**hour_data)
                    others_term = round(float(result), 6) if result is not None else 0.0

                    result = surplus_expr(**hour_data)
                    surplus_term = (
                        round(float(result), 6) if result is not None else 0.0
                    )

                # Calculate total using main formula
                cost_data = {
                    "energy_term": energy_term,
                    "power_term": power_term,
                    "others_term": others_term,
                    "surplus_term": surplus_term,
                    **pricing_rules.model_dump(),
                }

                total_eur = 0.0
                with contextlib.suppress(Exception):
                    result = main_expr(**cost_data)
                    total_eur = round(float(result), 6) if result is not None else 0.0

                # Prepare billing data (only calculated terms, not raw data)
                billing_data = {
                    "cups": cups,
                    "datetime": dt,
                    "energy_term": energy_term,
                    "power_term": power_term,
                    "others_term": others_term,
                    "surplus_term": surplus_term,
                    "total_eur": total_eur,
                    "tariff": tariff,
                    "pricing_config_hash": pricing_config_hash,
                }

                # Save to database
                await db_service.save_billing(billing_data)

                if dt in existing_hours:
                    updated_count += 1
                else:
                    saved_count += 1

            result = {
                "success": True,
                "cups": cups,
                "pricing_config_hash": pricing_config_hash,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "stats": {
                    "total_consumptions": len(consumptions),
                    "saved": saved_count,
                    "updated": updated_count,
                    "skipped": skipped_count,
                    "processed": saved_count + updated_count,
                },
            }

            _LOGGER.info(
                f"Billing cost update completed for CUPS {cups}: "
                f"{saved_count} saved, {updated_count} updated, {skipped_count} skipped"
            )

            return result

        except Exception as e:
            _LOGGER.error(f"Error updating costs for CUPS {cups}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "cups": cups,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }

    async def get_daily_costs(
        self,
        cups: str,
        pricing_rules: PricingRules,
        start_date: datetime,
        end_date: datetime,
        is_ceuta_melilla: bool = False,
    ) -> List[PricingAggregated]:
        """Get daily aggregated billing costs for a period.

        Args:
            cups: CUPS identifier for consumption data
            pricing_rules: Pricing configuration
            start_date: Start date for cost calculation
            end_date: End date for cost calculation
            is_ceuta_melilla: Whether to use Ceuta/Melilla PVPC prices

        Returns:
            List of PricingAggregated objects, one per day
        """
        _LOGGER.info(
            f"Getting daily costs for CUPS {cups} from {start_date.date()} to {end_date.date()}"
        )

        try:
            # Generate pricing configuration hash
            db_service = await self._get_db_service()
            pricing_config_hash = db_service.generate_pricing_config_hash(
                pricing_rules.model_dump()
            )

            # Get billing data for the period
            billing_records = await db_service.get_billing(
                cups=cups,
                start_date=start_date,
                end_date=end_date,
                pricing_config_hash=pricing_config_hash,
            )

            # If no billing data exists, calculate and store it first
            if not billing_records:
                _LOGGER.info(f"No billing data found, calculating costs first")
                update_result = await self.update_missing_costs(
                    cups,
                    pricing_rules,
                    start_date,
                    end_date,
                    is_ceuta_melilla,
                    force_recalculate=False,
                )

                if not update_result["success"]:
                    _LOGGER.error(
                        f"Failed to update costs: {update_result.get('error', 'Unknown error')}"
                    )
                    return []

                # Get the newly calculated billing data
                billing_records = await db_service.get_billing(
                    cups=cups,
                    start_date=start_date,
                    end_date=end_date,
                    pricing_config_hash=pricing_config_hash,
                )

            # Group by day and aggregate
            daily_aggregates = {}

            for billing in billing_records:
                # Get the date (without time) as key
                date_key = billing.datetime.date()

                if date_key not in daily_aggregates:
                    daily_aggregates[date_key] = {
                        "datetime": datetime.combine(date_key, datetime.min.time()),
                        "total_eur": 0.0,
                        "energy_term": 0.0,
                        "power_term": 0.0,
                        "others_term": 0.0,
                        "surplus_term": 0.0,
                        "hours": 0,
                    }

                # Add this hour's costs
                daily_aggregates[date_key]["total_eur"] += billing.total_eur or 0.0
                daily_aggregates[date_key]["energy_term"] += billing.energy_term or 0.0
                daily_aggregates[date_key]["power_term"] += billing.power_term or 0.0
                daily_aggregates[date_key]["others_term"] += billing.others_term or 0.0
                daily_aggregates[date_key]["surplus_term"] += (
                    billing.surplus_term or 0.0
                )
                daily_aggregates[date_key]["hours"] += 1

            # Convert to PricingAggregated objects
            result = []
            for date_key in sorted(daily_aggregates.keys()):
                agg = daily_aggregates[date_key]
                pricing_agg = PricingAggregated(
                    datetime=agg["datetime"],
                    value_eur=round(agg["total_eur"], 6),
                    energy_term=round(agg["energy_term"], 6),
                    power_term=round(agg["power_term"], 6),
                    others_term=round(agg["others_term"], 6),
                    surplus_term=round(agg["surplus_term"], 6),
                    delta_h=agg["hours"],
                )
                result.append(pricing_agg)

            _LOGGER.info(f"Generated {len(result)} daily cost aggregates")
            return result

        except Exception as e:
            _LOGGER.error(f"Error getting daily costs for CUPS {cups}: {str(e)}")
            raise

    async def get_monthly_costs(
        self,
        cups: str,
        pricing_rules: PricingRules,
        start_date: datetime,
        end_date: datetime,
        is_ceuta_melilla: bool = False,
    ) -> List[PricingAggregated]:
        """Get monthly aggregated billing costs for a period.

        Args:
            cups: CUPS identifier for consumption data
            pricing_rules: Pricing configuration
            start_date: Start date for cost calculation
            end_date: End date for cost calculation
            is_ceuta_melilla: Whether to use Ceuta/Melilla PVPC prices

        Returns:
            List of PricingAggregated objects, one per month
        """
        _LOGGER.info(
            f"Getting monthly costs for CUPS {cups} from {start_date.date()} to {end_date.date()}"
        )

        try:
            # Generate pricing configuration hash
            db_service = await self._get_db_service()
            pricing_config_hash = db_service.generate_pricing_config_hash(
                pricing_rules.model_dump()
            )

            # Get billing data for the period
            billing_records = await db_service.get_billing(
                cups=cups,
                start_date=start_date,
                end_date=end_date,
                pricing_config_hash=pricing_config_hash,
            )

            # If no billing data exists, calculate and store it first
            if not billing_records:
                _LOGGER.info(f"No billing data found, calculating costs first")
                update_result = await self.update_missing_costs(
                    cups,
                    pricing_rules,
                    start_date,
                    end_date,
                    is_ceuta_melilla,
                    force_recalculate=False,
                )

                if not update_result["success"]:
                    _LOGGER.error(
                        f"Failed to update costs: {update_result.get('error', 'Unknown error')}"
                    )
                    return []

                # Get the newly calculated billing data
                billing_records = await db_service.get_billing(
                    cups=cups,
                    start_date=start_date,
                    end_date=end_date,
                    pricing_config_hash=pricing_config_hash,
                )

            # Group by month and aggregate
            monthly_aggregates = {}

            for billing in billing_records:
                # Get year-month as key
                month_key = (billing.datetime.year, billing.datetime.month)

                if month_key not in monthly_aggregates:
                    # Create datetime for first day of month
                    month_start = datetime(month_key[0], month_key[1], 1)
                    monthly_aggregates[month_key] = {
                        "datetime": month_start,
                        "total_eur": 0.0,
                        "energy_term": 0.0,
                        "power_term": 0.0,
                        "others_term": 0.0,
                        "surplus_term": 0.0,
                        "hours": 0,
                    }

                # Add this hour's costs
                monthly_aggregates[month_key]["total_eur"] += billing.total_eur or 0.0
                monthly_aggregates[month_key]["energy_term"] += (
                    billing.energy_term or 0.0
                )
                monthly_aggregates[month_key]["power_term"] += billing.power_term or 0.0
                monthly_aggregates[month_key]["others_term"] += (
                    billing.others_term or 0.0
                )
                monthly_aggregates[month_key]["surplus_term"] += (
                    billing.surplus_term or 0.0
                )
                monthly_aggregates[month_key]["hours"] += 1

            # Convert to PricingAggregated objects
            result = []
            for month_key in sorted(monthly_aggregates.keys()):
                agg = monthly_aggregates[month_key]
                pricing_agg = PricingAggregated(
                    datetime=agg["datetime"],
                    value_eur=round(agg["total_eur"], 6),
                    energy_term=round(agg["energy_term"], 6),
                    power_term=round(agg["power_term"], 6),
                    others_term=round(agg["others_term"], 6),
                    surplus_term=round(agg["surplus_term"], 6),
                    delta_h=agg["hours"],
                )
                result.append(pricing_agg)

            _LOGGER.info(f"Generated {len(result)} monthly cost aggregates")
            return result

        except Exception as e:
            _LOGGER.error(f"Error getting monthly costs for CUPS {cups}: {str(e)}")
            raise

    async def get_billing_summary(
        self,
        cups: str,
        pricing_rules: PricingRules,
        target_date: Optional[datetime] = None,
        is_ceuta_melilla: bool = False,
    ) -> Dict[str, Any]:
        """Get billing summary data compatible with EdataHelper attributes.

        Args:
            cups: CUPS identifier
            pricing_rules: Pricing configuration
            target_date: Reference date for calculations (defaults to today)
            is_ceuta_melilla: Whether to use Ceuta/Melilla PVPC prices

        Returns:
            Dict with summary attributes matching EdataHelper format
        """

        from dateutil.relativedelta import relativedelta

        if target_date is None:
            target_date = datetime.now()

        # Calculate date ranges
        month_starts = target_date.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        last_month_starts = month_starts - relativedelta(months=1)

        # Initialize summary attributes
        summary: Dict[str, Any] = {"month_€": None, "last_month_€": None}

        try:
            # Get current month cost
            current_month_costs = await self.get_monthly_costs(
                cups=cups,
                pricing_rules=pricing_rules,
                start_date=month_starts,
                end_date=month_starts + relativedelta(months=1),
                is_ceuta_melilla=is_ceuta_melilla,
            )

            if current_month_costs:
                current_month_data = next(
                    (
                        c
                        for c in current_month_costs
                        if c.datetime.year == month_starts.year
                        and c.datetime.month == month_starts.month
                    ),
                    None,
                )
                if current_month_data:
                    summary["month_€"] = current_month_data.value_eur

            # Get last month cost
            last_month_costs = await self.get_monthly_costs(
                cups=cups,
                pricing_rules=pricing_rules,
                start_date=last_month_starts,
                end_date=month_starts,
                is_ceuta_melilla=is_ceuta_melilla,
            )

            if last_month_costs:
                last_month_data = next(
                    (
                        c
                        for c in last_month_costs
                        if c.datetime.year == last_month_starts.year
                        and c.datetime.month == last_month_starts.month
                    ),
                    None,
                )
                if last_month_data:
                    summary["last_month_€"] = last_month_data.value_eur

        except Exception as e:
            _LOGGER.warning(
                f"Error calculating billing summary for CUPS {cups}: {str(e)}"
            )

        # Round numeric values to 2 decimal places
        for key, value in summary.items():
            if isinstance(value, float):
                summary[key] = round(value, 2)

        return summary
