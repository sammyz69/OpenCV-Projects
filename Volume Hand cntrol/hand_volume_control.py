import cv2
import time
import numpy as np
import hand_tracking_module as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


pTime=0
cTime=0

wCam, hCam=640,480

cap= cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)

# Get default audio device using Pycaw
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Get volume range for mapping
volMin, volMax = volume.GetVolumeRange()[:2]


detector=htm.handDetector(detectionCon=0.7)

while True:
    success, img = cap.read()
    img=detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    # to do volume control we need to find position of thump tip(4) and index tip(8)
    if len(lmList) !=0:
        # print(lmList[4],lmList[8])

        x1,y1=lmList[4][1],lmList[4][2]
        x2,y2=lmList[8][1],lmList[8][2]
        cx,cy=(x1+x2)//2, (y1+y2)//2


        cv2.circle(img,(x1,y1),9,(250,0,250),cv2.FILLED)
        cv2.circle(img,(x2,y2),9,(250,0,250),cv2.FILLED)
        cv2.circle(img,(cx,cy),9,(250,0,250),cv2.FILLED)

        cv2.line(img, (x1,y1),(x2,y2),(0,100,0),3)
        length=math.hypot((x1-x2),(y1-y2))
        print(length)

        # Map the length range to volume range (e.g., 30 to 250 maps to volMin to volMax)
        vol = np.interp(length, [20, 150], [volMin, volMax])
        volume.SetMasterVolumeLevel(vol, None)

        # OPTIONAL: draw volume bar
        volBar = np.interp(length, [20, 150], [400, 150])
        volPerc = np.interp(length, [20, 150], [0, 100])

        cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volPerc)} %', (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 3)


        if length<50:
            cv2.circle(img,(cx,cy),9,(0,250,0),cv2.FILLED)

    cTime=time.time()
    fps=1/(cTime-pTime)
    pTime=cTime

    cv2.putText(img, f'FPS:{int(fps)}', (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 3)

    cv2.imshow("img", img)
    cv2.waitKey(1)

