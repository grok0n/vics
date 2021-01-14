import cv2

class picam:
	cam = None
	
	def __init__(self, width, height):
		self.cam = cv2.VideoCapture(self.gstreamer_pipeline(width, height), cv2.CAP_GSTREAMER)
	
	def gstreamer_pipeline(self, capture_width, capture_height):
		return (
			"nvarguscamerasrc ! "
			"video/x-raw(memory:NVMM), "
			"width=(int)1280, height=(int)720, "
			"format=(string)NV12, framerate=(fraction)60/1 ! "
			"nvvidconv flip-method=0 ! "
			"video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
			"videoconvert ! "
			"video/x-raw, format=(string)BGR ! appsink"
			% (
				capture_width,
				capture_height
			)
		)

	def save_image(self, path):
		cv2.imwrite(path, self.capture_image())

	def capture_image(self):
		if self.cam.isOpened():
			ret_val, img = self.cam.read()
			return img
		else:
			print("Unable to open camera")

	def cleanup(self):
		self.cam.release()

if __name__=="__main__":
	cam = picam(width=416, height=416)
	cam.save_image("test.jpg")
	
