import abc
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from kognitos.bdk.runtime.client.value import (BooleanValue, ConceptualValue,
                                               DictionaryValue, ListValue,
                                               NullValue, NumberValue,
                                               OpaqueValue, SensitiveValue,
                                               TextValue, Value)

logger = logging.getLogger("bdkctl")

MEMORY_STORE_DIR = Path.home() / ".bdkctl"
MEMORY_STORE_FILE = MEMORY_STORE_DIR / "memory_store.json"


class MemoryStorageBase(abc.ABC):
    """Base class for memory storage implementations."""

    @abc.abstractmethod
    def load(self) -> None:
        """Loads the memory store from the persistent backend."""

    @abc.abstractmethod
    def save(self) -> None:
        """Saves the current memory store to the persistent backend."""

    @abc.abstractmethod
    def get_item(self, key: str) -> Optional[Any]:
        """Retrieves an item from the memory store."""

    @abc.abstractmethod
    def set_item(self, key: str, value: Any) -> None:
        """Sets an item in the memory store."""

    @abc.abstractmethod
    def delete_item(self, key: str) -> None:
        """Deletes an item from the memory store."""

    @abc.abstractmethod
    def clear_all(self) -> None:
        """Clears all items from the memory store."""

    @abc.abstractmethod
    def get_all_items(self) -> Dict[str, Any]:
        """Retrieves all items from the memory store."""


class JsonFileStorage(MemoryStorageBase):
    def __init__(self, file_path: Path = MEMORY_STORE_FILE):
        self._file_path = file_path
        self._store: Dict[str, Any] = {}
        self.load()

    def _unwrap_value_for_json(self, value: Any) -> Any:
        """Converts BDK Value objects and Python collections to basic Python types for JSON serialization."""
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float, bool)):
            return value
        if value is None:
            return None

        if isinstance(value, list):
            return [self._unwrap_value_for_json(item) for item in value]
        if isinstance(value, dict):
            return {str(k): self._unwrap_value_for_json(v) for k, v in value.items()}

        if isinstance(value, TextValue):
            return value.text
        if isinstance(value, NumberValue):
            return value.number
        if isinstance(value, BooleanValue):
            return value.value
        if isinstance(value, NullValue):
            return None
        if isinstance(value, ListValue):
            return [self._unwrap_value_for_json(item) for item in value.value_instance]
        if isinstance(value, DictionaryValue):
            raw_dict = {}
            if hasattr(value, "_value") and isinstance(value._value, dict):
                raw_dict = value._value
            elif hasattr(value, "value") and isinstance(value.value, dict):
                raw_dict = value.value
            else:
                try:
                    raw_dict = {str(k): v for k, v in value.items()}
                except AttributeError:
                    logger.warning(
                        "DictionaryValue for %s does not have a standard ._value or .value dict attribute, nor is it directly iterable as a dict. Storing placeholder.", type(value)
                    )
                    return f"<DictionaryValueData:{str(list(value.keys()) if hasattr(value, 'keys') else 'UnknownKeys')[:50]}>"
            return {str(k): self._unwrap_value_for_json(v) for k, v in raw_dict.items()}

        if isinstance(value, ConceptualValue):
            return value.head
        if isinstance(value, OpaqueValue):
            return f"<OpaqueData:{value.is_a[0].text if value.is_a else 'Bytes'}>"
        if isinstance(value, SensitiveValue):
            return self._unwrap_value_for_json(value.value_instance)

        if isinstance(value, Value):
            logger.warning("Unhandled specific BDK Value type: %s. Storing a placeholder string.", type(value).__name__)
            return f"<UnhandledBDKValue:{type(value).__name__}>"

        return value

    def load(self) -> None:
        if not self._file_path.exists():
            self._store = {}
            return
        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if not content:
                    logger.warning("Memory store file %s is empty. Initializing empty store.", self._file_path)
                    self._store = {}
                    return
                self._store = json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning("Could not load memory store from %s: %s. Initializing empty store.", self._file_path, e, exc_info=True)
            self._store = {}
        except Exception as e:
            logger.error("Unexpected error loading memory store from %s: %s. Initializing empty store.", self._file_path, e, exc_info=True)
            self._store = {}

    def save(self) -> None:
        try:
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            unwrapped_store = {key: self._unwrap_value_for_json(val) for key, val in self._store.items()}
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(unwrapped_store, f, indent=2)
        except IOError as e:
            logger.error("Could not save memory store to %s: %s", self._file_path, e, exc_info=True)
        except Exception as e:
            logger.error("Unexpected error saving memory store to %s: %s", self._file_path, e, exc_info=True)

    def get_item(self, key: str) -> Optional[Any]:
        return self._store.get(key)

    def set_item(self, key: str, value: Any) -> None:
        self._store[key] = value
        self.save()

    def delete_item(self, key: str) -> None:
        if key in self._store:
            del self._store[key]
            self.save()

    def clear_all(self) -> None:
        self._store.clear()
        self.save()

    def get_all_items(self) -> Dict[str, Any]:
        return self._store.copy()
