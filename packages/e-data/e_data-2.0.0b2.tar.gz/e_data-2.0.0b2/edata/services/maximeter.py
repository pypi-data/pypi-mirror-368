"""Maximeter service for fetching and updating maximum power data."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from edata.connectors.datadis import DatadisConnector
from edata.models.maximeter import MaxPower
from edata.services.database import DatabaseService, get_database_service

_LOGGER = logging.getLogger(__name__)


class MaximeterService:
    """Service for managing maximum power data fetching and storage."""

    def __init__(
        self,
        datadis_connector: DatadisConnector,
        storage_dir: Optional[str] = None,
    ):
        """Initialize maximeter service.

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

    async def update_maxpower(
        self,
        cups: str,
        distributor_code: str,
        start_date: datetime,
        end_date: datetime,
        authorized_nif: Optional[str] = None,
        force_full_update: bool = False,
    ) -> Dict[str, Any]:
        """Update maximeter (maximum power) data for a CUPS in the specified date range.

        Args:
            cups: CUPS identifier
            distributor_code: Distributor company code
            start_date: Start date for maxpower data
            end_date: End date for maxpower data
            authorized_nif: Authorized NIF if accessing on behalf of someone
            force_full_update: If True, fetch all data ignoring existing records

        Returns:
            Dict with operation results and statistics
        """
        _LOGGER.info(
            f"Updating maxpower for CUPS {cups[-5:]:>5} from {start_date.date()} to {end_date.date()}"
        )

        # Determine actual start date based on existing data
        actual_start_date = start_date
        if not force_full_update:
            last_maxpower_date = await self.get_last_maxpower_date(cups)
            if last_maxpower_date:
                # Start from the day after the last maxpower reading
                actual_start_date = max(
                    start_date, last_maxpower_date + timedelta(hours=1)
                )
                _LOGGER.info(
                    f"Found existing maxpower data up to {last_maxpower_date.date()}, fetching from {actual_start_date.date()}"
                )
            else:
                _LOGGER.info(
                    f"No existing maxpower data found for CUPS {cups[-5:]:>5}, fetching all data"
                )

        # If actual start date is beyond end date, no new data needed
        if actual_start_date >= end_date:
            _LOGGER.info(
                f"No new maxpower data needed for CUPS {cups[-5:]:>5} (up to date)"
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
                "message": "Maxpower data is up to date",
            }

        try:
            # Fetch maxpower data from datadis (only missing data)
            maxpower_readings = await self._datadis.get_max_power(
                cups=cups,
                distributor_code=distributor_code,
                start_date=actual_start_date,
                end_date=end_date,
                authorized_nif=authorized_nif,
            )

            # Save to database
            saved_count = 0
            updated_count = 0

            for maxpower in maxpower_readings:
                # Convert Pydantic model to dict and add CUPS
                maxpower_dict = maxpower.model_dump()
                maxpower_dict["cups"] = cups

                # Check if maxpower reading already exists
                db_service = await self._get_db_service()
                existing = await db_service.get_maxpower_readings(
                    cups=cups, start_date=maxpower.datetime, end_date=maxpower.datetime
                )

                if existing:
                    updated_count += 1
                else:
                    saved_count += 1

                await db_service.save_maxpower(maxpower_dict)

            result = {
                "success": True,
                "cups": cups,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "actual_start": actual_start_date.isoformat(),
                },
                "stats": {
                    "fetched": len(maxpower_readings),
                    "saved": saved_count,
                    "updated": updated_count,
                },
            }

            if actual_start_date > start_date:
                result["message"] = (
                    f"Fetched only missing maxpower data from {actual_start_date.date()}"
                )

            _LOGGER.info(
                f"Maxpower update completed: {len(maxpower_readings)} fetched, "
                f"{saved_count} saved, {updated_count} updated"
            )

            return result

        except Exception as e:
            _LOGGER.error(f"Error updating maxpower for CUPS {cups}: {str(e)}")
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

    async def update_maxpower_range_by_months(
        self,
        cups: str,
        distributor_code: str,
        start_date: datetime,
        end_date: datetime,
        authorized_nif: Optional[str] = None,
        force_full_update: bool = False,
    ) -> Dict[str, Any]:
        """Update maxpower data month by month to respect datadis limits.

        Args:
            cups: CUPS identifier
            distributor_code: Distributor company code
            start_date: Start date for maxpower data
            end_date: End date for maxpower data
            authorized_nif: Authorized NIF if accessing on behalf of someone
            force_full_update: If True, fetch all data ignoring existing records

        Returns:
            Dict with operation results and statistics for all months
        """
        _LOGGER.info(
            f"Updating maxpower range for CUPS {cups[-5:]:>5} "
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

            # Update maxpower for this month
            maxpower_result = await self.update_maxpower(
                cups=cups,
                distributor_code=distributor_code,
                start_date=current_date,
                end_date=actual_end,
                authorized_nif=authorized_nif,
                force_full_update=force_full_update,
            )

            result_entry = {
                "month": current_date.strftime("%Y-%m"),
                "maxpower": maxpower_result,
            }

            results.append(result_entry)
            current_date = month_end

        # Calculate totals
        total_maxpower_fetched = sum(
            r["maxpower"]["stats"]["fetched"]
            for r in results
            if r["maxpower"]["success"]
        )
        total_maxpower_saved = sum(
            r["maxpower"]["stats"]["saved"] for r in results if r["maxpower"]["success"]
        )
        total_maxpower_updated = sum(
            r["maxpower"]["stats"]["updated"]
            for r in results
            if r["maxpower"]["success"]
        )

        summary = {
            "success": all(r["maxpower"]["success"] for r in results),
            "cups": cups,
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "months_processed": len(results),
            "total_stats": {
                "maxpower_fetched": total_maxpower_fetched,
                "maxpower_saved": total_maxpower_saved,
                "maxpower_updated": total_maxpower_updated,
            },
            "monthly_results": results,
        }

        _LOGGER.info(
            f"Maxpower range update completed: {len(results)} months processed, "
            f"{total_maxpower_fetched} maxpower readings fetched"
        )

        return summary

    async def get_stored_maxpower(
        self,
        cups: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List:
        """Get stored maxpower readings from database.

        Args:
            cups: CUPS identifier
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of MaxPower objects from database
        """
        db_service = await self._get_db_service()
        return await db_service.get_maxpower_readings(cups, start_date, end_date)

    async def get_last_maxpower_date(self, cups: str) -> Optional[datetime]:
        """Get the date of the last maxpower record in the database.

        Args:
            cups: CUPS identifier

        Returns:
            Datetime of last maxpower reading or None if no data exists
        """
        db_service = await self._get_db_service()
        latest_maxpower = await db_service.get_latest_maxpower(cups)

        if latest_maxpower:
            return latest_maxpower.datetime
        return None

    async def get_peak_power_for_period(
        self, cups: str, start_date: datetime, end_date: datetime
    ) -> Optional[MaxPower]:
        """Get the peak power reading for a specific period.

        Args:
            cups: CUPS identifier
            start_date: Start date for search
            end_date: End date for search

        Returns:
            MaxPower object with highest value_kw in the period, or None if no data
        """
        readings = await self.get_stored_maxpower(cups, start_date, end_date)

        if not readings:
            return None

        # Find the reading with maximum power
        peak_reading = max(readings, key=lambda r: r.value_kw)
        return peak_reading

    async def get_daily_peaks(
        self, cups: str, start_date: datetime, end_date: datetime
    ) -> Dict[str, MaxPower]:
        """Get daily peak power readings for a date range.

        Args:
            cups: CUPS identifier
            start_date: Start date
            end_date: End date

        Returns:
            Dict with date strings as keys and MaxPower objects as values
        """
        readings = await self.get_stored_maxpower(cups, start_date, end_date)

        if not readings:
            return {}

        # Group by date and find peak for each day
        daily_peaks = {}
        for reading in readings:
            date_key = reading.datetime.date().isoformat()

            if (
                date_key not in daily_peaks
                or reading.value_kw > daily_peaks[date_key].value_kw
            ):
                daily_peaks[date_key] = reading

        return daily_peaks

    async def get_maximeter_summary(
        self,
        cups: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get maximeter summary data compatible with EdataHelper attributes.

        Args:
            cups: CUPS identifier
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Dict with summary attributes matching EdataHelper format
        """
        maximeter_data = await self.get_stored_maxpower(cups, start_date, end_date)

        if not maximeter_data:
            return {
                "max_power_kW": None,
                "max_power_date": None,
                "max_power_mean_kW": None,
                "max_power_90perc_kW": None,
            }

        # Calculate summary statistics
        power_values = [m.value_kw for m in maximeter_data]
        max_power = max(power_values)
        mean_power = sum(power_values) / len(power_values)

        # Find date for max power
        max_power_date = next(
            m.datetime for m in maximeter_data if m.value_kw == max_power
        )

        # Calculate 90th percentile
        sorted_values = sorted(power_values)
        n = len(sorted_values)
        p90_index = int(0.9 * n)
        p90_power = sorted_values[p90_index] if p90_index < n else sorted_values[-1]

        return {
            "max_power_kW": round(max_power, 2),
            "max_power_date": max_power_date,
            "max_power_mean_kW": round(mean_power, 2),
            "max_power_90perc_kW": round(p90_power, 2),
        }
