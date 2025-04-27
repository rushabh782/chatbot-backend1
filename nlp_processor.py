"""
Module for natural language processing of user queries.
"""
import re
import logging
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download required NLTK data
print("Checking NLTK data...")
try:
    nltk.data.find('tokenizers/punkt')
    print("Found punkt package")
except LookupError:
    print("Downloading punkt package...")
    nltk.download('punkt')
    print("Punkt download complete")

try:
    nltk.data.find('corpora/stopwords')
    print("Found stopwords package")
except LookupError:
    print("Downloading stopwords package...")
    nltk.download('stopwords')
    print("Stopwords download complete")
print("NLTK data setup complete.")

logger = logging.getLogger(__name__)

class NLPProcessor:
    """Class for processing natural language queries."""
    
    def __init__(self):
        """Initialize the NLPProcessor class."""
        self.restaurant_keywords = {
            'restaurant', 'restaurants', 'food', 'eat', 'dining', 'dine',
            'cuisine', 'meal', 'breakfast', 'lunch', 'dinner', 'cafe', 'bistro',
            'eatery', 'pizzeria', 'steakhouse', 'bakery'
        }
        
        self.hotel_keywords = {
            'hotel', 'hotels', 'motel', 'inn', 'stay', 'accommodation', 'lodge',
            'lodging', 'resort', 'room', 'bed', 'suite', 'guest house', 'homestay'
        }
        
        self.vehicle_keywords = {
            'vehicle', 'vehicles', 'car', 'cars', 'bike', 'bikes', 'motorcycle',
            'scooter', 'rental', 'rentals', 'rent', 'transport', 'transportation',
            'cab', 'taxi', 'drive', 'driving', 'ride', 'riding', 'bus', 'cycle'
        }
        
        self.price_keywords = {
            'cheap', 'budget', 'affordable', 'inexpensive', 'economical', 'low cost',
            'expensive', 'premium', 'luxury', 'high-end', 'pricey', 'costly',
            'price', 'cost', 'fee', 'rate', 'charges'
        }
        
        self.rating_keywords = {
            'best', 'top', 'highest rated', 'highly rated', 'good', 'excellent',
            'worst', 'lowest rated', 'poorly rated', 'bad', 'terrible',
            'rating', 'rated', 'stars', 'score'
        }
        
        self.location_keywords = {
            'in', 'at', 'near', 'around', 'close to', 'vicinity', 'area',
            'neighborhood', 'zone', 'region', 'locality', 'district'
        }
        
        self.cuisine_types = {
            'indian', 'chinese', 'italian', 'mexican', 'japanese', 'thai',
            'continental', 'mughlai', 'south indian', 'north indian', 'asian',
            'american', 'mediterranean', 'middle eastern', 'lebanese', 'french',
            'spanish', 'greek', 'korean', 'vietnamese', 'seafood', 'vegetarian',
            'vegan', 'fusion', 'fast food', 'street food', 'pizza', 'burger',
            'sushi', 'steak', 'bbq', 'barbecue', 'cafe', 'bakery', 'dessert'
        }
        
        self.cuisine_similarity = {
            'chinese': ['asian', 'japanese', 'korean', 'thai', 'vietnamese'],
            'japanese': ['asian', 'chinese', 'korean', 'sushi'],
            'thai': ['asian', 'chinese', 'vietnamese'],
            'korean': ['asian', 'japanese', 'chinese'],
            'vietnamese': ['asian', 'thai', 'chinese'],
            'indian': ['south indian', 'north indian', 'mughlai'],
            'south indian': ['indian', 'vegetarian'],
            'north indian': ['indian', 'mughlai'],
            'mughlai': ['indian', 'north indian'],
            'italian': ['mediterranean', 'pizza', 'pasta'],
            'mexican': ['spanish', 'american'],
            'mediterranean': ['greek', 'lebanese', 'middle eastern', 'italian'],
            'middle eastern': ['mediterranean', 'lebanese'],
            'american': ['burger', 'fast food', 'bbq'],
            'fast food': ['burger', 'american', 'street food'],
            'street food': ['fast food'],
            'vegetarian': ['vegan', 'south indian'],
            'vegan': ['vegetarian'],
            'seafood': ['asian', 'mediterranean']
        }
        
        self.stop_words = set(stopwords.words('english'))
    
    def process_query(self, query):
        """
        Process a natural language query to extract the query type and filters.
        
        Args:
            query (str): The user's natural language query
            
        Returns:
            tuple: A tuple containing (query_type, filters)
        """
        try:
            # Preprocess query
            query = query.lower()
            tokens = word_tokenize(query)
            
            # Determine query type (restaurant, hotel, or vehicle)
            query_type = self._determine_query_type(query, tokens)
            
            # Extract filters based on query type
            filters = self._extract_filters(query, tokens, query_type)
            
            logger.info(f"Processed query: {query_type} with filters: {filters}")
            return query_type, filters
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            # Default to restaurant search with minimal filters if processing fails
            return 'restaurant', {'query': query}
    
    def _determine_query_type(self, query, tokens):
        """
        Determine the type of query (restaurant, hotel, or vehicle).
        
        Args:
            query (str): The full user query
            tokens (list): Tokenized query
            
        Returns:
            str: The query type ('restaurant', 'hotel', or 'vehicle')
        """
        # Count keyword occurrences for each category
        restaurant_count = sum(1 for token in tokens if token in self.restaurant_keywords)
        hotel_count = sum(1 for token in tokens if token in self.hotel_keywords)
        vehicle_count = sum(1 for token in tokens if token in self.vehicle_keywords)
        
        # Determine the most likely query type
        if restaurant_count > hotel_count and restaurant_count > vehicle_count:
            return 'restaurant'
        elif hotel_count > restaurant_count and hotel_count > vehicle_count:
            return 'hotel'
        elif vehicle_count > restaurant_count and vehicle_count > hotel_count:
            return 'vehicle'
        else:
            # Default to restaurant if unclear
            for cuisine in self.cuisine_types:
                if cuisine in query:
                    return 'restaurant'
            
            # Additional heuristics
            if any(word in query for word in ['room', 'stay', 'night', 'accommodation']):
                return 'hotel'
            elif any(word in query for word in ['drive', 'ride', 'passenger', 'seat']):
                return 'vehicle'
            
            # Final fallback
            return 'restaurant'
    
    def _extract_filters(self, query, tokens, query_type):
        """
        Extract filters from the query based on the query type.
        
        Args:
            query (str): The full user query
            tokens (list): Tokenized query
            query_type (str): The type of query ('restaurant', 'hotel', or 'vehicle')
            
        Returns:
            dict: A dictionary of filters
        """
        filters = {'query': query}  # Store original query for reference
        
        # Extract location information
        location = self._extract_location(query)
        if location:
            filters['location'] = location
        
        # Extract price preferences
        price_info = self._extract_price_info(query)
        if price_info:
            filters.update(price_info)
        
        # Extract rating preferences
        rating_info = self._extract_rating_info(query)
        if rating_info:
            filters.update(rating_info)
        
        # Extract query intent (cheap, expensive, best, worst, etc.)
        intent = self._extract_intent(query)
        if intent:
            filters['intent'] = intent
        
        # Extract type-specific filters
        if query_type == 'restaurant':
            # Extract cuisine preferences
            cuisine = self._extract_cuisine(query)
            if cuisine:
                filters['cuisine'] = cuisine
                
                # Find similar cuisines for suggestions
                similar_cuisines = self._find_similar_cuisines(cuisine)
                if similar_cuisines:
                    filters['similar_cuisines'] = similar_cuisines
        
        elif query_type == 'hotel':
            # Extract hotel category/amenities
            category = self._extract_hotel_category(query)
            if category:
                filters['category'] = category
            
            amenities = self._extract_amenities(query)
            if amenities:
                filters['amenities'] = amenities
        
        elif query_type == 'vehicle':
            # Extract vehicle type and passengers
            vehicle_type = self._extract_vehicle_type(query)
            if vehicle_type:
                filters['vehicle_type'] = vehicle_type
            
            passengers = self._extract_passengers(query)
            if passengers:
                filters['passengers'] = passengers
            
            preference = self._extract_vehicle_preference(query)
            if preference:
                filters['preference'] = preference
        
        return filters
    
    def _extract_location(self, query):
        """
        Extract location information from the query.
        
        Args:
            query (str): The user query
            
        Returns:
            str or None: The extracted location or None if not found
        """
        # Common locations in Mumbai
        locations = [
            'mumbai', 'borivali', 'andheri', 'bandra', 'dadar', 'churchgate', 
            'kurla', 'thane', 'powai', 'juhu', 'malad', 'goregaon', 'vikhroli',
            'chembur', 'ghatkopar', 'kandivali', 'vile parle', 'santacruz',
            'khar', 'marine lines', 'fort', 'mira road', 'vasai', 'virar'
        ]
        
        # Look for location patterns
        for location in locations:
            # Check for location in the query
            if location in query.lower():
                return location
            
            # Check for location pattern "in/at/near X"
            match = re.search(r'(?:in|at|near|around)\s+(\w+\s+\w+|\w+)', query.lower())
            if match:
                loc = match.group(1)
                # Verify it's a known location
                for known_loc in locations:
                    if known_loc in loc:
                        return known_loc
                
                # If no known location found, return the extracted one
                return loc
        
        return None
    
    def _extract_price_info(self, query):
        """
        Extract price-related information from the query.
        
        Args:
            query (str): The user query
            
        Returns:
            dict or None: Dictionary with price information or None if not found
        """
        price_info = {}
        
        # Check for numeric price values
        price_match = re.search(r'(?:under|below|less than|maximum|max)\s+(?:rs\.?|₹)?\s*(\d+)', query, re.IGNORECASE)
        if price_match:
            price_info['max_price'] = int(price_match.group(1))
        
        price_match = re.search(r'(?:above|over|more than|minimum|min)\s+(?:rs\.?|₹)?\s*(\d+)', query, re.IGNORECASE)
        if price_match:
            price_info['min_price'] = int(price_match.group(1))
        
        price_match = re.search(r'(?:between|from)\s+(?:rs\.?|₹)?\s*(\d+)\s+(?:to|and|[-])\s+(?:rs\.?|₹)?\s*(\d+)', query, re.IGNORECASE)
        if price_match:
            price_info['min_price'] = int(price_match.group(1))
            price_info['max_price'] = int(price_match.group(2))
        
        # Check for price keywords
        if 'cheap' in query or 'budget' in query or 'affordable' in query or 'inexpensive' in query:
            price_info['price_level'] = 'cheap'
        elif 'expensive' in query or 'luxury' in query or 'premium' in query or 'high-end' in query:
            price_info['price_level'] = 'expensive'
        
        return price_info if price_info else None
    
    def _extract_rating_info(self, query):
        """
        Extract rating-related information from the query.
        
        Args:
            query (str): The user query
            
        Returns:
            dict or None: Dictionary with rating information or None if not found
        """
        rating_info = {}
        
        # Check for numeric rating values
        rating_match = re.search(r'(?:rating|rated|score)(?:\s+(?:of|above|over|more than|higher than))?\s+(\d+(?:\.\d+)?)', query, re.IGNORECASE)
        if rating_match:
            rating_info['min_rating'] = float(rating_match.group(1))
        
        rating_match = re.search(r'(?:rating|rated)(?:\s+(?:below|under|less than|lower than))?\s+(\d+(?:\.\d+)?)', query, re.IGNORECASE)
        if rating_match:
            rating_info['max_rating'] = float(rating_match.group(1))
        
        # Check for rating keywords
        if 'best' in query or 'top' in query or 'highest rated' in query or 'excellent' in query:
            rating_info['rating_level'] = 'high'
        elif 'worst' in query or 'lowest rated' in query or 'bad' in query or 'terrible' in query:
            rating_info['rating_level'] = 'low'
        
        return rating_info if rating_info else None
    
    def _extract_intent(self, query):
        """
        Extract the main intent of the query.
        
        Args:
            query (str): The user query
            
        Returns:
            str or None: The main intent or None if unclear
        """
        # Define intent keywords for restaurants
        cheap_keywords = ['cheap', 'budget', 'affordable', 'inexpensive', 'economical', 'low price', 'low cost']
        expensive_keywords = ['expensive', 'luxury', 'premium', 'high-end', 'pricey', 'costly', 'upscale', 'fancy']
        best_keywords = ['best', 'top', 'highest rated', 'highly rated', 'excellent', '5 star', 'five star', 'top rated']
        worst_keywords = ['worst', 'lowest rated', 'poorly rated', 'bad', 'terrible', 'avoid']
        
        # Define intent keywords for hotels
        amenities_keywords = ['with pool', 'free wifi', 'gym', 'fitness', 'breakfast included', 'spa', 'parking', 'pet friendly']
        category_keywords = ['boutique', 'resort', 'motel', 'hostel', 'bed and breakfast', 'family hotel', 'business hotel']
        
        # Define intent keywords for vehicles
        vehicle_type_keywords = ['car', 'truck', 'van', 'bus', 'motorcycle', 'suv', 'cycle', 'bike']
        capacity_keywords = ['seats', 'passengers', 'people', 'person', 'capacity', 'for 2', 'for 4', 'for 6', 'fit']
        
        # Analyze the query
        query_type = None
        if 'restaurant' in query or 'food' in query or 'place to eat' in query:
            query_type = 'restaurant'
        elif 'hotel' in query or 'place to stay' in query or 'accommodation' in query:
            query_type = 'hotel'
        elif 'vehicle' in query or 'car' in query or 'rental' in query:
            query_type = 'vehicle'
            
        # Check for intent keywords in query
        if any(keyword in query for keyword in cheap_keywords):
            return 'cheap'
        elif any(keyword in query for keyword in expensive_keywords):
            return 'expensive'
        elif any(keyword in query for keyword in best_keywords):
            return 'best'
        elif any(keyword in query for keyword in worst_keywords):
            return 'worst'
        
        # Check for query type-specific intents
        if query_type == 'restaurant':
            # Check if the query is primarily about a cuisine
            for cuisine in self.cuisine_types:
                if cuisine in query:
                    return 'cuisine'
            
            # Check for location focus
            if any(keyword in query for keyword in self.location_keywords):
                return 'location'
                
        elif query_type == 'hotel':
            # Check for amenities focus
            if any(keyword in query for keyword in amenities_keywords):
                return 'amenities'
                
            # Check for category focus
            if any(keyword in query for keyword in category_keywords):
                return 'category'
                
            # Check for location focus
            if any(keyword in query for keyword in self.location_keywords):
                return 'location'
                
        elif query_type == 'vehicle':
            # Check for vehicle type focus
            if any(keyword in query for keyword in vehicle_type_keywords):
                return 'type'
                
            # Check for capacity focus
            if any(keyword in query for keyword in capacity_keywords):
                return 'capacity'
                
            # Check for location focus
            if any(keyword in query for keyword in self.location_keywords):
                return 'location'
        
        # Check for generic location focus if query type wasn't determined
        if any(keyword in query for keyword in self.location_keywords) or re.search(r'in\s+(\w+)', query):
            return 'location'
        
        # If we couldn't determine a clear intent, default to a mix of price and quality
        return 'price_quality_mix'
    
    def _extract_cuisine(self, query):
        """
        Extract cuisine preferences from the query.
        
        Args:
            query (str): The user query
            
        Returns:
            str or None: The cuisine preference or None if not found
        """
        for cuisine in self.cuisine_types:
            if cuisine in query:
                return cuisine
        
        return None
    
    def _find_similar_cuisines(self, cuisine):
        """
        Find similar cuisines to the one specified.
        
        Args:
            cuisine (str): The specified cuisine
            
        Returns:
            list or None: Similar cuisines or None if none found
        """
        if cuisine in self.cuisine_similarity:
            return self.cuisine_similarity[cuisine]
        return None
    
    def _extract_hotel_category(self, query):
        """
        Extract hotel category preferences from the query.
        
        Args:
            query (str): The user query
            
        Returns:
            str or None: The hotel category or None if not found
        """
        categories = ['luxury', 'budget', 'family', 'business', 'resort', 'friendly']
        
        for category in categories:
            if category in query:
                return category
        
        return None
    
    def _extract_amenities(self, query):
        """
        Extract amenity preferences from the query.
        
        Args:
            query (str): The user query
            
        Returns:
            list or None: The amenities or None if not found
        """
        # Common hotel amenities with variations to match the dataset format
        amenity_mapping = {
            'wifi': ['wifi', 'wi-fi', 'wi fi', 'wireless', 'internet', 'free wifi', 'free wi-fi'],
            'pool': ['pool', 'swimming pool', 'rooftop pool', 'outdoor pool', 'indoor pool'],
            'gym': ['gym', 'fitness center', 'fitness room', 'workout', 'exercise'],
            'spa': ['spa', 'wellness', 'massage', 'sauna'],
            'restaurant': ['restaurant', 'dining', 'cafe', 'eatery', 'food', 'fine dining'],
            'bar': ['bar', 'lounge', 'pub', 'cocktail'],
            'breakfast': ['breakfast', 'complimentary breakfast', 'free breakfast', 'morning meal'],
            'parking': ['parking', 'free parking', 'valet', 'car park'],
            'air conditioning': ['air conditioning', 'ac', 'a/c', 'climate control', 'air-conditioned'],
            'room service': ['room service', '24-hour service', '24/7 service'],
            'business': ['business center', 'conference', 'meeting rooms'],
            'laundry': ['laundry', 'dry cleaning', 'cleaning service']
        }
        
        amenities = []
        
        # Check for each amenity and its variations
        for main_amenity, variations in amenity_mapping.items():
            for variation in variations:
                if variation in query.lower():
                    if main_amenity not in amenities:  # Avoid duplicates
                        amenities.append(main_amenity)
                    break  # Found one variation, no need to check others
        
        return amenities if amenities else None
    
    def _extract_vehicle_type(self, query):
        """
        Extract vehicle type preferences from the query.
        
        Args:
            query (str): The user query
            
        Returns:
            str or None: The vehicle type or None if not found
        """
        vehicle_types = ['car', 'bike', 'motorcycle', 'scooter', 'bicycle', 'cycle', 'bus']
        
        for vehicle_type in vehicle_types:
            if vehicle_type in query:
                return vehicle_type
        
        return None
    
    def _extract_passengers(self, query):
        """
        Extract passenger count from the query.
        
        Args:
            query (str): The user query
            
        Returns:
            int or None: The passenger count or None if not found
        """
        # Look for patterns like "for X people", "X passengers", "seats X"
        passenger_match = re.search(r'(?:for|with)?\s*(\d+)\s*(?:people|person|passenger|passengers|persons|seats)', query, re.IGNORECASE)
        if passenger_match:
            return int(passenger_match.group(1))
        
        return None
    
    def _extract_vehicle_preference(self, query):
        """
        Extract vehicle preference from the query.
        
        Args:
            query (str): The user query
            
        Returns:
            str or None: The vehicle preference or None if not found
        """
        if 'luxury' in query or 'premium' in query or 'high-end' in query:
            return 'luxury'
        elif 'cheap' in query or 'budget' in query or 'affordable' in query:
            return 'cheap'
        
        return None
