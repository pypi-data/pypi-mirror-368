"""
Factory for creating LSH indices from database managers.
"""

import logging
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from ..ThothDbManager import ThothDbManager

from .manager import LshManager


class LshFactory:
    """Factory for creating LSH indices from any database type."""
    
    @staticmethod
    def create_lsh_from_db(
        db_manager: "ThothDbManager", 
        signature_size: int = 30,
        n_gram: int = 3,
        threshold: float = 0.5,
        verbose: bool = True,
        **kwargs
    ) -> None:
        """
        Create LSH index from any database manager type.
        
        This function extracts unique values from the database manager
        and creates an LSH index using the LshManager.
        
        Args:
            db_manager: Any ThothDbManager implementation
            signature_size: Size of MinHash signature
            n_gram: N-gram size for MinHash
            threshold: LSH similarity threshold
            verbose: Whether to show progress
            **kwargs: Additional arguments
        """
        if not db_manager.db_directory_path:
            raise ValueError("Database manager must have a valid db_directory_path")
        
        # Get unique values from the database
        logging.info(f"Extracting unique values from {db_manager.db_id}")
        unique_values = db_manager.get_unique_values()
        
        # Get or create LSH manager
        lsh_manager = db_manager.lsh_manager
        if lsh_manager is None:
            raise ValueError("Could not create LSH manager for database")
        
        # Create the LSH index
        lsh_manager.create_lsh(
            unique_values=unique_values,
            signature_size=signature_size,
            n_gram=n_gram,
            threshold=threshold,
            verbose=verbose,
            **kwargs
        )
        
        logging.info(f"LSH creation completed for {db_manager.db_id}")


def make_db_lsh(db_manager: "ThothDbManager", **kwargs) -> None:
    """
    Create LSH for any database type (maintains backward compatibility).
    
    This function provides backward compatibility with the existing
    make_db_lsh function signature while using the new architecture.
    
    Args:
        db_manager: Database manager instance
        **kwargs: LSH creation parameters
    """
    LshFactory.create_lsh_from_db(db_manager, **kwargs)
