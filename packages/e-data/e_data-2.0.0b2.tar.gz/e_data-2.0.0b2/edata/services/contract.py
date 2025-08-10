"""Contract service for fetching and managing contract data."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from edata.connectors.datadis import DatadisConnector
from edata.services.database import ContractModel, DatabaseService, get_database_service

_LOGGER = logging.getLogger(__name__)


class ContractService:
    """Service for managing contract data fetching and storage."""

    def __init__(
        self,
        datadis_connector: DatadisConnector,
        storage_dir: Optional[str] = None,
    ):
        """Initialize contract service.

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

    async def update_contracts(
        self, cups: str, distributor_code: str, authorized_nif: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update contract data for a CUPS.

        Args:
            cups: CUPS identifier
            distributor_code: Distributor code for the CUPS
            authorized_nif: Optional authorized NIF for access

        Returns:
            Dict with operation results and statistics
        """
        _LOGGER.info(f"Updating contracts for CUPS {cups[-5:]}")

        try:
            # Fetch contract data from Datadis
            contracts_data = await self._datadis.get_contract_detail(
                cups=cups,
                distributor_code=distributor_code,
                authorized_nif=authorized_nif,
            )

            if not contracts_data:
                _LOGGER.warning(f"No contract data found for CUPS {cups[-5:]}")
                return {
                    "success": True,
                    "stats": {
                        "fetched": 0,
                        "saved": 0,
                        "updated": 0,
                        "total_stored": 0,
                    },
                }

            # Get existing contracts to avoid duplicates
            db_service = await self._get_db_service()
            existing = await db_service.get_contracts(cups=cups)
            existing_periods = {(c.date_start, c.date_end) for c in existing}

            # Save contracts to database
            saved_count = 0
            updated_count = 0

            for contract in contracts_data:
                contract_dict = contract.model_dump()
                contract_dict["cups"] = cups

                # Check if this contract period already exists
                period_key = (contract.date_start, contract.date_end)

                if period_key in existing_periods:
                    updated_count += 1
                    _LOGGER.debug(
                        f"Updating existing contract for CUPS {cups[-5:]} "
                        f"period {contract.date_start.date()}-{contract.date_end.date()}"
                    )
                else:
                    saved_count += 1
                    _LOGGER.debug(
                        f"Saving new contract for CUPS {cups[-5:]} "
                        f"period {contract.date_start.date()}-{contract.date_end.date()}"
                    )

                # Save to database
                await db_service.save_contract(contract_dict)

            # Get total contracts stored for this CUPS
            all_contracts = await db_service.get_contracts(cups=cups)
            total_stored = len(all_contracts)

            result = {
                "success": True,
                "stats": {
                    "fetched": len(contracts_data),
                    "saved": saved_count,
                    "updated": updated_count,
                    "total_stored": total_stored,
                },
            }

            _LOGGER.info(
                f"Contract update completed for CUPS {cups[-5:]}: "
                f"{len(contracts_data)} fetched, {saved_count} saved, {updated_count} updated"
            )

            return result

        except Exception as e:
            _LOGGER.error(f"Error updating contracts for CUPS {cups[-5:]}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "stats": {"fetched": 0, "saved": 0, "updated": 0, "total_stored": 0},
            }

    async def get_contracts(
        self,
        cups: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[ContractModel]:
        """Get stored contract data for a CUPS.

        Args:
            cups: CUPS identifier
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of Contract objects
        """
        _LOGGER.debug(
            f"Getting contracts for CUPS {cups[-5:]}"
            f"{f' from {start_date.date()}' if start_date else ''}"
            f"{f' to {end_date.date()}' if end_date else ''}"
        )

        try:
            db_service = await self._get_db_service()
            contracts = await db_service.get_contracts(cups=cups)

            # Apply date filters if provided
            if start_date or end_date:
                filtered_contracts = []
                for contract in contracts:
                    # Check if contract period overlaps with requested period
                    if start_date and contract.date_end < start_date:
                        continue
                    if end_date and contract.date_start > end_date:
                        continue
                    filtered_contracts.append(contract)
                contracts = filtered_contracts

            _LOGGER.debug(f"Found {len(contracts)} contracts for CUPS {cups[-5:]}")
            return contracts

        except Exception as e:
            _LOGGER.error(f"Error getting contracts for CUPS {cups[-5:]}: {str(e)}")
            return []

    async def get_active_contract(
        self, cups: str, reference_date: Optional[datetime] = None
    ) -> Optional[ContractModel]:
        """Get the active contract for a CUPS at a specific date.

        Args:
            cups: CUPS identifier
            reference_date: Date to check for active contract (defaults to now)

        Returns:
            Active contract if found, None otherwise
        """
        if reference_date is None:
            reference_date = datetime.now()

        _LOGGER.debug(
            f"Getting active contract for CUPS {cups[-5:]} at {reference_date.date()}"
        )

        try:
            contracts = await self.get_contracts(cups=cups)

            for contract in contracts:
                if contract.date_start <= reference_date <= contract.date_end:
                    _LOGGER.debug(
                        f"Found active contract for CUPS {cups[-5:]} "
                        f"period {contract.date_start.date()}-{contract.date_end.date()}"
                    )
                    return contract

            _LOGGER.warning(
                f"No active contract found for CUPS {cups[-5:]} at {reference_date.date()}"
            )
            return None

        except Exception as e:
            _LOGGER.error(
                f"Error getting active contract for CUPS {cups[-5:]}: {str(e)}"
            )
            return None

    async def get_latest_contract(self, cups: str) -> Optional[ContractModel]:
        """Get the most recent contract for a CUPS.

        Args:
            cups: CUPS identifier

        Returns:
            Latest contract if found, None otherwise
        """
        _LOGGER.debug(f"Getting latest contract for CUPS {cups[-5:]}")

        try:
            contracts = await self.get_contracts(cups=cups)

            if not contracts:
                _LOGGER.warning(f"No contracts found for CUPS {cups[-5:]}")
                return None

            # Sort by end date descending to get the most recent
            latest_contract = max(contracts, key=lambda c: c.date_end)

            _LOGGER.debug(
                f"Found latest contract for CUPS {cups[-5:]} "
                f"period {latest_contract.date_start.date()}-{latest_contract.date_end.date()}"
            )
            return latest_contract

        except Exception as e:
            _LOGGER.error(
                f"Error getting latest contract for CUPS {cups[-5:]}: {str(e)}"
            )
            return None

    async def get_contract_summary(self, cups: str) -> Dict[str, Any]:
        """Get contract summary attributes for a CUPS.

        Args:
            cups: CUPS identifier

        Returns:
            Dict with contract summary attributes
        """
        _LOGGER.debug(f"Getting contract summary for CUPS {cups[-5:]}")

        try:
            # Get the most recent contract
            latest_contract = await self.get_latest_contract(cups)

            if not latest_contract:
                _LOGGER.warning(f"No contracts found for CUPS {cups[-5:]}")
                return {
                    "contract_p1_kW": None,
                    "contract_p2_kW": None,
                }

            summary = {
                "contract_p1_kW": latest_contract.power_p1,
                "contract_p2_kW": latest_contract.power_p2,
                # Add other contract-related summary attributes here as needed
            }

            _LOGGER.debug(f"Contract summary calculated for CUPS {cups[-5:]}")
            return summary

        except Exception as e:
            _LOGGER.error(
                f"Error getting contract summary for CUPS {cups[-5:]}: {str(e)}"
            )
            return {
                "contract_p1_kW": None,
                "contract_p2_kW": None,
            }

    async def get_contract_stats(self, cups: str) -> Dict[str, Any]:
        """Get statistics about contracts for a CUPS.

        Args:
            cups: CUPS identifier

        Returns:
            Dict with contract statistics
        """
        _LOGGER.debug(f"Getting contract statistics for CUPS {cups[-5:]}")

        try:
            contracts = await self.get_contracts(cups=cups)

            if not contracts:
                return {
                    "total_contracts": 0,
                    "date_range": None,
                    "power_ranges": {},
                }

            # Calculate date range
            earliest_start = min(c.date_start for c in contracts)
            latest_end = max(c.date_end for c in contracts)

            # Calculate power ranges
            p1_powers = [c.power_p1 for c in contracts if c.power_p1 is not None]
            p2_powers = [c.power_p2 for c in contracts if c.power_p2 is not None]

            power_ranges = {}
            if p1_powers:
                power_ranges["p1_kw"] = {"min": min(p1_powers), "max": max(p1_powers)}
            if p2_powers:
                power_ranges["p2_kw"] = {"min": min(p2_powers), "max": max(p2_powers)}

            stats = {
                "total_contracts": len(contracts),
                "date_range": {
                    "earliest_start": earliest_start,
                    "latest_end": latest_end,
                },
                "power_ranges": power_ranges,
            }

            _LOGGER.debug(f"Contract statistics calculated for CUPS {cups[-5:]}")
            return stats

        except Exception as e:
            _LOGGER.error(
                f"Error getting contract statistics for CUPS {cups[-5:]}: {str(e)}"
            )
            return {}
