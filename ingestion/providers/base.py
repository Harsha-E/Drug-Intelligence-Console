from typing import List, Dict, Any
from abc import ABC, abstractmethod

class SourceProvider(ABC):
    """
    Interface for external clinical knowledge sources.
    Every provider must translate its source data into the common canonical schema.
    """
    
    @abstractmethod
    def fetch_all(self) -> List[Dict[str, Any]]:
        """
        Fetches knowledge and returns a list of canonical drug/ingredient dicts.
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        pass
