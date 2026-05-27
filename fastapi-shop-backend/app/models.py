from sqlalchemy import Column, Integer, String, CheckConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, autoincrement=False)
    stock = Column(Integer, nullable=False)
    description = Column(String)

    __table_args__ = (
        CheckConstraint("stock >= 0", name="check_stock_non_negative"),
    )