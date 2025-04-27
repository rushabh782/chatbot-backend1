"""
Test the direct name lookup functionality for hotels and vehicles
"""
import logging
import sys
from data_loader import DataLoader
from nlp_processor import NLPProcessor
from recommendation_engine import RecommendationEngine

# Configure logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

# Create instances
data_loader = DataLoader()
restaurants_data = data_loader.load_restaurants_data()
hotels_data = data_loader.load_hotels_data()
vehicles_data = data_loader.load_vehicles_data()

nlp_processor = NLPProcessor()
recommendation_engine = RecommendationEngine(restaurants_data, hotels_data, vehicles_data)

# Test hotel direct lookup
def test_hotel_name_lookup():
    print("\n=== Testing hotel name lookup ===")
    query = "Tell me about The Oberoi Mumbai"
    print(f"Query: {query}")
    
    query_type, filters = nlp_processor.process_query(query)
    print(f"Detected query type: {query_type}")
    print(f"Extracted filters: {filters}")
    
    # Get recommendations
    if query_type == 'hotel':
        results = recommendation_engine.recommend_hotels(filters)
        for result in results:
            print(f"\nResult: {result}")
    else:
        print(f"Error: Query type detected as {query_type}, expected 'hotel'")

# Test vehicle direct lookup
def test_vehicle_name_lookup():
    print("\n=== Testing vehicle name lookup ===")
    query = "I want to rent a Toyota Fortuner"
    print(f"Query: {query}")
    
    query_type, filters = nlp_processor.process_query(query)
    print(f"Detected query type: {query_type}")
    print(f"Extracted filters: {filters}")
    
    # Get recommendations
    if query_type == 'vehicle':
        results = recommendation_engine.recommend_vehicles(filters)
        for result in results:
            print(f"\nResult: {result}")
    else:
        print(f"Error: Query type detected as {query_type}, expected 'vehicle'")

if __name__ == "__main__":
    test_hotel_name_lookup()
    test_vehicle_name_lookup()