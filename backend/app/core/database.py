from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis
from influxdb_client import InfluxDBClient
import structlog
from typing import Optional

from app.core.config import settings

logger = structlog.get_logger()

# SQLAlchemy setup
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
redis_client: Optional[redis.Redis] = None

# InfluxDB setup
influxdb_client: Optional[InfluxDBClient] = None

async def init_db():
    """Initialize database connections"""
    global redis_client, influxdb_client
    
    try:
        # Initialize Redis
        redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        
        # Test Redis connection
        redis_client.ping()
        logger.info("Redis connection established")
        
        # Initialize InfluxDB
        influxdb_client = InfluxDBClient(
            url=settings.INFLUXDB_URL,
            token=settings.INFLUXDB_TOKEN,
            org=settings.INFLUXDB_ORG
        )
        
        # Test InfluxDB connection
        health = influxdb_client.health()
        if health.status == "pass":
            logger.info("InfluxDB connection established")
        else:
            logger.warning(f"InfluxDB health check failed: {health.message}")
        
        # Create database tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    """Get Redis client"""
    if redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return redis_client

def get_influxdb():
    """Get InfluxDB client"""
    if influxdb_client is None:
        raise RuntimeError("InfluxDB client not initialized")
    return influxdb_client

async def close_db():
    """Close database connections"""
    global redis_client, influxdb_client
    
    if redis_client:
        redis_client.close()
        logger.info("Redis connection closed")
    
    if influxdb_client:
        influxdb_client.close()
        logger.info("InfluxDB connection closed") 