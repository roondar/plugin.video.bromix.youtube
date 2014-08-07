# -*- coding: utf-8 -*-

import time

import client
from youtube.client import YouTubeClient

if __name__ == "__main__":
    #local_time = time.localtime()
    #utc_time = time.gmtime()
    
    #timeStr = time.strftime("%Y-%m-%dT%H:%M:%SZ", utc_time)
    
    #diff = utc_time-local_time
    
    #hours = diff/1000 
    
    __USERNAME__ = "a8240166@drdrb.net"#"YOUR_USERNAME"
    __PASSWORD__ = "0012345678900" #"YOUR_PASSWORD"
    
    __client__ = YouTubeClient(username=__USERNAME__, password=__PASSWORD__, maxResult=25)
    hasLogin = __client__.hasLogin()
    
    pass