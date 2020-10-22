from aiohttp import ClientSession

async def call_api(url, payload):
    async with ClientSession() as session:
        data = {'text':str(payload)}
        async with session.post(url, json=data) as response:
            print(response.status)
            return await response.text()


async def call_bot(botToken, chatId, payload):
    async with ClientSession() as session:
        data = {'chat_id':chatId, 'text':str(payload)}
        async with session.post('https://api.telegram.org/bot%s/sendMessage' % (botToken), json=data) as response:
            print(response.status)
            return await response.text()