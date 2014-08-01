# -*- coding: utf-8 -*-

import time
import video

if __name__ == "__main__":
    """normal video - no age-restriction, no signature"""
    #videoInfos = video.getVideoStreamInfos('IKiaiHFtQCY')
    
    """test 480p and 360p"""
    #videoInfos = video.getVideoStreamInfos('p4zdj-HO0uc')
    
    #videoInfos = getVideoStreamInfos('zJ_ld0PjdQg')
    #videoInfos = getVideoStreamInfos('yZ2RCJ28UPQ')
    #videoInfos = getVideoStreamInfos('O-zpOMYRi0w')
    #videoInfos = video.getVideoStreamInfos('kqYuEKtDvAc')
    
    start = time.time()
    videoInfos = video.getVideoStreamInfos('p4zdj-HO0uc')
    end = time.time()
    
    diff = end-start
    
    stream1080 = video.getBestFittingVideoStreamInfo(videoInfos=videoInfos, size=1080)
    stream720 = video.getBestFittingVideoStreamInfo(videoInfos=videoInfos, size=720)
    stream480 = video.getBestFittingVideoStreamInfo(videoInfos=videoInfos, size=480)
    stream360 = video.getBestFittingVideoStreamInfo(videoInfos=videoInfos, size=360)
    
    url = stream720.getUrl()
    pass