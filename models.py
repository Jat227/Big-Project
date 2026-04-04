"""
Async SQLAlchemy models for PostgreSQL.
Falls back gracefully to SQLite for local dev without Docker.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./database.db"   # fallback for local dev without Docker
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    # PostgreSQL pool settings
    **({
        "pool_size": 20,
        "max_overflow": 40,
    } if "postgresql" in DATABASE_URL else {})
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class SearchQuery(Base):
    __tablename__ = "search_queries"
    id         = Column(Integer, primary_key=True, index=True)
    search_term = Column(String, unique=True, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    products   = relationship("Product", back_populates="search", cascade="all, delete-orphan")

    def to_dict(self):
        return {"search_term": self.search_term}

class Product(Base):
    __tablename__ = "products"
    id        = Column(Integer, primary_key=True, index=True)
    search_id = Column(Integer, ForeignKey("search_queries.id"))
    name      = Column(String)
    category  = Column(String)
    image     = Column(String)
    search    = relationship("SearchQuery", back_populates="products")
    prices    = relationship("PricePoint", back_populates="product", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "name": self.name,
            "image": self.image,
            "prices": [p.to_dict() for p in self.prices],
        }

class PricePoint(Base):
    __tablename__ = "price_points"
    id         = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    store      = Column(String)
    price      = Column(Integer)
    logo       = Column(String)
    url        = Column(String)
    product    = relationship("Product", back_populates="prices")

    def to_dict(self):
        return {
            "store": self.store,
            "price": self.price,
            "logo": self.logo,
            "url": self.url,
        }

async def init_db():
    """Create all tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
