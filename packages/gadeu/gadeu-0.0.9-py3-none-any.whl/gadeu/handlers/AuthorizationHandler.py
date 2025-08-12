# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

from abc import ABC, abstractmethod
import tornado


class AuthorizationHandler(ABC):
    """
    Authorization Handlers encapsulate the extraction and validation steps required to authorize a request.

    Implementors are responsible for extraction semantics, and may provide a default validator that Applications can override.

    Applications are responsible for configuring a handler, and providing a validator as part of configuration.

    Authorization Handlers validate secrets by performing any necessary decoding and decryption using Application-supplied encryption key(s). Validation of the results remains the responsibility of the Application. For example, ``BearerTokenAuthorizationHandler`` will extract and decompose a JWT, but it will not validate the claims to authorize the request, Application is reponsible for claims validation.

    Where an Authorization Handler provides a default validator there will most-likely also be additional decorators to configure metadata (such as decorating a request handler or method with required "Claims".)

    Consult the documentation of each Authorization Handler to understand its requirements and usage.
    """

    def __init__(self):
        pass

    @abstractmethod
    def authorize(self, requestHandler:tornado.web.RequestHandler) -> None:
        """
        Method which performs authorization. The specifics of which are an implementation detail of each ``AuthorizationHandler`` subclass.
        """
        pass
