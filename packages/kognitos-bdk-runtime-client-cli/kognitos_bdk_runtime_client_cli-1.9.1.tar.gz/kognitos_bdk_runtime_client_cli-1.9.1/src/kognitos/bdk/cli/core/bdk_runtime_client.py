from typing import Any, List, Optional, Tuple, Union

import boto3

from kognitos.bdk.cli.core.client import BDKClient
from kognitos.bdk.runtime.client.book_descriptor import BookDescriptor
from kognitos.bdk.runtime.client.book_procedure_descriptor import \
    BookProcedureDescriptor
from kognitos.bdk.runtime.client.client import Client as ActualBDKClient
from kognitos.bdk.runtime.client.concept_value import ConceptValue
from kognitos.bdk.runtime.client.environment_information import \
    EnvironmentInformation
from kognitos.bdk.runtime.client.input_concept import InputConcept
from kognitos.bdk.runtime.client.offload import AWSOffload
from kognitos.bdk.runtime.client.question_answer import Question
from kognitos.bdk.runtime.client.test_connection import TestConnectionResponse


class DefaultBDKClient(BDKClient):
    """
    Adapter for the BDK Runtime Client, implementing the BDKClientPort interface.
    This class wraps the actual BDK client interactions.
    """

    def __init__(self, endpoint: str, region_name: Optional[str] = None, account_id: Optional[str] = None):
        """
        Initializes the DefaultBDKClient.

        Args:
            endpoint: The BDK client endpoint URL.
            region_name: AWS region name. If None, it will be inferred from the boto3 session.
            account_id: AWS account ID. If None, it will be inferred using STS.
        """
        if not endpoint:
            raise ValueError("BDK client endpoint cannot be empty.")

        session = boto3.Session()
        self._region_name = region_name or session.region_name

        try:
            self._account_id = account_id or boto3.client("sts").get_caller_identity().get("Account")
        except Exception as e:  # pylint: disable=broad-except
            print(f"Warning: Could not determine AWS Account ID via STS ({type(e).__name__}): {e}")
            self._account_id = None

        if not self._region_name:
            print("Warning: AWS region_name could not be determined. This might cause issues.")

        self._client = ActualBDKClient.from_url(endpoint, self._region_name, self._account_id, insecure=True)

    @staticmethod
    def build(bdkctl_endpoint: Optional[str]) -> BDKClient:
        """Builds and returns an instance of the DefaultBDKClient."""
        if not bdkctl_endpoint:
            raise ValueError("Please make sure to set the 'BDKCTL_DEFAULT_ENDPOINT' env var, " + "or provide an endpoint argument.")
        return DefaultBDKClient(endpoint=bdkctl_endpoint)

    def retrieve_books(self) -> List[BookDescriptor]:
        books = self._client.retrieve_books()
        books.sort(key=lambda x: x.name)
        return books

    def retrieve_book(self, name: str, version: str) -> BookDescriptor:
        return self._client.retrieve_book(name=name, version=version)

    def retrieve_procedures(self, name: str, version: str, include_connect: bool) -> List[BookProcedureDescriptor]:
        return self._client.retrieve_procedures(name=name, version=version, include_connect=include_connect)

    def retrieve_procedure(self, name: str, version: str, procedure_id: str, include_connect: bool) -> Optional[BookProcedureDescriptor]:
        all_procedures = self._client.retrieve_procedures(name=name, version=version, include_connect=include_connect)
        for proc in all_procedures:
            if proc.id == procedure_id:
                return proc
        return None

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
        return self._client.invoke_procedure(
            name=name,
            version=version,
            procedure_id=procedure_id,
            input_concepts=input_concepts,
            authentication_id=authentication_id,
            authentication_credentials=authentication_credentials,
            offload=offload,
        )

    def environment_information(self) -> EnvironmentInformation:
        return self._client.environment_information()

    def test_connection(
        self,
        name: str,
        version: str,
        authentication_id: Optional[str] = None,
        authentication_credentials: Optional[List[Tuple[str, Any]]] = None,
    ) -> TestConnectionResponse:
        return self._client.test_connection(
            name=name,
            version=version,
            authentication_id=authentication_id,
            authentication_credentials=authentication_credentials,
        )

    def get_raw_client(self) -> ActualBDKClient:
        """Provides access to the underlying BDK client. Use with caution."""
        return self._client
