from rubigram.types import Update, InlineMessage
from rubigram.method import Method
from aiohttp import web


class Client(Method):
    def __init__(self, token: str, endpoint: str = None, host: str = "0.0.0.0", port: int = 8000):
        self.token = token
        self.port = port
        self.host = host
        self.endpoint = endpoint
        self.messages_handler = []
        self.inlines_handler = []
        self.routes = web.RouteTableDef()
        self.api = f"https://botapi.rubika.ir/v3/{self.token}/"
        super().__init__(token)

    
    def on_message(self, *filters):
        def decorator(func):
            async def wrapper(client, update):
                if all(f(update) for f in filters):
                    await func(client, update)
            self.messages_handler.append(wrapper)
            return func
        return decorator
    
    def on_inline_message(self, *filters):
        def decorator(func):
            async def wrapper(client, update):
                if all(f(update) for f in filters):
                    await func(client, update)
            self.inlines_handler.append(wrapper)
            return func
        return decorator
    
    async def update(self, data: dict):
        if "inline_message" in data:
            event = InlineMessage.read(data["inline_message"])
            for handler in self.inlines_handler:
                await handler(self, event)
        else:
            event = Update.read(data["update"], self)
            for handler in self.messages_handler:
                await handler(self, event)
    
    async def set_endpoints(self):
        await self.update_bot_endpoint(self.endpoint + "/ReceiveUpdate", "ReceiveUpdate")
        await self.update_bot_endpoint(self.endpoint + "/ReceiveInlineMessage", "ReceiveInlineMessage")

    def run(self):
        @self.routes.post("/ReceiveUpdate")
        async def receive_update(request):
            data = await request.json()
            await self.update(data)
            return web.json_response({"status": "OK"})

        @self.routes.post("/ReceiveInlineMessage")
        async def receive_inline_message(request):
            data = await request.json()
            await self.update(data)
            return web.json_response({"status": "ok"})

        app = web.Application()
        app.add_routes(self.routes)

        async def on_startup(app):
            if self.endpoint:
                await self.set_endpoints()

        app.on_startup.append(on_startup)
        web.run_app(app, host = self.host, port = self.port)