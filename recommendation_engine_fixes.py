"""
Improved recommendation functions with direct name lookup support
"""

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
        
        # Check for direct hotel name search
        original_query = filters.get('query', '').lower()
        
        # First try to find exact hotel name matches in the query
        for _, hotel in self.hotels_data.iterrows():
            hotel_name = str(hotel.get('name', '')).lower()
            if hotel_name and len(hotel_name) > 3 and hotel_name in original_query:
                logger.info(f"Found hotel name in query: {hotel_name}")
                hotel_row = self.hotels_data[self.hotels_data['name'].str.lower() == hotel_name]
                if not hotel_row.empty:
                    # Return the specific hotel
                    return [format_hotel(hotel_row.iloc[0])]
        
        # If no exact hotel name match, proceed with normal filtering
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
            # Case 5: Amenities-Based Hotel Search (amenities → rating ≥ X → price ≤ Y → location)
            filtered_data = self._filter_amenities_hotels(filtered_data, filters)
        
        elif intent == 'category':
            # Case 6: Category/Type-Based Hotel Search (category → rating ≥ X → price ≤ Y → location)
            filtered_data = self._filter_category_hotels(filtered_data, filters)
        
        elif intent == 'location':
            # Case 7: Location-Based Hotel Search (location → rating ≥ X → price ≤ Y → amenities)
            filtered_data = self._filter_location_hotels(filtered_data, filters)
        
        else:  # price_quality_mix
            # Case 8: Price+Quality Mix (rating ≥ X → price ≤ Y → location → amenities)
            filtered_data = self._filter_price_quality_mix_hotels(filtered_data, filters)
        
        # Sort results based on the intent
        filtered_data = self._sort_hotels_by_intent(filtered_data, intent)
        
        # Format results
        results = []
        for _, row in filtered_data.head(max_results).iterrows():
            results.append(format_hotel(row))
        
        # Handle no results case
        if not results:
            logger.info("No hotel recommendations found for the filters")
            return ["No hotels found matching your criteria. Try different preferences."]
            
        logger.info(f"Found {len(results)} hotel recommendations")
        return results
        
    except Exception as e:
        logger.error(f"Error generating hotel recommendations: {str(e)}")
        return ["Error generating hotel recommendations. Please try again with different criteria."]


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
        
        # Check for direct vehicle name search
        original_query = filters.get('query', '').lower()
        
        # First try to find exact vehicle name matches in the query
        for _, vehicle in self.vehicles_data.iterrows():
            vehicle_name = str(vehicle.get('name', '')).lower()
            if vehicle_name and len(vehicle_name) > 3 and vehicle_name in original_query:
                logger.info(f"Found vehicle name in query: {vehicle_name}")
                vehicle_row = self.vehicles_data[self.vehicles_data['name'].str.lower() == vehicle_name]
                if not vehicle_row.empty:
                    # Return the specific vehicle
                    return [format_vehicle(vehicle_row.iloc[0])]
                    
        # If no direct name match, continue with regular filtering
        filtered_data = self.vehicles_data.copy()
        
        # Determine the filtering strategy based on intent
        intent = filters.get('intent', 'price_quality_mix')
        
        # Apply filters based on the intent
        if intent == 'cheap':
            # Case 1: Cheapest Vehicles (pricePerDay ≤ X → type → Ratings → pickupLocation)
            filtered_data = self._filter_cheap_vehicles(filtered_data, filters)
        
        elif intent == 'expensive':
            # Case 2: Most Expensive Vehicles (pricePerDay = max → type → Ratings → capacity)
            filtered_data = self._filter_expensive_vehicles(filtered_data, filters)
        
        elif intent == 'best':
            # Case 3: Best-Rated Vehicles (Ratings ≥ X → type → pricePerDay → capacity)
            filtered_data = self._filter_best_vehicles(filtered_data, filters)
        
        elif intent == 'worst':
            # Case 4: Worst-Rated Vehicles (Ratings ≤ X → type → pricePerDay → capacity)
            filtered_data = self._filter_worst_vehicles(filtered_data, filters)
        
        elif intent == 'type':
            # Case 5: Type-Based Vehicle Search (type → pricePerDay → Ratings → pickupLocation)
            filtered_data = self._filter_type_vehicles(filtered_data, filters)
        
        elif intent == 'capacity':
            # Case 6: Capacity-Based Vehicle Search (Passengers ≥ N → type → pricePerDay → Ratings)
            filtered_data = self._filter_capacity_vehicles(filtered_data, filters)
        
        elif intent == 'location':
            # Case 7: Location-Based Vehicle Search (pickupLocation/dropOffLocation → type → pricePerDay → Ratings)
            filtered_data = self._filter_location_vehicles(filtered_data, filters)
        
        else:  # price_quality_mix
            # Case 8: Price+Quality Mix (Ratings ≥ X → pricePerDay ≤ Y → type → capacity)
            filtered_data = self._filter_price_quality_mix_vehicles(filtered_data, filters)
        
        # Sort results based on the intent
        filtered_data = self._sort_vehicles_by_intent(filtered_data, intent)
        
        # Format results
        results = []
        for _, row in filtered_data.head(max_results).iterrows():
            results.append(format_vehicle(row))
        
        # Handle no results case
        if not results:
            logger.info("No vehicle recommendations found for the filters")
            return ["No vehicles found matching your criteria. Try different preferences."]
            
        logger.info(f"Found {len(results)} vehicle recommendations")
        return results
        
    except Exception as e:
        logger.error(f"Error generating vehicle recommendations: {str(e)}")
        return ["Error generating vehicle recommendations. Please try again with different criteria."]