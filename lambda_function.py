import json
import requests
import pdfplumber
from transformers import pipeline
import io

# Initialize the summarization model
summarizer = pipeline("summarization")

# Function to search papers on arXiv
def search_papers_arxiv(keyword, num_results=5):
    search_url = f'http://export.arxiv.org/api/query?search_query=all:{keyword}&start=0&max_results={num_results}'
    response = requests.get(search_url)
    papers = []
    
    if response.status_code == 200:
        data = response.text
        # Parsing the XML response and extracting details
        for entry in data.split('<entry>')[1:]:
            title = entry.split('<title>')[1].split('</title>')[0]
            summary = entry.split('<summary>')[1].split('</summary>')[0]
            pdf_url = entry.split('<link title="pdf" href="')[1].split('"')[0]
            papers.append({
                "title": title,
                "abstract": summary,
                "pdf_url": pdf_url
            })
    return papers

# Function to download PDF
def download_pdf(pdf_url):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        return response.content
    return None

# Function to extract text from the downloaded PDF
def extract_text_from_pdf(pdf_data):
    with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to summarize the extracted text in chunks
def summarize_in_chunks(text, max_chunk_size=1000):
    chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=150, min_length=50, do_sample=False)
        summaries.append(summary[0]['summary_text'])
    return ' '.join(summaries)

# Lambda entry point
def lambda_handler(event, context):
    keyword = event['queryStringParameters']['keyword']
    num_results = int(event['queryStringParameters']['num_results'])

    papers = search_papers_arxiv(keyword, num_results)
    summaries = []
    
    for paper in papers:
        pdf_data = download_pdf(paper['pdf_url'])
        if pdf_data:
            text = extract_text_from_pdf(pdf_data)
            summary = summarize_in_chunks(text)
            summaries.append({
                'title': paper['title'],
                'summary': summary
            })
    
    # Return the summaries as a JSON response
    return {
        'statusCode': 200,
        'body': json.dumps(summaries)
    }
