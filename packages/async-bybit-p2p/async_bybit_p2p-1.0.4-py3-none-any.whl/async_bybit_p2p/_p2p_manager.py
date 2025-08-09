import asyncio
import base64
import hashlib
import hmac
import json
import os

from ._p2p_method import P2PMethod
import aiohttp
import logging
import aiofiles
from ._exceptions import FailedRequestError
import time
from datetime import datetime as dt, timezone
from json import JSONDecodeError

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

# - *- coding: utf- 8 - *-
from typing import Optional

import aiohttp


_SUBDOMAIN_TESTNET = "api-testnet"
_SUBDOMAIN_MAINNET = "api"
_DOMAIN_MAIN = "bybit"
_DOMAIN_ALT = "bytick"
_TLD_MAIN = "com"


class P2PManager:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        testnet: bool = False,
        recv_window: int = 5000,
        rsa: bool = False,
        alt_domain: bool = False,
        tld: str = "com"
    ):
        self._testnet = testnet
        self._api_key = api_key
        self._api_secret = api_secret
        self._recv_window = recv_window
        self._rsa = rsa
        self._alt_domain = alt_domain

        self._subdomain = _SUBDOMAIN_TESTNET if self._testnet else _SUBDOMAIN_MAINNET
        self._domain = _DOMAIN_ALT if self._alt_domain else _DOMAIN_MAIN
        self._tld = tld
        self._url = f"https://{self._subdomain}.{self._domain}.{self._tld}"

        self._session = aiohttp.ClientSession()

    def _sign(
        self,
        use_rsa_authentication: bool,
        param_str: str,
        binary: bool = False
    ):
        def generate_hmac():
            hash = hmac.new(
                bytes(self._api_secret, "utf-8"),
                param_str.encode("utf-8"),
                hashlib.sha256
            )
            return hash.hexdigest()
        
        def generate_hmac_binary():
            hash = hmac.new(
                bytes(self._api_secret, "utf-8"),
                param_str,
                hashlib.sha256,
            )
            return hash.hexdigest()
        
        def generate_rsa():
            hash = SHA256.new(param_str.encode("utf-8"))
            encoded_signature = base64.b64encode(
                PKCS1_v1_5.new(RSA.importKey(self._api_secret)).sign(
                    hash
                )
            )
            return encoded_signature.decode()
        
        def generate_rsa_binary():
            hash = SHA256.new(param_str)
            encoded_signature = base64.b64encode(
                PKCS1_v1_5.new(RSA.importKey(self._api_secret)).sign(
                    hash
                )
            )
            return encoded_signature.decode()
        
        if not use_rsa_authentication:
            if binary:
                return generate_hmac_binary()
            return generate_hmac()
        else:
            if binary:
                return generate_rsa_binary()
            return generate_rsa()
        
    def _generate_sign(self, payload, timestamp):
        sign_string = str(timestamp) + self._api_key + str(self._recv_window) + payload
        return self._sign(self._rsa, sign_string)
    
    def _generate_sign_binary(self, payload, timestamp):
        sign_string = f"{timestamp}{self._api_key}{self._recv_window}".encode() + payload
        return self._sign(self._rsa, sign_string, True)

    def _cast_values(
        self,
        params
    ):
        str_params = [
            "itemId",
            "side",
            "currency_id",
            # get_ad_detail
            "id",
            "priceType",
            "premium",
            "price",
            "minAmount",
            "maxAmount",
            "remark",
            "actionType",
            "quantity",
            "paymentPeriod",
            # -> tradingPreferenceSet
            "hasUnPostAd",
            "isKyc",
            "isEmail",
            "isMobile",
            "hasRegisterTime",
            "registerTimeThreshold",
            "orderFinishNumberDay30",
            "completeRateDay30",
            "nationalLimit",
            "hasOrderFinishNumberDay30",
            "hasCompleteRateDay30",
            "hasNationalLimit",
            # get_orders
            "beginTime",
            "endTime",
            "tokenId",
            # get chat message
            "startMessageId"
        ]
        int_params = [
            "positionIdx",
        ]

        self._cast_dict_recursively(params, str_params, int_params)

    def _cast_dict_recursively(self, dictionary, str_params, int_params):
        for key, value in dictionary.items():
            if value is None:
                continue
            if isinstance(value, dict):
                self._cast_dict_recursively(value, str_params, int_params)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._cast_dict_recursively(item, str_params, int_params)
                    else:
                        if key in str_params and not isinstance(item, str):
                            value[i] = str(item)
                        elif key in int_params and not isinstance(item, int):
                            value[i] = int(item)
            elif isinstance(value, bool):
                dictionary[key] = value
            else:
                if key in str_params and not isinstance(value, str):
                    dictionary[key] = str(value)
                elif key in int_params and not isinstance(value, int):
                    dictionary[key] = int(value)

    def _generate_payload(
        self,
        http_method: str = "GET",
        params: dict = None
    ):
        http_method = http_method.upper()
        if http_method == "GET":
            payload = "&".join(
                [
                    str(k) + "=" + str(v)
                    for k, v in sorted(params.items())
                    if v is not None
                ]
            )
            return payload
        elif http_method == "POST":
            self._cast_values(params)
            return json.dumps(params)

    def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            new_session = aiohttp.ClientSession()
            self._session = aiohttp.ClientSession()

        return self._session

    async def close_session(self) -> None:
        if self._session is None:
            return None

        await self._session.close()

    async def _request(
        self,
        method: P2PMethod,
        params: dict = {}
    ):
        try:
            missing_params = [p for p in method.required_params if p not in params]
            if missing_params:
                await self.close_session()
                raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")
            
            for i in params.keys():
                if isinstance(params[i], float) and params[i] == int(params[i]):
                    params[i] = int(params[i])

            timestamp = int(time.time() * 10 ** 3)
            contentType = "application/json"

            if method.http_method == "FILE":
                filepath = params["upload_file"]
                boundary = "boundary-for-file"
                contentType = f"multipart/form-data; boundary={boundary}"
                filename = os.path.basename(str(filepath))
                mime_type = "image/png"
                
                async with aiofiles.open(filepath, 'rb') as f:
                    binary_data = await f.read()

                
                payload = (
                    f"--{boundary}\r\n"
                    f"Content-Disposition: form-data; name=\"upload_file\"; filename=\"{filename}\"\r\n"
                    f"Content-Type: {mime_type}\r\n\r\n"
                ).encode() + binary_data + f"\r\n--{boundary}--\r\n".encode()
                signature = self._generate_sign_binary(payload, timestamp)
            else:
                payload = self._generate_payload(
                    method.http_method,
                    params
                )
                signature = self._generate_sign(
                    payload,
                    timestamp
                )

            headers = {
                'X-BAPI-API-KEY': self._api_key,
                'X-BAPI-SIGN': signature,
                'X-BAPI-SIGN-TYPE': '2',
                'X-BAPI-TIMESTAMP': str(timestamp),
                'X-BAPI-RECV-WINDOW': str(self._recv_window),
                'Content-Type': contentType
            }

            endpoint = self._url + method.url

            if method.http_method == "GET":
                response = await self._session.get(
                    endpoint + f"?{payload}" if payload != "" else "",
                    headers=headers,
                )
            elif method.http_method == 'POST' or method.http_method == "FILE":
                response = await self._session.post(
                    endpoint,
                    headers=headers,
                    data=payload
                )
            else:
                return False, f"Unsupported HTTP method: {method.http_method}"
            
            if response.status != 200:
                if response.status == 403:
                    error_msg = "Access denied error. Possible causes: 1) your IP is located in the US or Mainland China, 2) IP banned due to ratelimit violation"
                elif response.status == 401:
                    error_msg = "Unauthorized. Possible causes: 1) incorrect API key and/or secret, 2) incorrect environment: Mainnet vs Testnet"
                else:
                    error_msg = f"HTTP status code is: {response.status}, expected: 200"

                await self.close_session()
                raise FailedRequestError(
                    request=f"{endpoint}: {payload}",
                    message=error_msg,
                    status_code=response.status,
                    time=dt.now(timezone.utc).strftime("%H:%M:%S"),
                    resp_headers=headers,
                )
            
            try:
                response_data = await response.json()
            except JSONDecodeError as ex:
                await self.close_session()
                raise FailedRequestError(
                    request=f"{endpoint}: {payload}",
                    message="Could not decode JSON.",
                    status_code=response.status,
                    time=dt.now(timezone.utc).strftime("%H:%M:%S"),
                    resp_headers=headers,
                )
            
            ret_code = "retCode"
            ret_msg = "retMsg"

            if ret_code not in response_data:
                ret_code = "ret_code"
            if ret_msg not in response_data:
                ret_msg = "ret_msg"

            if response_data[ret_code]:
                error_msg = f"{response_data[ret_msg]} (ErrCode: {response_data[ret_code]})"
                await self.close_session()
                raise FailedRequestError(
                    request=f"{endpoint}: {payload}",
                    message=response_data[ret_msg],
                    status_code=response_data[ret_code],
                    time=dt.now(timezone.utc).strftime("%H:%M:%S"),
                    resp_headers=headers,
                )
            else:
                return response_data
        except Exception as ex:
            print(ex)
            await self.close_session()