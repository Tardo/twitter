# Copyright 2018 Alexandre Díaz <dev@redneboa.es>
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).
import tweepy
import threading
import time

API_PAG_LIMIT=900

#-- Application AUTH
CONSUMER_KEY = "PUT YOUR APP KEY HERE"
CONSUMER_SECRET = "PUT YOUR APP KEY HERE"
#-- User AUTH
ACCESS_KEY = "PUT YOUR USER KEY HERE"
ACCESS_SECRET = "PUT YOUR USER KEY HERE"


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

print("Ok %s... deleting all stuff of your account..." % api.me().screen_name)

timeline = api.user_timeline(count=API_PAG_LIMIT)
favorites = api.favorites(count=API_PAG_LIMIT)

if any(timeline):
    print("Found %d tweets to remove!" % len(timeline))
    # Delete tweets one by one
    def del_tweets():
        try:
            for status in timeline:
                time.sleep(1)
                print("Deleted tweet created at '%s'" %
                      status.created_at.strftime("%d-%m-%Y %H:%M:%S"))
                api.destroy_status(status.id)
        except tweepy.RateLimitError:
            print("Twitter Rate Limit!! Can't use api... please, try it later.")
        print("All tweets deleted successfully!")
    threading.Thread(target=del_tweets).start()
else:
    print("All OK! No tweets to delete.")

if any(favorites):
    print("Found %d favorited tweets to unlike!" % len(favorites))
    # Delete tweets one by one
    def del_favorites():
        try:
            for favorite in favorites:
                time.sleep(1)
                print("Unliked tweet of '%s' that liked on '%s'" %
                      (favorite.author.screen_name,
                       favorite.created_at.strftime("%d-%m-%Y %H:%M:%S")))
                api.destroy_favorite(favorite.id)
        except tweepy.RateLimitError:
            print("Twitter Rate Limit!! Can't use api... please, try it later.")
        print("All tweets unliked successfully!")
    threading.Thread(target=del_favorites).start()
else:
    print("All OK! No tweets to unlike.")
