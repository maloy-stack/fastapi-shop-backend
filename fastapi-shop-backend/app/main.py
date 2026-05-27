from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, AsyncSessionLocal
from app.models import Product, Base
from app.schemas import PurchaseRequest, PurchaseResponse
from app.redis_client import redis_client
from app.rabbitmq import rabbitmq_publisher
from app.config import RABBITMQ_EXCHANGE

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as session:
        async with session.bind.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        result = await session.execute(select(Product).where(Product.product_id == 42))
        product = result.scalar_one_or_none()
        if not product:
            session.add(Product(product_id=42, stock=1_000_000, description="Тестовый товар"))
            await session.commit()

    await redis_client.initialize()
    # Загружаем сток в Redis, если его там нет

    if not await redis_client.client.exists("product_stock:42"):
        await redis_client.client.set("product_stock:42", 1_000_000)
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/purchase", response_model=PurchaseResponse)
async def purchase(req: PurchaseRequest, db: AsyncSession = Depends(get_db)):
    query = text(
        "UPDATE products "
        "SET stock = stock - :amount "
        "WHERE product_id = :pid AND stock >= :amount "
        "RETURNING stock"
    )
    result = await db.execute(query, {"amount": req.purchased_count, "pid": req.product_id})
    updated = result.scalar_one_or_none()

    if updated is None:
        raise HTTPException(status_code=409, detail="Недостаточно товара на складе")

    await db.commit()

    await rabbitmq_publisher.publish("purchase_events", {
        "user_id": req.user_id,
        "product_id": req.product_id,
        "purchased_count": req.purchased_count,
        "status": "success"
    })

    return PurchaseResponse(status="success")