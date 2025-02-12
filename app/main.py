from contextlib import asynccontextmanager
from app.bot.create_bot import dp, start_bot, bot, stop_bot
from app.config import settings, broker
from aiogram.types import Update
from fastapi import FastAPI, Request
from loguru import logger
from app.api.router import router as router_fast_stream

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting bot setup...")
    await start_bot()
    await broker.start()
    webhook_url = settings.hook_url
    await bot.set_webhook(url=webhook_url,
                          allowed_updates=dp.resolve_used_update_types(),
                          drop_pending_updates=True)
    logger.success(f"Webhook set to {webhook_url}")
    yield
    logger.info("Shutting down bot...")
    # await bot.delete_webhook()
    await stop_bot()
    await broker.stop()
    # logger.info("Webhook deleted")


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def webhook(request: Request) -> None:
    logger.info("Received webhook request")
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    logger.info("Update processed")


app.include_router(router_fast_stream)