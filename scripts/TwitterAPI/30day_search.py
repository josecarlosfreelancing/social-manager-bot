from os import environ

from searchtweets import load_credentials, gen_rule_payload, collect_results


environ['SEARCHTWEETS_CONSUMER_KEY'] = 'lcXGBbAUArkH1HE1aaBnrWcrW'
environ['SEARCHTWEETS_CONSUMER_SECRET'] = 'KgdoZlt8mlXtXUgXJxokFdUMwtfLKynuaAGWEpJD035xwd3Sto'
environ['SEARCHTWEETS_ENDPOINT'] = 'https://api.twitter.com/1.1/tweets/search/30day/snikpic.json'
search_args = load_credentials(account_type="premium")
rule = gen_rule_payload("beyonce", results_per_call=100) # testing with a sandbox account
tweets = collect_results(rule,
                         max_results=100,
                         result_stream_args=search_args)
print(len(tweets))


if __name__ == '__main__':
    pass