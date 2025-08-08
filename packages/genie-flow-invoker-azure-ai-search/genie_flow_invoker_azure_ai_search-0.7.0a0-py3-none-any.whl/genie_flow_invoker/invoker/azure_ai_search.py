from abc import ABC
from copy import deepcopy

from genie_flow_invoker import GenieInvoker
from genie_flow_invoker.codec import JsonInputDecoder, JsonOutputEncoder
from genie_flow_invoker.utils import get_config_value

from loguru import logger
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.search.documents import SearchClient


class AbstractAzureAISearchInvoker(
    GenieInvoker,
    JsonOutputEncoder,
    ABC,
):
    """
    The abstract Azure AI Search Invoker class. This class orchestrates the creation of
    the Azure AI Search Client. It also captures and maintains any default parameters
    that may have been set at the key `search_params` of a `meta.yaml` configuration file.

    Uses the Azure AI Search SDK of which documentation can be found here:
    https://azuresdkdocs.blob.core.windows.net/$web/python/azure-search-documents/11.5.1/azure.search.documents.html#module-azure.search.documents
    """

    def __init__(
            self,
            search_client: SearchClient,
            search_params: dict,
    ):
        """
        Instantiate a new AI Search Invoker. It needs an Azure AI Search Client.
        :param search_client: the Azure AI Search Client
        """
        super().__init__()
        self._search_client = search_client
        self._search_params = search_params

    @classmethod
    def from_config(cls, config: dict):
        """
        Create a new AI Search Invoker instance from a configuration dictionary. The
        dictionary should contain the following keys:
        - service_endpoint: the endpoint of the AI Search Service. Can also be set using
          the environment variable AZURE_SEARCH_SERVICE_ENDPOINT
        - index_name: the name of the AI Search Index. Can also be set using
          environment variable AZURE_INDEX_NAME
        - api_key: the key to be used to access the AI Search Service. Can also be set
          using environment variable AZURE_SEARCH_API_KEY

        If no API Key is provided, the Azure Search API client will try to authenticate
        using the `DefaultAzureCredential`.

        :param config: the dictionary obtained from the configuration file `meta.yaml`
        :return: a new instance of the AI Search Invoker
        """
        service_endpoint = get_config_value(
            config,
            "AZURE_SEARCH_SERVICE_ENDPOINT",
            "service_endpoint",
            "Search Service Endpoint",
        )
        index_name = get_config_value(
            config,
            "AZURE_SEARCH_INDEX_NAME",
            "index_name",
            "Search Index Name",
        )

        key = get_config_value(
            config,
            "AZURE_SEARCH_API_KEY",
            "api_key",
            "Search API Key",
            None,
        )
        if key is not None:
            logger.debug(
                "Using provided API Key to "
                "authenticate to Azure AI Search Service"
            )
            credential = AzureKeyCredential(key)
        else:
            logger.debug(
                "Using default Azure credential to "
                "authenticate to Azure AI Search Service"
            )
            credential = DefaultAzureCredential()

        client = SearchClient(
            endpoint=service_endpoint,
            index_name=index_name,
            credential=credential,
        )

        search_params = config.get("search_params", {})

        return cls(client, search_params)

    def _compile_params(self, new_params: dict) -> dict:
        params = deepcopy(self._search_params)
        params.update(new_params)
        return params


class AzureAISearchInvoker(
    AbstractAzureAISearchInvoker,
    JsonInputDecoder,
):

    def invoke(self, content: str) -> str:
        """
        The invocation of the Azure AI Search. Input is either the content to be searched
        or a JSON with parameters to be used in the search request.

        This method returns a JSON representation of the results obtained.

        :param content: a string representing either the search text or a JSON representation
            of the parameters to be passed.
        :return: a JSON representation of the results obtained
        """
        try:
            search_params = self._decode_input(content)
        except ValueError:
            search_params = dict(search_text=content)
        params = self._compile_params(search_params)

        logger.debug("Calling Azure AI Search with params {}", str(params))
        result = self._search_client.search(**params)

        return self._encode_output(result)


class AzureAILuceneSearchInvoker(AbstractAzureAISearchInvoker):

    def invoke(self, content: str) -> str:
        """
        This invokes a full Lucene search using the content parameter as the search
        definition.

        Additional parameters for this invocation should be set on the `search_params`
        key of the configuration file `meta.yaml`.

        Returns a JSON representation of the results obtained.

        :param content: the Lucene search definition
        :return: a JSON representation of the results obtained
        """
        search_params = dict(search_text=content, query_type="full")
        params = self._compile_params(search_params)
        result = self._search_client.search(**params)
        return self._encode_output(result)


class AzureAISemanticSearchInvoker(AbstractAzureAISearchInvoker):

    def invoke(self, content: str) -> str:
        """
        Conducts a semantic search using the content parameter as the text to search.

        Additional parameters for this invocation should be set on the `search_params`
        key of the configuration file `meta.yaml`.

        :param content: the text to search semantically
        :return: a JSON representation of the results obtained
        """
        search_params = dict(search_text=content, query_type="semantic")
        params = self._compile_params(search_params)
        result = self._search_client.search(**params)
        return self._encode_output(result)
