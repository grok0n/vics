from devices.mpu6050 import mpu6050
from devices.picam import picam
import time

# MPU-6050 Gyroscope and Accelorometer
mpu = mpu6050(0x68)

# Raspberry Pi Camera V2
cam = None

def initialize_devices(width=500, height=500):
	# Initialize MPU-6050 device
	global mpu
	global cam

	mpu.set_accel_range(mpu.ACCEL_RANGE_2G)
	mpu.set_gyro_range(mpu.GYRO_RANGE_2000DEG)
	mpu.gyro_calibrate()

	cam = picam(width, height)

def get_halt_signal(accel):
	# The halt signal will be ON if a large negative value in the x-direction is calculated

	if abs(accel) > 10 and accel%2!=0:
		return 1
	else: 
		return 0
	
# Data collection process	
def data_collection(mins):
	
	# Get the ID of the last processed data sample
	with open("dataset/last.txt") as f:
		count = int(f.read())

	start_time = time.time()	
	
	angle_halt = open("dataset/angle_halt.txt", "a")	

	max_angle = 0
	max_accel = 0
	
	segment_start = time.time()
	# Loop until specified minutes have elasped
	while time.time() - start_time < mins*60:
		angle = int(mpu.get_angle_data()['z'])
		accel = int(mpu.get_accel_data()['x'])
		
		if abs(angle) > abs(max_angle):
			max_angle = angle
	
		if abs(accel) > abs(max_accel):
			max_accel = accel
	
		if time.time() - segment_start > 1:
			count+=1
			# Capture and save image
			cam.save_image("dataset/images/"+str(count)+".jpg")

			halt = get_halt_signal(max_accel)
			
			# write the calculated values of the angle and the halt signal to the angle_halt.txt file	
			angle_halt.write(str(max_angle)+" "+str(max_accel)+"\n")		

			max_angle = 0
			max_accel = 0

			segment_start = time.time()	

	angle_halt.close()

	# Update the start.txt file with ID of lastest processed data sample
	with open("dataset/last.txt", "w") as f:
		f.write(str(count))

initialize_devices()
time.sleep(30)
data_collection(mins=2)
cam.cleanup()