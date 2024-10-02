import cv2 as cv
import os

# Set the confidence and NMS thresholds
Conf_threshold = 0.4
NMS_threshold = 0.4
COLORS = [(255, 0, 255)]  # Use a single color

# Load class names
class_names = []
with open('classes.txt', 'r') as f:
    class_names = [cname.strip() for cname in f.readlines()]

# Load the YOLOv4 model
net = cv.dnn.readNet('yolov4-test_last_v7.weights', 'yolov4-custom.cfg')
net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv.dnn.DNN_TARGET_OPENCL_FP16)
model = cv.dnn_DetectionModel(net)
model.setInputParams(size=(416, 416), scale=1/255, swapRB=True)

# Try to load the YOLOv8 model
try:
    yolov8_model = YOLO('best.pt')
    print("YOLOv8 model loaded successfully!")
    print(yolov8_model)  # Print model summary
except Exception as e:
    print(f"Error loading the YOLOv8 model: {e}")

def detect_objects(frame):
    classes, scores, boxes = model.detect(frame, Conf_threshold, NMS_threshold)
    detected_hand_box = None
    for index, (classid, score, box) in enumerate(zip(classes, scores, boxes)):
        x, y, w, h = box
        color = COLORS[int(classid) % len(COLORS)]
        label = "%s : %.2f" % (class_names[classid], score)
        cv.rectangle(frame, box, color, 3)
        cv.putText(frame, label, (box[0], box[1]-10), cv.FONT_HERSHEY_COMPLEX, 1.5, color, 2)
        if class_names[classid] == 'hand':
            detected_hand_box = box
            hand_img = frame[y:y+h, x:x+w]

    return frame, detected_hand_box
