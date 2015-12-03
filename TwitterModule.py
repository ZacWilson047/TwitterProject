from collections import defaultdict
from copy import deepcopy
import util
import twitter
import json
import time
import string
import stop_words


STOP_WORDS = stop_words.get_stop_words('english')

api = twitter.Api(consumer_key='b170h2arKC4VoITriN5jIjFRN',
                  consumer_secret='z2npapLunYynvp9E783KsTiTMUR4CE6jgGIFqXOdzmXNkYI7g9',
                  access_token_key='3842613073-L7vq82QRYRGCbO1kzN9bYfjfbbV7kOpWWLYnBGG',
                  access_token_secret='FU6AJWG4iDHfzQWhjKB1r3SIwoyzTcgFe0LjyNfq8r6aR')

cached_query_results = {}
cached_user_results = {}


def search_tweets(query, max_searches=5, override_cache=False):
    """Searches for tweets that match query.

    Args:
        query: The search query string. Can be a phrase or hashtag.
            See https://dev.twitter.com/rest/reference/get/search/tweets
        max_searches: The maximum number of API searches that will be
            executed for the given query. Default value is 5 searches.
            100 tweets can be obtained per API search, so by default
            a maximum of 500 tweets will be returned.
        override_cache: Whether to execute a search even if there is
            already a cached result for the query. Defaults to False.

    Returns:
        A list of tweet objects matching the query with most recent
        tweets first.
    """
    if query in cached_query_results and override_cache is not False:
        raise UserWarning('input query {0} is already in '
                          'cached_query_results'.format(query))
    remaining_timeout = api.GetSleepTime('/search/tweets')
    if remaining_timeout != 0:
        print ('searchTweets() must wait {0} seconds in order to not exceed '
               'the Twitter API rate limit.'.format(remaining_timeout + 1))
        time.sleep(remaining_timeout + 1)
    result = []
    search_result = api.GetSearch(term=query, count=100) # could also add lang='en'
    result.extend(search_result)
    oldest_tweet_id = min([t.GetId() for t in search_result])
    num_searches = 1
    while len(search_result) == 100 and num_searches < max_searches:
        search_result = _search_tweets_aux(query, oldest_tweet_id)
        oldest_tweet_id = min([t.GetId() for t in search_result])
        result.extend(search_result)
        num_searches += 1
    global cached_query_results
    cached_query_results[query] = result
    return result

def _search_tweets_aux(query, max_tweet_id):
    """Auxiliary helper function for search_tweets."""
    remaining_timeout = api.GetSleepTime('/search/tweets')
    if remaining_timeout != 0:
        print ('searchTweets() must wait {0} seconds in order to not exceed '
               'the Twitter API rate limit.'.format(remaining_timeout + 1))
        time.sleep(remaining_timeout + 1)
    search_result = api.GetSearch(term=query, count=100, max_id=max_tweet_id - 1)
    return search_result


def no_duplicate_tweets(tweets):
    """Returns True iff tweets in input list are all unique."""
    ids = set()
    for tweet in tweets:
        tweet_id = tweet.GetId()
        if tweet_id in ids:
            return False
        ids.add(tweet_id)
    return True


def tweets_to_text_strings(tweets):
    """Converts list of tweets to list of tweet text strings."""
    return [tweet.GetText() for tweet in tweets]


def tweets_to_word_counter(tweets, normalize=False, lowercase=True):
    """Converts list of tweets to dict of word counts.

    Args:
        tweets: List of tweet objects to process.
        normalize: Whether to return frequencies instead of counts.
            Default value is False (return counts).
        lowercase: Whether to convert all words to lowercase.
            Default value if True.

    Returns:
        util.Counter object containing counts of words in the tweets.
        Words are keys, counts are values. If normalize is set to True,
        then function will return word frequencies as values.
    """
    word_counter = util.Counter()
    for tweet in tweets:
        word_counter += string_to_nonstopword_counter(tweet.GetText(), lowercase)
    if normalize:
        word_counter.normalize()
    return word_counter


def string_to_nonstopword_list(text):
    """Returns list of non-stopwords in string.

    Args:
        text: The string to process.

    Returns:
        List of non-stopwords in text string. Punctuation, whitespace,
        and hyperlinks are removed. Hashtag and @USERNAME punctionation
        is not removed.
    """
    # split strings into words and remove whitespace:
    words = text.split()
    # remove non-hashtag and non-username punctionation:
    chars_to_remove = list(deepcopy(string.punctuation))
    chars_to_remove.remove('#')
    chars_to_remove.remove('@')
    chars_to_remove = ''.join(chars_to_remove)
    words = [word.strip(chars_to_remove) for word in words]
    # remove stopwords:
    words = filter(lambda w: w.lower() not in STOP_WORDS, words)
    # remove hyperlinks:
    words = filter(lambda w: not (len(w) > 7 and w[0:9] == 'https://'), words)
    return words


def string_to_nonstopword_counter(text, lowercase=True):
    """Converts string to util.Counter of non-stopwords in text string.

    Args:
        text: The string to process.
        lowercase: Whether the convert the words in the string to lowercase.

    Returns:
        util.Counter object containing counts of non-stopwords in string.
        Punctuation, whitespace, and hyperlinks are removed. Hashtag
        and @USERNAME punctionation is not removed.
    """
    words = string_to_nonstopword_list(text)
    word_counter = util.Counter()
    for word in words:
        if lowercase:
            word = word.lower()
        word_counter[word] += 1
    return word_counter


def get_user_tweets(username, max_searches=5, override_cache=False):
    """Searches for tweets that match query.

    Args:
        username: The username of the Twitter account that tweets will
            be downloaded for.
        max_searches: The maximum number of API searches that will be
            executed for the given user. Default value is 5 searches.
            100 tweets can be obtained per API search, so by default
            a maximum of 500 tweets will be returned.
        override_cache: Whether to execute a search even if there is
            already a cached result for the specifed Twitter user.
            Defaults to False.

    Returns:
        A list of tweet objects corresponding to the specified users's
        public tweets, with their most recent tweets first.
    """
    if username in cached_user_results and override_cache is not False:
        raise UserWarning('input username {0} is already in '
                          'cached_user_results'.format(query))
    remaining_timeout = api.GetSleepTime('/search/tweets') # might need to change this
    if remaining_timeout != 0:
        print ('searchTweets() must wait {0} seconds in order to not exceed '
               'the Twitter API rate limit.'.format(remaining_timeout + 1))
        time.sleep(remaining_timeout + 1)
    result = []
    search_result = api.GetUserTimeline(screen_name=username, count=200) # could also add lang='en'
    result.extend(search_result)
    oldest_tweet_id = min([t.GetId() for t in search_result])
    num_searches = 1
    while len(search_result) == 200 and num_searches < max_searches:
        search_result = _get_user_tweets_aux(username, oldest_tweet_id)
        if not search_result:
            break
        oldest_tweet_id = min([t.GetId() for t in search_result])
        result.extend(search_result)
        num_searches += 1
    global cached_user_results
    cached_user_results[username] = result
    return result


def _get_user_tweets_aux(username, max_tweet_id):
    """Auxiliary helper function for search_tweets."""
    remaining_timeout = api.GetSleepTime('/search/tweets')
    if remaining_timeout != 0:
        print ('searchTweets() must wait {0} seconds in order to not exceed '
               'the Twitter API rate limit.'.format(remaining_timeout + 1))
        time.sleep(remaining_timeout + 1)
    search_result = api.GetUserTimeline(screen_name=username, count=200,
                                        max_id=max_tweet_id - 1)
    return search_result







