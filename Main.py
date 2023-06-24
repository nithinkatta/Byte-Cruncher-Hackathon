import math
import cv2
import mediapipe as mp
import time
from gtts import gTTS
import os

# Uninstall playsound : pip uninstall playsound
# Install playsound of lesser version : pip install playsound==1.2.2
from playsound import playsound


class handDetector():
    def __init__(self, mode=False, maxHands=1, detectionCon=0, trackCon=0):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4,8,12,16,20]

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        bbox = []
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                # print(h,lm.y)
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                # print(id, cx, cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 7, (255, 0, 255), cv2.FILLED)
            xmin,xmax = min(xList),max(xList)
            ymin,ymax = min(yList),max(yList)
            bbox = xmin,ymin,xmax,ymax

            if draw:
                cv2.rectangle(img,(xmin-20,ymin-20),(xmax+20,ymax+20),(0,255,0,2))

        return self.lmList,bbox

    def fingersUp(self):
        fingers = []
        #thumb
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0]-1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        #fingers
        for id in range(1,5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def findDistance(self,p1,p2,img,draw=True,r=15,t=3):
        x1,y1 = self.lmList[p1][1:]
        x2,y2 = self.lmList[p2][1:]
        cx,cy = (x1+x2)//2,(y1+y2)//2

        if draw:
            cv2.line(img,(x1,y1),(x2,y2),(255,0,255),t)
            cv2.circle(img,(x1,y1),r,(255,0,255),cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
        length = math.hypot(x2-x1,y2-y1)

        return length,img,[x1,y1,x2,y2,cx,cy]


# def main():
#     pTime = 0
#     cap = cv2.VideoCapture(0)
#     detector = handDetector()
#     while True:
#         success, img = cap.read()
#         img = detector.findHands(img)
#         lmList = detector.findPosition(img)


#         cTime = time.time()
#         fps = 1 / (cTime - pTime)
#         pTime = cTime

#         cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
#                     (255, 0, 255), 3)

#         cv2.imshow("Image", img)
#         cv2.waitKey(1)

wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 7

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = handDetector()
data = []
def main():
    prev = ""
    arr = []
    global data
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList,bbox = detector.findPosition(img,draw= True)
        #print(lmList)
        flag = True
        cv2.line(img, (600, 40), (600, 100), (0, 0, 255), 3)
        if len(lmList) != 0:
            # flag = True
            fingers = detector.fingersUp()
            # print(fingers)
            totalFingers = fingers.count(1)
            # print(totalFingers)

            # cv2.rectangle(img, (20, 255), (170, 425), (0, 0, 0), cv2.FILLED)
            
            x1, y1 = lmList[4][1:]
            x2, y2 = lmList[8][1:]
            # print(x1, y1, x2, y2)

            # 3. Check which fingers are up   
            fingers = detector.fingersUp()
            # print(fingers)
            # cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
            #                 (255, 0, 255), 2)

            if fingers[0] == 1 and fingers[1] == 0 and fingers[3] == 1 and fingers[4] == 1:
                # 9. Find distance between fingers
                length, img, lineInfo = detector.findDistance(4, 8, img)
                #print(length)
                # 10. Click mouse if distance short
                if length < 40:
                    cur = "Super"
                    # arr.append(cur)
                    # obj = gTTS(text=cur, lang='en', slow=False)
                    # obj.save("super.mp3")
                    if prev != cur:
                        playsound("super.mp3")
                        arr.append(cur)
                    prev = cur
                    cv2.circle(img, (lineInfo[4], lineInfo[5]),
                                15, (0, 255, 0), cv2.FILLED)
                    # autopy.mouse.click()
                    # cv2.putText(img, " ".join(arr), (45, 65), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 5 )
                    flag = False
                

            if fingers[0]==0 and fingers[1]==1 and fingers[2]==1 and fingers[3]==1 and fingers[4]==1 and flag:
                #  print("I am fine")
                # time.sleep(1)
                cur = "I am fine"
                # obj = gTTS(text=cur, lang='en', slow=False)
                # obj.save("fine.mp3")
                if prev != cur:
                    arr.append(cur)
                    playsound("fine.mp3")
                # time.sleep(2)
                # cv2.putText(img, str("I am fine"), (45, 65), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 5 )
                prev = cur

            elif fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 1:
                cur = "are"
                # obj = gTTS(text=cur, lang='en', slow=False)
                # obj.save("are.mp3")
                if prev != cur:
                    arr.append(cur)
                    playsound("are.mp3")
                # cv2.putText(img, str("Lets play"), (45, 65), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 5 )
                prev = cur

            elif fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                cur = "How"
                # obj = gTTS(text=cur, lang='en', slow=False)
                # obj.save("how.mp3")
                if prev != cur:
                    arr.append(cur)
                    playsound("how.mp3")
                prev = cur
                # cv2.putText(img, str("Yes"), (45, 65), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 5 )

            elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                # time.sleep(2)
                cur = "call"
                # obj = gTTS(text=cur, lang='en', slow=False)
                # obj.save("call.mp3")
                if prev != cur:
                    arr.append(cur)
                    playsound("call.mp3")
                # time.sleep(2)
                # cv2.putText(img, str("Call"), (45, 65), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 5 )
                prev = cur
            
            elif fingers[0]==1 and fingers[1]==1 and fingers[2]==1 and fingers[3]==0 and fingers[4]==0:
                cur = "delete"
                if prev != cur:
                    if len(arr) > 0:
                        arr.pop()
                    if len(data) > 0:
                        data.pop()
                    
                prev = cur
            
            elif fingers[0]== 0 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                cur = "."
                if prev != cur:
                    arr.append(cur)
                data += " ".join(arr)
                arr = []
                # cv2.putText(img, str("Stop"), (45, 65), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 5 )
                prev = cur

            elif fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                cur = "You"
                # obj = gTTS(text=cur, lang='en', slow=False)
                # obj.save("you.mp3")
                if prev != cur:
                    arr.append(cur)
                    playsound("you.mp3")
                prev = cur
            

            # elif totalFingers == 1:
            #     Volume.fun() 
            # elif flag:
                # cv2.putText(img, str(totalFingers), (45, 65), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 0), 5)


            elif fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4]==1:
                data += "".join(arr)
                print(" ".join(data))
                break

        
        cv2.putText(img, " ".join(arr), (45, 65), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1 ,cv2.LINE_AA)

        if len(arr)>=5:
            data.append(" ".join(arr))
            arr = []
        cv2.imshow("Image", img)
        cv2.waitKey(3)
        # time.sleep(2)
        


if __name__ == "__main__":
    main()