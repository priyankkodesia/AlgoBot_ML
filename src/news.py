import json
import time
import requests
from fuzzywuzzy import fuzz
from src.mistral_chat import MistralChat
from src.nifty_list import nifty50_companies

# Define the API endpoint and key
api_url = 'https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey=aa74d16ab7704bc7913d0c9e677f1e7d'


def fetch_news():
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json().get('articles', [])
    else:
        print(f"Failed to fetch news: {response.status_code}")
        return []


# Function to find similarity between two strings
def find_similarity(s1, s2):
    return fuzz.token_set_ratio(s1.lower(), s2.lower())


def analyze_sentiment(description):
    prompt = (
        f"Analyze the sentiment of the following news description and provide a sentiment rating "
        f"(very positive (5), positive (4), neutral (3), negative(2), very negative(1)) along with a confidence score "
        f"between 0 and 100. If the news is about the broader market like NIFTY BANK overall, ignore the news. "
        f"Output should be only json with the format."
        f"The news can contain information about multiple stocks. Group the stocks by the sentiment score in a single "
        f"object wherever needed. use the actual NSE India ticker symbol value matching the stock name. Refer the below example-"
        f"'[{{\"confidence_level\": 0.85, \"sentiment\": 4, \"symbol\": [\"L&T\"], \"timestamp\": "
        f"\"2022-02-16T16:00:00Z\"}},"
        f"{{\"confidence_level\": 0.5, \"sentiment\": 2, \"symbol\": [\"SBIN\", \"PNB\", \"HDFCBANK\"], "
        f"\"timestamp\": \"2022-02-16T16:00:00Z\"}}]' :\n\n{description}"
    )

    # Assuming MistralChat is a class that handles communication with the Mistral LLM
    agent = MistralChat()
    response = None
    try:
        response = json.loads(agent.chat(prompt))
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None, None

    # Extract the sentiment and confidence from the response
    sentiments = []
    for item in response:
        sentiment = item.get("sentiment")
        confidence = item.get("confidence_level")
        symbols = item.get("symbol")
        if sentiment is not None and confidence is not None and confidence >= 0.7:
            sentiments.append((symbols, sentiment, confidence))

    return sentiments


