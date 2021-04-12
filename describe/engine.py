"""
Processes the output of the YOLO objection detection algorithm to get a list of object that were found in the image as well as their locations.
The engine then uses a text-to-speech module to say what was in the captured scenery
"""
import cv2
import asyncio

import os
os.sys.path.append("..")

import numpy as np
from devs_and_utils.picam import picam
from devs_and_utils.google_voice import GoogleVoice
from detector import ObjectDetector

import time # Take out

from playsound import playsound

class SceneDescribeSystem:
	
	def __init__(self, scene_size=416, division=1):
		self.division = division # Use _get_object_location1 or __get_object_location2
		self.scene_size = scene_size

		# Raspbery Pi Cam for taking 416x416 images of scenery
		self.cam = picam(width=scene_size, height=scene_size)
	
		# Speech to text module
		self.voice = GoogleVoice()

		# object detector
		self.detector = ObjectDetector()

	# Takes information of a box and returns the box location (Top left, Top center, Top right, Bottom left, Bottom center, Bottom right)
	def __get_object_location1(self, x1, y1, x2, y2):
		scene_3 = self.scene_size/3
		scene_2 = self.scene_size/2
		divs_x = [scene_3, 2*scene_3, self.scene_size]
		divs_y = [scene_2, self.scene_size]

		x_overlaps = [0,0,0]
		y_overlaps = [0,0]
	
		for i in range(3):
			overlapx = max(min(x2, divs_x[i]) - max(x1, divs_x[i]-scene_3), 0)
			x_overlaps[i] = overlapx;	

		for i in range(2):
			overlapy = max(min(y2, divs_y[i]) - max(y1, divs_y[i]-scene_2), 0)
			y_overlaps[i] = overlapy;	

		x_div_name = ["left", "center", "right"]
		y_div_name = ["top", "bottom"]
	
		return (y_div_name[np.argmax(np.array(y_overlaps))] + " " + x_div_name[np.argmax(np.array(x_overlaps))])

	# Takes information of a box and returns the box location (Top left, Top center, Top right, Mid left, Mid center, Mid right, Bottom left, Bottom center, Bottom right)
	def __get_object_location2(self, x1, y1, x2, y2):
		scene_3 = self.scene_size/3
		divs = [scene_3, 2*scene_3, self.scene_size]

		x_overlaps = [0,0,0]
		y_overlaps = [0,0,0]
	
		for i in range(3):
			overlapx = max(min(x2, divs[i]) - max(x1, divs[i]-scene_3), 0)
			x_overlaps[i] = overlapx;	

			overlapy = max(min(y2, divs[i]) - max(y1, divs[i]-scene_3), 0)
			y_overlaps[i] = overlapy;	

		x_div_name = ["left", "center", "right"]
		y_div_name = ["top", "mid", "bottom"]
	
		return (y_div_name[np.argmax(np.array(y_overlaps))] + " " + x_div_name[np.argmax(np.array(x_overlaps))])


	# Take in a list of objects detected in scene and return an appropriate text response that describes the scene
	def __generate_response(self, objs):
		response = ""
	
		num_objs = len(objs)

		for i in range(num_objs):
			if i == (num_objs-1):
				response += ("and ")
	
			response += ("there is ")
			if objs[i][0][0] in ["a","e","i","o","u"]:
				response += ("an ")
			else:
				response += ("a ")

			response += ("{0} at the ".format(objs[i][0]))
			response += ("{0} corner of the scene, ".format(objs[i][1]))

		return response[:-2] # get rid of extra ", " at end

	def cleanup(self):
		self.cam.cleanup()

	def run(self):
		# Capture the scene and returned voice response of the objects in the scene def run(self, division=2): # Capture image
		img = self.cam.capture_image()
	
		start = time.time()
		# Run inference
		res = self.detector.detect(img)
		end = time.time()
		print(f"Ran inference in {end - start} seconds!")

		response = None
		if type(res) != int:
			# Create python list of the objects of the format [class_name, object_location]
			objs = []
			for obj in res:
				if self.division == 1:
					objs.append([obj[4], self.__get_object_location1(obj[0], obj[1], obj[2], obj[3])])
				else:
					objs.append([obj[4], self.__get_object_location2(obj[0], obj[1], obj[2], obj[3])])
		
			# Generate response using list
			response = self.__generate_response(objs)

		else:
			response = "Sorry, no objects were detected."

		print(response)
		
		# Turn generated response to speech
		self.voice.text_to_speech(voice_name="en-GB-Standard-B", text=response, name="response")	

		# Send generated audio file "response.wav" to speakers
		response_wav = open("response.wav", "rb")

		playsound("response.wav") # play repsonse on speakers

		# Delete response.wav
		os.remove("response.wav")
		
if __name__=="__main__":
	system = SceneDescribeSystem()
	start = time.time()
	system.run()
	system.cleanup()

