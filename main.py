import requests
from bs4 import BeautifulSoup
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
import string

url = "https://blog.hubspot.com/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

article_divs = soup.find_all('h3', class_='blog-post-card-title')
article_links = [h3.find('a')['href'] for h3 in article_divs[:3]]

def get_article_content(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    article_content = soup.find('span', id='hs_cos_wrapper_post_body')
    if article_content:
        return article_content.get_text(separator=' ')
    else:
        return ""

def get_article_title(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    title_element = soup.find('span', id='hs_cos_wrapper_name')
    if title_element:
        return title_element.get_text().strip()
    else:
        return "No Title Found"

def analyze_article(content):
    words = content.split()  
    num_words = len(words)

    num_letters = sum(len(word) for word in words if word.isalnum())  

    stop_words = set(stopwords.words('english'))
    words = [word.lower() for word in words if word.lower() not in stop_words]

    words = [''.join(char for char in word if char not in string.punctuation + '—') for word in words]
    words = [word for word in words if word and word != '-']

    phrases = []
    for n in range(1, 4):  
        phrases.extend(ngrams(words, n))

    key_phrases = Counter(phrases).most_common(5)

    return num_words, num_letters, key_phrases

for link in article_links:
    title = get_article_title(link)
    print("Article:", title)
    content = get_article_content(link)
    num_words, num_letters, key_phrases = analyze_article(content)
    print("Number of words:", num_words)
    print("Number of letters:", num_letters)
    print("Top 5 key phrases:")
    for i, (phrase, count) in enumerate(key_phrases):
        ordinal_suffix = "th" if 11 <= i + 1 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get((i + 1) % 10, "th")
        phrase_str = ' '.join(phrase) if len(phrase) > 1 else phrase[0]
        print(f"{i + 1}{ordinal_suffix} phrase: {phrase_str} (count: {count})")
    print()