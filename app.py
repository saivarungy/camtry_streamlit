import threading
from typing import Union

import av
import numpy as np
import streamlit as st

#######
import random
import HandTrackingModule as htm
import time
import pandas as pd
#######

from streamlit_webrtc import(
    RTCConfiguration,
    WebRtcMode,
    WebRtcStreamerContext,
    webrtc_streamer,
    VideoTransformerBase
)
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)


def processing(fingersList):
    fingerTipIds=[4,8,12,16,20]
    if len(fingersList)!=0:
        fingers=[]

        # for thumb finger only
        if fingersList[fingerTipIds[0]][1] < fingersList[fingerTipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        for id in range(1, 5):
            if fingersList[fingerTipIds[id]][2] < fingersList[fingerTipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        #######calculation for hand cricket############################################################################
        value = 0
        # conditions for 0
        if fingers[0] == 0 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            value = 0
            compValue=0
        # conditions for 1
        if fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            value = 1
        # condition for 2
        elif fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
            value = 2
        # condition for 3
        elif fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
            value = 3
        # condition for 4
        elif fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
            value = 4
        # condition for 5
        elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
            value = 5
        # condition for 6
        elif fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            value = 6
        else:
            value=0
            compValue=0

        if value!=0:
            #######computer player part####################################################################################
            compValue = random.randint(1, 6)

        return value,compValue

    elif(len(fingersList)==0):
        value=0
        compValue=0
        return value,compValue



def main():
    class VideoTransformer(VideoTransformerBase):
        frame_lock: threading.Lock  # `transform()` is running in another thread, then a lock object is used here for thread-safety.
        #in_image: Union[np.ndarray, None]
        out_image: Union[np.ndarray, None]

        def __init__(self) -> None:
            self.frame_lock = threading.Lock()
            #self.in_image = None
            self.out_image = None

        def transform(self, frame: av.VideoFrame) -> np.ndarray:
            in_image = frame.to_ndarray(format="bgr24")

            out_image = in_image[:, ::-1, :]  # Simple flipping for example.

            with self.frame_lock:
                self.in_image = in_image
                #self.out_image = out_image

            #return out_image
            return in_image

    ctx = webrtc_streamer(key="snapshot", 
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=RTC_CONFIGURATION,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
            video_transformer_factory=VideoTransformer)
    ############################################
    detector=htm.handDetector(detectionCon=1)
    ############################################
    if ctx.video_transformer:
        if st.button("Snapshot"):
            with ctx.video_transformer.frame_lock:
                out_image = ctx.video_transformer.in_image
                #out_image = ctx.video_transformer.out_image
                out_image = out_image.astype(np.uint8)
            if out_image is not None:
                #st.write("Input image:")
                #st.image(in_image, channels="BGR")
                st.write("Output image:")
                st.image(out_image, channels="BGR")


                ##################
                img=detector.findHands(out_image)
                fingersList=detector.findPosition(img,draw = True)
                value = processing(fingersList)
                st.info(value)
                ##################


            else:
                st.warning("No frames available yet.")


if __name__ == "__main__":
    main()