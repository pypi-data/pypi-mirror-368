import asyncio
import socket
import json as js
from time import sleep

import aiohttp
import async_timeout

from .exceptions import (Ipx800v3CannotConnectError, Ipx800v3InvalidAuthError,
                         Ipx800v3RequestError)

class IPX800V3:
    """Class representing the IPX800V3 and its "API".

    Attributes: None
    """

    def __init__(
        self,
        host:str,
        port : int = 80,
        username : str = None,
        password : str = None,
        request_retries: int = 3, 
        request_timeout: int = 5,
        request_checkstatus: bool = True,
        session: aiohttp.client.ClientSession = None
    ) -> None:
        self.host = host
        self.port = port
        self._url = f"http://{self.host}:{self.port}"
        self._username = username
        self._password = password

        self._request_retries = request_retries
        self._request_timeout = request_timeout
        self._request_checkstatus = request_checkstatus


        self._session = session
        self._close_session = False

        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True


    async def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def ping(self) -> bool:
        """simple query to xdevices.json api and check value of return to ping the IPX"""
        response = await self._request(url=f"/api/xdevices.json",params={})
        return response["product"] == "IPX800_V3"

    async def global_get(self) -> dict:
        """Get all values from the IPX800 answer."""
        values = {}
        for i in (10, 20):
            values.update(await self._request(params={"cmd": i}))
            values.pop("product")
        return values

    async def _request(self, url: str = f"/api/xdevices.json", params: dict = {}, json : bool = True):
        auth = None
        if self._username and self._password:
            auth = aiohttp.BasicAuth(self._username, self._password)

        try:
            request_retries = self._request_retries
            while request_retries > 0:
                with async_timeout.timeout(self._request_timeout):
                    response = await self._session.get(
                        f"{self._url}{url}",
                        auth=auth,
                        params=params,
                    )

                if response.status == 401:
                    raise Ipx800v3InvalidAuthError("Auth failed on the IPX800.")

                if response.status:
                    if json:
                        content = js.loads(await response.text())
                    else:
                        content = True
                    response.close()
                    if not self._request_checkstatus or response.status == 200:
                        return content

                request_retries -= 1
                sleep(1)

            raise Ipx800v3RequestError("IPX800 API request error")

        except asyncio.TimeoutError as exception:
            raise Ipx800v3CannotConnectError(
                "Timeout occurred while connecting to IPX800."
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise Ipx800v3CannotConnectError(
                "Error occurred while communicating with the IPX800."
            ) from exception

    async def __aenter__(self):
        """Async enter."""
        return self

    async def __aexit__(self, *_exc_info) -> None:
        """Async exit."""
        await self.close()


class BaseSwitch(IPX800V3):
    """Base class to abstract switch operations."""

    def __init__(self, ipx: IPX800V3, prefix:str, id:int, name:str, cmd:str) -> None:
        super().__init__(host=ipx.host, port=ipx.port, username=ipx._username, password=ipx._password)
        self.id = id
        self._name = name
        self._cmd = cmd
        self._prefix = prefix

    @property
    async def status(self) -> bool:
        """Return the current status."""
        params = {"cmd": self._cmd}
        response = await self._request(params=params)
        return response[f"{self._prefix}{self.id}"] == 1

    async def on(self) -> bool:
        """Turn on and return True if it was successful."""
        params = {f"set{self.id}": 1}
        await self._request(url=f"/preset.htm", params=params, json=False)
        return True

    async def off(self) -> bool:
        """Turn off and return True if it was successful."""
        params = {f"set{self.id}": 0}
        await self._request(url=f"/preset.htm", params=params, json=False)
        return True
    
    async def toggle(self) -> bool:
        """Toggle the output and return True if successful."""
        if self.status == 1:
            await self.off()
        else:
            await self.on()
        return True

    async def __repr__(self) -> str:
        return f"<ipx800.{self._name} id={self.id}>"

    async def __str__(self) -> str:
        return (
            f"[IPX800-{self._name}: id={self.id}, "
            f"status={'On' if self.status else 'Off'}]"
        )


class Output(BaseSwitch):
    """IPX800v3 output"""
    def __init__(self, ipx: IPX800V3, id: int) -> None:
        super().__init__(ipx=ipx, prefix="OUT", id=id, name="output", cmd="20")

class Input(BaseSwitch):
    """ IPX800v3 input"""
    def __init__(self, ipx: IPX800V3, id: int) -> None:
        super().__init__(ipx=ipx, prefix='IN', id=id, name="input", cmd="10")
    
    async def on(self):
        raise NotImplementedError
    
    async def off(self):
        raise NotImplementedError
    
    async def toggle(self):
        raise NotImplementedError


class Analog(IPX800V3):
    """ IPX800v3 input"""
    def __init__(self, ipx: IPX800V3, id: int) -> None:
        super().__init__(host=ipx.host, port=ipx.port, username=ipx._username, password=ipx._password)
        self.id = id
        self._name = "analog"
        self._cmd = "30"
        self._prefix = "AN"

    @property
    async def status(self) -> bool:
        """Return the current status."""
        params = {"cmd": self._cmd}
        response = await self._request(params=params)
        return float(response[f"{self._prefix}{self.id}"])

    async def __str__(self) -> str:
        return (
            f"[IPX800-{self._name}: id={self.id}, "
            f"status={self.status}]"
        )
