import site; site.addsitedir("/usr/local/lib/python2.7/site-packages")
import cv2
import json
from matplotlib import pyplot as plt
img1 = cv2.imread('img/id.png',0)          # queryImage
# trainImage

# Initiate SIFT detector
#orb = cv2.ORB()
orb = cv2.ORB()

# find the keypoints and descriptors with SIFT
kp1, des1 = orb.detectAndCompute(img1,None)
#kp2, des2 = orb.detectAndCompute(img2,None)
#print json.dumps(des1.tolist())
# create BFMatcher object
#bf = cv2.BFMatcher(cv2.NORM_HAMMING)#, crossCheck=True)

img3 = cv2.drawKeypoints(img1,kp1,color=(0,255,0), flags=0)
plt.imshow(img3),plt.show()
#img4 = cv2.drawKeypoints(img2,kp2,color=(0,255,0), flags=0)
#plt.imshow(img4),plt.show()

#matches = bf.knnMatch(des1, trainDescriptors = des2, k = 2)
#p1, p2, kp_pairs = filter_matches(kp1, kp2, matches)
#explore_match('find_obj', img1,img2,kp_pairs)#cv2 shows image

cv2.waitKey()
cv2.destroyAllWindows()