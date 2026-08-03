from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from .execution_record import ExecutionRecord

class ExecutionStoreInterface(ABC):
    
    @abstractmethod
    def save(self, record: ExecutionRecord) -> None:
        pass

    @abstractmethod
    def get(self, analysis_id: str) -> Optional[ExecutionRecord]:
        pass

    @abstractmethod
    def list(self) -> List[ExecutionRecord]:
        pass

    @abstractmethod
    def latest(self, limit: int = 50) -> List[ExecutionRecord]:
        pass

    @abstractmethod
    def search(self, filters: Dict[str, Any]) -> List[ExecutionRecord]:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass
