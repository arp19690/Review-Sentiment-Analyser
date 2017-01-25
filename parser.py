from pyquery import PyQuery as pq
import requests
from nltk import tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from config import TRUSTED_COMPANY_URL


def get_all_urls_and_content(base_url, limit=5):
    output_list, i = list(), 0

    while i <= limit:
        new_url = base_url + "?page=" + str(i)
        request_data = requests.get(new_url)
        status_code = request_data.status_code
        if status_code == 200:
            output_list.append((new_url, request_data.content))
            i += 1
        else:
            break

    return output_list


def analyse_sentiments(comment):
    lines_list = tokenize.sent_tokenize(comment)
    sid = SentimentIntensityAnalyzer()

    for sentence in lines_list:
        scores = sid.polarity_scores(sentence)
        pos_score = scores["pos"]
        neg_score = scores["neg"]
        if pos_score > neg_score:
            return 'positive'
        elif neg_score > pos_score:
            return 'negative'
        elif neg_score == pos_score:
            return 'neutral'


def parse_data(html_str):
    positive_list, negative_list, nuetral_list = list(), list(), list()
    parsed_data = pq(html_str)

    # removing replies by our company
    parsed_data('div.replies').remove()
    review_data = parsed_data('div.review')

    if len(review_data) > 0:
        for review in review_data.items():
            review_title = review("div.content > h5.title > a").text().replace(
                '"',
                '').strip()
            review_comment = review("div.content > p.body").text()
            review_username = review("div.user > div.user__name > a").text()
            review_stars = review("div.rating > div.stars").attr("data-rating")

            data_dict = {
                "title": review_title,
                "comment": review_comment,
                "stars": review_stars,
                "user_name": review_username,
            }

            review_sentiment = analyse_sentiments(review_comment)
            if review_sentiment == "positive":
                positive_list.append(data_dict)
            elif review_sentiment == "negative":
                negative_list.append(data_dict)
            elif review_sentiment == "neutral":
                nuetral_list.append(data_dict)

    return positive_list, negative_list, nuetral_list


try:
    positives, negatives, neutrals = list(), list(), list()
    data_list = get_all_urls_and_content(TRUSTED_COMPANY_URL)
    if len(data_list) > 0:
        for tmp in data_list:
            tmp_pos, tmp_neg, tmp_neu = parse_data(tmp[1])
            positives += tmp_pos
            negatives += tmp_neg
            neutrals += tmp_neu

    print("Total Positive: " + str(len(positives)))
    print("Total Negative: " + str(len(negatives)))
    print("Total Neutrals: " + str(len(neutrals)))
except Exception as e:
    print("An error occured:")
    print(str(e))
