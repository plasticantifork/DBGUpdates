#!/usr/bin/python

import sys, os
import traceback
import requests
import hashlib
import credentials
import tweepy
import praw
from lxml import etree
from datetime import datetime,timedelta

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return '%3.1f %s%s' % (num, unit, suffix)
        num /= 1024.0
    return '%.1f %s%s' % (num, 'Yi', suffix)

def Monitor():
    with open(os.path.join(sys.path[0], 'siteList.txt'), 'r') as f:
        for line in f:
            timeZone = datetime.utcnow() - timedelta(hours=7)
            updateTime = timeZone.strftime('%Y-%m-%d %I:%M %p') + ' PST'
            Message = line.split(',')[0]
            hashTags = line.split(',')[2]
            url = line.split(',')[1]
            urlCommon = line.split(',')[3]
            fileName = 'tstamps/%s' % Message
            fileNameCommon = 'tstamps/C-%s' % Message
            try:
                tstampFileCommon = open(os.path.join(sys.path[0], fileNameCommon), 'r')
            except:
                resp = requests.head(urlCommon)
                websiteTstampCommon = resp.headers['Last-Modified']
                tstampFileCommon = open(os.path.join(sys.path[0], fileNameCommon), 'w')
                tstampFileCommon.write(websiteTstampCommon)
                tstampFileCommon.close()
                print 'Creating common tstamp file: %s' % Message
            try:
                tstampFile = open(os.path.join(sys.path[0], fileName), 'r')
            except:
                resp = requests.head(url)
                websiteTstamp = resp.headers['Last-Modified']
                tstampFile = open(os.path.join(sys.path[0], fileName), 'w')
                tstampFile.write(websiteTstamp)
                tstampFile.close()
                print 'Creating tstamp file: %s' % Message
            else:
                resp = requests.head(url)
                websiteTstamp = resp.headers['Last-Modified']
                tstampFile = open(os.path.join(sys.path[0], fileName), 'r')
                oldWebsiteTstamp = tstampFile.readline().strip()
                tstampFile.close()
                tstampFile = open(os.path.join(sys.path[0], fileName), 'w')
                tstampFile.write(websiteTstamp)
                tstampFile.close()
                #oldWebsiteTstamp = 'sdfsdf'
                resp = requests.head(urlCommon)
                websiteTstampCommon = resp.headers['Last-Modified']
                tstampFileCommon = open(os.path.join(sys.path[0], fileNameCommon), 'r')
                oldWebsiteTstampCommon = tstampFileCommon.readline().strip()
                tstampFileCommon.close()
                tstampFileCommon = open(os.path.join(sys.path[0], fileNameCommon), 'w')
                tstampFileCommon.write(websiteTstampCommon)
                tstampFileCommon.close()
                #oldWebsiteTstampCommon = 'sdfsdf'
                if(websiteTstamp != oldWebsiteTstamp) or (websiteTstampCommon != oldWebsiteTstampCommon):
                    patchSize = 0
                    redditFileNames = []
                    if ('Upcoming' not in Message) and ('PS2' in Message):
                        if (url == 'http://manifest.patch.daybreakgames.com/patch/sha/manifest/planetside2/planetside2-live/live/planetside2-live.sha.soe.txt'):
                            newUrl = url
                            lastUrl = 'http://manifest.patch.daybreakgames.com/patch/sha/manifest/planetside2/planetside2-live/livelast/planetside2-live.sha.soe.txt'
                            newCommonUrl = 'http://manifest.patch.daybreakgames.com/patch/sha/manifest/planetside2/planetside2-livecommon/live/planetside2-livecommon.sha.soe.txt'
                            lastCommonUrl = 'http://manifest.patch.daybreakgames.com/patch/sha/manifest/planetside2/planetside2-livecommon/livelast/planetside2-livecommon.sha.soe.txt'
                        elif (url == 'http://manifest.patch.daybreakgames.com/patch/sha/manifest/planetside2/planetside2-test/live/planetside2-test.sha.soe.txt'):
                            newUrl = url
                            lastUrl = 'http://manifest.patch.daybreakgames.com/patch/sha/manifest/planetside2/planetside2-test/livelast/planetside2-test.sha.soe.txt'
                            newCommonUrl = 'http://manifest.patch.daybreakgames.com/patch/sha/manifest/planetside2/planetside2-testcommon/live/planetside2-testcommon.sha.soe.txt'
                            lastCommonUrl = 'http://manifest.patch.daybreakgames.com/patch/sha/manifest/planetside2/planetside2-testcommon/livelast/planetside2-testcommon.sha.soe.txt'
                        if(websiteTstamp != oldWebsiteTstamp):
                            newRoot = etree.parse(newUrl)
                            lastRoot = etree.parse(lastUrl)
                            for newFile in newRoot.iter('file'):
                                if (newFile.get('delete') != 'yes'):
                                    lastFile = lastRoot.xpath(newRoot.getpath(newFile))
                                    if isinstance(lastFile, list):
                                                lastFile = lastFile[0]
                                    if (newFile.get('timestamp')!=lastFile.get('timestamp')):
                                        if (lastFile is None) or (not len(newFile)):
                                            if (isinstance(newFile.get('compressedSize'), str)):
                                                patchSize+=int(newFile.get('compressedSize'))
                                                redditFileNames.append(newFile.get('name'))
                                        else:
                                            patchFound = False
                                            for patch in newFile.iter():
                                                if (not patchFound) and (patch.get('sourceTimestamp')==lastFile.get('timestamp')):
                                                    patchSize+=int(patch.get('patchCompressedSize'))
                                                    redditFileNames.append(newFile.get('name'))
                                                    patchFound = True
                                            if not patchFound:
                                                if (isinstance(newFile.get('compressedSize'), str)):
                                                    patchSize+=int(newFile.get('compressedSize'))
                                                    redditFileNames.append(newFile.get('name'))
                        if (websiteTstampCommon != oldWebsiteTstampCommon):
                            newRoot = etree.parse(newCommonUrl)
                            lastRoot = etree.parse(lastCommonUrl)
                            for newFile in newRoot.iter('file'):
                                if (newFile.get('delete') != 'yes'):
                                    lastFile = lastRoot.xpath(newRoot.getpath(newFile))
                                    if isinstance(lastFile, list):
                                                lastFile = lastFile[0]
                                    if (newFile.get('timestamp')!=lastFile.get('timestamp')):
                                        if (lastFile is None) or (not len(newFile)):
                                            if (isinstance(newFile.get('compressedSize'), str)):
                                                patchSize+=int(newFile.get('compressedSize'))
                                                redditFileNames.append(newFile.get('name'))
                                        else:
                                            patchFound = False
                                            for patch in newFile.iter():
                                                if (not patchFound) and (patch.get('sourceTimestamp')==lastFile.get('timestamp')):
                                                    patchSize+=int(patch.get('patchCompressedSize'))
                                                    redditFileNames.append(newFile.get('name'))
                                                    patchFound = True
                                            if not patchFound:
                                                if (isinstance(newFile.get('compressedSize'), str)):
                                                    patchSize+=int(newFile.get('compressedSize'))
                                                    redditFileNames.append(newFile.get('name'))
                    if ('Upcoming' not in Message) and ('PS2' in Message):
                        r = praw.Reddit('Planetside 2 Update Poster')
                        r.login(credentials.u, credentials.p, disable_warning=True)
                        redditMessage = ' '.join(Message.replace('@Planetside2', '').split())
                        redditPost = u'\u25B2 %s update detected at %s' % (redditMessage, updateTime)
                        print '%s|Posting to Reddit (%s)' % (updateTime, Message)
                        redditFileNames.sort()
                        redditBody = '##**Files Changed**\n\n* %s\n\n**Size:** %s (%s bytes)\n\n*via [@PS2Updates](https://twitter.com/ps2updates)*' % ('\n* '.join(redditFileNames), sizeof_fmt(patchSize), '{0:,}'.format(patchSize))
                        r.submit('planetside', redditPost, text=redditBody)
                        
                        twitterAuthFile = open(os.path.join(sys.path[0], 'twitterAuth'), 'r')
                        consumerKey = twitterAuthFile.readline().strip()
                        consumerSecret = twitterAuthFile.readline().strip()
                        accessToken = twitterAuthFile.readline().strip()
                        accessTokenSecret = twitterAuthFile.readline().strip()
                        twitterAuthFile.close()
                        auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
                        auth.set_access_token(accessToken, accessTokenSecret)
                        api = tweepy.API(auth)
                    if 'Upcoming' in Message:
                        twitterPost = u'\u27F3 %s update detected at %s %s' % (Message, updateTime, hashTags)
                    else:
                        twitterPost = u'\u25B2 %s update detected at %s %s' % (Message, updateTime, hashTags)
                    print '%s|Posting to Twitter (%s)' % (updateTime, Message)
                    api.update_status(status=twitterPost)
try:
    Monitor()
except requests.exceptions.HTTPError:
    print 'HTTPError Occurred'
except Exception:
    traceback.print_exc()
quit()
