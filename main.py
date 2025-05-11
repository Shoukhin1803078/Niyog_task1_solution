
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn


import requests
from bs4 import BeautifulSoup
import openai
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

class ScrapingRequest(BaseModel):
    url: str
    question: str

class ScrapingResponse(BaseModel):
    answer: str


app = FastAPI(title="Website Scraping with LLM Integration API")
load_dotenv()
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")




def fetch_website_with_selenium(url):
    """Fetch the content of a website using Selenium for JavaScript-rendered content."""
    
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--disable-gpu")  
    chrome_options.add_argument("--window-size=1920,1080")  
    chrome_options.add_argument("--disable-extensions")  
    chrome_options.add_argument("--no-sandbox")  
    chrome_options.add_argument("--disable-dev-shm-usage")  
   
    try:
       
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
       
       
        driver.get(url)
       
       
        wait_time = 10
        time.sleep(wait_time)
       
       
        scroll_pause_time = 2
        last_height = driver.execute_script("return document.body.scrollHeight")
       
       
        for scroll in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
       
       
        html_content = driver.page_source
       
       
        driver.quit()
       
        return html_content
   
    except Exception as e:
        try:
            driver.quit()
        except:
            pass
        return None


def fetch_website_with_requests(url):
    """Fetch the content of a website using simple requests."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return None


def extract_text(html_content):
    """Extract text content from HTML."""
    if not html_content:
        return ""
   
    soup = BeautifulSoup(html_content, 'html.parser')
   
   
    for script in soup(["script", "style"]):
        script.extract()
   
   
    text = soup.get_text(separator=' ', strip=True)
   
   
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
   
    return text


def extract_all_content(html_content):
    """Extract various types of content from HTML."""
    if not html_content:
        return []
   
    soup = BeautifulSoup(html_content, 'html.parser')
    all_content_parts = []
   
   
    headings = []
    for i in range(1, 7):
        for heading in soup.find_all(f'h{i}'):
            heading_text = heading.get_text(strip=True)
            if heading_text:
                headings.append(f"Heading (H{i}): {heading_text}")
   
    if headings:
        all_content_parts.append("HEADINGS:")
        all_content_parts.extend(headings)
   
   
    paragraphs = []
    for p in soup.find_all('p'):
        p_text = p.get_text(strip=True)
        if p_text and len(p_text) > 20: 
            paragraphs.append(p_text)
   
    if paragraphs:
        all_content_parts.append("\nPARAGRAPHS:")
        all_content_parts.extend(paragraphs)
   
   
    lists = []
   
   
    for ul in soup.find_all('ul'):
        items = ul.find_all('li')
        if items:
            list_items = [f"• {item.get_text(strip=True)}" for item in items]
            lists.append('\n'.join(list_items))
   
   
    for ol in soup.find_all('ol'):
        items = ol.find_all('li')
        if items:
            list_items = [f"{idx+1}. {item.get_text(strip=True)}" for idx, item in enumerate(items)]
            lists.append('\n'.join(list_items))
   
    if lists:
        all_content_parts.append("\nLISTS:")
        all_content_parts.extend(lists)
   
   
    links = []
    for a in soup.find_all('a', href=True):
        link_text = a.get_text(strip=True)
        if link_text and len(link_text) > 1: 
            href = a['href']
            
            if href.startswith('/') or href.startswith('http'):
                links.append(f"Link: {link_text} -> {href}")
   
    if links:
        all_content_parts.append("\nLINKS:")
        all_content_parts.extend(links)
   
   
    meta_info = []
    description = soup.find('meta', attrs={'name': 'description'})
    if description and description.get('content'):
        meta_info.append(f"Description: {description['content']}")
   
    keywords = soup.find('meta', attrs={'name': 'keywords'})
    if keywords and keywords.get('content'):
        meta_info.append(f"Keywords: {keywords['content']}")
   
    if meta_info:
        all_content_parts.append("\nMETA INFORMATION:")
        all_content_parts.extend(meta_info)
   
   
    main_text = extract_text(str(soup))
    if main_text:
        all_content_parts.append("\nFULL TEXT CONTENT:")
        all_content_parts.append(main_text)
   
    return all_content_parts


def scrape_website(url):
    """Main function to scrape website content."""
   
    html_content = fetch_website_with_selenium(url)
   
   
    if not html_content:
        html_content = fetch_website_with_requests(url)
   
    if not html_content:
        raise HTTPException(status_code=500, detail="Failed to retrieve website content using both methods.")
   
   
    content_parts = extract_all_content(html_content)
   
   
    combined_content = "\n\n".join(content_parts)
   
    return combined_content


def process_with_llm(content, question, model="gpt-4o-mini"):
    """Process the scraped content with OpenAI's LLM to answer the question."""
    try:
       
        llm = ChatOpenAI(model=model)
       
       
        template = ChatPromptTemplate([
            ("system", "You are an AI assistant that analyzes website content and answers questions based on that content. Focus on providing accurate information from the content provided. If the information is not found in the content, clearly state this."),
            ("human", "Here is the content from a website:\n\n{content}\n\nQuestion: {question}")
        ])
       
       
        max_content_length = 14000  
        if len(content) > max_content_length:
            content = content[:max_content_length] + "\n[Content truncated due to length]"
       
       
        prompt_value = template.invoke(
            {
                "question": question,
                "content": content
            }
        )
       
       
        response = llm.invoke(prompt_value)
       
        return response.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing with LLM: {str(e)}")


@app.post("/scrape-and-answer", response_model=ScrapingResponse)
async def scrape_and_answer(request: ScrapingRequest):
    try:
       
        scraped_content = scrape_website(request.url)
       
       
        answer = process_with_llm(scraped_content, request.question)
       
       
        return ScrapingResponse(answer=answer)
   
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)