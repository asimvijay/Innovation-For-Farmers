import cv2
import os
import glob

images = glob.glob("./static/*.jpg")
images = sorted(images, key=os.path.getctime)
vid = []
for image in images:
    img = cv2.imread(image)
    height, width, layers = img.shape
    size = (width, height)
    vid.append(img)


out = cv2.VideoWriter('timelapse1.mp4',cv2.VideoWriter_fourcc(*'DIVX'),15,size)

for i in range(len(vid)):
    out.write(vid[i])
out.release()

print(images)
print(len(images))

