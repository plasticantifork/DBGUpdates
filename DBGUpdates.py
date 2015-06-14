#!/usr/bin/python

import sys, os
import traceback
import requests
from requests.exceptions import HTTPError
import hashlib
import credentials
import tweepy
import praw
from datetime import datetime,timedelta

def Monitor():
    r = praw.Reddit('Planetside 2 Update Poster')
    r.login(credentials.u, credentials.p)
    twitterAuthFile = open(os.path.join(sys.path[0], 'twitterAuth'), 'r')
    consumerKey = twitterAuthFile.readline().strip()
    consumerSecret = twitterAuthFile.readline().strip()
    accessToken = twitterAuthFile.readline().strip()
    accessTokenSecret = twitterAuthFile.readline().strip()
    twitterAuthFile.close()
    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(auth)
    with open(os.path.join(sys.path[0], 'siteList.txt'), 'r') as f:
        for line in f:
            timeZone = datetime.utcnow() - timedelta(hours=7)
            updateTime = timeZone.strftime('%Y-%m-%d %I:%M %p') + ' PST'
            Message = line.split(',')[0]
            hashTags = line.split(',')[2]
            url = line.split(',')[1]
            fileName = 'hashes/' + Message
            try:
                hashFile = open(os.path.join(sys.path[0], fileName), 'r')
            except:
                websiteHash = hashlib.md5(requests.get(url).content).hexdigest()
                hashFile = open(os.path.join(sys.path[0], fileName), 'w')
                hashFile.write(websiteHash)
                hashFile.close()
                print 'First time run for: %s' % Message
            else:
                websiteHash = hashlib.md5(requests.get(url).content).hexdigest()
                hashFile = open(os.path.join(sys.path[0], fileName), "r")
                oldWebsiteHash = hashFile.readline().strip()
                hashFile.close()
                hashFile = open(os.path.join(sys.path[0], fileName), "w")
                hashFile.write(websiteHash)
                hashFile.close()
                if(websiteHash != oldWebsiteHash):
                    if ('Upcoming' not in Message) and ('PS2' in Message):
                        redditMessage = ' '.join(Message.replace('@Planetside2', '').split())
                        redditPost = u'\u25B2 %s update detected at %s' % (redditMessage, updateTime)
                        print '%s|Posting to Reddit (%s)' % (updateTime, Message)
                        r.submit('planetside', redditPost, text='*via [@DBGUpdates](https://twitter.com/dbgupdates)*')
                    if 'Upcoming' in Message:
                        twitterPost = u'\u27F3 %s update detected at %s %s' % (Message, updateTime, hashTags)
                    else:
                        twitterPost = u'\u25B2 %s update detected at %s %s' % (Message, updateTime, hashTags)
                    print '%s|Posting to Twitter (%s)' % (updateTime, Message)
                    api.update_status(status=twitterPost)
try:
    Monitor()
except HTTPError:
    print "HTTPError Occurred"
except Exception:
    traceback.print_exc()
quit()
