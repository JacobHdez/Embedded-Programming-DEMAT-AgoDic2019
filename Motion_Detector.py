import cv2, socket
import numpy as np

from urllib.request import urlopen

UDP_IP_1 = "192.168.1.110"
UDP_IP_2 = "192.168.1.117"

UDP_PORT_1 = 8080
UDP_PORT_2 = 8080

MESSAGE = "Detected"
bytes_to_send = str.encode(MESSAGE)

update_back = 120 # 15 fps
update_gray = update_back

packet_send = 0
motion_detected = 0

count_motion = 1
'''
print("UDP target IP:", UDP_IP_1)
print("UDP target port:", UDP_PORT_1)

print("UDP target IP:", UDP_IP_2)
print("UDP target port:", UDP_PORT_2)

print("Message:", MESSAGE)
'''
static_back = None

#print("Open the stream")
stream = urlopen("http://192.168.1.119:81/stream")
mbytes = bytes()

while True:
	mbytes += stream.read(1024)

	a = mbytes.find(b'\xff\xd8')
	b = mbytes.find(b'\xff\xd9')
	if a != -1 and b != -1:
		frame = mbytes[a : b + 2]
		mbytes = mbytes[b + 2 :]

		frame = cv2.imdecode(np.frombuffer(frame, dtype = np.uint8), cv2.IMREAD_COLOR)

		gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
		gray = cv2.GaussianBlur(gray, (21, 21), 0)

		if update_gray == update_back:
			static_back = None
			update_gray -= 1
		elif update_gray == 0:
			update_gray = update_back
		else:
			update_gray -= 1

		if static_back is None:
			static_back = gray
			continue

		diff_frame = cv2.absdiff(static_back, gray)

		thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
		thresh_frame = cv2.dilate(thresh_frame, None, iterations = 2)

		cnts, hierarchy = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		motion_detected = 0
		for contour in cnts:
			if cv2.contourArea(contour) < 5000:
				continue

			motion = 1
			motion_detected = 1

			if packet_send == 0:
				sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				sock.sendto(bytes_to_send, (UDP_IP_1, UDP_PORT_1))
				sock.sendto(bytes_to_send, (UDP_IP_2, UDP_PORT_2))

				#print(count_motion, MESSAGE)
				count_motion += 1

				packet_send = 1

			(x, y, w, h) = cv2.boundingRect(contour)
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)

		if motion_detected == 0:
			if packet_send == 1:
				packet_send = 0
				print("NMD")
		'''
		cv2.imshow("Gray Frame", gray)
		cv2.imshow("Difference Frame", diff_frame)
		cv2.imshow("Threshold Frame", thresh_frame)
		cv2.imshow("Color Frame", frame)

		key = cv2.waitKey(1)
		if (key) == ord('q'):
			break
		'''

#cv2.destroyAllWindows()
