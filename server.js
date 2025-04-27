const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');

const app = express();
const port = 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

// Route to get recommendations
app.post('/api/recommendations', (req, res) => {
  const { query } = req.body;
  
  if (!query) {
    return res.status(400).json({ error: 'Query is required' });
  }

  try {
    // Execute the Python script with the query
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
    });

    // Handle process completion
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error(`Python process exited with code ${code}`);
        console.error(`Error: ${error}`);
        return res.status(500).json({ error: 'Failed to get recommendations', details: error });
      }

      try {
        // Extract JSON content from the output (ignore NLTK debug messages)
        const jsonStartIndex = result.indexOf('{');
        const jsonEndIndex = result.lastIndexOf('}') + 1;
        
        if (jsonStartIndex >= 0 && jsonEndIndex > 0) {
          const jsonContent = result.substring(jsonStartIndex, jsonEndIndex);
          const recommendations = JSON.parse(jsonContent);
          res.json(recommendations);
        } else {
          console.error('Could not find valid JSON in the Python output');
          res.status(500).json({ error: 'Invalid format from Python script', raw: result });
        }
      } catch (e) {
        console.error('Failed to parse Python script output:', e);
        res.status(500).json({ error: 'Failed to parse recommendations', details: e.message, raw: result });
      }
    });
  } catch (e) {
    console.error('Failed to execute Python script:', e);
    res.status(500).json({ error: 'Internal server error', details: e.message });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Service is running' });
});

// Start the server
app.listen(port, '0.0.0.0', () => {
  console.log(`Recommendation API server running on port ${port}`);
});