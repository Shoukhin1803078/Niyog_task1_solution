# Niyog_task_1_solution

# Web Scraping with LLM Integration

I created this Fast API application provides a REST API for scraping website content and using an LLM (Large Language Model) to answer questions about the content. 

## Features

-  Scrapes content from any website URL
-  Uses OpenAI GPT models to answer questions about the website content
-  Handles JavaScript-rendered websites using Selenium
-  REST API interface with JSON request/response

## Installation

### Prerequisites

- Python 3.8 or higher
- Chrome browser (for Selenium WebDriver)
- OpenAI API key

### Clone the Repository

```
https://github.com/Shoukhin1803078/Niyog_task1_solution.git
cd Niyog_task1_solution
```

### Step-2 : Create a virtual environment and activate it
```
python -m venv venv
# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step-3 : Install Dependencies 
```
pip install -r requirements.txt
```
### Step-4 : Create .env file and Configure OpenAI API Key into .env
```
OPENAI_API_KEY = 'openai-api-key-here'
```

### Step-5 : Start the Development Server
```
uvircorn main:app --reload
or 
python main.py
```

In swagger UI API will be at http://localhost:8000/docs
In POSTMAN API will be available at http://127.0.0.1:8000/scrape-and-answer


### Sample Request Body:
{
    "url": "https://example.com",
    "question": "What is the main topic of this website?"
}
​
### Sample Response:
{
    "answer": "The main topic of this website is [topic]."
}


# My output (API Endpoint Test):
<img width="1710" alt="Screenshot 2025-05-11 at 5 50 31 PM" src="https://github.com/user-attachments/assets/05d5d76d-1ade-467a-877e-cdc1705bc769" />

<img width="1710" alt="Screenshot 2025-05-11 at 5 59 24 PM" src="https://github.com/user-attachments/assets/5d94038f-b8bc-4d24-adeb-9ce657df52c9" />
<img width="1710" alt="Screenshot 2025-05-11 at 5 59 50 PM" src="https://github.com/user-attachments/assets/57569c35-a417-40de-a260-fcb0d3f5ec3a" />

