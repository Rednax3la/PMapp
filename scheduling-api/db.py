# scheduling-api/db.py
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import os
from urllib.parse import quote_plus
import sys

# MongoDB Atlas Configuration
MONGO_USERNAME = os.environ.get("MONGO_USERNAME", "wambugualexander09")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", "Fy86KJ5m6CuucR5P")
MONGO_CLUSTER = os.environ.get("MONGO_CLUSTER", "cluster0.lumzvbr.mongodb.net")
MONGO_DATABASE = os.environ.get("MONGO_DATABASE", "zainpm_db")

# Construct MongoDB Atlas URI
def get_mongo_uri():
    """Construct MongoDB Atlas connection string"""
    if MONGO_USERNAME and MONGO_PASSWORD and MONGO_CLUSTER:
        # URL encode credentials to handle special characters
        username = quote_plus(MONGO_USERNAME)
        password = quote_plus(MONGO_PASSWORD)
        
        # Full Atlas connection string
        uri = f"mongodb+srv://{username}:{password}@{MONGO_CLUSTER}/{MONGO_DATABASE}?retryWrites=true&w=majority&appName=ZainPM"
        return uri
    else:
        # Fallback (shouldn't happen with our hardcoded values)
        return "mongodb://localhost:27017"

def create_mongo_client():
    """Create MongoDB client with proper error handling for Atlas"""
    mongo_uri = get_mongo_uri()
    
    try:
        print("🔄 Connecting to MongoDB Atlas...")
        print(f"📍 Cluster: {MONGO_CLUSTER}")
        print(f"🗄️  Database: {MONGO_DATABASE}")
        
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=10000,  # 10 seconds
            connectTimeoutMS=20000,          # 20 seconds  
            socketTimeoutMS=30000,           # 30 seconds
            retryWrites=True,
            w='majority'
        )
        
        # Test the connection
        print("🧪 Testing connection...")
        client.admin.command('ping')
        
        # Get server info
        server_info = client.server_info()
        print(f"✅ Successfully connected to MongoDB Atlas!")
        print(f"📊 MongoDB Version: {server_info.get('version', 'Unknown')}")
        
        return client
        
    except ServerSelectionTimeoutError as e:
        print(f"❌ MongoDB Atlas Connection Timeout: {e}")
        print("💡 Troubleshooting tips:")
        print("   1. Check your internet connection")
        print("   2. Verify your MongoDB Atlas cluster is running")
        print("   3. Check if your IP address is whitelisted in Atlas")
        print("   4. Verify username and password are correct")
        sys.exit(1)
        
    except ConnectionFailure as e:
        print(f"❌ MongoDB Atlas Connection Failed: {e}")
        print("💡 Possible issues:")
        print("   1. Invalid credentials")
        print("   2. Cluster not accessible")
        print("   3. Network firewall blocking connection")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected MongoDB Atlas error: {e}")
        print(f"🔗 Connection URI (credentials hidden): mongodb+srv://***:***@{MONGO_CLUSTER}/{MONGO_DATABASE}")
        sys.exit(1)

# Initialize MongoDB Atlas client
client = create_mongo_client()

# Database and Collections
db = client[MONGO_DATABASE]
users_col = db['users']
projects_col = db['projects']
tasks_col = db['tasks']
updates_col = db['updates']
project_updates_col = db['project_updates']

# Create indexes for better performance
def create_indexes():
    """Create database indexes for optimal performance"""
    try:
        print("🔧 Creating database indexes...")
        
        # Users collection indexes
        users_col.create_index("username", unique=True)
        users_col.create_index("company_name")
        
        # Projects collection indexes
        projects_col.create_index([("company_name", 1), ("name", 1)], unique=True)
        projects_col.create_index("company_name")
        projects_col.create_index("start_date")
        
        # Tasks collection indexes
        tasks_col.create_index([("project_id", 1), ("name", 1)], unique=True)
        tasks_col.create_index("project_id")
        tasks_col.create_index("start_time")
        tasks_col.create_index("members")
        
        # Updates collection indexes
        updates_col.create_index("task_id")
        updates_col.create_index("timestamp")
        
        # Project updates collection indexes
        project_updates_col.create_index("project_id")
        project_updates_col.create_index("timestamp")
        
        print("✅ Database indexes created successfully!")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not create indexes: {e}")

def ping():
    """Test database connection"""
    try:
        result = client.admin.command('ping')
        return {
            "status": "success", 
            "message": "MongoDB Atlas is connected", 
            "cluster": MONGO_CLUSTER,
            "database": MONGO_DATABASE,
            "result": result
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"MongoDB Atlas connection failed: {str(e)}",
            "cluster": MONGO_CLUSTER
        }

def get_db_stats():
    """Get database statistics"""
    try:
        stats = db.command("dbStats")
        collections_info = []
        
        # Get info about each collection
        for collection_name in db.list_collection_names():
            collection = db[collection_name]
            count = collection.count_documents({})
            collections_info.append({
                "name": collection_name,
                "documents": count
            })
        
        return {
            "database": stats.get("db"),
            "collections": collections_info,
            "total_collections": stats.get("collections", 0),
            "total_objects": stats.get("objects", 0),
            "dataSize": f"{stats.get('dataSize', 0) / 1024 / 1024:.2f} MB",
            "storageSize": f"{stats.get('storageSize', 0) / 1024 / 1024:.2f} MB"
        }
    except Exception as e:
        return {"error": str(e)}

def check_atlas_connection():
    """Comprehensive Atlas connection check"""
    print("\n" + "="*50)
    print("🔍 MONGODB ATLAS CONNECTION CHECK")
    print("="*50)
    
    # 1. Test ping
    ping_result = ping()
    if ping_result["status"] == "success":
        print("✅ Connection: OK")
    else:
        print(f"❌ Connection: FAILED - {ping_result['message']}")
        return False
    
    # 2. Test database operations
    try:
        # Try to insert a test document
        test_collection = db['connection_test']
        test_doc = {"test": True, "timestamp": "2024-01-01"}
        result = test_collection.insert_one(test_doc)
        print(f"✅ Write Test: OK (ID: {result.inserted_id})")
        
        # Try to read the document
        found_doc = test_collection.find_one({"_id": result.inserted_id})
        if found_doc:
            print("✅ Read Test: OK")
        
        # Clean up test document
        test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Delete Test: OK")
        
    except Exception as e:
        print(f"❌ Database Operations: FAILED - {e}")
        return False
    
    # 3. Show database stats
    stats = get_db_stats()
    if "error" not in stats:
        print(f"📊 Database: {stats['database']}")
        print(f"📦 Collections: {stats['total_collections']}")
        print(f"📄 Documents: {stats['total_objects']}")
        print(f"💾 Data Size: {stats['dataSize']}")
    
    print("="*50)
    print("🎉 MongoDB Atlas is ready for ZainPM!")
    print("="*50 + "\n")
    return True

# Initialize indexes on startup
if __name__ == "__main__":
    create_indexes()
    check_atlas_connection()
else:
    # Create indexes when module is imported
    try:
        create_indexes()
    except Exception as e:
        print(f"⚠️  Could not create indexes on import: {e}")

# Export collections for easy importing
__all__ = [
    'client', 'db', 'users_col', 'projects_col', 'tasks_col', 
    'updates_col', 'project_updates_col', 'ping', 'get_db_stats'
]