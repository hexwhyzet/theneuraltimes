from random import shuffle

import nltk as nltk


def count_human_names(text: str):
    tokens = nltk.tokenize.word_tokenize(text)
    pos = nltk.pos_tag(tokens)
    chunk = nltk.ne_chunk(pos, binary=False)
    return len(list(chunk.subtrees(filter=lambda t: t.label() == 'PERSON')))


class ArticleHeadline:
    headline: str
    url: str

    def __init__(self, headline: str, url: str):
        self.headline = headline
        self.url = url

    def __repr__(self):
        return f"{self.headline} - {self.url}"


def extract_interesting(headlines: list[ArticleHeadline]):
    headlines.sort(key=lambda x: count_human_names(x.headline))
    yet_not_selected_headlines = headlines[10:]
    shuffle(yet_not_selected_headlines)
    return headlines[:10] + yet_not_selected_headlines[:10]
