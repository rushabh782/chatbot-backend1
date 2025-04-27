"""
Module for generating recommendations based on user filters.
"""
import logging
import pandas as pd
import re
from utils import format_restaurant, format_hotel, format_vehicle

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """Class for generating recommendations based on user filters."""
    
    def __init__(self, restaurants_data, hotels_data, vehicles_data):
        """
        Initialize the RecommendationEngine class.
        
        Args:
            restaurants_data (pd.DataFrame): Preprocessed restaurant data
            hotels_data (pd.DataFrame): Preprocessed hotel data
            vehicles_data (pd.DataFrame): Preprocessed vehicle data
        """
        self.restaurants_data = restaurants_data
        self.hotels_data = hotels_data
        self.vehicles_data = vehicles_data
        self.suggested_alternatives = []
    
    def recommend_restaurants(self, filters, max_results=5):
        """
        Generate restaurant recommendations based on filters.
        
        Args:
            filters (dict): Dictionary of filters
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of formatted restaurant recommendations
        """
        try:
            logger.info(f"Generating restaurant recommendations with filters: {filters}")
            self.suggested_alternatives = []  # Reset suggested alternatives
            
            # Get a copy of the data to filter
            filtered_data = self.restaurants_data.copy()
            
            # Determine the filtering strategy based on intent
            intent = filters.get('intent', 'price_quality_mix')
            
            # Apply filters based on the intent
            if intent == 'cheap':
                # Case 1: Cheap Restaurants (price_range_to ≤ X → rating ≥ Y → address → cuisines)
                filtered_data = self._filter_cheap_restaurants(filtered_data, filters)
            
            elif intent == 'expensive':
                # Case 2: Most Expensive (price_range_from ≥ X → rating ≥ Y → address → cuisines)
                filtered_data = self._filter_expensive_restaurants(filtered_data, filters)
            
            elif intent == 'best':
                # Case 3: Best/Highest-Rated (rating ≥ X → price_range_to ≤ Y → cuisines → address)
                filtered_data = self._filter_best_restaurants(filtered_data, filters)
            
            elif intent == 'worst':
                # Case 4: Worst/Lowest-Rated (rating ≤ X → price_range_from ≥ Y → cuisines → address)
                filtered_data = self._filter_worst_restaurants(filtered_data, filters)
            
            elif intent == 'location':
                # Case 5: Location-Based (address → rating ≥ X → price_range_to ≤ Y → cuisines)
                filtered_data = self._filter_location_restaurants(filtered_data, filters)
            
            elif intent == 'cuisine':
                # Case 6: Cuisine-Based (cuisines → rating ≥ X → price_range_to ≤ Y → address)
                filtered_data = self._filter_cuisine_restaurants(filtered_data, filters)
            
            else:  # price_quality_mix
                # Case 7: Price+Quality Mix (rating ≥ X → price_range_to ≤ Y → address → cuisines)
                filtered_data = self._filter_price_quality_mix_restaurants(filtered_data, filters)
            
            # Sort results based on the intent
            filtered_data = self._sort_restaurants_by_intent(filtered_data, intent)
            
            # Format results for display
            results = []
            for _, row in filtered_data.head(max_results).iterrows():
                results.append(format_restaurant(row))
            
            # Add similar cuisine suggestions if applicable
            if 'cuisine' in filters and 'similar_cuisines' in filters:
                cuisine = filters['cuisine']
                similar_cuisines = filters['similar_cuisines']
                self.suggested_alternatives.append(f"If you like {cuisine.title()} cuisine, you might also enjoy: {', '.join(c.title() for c in similar_cuisines)}")
            
            logger.info(f"Found {len(results)} restaurant recommendations")
            return results
            
        except Exception as e:
            logger.error(f"Error generating restaurant recommendations: {str(e)}")
            return []
    
    def _filter_cheap_restaurants(self, data, filters):
        """
        Filter for cheap restaurants.
        Priority: price_range_to ≤ X → rating ≥ Y → address → cuisines
        """
        # 1. Filter by price (primary)
        if 'max_price' in filters:
            data = data[data['price_range_to'] <= filters['max_price']]
        elif 'price_level' in filters and filters['price_level'] == 'cheap':
            # Use a reasonable default for "cheap" if no specific price given
            data = data.sort_values('price_range_to')
            data = data.head(int(len(data) * 0.3))  # Top 30% cheapest
        
        # 2. Filter by rating (secondary)
        if 'min_rating' in filters:
            data = data[data['rating'] >= filters['min_rating']]
        
        # 3. Filter by location (tertiary)
        if 'location' in filters:
            location_pattern = re.compile(filters['location'], re.IGNORECASE)
            data = data[data['address'].apply(lambda x: bool(location_pattern.search(x)))]
        
        # 4. Filter by cuisine (quaternary)
        if 'cuisine' in filters:
            cuisine_pattern = re.compile(filters['cuisine'], re.IGNORECASE)
            data = data[data['cuisines'].apply(lambda x: bool(cuisine_pattern.search(str(x))))]
        
        return data
    
    def _filter_expensive_restaurants(self, data, filters):
        """
        Filter for expensive restaurants.
        Priority: price_range_from ≥ X → rating ≥ Y → address → cuisines
        """
        # 1. Filter by price (primary)
        if 'min_price' in filters:
            data = data[data['price_range_from'] >= filters['min_price']]
        elif 'price_level' in filters and filters['price_level'] == 'expensive':
            # Use a reasonable default for "expensive" if no specific price given
            data = data.sort_values('price_range_from', ascending=False)
            data = data.head(int(len(data) * 0.3))  # Top 30% most expensive
        
        # 2. Filter by rating (secondary)
        if 'min_rating' in filters:
            data = data[data['rating'] >= filters['min_rating']]
        
        # 3. Filter by location (tertiary)
        if 'location' in filters:
            location_pattern = re.compile(filters['location'], re.IGNORECASE)
            data = data[data['address'].apply(lambda x: bool(location_pattern.search(x)))]
        
        # 4. Filter by cuisine (quaternary)
        if 'cuisine' in filters:
            cuisine_pattern = re.compile(filters['cuisine'], re.IGNORECASE)
            data = data[data['cuisines'].apply(lambda x: bool(cuisine_pattern.search(str(x))))]
        
        return data
    
    def _filter_best_restaurants(self, data, filters):
        """
        Filter for best/highest-rated restaurants.
        Priority: rating ≥ X → price_range_to ≤ Y → cuisines → address
        """
        # 1. Filter by rating (primary)
        if 'min_rating' in filters:
            data = data[data['rating'] >= filters['min_rating']]
        else:
            # Default to 4.0+ rating for "best" if not specified
            data = data[data['rating'] >= 4.0]
        
        # 2. Filter by price (secondary, optional)
        if 'max_price' in filters:
            data = data[data['price_range_to'] <= filters['max_price']]
        
        # 3. Filter by cuisine (tertiary)
        if 'cuisine' in filters:
            cuisine_pattern = re.compile(filters['cuisine'], re.IGNORECASE)
            data = data[data['cuisines'].apply(lambda x: bool(cuisine_pattern.search(str(x))))]
        
        # 4. Filter by location (quaternary)
        if 'location' in filters:
            location_pattern = re.compile(filters['location'], re.IGNORECASE)
            data = data[data['address'].apply(lambda x: bool(location_pattern.search(x)))]
        
        return data
    
    def _filter_worst_restaurants(self, data, filters):
        """
        Filter for worst/lowest-rated restaurants.
        Priority: rating ≤ X → price_range_from ≥ Y → cuisines → address
        """
        # 1. Filter by rating (primary)
        if 'max_rating' in filters:
            data = data[data['rating'] <= filters['max_rating']]
        else:
            # Default to 3.0- rating for "worst" if not specified
            data = data[data['rating'] <= 3.0]
        
        # 2. Filter by price (secondary, optional)
        if 'min_price' in filters:
            data = data[data['price_range_from'] >= filters['min_price']]
        
        # 3. Filter by cuisine (tertiary)
        if 'cuisine' in filters:
            cuisine_pattern = re.compile(filters['cuisine'], re.IGNORECASE)
            data = data[data['cuisines'].apply(lambda x: bool(cuisine_pattern.search(str(x))))]
        
        # 4. Filter by location (quaternary)
        if 'location' in filters:
            location_pattern = re.compile(filters['location'], re.IGNORECASE)
            data = data[data['address'].apply(lambda x: bool(location_pattern.search(x)))]
        
        return data
    
    def _filter_location_restaurants(self, data, filters):
        """
        Filter for location-based restaurants.
        Priority: address → rating ≥ X → price_range_to ≤ Y → cuisines
        """
        # 1. Filter by location (primary)
        if 'location' in filters:
            location_pattern = re.compile(filters['location'], re.IGNORECASE)
            data = data[data['address'].apply(lambda x: bool(location_pattern.search(x)))]
        
        # 2. Filter by rating (secondary)
        if 'min_rating' in filters:
            data = data[data['rating'] >= filters['min_rating']]
        
        # 3. Filter by price (tertiary)
        if 'max_price' in filters:
            data = data[data['price_range_to'] <= filters['max_price']]
        
        # 4. Filter by cuisine (quaternary)
        if 'cuisine' in filters:
            cuisine_pattern = re.compile(filters['cuisine'], re.IGNORECASE)
            data = data[data['cuisines'].apply(lambda x: bool(cuisine_pattern.search(str(x))))]
        
        return data
    
    def _filter_cuisine_restaurants(self, data, filters):
        """
        Filter for cuisine-based restaurants.
        Priority: cuisines → rating ≥ X → price_range_to ≤ Y → address
        """
        # 1. Filter by cuisine (primary)
        if 'cuisine' in filters:
            cuisine_pattern = re.compile(filters['cuisine'], re.IGNORECASE)
            data = data[data['cuisines'].apply(lambda x: bool(cuisine_pattern.search(str(x))))]
        
        # 2. Filter by rating (secondary)
        if 'min_rating' in filters:
            data = data[data['rating'] >= filters['min_rating']]
        
        # 3. Filter by price (tertiary)
        if 'max_price' in filters:
            data = data[data['price_range_to'] <= filters['max_price']]
        
        # 4. Filter by location (quaternary)
        if 'location' in filters:
            location_pattern = re.compile(filters['location'], re.IGNORECASE)
            data = data[data['address'].apply(lambda x: bool(location_pattern.search(x)))]
        
        return data
    
    def _filter_price_quality_mix_restaurants(self, data, filters):
        """
        Filter for price+quality mix restaurants.
        Priority: rating ≥ X → price_range_to ≤ Y → address → cuisines
        """
        # 1. Filter by rating (primary)
        if 'min_rating' in filters:
            data = data[data['rating'] >= filters['min_rating']]
        else:
            # Default to 3.5+ rating for "quality" if not specified
            data = data[data['rating'] >= 3.5]
        
        # 2. Filter by price (secondary)
        if 'max_price' in filters:
            data = data[data['price_range_to'] <= filters['max_price']]
        
        # 3. Filter by location (tertiary)
        if 'location' in filters:
            location_pattern = re.compile(filters['location'], re.IGNORECASE)
            data = data[data['address'].apply(lambda x: bool(location_pattern.search(x)))]
        
        # 4. Filter by cuisine (quaternary)
        if 'cuisine' in filters:
            cuisine_pattern = re.compile(filters['cuisine'], re.IGNORECASE)
            data = data[data['cuisines'].apply(lambda x: bool(cuisine_pattern.search(str(x))))]
        
        return data
    
    def _sort_restaurants_by_intent(self, data, intent):
        """Sort filtered restaurants based on the intent."""
        if not data.empty:
            if intent == 'cheap':
                # Sort by price (ascending), then rating (descending)
                return data.sort_values(['price_range_to', 'rating'], ascending=[True, False])
            
            elif intent == 'expensive':
                # Sort by price (descending), then rating (descending)
                return data.sort_values(['price_range_from', 'rating'], ascending=[False, False])
            
            elif intent == 'best':
                # Sort by rating (descending), then review count (descending)
                return data.sort_values(['rating', 'review_count'], ascending=[False, False])
            
            elif intent == 'worst':
                # Sort by rating (ascending), then price (descending)
                return data.sort_values(['rating', 'price_range_from'], ascending=[True, False])
            
            elif intent == 'location' or intent == 'cuisine':
                # Sort by rating (descending), then price (ascending)
                return data.sort_values(['rating', 'price_range_to'], ascending=[False, True])
            
            else:  # price_quality_mix
                # Calculate a score based on rating and price
                if 'score' not in data.columns:
                    # Normalize price_range_to to 0-1 scale (inverted so lower is better)
                    max_price = data['price_range_to'].max() if data['price_range_to'].max() > 0 else 1
                    norm_price = 1 - (data['price_range_to'] / max_price)
                    
                    # Normalize rating to 0-1 scale
                    norm_rating = data['rating'] / 5
                    
                    # Combine for a value score (70% rating, 30% price)
                    data['score'] = (0.7 * norm_rating) + (0.3 * norm_price)
                
                # Sort by the computed score (descending)
                return data.sort_values('score', ascending=False)
        
        return data
    
    def recommend_hotels(self, filters, max_results=5):
        """
        Generate hotel recommendations based on filters.
        
        Args:
            filters (dict): Dictionary of filters
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of formatted hotel recommendations
        """
        try:
            logger.info(f"Generating hotel recommendations with filters: {filters}")
            self.suggested_alternatives = []  # Reset suggested alternatives
            
            # Get a copy of the data to filter
            filtered_data = self.hotels_data.copy()
            
            # Determine the filtering strategy based on intent
            intent = filters.get('intent', 'price_quality_mix')
            
            # Apply filters based on the intent
            if intent == 'cheap':
                # Case 1: Cheapest Hotels (price ≤ X → rating ≥ Y → location → category)
                filtered_data = self._filter_cheap_hotels(filtered_data, filters)
            
            elif intent == 'expensive':
                # Case 2: Most Expensive Hotel (price = max → rating ≥ Y → location → category)
                filtered_data = self._filter_expensive_hotels(filtered_data, filters)
            
            elif intent == 'best':
                # Case 3: Best-Rated Hotels (rating ≥ X → price ≤ Y → location → category)
                filtered_data = self._filter_best_hotels(filtered_data, filters)
            
            elif intent == 'worst':
                # Case 4: Worst-Rated Hotels (rating ≤ X → price ≤/≥ Y → location → category)
                filtered_data = self._filter_worst_hotels(filtered_data, filters)
            
            elif intent == 'amenities':
                # Case 5: Amenities-Based (amenities → rating ≥ X → price ≤ Y → location)
                filtered_data = self._filter_amenities_hotels(filtered_data, filters)
            
            elif intent == 'category':
                # Case 6: Category/Type-Based (category → rating ≥ X → price ≤ Y → location)
                filtered_data = self._filter_category_hotels(filtered_data, filters)
            
            elif intent == 'location':
                # Case 7: Location-Based (location → rating ≥ X → price ≤ Y → amenities)
                filtered_data = self._filter_location_hotels(filtered_data, filters)
            
            else:  # price_quality_mix
                # Case 8: Price+Quality Mix (rating ≥ X → price ≤ Y → location → amenities)
                filtered_data = self._filter_price_quality_mix_hotels(filtered_data, filters)
            
            # Sort results based on the intent
            filtered_data = self._sort_hotels_by_intent(filtered_data, intent)
            
            # Format results for display
            results = []
            for _, row in filtered_data.head(max_results).iterrows():
                results.append(format_hotel(row))
            
            logger.info(f"Found {len(results)} hotel recommendations")
            return results
            
        except Exception as e:
            logger.error(f"Error generating hotel recommendations: {str(e)}")
            return []
            
    def _filter_cheap_hotels(self, data, filters):
        """
        Filter for cheap hotels.
        Priority: price ≤ X → rating ≥ Y → location → category
        """
        # 1. Filter by price (primary)
        if 'max_price' in filters:
            data = data[data['price'] <= filters['max_price']]
        elif 'price_level' in filters and filters['price_level'] == 'cheap':
            # Use a reasonable default for "cheap" if no specific price given
            data = data.sort_values('price')
            data = data.head(int(len(data) * 0.3))  # Top 30% cheapest
        
        # 2. Filter by rating (secondary)
        if 'min_rating' in filters:
            data = data[data['rating'] >= filters['min_rating']]
        elif 'rating_level' in filters and filters['rating_level'] == 'high':
            data = data[data['rating'] >= 4.0]
        
        # 3. Filter by location (tertiary)
        if 'location' in filters:
            location_pattern = re.compile(filters['location'], re.IGNORECASE)
            data = data[data['location'].apply(lambda x: bool(location_pattern.search(str(x))))]
        
        # 4. Filter by category (quaternary)
        if 'category' in filters:
            category_pattern = re.compile(filters['category'], re.IGNORECASE)
            data = data[data['category'].apply(lambda x: bool(category_pattern.search(str(x))))]
        
        return data
    
    def _filter_expensive_hotels(self, data, filters):
        """
        Filter for expensive hotels.
        Priority: price = max → rating ≥ Y → location → category
        """
        # 1. Filter by price (primary)
        if 'min_price' in filters:
            data = data[data['price'] >= filters['min_price']]
        elif 'price_level' in filters and filters['price_level'] == 'expensive':
            # Use a reasonable default for "expensive" if no specific price given
            data = data.sort_values('price', ascending=False)
            data = data.head(int(len(data) * 0.3))  # Top 30% most expensive
        
        # 2. Filter by rating (secondary)
        if 'min_rating' in filters:
            data = data[data['rating'] >= filters['min_rating']]
        elif 'rating_level' in filters and filters['rating_level'] == 'high':
            data = data[data['rating'] >= 4.0]
        
        # 3. Filter by location (tertiary)
        if 'location' in filters:
            location_pattern = re.compile(filters['location'], re.IGNORECASE)
            data = data[data['location'].apply(lambda x: bool(location_pattern.search(str(x))))]
        
        # 4. Filter by category (quaternary)
        if 'category' in filters:
            category_pattern = re.compile(filters['category'], re.IGNORECASE)
            data = data[data['category'].apply(lambda x: bool(category_pattern.search(str(x))))]
        
        return data
    
    def _filter_best_hotels(self, data, filters):
        """
        Filter for best/highest-rated hotels.
        Priority: rating ≥ X → price ≤ Y → location → category
        """
        # 1. Filter by rating (primary)
        if 'min_rating' in filters:
            data = data[data['rating'] >= filters['min_rating']]
        elif 'rating_level' in filters and filters['rating_level'] == 'high':
            data = data[data['rating'] >= 4.0]
        else:
            # Default to 4.0+ rating for "best" if not specified
            data = data[data['rating'] >= 4.0]
        
        # 2. Filter by price (secondary, optional)
        if 'max_price' in filters:
            data = data[data['price'] <= filters['max_price']]
        
        # 3. Filter by location (tertiary)
        if 'location' in filters:
            location_pattern = re.compile(filters['location'], re.IGNORECASE)
            data = data[data['location'].apply(lambda x: bool(location_pattern.search(str(x))))]
        
        # 4. Filter by category (quaternary)
        if 'category' in filters:
            category_pattern = re.compile(filters['category'], re.IGNORECASE)
            data = data[data['category'].apply(lambda x: bool(category_pattern.search(str(x))))]
        
        return data
    
    def _filter_worst_hotels(self, data, filters):
        """
        Filter for worst/lowest-rated hotels.
        Priority: rating ≤ X → price ≤/≥ Y → location → category
        """
        # 1. Filter by rating (primary)
        if 'max_rating' in filters:
            data = data[data['rating'] <= filters['max_rating']]
        elif 'rating_level' in filters and filters['rating_level'] == 'low':
            data = data[data['rating'] <= 3.0]
        else:
            # Default to 3.0- rating for "worst" if not specified
            data = data[data['rating'] <= 3.0]
        
        # 2. Filter by price (secondary, optional)
        if 'min_price' in filters:
            data = data[data['price'] >= filters['min_price']]
        elif 'max_price' in filters:
            data = data[data['price'] <= filters['max_price']]
        
        # 3. Filter by location (tertiary)
        if 'location' in filters:
            location_pattern = re.compile(filters['location'], re.IGNORECASE)
            data = data[data['location'].apply(lambda x: bool(location_pattern.search(str(x))))]
        
        # 4. Filter by category (quaternary)
        if 'category' in filters:
            category_pattern = re.compile(filters['category'], re.IGNORECASE)
            data = data[data['category'].apply(lambda x: bool(category_pattern.search(str(x))))]
        
        return data
    
    def _filter_amenities_hotels(self, data, filters):
        """
        Filter for amenities-based hotels.
        Priority: amenities → rating ≥ X → price ≤ Y → location
        """
        # Make a copy of the original data in case we don't find matches
        original_data = data.copy()
        filtered_data = original_data.copy()
        
        # Create a scoring system instead of strict filtering
        if 'amenities' in filters and filters['amenities']:
            # Initialize a score column
            filtered_data['amenity_score'] = 0
            
            # Score each hotel based on how many requested amenities it has
            for amenity in filters['amenities']:
                # Create patterns for this amenity with variations
                amenity_pattern = re.compile(r'\b' + re.escape(amenity) + r'\b', re.IGNORECASE)
                
                # Look in amenities field
                filtered_data['amenity_score'] += filtered_data['amenities'].apply(
                    lambda x: 1 if amenity_pattern.search(str(x)) else 0
                )
                
                # Also check description for amenities
                filtered_data['amenity_score'] += filtered_data['description'].apply(
                    lambda x: 0.5 if amenity_pattern.search(str(x)) else 0
                )
            
            # Filter to include only hotels with at least one matching amenity
            filtered_data = filtered_data[filtered_data['amenity_score'] > 0]
            
            # Sort by amenity score (highest first)
            filtered_data = filtered_data.sort_values('amenity_score', ascending=False)
        
        # If we have results, apply secondary filters
        if not filtered_data.empty:
            # 2. Filter by rating (secondary)
            if 'min_rating' in filters:
                filtered_data = filtered_data[filtered_data['rating'] >= filters['min_rating']]
            elif 'rating_level' in filters and filters['rating_level'] == 'high':
                filtered_data = filtered_data[filtered_data['rating'] >= 4.0]
            
            # 3. Filter by price (tertiary)
            if 'max_price' in filters:
                filtered_data = filtered_data[filtered_data['price'] <= filters['max_price']]
            
            # 4. Filter by location (quaternary)
            if 'location' in filters:
                location_pattern = re.compile(filters['location'], re.IGNORECASE)
                location_filtered = filtered_data[filtered_data['location'].apply(
                    lambda x: bool(location_pattern.search(str(x)))
                )]
                
                # Only apply location filter if it doesn't empty the results
                if not location_filtered.empty:
                    filtered_data = location_filtered
        
        # If still no results, try a more relaxed approach focusing on description
        if filtered_data.empty and 'amenities' in filters and filters['amenities']:
            # Try with a broader search in the description
            filtered_data = original_data.copy()
            filtered_data['amenity_score'] = 0
            
            for amenity in filters['amenities']:
                # Search more broadly in the description
                filtered_data['amenity_score'] += filtered_data['description'].apply(
                    lambda x: 1 if amenity.lower() in str(x).lower() else 0
                )
            
            # Filter to hotels with at least one amenity mention
            filtered_data = filtered_data[filtered_data['amenity_score'] > 0]
            filtered_data = filtered_data.sort_values('amenity_score', ascending=False)
        
        return filtered_data
    
    def _filter_category_hotels(self, data, filters):
        """
        Filter for category/type-based hotels.
        Priority: category → rating ≥ X → price ≤ Y → location
        """
        # 1. Filter by category (primary)
        if 'category' in filters:
            category_pattern = re.compile(filters['category'], re.IGNORECASE)
            data = data[data['category'].apply(lambda x: bool(category_pattern.search(str(x))))]
        
        # 2. Filter by rating (secondary)
        if 'min_rating' in filters:
            data = data[data['rating'] >= filters['min_rating']]
        elif 'rating_level' in filters and filters['rating_level'] == 'high':
            data = data[data['rating'] >= 4.0]
        
        # 3. Filter by price (tertiary)
        if 'max_price' in filters:
            data = data[data['price'] <= filters['max_price']]
        
        # 4. Filter by location (quaternary)
        if 'location' in filters:
            location_pattern = re.compile(filters['location'], re.IGNORECASE)
            data = data[data['location'].apply(lambda x: bool(location_pattern.search(str(x))))]
        
        return data
    
    def _filter_location_hotels(self, data, filters):
        """
        Filter for location-based hotels.
        Priority: location → rating ≥ X → price ≤ Y → amenities
        """
        # 1. Filter by location (primary)
        if 'location' in filters:
            location_pattern = re.compile(filters['location'], re.IGNORECASE)
            data = data[data['location'].apply(lambda x: bool(location_pattern.search(str(x))))]
        
        # 2. Filter by rating (secondary)
        if 'min_rating' in filters:
            data = data[data['rating'] >= filters['min_rating']]
        elif 'rating_level' in filters and filters['rating_level'] == 'high':
            data = data[data['rating'] >= 4.0]
        
        # 3. Filter by price (tertiary)
        if 'max_price' in filters:
            data = data[data['price'] <= filters['max_price']]
        
        # 4. Filter by amenities (quaternary)
        if 'amenities' in filters and filters['amenities']:
            for amenity in filters['amenities']:
                amenity_pattern = re.compile(amenity, re.IGNORECASE)
                data = data[data['amenities'].apply(lambda x: bool(amenity_pattern.search(str(x))))]
        
        return data
    
    def _filter_price_quality_mix_hotels(self, data, filters):
        """
        Filter for price+quality mix hotels.
        Priority: rating ≥ X → price ≤ Y → location → amenities
        """
        # 1. Filter by rating (primary)
        if 'min_rating' in filters:
            data = data[data['rating'] >= filters['min_rating']]
        elif 'rating_level' in filters and filters['rating_level'] == 'high':
            data = data[data['rating'] >= 4.0]
        else:
            # Default to 3.5+ rating for "quality" if not specified
            data = data[data['rating'] >= 3.5]
        
        # 2. Filter by price (secondary)
        if 'max_price' in filters:
            data = data[data['price'] <= filters['max_price']]
        
        # 3. Filter by location (tertiary)
        if 'location' in filters:
            location_pattern = re.compile(filters['location'], re.IGNORECASE)
            data = data[data['location'].apply(lambda x: bool(location_pattern.search(str(x))))]
        
        # 4. Filter by amenities (quaternary)
        if 'amenities' in filters and filters['amenities']:
            for amenity in filters['amenities']:
                amenity_pattern = re.compile(amenity, re.IGNORECASE)
                data = data[data['amenities'].apply(lambda x: bool(amenity_pattern.search(str(x))))]
        
        return data
    
    def _sort_hotels_by_intent(self, data, intent):
        """Sort filtered hotels based on the intent."""
        if not data.empty:
            if intent == 'cheap':
                # Sort by price (ascending), then rating (descending)
                return data.sort_values(['price', 'rating'], ascending=[True, False])
            
            elif intent == 'expensive':
                # Sort by price (descending), then rating (descending)
                return data.sort_values(['price', 'rating'], ascending=[False, False])
            
            elif intent == 'best':
                # Sort by rating (descending)
                return data.sort_values('rating', ascending=False)
            
            elif intent == 'worst':
                # Sort by rating (ascending), then price (descending)
                return data.sort_values(['rating', 'price'], ascending=[True, False])
            
            elif intent == 'location' or intent == 'category' or intent == 'amenities':
                # Sort by rating (descending), then price (ascending)
                return data.sort_values(['rating', 'price'], ascending=[False, True])
            
            else:  # price_quality_mix
                # Calculate a score based on rating and price
                if 'score' not in data.columns:
                    # Normalize price to 0-1 scale (inverted so lower is better)
                    max_price = data['price'].max() if data['price'].max() > 0 else 1
                    norm_price = 1 - (data['price'] / max_price)
                    
                    # Normalize rating to 0-1 scale
                    norm_rating = data['rating'] / 5
                    
                    # Combine for a value score (70% rating, 30% price)
                    data['score'] = (0.7 * norm_rating) + (0.3 * norm_price)
                
                # Sort by the computed score (descending)
                return data.sort_values('score', ascending=False)
        
        return data
    
    def recommend_vehicles(self, filters, max_results=5):
        """
        Generate vehicle rental recommendations based on filters.
        
        Args:
            filters (dict): Dictionary of filters
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of formatted vehicle recommendations
        """
        try:
            logger.info(f"Generating vehicle recommendations with filters: {filters}")
            self.suggested_alternatives = []  # Reset suggested alternatives
            
            # Get a copy of the data to filter
            filtered_data = self.vehicles_data.copy()
            
            # Determine the filtering strategy based on intent
            intent = filters.get('intent', 'price_quality_mix')
            
            # Apply filters based on the intent
            if intent == 'cheap':
                # Case 1: Cheapest Rentals (pricePerDay ≤ X → type → Ratings → pickupLocation)
                filtered_data = self._filter_cheap_vehicles(filtered_data, filters)
            
            elif intent == 'expensive':
                # Case 2: Most Expensive Rental (pricePerDay = max → type → Ratings → capacity)
                filtered_data = self._filter_expensive_vehicles(filtered_data, filters)
            
            elif intent == 'best':
                # Case 3: Top-Rated Vehicles (Ratings ≥ X → type → pricePerDay → capacity)
                filtered_data = self._filter_best_vehicles(filtered_data, filters)
            
            elif intent == 'worst':
                # Case 4: Low-Rated Vehicles (Ratings ≤ X → type → pricePerDay → capacity)
                filtered_data = self._filter_worst_vehicles(filtered_data, filters)
            
            elif intent == 'type':
                # Case 5: Type-Based (type → pricePerDay → Ratings → pickupLocation)
                filtered_data = self._filter_type_vehicles(filtered_data, filters)
            
            elif intent == 'capacity':
                # Case 6: Capacity-Based (Passengers ≥ N → type → pricePerDay → Ratings)
                filtered_data = self._filter_capacity_vehicles(filtered_data, filters)
            
            elif intent == 'location':
                # Case 7: Location-Based (pickupLocation/dropOffLocation → type → pricePerDay → Ratings)
                filtered_data = self._filter_location_vehicles(filtered_data, filters)
            
            else:  # price_quality_mix
                # Case 8: Price+Quality Mix (Ratings ≥ X → pricePerDay ≤ Y → type → capacity)
                filtered_data = self._filter_price_quality_mix_vehicles(filtered_data, filters)
            
            # Sort results based on the intent
            filtered_data = self._sort_vehicles_by_intent(filtered_data, intent)
            
            # Format results for display
            results = []
            for _, row in filtered_data.head(max_results).iterrows():
                results.append(format_vehicle(row))
            
            logger.info(f"Found {len(results)} vehicle recommendations")
            return results
            
        except Exception as e:
            logger.error(f"Error generating vehicle recommendations: {str(e)}")
            return []
            
    def _filter_cheap_vehicles(self, data, filters):
        """
        Filter for cheap vehicles.
        Priority: pricePerDay ≤ X → type → Ratings → pickupLocation
        """
        # 1. Filter by price (primary)
        if 'max_price' in filters:
            data = data[data['pricePerDay'] <= filters['max_price']]
        elif 'price_level' in filters and filters['price_level'] == 'cheap':
            # Use a reasonable default for "cheap" if no specific price given
            data = data.sort_values('pricePerDay')
            data = data.head(int(len(data) * 0.3))  # Top 30% cheapest
        
        # 2. Filter by vehicle type (secondary)
        if 'vehicle_type' in filters and filters['vehicle_type']:
            type_pattern = re.compile(filters['vehicle_type'], re.IGNORECASE)
            data = data[data['type'].apply(lambda x: bool(type_pattern.search(str(x))))]
        
        # 3. Filter by rating (tertiary)
        if 'min_rating' in filters:
            data = data[data['Ratings'] >= filters['min_rating']]
        elif 'rating_level' in filters and filters['rating_level'] == 'high':
            data = data[data['Ratings'] >= 4.0]
        
        # 4. Filter by pickup location (quaternary)
        if 'location' in filters:
            location_pattern = re.compile(filters['location'], re.IGNORECASE)
            pickup_match = data['pickupLocation'].apply(lambda x: bool(location_pattern.search(str(x))))
            data = data[pickup_match]
        
        return data
    
    def _filter_expensive_vehicles(self, data, filters):
        """
        Filter for expensive vehicles.
        Priority: pricePerDay = max → type → Ratings → capacity
        """
        # 1. Filter by price (primary)
        if 'min_price' in filters:
            data = data[data['pricePerDay'] >= filters['min_price']]
        elif 'price_level' in filters and filters['price_level'] == 'expensive':
            # Use a reasonable default for "expensive" if no specific price given
            data = data.sort_values('pricePerDay', ascending=False)
            data = data.head(int(len(data) * 0.3))  # Top 30% most expensive
        
        # 2. Filter by vehicle type (secondary)
        if 'vehicle_type' in filters and filters['vehicle_type']:
            type_pattern = re.compile(filters['vehicle_type'], re.IGNORECASE)
            data = data[data['type'].apply(lambda x: bool(type_pattern.search(str(x))))]
        
        # 3. Filter by rating (tertiary)
        if 'min_rating' in filters:
            data = data[data['Ratings'] >= filters['min_rating']]
        elif 'rating_level' in filters and filters['rating_level'] == 'high':
            data = data[data['Ratings'] >= 4.0]
        
        # 4. Filter by passenger capacity (quaternary)
        if 'passengers' in filters and filters['passengers']:
            data = data[data['Passengers'] >= filters['passengers']]
        
        return data
    
    def _filter_best_vehicles(self, data, filters):
        """
        Filter for best/highest-rated vehicles.
        Priority: Ratings ≥ X → type → pricePerDay → capacity
        """
        # 1. Filter by rating (primary)
        if 'min_rating' in filters:
            data = data[data['Ratings'] >= filters['min_rating']]
        elif 'rating_level' in filters and filters['rating_level'] == 'high':
            data = data[data['Ratings'] >= 4.0]
        else:
            # Default to 4.0+ rating for "best" if not specified
            data = data[data['Ratings'] >= 4.0]
        
        # 2. Filter by vehicle type (secondary)
        if 'vehicle_type' in filters and filters['vehicle_type']:
            type_pattern = re.compile(filters['vehicle_type'], re.IGNORECASE)
            data = data[data['type'].apply(lambda x: bool(type_pattern.search(str(x))))]
        
        # 3. Filter by price (tertiary, optional)
        if 'max_price' in filters:
            data = data[data['pricePerDay'] <= filters['max_price']]
        
        # 4. Filter by passenger capacity (quaternary)
        if 'passengers' in filters and filters['passengers']:
            data = data[data['Passengers'] >= filters['passengers']]
        
        return data
    
    def _filter_worst_vehicles(self, data, filters):
        """
        Filter for worst/lowest-rated vehicles.
        Priority: Ratings ≤ X → type → pricePerDay → capacity
        """
        # 1. Filter by rating (primary)
        if 'max_rating' in filters:
            data = data[data['Ratings'] <= filters['max_rating']]
        elif 'rating_level' in filters and filters['rating_level'] == 'low':
            data = data[data['Ratings'] <= 3.0]
        else:
            # Default to 3.0- rating for "worst" if not specified
            data = data[data['Ratings'] <= 3.0]
        
        # 2. Filter by vehicle type (secondary)
        if 'vehicle_type' in filters and filters['vehicle_type']:
            type_pattern = re.compile(filters['vehicle_type'], re.IGNORECASE)
            data = data[data['type'].apply(lambda x: bool(type_pattern.search(str(x))))]
        
        # 3. Filter by price (tertiary, optional)
        if 'min_price' in filters:
            data = data[data['pricePerDay'] >= filters['min_price']]
        
        # 4. Filter by passenger capacity (quaternary)
        if 'passengers' in filters and filters['passengers']:
            data = data[data['Passengers'] >= filters['passengers']]
        
        return data
    
    def _filter_type_vehicles(self, data, filters):
        """
        Filter for type-based vehicles.
        Priority: type → pricePerDay → Ratings → pickupLocation
        """
        # 1. Filter by vehicle type (primary)
        if 'vehicle_type' in filters and filters['vehicle_type']:
            type_pattern = re.compile(filters['vehicle_type'], re.IGNORECASE)
            data = data[data['type'].apply(lambda x: bool(type_pattern.search(str(x))))]
        
        # 2. Filter by price (secondary)
        if 'max_price' in filters:
            data = data[data['pricePerDay'] <= filters['max_price']]
        
        # 3. Filter by rating (tertiary)
        if 'min_rating' in filters:
            data = data[data['Ratings'] >= filters['min_rating']]
        elif 'rating_level' in filters and filters['rating_level'] == 'high':
            data = data[data['Ratings'] >= 4.0]
        
        # 4. Filter by pickup location (quaternary)
        if 'location' in filters:
            location_pattern = re.compile(filters['location'], re.IGNORECASE)
            pickup_match = data['pickupLocation'].apply(lambda x: bool(location_pattern.search(str(x))))
            data = data[pickup_match]
        
        return data
    
    def _filter_capacity_vehicles(self, data, filters):
        """
        Filter for capacity-based vehicles.
        Priority: Passengers ≥ N → type → pricePerDay → Ratings
        """
        # 1. Filter by passenger capacity (primary)
        if 'passengers' in filters and filters['passengers']:
            data = data[data['Passengers'] >= filters['passengers']]
        
        # 2. Filter by vehicle type (secondary)
        if 'vehicle_type' in filters and filters['vehicle_type']:
            type_pattern = re.compile(filters['vehicle_type'], re.IGNORECASE)
            data = data[data['type'].apply(lambda x: bool(type_pattern.search(str(x))))]
        
        # 3. Filter by price (tertiary)
        if 'max_price' in filters:
            data = data[data['pricePerDay'] <= filters['max_price']]
        
        # 4. Filter by rating (quaternary)
        if 'min_rating' in filters:
            data = data[data['Ratings'] >= filters['min_rating']]
        elif 'rating_level' in filters and filters['rating_level'] == 'high':
            data = data[data['Ratings'] >= 4.0]
        
        return data
    
    def _filter_location_vehicles(self, data, filters):
        """
        Filter for location-based vehicles.
        Priority: pickupLocation/dropOffLocation → type → pricePerDay → Ratings
        """
        # 1. Filter by location (primary)
        if 'location' in filters:
            location_pattern = re.compile(filters['location'], re.IGNORECASE)
            pickup_match = data['pickupLocation'].apply(lambda x: bool(location_pattern.search(str(x))))
            dropoff_match = data['dropOffLocation'].apply(lambda x: bool(location_pattern.search(str(x))))
            data = data[pickup_match | dropoff_match]
        
        # 2. Filter by vehicle type (secondary)
        if 'vehicle_type' in filters and filters['vehicle_type']:
            type_pattern = re.compile(filters['vehicle_type'], re.IGNORECASE)
            data = data[data['type'].apply(lambda x: bool(type_pattern.search(str(x))))]
        
        # 3. Filter by price (tertiary)
        if 'max_price' in filters:
            data = data[data['pricePerDay'] <= filters['max_price']]
        
        # 4. Filter by rating (quaternary)
        if 'min_rating' in filters:
            data = data[data['Ratings'] >= filters['min_rating']]
        elif 'rating_level' in filters and filters['rating_level'] == 'high':
            data = data[data['Ratings'] >= 4.0]
        
        return data
    
    def _filter_price_quality_mix_vehicles(self, data, filters):
        """
        Filter for price+quality mix vehicles.
        Priority: Ratings ≥ X → pricePerDay ≤ Y → type → capacity
        """
        # 1. Filter by rating (primary)
        if 'min_rating' in filters:
            data = data[data['Ratings'] >= filters['min_rating']]
        elif 'rating_level' in filters and filters['rating_level'] == 'high':
            data = data[data['Ratings'] >= 4.0]
        else:
            # Default to 3.5+ rating for "quality" if not specified
            data = data[data['Ratings'] >= 3.5]
        
        # 2. Filter by price (secondary)
        if 'max_price' in filters:
            data = data[data['pricePerDay'] <= filters['max_price']]
        
        # 3. Filter by vehicle type (tertiary)
        if 'vehicle_type' in filters and filters['vehicle_type']:
            type_pattern = re.compile(filters['vehicle_type'], re.IGNORECASE)
            data = data[data['type'].apply(lambda x: bool(type_pattern.search(str(x))))]
        
        # 4. Filter by passenger capacity (quaternary)
        if 'passengers' in filters and filters['passengers']:
            data = data[data['Passengers'] >= filters['passengers']]
        
        return data
    
    def _sort_vehicles_by_intent(self, data, intent):
        """Sort filtered vehicles based on the intent."""
        if not data.empty:
            if intent == 'cheap':
                # Sort by price (ascending), then rating (descending)
                return data.sort_values(['pricePerDay', 'Ratings'], ascending=[True, False])
            
            elif intent == 'expensive':
                # Sort by price (descending), then rating (descending)
                return data.sort_values(['pricePerDay', 'Ratings'], ascending=[False, False])
            
            elif intent == 'best':
                # Sort by rating (descending), then price (ascending)
                return data.sort_values(['Ratings', 'pricePerDay'], ascending=[False, True])
            
            elif intent == 'worst':
                # Sort by rating (ascending), then price (descending)
                return data.sort_values(['Ratings', 'pricePerDay'], ascending=[True, False])
            
            elif intent in ['type', 'location', 'capacity']:
                # Sort by rating (descending), then price (ascending)
                return data.sort_values(['Ratings', 'pricePerDay'], ascending=[False, True])
            
            else:  # price_quality_mix
                # Calculate a score based on rating and price
                if 'score' not in data.columns:
                    # Normalize price to 0-1 scale (inverted so lower is better)
                    max_price = data['pricePerDay'].max() if data['pricePerDay'].max() > 0 else 1
                    norm_price = 1 - (data['pricePerDay'] / max_price)
                    
                    # Normalize rating to 0-1 scale
                    norm_rating = data['Ratings'] / 5
                    
                    # Combine for a value score (70% rating, 30% price)
                    data['score'] = (0.7 * norm_rating) + (0.3 * norm_price)
                
                # Sort by the computed score (descending)
                return data.sort_values('score', ascending=False)
        
        return data
