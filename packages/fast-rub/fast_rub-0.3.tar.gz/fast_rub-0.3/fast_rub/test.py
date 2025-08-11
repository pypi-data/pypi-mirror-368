from Client import Client,Update
bot=Client("test")
@bot.on_message_updates()
async def main(m:Update):
    print()
bot.run()