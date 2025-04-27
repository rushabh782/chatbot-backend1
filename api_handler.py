#!/usr/bin/env python
"""
API handler for the recommendation chatbot.
This script processes a query and returns recommendations as JSON.
"""
import sys
import json
import logging
from data_loader import DataLoader
from nlp_processor import NLPProcessor
from recommendation_engine import RecommendationEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def get_recommendations(query):
    """
    Process a query and return recommendations.
    
    Args:
        query (str): The user's query string
        
    Returns:
        dict: A dictionary containing the recommendations and metadata
    """
    try:
        # Initialize the components
        data_loader = DataLoader()
        restaurants_data = data_loader.load_restaurants_data()
        hotels_data = data_loader.load_hotels_data()
        vehicles_data = data_loader.load_vehicles_data()
        
        nlp_processor = NLPProcessor()
        recommendation_engine = RecommendationEngine(restaurants_data, hotels_data, vehicles_data)
        
        # Process the query
        query_type, filters = nlp_processor.process_query(query)
        
        # Generate recommendations based on query type
        if query_type == 'restaurant':
            recommendations = recommendation_engine.recommend_restaurants(filters)
            category = 'restaurants'
        elif query_type == 'hotel':
            recommendations = recommendation_engine.recommend_hotels(filters)
            category = 'hotels'
        elif query_type == 'vehicle':
            recommendations = recommendation_engine.recommend_vehicles(filters)
            category = 'vehicles'
        else:
            recommendations = []
            category = 'unknown'
        
        # Extract alternatives if available
        alternatives = None
        if hasattr(recommendation_engine, 'suggested_alternatives') and recommendation_engine.suggested_alternatives:
            alternatives = recommendation_engine.suggested_alternatives
        
        # Prepare the response
        response = {
            'success': True,
            'query': query,
            'query_type': query_type,
            'category': category,
            'filters': filters,
            'count': len(recommendations),
            'recommendations': recommendations
        }
        
        if alternatives:
            response['alternatives'] = alternatives
            
        return response
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'query': query
        }

if __name__ == "__main__":
    # Check if a query was provided as a command-line argument
    if len(sys.argv) < 2:
        logger.error("No query provided")
        result = {
            'success': False,
            'error': 'No query provided'
        }
    else:
        # Get the query from command-line arguments
        query = sys.argv[1]
        result = get_recommendations(query)
    
    # Print the result as JSON to stdout
    print(json.dumps(result))