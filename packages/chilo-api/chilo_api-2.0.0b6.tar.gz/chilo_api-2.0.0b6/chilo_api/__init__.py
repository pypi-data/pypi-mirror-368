from typing import Union

from chilo_api.core.router import Router as Chilo
from chilo_api.core import logger
from chilo_api.core.logger.decorator import log
from chilo_api.core.requirements import requirements
from chilo_api.core.rest.request import RestRequest
from chilo_api.core.rest.response import RestResponse
from chilo_api.core.grpc.request import GRPCRequest
from chilo_api.core.grpc.response import GRPCResponse

Request = Union[RestRequest, GRPCRequest]
Response = Union[RestResponse, GRPCResponse]
