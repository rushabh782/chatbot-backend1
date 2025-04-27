"""
Utility functions for formatting and displaying recommendation results.
"""
import textwrap

def format_restaurant(restaurant):
    """
    Format restaurant data for display.
    
    Args:
        restaurant (pd.Series): Restaurant data
        
    Returns:
        str: Formatted restaurant information
    """
    # Calculate price range string
    price_range = ""
    if restaurant['price_range_from'] > 0 and restaurant['price_range_to'] > 0:
        price_range = f"₹{int(restaurant['price_range_from'])} - ₹{int(restaurant['price_range_to'])}"
    elif restaurant['price_range_to'] > 0:
        price_range = f"Up to ₹{int(restaurant['price_range_to'])}"
    elif restaurant['price_range_from'] > 0:
        price_range = f"From ₹{int(restaurant['price_range_from'])}"
    else:
        price_range = "Price not available"
    
    # Calculate rating stars
    rating = restaurant['rating'] if not restaurant.get('score') else restaurant['score'] * 5
    if not rating or rating != rating:  # Check for NaN
        rating_stars = "No ratings"
    else:
        full_stars = int(rating)
        half_star = round(rating - full_stars) >= 0.5
        rating_stars = "★" * full_stars + ("½" if half_star else "")
    
    # Get review count info
    review_count = restaurant.get('review_count', 0)
    review_info = f" ({review_count} reviews)" if review_count else ""
    
    # Format cuisines
    cuisines = restaurant.get('cuisines', '')
    if cuisines and cuisines != cuisines:  # Check for NaN
        cuisines = "Cuisine not specified"
    
    # Wrap address text
    address = textwrap.fill(restaurant.get('address', 'Address not available'), width=60)
    
    # Format phone number
    phone = restaurant.get('Phone', 'Phone not available')
    
    # Build the formatted string
    formatted = (
        f"{restaurant['name']}\n"
        f"Rating: {rating_stars}{review_info}\n"
        f"Price: {price_range}\n"
        f"Cuisines: {cuisines}\n"
        f"Address: {address}\n"
        f"Phone: {phone}"
    )
    
    return formatted

def format_hotel(hotel):
    """
    Format hotel data for display.
    
    Args:
        hotel (pd.Series): Hotel data
        
    Returns:
        str: Formatted hotel information
    """
    # Calculate rating stars
    rating = hotel['rating'] if not hotel.get('score') else hotel['score'] * 5
    if not rating or rating != rating:  # Check for NaN
        rating_stars = "No ratings"
    else:
        full_stars = int(rating)
        half_star = round(rating - full_stars) >= 0.5
        rating_stars = "★" * full_stars + ("½" if half_star else "")
    
    # Process price
    price = f"₹{int(hotel['price'])}" if hotel.get('price') else "Price not available"
    
    # Process category
    category = hotel.get('category', 'Not specified')
    
    # Process amenities
    amenities = hotel.get('amenities', '')
    if not amenities:
        amenities_list = "Not specified"
    else:
        # Try to clean up amenities - they might be in a CSV-like format
        amenities = str(amenities)
        amenities_list = ', '.join([a.strip() for a in amenities.split(',') if a.strip()])
        amenities_list = textwrap.fill(amenities_list, width=60)
    
    # Process location
    location = hotel.get('location', 'Location not available')
    location = textwrap.fill(location, width=60)
    
    # Process description (truncate if too long)
    description = hotel.get('description', '')
    if description:
        description = textwrap.fill(description[:200] + '...' if len(description) > 200 else description, width=60)
    else:
        description = "No description available"
    
    # Build the formatted string
    formatted = (
        f"{hotel['name']}\n"
        f"Rating: {rating_stars}\n"
        f"Price: {price}\n"
        f"Category: {category}\n"
        f"Location: {location}\n"
        f"Amenities: {amenities_list}\n"
        f"Description: {description}"
    )
    
    return formatted

def format_vehicle(vehicle):
    """
    Format vehicle data for display.
    
    Args:
        vehicle (pd.Series): Vehicle data
        
    Returns:
        str: Formatted vehicle information
    """
    # Calculate rating stars
    rating = vehicle.get('Ratings')
    if not rating or rating != rating:  # Check for NaN
        rating_stars = "No ratings"
    else:
        full_stars = int(rating)
        half_star = round(rating - full_stars) >= 0.5
        rating_stars = "★" * full_stars + ("½" if half_star else "")
    
    # Process prices
    daily_price = f"₹{int(vehicle['pricePerDay'])}" if vehicle.get('pricePerDay') else "Not available"
    hourly_price = f"₹{int(vehicle['pricePerHour'])}" if vehicle.get('pricePerHour') else "Not available"
    
    # Process type and preference
    vehicle_type = vehicle.get('type', 'Not specified')
    preference = vehicle.get('Preference', 'Not specified')
    
    # Process passenger capacity
    passengers = vehicle.get('Passengers', 'Not specified')
    
    # Process locations
    pickup = vehicle.get('pickupLocation', 'Not specified')
    pickup = textwrap.fill(pickup, width=60)
    
    dropoff = vehicle.get('dropOffLocation', 'Not specified')
    dropoff = textwrap.fill(dropoff, width=60)
    
    # Extract model details
    model_name = vehicle.get('name', 'Not specified')
    
    # Try to extract color information from model_info if available
    model_info = vehicle.get('model_info', {})
    colors = []
    if isinstance(model_info, dict):
        for key, value in model_info.items():
            if isinstance(value, dict) and 'color' in value:
                colors.append(value['color'])
    
    color_info = ", ".join(colors) if colors else "Not specified"
    
    # Build the formatted string
    formatted = (
        f"{model_name} ({vehicle_type.title()})\n"
        f"Rating: {rating_stars}\n"
        f"Price: {daily_price}/day | {hourly_price}/hour\n"
        f"Preference: {preference}\n"
        f"Passenger Capacity: {passengers}\n"
        f"Available Colors: {color_info}\n"
        f"Pickup Locations: {pickup}\n"
        f"Drop-off Locations: {dropoff}"
    )
    
    return formatted
