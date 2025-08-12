# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

import inspect
from typing import Any, Callable, Type, TypeVar, cast

from ..AuthorizationMethod import AuthorizationMethod
from ..AuthorizationManager import AuthorizationManager


METHOD = TypeVar('METHOD', bound=Callable[..., Any])

class apiKey(object):
    """
    Applied to a ``RequestHandler`` method to perform API KEY authorization.
    """

    __target:METHOD

    def __init__(self, target:METHOD) -> None:
        if inspect.isclass(target):
            raise Exception('@apiKey should only be applied to class methods, not classes.')
        self.__target = target

    def __get__(self, instance:Any, owner:Type[Any]) -> METHOD:
        if instance is None:
            return self
        method = lambda *args, **kwargs: self(instance, *args, **kwargs)
        method.__name__ = self.__target.__name__
        return cast(METHOD, method)
    
    def __call__(self, instance:Any, *args:Any, **kwargs:Any) -> Any:
        handler = AuthorizationManager.getAuthorizationHandler(AuthorizationMethod.APIKEY)
        handler.authorize(instance)
        return self.__target(instance, *args, **kwargs)

    @property
    def __wrapped__(self) -> METHOD:
        return self.__target
