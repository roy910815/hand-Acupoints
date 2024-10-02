import cv2
import torch
from ultralytics import YOLO


def analysis():
    model = YOLO('best(3).pt')
    image_path = 'detected_hand.jpg'
    image = cv2.imread(image_path)

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    results = model(image_rgb)


    if len(results) > 0:
        result = results[0]  # 取第一个结果
        boxes = result.boxes  # 获取边界框信息
        keypoints = result.keypoints  # 获取关键点信息


    # 确保检测到的 boxes 不为空
        if boxes is not None and len(boxes) > 0:
            xyxy = boxes.xyxy  # 取出 xyxy 坐标
            confidences = boxes.conf  # 置信度
            class_ids = boxes.cls  # 类别 id
            names = result.names  # 类别名称

        # 绘制边界框和类别信息
            for i in range(len(xyxy)):
                x1, y1, x2, y2 = xyxy[i]
                conf = confidences[i]
                cls_id = class_ids[i]
                label = f'{names[int(cls_id)]} {conf:.2f}'
                cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 255), 2)
                cv2.putText(image, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

            # 绘制关键点
                if keypoints is not None:
                    keypoints_data = keypoints.xy  # 使用 xy 坐标
                    for keypoint in keypoints_data[i]:
                        kp_x, kp_y = keypoint[:2]  # 提取 (x, y) 坐标
                        cv2.circle(image, (int(kp_x), int(kp_y)), 5, (141, 180, 137), -1)  # 绿色圆点
        else:
            print("No detections found in the image.")
    else:
        print("No results returned by the model.")

    screen_res = 360, 640  # 这里设置为 980x600 的分辨率，您可以根据需要调整
    scale_width = screen_res[0] / image.shape[1]
    scale_height = screen_res[1] / image.shape[0]
    scale = min(scale_width, scale_height)
    window_width = int(image.shape[1] * scale)
    window_height = int(image.shape[0] * scale)

    # 使用 OpenCV 调整图像大小
    image = cv2.resize(image, (window_width, window_height))
    cv2.imwrite('detected_hand.jpg', image)


    

# 显示调整大小后的图像

