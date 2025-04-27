/**
 * This script is used to test the API handler without running the full server.
 * It executes a single query and logs the response.
 */
const { spawn } = require('child_process');

// The query to test
const query = process.argv[2] || "Find Italian restaurants in Bandra";

console.log(`Testing with query: "${query}"`);

// Execute the Python API handler
const pythonProcess = spawn('python', ['api_handler.py', query]);

let result = '';
let error = '';

// Collect data from stdout
pythonProcess.stdout.on('data', (data) => {
  result += data.toString();
});

// Collect any errors from stderr
pythonProcess.stderr.on('data', (data) => {
  error += data.toString();
  console.error(`Error: ${data}`);
});

// Handle process completion
pythonProcess.on('close', (code) => {
  if (code !== 0) {
    console.error(`Python process exited with code ${code}`);
    return;
  }

  try {
    // Parse and display the JSON result
    const response = JSON.parse(result);
    console.log(JSON.stringify(response, null, 2));
    
    console.log(`\nQuery type: ${response.query_type}`);
    console.log(`Results found: ${response.count}`);
  } catch (e) {
    console.error('Failed to parse Python output:', e);
    console.log('Raw output:', result);
  }
});