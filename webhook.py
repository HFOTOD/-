import json

from aiohttp import web
from aiogram import Bot

import database as db
from payments import verify_webhook


def make_app(bot: Bot) -> web.Application:
    async def webhook(request: web.Request) -> web.Response:
        raw = await request.read()
        signature = request.headers.get("X-Signature", "")  # имя заголовка зависит от провайдера
        if not verify_webhook(raw, signature):
            return web.Response(status=403)

        data = json.loads(raw)
        order_id = data.get("order_id")

        if data.get("status") == "paid":  # значение статуса зависит от провайдера
            payment = db.get_payment(order_id)
            if payment and payment[2] != "paid":
                db.mark_paid(order_id)
                await bot.send_message(payment[0], "✅ Оплата получена, тариф активирован!")
                # здесь выдавайте доступ / подписку
        return web.Response(text="ok")

    async def health(_: web.Request) -> web.Response:
        return web.Response(text="ok")

    app = web.Application()
    app.router.add_post("/webhook", webhook)
    app.router.add_get("/", health)
    return app
