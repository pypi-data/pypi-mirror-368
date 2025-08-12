# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

import enum
from typing import Any, Callable
import tornado

from ..AuthorizationMethod import AuthorizationMethod
from ..TokenUtil import TokenUtil
from .AuthorizationHandler import AuthorizationHandler


class ApiKeyLocation(enum.IntEnum):
    COOKIE = 1
    HEADER = 2
    QUERY = 3


class ApiKeyAuthorizationHandler(AuthorizationHandler):
    """
    An authorization handler for API KEY security scheme.
    """

    __claimsArgumentName:str
    __key:str
    __location:ApiKeyLocation
    __name:str
    __validator:Callable[[str, dict[str,Any]],bool]

    def __init__(self, key:str, validator:Callable[[str, dict[str,Any]],bool] = lambda t,c: True, location:ApiKeyLocation = ApiKeyLocation.HEADER, name:str = 'X-Api-Key', claimsArgumentName:str = 'claims'):
        super().__init__()
        self.__claimsArgumentName = claimsArgumentName
        self.__key = key
        self.__location = location
        self.__name = name
        self.__validator = validator

    def authorize(self, requestHandler:tornado.web.RequestHandler) -> None:
        apiKey:str = None
        match self.__location:
            case ApiKeyLocation.COOKIE:
                apiKey = requestHandler.request.cookies.get(self.__name, None)
            case ApiKeyLocation.HEADER:
                apiKey = requestHandler.request.headers.get(self.__name, None)
            case ApiKeyLocation.QUERY:
                apiKey = requestHandler.get_argument(self.__name, None)
        if apiKey is None:
            raise tornado.web.HTTPError(403, 'No Authorization')
        claims:dict[str,Any] = None
        try:
            claims = TokenUtil.getTokenClaims(self.__key, apiKey, AuthorizationMethod.APIKEY)
            if self.__claimsArgumentName is not None:
                requestHandler.request.arguments[self.__claimsArgumentName] = claims
        except:
            raise tornado.web.HTTPError(403, 'Authorization Fail')
        if not self.__validator(apiKey, claims):
            raise tornado.web.HTTPError(403, 'Not Authorized')
