from aiohttp import ClientSession, FormData
import aiofiles

class NetWork:
    def __init__(self, token: str):
        self.token = token
        self.api = f"https://botapi.rubika.ir/v3/{self.token}/"
        
    async def request(self, method: str, json: dict) -> dict:
        async with ClientSession() as session:
            async with session.post(self.api + method, json=json) as response:
                response.raise_for_status()
                return await response.json()
            
    async def request_upload_file(self, url: str, path: str, name: str) -> str:
        form = FormData()
        form.add_field("file", open(path, "rb"), filename=name, content_type="application/octet-stream")
        async with ClientSession() as session:
            async with session.post(url, data=form) as response:
                response.raise_for_status()
                result = await response.json()
                return result["data"]["file_id"]
            
    async def request_download_file(self, url: str, name: str):
        async with ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                async with aiofiles.open(name, mode="wb") as file:
                    await file.write(await response.read())
                    return {"status": True, "file": name}