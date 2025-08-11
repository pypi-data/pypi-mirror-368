from Client import Client
import asyncio
bot=Client("gdd")
async def main():
    bot.send_file("b0IS2Uw0DAc04aa76508d5d7640fa51f","time.txt","test")
asyncio.run(main())