# -*- coding: utf-8 -*-
# Copyright 2018 Alexandre Díaz <dev@redneboa.es>
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).
# Using TWEEPY 3.7.0
import tweepy
import threading
import time
import sys
import getopt
from datetime import datetime


class TwitterApp(object):
    def __init__(self, app_key, app_secret):
        self.app_key = app_key
        self.app_secret = app_secret
        self._api = None

    def login_as(self, user_key, user_secret):
        auth = tweepy.OAuthHandler(self.app_key, self.app_secret)
        auth.set_access_token(user_key, user_secret)
        self._api = tweepy.API(auth)
        return self._api.me()

    def get_timeline(self, count):
        return self._api.user_timeline(count=count)

    def get_favorites(self, count):
        return self._api.favorites(count=count)

    @property
    def api(self):
        return self._api


class TwitterStatusDeleter(object):
    def __init__(self, twitter_app, statuses):
        self._app = twitter_app
        self._condition_days = 0
        self.delay = 3
        self.statuses = statuses

    def set_delay(self, delay):
        self.delay = delay

    def del_status(self, status):
        if self._can_delete_status(status):
            print("Deleted status created at '%s'" %
                  status.created_at.strftime("%d-%m-%Y %H:%M:%S"))
            self._app.api.destroy_status(status.id)

    def run(self):
        try:
            for status in self.statuses:
                self.del_status(status)
                time.sleep(self.delay)
            return True
        except tweepy.RateLimitError:
            print("Twitter Rate Limit!! Can't use api... please, try it later.")
        return False

    def set_condition_days(self, days):
        self._condition_days = days

    def _can_delete_status(self, status):
        if self._condition_days and abs(
                (datetime.now() - status.created_at).days) >= self._condition_days:
            return True
        return False

class TimelineDeleter(TwitterStatusDeleter):
    def run(self):
        res = super(TimelineDeleter, self).run()
        if res:
            print("Timeline successfully deleted :)")
        return res

class FavoritesDeleter(TwitterStatusDeleter):
    def run(self):
        res = super(FavoritesDeleter, self).run()
        if res:
            print("Favorites successfully deleted :)")
        return res


if __name__ == "__main__":
    # Default Input Params
    app_key = None
    app_secret = None
    user_key = None
    user_secret = None
    filter_days = None
    max_status_pag = 900

    # Parse User Input Params
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "ak:as:uk:us:fd:ms:",
            [
                "app-key=",
                "app-secret=",
                "user-key=",
                "user-secret=",
                "filter-days=",
                "max-status-pag=",
            ])
    except getopt.GetoptError:
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-ak', '--app-key'):
            app_key = arg
        elif opt in ('-as', '--app-secret'):
            app_secret = arg
        elif opt in ('-uk', '--user-key'):
            user_key = arg
        elif opt in ('-us', '--user-secret'):
            user_secret = arg
        elif opt in ('-fd', '--filter-days'):
            filter_days = arg
        elif opt in ('-ms', '--max-status-pag'):
            max_status_pag = arg

    if not app_key or not app_secret or not user_key or not user_secret:
        print("Invalid parameters!")
        sys.exit(2)

    # Launch App
    app = TwitterApp(app_key, app_secret)
    login = app.login_as(user_key, user_secret)
    if login:
        print("Ok %s... deleting all stuff of your account..." % login.screen_name)
        timeline = app.get_timeline(max_status_pag)
        timeline_deleter = TimelineDeleter(app, timeline)
        timeline_deleter.set_condition_days(filter_days)
        threading.Thread(target=timeline_deleter.run).start()

        favorites = app.get_favorites(max_status_pag)
        fav_deleter = FavoritesDeleter(app, favorites)
        fav_deleter.set_condition_days(filter_days)
        threading.Thread(target=fav_deleter.run).start()
