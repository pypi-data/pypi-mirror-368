"""
Storage strategies for LSH data persistence.
"""

import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Tuple, Optional


class LshStorageStrategy(ABC):
    """Abstract base class for LSH storage strategies."""
    
    @abstractmethod
    def save(self, lsh_data: Any, minhashes_data: Any, base_path: Path) -> None:
        """
        Save LSH data and minhashes to storage.
        
        Args:
            lsh_data: The LSH index data
            minhashes_data: The minhashes data
            base_path: Base path for storage (without file extension)
        """
        pass
        
    @abstractmethod
    def load(self, base_path: Path) -> Tuple[Optional[Any], Optional[Any]]:
        """
        Load LSH data and minhashes from storage.
        
        Args:
            base_path: Base path for storage (without file extension)
            
        Returns:
            Tuple of (lsh_data, minhashes_data) or (None, None) if not found
        """
        pass
        
    @abstractmethod
    def exists(self, base_path: Path) -> bool:
        """
        Check if LSH data exists in storage.
        
        Args:
            base_path: Base path for storage (without file extension)
            
        Returns:
            True if data exists, False otherwise
        """
        pass


class PickleStorage(LshStorageStrategy):
    """Pickle-based storage strategy (current implementation)."""
    
    def save(self, lsh_data: Any, minhashes_data: Any, base_path: Path) -> None:
        """Save LSH data using pickle format."""
        lsh_path = base_path.with_suffix('.pkl')

        # Use the old naming convention: {db_id}_minhashes.pkl instead of {db_id}_lsh_minhashes.pkl
        # Extract db_id from base_path stem (remove _lsh suffix if present)
        db_id = base_path.stem.replace('_lsh', '') if base_path.stem.endswith('_lsh') else base_path.stem
        minhashes_path = base_path.parent / f"{db_id}_minhashes.pkl"

        # Ensure directory exists
        base_path.parent.mkdir(parents=True, exist_ok=True)

        # Save LSH data
        with open(lsh_path, 'wb') as f:
            pickle.dump(lsh_data, f)

        # Save minhashes data
        with open(minhashes_path, 'wb') as f:
            pickle.dump(minhashes_data, f)
    
    def load(self, base_path: Path) -> Tuple[Optional[Any], Optional[Any]]:
        """Load LSH data from pickle files."""
        lsh_path = base_path.with_suffix('.pkl')

        # Use the old naming convention: {db_id}_minhashes.pkl instead of {db_id}_lsh_minhashes.pkl
        # Extract db_id from base_path stem (remove _lsh suffix if present)
        db_id = base_path.stem.replace('_lsh', '') if base_path.stem.endswith('_lsh') else base_path.stem
        minhashes_path = base_path.parent / f"{db_id}_minhashes.pkl"

        try:
            # Load LSH data
            with open(lsh_path, 'rb') as f:
                lsh_data = pickle.load(f)

            # Load minhashes data
            with open(minhashes_path, 'rb') as f:
                minhashes_data = pickle.load(f)

            return lsh_data, minhashes_data

        except (FileNotFoundError, pickle.PickleError):
            return None, None
    
    def exists(self, base_path: Path) -> bool:
        """Check if both LSH and minhashes pickle files exist."""
        lsh_path = base_path.with_suffix('.pkl')

        # Use the old naming convention: {db_id}_minhashes.pkl instead of {db_id}_lsh_minhashes.pkl
        # Extract db_id from base_path stem (remove _lsh suffix if present)
        db_id = base_path.stem.replace('_lsh', '') if base_path.stem.endswith('_lsh') else base_path.stem
        minhashes_path = base_path.parent / f"{db_id}_minhashes.pkl"

        # Add debug logging to help diagnose path issues
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Checking LSH files existence:")
        logger.debug(f"  Base path: {base_path}")
        logger.debug(f"  DB ID: {db_id}")
        logger.debug(f"  LSH path: {lsh_path} (exists: {lsh_path.exists()})")
        logger.debug(f"  Minhashes path: {minhashes_path} (exists: {minhashes_path.exists()})")

        lsh_exists = lsh_path.exists()
        minhashes_exists = minhashes_path.exists()

        if not lsh_exists or not minhashes_exists:
            logger.warning(f"LSH files missing - LSH: {lsh_path} (exists: {lsh_exists}), Minhashes: {minhashes_path} (exists: {minhashes_exists})")

        return lsh_exists and minhashes_exists
