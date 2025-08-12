# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

import enum


class AuthorizationMethod(enum.StrEnum):
    """Identifies the security scheme used for Authorization."""
    APIKEY = 'apiKey'
    """API Key Authorization; An API Key is provided via Header, Cookie, or Query String."""
    # TODO: BASICHTTP = 'basicHttp'
    BEARERTOKEN = 'bearerToken'
    """Bearer Token Authorization; A Bearer Token is provided via ``Authorization`` Header."""
    # TODO: MUTUALTLS = 'mutualTLS'
    # TODO: OAUTH2 = 'oauth2'
    # TODO: OPENID = 'openId'
