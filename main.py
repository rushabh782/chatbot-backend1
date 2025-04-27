#!/usr/bin/env python3
"""
Command-line restaurant, hotel, and vehicle rental recommendation chatbot.
"""
import sys
import logging
from nlp_processor import NLPProcessor
from data_loader import DataLoader
from recommendation_engine import RecommendationEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def print_welcome_message():
    """Print welcome message with instructions for the user."""
    print("=" * 80)
    print("Welcome to the Travel Recommendation Assistant!")
    print("=" * 80)
    print("I can help you find restaurants, hotels, and vehicle rentals.")
    print("\nExample queries:")
    print("- 'Find cheap Italian restaurants in Mumbai with rating above 4'")
    print("- 'Show me the best hotels in Borivali'")
    print("- 'I need a luxury vehicle for 4 passengers'")
    print("\nType 'exit', 'quit', or 'bye' to end the conversation.")
    print("=" * 80)

def main():
    """Main function to run the chatbot."""
    # Load data
    try:
        data_loader = DataLoader()
        restaurants_data = data_loader.load_restaurants_data()
        hotels_data = data_loader.load_hotels_data()
        vehicles_data = data_loader.load_vehicles_data()
        
        # Initialize NLP processor and recommendation engine
        nlp = NLPProcessor()
        recommendation_engine = RecommendationEngine(
            restaurants_data, hotels_data, vehicles_data
        )
        
        # Print welcome message
        print_welcome_message()
        
        # Main conversation loop
        while True:
            # Get user input
            user_input = input("\n➤ ").strip()
            
            # Check if user wants to exit
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\nThank you for using the Travel Recommendation Assistant. Goodbye!")
                break
            
            # Skip empty inputs
            if not user_input:
                continue
            
            # Process user input
            try:
                query_type, filters = nlp.process_query(user_input)
                
                # Get recommendations based on query type and filters
                if query_type == 'restaurant':
                    results = recommendation_engine.recommend_restaurants(filters)
                    
                elif query_type == 'hotel':
                    results = recommendation_engine.recommend_hotels(filters)
                    
                elif query_type == 'vehicle':
                    results = recommendation_engine.recommend_vehicles(filters)
                    
                else:
                    print("I'm not sure what you're looking for. Could you please try again with more details?")
                    continue
                
                # Display results
                if results:
                    print(f"\nHere are some recommendations based on your request:")
                    for i, result in enumerate(results, 1):
                        print(f"\n{i}. {result}")
                    
                    if hasattr(recommendation_engine, 'suggested_alternatives') and recommendation_engine.suggested_alternatives:
                        print("\nYou might also be interested in:")
                        for alt in recommendation_engine.suggested_alternatives:
                            print(f"- {alt}")
                else:
                    print("\nI couldn't find any recommendations matching your criteria. Could you try with different preferences?")
            
            except Exception as e:
                logger.error(f"Error processing request: {str(e)}")
                print("Sorry, I encountered an error processing your request. Please try again.")
    
    except Exception as e:
        logger.error(f"Failed to initialize: {str(e)}")
        print("Error initializing the recommendation system. Please check your data files.")
        sys.exit(1)

if __name__ == "__main__":
    main()
