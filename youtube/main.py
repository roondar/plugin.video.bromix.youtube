# -*- coding: utf-8 -*-

import video

if __name__ == "__main__":
    videoInfos = video.getVideoStreamInfos('kqYuEKtDvAc')
    #videoInfos = getVideoStreamInfos('zJ_ld0PjdQg')
    #videoInfos = getVideoStreamInfos('yZ2RCJ28UPQ')
    #videoInfos = getVideoStreamInfos('O-zpOMYRi0w')
    
    stream1080 = video.getBestFittingVideoStreamInfo(videoInfos=videoInfos, size=1080)
    stream480 = video.getBestFittingVideoStreamInfo(videoInfos=videoInfos, size=480)
    stream720 = video.getBestFittingVideoStreamInfo(videoInfos=videoInfos, size=720)
    
    url = stream720.getUrl()
    pass