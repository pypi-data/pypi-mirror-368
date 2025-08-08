IPX800V3
==========

A python library to control a IPX800 V3 device build by GCE-Electronics through its light "API".

* Python 3.8+ support
* WTFPL License

IPX800V3 features implemented
---------------------------

* Control:

  - outputs (``ipx.outputs[]``)
  - inputs (``ipx.intputs[]``)
  - analogs (``ipx.analogs[]``)

Installation
------------

.. code-block:: console

    > pip install pyipx800v3_async

Usage
-----

.. code-block:: python

    import asyncio

    from pyipx800v3_async import IPX800V3

    async def main():
        async with IPX800V3(host="127.0.0.1", port=80, username="username", password="password") as ipx:
            print(await ipx.ping())

            data = await ipx.global_get()
            print(data)
            
            out1 = Output(ipx=ipx, id=1)
            print(out1.id)
            print(await out1.status)
            await out1.on()
            await asyncio.sleep(1)
            print(await out1.status)
            await out1.off()
            await asyncio.sleep(1)
            print(await out1.status)

            in1 = Input(ipx=ipx, id=1)
            print(await in1.status)

            an1 = Analog(ipx=ipx, id=1)
            print(await an1.value)

Links
-----

* GCE IPX800V3 API: https://download.gce-electronics.com/data/007_IPX800_V3/IPX_API.pdf

Licence
-------

Licensed under WTFPL License
