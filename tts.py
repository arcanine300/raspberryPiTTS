#! usr/bin/env python3
from pydub import AudioSegment
import praw
import datetime
import os
from gtts import gTTS
import pylirc
import RPi.GPIO as GPIO

blocking = 0

def loop():
    reddit = praw.Reddit(client_id='',
                         client_secret='',
                         user_agent='',
                         username='',
                         password='')

    subreddit = reddit.subreddit()
    flairs = []
    readPosts = False
    flipflop = False
    irSignal = False
    #prev_post = subreddit.top(limit=1) #init to rand value for first iteration

    while True:
        if flipflop:
            posts = list(subreddit.hot(limit=20))
            print("Fetching new headlines...")
            flipflop = False
        else:
            posts = list(subreddit.new(limit=20))
            print("Fetching new headlines...")
            flipflop = True

        if len(posts) > 0:
            readPosts = True

        while readPosts:
            if len(posts) < 1:
                readPosts = False
                break
            else:	
                post = posts[0] 
                if post.link_flair_text in flairs:
                    if "?" not in post.title:
                        tts = gTTS(text=post.title, lang='en-au')
                        tts.save("PostTitle.mp3")
                        soundObj = AudioSegment.from_mp3("PostTitle.mp3")
                        soundObj.export("tts.wav", format="wav")
                        #prev_post = post
                        posts.pop(0)
                        #input("Press Enter to receive auditory depression")
                        print("Press button 0 on the remote to receive auditory depression")
                        while not irSignal:
                            s = pylirc.nextcode(1)
                            while(s):
                                for (code) in s:
                                    #print(code["config"])#uncomment line to print button name to screen
                                    if code["config"] == 'KEY_NUMERIC_0':
                                        irSignal = True
                                if(not blocking):
                                    s = pylirc.nextcode(1)
                                else:
                                    s = []
                        os.system("aplay -D bluealsa /home/pi/tts.wav")
                        irSignal = False
                    else:
                        posts.pop(0)
                else:
                    posts.pop(0)

def destroy():
    GPIO.cleanup()
    pylirc.exit()

if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM) 
        pylirc.init("pylirc", "./conf", blocking)
        loop()
    except KeyboardInterrupt:
        destroy()
