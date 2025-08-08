"""
LSH Manager for database-independent LSH operations.
"""

import logging
import pickle
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

from datasketch import MinHash, MinHashLSH

from .core import create_lsh_index, query_lsh_index
from .storage import LshStorageStrategy, PickleStorage


class LshManager:
    """
    Manages LSH operations independently of database implementation.
    
    This class handles creation, storage, loading, and querying of LSH indices
    using a pluggable storage strategy.
    """
    
    def __init__(self, storage_path: Path, storage_strategy: Optional[LshStorageStrategy] = None):
        """
        Initialize the LSH manager.
        
        Args:
            storage_path: Base path for LSH storage (directory containing preprocessed folder)
            storage_strategy: Storage strategy to use (defaults to PickleStorage)
        """
        self.storage_path = Path(storage_path)
        self.storage_strategy = storage_strategy or PickleStorage()
        self.lsh: Optional[MinHashLSH] = None
        self.minhashes: Optional[Dict[str, Tuple[MinHash, str, str, str]]] = None
        
        # Determine the database ID from the path
        self.db_id = self.storage_path.name
        
        # Set up the preprocessed directory path
        self.preprocessed_path = self.storage_path / "preprocessed"
        self.lsh_base_path = self.preprocessed_path / f"{self.db_id}_lsh"
    
    def create_lsh(
        self, 
        unique_values: Dict[str, Dict[str, List[str]]], 
        signature_size: int = 30,
        n_gram: int = 3,
        threshold: float = 0.5,
        verbose: bool = True,
        **kwargs
    ) -> None:
        """
        Create and persist LSH index from unique values.
        
        Args:
            unique_values: Dictionary of unique values from database
            signature_size: Size of MinHash signature
            n_gram: N-gram size for MinHash
            threshold: LSH similarity threshold
            verbose: Whether to show progress
            **kwargs: Additional arguments
        """
        logging.info(f"Creating LSH for database: {self.db_id}")
        
        # Ensure preprocessed directory exists
        self.preprocessed_path.mkdir(parents=True, exist_ok=True)
        
        # Save unique values for reference
        unique_values_path = self.preprocessed_path / f"{self.db_id}_unique_values.pkl"
        with open(unique_values_path, "wb") as file:
            pickle.dump(unique_values, file)
        logging.info("Saved unique values")
        
        # Create LSH index
        lsh, minhashes = create_lsh_index(
            unique_values=unique_values,
            signature_size=signature_size,
            n_gram=n_gram,
            threshold=threshold,
            verbose=verbose
        )
        
        # Store LSH data using the storage strategy
        self.storage_strategy.save(lsh, minhashes, self.lsh_base_path)
        logging.info(f"LSH saved to {self.lsh_base_path}")
        
        # Keep in memory for immediate use
        self.lsh = lsh
        self.minhashes = minhashes
    
    def load_lsh(self) -> bool:
        """
        Load LSH index from storage.
        
        Returns:
            True if successfully loaded, False otherwise
        """
        try:
            if not self.storage_strategy.exists(self.lsh_base_path):
                # Show the actual file paths being checked for better debugging
                lsh_file = self.lsh_base_path.with_suffix('.pkl')
                # Use the old naming convention for minhashes file
                db_id = self.lsh_base_path.stem.replace('_lsh', '') if self.lsh_base_path.stem.endswith('_lsh') else self.lsh_base_path.stem
                minhashes_file = self.lsh_base_path.parent / f"{db_id}_minhashes.pkl"
                unique_values_file = self.lsh_base_path.parent / f"{db_id}_unique_values.pkl"
                logging.warning(f"LSH files not found. Expected files:")
                logging.warning(f"  LSH file: {lsh_file}")
                logging.warning(f"  Minhashes file: {minhashes_file}")
                logging.warning(f"  Unique values file: {unique_values_file}")
                return False
            
            lsh_data, minhashes_data = self.storage_strategy.load(self.lsh_base_path)
            
            if lsh_data is None or minhashes_data is None:
                logging.error(f"Failed to load LSH data from {self.lsh_base_path}")
                return False
            
            self.lsh = lsh_data
            self.minhashes = minhashes_data
            logging.info(f"LSH loaded successfully for {self.db_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error loading LSH for {self.db_id}: {e}")
            return False
    
    def query(
        self, 
        keyword: str, 
        signature_size: int = 30,
        n_gram: int = 3,
        top_n: int = 10,
        **kwargs
    ) -> Dict[str, Dict[str, List[str]]]:
        """
        Query the LSH index for similar values.
        
        Args:
            keyword: Search keyword
            signature_size: Size of MinHash signature
            n_gram: N-gram size for MinHash
            top_n: Number of top results to return
            **kwargs: Additional arguments
            
        Returns:
            Dictionary of similar values organized by table and column
            
        Raises:
            Exception: If LSH is not loaded or query fails
        """
        if self.lsh is None or self.minhashes is None:
            # Try to load LSH if not already loaded
            if not self.load_lsh():
                raise Exception(f"Error loading LSH for {self.db_id}")
        
        return query_lsh_index(
            lsh=self.lsh,
            minhashes=self.minhashes,
            keyword=keyword,
            signature_size=signature_size,
            n_gram=n_gram,
            top_n=top_n
        )
    
    def is_available(self) -> bool:
        """
        Check if LSH data is available (either loaded or stored).
        
        Returns:
            True if LSH is available, False otherwise
        """
        return (self.lsh is not None and self.minhashes is not None) or \
               self.storage_strategy.exists(self.lsh_base_path)
    
    def clear(self) -> None:
        """Clear loaded LSH data from memory."""
        self.lsh = None
        self.minhashes = None
