"""
Работа с платёжкой.
ЭТИ ДВЕ ФУНКЦИИ НУЖНО ПОДОГНАТЬ ПОД ДОКУМЕНТАЦИЮ ВАШЕГО ПРОВАЙДЕРА:
адрес, формат запроса, имя поля со ссылкой, способ проверки подписи.
"""
import hashlib
import hmac

import aiohttp

import config


async def create_payment_link(order_id: str, amount: float, description: str) -> str:
    if not config.PAY_API_URL:
        raise RuntimeError("PAY_API_URL не заполнен")

    payload = {
        "order_id": order_id,
        "amount": amount,
        "currency": "RUB",
        "description": description,
    }
    if config.PUBLIC_URL:
        payload["webhook_url"] = f"{config.PUBLIC_URL}/webhook"

    headers = {"Authorization": f"Bearer {config.PAY_API_KEY}"}

    async with aiohttp.ClientSession() as session:
        async with session.post(config.PAY_API_URL, json=payload, headers=headers) as resp:
            data = await resp.json()
            return data["payment_url"]  # имя поля зависит от провайдера


def verify_webhook(raw_body: bytes, signature: str) -> bool:
    expected = hmac.new(
        config.PAY_WEBHOOK_SECRET.encode(), raw_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature or "")
