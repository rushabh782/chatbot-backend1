"""
Module for loading and preprocessing data from CSV files.
"""
import os
import pandas as pd
import logging
import ast
import re

logger = logging.getLogger(__name__)

class DataLoader:
    """Class for loading and preprocessing data from CSV files."""
    
    def __init__(self):
        """Initialize the DataLoader class."""
        self.data_dir = "attached_assets"
        self.restaurants_file = os.path.join(self.data_dir, "tripadvisorr.csv")
        self.hotels_file = os.path.join(self.data_dir, "hotels_data.csv")
        self.vehicles_file = os.path.join(self.data_dir, "vehicles_data.csv")
    
    def load_restaurants_data(self):
        """
        Load and preprocess restaurant data from CSV file.
        
        Returns:
            pandas.DataFrame: Preprocessed restaurant data
        """
        try:
            logger.info(f"Loading restaurant data from {self.restaurants_file}")
            restaurants_df = pd.read_csv(self.restaurants_file)
            
            # Clean and preprocess data
            # Convert price range columns to numeric
            restaurants_df['price_range_from'] = pd.to_numeric(restaurants_df['price_range_from'], errors='coerce')
            restaurants_df['price_range_to'] = pd.to_numeric(restaurants_df['price_range_to'], errors='coerce')
            
            # Convert rating to numeric
            restaurants_df['rating'] = pd.to_numeric(restaurants_df['rating'], errors='coerce')
            
            # Convert review counts to numeric
            restaurants_df['review_count'] = pd.to_numeric(restaurants_df['review_count'], errors='coerce')
            
            # Fill NaN values with appropriate defaults
            restaurants_df['price_range_from'] = restaurants_df['price_range_from'].fillna(0)
            restaurants_df['price_range_to'] = restaurants_df['price_range_to'].fillna(1000)  # Default upper price
            
            # Lowercase address and cuisines for easier searching
            restaurants_df['address'] = restaurants_df['address'].fillna('').astype(str).str.lower()
            restaurants_df['cuisines'] = restaurants_df['cuisines'].fillna('').astype(str).str.lower()
            
            logger.info(f"Successfully loaded {len(restaurants_df)} restaurants")
            return restaurants_df
            
        except Exception as e:
            logger.error(f"Error loading restaurant data: {str(e)}")
            raise
    
    def load_hotels_data(self):
        """
        Load and preprocess hotel data from CSV file.
        
        Returns:
            pandas.DataFrame: Preprocessed hotel data
        """
        try:
            logger.info(f"Loading hotel data from {self.hotels_file}")
            hotels_df = pd.read_csv(self.hotels_file)
            
            # Clean and preprocess data
            # Convert price to numeric
            hotels_df['price'] = pd.to_numeric(hotels_df['price'], errors='coerce')
            
            # Convert rating to numeric
            hotels_df['rating'] = pd.to_numeric(hotels_df['rating'], errors='coerce')
            
            # Process description and location fields
            hotels_df['description'] = hotels_df['description'].fillna('').astype(str)
            hotels_df['location'] = hotels_df['location'].fillna('').astype(str).str.lower()
            
            # Process amenities
            hotels_df['amenities'] = hotels_df['amenities'].fillna('').astype(str).str.lower()
            
            # Process category
            hotels_df['category'] = hotels_df['category'].fillna('').astype(str).str.lower()
            
            logger.info(f"Successfully loaded {len(hotels_df)} hotels")
            return hotels_df
            
        except Exception as e:
            logger.error(f"Error loading hotel data: {str(e)}")
            raise
    
    def load_vehicles_data(self):
        """
        Load and preprocess vehicle rental data from CSV file.
        
        Returns:
            pandas.DataFrame: Preprocessed vehicle rental data
        """
        try:
            logger.info(f"Loading vehicle data from {self.vehicles_file}")
            vehicles_df = pd.read_csv(self.vehicles_file)
            
            # Clean and preprocess data
            # Convert price fields to numeric
            vehicles_df['pricePerDay'] = pd.to_numeric(vehicles_df['pricePerDay'], errors='coerce')
            vehicles_df['pricePerHour'] = pd.to_numeric(vehicles_df['pricePerHour'], errors='coerce')
            
            # Convert rating to numeric
            vehicles_df['Ratings'] = pd.to_numeric(vehicles_df['Ratings'], errors='coerce')
            
            # Convert passengers to numeric
            vehicles_df['Passengers'] = pd.to_numeric(vehicles_df['Passengers'], errors='coerce')
            
            # Process pickup and dropoff locations
            vehicles_df['pickupLocation'] = vehicles_df['pickupLocation'].fillna('').astype(str).str.lower()
            vehicles_df['dropOffLocation'] = vehicles_df['dropOffLocation'].fillna('').astype(str).str.lower()
            
            # Process preference
            vehicles_df['Preference'] = vehicles_df['Preference'].fillna('').astype(str).str.lower()
            
            # Process vehicle type
            vehicles_df['type'] = vehicles_df['type'].fillna('').astype(str).str.lower()
            
            # Process model information (attempt to safely parse model json strings)
            def parse_model_info(model_str):
                if pd.isna(model_str) or model_str == '':
                    return {}
                
                try:
                    # Try to safely evaluate the string as a dictionary
                    return ast.literal_eval(model_str)
                except (SyntaxError, ValueError):
                    # If that fails, try to extract color information with regex
                    colors = re.findall(r"'color': '([^']+)'", model_str)
                    if colors:
                        return {'colors': colors}
                    return {}
            
            vehicles_df['model_info'] = vehicles_df['model'].apply(parse_model_info)
            
            logger.info(f"Successfully loaded {len(vehicles_df)} vehicles")
            return vehicles_df
            
        except Exception as e:
            logger.error(f"Error loading vehicle data: {str(e)}")
            raise
