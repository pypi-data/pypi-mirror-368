from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple, Union

from kognitos.bdk.runtime.client.book_descriptor import BookDescriptor
from kognitos.bdk.runtime.client.book_procedure_descriptor import \
    BookProcedureDescriptor
from kognitos.bdk.runtime.client.concept_value import ConceptValue
from kognitos.bdk.runtime.client.environment_information import \
    EnvironmentInformation
from kognitos.bdk.runtime.client.input_concept import InputConcept
from kognitos.bdk.runtime.client.offload import AWSOffload
from kognitos.bdk.runtime.client.question_answer import Question
from kognitos.bdk.runtime.client.test_connection import TestConnectionResponse


class BDKClient(ABC):
    """
    Class defining the operations for interacting with the BDK (Book Development Kit).
    This interface decouples the core application from the concrete BDK client implementation.
    """

    @abstractmethod
    def retrieve_books(self) -> List[BookDescriptor]:
        """Retrieves a list of all available books."""

    @abstractmethod
    def retrieve_book(self, name: str, version: str) -> BookDescriptor:
        """Retrieves a specific book by its name and version."""

    @abstractmethod
    def retrieve_procedures(self, name: str, version: str, include_connect: bool) -> List[BookProcedureDescriptor]:
        """Retrieves procedures for a given book."""

    @abstractmethod
    def retrieve_procedure(self, name: str, version: str, procedure_id: str, include_connect: bool) -> Optional[BookProcedureDescriptor]:
        """Retrieves a single procedure by its ID from a given book."""

    @abstractmethod
    def invoke_procedure(
        self,
        name: str,
        version: str,
        procedure_id: str,
        input_concepts: List[InputConcept],
        authentication_id: Optional[str] = None,
        authentication_credentials: Optional[List[Tuple[str, Any]]] = None,
        offload: Optional[AWSOffload] = None,
    ) -> Union[List[ConceptValue], List[Question]]:
        """Invokes a specific procedure within a book."""

    @abstractmethod
    def environment_information(self) -> EnvironmentInformation:
        """Retrieves information about the BDK environment."""

    @abstractmethod
    def test_connection(
        self,
        name: str,
        version: str,
        authentication_id: Optional[str] = None,
        authentication_credentials: Optional[List[Tuple[str, Any]]] = None,
    ) -> TestConnectionResponse:
        """Tests the connection to a book, potentially with authentication."""
