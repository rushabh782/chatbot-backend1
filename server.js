require('dotenv').config();
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;
const flaskApiUrl = process.env.FLASK_API_URL || 'http://localhost:5000';

app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

// API proxy to call Flask (if needed)
app.post('/api/recommendations', (req, res) => {
  const { query } = req.body;

  if (!query) {
    return res.status(400).json({ error: 'Query is required' });
  }

  const pythonProcess = spawn('python', ['api_handler.py', query], {
    cwd: path.resolve(__dirname)
  });

  let result = '';
  let error = '';

  pythonProcess.stdout.on('data', (data) => {
    result += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    error += data.toString();
  });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      console.error(`Python exited with code ${code}`);
      console.error(error);
      return res.status(500).json({ error: 'Python error', details: error });
    }

    try {
      const jsonStart = result.indexOf('{');
      const jsonEnd = result.lastIndexOf('}') + 1;
      if (jsonStart >= 0 && jsonEnd > 0) {
        const jsonContent = result.substring(jsonStart, jsonEnd);
        const recommendations = JSON.parse(jsonContent);
        return res.json(recommendations);
      } else {
        throw new Error("No valid JSON found in output");
      }
    } catch (e) {
      return res.status(500).json({
        error: 'Failed to parse Python output',
        raw: result,
        details: e.message
      });
    }
  });
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Node.js server is running' });
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Node.js server running on port ${port}`);
});
