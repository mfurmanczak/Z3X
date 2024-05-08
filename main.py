import requests
from bs4 import BeautifulSoup
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
import string

#Change the number of articles and phrases to analyze
NUM_PHRASES = 5
NUM_ARTICLES = 3

url = "https://blog.hubspot.com/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

article_divs = soup.find_all('h3', class_='blog-post-card-title')
article_links = [h3.find('a')['href'] for h3 in article_divs[:NUM_ARTICLES]]


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

    words = [''.join(
        char for char in word if char not in string.punctuation + '—') for word in words]
    words = [word for word in words if word and word != '-']

    phrases = []
    for n in range(1, 4):
        phrases.extend(ngrams(words, n))

    key_phrases = Counter(phrases).most_common()

    last_count = key_phrases[NUM_PHRASES -
                             1][1] if len(key_phrases) >= NUM_PHRASES else 0

    additional_phrases = []
    for phrase, count in key_phrases[NUM_PHRASES:]:
        if count == last_count:
            additional_phrases.append((phrase, count))
        else:
            break

    key_phrases = key_phrases[:NUM_PHRASES] + additional_phrases

    return num_words, num_letters, key_phrases


def main():
    for link in article_links:
        title = get_article_title(link)
        print("Article:", title)
        content = get_article_content(link)
        num_words, num_letters, key_phrases = analyze_article(content)
        print("Number of words:", num_words)
        print("Number of letters:", num_letters)
        print("Top 5 key phrases:")

        max_phrase_length = max(len(' '.join(phrase)) if len(
            phrase) > 1 else len(phrase[0]) for phrase, _ in key_phrases)

        max_ordinal_digits = len(str(len(key_phrases)))

        print(
            f"{'Pos':<{max_ordinal_digits + 4}}| {'Phrase':<{max_phrase_length + 4}} | Count")
        print("-" * (max_ordinal_digits + max_phrase_length + 19))

        last_count = None
        last_ordinal = 0

        for i, (phrase, count) in enumerate(key_phrases):
            last_count = count
            last_ordinal = i

            if i < NUM_PHRASES:
                ordinal_suffix = "th" if 11 <= last_ordinal + \
                    1 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get((last_ordinal + 1) % 10, "th")
                phrase_str = ' '.join(phrase) if len(phrase) > 1 else phrase[0]
                ordinal = f"{last_ordinal + 1}{ordinal_suffix:<2}"
                print(
                    f"{ordinal:<{max_ordinal_digits + 4}}| {phrase_str:<{max_phrase_length+4}} | {count}")
            else:
                phrase_str = ' '.join(phrase) if len(phrase) > 1 else phrase[0]
                print(
                    f"{' ' * (max_ordinal_digits + 4)}| {phrase_str:<{max_phrase_length+4}} | {count}")

        print()


if __name__ == "__main__":
    main()
