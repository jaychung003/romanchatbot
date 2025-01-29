# Roman Empire Chatbot with Phoenix Monitoring

## Prerequisites
- Python 3.8 or higher
- OpenAI API key

## Setup Instructions

1. Clone the repository and navigate to the project directory

2. Create a Python virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install arize-phoenix>=3.22.0 openinference-instrumentation-openai streamlit fastapi uvicorn jinja2 langchain-community wikipedia openai languchain-openai chromadb
```

4. Set up your OpenAI API key as an environment variable:
```bash
# On Unix/MacOS:
export OPENAI_API_KEY='your-api-key-here'

# On Windows (Command Prompt):
set OPENAI_API_KEY=your-api-key-here

# On Windows (PowerShell):
$env:OPENAI_API_KEY='your-api-key-here'
```

## Running the Application

1. Start the Phoenix monitoring dashboard:
```bash
python phoenix_combined.py
```
This will start the monitoring dashboard at http://localhost:6008

2. In a new terminal window, start the Streamlit application:
```bash
streamlit run main.py
```
This will start the chatbot interface at http://localhost:8501

## Accessing the Applications
- Chatbot Interface: http://localhost:8501
- Monitoring Dashboard: http://localhost:6008

## Troubleshooting
- Ensure all required ports (6008 and 8501) are available
- Check that your OpenAI API key is correctly set in the environment
- Verify that you have activated the virtual environment before running the applications
- Check the terminal output for any error messages
- If the Phoenix dashboard doesn't load, try refreshing the page after a few seconds

## Project Structure
- `main.py`: Streamlit chatbot interface
- `phoenix_combined.py`: Phoenix monitoring dashboard
- `templates/`: HTML templates for the monitoring interface

## Getting Help
If you encounter any issues:
1. Check the terminal output for error messages
2. Ensure all dependencies are correctly installed
3. Verify your OpenAI API key is valid and properly set# romanchatbot
