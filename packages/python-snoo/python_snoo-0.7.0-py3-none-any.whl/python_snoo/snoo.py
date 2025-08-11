# snoo.py
import asyncio
import json
import logging
import secrets
import uuid
from datetime import datetime as dt

import aiohttp
from pubnub.enums import PNReconnectionPolicy
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub_asyncio import PubNubAsyncio

from .containers import (
    AuthorizationInfo,
    SnooDevice,
    SnooStates,
)
from .exceptions import InvalidSnooAuth, SnooAuthException, SnooCommandException, SnooDeviceError
from .pubnub_async import SnooPubNub

_LOGGER = logging.getLogger(__name__)


class Snoo:
    def __init__(self, email, password, clientsession: aiohttp.ClientSession):
        self.email = email
        self.password = password
        self.session = clientsession
        self.aws_auth_url = "https://cognito-idp.us-east-1.amazonaws.com/"
        self.snoo_auth_url = "https://api-us-east-1-prod.happiestbaby.com/us/me/v10/pubnub/authorize"
        self.snoo_devices_url = "https://api-us-east-1-prod.happiestbaby.com/hds/me/v11/devices"
        self.snoo_data_url = "https://happiestbaby.pubnubapi.com"
        self.snoo_baby_url = "https://api-us-east-1-prod.happiestbaby.com/us/me/v10/babies/"
        self.aws_auth_hdr = {
            "x-amz-target": "AWSCognitoIdentityProviderService.InitiateAuth",
            "accept-language": "US",
            "content-type": "application/x-amz-json-1.1",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/4.12.0",
            "accept": "application/json",
        }
        self.aws_refresh_hdr = {
            "accept": "*/*",
            "content-type": "application/x-amz-json-1.1",
            "x-amz-target": "AWSCognitoIdentityProviderService.InitiateAuth",
            "accept-encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
            "user-agent": "Happiest Baby/2.1.6 (com.happiestbaby.hbapp; build:88; iOS 18.3.0) Alamofire/5.9.1",
            "accept-language": "en-US;q=1.0",
            "content-length": "1895",
        }
        self.snoo_auth_hdr = {
            "accept-language": "US",
            "content-type": "application/json; charset=UTF-8",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/4.12.0",
            "accept": "application/json",
        }

        self.aws_auth_data = {
            "AuthParameters": {
                "PASSWORD": self.password,
                "USERNAME": self.email,
            },
            "AuthFlow": "USER_PASSWORD_AUTH",
            "ClientId": "6kqofhc8hm394ielqdkvli0oea",
        }
        self.snoo_auth_data = {
            "advertiserId": "",
            "appVersion": "1.8.7",
            "device": "panther",
            "deviceHasGSM": True,
            "locale": "en",
            "os": "Android",
            "osVersion": "14",
            "platform": "Android",
            "timeZone": "America/New_York",
            "userCountry": "US",
            "vendorId": "eyqurgwYQSqmnExnzyiLO5",
        }

        self.aws_auth_data = json.dumps(self.aws_auth_data)
        self.snoo_auth_data = json.dumps(self.snoo_auth_data)
        self.tokens: AuthorizationInfo | None = None
        self.pubnub = None
        self.subscription_functions = {}
        self.data_map = {}
        self.pubnub_instances: dict[str, SnooPubNub] = {}
        self.reauth_task: asyncio.Task | None = None

    async def refresh_tokens(self):
        # TODO: Figure out hwo to get this to work and not do a serializaiton exception
        data = {
            "AuthParameters": {"REFRESH_TOKEN": self.tokens.aws_refresh},
            "AuthFlow": "REFRESH_TOKEN_AUTH",
            "ClientId": "6kqofhc8hm394ielqdkvli0oea",
        }
        r = await self.session.post(self.aws_auth_url, data=data, headers=self.aws_auth_hdr)
        resp = await r.json(content_type=None)
        if "__type" in resp and resp["__type"] == "NotAuthorizedException":
            raise InvalidSnooAuth()
        result = resp["AuthenticationResult"]
        self.tokens = AuthorizationInfo(aws_id=result[""])

    def check_tokens(self):
        if self.tokens is None:
            raise Exception("You need to authenticate before you continue")

    def generate_snoo_auth_headers(self, amz_token):
        hdrs = self.snoo_auth_hdr.copy()
        hdrs["authorization"] = f"Bearer {amz_token}"
        return hdrs

    def generate_snoo_data_url(self, device_id, snoo_token):
        if isinstance(device_id, float):
            device_id = str(int(device_id))
        req_uuid = uuid.uuid1()
        dev_uuid = uuid.uuid1()
        app_dev_id_len = 24
        n = app_dev_id_len * 3 // 4
        app_dev_id = secrets.token_urlsafe(n)
        url = f"https://happiestbaby.pubnubapi.com/v2/history/sub-key/sub-c-97bade2a-483d-11e6-8b3b-02ee2ddab7fe/channel/ActivityState.{device_id}?pnsdk=PubNub-Kotlin%2F7.4.0&l_pub=0.064&auth={snoo_token}&requestid={req_uuid}&include_token=true&count=1&include_meta=false&reverse=false&uuid=android_{app_dev_id}_{dev_uuid}"
        return url

    def generate_id(self):
        app_dev_id_len = 24
        n = app_dev_id_len * 3 // 4
        app_dev_id = secrets.token_urlsafe(n)
        return app_dev_id

    async def subscribe(self, device: SnooDevice, function):
        pnconfig = PNConfiguration()
        pnconfig.subscribe_key = "sub-c-97bade2a-483d-11e6-8b3b-02ee2ddab7fe"
        pnconfig.publish_key = "pub-c-699074b0-7664-4be2-abf8-dcbb9b6cd2bf"
        pnconfig.user_id = secrets.token_urlsafe(16)
        pnconfig.auth_key = self.tokens.snoo
        pnconfig.reconnect_policy = PNReconnectionPolicy.EXPONENTIAL
        self.pubnub = PubNubAsyncio(pnconfig)
        device_id = device.serialNumber

        if device_id not in self.pubnub_instances:
            self.pubnub_instances[device_id] = SnooPubNub(self.pubnub, device_id)
        pubnub_instance = self.pubnub_instances[device_id]
        unsub = pubnub_instance.subscribe(function)
        asyncio.create_task(pubnub_instance.run())
        return unsub

    async def disconnect(self):
        for pubnub_instance in self.pubnub_instances.values():
            if pubnub_instance.task:
                pubnub_instance.task.cancel()
                try:
                    await pubnub_instance.task
                except asyncio.CancelledError:
                    pass
        self.pubnub_instances = {}
        self.reauth_task.cancel()

    def publish_callback(self, result, status):
        if status.is_error():
            _LOGGER.warning(f"Message failed with {status.status_code}, {status.error_data.__dict__}")

    async def send_command(self, command: str, device: SnooDevice, **kwargs):
        ts = int(dt.now().timestamp() * 10_000_000)
        try:
            await (
                self.pubnub.publish()
                .channel(f"ControlCommand.{device.serialNumber}")
                .message({"ts": ts, "command": command, **kwargs})
                .future()
            )
        except Exception as e:
            raise SnooCommandException from e

    async def start_snoo(self, device: SnooDevice):
        await self.send_command("start_snoo", device)

    async def stop_snoo(self, device: SnooDevice):
        await self.send_command("go_to_state", device, **{"state": "ONLINE", "hold": "off"})

    async def set_level(self, device: SnooDevice, level: SnooStates, hold: bool = False):
        if hold:
            hold = "on"
        else:
            hold = "off"

        await self.send_command("go_to_state", device, **{"state": level.value, "hold": hold})

    async def set_sticky_white_noise(self, device: SnooDevice, on: bool):
        await self.send_command(
            "set_sticky_white_noise",
            device,
            **{"state": "on" if on else "off", "timeout_min": 15},
        )

    async def get_status(self, device: SnooDevice):
        await self.send_command("send_status", device)

    async def auth_amazon(self):
        r = await self.session.post(self.aws_auth_url, data=self.aws_auth_data, headers=self.aws_auth_hdr)
        resp = await r.json(content_type=None)
        if "__type" in resp and resp["__type"] == "NotAuthorizedException":
            raise InvalidSnooAuth()
        result = resp["AuthenticationResult"]
        return result

    async def auth_snoo(self, id_token):
        hdrs = self.generate_snoo_auth_headers(id_token)
        r = await self.session.post(self.snoo_auth_url, data=self.snoo_auth_data, headers=hdrs)
        return await r.json()

    async def authorize(self) -> AuthorizationInfo:
        try:
            amz = await self.auth_amazon()
            access = amz["AccessToken"]
            _id = amz["IdToken"]
            ref = amz["RefreshToken"]
            snoo_token = await self.auth_snoo(_id)
            snoo_expiry = snoo_token["expiresIn"] / 1.5
            snoo_token = snoo_token["snoo"]["token"]
            self.tokens = AuthorizationInfo(snoo=snoo_token, aws_access=access, aws_id=_id, aws_refresh=ref)
            self.reauth_task = asyncio.create_task(self.schedule_reauthorization(snoo_expiry))
        except InvalidSnooAuth as ex:
            raise ex
        except Exception as ex:
            raise SnooAuthException from ex
        return self.tokens

    async def schedule_reauthorization(self, snoo_expiry: int):
        _LOGGER.info("Snoo token has expired - reauthorizing...")
        try:
            await asyncio.sleep(snoo_expiry)
            await self.authorize()
            for instance in self.pubnub_instances.values():
                instance.update_token(self.tokens.snoo)
            self.pubnub.config.auth_token = self.tokens.snoo

        except Exception as ex:
            _LOGGER.exception(f"Error during reauthorization: {ex}")

    async def get_devices(self) -> list[SnooDevice]:
        hdrs = self.generate_snoo_auth_headers(self.tokens.aws_id)
        try:
            r = await self.session.get(self.snoo_devices_url, headers=hdrs)
            resp = await r.json()
        except Exception as ex:
            raise SnooDeviceError from ex
        devs = [SnooDevice.from_dict(dev) for dev in resp["snoo"]]
        return devs

    # lowest = 'lvl-2'
    # low='lvl-1'
    # normal='lvl10'
    # high='lvl+1'
    # highest='lvl+2'
    #
    #
    # soothing
    # normal='lvl10'
    # high='lvl+1'
    # highest='lvl+2'
