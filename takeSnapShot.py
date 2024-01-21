import sys
import os
from os.path import exists
import requests
import time
from time import sleep
from datetime import datetime, timedelta
from PIL import Image
from PIL import ImageEnhance
from io import BytesIO

camera_connections = {}
rtsp_username = "admin"
rtsp_password = "w99g4yczb"
ipAddress = "192.168.1.100"
width = 800
height = 480
cameras = 2
channels = {1:0, 2:0}
year, month, day  = 2024, 1, 5
cam_1_time = 0
cam_2_time = 0

def secs():
    return time.time()

def calculateChickWeek():
    current_date_time = datetime.now()
    chick_date = datetime(year, month, day)
    current_date = datetime(current_date_time.year, 
                            current_date_time.month, 
                            current_date_time.day)
    week_diff = (current_date - chick_date).days // 7
    return week_diff

def checkFiles():
    week_diff = calculateChickWeek()
    output_path = f"/home/pi/Documents/TakeSnapShot/images/week_{week_diff}/output"
    if not exists(output_path):
        os.makedirs(output_path)
    for i in range(1, (len(channels) + 1)):
        picNo = 0
        dir_path = f"/home/pi/Documents/TakeSnapShot/images/week_{week_diff}/camera_{i}"
        if not exists(dir_path):
            os.makedirs(dir_path)
        for path in os.listdir(dir_path):
            if os.path.isfile(os.path.join(dir_path, path)):
                picNo += 1
        channels[i] = picNo
        # print(f"There are {picNo} images on camera {i}")
    return week_diff

def editImages(week_diff, cam_1, cam_2, image):
    dir_path = f"/home/pi/Documents/TakeSnapShot/images/week_{week_diff}"
    # Open the images
    image1 = Image.open(f"{dir_path}/camera_{cam_1}/{image}.jpg")
    image2 = Image.open(f"{dir_path}/camera_{cam_2}/{image}.jpg")

    # Resize images to the same height
    print(f"image size is {image1.width}x{image1.height}")
    image1 = image1.resize((960, 540))
    image2 = image2.resize((image1.width, image1.height))

    #Create a new image with the appropriate height and combine width
    new_image = Image.new('RGB', (image1.width + image2.width, image1.height))

    #Paste the two images into the new image
    new_image.paste(image1, (0, 0))
    new_image.paste(image2, (image1.width, 0))

    #Save the result
    new_image.save(f"/home/pi/Documents/TakeSnapShot/images/week_{week_diff}/output/{image}.jpg")
    
def capture_from_camera(week_diff, cam_no, picNo):
    dir_path = f"/home/pi/Documents/TakeSnapShot/images/week_{week_diff}"
    url = f"http://{rtsp_username}:{rtsp_password}@{ipAddress}/ISAPI/Streaming/channels"\
        f"/{cam_no}01/picture?videoResolutionWidth=1920&videoResolutionHeight=1080"
    response = requests.get(url)
    if response.status_code == 200:
        #Convert the response content to an image
        print(f"taking image: {picNo} on camera {cam_no}")
        image = Image.open(BytesIO(response.content))
        # Save the image
        image.save(f"{dir_path}/camera_{cam_no}/{picNo}.jpg")
        picNo += 1
        channels[cam_no] = picNo
    else:
        print("Failed to retrieve the snapshot. Status code: ", response.status_code)
    
    
def main():
    
    start_time = secs()
    try:
        while True:
            current_time = secs()
            if (current_time - start_time) >= 5:
                week_diff = checkFiles()
                for i in range(1, (len(channels) + 1)):
                    capture_from_camera(week_diff, i, channels[i])
                editImages(week_diff, 1, 2, channels[1]-1)
                start_time = secs()
    except KeyboardInterrupt:
        print("Program interrupt by the user.")
    finally:
        print("Resources have been released. Program terminated. ")

if __name__ == '__main__':    
    main() 