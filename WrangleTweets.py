import TwitterModule
import util
import cPickle

# Polling data is Real Clear Politics polling average from 11/16 - 11/30
POLLING_DATA = {
    "Trump": 28.3,
    "Carson": 18.8,
    "Rubio": 13.8,
    "Cruz": 13.0,
    "Bush": 5.3,
    "Fiorina": 3.5,
    "Huckabee": 2.8,
    "Christie": 2.5,
    "Kasich": 2.5,
    "Paul": 2.3,
    "Graham": 0.5,
    "Pataki": 0.5,
    "Santorum": 0.3,
    "Clinton": 57.8,
    "Sanders": 30.4,
    "O'Malley": 3.6
}

CANDIDATE_USERNAMES = {
    "Trump": "realDonaldTrump",
    "Carson": "RealBenCarson",
    "Rubio": "marcorubio",
    "Cruz": "tedcruz",
    "Bush": "JebBush",
    "Fiorina": "CarlyFiorina",
    "Huckabee": "GovMikeHuckabee",
    "Christie": "ChrisChristie",
    "Kasich": "JohnKasich",
    "Paul": "RandPaul",
    "Graham": "LindseyGrahamSC",
    "Pataki": "GovernorPataki",
    "Santorum": "RickSantorum",
    "Clinton": "HillaryClinton",
    "Sanders": "BernieSanders",
    "O'Malley": "MartinOMalley"
}

GOP_CANDIDATES = {
    "Trump", "Carson", "Rubio", "Cruz", "Bush", "Fiorina", "Huckabee",
    "Christie", "Kasich", "Paul", "Graham", "Pataki", "Santorum"
}
DEM_CANDIDATES = {"Clinton", "Sanders", "O'Malley"}
ALL_CANDIDATES = GOP_CANDIDATES.union(DEM_CANDIDATES)


class Candidate(object):
    """2016 Presidential candidate object.

    Attributes:
        name: Last name of candidate.
        twitter_username: Twitter username of candidate.
        party: Either "Democratic" or "Republican".
        polling: Percentage of votes that candidate is polling at.
        tweets: List of candidates tweets.
        hashtag_counter: Counter of candidate's hashtags.
        usermentions_counter: Counter of candidate's user mentions.
        words_counter: Counter of candidate's words,
            excluding hashtags and user mentions.
    """

    def __init__(self, name):
        if name not in ALL_CANDIDATES:
            raise ValueError("Invalid candidate name: {0}".format(name))
        self.name = name
        self.twitter_username = CANDIDATE_USERNAMES[self.name]
        if self.name in DEM_CANDIDATES:
            self.party = "Democratic"
        elif self.name in GOP_CANDIDATES:
            self.party = "Republican"
        else:
            raise UserWarning("Party identification error.")
        self.polling = POLLING_DATA[self.name]

    def get_all_tweets(self):
        self.tweets = TwitterModule.get_user_tweets(self.twitter_username, max_searches=1000)
        foo = TwitterModule.tweets_to_word_counter(self.tweets)
        bar = TwitterModule.split_words_hashtags_usermentions(foo)
        self.words_counter = bar[0]
        self.hashtag_counter = bar[1]
        self.usermentions_counter = bar[2]

    def serialize_counters(self):
        with open("serialization_output/{0}_words.csv".format(self.name), "w") as fileout:
            output = []
            for word in self.words_counter:
                output.extend([word] * self.words_counter[word])
            fileout.write(",".join(output) + "\n")
        with open("serialization_output/{0}_hashtags.csv".format(self.name), "w") as fileout:
            output = []
            for hashtag in self.hashtag_counter:
                output.extend([hashtag] * self.hashtag_counter[hashtag])
            fileout.write(",".join(output) + "\n")
        with open("serialization_output/{0}_usermentions.csv".format(self.name), "w") as fileout:
            output = []
            for user in self.usermentions_counter:
                output.extend([user] * self.usermentions_counter[user])
            fileout.write(",".join(output) + "\n")


def serialize_candidate_into(candidates):
    with open("candidate_info_all.csv", "w") as fileout:
        fileout.write(",".join(("name", "twitter_username", "party", "polling")) + "\n")
        for c in candidates:
            row = ",".join((c.name, c.twitter_username, c.party, str(c.polling)))
            fileout.write(row + "\n")


def main():
    candidates = [Candidate(name) for name in ALL_CANDIDATES]
    serialize_candidate_into(candidates)
    for candidate in candidates:
        candidate.get_all_tweets()
        candidate.serialize_counters()
        with open("backup/{0}.pickle".format(candidate.name), "w") as fileout:
            cPickle.dump(candidate, fileout)
    print "WrangleTweets.py has finishing running."


if __name__ == '__main__':
    main()

