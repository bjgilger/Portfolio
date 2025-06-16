import requests
from bs4 import BeautifulSoup
import string
import os

BASE_URL = "https://www.nature.com"
START_URL = "https://www.nature.com/nature/articles?sort=PubDate&year=2020"

def tag_leading_to_view_article(tag):
    return tag.has_attr("data-track-action") and tag["data-track-action"] == "view article"

def tag_containing_article_type(tag):
    return tag.name == "span" and tag.has_attr("data-test") and tag["data-test"] == "article.type"

def tag_containing_article_title(tag):
    return (
        tag.name == "h1"
        and tag.has_attr("class")
        and len(tag["class"]) > 0
        and "article" in tag["class"][0]
        and "title" in tag["class"][0]
    )

def sanitize_filename(title):
    filename = title.strip()
    filename = filename.translate(str.maketrans("", "", string.punctuation))
    filename = "_".join(filename.split())
    return filename

def main():
    num_pages = int(input())
    article_type = input().strip()

    session = requests.Session()
    for page in range(1, num_pages + 1):
        page_url = f"{START_URL}&page={page}"
        folder = f"Page_{page}"
        os.makedirs(folder, exist_ok=True)

        resp = session.get(page_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        type_spans = soup.find_all(tag_containing_article_type)

        # Filter by user-specified type (exact match, case-sensitive)
        matching_spans = [
            span for span in type_spans if span.text.strip() == article_type
        ]
        articles = [span.find_parent("article") for span in matching_spans]

        for article in articles:
            link_tag = article.find(tag_leading_to_view_article)
            if not link_tag:
                continue
            article_href = link_tag.get("href")
            article_url = BASE_URL + article_href if not article_href.startswith("http") else article_href

            art_resp = session.get(article_url)
            art_soup = BeautifulSoup(art_resp.text, "html.parser")

            h1_tag = art_soup.find(tag_containing_article_title)
            if not h1_tag or not h1_tag.text.strip():
                continue
            title = h1_tag.text.strip()

            teaser_p = art_soup.find("p", class_="article__teaser")
            if not teaser_p or not teaser_p.text.strip():
                continue
            body = teaser_p.text.strip()

            filename = sanitize_filename(title) + ".txt"
            file_path = os.path.join(folder, filename)
            with open(file_path, "wb") as f:
                f.write(body.encode("utf-8"))

if __name__ == "__main__":
    main()
