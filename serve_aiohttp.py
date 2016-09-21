#!/usr/bin/env python

"""
Minimal example for running an async web server using aiohttp.

Code taken from here:
http://aiohttp.readthedocs.io/en/stable/web.html
"""

from aiohttp import web

async def hello(request):
    return web.Response(body=b"Hello, world")

app = web.Application()
app.router.add_route('GET', '/', hello)

web.run_app(app)
