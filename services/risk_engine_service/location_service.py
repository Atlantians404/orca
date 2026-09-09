from typing import Dict, List 
 
import os 
from concurrent.futures import ThreadPoolExecutor 
 
from dotenv import load_dotenv 
from pymongo import MongoClient 
 
 
load_dotenv() 
 
MONGO_URI = os.getenv("MONGO_URI") 
 
if not MONGO_URI: 
    raise ValueError("MONGO_URI is not set in .env") 
 
 
client = MongoClient( 
    MONGO_URI, 
    maxPoolSize=20 
) 
 
db = client["ORCA"] 
 
collection = db["district_boundaries"] 
 
 
def find_location(node): 
    node_id = node["node_id"] 
 
    latitude = node["latitude"] 
    longitude = node["longitude"] 
 
    point = { 
        "type": "Point", 
        "coordinates": [ 
            longitude, 
            latitude 
        ] 
    } 
 
    district = collection.find_one( 
        { 
            "geometry": { 
                "$geoIntersects": { 
                    "$geometry": point 
                } 
            } 
        }, 
        { 
            "_id": 0, 
            "district": 1, 
            "state": 1 
        } 
    ) 
 
    if district: 
        return node_id, { 
            "district": district.get("district"), 
            "state": district.get("state") 
        } 
 
    return node_id, { 
        "district": None, 
        "state": None 
    } 
 
 
async def get_locations_batch(nodes: List[dict]) -> Dict[str, dict]: 
 
    result = {} 
 
    with ThreadPoolExecutor(max_workers=20) as executor: 
 
        locations = executor.map( 
            find_location, 
            nodes 
        ) 
 
        for node_id, location in locations: 
            result[node_id] = location 
 
    return result