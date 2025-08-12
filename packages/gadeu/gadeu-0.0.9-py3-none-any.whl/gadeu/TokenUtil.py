# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

import os
from typing import Any
import base58
import hashlib
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

from .AuthorizationMethod import AuthorizationMethod


class TokenUtil:
    """A class that can Create and Verify cryptographically secure tokens."""

    def __init__(cls) -> None:
        pass

    @classmethod
    def __createAesKey(cls) -> str:        
        key = os.urandom(32)
        return base58.b58encode(key).decode()

    @classmethod
    def __createJwk(cls) -> str:
        import jwcrypto.jwk as jwk
        jkey = jwk.JWK(generate='oct', size=256)
        key:str = jkey.export()
        return base58.b58encode(key).decode()

    @classmethod
    def __createApiKeyToken(cls, key:bytes, claims:dict[str,Any]) -> str:
        blockSizeBits = 128
        blockSizeBytes = int(blockSizeBits/8)
        iv = hashlib.shake_128(key, usedforsecurity=True).digest(blockSizeBytes)
        cbc = Cipher(algorithms.AES256(key), modes.CBC(iv)).encryptor()
        padder = padding.PKCS7(blockSizeBits).padder()
        input = padder.update(json.dumps(claims).encode()) + padder.finalize()
        output = cbc.update(input) + cbc.finalize()
        result = base58.b58encode(output).decode()
        mid = int(len(result)/2)
        return result[0:mid] + '.' + result[mid:]

    @classmethod
    def __createBearerToken(cls, key:bytes, claims:dict[str,Any]) -> str:
        import jwcrypto.jwk as jwk
        import jwcrypto.jwt as jwt
        jkey = jwk.JWK(**json.loads(key))
        stoken = jwt.JWT(header={'alg':'HS256'}, claims=claims)
        stoken.make_signed_token(jkey)
        etoken = jwt.JWT(header={'alg':'A256KW', 'enc':'A256CBC-HS512'}, claims=stoken.serialize())
        etoken.make_encrypted_token(jkey)
        return etoken.serialize()

    @classmethod
    def __getApiKeyTokenClaims(cls, key:bytes, token:str) -> dict[str,Any]:
        blockSizeBits = 128
        blockSizeBytes = int(blockSizeBits/8)
        buf = base58.b58decode(token.replace('.',''))
        iv = hashlib.shake_128(key, usedforsecurity=True).digest(blockSizeBytes)
        cbc = Cipher(algorithms.AES256(key), modes.CBC(iv)).decryptor()
        output = cbc.update(buf) + cbc.finalize()
        unpadder = padding.PKCS7(blockSizeBits).unpadder()
        result = unpadder.update(output) + unpadder.finalize()
        return json.loads(result)

    @classmethod
    def __getBearerTokenClaims(cls, key:bytes, token:str) -> str:
        import jwcrypto.jwk as jwk
        import jwcrypto.jwt as jwt
        jkey = jwk.JWK(**json.loads(key))
        etoken = jwt.JWT(key=jkey, jwt=token, expected_type='JWE')
        stoken = jwt.JWT(key=jkey, jwt=etoken.claims)
        return json.loads(stoken.claims)

    @classmethod
    def createSecretKey(cls, authorizationMethod:AuthorizationMethod) -> str:
        """
        Creates a SECRET KEY required for encryption (and signing) of TOKENS.
        
        A SECRET KEY should not be shared, typically stored to a key vault for applications that need to securely access it for performing TOKEN verification.

        :param authorizationMethod: The :py:class:`~gadeu.AuthorizationMethod` to create a SECRET KEY for. Keys are generally not portable between security schemes.
        :return str: An encoded string that can be stored in JSON, XML, etc without additional encoding.
        """
        match authorizationMethod:
            case AuthorizationMethod.APIKEY:
                return cls.__createAesKey()
            case AuthorizationMethod.BEARERTOKEN:
                return cls.__createJwk()
            case _:
                raise Exception(f'Unsupported authorizationMethod "{authorizationMethod}"')

    @classmethod
    def createToken(cls, secretKey:bytes|str, claims:dict[str,Any], authorizationMethod:AuthorizationMethod) -> str:
        """
        Creates a TOKEN required for authorization of applications and/or users.

        A TOKEN can be shared with the individual or organization it is created for.

        :param bytes|str secretKey: The SECRET KEY used for encryption (and signing) of the TOKEN.
        :param dict[str,Any] claims: The Claims to be stored within the token. Claims are always encrypted.
        :param authorizationMethod: The :py:class:`~gadeu.AuthorizationMethod` to create the TOKEN for. Tokens are generally not portable between security schemes.
        :return str: A token formatted as-expected for the specified Authorization Method. For example, for ``bearerToken`` auth the result is a serialized JWT.
        """
        if type(secretKey) is str:
            secretKey = base58.b58decode(secretKey.encode())
        match authorizationMethod:
            case AuthorizationMethod.APIKEY:
                return cls.__createApiKeyToken(secretKey, claims)
            case AuthorizationMethod.BEARERTOKEN:
                return cls.__createBearerToken(secretKey, claims)
            case _:
                raise Exception(f'Unsupported authorizationMethod "{authorizationMethod}"')

    @classmethod
    def getTokenClaims(cls, secretKey:bytes|str, token:str, authorizationMethod:AuthorizationMethod) -> dict[str,Any]:
        """
        Given a SECRET KEY and a TOKEN, returns the Claims contained within the token.

        :param bytes|str secretKey: The SECRET KEY to use for token decryption (and signature verification).
        :param str token: The TOKEN to be decrypted and inspected for Claims.
        :param authorizationMethod: The :py:class:`~gadeu.AuthorizationMethod` the TOKEN was created for.
        :return dict[str,Any]: A dictionary containing the Claims as key-value pairs.
        """
        if type(secretKey) is str:
            secretKey = base58.b58decode(secretKey.encode())
        match authorizationMethod:
            case AuthorizationMethod.APIKEY:
                return cls.__getApiKeyTokenClaims(secretKey, token)
            case AuthorizationMethod.BEARERTOKEN:
                return cls.__getBearerTokenClaims(secretKey, token)
            case _:
                raise Exception(f'Unsupported authorizationMethod "{authorizationMethod}"')