def process_articles(articles):
    results = []
    # articles = [
    #     {
    #         "source": {"id": "google-news", "name": "Google News"},
    #         "author": "ET Now",
    #         "title": "Investors are optimistic about Maruti Suzuki, Kotak Mahindra, expecting strong growth.",
    #         "description": None,
    #         "url": "https://news.google.com/rss/articles/CBMigwFodHRwczovL3d3dy5ldG5vd25ld3MuY29tL21hcmtldHMvZGVmZW5jZS1zdG9jay10by1idXktY29jaGluLXNoaXB5YXJkcy1hcm0tYmFncy1ycy0xMTAwLWNyb3JlLW9yZGVyLWNoZWNrLXRhcmdldC1hcnRpY2xlLTExMTM2ODEwONIBhwFodHRwczovL3d3dy5ldG5vd25ld3MuY29tL21hcmtldHMvZGVmZW5jZS1zdG9jay10by1idXktY29jaGluLXNoaXB5YXJkcy1hcm0tYmFncy1ycy0xMTAwLWNyb3JlLW9yZGVyLWNoZWNrLXRhcmdldC1hcnRpY2xlLTExMTM2ODEwOC9hbXA?oc=5",
    #         "urlToImage": None,
    #         "publishedAt": "2024-07-01T10:30:33Z",
    #         "content": None
    #     },
    #     {
    #         "source": {"id": None, "name": "Financial Express"},
    #         "author": "The Financial Express",
    #         "title": "Infosys, HDFC Bank faced a downturn due to economic uncertainty.",
    #         "description": None,
    #         "url": "https://www.financialexpress.com/auto/news/june-auto-sales-2024-live-updates-maruti-suzuki-tata-motors-hyundai-hero-motocorp-and-more/3539972/",
    #         "urlToImage": None,
    #         "publishedAt": "2024-07-01T10:26:21Z",
    #         "content": None
    #     },
    #     {
    #         "source": {"id": "the-times-of-india", "name": "The Times of India"},
    #         "author": "TOI Business Desk",
    #         "title": "While Axis Bank, HCL Tech showed promising performance, PowerGrid struggled.",
    #         "description": None,
    #         "url": "https://timesofindia.indiatimes.com/business/india-business/stock-market-today-bse-sensex-nifty50-july-1-2024-dalal-street-indian-equities-global-markets/articleshow/111392229.cms",
    #         "urlToImage": "https://static.toiimg.com/thumb/msid-111392587,width-1070,height-580,imgsize-83112,resizemode-75,overlay-toi_sw,pt-32,y_pad-40/photo.jpg",
    #         "publishedAt": "2024-07-01T10:13:00Z",
    #         "content": None
    #     },
    #     {
    #         "source": {"id": "the-times-of-india", "name": "The Times of India"},
    #         "author": "Nikhil Agarwal",
    #         "title": "Investors are optimistic about Asian Paints, Titan, expecting strong growth.",
    #         "description": None,
    #         "url": "https://economictimes.indiatimes.com/markets/stocks/news/how-stock-markets-have-behaved-before-and-after-budgets-since-2000/articleshow/111400780.cms",
    #         "urlToImage": "https://img.etimg.com/thumb/msid-111400761,width-1200,height-630,imgsize-655876,overlay-etmarkets/photo.jpg",
    #         "publishedAt": "2024-07-01T08:46:46Z",
    #         "content": None
    #     },
    #     {
    #         "source": {"id": "google-news", "name": "Google News"},
    #         "author": "Hindustan Times",
    #         "title": "Bharti Airtel faced a downturn due to economic uncertainty.",
    #         "description": None,
    #         "url": "https://news.google.com/rss/articles/CBMidWh0dHBzOi8vd3d3LmhpbmR1c3RhbnRpbWVzLmNvbS9idXNpbmVzcy9uYW1pdGEtdGhhcGFyLW1heS1nYWluLXJzLTEyNy1jcm9yZS1pbi1lbWN1cmUtcGhhcm1hLWlwby0xMDE3MTk4MjMwMTA5OTMuaHRtbNIBeWh0dHBzOi8vd3d3LmhpbmR1c3RhbnRpbWVzLmNvbS9idXNpbmVzcy9uYW1pdGEtdGhhcGFyLW1heS1nYWluLXJzLTEyNy1jcm9yZS1pbi1lbWN1cmUtcGhhcm1hLWlwby0xMDE3MTk4MjMwMTA5OTMtYW1wLmh0bWw?oc=5",
    #         "urlToImage": None,
    #         "publishedAt": "2024-07-01T06:58:09Z",
    #         "content": None
    #     }
    # ]

    for article in articles:
        description = article.get('description', '')
        title = article.get('title', '')
        content = description if description else title

        if content:  # Proceed only if there is content to analyze
            article_symbols = []
            for symbol, name in nifty50_companies.items():
                if find_similarity(symbol, content) > 70 or find_similarity(name, content) > 70:
                    article_symbols.append(symbol)

            if article_symbols:  # Only analyze sentiment if symbols were found
                res = analyze_sentiment(content)
                if res:
                    results.append(res)

    return flatten_and_group_results(results)


def flatten_and_group_results(results):
    grouped_results = {}
    for res in results:
        for item in res:
            symbols, sentiment, confidence = item
            if sentiment not in grouped_results:
                grouped_results[sentiment] = []
            grouped_results[sentiment].extend(symbols)

    return grouped_results


if __name__ == "__main__":
    while True:
        news_articles = fetch_news()
        # Sample output -> {2: ['INFY', 'HDFCBANK', 'POWERGRID', 'BHARTIARTL'], 4: ['MARUTI', 'KOTAKBANK', 'AXISBANK', 'HCLTECH', 'ASIANPAINT', 'TITAN']}
        analyzed_results = process_articles(news_articles)

        for result in analyzed_results:
            print(result)

        time.sleep(3600)
