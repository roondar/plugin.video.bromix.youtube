# -*- coding: utf-8 -*-

import time

from resources.lib._old.youtube import video


if __name__ == "__main__":
    """normal video - no age-restriction, no signature"""
    #videoInfos = video.getVideoStreamInfos('IKiaiHFtQCY')
    
    """test 480p and 360p"""
    #videoInfos = video.getVideoStreamInfos('p4zdj-HO0uc')
    
    """Some kind of 3D?"""    
    #videoInfos = video.getVideoStreamInfos('kqYuEKtDvAc')
    
    """age-restricted"""
    #videoInfos = video.getVideoStreamInfos('yZ2RCJ28UPQ')
    
    """vevo + signature"""
    #videoInfos = video.getVideoStreamInfos('O-zpOMYRi0w')
    
    start = time.time()
    videoInfos = video.getVideoStreamInfos('yZ2RCJ28UPQ')
    end = time.time()
    
    diff = end-start
    
    stream1080 = video.getBestFittingVideoStreamInfo(videoInfos=videoInfos, size=1080)
    stream720 = video.getBestFittingVideoStreamInfo(videoInfos=videoInfos, size=720)
    stream480 = video.getBestFittingVideoStreamInfo(videoInfos=videoInfos, size=480)
    stream360 = video.getBestFittingVideoStreamInfo(videoInfos=videoInfos, size=360)
    
    url = stream720.getUrl()
    pass