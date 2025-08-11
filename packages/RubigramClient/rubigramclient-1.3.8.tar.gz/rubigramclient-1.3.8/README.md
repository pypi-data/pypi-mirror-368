# Rubigram
A lightweight Python library to build Rubika bots easily.

## Installation
```bash
pip install RubigramClient
```
## Example
```python
from rubigram import Client, filters
from rubigram.types import Update

bot = Client("your_bot_token", "you_endpoint_url")

@bot.on_message(filters.command("start"))
async def start_handler(client, message: Update):    
    await message.reply("Hi, WELCOME TO RUBIGRAM")

bot.run()
```