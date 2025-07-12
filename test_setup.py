#!/usr/bin/env python3
"""
Test script to verify MLOps Monitoring Platform setup
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_database_connections():
    """Test database connections"""
    print("🔍 Testing database connections...")
    
    try:
        from app.core.database import init_db, get_redis, get_influxdb
        from app.core.config import settings
        
        # Test database initialization
        await init_db()
        print("✅ Database initialization successful")
        
        # Test Redis connection
        redis_client = get_redis()
        redis_client.ping()
        print("✅ Redis connection successful")
        
        # Test InfluxDB connection
        influxdb_client = get_influxdb()
        health = influxdb_client.health()
        if health.status == "pass":
            print("✅ InfluxDB connection successful")
        else:
            print(f"⚠️  InfluxDB health check: {health.message}")
            
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False
    
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        import fastapi
        import sqlalchemy
        import redis
        import influxdb_client
        import prometheus_client
        import structlog
        import pydantic
        print("✅ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {str(e)}")
        return False

def test_config():
    """Test configuration loading"""
    print("🔍 Testing configuration...")
    
    try:
        from app.core.config import settings
        
        print(f"✅ Configuration loaded successfully")
        print(f"   - App Name: {settings.APP_NAME}")
        print(f"   - Database URL: {settings.DATABASE_URL}")
        print(f"   - Redis URL: {settings.REDIS_URL}")
        print(f"   - InfluxDB URL: {settings.INFLUXDB_URL}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return False

def test_models():
    """Test model definitions"""
    print("🔍 Testing model definitions...")
    
    try:
        from app.models.user import User, UserRole
        from app.models.model import Model, ModelStatus, ModelFramework, ModelType
        from app.models.metric import ModelMetric, MetricType, DriftType
        from app.models.alert import Alert, AlertSeverity, AlertStatus, AlertType
        
        print("✅ All models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Model test failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🚀 MLOps Monitoring Platform - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Model Definitions", test_models),
        ("Database Connections", test_database_connections),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Setup is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the setup.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 