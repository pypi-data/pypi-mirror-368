
[![gadeu on PyPI](https://img.shields.io/pypi/v/gadeu.svg)](https://pypi.org/project/gadeu/) [![gadeu on readthedocs](https://readthedocs.org/projects/gadeu/badge/?version=latest)](https://gadeu.readthedocs.io)

**gadeu** (가드) is a decorative auth library for [Tornado](https://www.tornadoweb.org).

This README is only a high-level introduction to **gadeu**. For more detailed documentation, please view the official docs at [https://gadeu.readthedocs.io](https://gadeu.readthedocs.io).

## Installation

You can install ``gadeu`` from [PyPI](https://pypi.org/project/gadeu/) through usual means, such as ``pip``:

```bash

   pip install gadeu
```

## Usage

To use ``gadeu`` two things must be done; first you must register at least one authorization handler, and second you must apply one of the authorization decorators to a request handler method. Consider the following example:

```python

    import tornado
    from gadeu import *
    from .api.FakeApi import FakeApi

    # you configure an authorization handler
    AuthorizationManager.setAuthorizationHandler(
        AuthorizationMethod.APIKEY,
        handlers.ApiKeyAuthorizationHandler(key=apiKeySecret)
    )

    # you create a tornado app
    app = tornado.web.Application()
    # you add some handlers for your app
    app.add_handlers('.*', [
        (r'/api/v2/fakes', FakeApi),
        (r'/api/v2/fakes/(?P<id>\d+)', FakeApi),
        (r'/api/v2/fakes/(?P<name>[\dA-Za-z]+)', FakeApi),
        (r'/api/v2/fakes/(?P<id>\d+)/(?P<name>[^/][\dA-Za-z]+)', FakeApi)
    ])
```

Elsewhere in your project, you defined `FakeApi` and decorated at least one handler:

```python

    import tornado
    from gadeu import authorization

    class FakeApi(tornado.web.RequestHandler):    

        def initialize(self) -> None:
            pass

        @authorization.apiKey
        async def put(self, id:str, name:str) -> None:
            _d[id] = name
            self.set_status(204)
```

In the above example, ``FakeApi.put`` has been decorated with ``@authorization.apiKey`` which will force a check for a valid API Key. The expectations of that check are implemented via the ``ApiKeyAuthorizationHandler`` configured in the first few lines of the example. There are more options than are shown here, but this basic setup is enough for a server to check for a valid API Key.

If you need to generate an encryption key there is a ``TokenUtil`` class that exposes a ``createSecretKey(...)`` method which you can use for this purpose, example:

```python

    from gadeu import *

    # never share this key! it should get stored to a keyvault and
    # managed securely as part of your app settings.
    secretKey = TokenUtil.createSecretKey(AuthorizationMethod.APIKEY)
```

You can also use ``TokenUtil`` to generate API Keys using your secret key.

```python

    # share this token securely with your business partners, developers,
    # testers, etc that need to authorize requests with a server.
    apiKey = TokenUtil.createToken(secretKey, {'app':'bob123'}, AuthorizationMethod.APIKEY)
```

In the above example you can see a dictionary ``{'app':'bob123'}``, this is a "claims object" that gets encoded into the resulting token (``apiKey``). See the section below **Checking Claims** for more information on how they can be accessed.

Currently, only ``apiKey`` and ``bearerToken`` security schemes are supported, with a plan to add others as they are requested, PR'd, or required for our own projects. Both ``apiKey`` and ``bearerToken`` tokens are encrypted, and unless you leak your secret keys the wider public should not be able to peek at the token contents (ie. the "claims" you've stored.) That said, it is NOT a good practice to store anything sensitive in a claim (such as keys, passwords, etc.)

### Custom/Proprietary Authorization Methods

You can subclass ``AuthorizationHandler`` to implement custom behavior. You are encouraged to submit a PR if you find yourself implementing any well known security schemes such as:

* mutualTLS
* OAuth2
* openIdConnect

Since we do not currently use these schemes there are not yet handlers for them, despite their popularity.

### Checking Claims

In the future there will be decorators to facilitate claims assertions.

In the current implementation you can check claims "globally" from a custom ``validator`` function, or "locally" within your handler methods. Example:

```python

    # you configure an authorization handler
    AuthorizationManager.setAuthorizationHandler(
        AuthorizationMethod.APIKEY,
        handlers.ApiKeyAuthorizationHandler(
            key=apiKeySecret,
            validator=lambda token,claims: claims.get('has_api_access', False) == True
        )
    )

    # elsewhere, you decorate your services, and check claims
    class FakeApi(tornado.web.RequestHandler):    

        @authorization.apiKey
        async def put(self, id:str, name:str) -> None:
            claims = self.request.arguments.get('claims', None)
            if claims.get('can_edit', False) != True:
                raise tornado.web.HTTPError(403)
            # do stuff

```

If ``claims`` is an argument name you already use (and therefore would be clobbered by ``gadeu``) then you can configure a custom argument name in your ``AuthorizationHandler``. Example:

```python

    AuthorizationManager.setAuthorizationHandler(
        AuthorizationMethod.APIKEY,
        handlers.ApiKeyAuthorizationHandler(
            key=secretKey,
            claimsArgumentName='my_epic_arg_name')
    )
```

Lastly, ``TokenUtil`` can be used directly against a token to check claims. This may be useful for non-standard scenarios (token passing over a websocket connection for example), or if you are building user-tools for managing and verifying tokens. Example:

```python

    secretKey = TokenUtil.createSecretKey(AuthorizationMethod.APIKEY)
    token = TokenUtil.createToken(
        secretKey, 
        { 'id':123, 'ts':datetime.now().isoformat() },
        AuthorizationMethod.APIKEY)
    claims = TokenUtil.getTokenClaims(
        secretKey,
        token,
        AuthorizationMethod.APIKEY)
    print(claims)

    # outputs:
    #
    # {'id': 123, 'ts': '2025-05-10T17:58:41.048820'}
    #

```

## Contact

You can reach me on [Discord](https://discordapp.com/users/307684202080501761) or [open an Issue on Github](https://github.com/wilson0x4d/gadeu/issues/new/choose).
