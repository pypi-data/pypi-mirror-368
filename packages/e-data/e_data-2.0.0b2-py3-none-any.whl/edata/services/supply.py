"""Supply service for fetching and managing supply data."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from edata.connectors.datadis import DatadisConnector
from edata.services.database import DatabaseService, SupplyModel, get_database_service

_LOGGER = logging.getLogger(__name__)


class SupplyService:
    """Service for managing supply data fetching and storage."""

    def __init__(
        self,
        datadis_connector: DatadisConnector,
        storage_dir: Optional[str] = None,
    ):
        """Initialize supply service.

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

    async def update_supplies(
        self, authorized_nif: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update supply data from Datadis.

        Args:
            authorized_nif: Optional authorized NIF for access

        Returns:
            Dict with operation results and statistics
        """
        _LOGGER.info("Updating supplies from Datadis")

        try:
            # Fetch supply data from Datadis
            supplies_data = await self._datadis.get_supplies(
                authorized_nif=authorized_nif
            )

            if not supplies_data:
                _LOGGER.warning("No supply data found")
                return {
                    "success": True,
                    "stats": {
                        "fetched": 0,
                        "saved": 0,
                        "updated": 0,
                        "total_stored": 0,
                    },
                }

            # Save supplies to database
            saved_count = 0
            updated_count = 0
            db_service = await self._get_db_service()

            for supply in supplies_data:
                # Convert Pydantic model to dict for database storage
                supply_dict = supply.model_dump()

                # Check if supply already exists
                existing = await db_service.get_supplies(cups=supply.cups)

                if existing:
                    updated_count += 1
                    _LOGGER.debug(
                        f"Updating existing supply for CUPS {supply.cups[-5:]}"
                    )
                else:
                    saved_count += 1
                    _LOGGER.debug(f"Saving new supply for CUPS {supply.cups[-5:]}")

                # Save to database
                await db_service.save_supply(supply_dict)

            # Get total supplies stored
            all_supplies = await db_service.get_supplies()
            total_stored = len(all_supplies)

            result = {
                "success": True,
                "stats": {
                    "fetched": len(supplies_data),
                    "saved": saved_count,
                    "updated": updated_count,
                    "total_stored": total_stored,
                },
            }

            _LOGGER.info(
                f"Supply update completed: "
                f"{len(supplies_data)} fetched, {saved_count} saved, {updated_count} updated"
            )

            return result

        except Exception as e:
            _LOGGER.error(f"Error updating supplies: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "stats": {"fetched": 0, "saved": 0, "updated": 0, "total_stored": 0},
            }

    async def get_supplies(self, cups: Optional[str] = None) -> List[SupplyModel]:
        """Get stored supply data.

        Args:
            cups: Optional CUPS identifier filter

        Returns:
            List of Supply objects
        """
        _LOGGER.debug(f"Getting supplies{f' for CUPS {cups[-5:]}' if cups else ''}")

        try:
            db_service = await self._get_db_service()
            supplies = await db_service.get_supplies(cups=cups)

            _LOGGER.debug(f"Found {len(supplies)} supplies")
            return supplies

        except Exception as e:
            _LOGGER.error(f"Error getting supplies: {str(e)}")
            return []

    async def get_supply_by_cups(self, cups: str) -> Optional[SupplyModel]:
        """Get a specific supply by CUPS.

        Args:
            cups: CUPS identifier

        Returns:
            Supply object if found, None otherwise
        """
        _LOGGER.debug(f"Getting supply for CUPS {cups[-5:]}")

        try:
            db_service = await self._get_db_service()
            supplies = await db_service.get_supplies(cups=cups)

            if supplies:
                _LOGGER.debug(f"Found supply for CUPS {cups[-5:]}")
                return supplies[0]  # Should be unique

            _LOGGER.warning(f"No supply found for CUPS {cups[-5:]}")
            return None

        except Exception as e:
            _LOGGER.error(f"Error getting supply for CUPS {cups[-5:]}: {str(e)}")
            return None

    async def get_cups_list(self) -> List[str]:
        """Get list of all stored CUPS.

        Returns:
            List of CUPS identifiers
        """
        _LOGGER.debug("Getting CUPS list")

        try:
            db_service = await self._get_db_service()
            supplies = await db_service.get_supplies()
            cups_list = [supply.cups for supply in supplies if supply.cups]

            _LOGGER.debug(f"Found {len(cups_list)} CUPS")
            return cups_list

        except Exception as e:
            _LOGGER.error(f"Error getting CUPS list: {str(e)}")
            return []

    async def get_active_supplies(
        self, reference_date: Optional[datetime] = None
    ) -> List[SupplyModel]:
        """Get supplies that are active at a given date.

        Args:
            reference_date: Date to check for active supplies (defaults to now)

        Returns:
            List of active supplies
        """
        if reference_date is None:
            reference_date = datetime.now()

        _LOGGER.debug(f"Getting active supplies for date {reference_date.date()}")

        try:
            db_service = await self._get_db_service()
            all_supplies = await db_service.get_supplies()

            active_supplies = []
            for supply in all_supplies:
                if supply.date_start <= reference_date <= supply.date_end:
                    active_supplies.append(supply)

            _LOGGER.debug(f"Found {len(active_supplies)} active supplies")
            return active_supplies

        except Exception as e:
            _LOGGER.error(f"Error getting active supplies: {str(e)}")
            return []

    async def get_supply_stats(self) -> Dict[str, Any]:
        """Get statistics about stored supplies.

        Returns:
            Dict with supply statistics
        """
        _LOGGER.debug("Calculating supply statistics")

        try:
            db_service = await self._get_db_service()
            supplies = await db_service.get_supplies()

            if not supplies:
                return {
                    "total_supplies": 0,
                    "total_cups": 0,
                    "date_range": None,
                    "distributors": {},
                    "point_types": {},
                }

            # Calculate date range
            earliest_start = min(s.date_start for s in supplies)
            latest_end = max(s.date_end for s in supplies)

            # Count by distributor
            distributors = {}
            # Count by point type
            point_types = {}

            for supply in supplies:
                # Count distributors
                dist = supply.distributor or "Unknown"
                distributors[dist] = distributors.get(dist, 0) + 1

                # Count point types
                pt = supply.point_type or "Unknown"
                point_types[pt] = point_types.get(pt, 0) + 1

            stats = {
                "total_supplies": len(supplies),
                "total_cups": len(set(s.cups for s in supplies)),
                "date_range": {
                    "earliest_start": earliest_start,
                    "latest_end": latest_end,
                },
                "distributors": distributors,
                "point_types": point_types,
            }

            _LOGGER.debug(f"Supply statistics: {len(supplies)} total supplies")
            return stats

        except Exception as e:
            _LOGGER.error(f"Error calculating supply statistics: {str(e)}")
            return {}

    async def validate_cups(self, cups: str) -> bool:
        """Validate that a CUPS exists in stored supplies.

        Args:
            cups: CUPS identifier to validate

        Returns:
            True if CUPS exists, False otherwise
        """
        _LOGGER.debug(f"Validating CUPS {cups[-5:]}")

        try:
            supply = await self.get_supply_by_cups(cups)
            is_valid = supply is not None

            if is_valid:
                _LOGGER.debug(f"CUPS {cups[-5:]} is valid")
            else:
                _LOGGER.warning(f"CUPS {cups[-5:]} not found")

            return is_valid

        except Exception as e:
            _LOGGER.error(f"Error validating CUPS {cups[-5:]}: {str(e)}")
            return False

    async def get_distributor_code(self, cups: str) -> Optional[str]:
        """Get distributor code for a CUPS.

        Args:
            cups: CUPS identifier

        Returns:
            Distributor code if found, None otherwise
        """
        _LOGGER.debug(f"Getting distributor code for CUPS {cups[-5:]}")

        try:
            supply = await self.get_supply_by_cups(cups)
            if supply and supply.distributor_code:
                _LOGGER.debug(
                    f"Found distributor code {supply.distributor_code} for CUPS {cups[-5:]}"
                )
                return supply.distributor_code

            _LOGGER.warning(f"No distributor code found for CUPS {cups[-5:]}")
            return None

        except Exception as e:
            _LOGGER.error(
                f"Error getting distributor code for CUPS {cups[-5:]}: {str(e)}"
            )
            return None

    async def get_point_type(self, cups: str) -> Optional[int]:
        """Get point type for a CUPS.

        Args:
            cups: CUPS identifier

        Returns:
            Point type if found, None otherwise
        """
        _LOGGER.debug(f"Getting point type for CUPS {cups[-5:]}")

        try:
            supply = await self.get_supply_by_cups(cups)
            if supply and supply.point_type is not None:
                _LOGGER.debug(
                    f"Found point type {supply.point_type} for CUPS {cups[-5:]}"
                )
                return supply.point_type

            _LOGGER.warning(f"No point type found for CUPS {cups[-5:]}")
            return None

        except Exception as e:
            _LOGGER.error(f"Error getting point type for CUPS {cups[-5:]}: {str(e)}")
            return None

    async def get_supply_summary(self, cups: str) -> Dict[str, Any]:
        """Get supply summary attributes for a CUPS.

        Args:
            cups: CUPS identifier

        Returns:
            Dict with supply summary attributes
        """
        _LOGGER.debug(f"Getting supply summary for CUPS {cups[-5:]}")

        try:
            supply = await self.get_supply_by_cups(cups)

            if not supply:
                _LOGGER.warning(f"No supply found for CUPS {cups[-5:]}")
                return {"cups": None}

            summary = {
                "cups": supply.cups,
                # Add other supply-related summary attributes here as needed
                # These would be used by EdataHelper for calculating summary attributes
            }

            _LOGGER.debug(f"Supply summary calculated for CUPS {cups[-5:]}")
            return summary

        except Exception as e:
            _LOGGER.error(
                f"Error getting supply summary for CUPS {cups[-5:]}: {str(e)}"
            )
            return {"cups": None}
