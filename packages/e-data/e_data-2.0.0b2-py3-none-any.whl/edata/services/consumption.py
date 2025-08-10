"""Consumption service for fetching and updating consumption data."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from edata.connectors.datadis import DatadisConnector
from edata.models.consumption import Consumption, ConsumptionAggregated
from edata.services.database import ConsumptionModel as DbConsumption
from edata.services.database import DatabaseService, get_database_service
from edata.utils import get_pvpc_tariff

_LOGGER = logging.getLogger(__name__)


class ConsumptionService:
    """Service for managing consumption data fetching and storage."""

    def __init__(
        self,
        datadis_connector: DatadisConnector,
        storage_dir: Optional[str] = None,
    ):
        """Initialize consumption service.

        Args:
            datadis_connector: Configured Datadis connector instance
            storage_dir: Directory for database and cache storage
        """
        self._datadis = datadis_connector
        self._storage_dir = storage_dir
        self._db_service = None

    async def _get_db_service(self) -> DatabaseService:
        """Get database service, initializing if needed."""
        if self._db_service is None:
            self._db_service = await get_database_service(self._storage_dir)
        return self._db_service

    async def update_consumptions(
        self,
        cups: str,
        distributor_code: str,
        start_date: datetime,
        end_date: datetime,
        measurement_type: str = "0",
        point_type: int = 5,
        authorized_nif: Optional[str] = None,
        force_full_update: bool = False,
    ) -> Dict[str, Any]:
        """Update consumption data for a CUPS in the specified date range.

        Args:
            cups: CUPS identifier
            distributor_code: Distributor company code
            start_date: Start date for consumption data
            end_date: End date for consumption data
            measurement_type: Type of measurement (default "0" for hourly)
            point_type: Type of supply point (default 5)
            authorized_nif: Authorized NIF if accessing on behalf of someone
            force_full_update: If True, fetch all data ignoring existing records

        Returns:
            Dict with operation results and statistics
        """
        _LOGGER.info(
            f"Updating consumptions for CUPS {cups[-5:]:>5} from {start_date.date()} to {end_date.date()}"
        )

        # Determine actual start date based on existing data
        actual_start_date = start_date
        if not force_full_update:
            last_consumption_date = await self.get_last_consumption_date(cups)
            if last_consumption_date:
                # Start from the day after the last consumption
                actual_start_date = max(
                    start_date, last_consumption_date + timedelta(hours=1)
                )
                _LOGGER.info(
                    f"Found existing data up to {last_consumption_date.date()}, fetching from {actual_start_date.date()}"
                )
            else:
                _LOGGER.info(
                    f"No existing consumption data found for CUPS {cups[-5:]:>5}, fetching all data"
                )

        # If actual start date is beyond end date, no new data needed
        if actual_start_date >= end_date:
            _LOGGER.info(
                f"No new consumption data needed for CUPS {cups[-5:]:>5} (up to date)"
            )
            return {
                "success": True,
                "cups": cups,
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
                "message": "Data is up to date",
            }

        try:
            # Fetch consumption data from datadis (only missing data)
            consumptions = await self._datadis.get_consumption_data(
                cups=cups,
                distributor_code=distributor_code,
                start_date=actual_start_date,
                end_date=end_date,
                measurement_type=measurement_type,
                point_type=point_type,
                authorized_nif=authorized_nif,
            )

            # Save to database
            saved_count = 0
            updated_count = 0

            for consumption in consumptions:
                # Convert Pydantic model to dict and add CUPS
                consumption_dict = consumption.model_dump()
                consumption_dict["cups"] = cups

                # Check if consumption already exists
                db_service = await self._get_db_service()
                existing = await db_service.get_consumptions(
                    cups=cups,
                    start_date=consumption.datetime,
                    end_date=consumption.datetime,
                )

                if existing:
                    updated_count += 1
                else:
                    saved_count += 1

                await db_service.save_consumption(consumption_dict)

            result = {
                "success": True,
                "cups": cups,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "actual_start": actual_start_date.isoformat(),
                },
                "stats": {
                    "fetched": len(consumptions),
                    "saved": saved_count,
                    "updated": updated_count,
                },
            }

            if actual_start_date > start_date:
                result["message"] = (
                    f"Fetched only missing data from {actual_start_date.date()}"
                )

            _LOGGER.info(
                f"Consumption update completed: {len(consumptions)} fetched, "
                f"{saved_count} saved, {updated_count} updated"
            )

            return result

        except Exception as e:
            _LOGGER.error(f"Error updating consumptions for CUPS {cups}: {str(e)}")
            return {
                "success": False,
                "cups": cups,
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

    async def update_consumption_range_by_months(
        self,
        cups: str,
        distributor_code: str,
        start_date: datetime,
        end_date: datetime,
        measurement_type: str = "0",
        point_type: int = 5,
        authorized_nif: Optional[str] = None,
        force_full_update: bool = False,
    ) -> Dict[str, Any]:
        """Update consumption data month by month to respect datadis limits.

        Args:
            cups: CUPS identifier
            distributor_code: Distributor company code
            start_date: Start date for consumption data
            end_date: End date for consumption data
            measurement_type: Type of measurement (default "0" for hourly)
            point_type: Type of supply point (default 5)
            authorized_nif: Authorized NIF if accessing on behalf of someone
            force_full_update: If True, fetch all data ignoring existing records

        Returns:
            Dict with operation results and statistics for all months
        """
        _LOGGER.info(
            f"Updating consumption range for CUPS {cups[-5:]:>5} "
            f"from {start_date.date()} to {end_date.date()} by months"
        )

        results = []
        current_date = start_date

        while current_date < end_date:
            # Calculate month end
            if current_date.month == 12:
                month_end = current_date.replace(
                    year=current_date.year + 1, month=1, day=1
                )
            else:
                month_end = current_date.replace(month=current_date.month + 1, day=1)

            # Don't go past the requested end date
            actual_end = min(month_end, end_date)

            # Update consumptions for this month
            consumption_result = await self.update_consumptions(
                cups=cups,
                distributor_code=distributor_code,
                start_date=current_date,
                end_date=actual_end,
                measurement_type=measurement_type,
                point_type=point_type,
                authorized_nif=authorized_nif,
                force_full_update=force_full_update,
            )

            result_entry = {
                "month": current_date.strftime("%Y-%m"),
                "consumption": consumption_result,
            }

            results.append(result_entry)
            current_date = month_end

        # Calculate totals
        total_consumptions_fetched = sum(
            r["consumption"]["stats"]["fetched"]
            for r in results
            if r["consumption"]["success"]
        )
        total_consumptions_saved = sum(
            r["consumption"]["stats"]["saved"]
            for r in results
            if r["consumption"]["success"]
        )
        total_consumptions_updated = sum(
            r["consumption"]["stats"]["updated"]
            for r in results
            if r["consumption"]["success"]
        )

        summary = {
            "success": all(r["consumption"]["success"] for r in results),
            "cups": cups,
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "months_processed": len(results),
            "total_stats": {
                "consumptions_fetched": total_consumptions_fetched,
                "consumptions_saved": total_consumptions_saved,
                "consumptions_updated": total_consumptions_updated,
            },
            "monthly_results": results,
        }

        _LOGGER.info(
            f"Consumption range update completed: {len(results)} months processed, "
            f"{total_consumptions_fetched} consumptions fetched"
        )

        return summary

    async def get_stored_consumptions(
        self,
        cups: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[DbConsumption]:
        """Get stored consumptions from database.

        Args:
            cups: CUPS identifier
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of database Consumption objects
        """
        db_service = await self._get_db_service()
        return await db_service.get_consumptions(cups, start_date, end_date)

    async def get_last_consumption_date(self, cups: str) -> Optional[datetime]:
        """Get the date of the last consumption record in the database.

        Args:
            cups: CUPS identifier

        Returns:
            Datetime of last consumption or None if no data exists
        """
        db_service = await self._get_db_service()
        latest_consumption = await db_service.get_latest_consumption(cups)

        if latest_consumption:
            return latest_consumption.datetime
        return None

    async def get_daily_consumptions(
        self, cups: str, start_date: datetime, end_date: datetime
    ) -> List[ConsumptionAggregated]:
        """Calculate daily consumption aggregations.

        Args:
            cups: CUPS identifier
            start_date: Start date for aggregation
            end_date: End date for aggregation

        Returns:
            List of daily consumption aggregations
        """
        # Get hourly consumptions from database
        db_service = await self._get_db_service()
        db_consumptions = await db_service.get_consumptions(cups, start_date, end_date)

        # Convert to Pydantic models for processing
        consumptions = []
        for db_cons in db_consumptions:
            cons = Consumption(
                datetime=db_cons.datetime,
                delta_h=db_cons.delta_h,
                value_kwh=db_cons.value_kwh,
                surplus_kwh=db_cons.surplus_kwh or 0.0,
                real=db_cons.real or True,
            )
            consumptions.append(cons)

        # Sort by datetime
        consumptions.sort(key=lambda x: x.datetime)

        # Aggregate by day
        daily_aggregations = {}

        for consumption in consumptions:
            curr_day = consumption.datetime.replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            # Determine tariff period
            tariff = get_pvpc_tariff(consumption.datetime)

            # Initialize daily aggregation if not exists
            if curr_day not in daily_aggregations:
                daily_aggregations[curr_day] = {
                    "datetime": curr_day,
                    "value_kwh": 0.0,
                    "value_p1_kwh": 0.0,
                    "value_p2_kwh": 0.0,
                    "value_p3_kwh": 0.0,
                    "surplus_kwh": 0.0,
                    "surplus_p1_kwh": 0.0,
                    "surplus_p2_kwh": 0.0,
                    "surplus_p3_kwh": 0.0,
                    "delta_h": 0.0,
                }

            # Add consumption values
            daily_aggregations[curr_day]["value_kwh"] += consumption.value_kwh
            daily_aggregations[curr_day]["surplus_kwh"] += consumption.surplus_kwh
            daily_aggregations[curr_day]["delta_h"] += consumption.delta_h

            # Add by tariff period
            if tariff == "p1":
                daily_aggregations[curr_day]["value_p1_kwh"] += consumption.value_kwh
                daily_aggregations[curr_day][
                    "surplus_p1_kwh"
                ] += consumption.surplus_kwh
            elif tariff == "p2":
                daily_aggregations[curr_day]["value_p2_kwh"] += consumption.value_kwh
                daily_aggregations[curr_day][
                    "surplus_p2_kwh"
                ] += consumption.surplus_kwh
            elif tariff == "p3":
                daily_aggregations[curr_day]["value_p3_kwh"] += consumption.value_kwh
                daily_aggregations[curr_day][
                    "surplus_p3_kwh"
                ] += consumption.surplus_kwh

        # Convert to ConsumptionAggregated objects and round values
        result = []
        for day_data in sorted(
            daily_aggregations.values(), key=lambda x: x["datetime"]
        ):
            # Round all float values to 2 decimal places
            for key, value in day_data.items():
                if isinstance(value, float):
                    day_data[key] = round(value, 2)

            aggregated = ConsumptionAggregated(**day_data)
            result.append(aggregated)

        return result

    async def get_monthly_consumptions(
        self,
        cups: str,
        start_date: datetime,
        end_date: datetime,
        cycle_start_day: int = 1,
    ) -> List[ConsumptionAggregated]:
        """Calculate monthly consumption aggregations.

        Args:
            cups: CUPS identifier
            start_date: Start date for aggregation
            end_date: End date for aggregation
            cycle_start_day: Day of month when billing cycle starts (1-30)

        Returns:
            List of monthly consumption aggregations
        """
        # Get hourly consumptions from database
        db_service = await self._get_db_service()
        db_consumptions = await db_service.get_consumptions(cups, start_date, end_date)

        # Convert to Pydantic models for processing
        consumptions = []
        for db_cons in db_consumptions:
            cons = Consumption(
                datetime=db_cons.datetime,
                delta_h=db_cons.delta_h,
                value_kwh=db_cons.value_kwh,
                surplus_kwh=db_cons.surplus_kwh or 0.0,
                real=db_cons.real or True,
            )
            consumptions.append(cons)

        # Sort by datetime
        consumptions.sort(key=lambda x: x.datetime)

        # Calculate cycle offset
        cycle_offset = cycle_start_day - 1

        # Aggregate by month (considering billing cycle)
        monthly_aggregations = {}

        for consumption in consumptions:
            curr_day = consumption.datetime.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            # Adjust for billing cycle start day
            billing_month_date = (curr_day - timedelta(days=cycle_offset)).replace(
                day=1
            )

            # Determine tariff period
            tariff = get_pvpc_tariff(consumption.datetime)

            # Initialize monthly aggregation if not exists
            if billing_month_date not in monthly_aggregations:
                monthly_aggregations[billing_month_date] = {
                    "datetime": billing_month_date,
                    "value_kwh": 0.0,
                    "value_p1_kwh": 0.0,
                    "value_p2_kwh": 0.0,
                    "value_p3_kwh": 0.0,
                    "surplus_kwh": 0.0,
                    "surplus_p1_kwh": 0.0,
                    "surplus_p2_kwh": 0.0,
                    "surplus_p3_kwh": 0.0,
                    "delta_h": 0.0,
                }

            # Add consumption values
            monthly_aggregations[billing_month_date][
                "value_kwh"
            ] += consumption.value_kwh
            monthly_aggregations[billing_month_date][
                "surplus_kwh"
            ] += consumption.surplus_kwh
            monthly_aggregations[billing_month_date]["delta_h"] += consumption.delta_h

            # Add by tariff period
            if tariff == "p1":
                monthly_aggregations[billing_month_date][
                    "value_p1_kwh"
                ] += consumption.value_kwh
                monthly_aggregations[billing_month_date][
                    "surplus_p1_kwh"
                ] += consumption.surplus_kwh
            elif tariff == "p2":
                monthly_aggregations[billing_month_date][
                    "value_p2_kwh"
                ] += consumption.value_kwh
                monthly_aggregations[billing_month_date][
                    "surplus_p2_kwh"
                ] += consumption.surplus_kwh
            elif tariff == "p3":
                monthly_aggregations[billing_month_date][
                    "value_p3_kwh"
                ] += consumption.value_kwh
                monthly_aggregations[billing_month_date][
                    "surplus_p3_kwh"
                ] += consumption.surplus_kwh

        # Convert to ConsumptionAggregated objects and round values
        result = []
        for month_data in sorted(
            monthly_aggregations.values(), key=lambda x: x["datetime"]
        ):
            # Round all float values to 2 decimal places
            for key, value in month_data.items():
                if isinstance(value, float):
                    month_data[key] = round(value, 2)

            aggregated = ConsumptionAggregated(**month_data)
            result.append(aggregated)

        return result

    async def get_consumption_summary(
        self, cups: str, target_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get consumption summary data compatible with EdataHelper attributes.

        Args:
            cups: CUPS identifier
            target_date: Reference date for calculations (defaults to today)

        Returns:
            Dict with summary attributes matching EdataHelper format
        """
        from datetime import timedelta

        from dateutil.relativedelta import relativedelta

        if target_date is None:
            target_date = datetime.now()

        # Calculate date ranges
        today_starts = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_starts = today_starts - timedelta(days=1)
        month_starts = target_date.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        last_month_starts = month_starts - relativedelta(months=1)

        # Get daily and monthly aggregations
        daily_consumptions = await self.get_daily_consumptions(
            cups=cups, start_date=yesterday_starts, end_date=today_starts
        )

        monthly_consumptions = await self.get_monthly_consumptions(
            cups=cups,
            start_date=last_month_starts,
            end_date=month_starts + relativedelta(months=1),
        )

        # Get all consumptions to find last registered data
        all_consumptions = await self.get_stored_consumptions(cups=cups)

        # Initialize summary attributes
        summary: Dict[str, Any] = {
            # Yesterday consumption
            "yesterday_kWh": None,
            "yesterday_hours": None,
            "yesterday_p1_kWh": None,
            "yesterday_p2_kWh": None,
            "yesterday_p3_kWh": None,
            "yesterday_surplus_kWh": None,
            "yesterday_surplus_p1_kWh": None,
            "yesterday_surplus_p2_kWh": None,
            "yesterday_surplus_p3_kWh": None,
            # Current month consumption
            "month_kWh": None,
            "month_surplus_kWh": None,
            "month_days": None,
            "month_daily_kWh": None,
            "month_p1_kWh": None,
            "month_p2_kWh": None,
            "month_p3_kWh": None,
            "month_surplus_p1_kWh": None,
            "month_surplus_p2_kWh": None,
            "month_surplus_p3_kWh": None,
            # Last month consumption
            "last_month_kWh": None,
            "last_month_surplus_kWh": None,
            "last_month_days": None,
            "last_month_daily_kWh": None,
            "last_month_p1_kWh": None,
            "last_month_p2_kWh": None,
            "last_month_p3_kWh": None,
            "last_month_surplus_p1_kWh": None,
            "last_month_surplus_p2_kWh": None,
            "last_month_surplus_p3_kWh": None,
            # Last registered data
            "last_registered_date": None,
            "last_registered_day_kWh": None,
            "last_registered_day_surplus_kWh": None,
            "last_registered_day_hours": None,
            "last_registered_day_p1_kWh": None,
            "last_registered_day_p2_kWh": None,
            "last_registered_day_p3_kWh": None,
            "last_registered_day_surplus_p1_kWh": None,
            "last_registered_day_surplus_p2_kWh": None,
            "last_registered_day_surplus_p3_kWh": None,
        }

        # Fill yesterday data
        yesterday_data = next(
            (
                d
                for d in daily_consumptions
                if d.datetime.date() == yesterday_starts.date()
            ),
            None,
        )
        if yesterday_data:
            summary["yesterday_kWh"] = yesterday_data.value_kwh
            summary["yesterday_hours"] = yesterday_data.delta_h
            summary["yesterday_p1_kWh"] = yesterday_data.value_p1_kwh
            summary["yesterday_p2_kWh"] = yesterday_data.value_p2_kwh
            summary["yesterday_p3_kWh"] = yesterday_data.value_p3_kwh
            summary["yesterday_surplus_kWh"] = yesterday_data.surplus_kwh
            summary["yesterday_surplus_p1_kWh"] = yesterday_data.surplus_p1_kwh
            summary["yesterday_surplus_p2_kWh"] = yesterday_data.surplus_p2_kwh
            summary["yesterday_surplus_p3_kWh"] = yesterday_data.surplus_p3_kwh

        # Fill current month data
        current_month_data = next(
            (
                m
                for m in monthly_consumptions
                if m.datetime.year == month_starts.year
                and m.datetime.month == month_starts.month
            ),
            None,
        )
        if current_month_data:
            summary["month_kWh"] = current_month_data.value_kwh
            summary["month_surplus_kWh"] = current_month_data.surplus_kwh
            summary["month_days"] = (
                current_month_data.delta_h / 24 if current_month_data.delta_h else None
            )
            summary["month_daily_kWh"] = (
                (current_month_data.value_kwh / (current_month_data.delta_h / 24))
                if current_month_data.delta_h and current_month_data.delta_h > 0
                else None
            )
            summary["month_p1_kWh"] = current_month_data.value_p1_kwh
            summary["month_p2_kWh"] = current_month_data.value_p2_kwh
            summary["month_p3_kWh"] = current_month_data.value_p3_kwh
            summary["month_surplus_p1_kWh"] = current_month_data.surplus_p1_kwh
            summary["month_surplus_p2_kWh"] = current_month_data.surplus_p2_kwh
            summary["month_surplus_p3_kWh"] = current_month_data.surplus_p3_kwh

        # Fill last month data
        last_month_data = next(
            (
                m
                for m in monthly_consumptions
                if m.datetime.year == last_month_starts.year
                and m.datetime.month == last_month_starts.month
            ),
            None,
        )
        if last_month_data:
            summary["last_month_kWh"] = last_month_data.value_kwh
            summary["last_month_surplus_kWh"] = last_month_data.surplus_kwh
            summary["last_month_days"] = (
                last_month_data.delta_h / 24 if last_month_data.delta_h else None
            )
            summary["last_month_daily_kWh"] = (
                (last_month_data.value_kwh / (last_month_data.delta_h / 24))
                if last_month_data.delta_h and last_month_data.delta_h > 0
                else None
            )
            summary["last_month_p1_kWh"] = last_month_data.value_p1_kwh
            summary["last_month_p2_kWh"] = last_month_data.value_p2_kwh
            summary["last_month_p3_kWh"] = last_month_data.value_p3_kwh
            summary["last_month_surplus_p1_kWh"] = last_month_data.surplus_p1_kwh
            summary["last_month_surplus_p2_kWh"] = last_month_data.surplus_p2_kwh
            summary["last_month_surplus_p3_kWh"] = last_month_data.surplus_p3_kwh

        # Fill last registered data
        if all_consumptions:
            # Sort by datetime and get the last one
            last_consumption = max(all_consumptions, key=lambda c: c.datetime)
            summary["last_registered_date"] = last_consumption.datetime

            # Get the last day's aggregated data
            last_day_start = last_consumption.datetime.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            last_day_end = last_day_start + timedelta(days=1)

            last_day_daily = await self.get_daily_consumptions(
                cups=cups, start_date=last_day_start, end_date=last_day_end
            )

            if last_day_daily:
                last_day_data = last_day_daily[0]
                summary["last_registered_day_kWh"] = last_day_data.value_kwh
                summary["last_registered_day_surplus_kWh"] = last_day_data.surplus_kwh
                summary["last_registered_day_hours"] = last_day_data.delta_h
                summary["last_registered_day_p1_kWh"] = last_day_data.value_p1_kwh
                summary["last_registered_day_p2_kWh"] = last_day_data.value_p2_kwh
                summary["last_registered_day_p3_kWh"] = last_day_data.value_p3_kwh
                summary["last_registered_day_surplus_p1_kWh"] = (
                    last_day_data.surplus_p1_kwh
                )
                summary["last_registered_day_surplus_p2_kWh"] = (
                    last_day_data.surplus_p2_kwh
                )
                summary["last_registered_day_surplus_p3_kWh"] = (
                    last_day_data.surplus_p3_kwh
                )

        # Round numeric values to 2 decimal places
        for key, value in summary.items():
            if isinstance(value, float):
                summary[key] = round(value, 2)

        return summary
