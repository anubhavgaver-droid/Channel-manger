import logging
import asyncio
import uvloop
from aiohttp import web, ClientSession
from pyrogram import Client
import config
from admin import register_admin_handlers
from start import register_start_handlers

# High performance loop installation
uvloop.install()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Render Web Server & Self-Ping Keep-Alive Setup ---
routes = web.RouteTableDef()

@routes.get("/")
async def health_check(request):
    return web.Response(text="Bot is running successfully!", status=200)

async def start_web_server():
    web_app = web.Application()
    web_app.add_routes(routes)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", config.PORT)
    await site.start()
    logger.info(f"Web server bound successfully to port {config.PORT}")

async def self_ping():
    """Self-pings the web service to prevent Render from idling/spinning down."""
    await asyncio.sleep(15)
    app_url = f"http://localhost:{config.PORT}"
    while True:
        try:
            async with ClientSession() as session:
                async with session.get(app_url) as resp:
                    if resp.status == 200:
                        logger.info("Self-ping keep-alive successful.")
        except Exception as e:
            logger.debug(f"Self-ping warning: {e}")
        await asyncio.sleep(300) # Ping every 5 minutes

async def main():
    # Initialize Pyrogram Client inside main() where event loop is active
    app = Client(
        "MultiChannelProtectionBot",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN
    )

    # Register handlers inside main loop
    register_admin_handlers(app)
    register_start_handlers(app)

    # Start web server and background keep-alive task
    await start_web_server()
    asyncio.create_task(self_ping())
    
    # Start Telegram Bot
    await app.start()
    logger.info("Bot is active and running with clean modular structure!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped gracefully.")
