
import site; site.addsitedir("/usr/local/lib/python2.7/site-packages")

import cv2
from find_obj import filter_matches,explore_match
import json
from matplotlib import pyplot as plt
img1 = cv2.imread('img/box.png',0)          # queryImage
img2 = cv2.imread('img/box_in_scene.png',0) # trainImage

# Initiate SIFT detector
orb = cv2.ORB()
#orb = cv2.SURF()

# find the keypoints and descriptors with SIFT
kp1, des1 = orb.detectAndCompute(img1,None)
kp2, des2 = orb.detectAndCompute(img2,None)
#print json.dumps(des1.tolist())
# create BFMatcher object
bf = cv2.BFMatcher(cv2.NORM_HAMMING)#, crossCheck=True)
FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks = 50)

flann = cv2.FlannBasedMatcher(index_params, search_params)

img3 = cv2.drawKeypoints(img1,kp1,color=(0,255,0), flags=0)
plt.imshow(img3),plt.show()
img4 = cv2.drawKeypoints(img2,kp2,color=(0,255,0), flags=0)
plt.imshow(img4),plt.show()

matches = flann.knnMatch(des1, des2, k = 2)
p1, p2, kp_pairs = filter_matches(kp1, kp2, matches)
explore_match('find_obj', img1,img2,kp_pairs)#cv2 shows image

cv2.waitKey()
cv2.destroyAllWindows()