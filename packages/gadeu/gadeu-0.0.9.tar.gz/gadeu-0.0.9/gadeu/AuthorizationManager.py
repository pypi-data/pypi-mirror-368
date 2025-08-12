# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

from .handlers.AuthorizationHandler import AuthorizationHandler
from .AuthorizationMethod import AuthorizationMethod


class AuthorizationManager:
    """
    Manages "Authorization Handlers" for "Authorization Methods".
    """

    __handlers:dict[AuthorizationMethod,AuthorizationHandler] = dict[AuthorizationMethod,AuthorizationHandler]()

    @classmethod
    def setAuthorizationHandler(cls, authorizationMethod:AuthorizationMethod, authorizationHandler:AuthorizationHandler|None) -> None:
        """
        Sets the :py:class:`~gadeu.handlers.AuthorizationHandler` for the specified :py:class:`~gadeu.AuthorizationMethod`.
        
        :param AuthorizationMethod authorizationMethod: The Authorization Method to set the handler for.
        :param AuthorizationHandler authorizationHandler: The Authorization Handler to set for the specified method.
        """
        if authorizationHandler is None:
            cls.__handlers.pop(authorizationMethod, None)
        else:
            cls.__handlers[authorizationMethod] = authorizationHandler

    @classmethod
    def getAuthorizationHandler(cls, authorizationMethod:AuthorizationMethod) -> AuthorizationHandler|None:
        """
        Gets the :py:class:`~gadeu.handlers.AuthorizationHandler` for the specified :py:class:`~gadeu.AuthorizationMethod`, if any.

        :param AuthorizationMethod authorizationMethod: The Authorization Method to set the handler for.
        :returns: The currently assigned :py:class:`~gadeu.handlers.AuthorizationHandler`, if any. Otherwise ``None``.
        """
        return cls.__handlers.get(authorizationMethod, None)
