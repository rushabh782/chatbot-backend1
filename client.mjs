/**
 * Example client for the Recommendation API (ESM version)
 * This script demonstrates how to make API requests to the recommendation system
 */
import fetch from 'node-fetch';

// The API base URL
const API_URL = 'http://localhost:3000/api';

/**
 * Get recommendations based on a natural language query
 * @param {string} query - The natural language query (e.g., "Find Italian restaurants in Mumbai")
 * @returns {Promise<object>} - The recommendations response
 */
async function getRecommendations(query) {
  try {
    const response = await fetch(`${API_URL}/recommendations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error getting recommendations:', error);
    throw error;
  }
}

/**
 * Check if the API is running
 * @returns {Promise<boolean>} - True if API is running
 */
async function checkApiHealth() {
  try {
    const response = await fetch(`${API_URL}/health`);
    
    if (!response.ok) {
      return false;
    }
    
    const data = await response.json();
    return data.status === 'ok';
  } catch (error) {
    console.error('API health check failed:', error);
    return false;
  }
}

/**
 * Display recommendations in a user-friendly format
 * @param {object} data - The API response
 */
function displayRecommendations(data) {
  console.log('\n===================================');
  console.log(`Results for: "${data.query}"`);
  console.log(`Category: ${data.category}`);
  console.log(`Found ${data.count} results`);
  console.log('===================================\n');

  if (data.count === 0) {
    console.log('No recommendations found for your query.');
    return;
  }

  data.recommendations.forEach((recommendation, index) => {
    console.log(`[${index + 1}] ${recommendation}`);
    console.log('-----------------------------------');
  });

  if (data.alternatives) {
    console.log('\nYou might also be interested in:');
    data.alternatives.forEach(alt => console.log(`- ${alt}`));
  }
}

/**
 * Main function to run the example
 */
async function main() {
  // Get the query from command line arguments
  const query = process.argv[2] || 'Find Italian restaurants in Mumbai';
  
  console.log(`Searching for: "${query}"`);
  
  try {
    // Check if API is running
    const isHealthy = await checkApiHealth();
    if (!isHealthy) {
      console.error('API is not running. Please start the API server first.');
      return;
    }
    
    // Get and display recommendations
    const recommendations = await getRecommendations(query);
    displayRecommendations(recommendations);
    
  } catch (error) {
    console.error('Failed to get recommendations:', error.message);
  }
}

// Run the example
main();