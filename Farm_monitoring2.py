import cv2
import argparse
import numpy as np

from firebase import Firebase


config = {
  "apiKey": "AIzaSyBszPH4eiKWK967_Sak7_poVgw8YirawHg",
  "authDomain": "iot-project-75a09.firebaseapp.com",
  "databaseURL": "https://iot-project-75a09-default-rtdb.firebaseio.com",
  "projectId": "iot-project-75a09",
  "storageBucket": "iot-project-75a09.appspot.com",
  "messagingSenderId": "223980456770",
  "appId": "1:223980456770:web:28c9f1e11dfe2ad1a416db",
  "measurementId": "G-QPBKEX3VYN"
}

firebase = Firebase(config)
db = firebase.database()


def get_output_layers(net):
    
    layer_names = net.getLayerNames()
    
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    #print(output_layers)

    return output_layers


def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):

    label = str(classes[class_id])
    color = COLORS[class_id]

    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
    cv2.putText(img, label, (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    #print(label)
cam = cv2.VideoCapture(0)

classes = None

with open('yolov3.txt', 'r') as f:
    classes = [line.strip() for line in f.readlines()]

print(len(classes))
        
COLORS = np.random.uniform(0, 255, size=(len(classes)+30, 3))
while True:
    
    _,image = cam.read()

    Width = image.shape[1]
    Height = image.shape[0]
    scale = 0.00392
    
    net = cv2.dnn.readNet('yolov3.weights', 'yolov3.cfg')

    blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)

    net.setInput(blob)

    outs = net.forward(get_output_layers(net))

    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.4

    flag_bike = 0
    flag_person = 0

    for out in outs:
        for detection in out:
            #print(len(detection))
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.7:
                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])

                
        cv2.imshow('object detection', image)
        if(cv2.waitKey(1) == ord('q')):
            cv2.imwrite('object-detection.jpg', image)
            break


    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    Human_count=0
    Cow_count=0
    Sheep_count=0
    elephant_Alert_flag=0
    dog_Alert_flag=0
    bear_Alert_flag=0

    Drinking_cow_count = 0
    Drinking_sheep_count = 0
    
    for i in indices:

            box = boxes[i]
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]
            draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))

            class_id = class_ids[i]

            label = str(classes[class_id])
            print(label)

            if(label=='Human'):
                Human_count+=1

            if(label=='cow'):
                Cow_count+=1

            if(label=='sheep'):
                Sheep_count+=1
                
            if(label=='elephant'):
                elephant_Alert_flag=1

            if(label=='dog'):
                dog_Alert_flag=1

            if(label=='bear'):
                bear_Alert_flag=1
            
            if(round(x)>round(2*Width/3)):
                if(label=='cow'):
                    Drinking_cow_count+=1

                if(label=='sheep'):
                    Drinking_sheep_count+=1
                
              

            
            cv2.imshow('object detection', image)
            if(cv2.waitKey(1) == ord('q')):
                cv2.imwrite('object-detection.jpg', image)
                break
            
    print(f'Human Count: + {Human_count}')
    print(f'Cow Count: + {Cow_count}')
    print(f'Sheep Count: + {Sheep_count}')
    
    cv2.putText(image, 'Human count  : '+ str(Human_count), (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 2)
    cv2.putText(image, 'Cow Count    : '+ str(Cow_count) + ' , Drinking Cow Count: ' + str(Drinking_cow_count), (10,80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 2)
    cv2.putText(image, 'Sheep Count  : '+ str(Sheep_count) + ' , Drinking sheep Count: ' + str(Drinking_sheep_count), (10,100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 2)

    Alert_animal_flag=0
    Alert_animal = ''
    if(dog_Alert_flag==1):
        Alert_animal=Alert_animal+ 'dog'
        Alert_animal_flag=1

    if(elephant_Alert_flag==1):
        Alert_animal=Alert_animal+ '  elephant'
        Alert_animal_flag=1

    if(bear_Alert_flag==1):
        Alert_animal=Alert_animal+ '  bear'
        Alert_animal_flag=1

    if(dog_Alert_flag==1) or (elephant_Alert_flag==1) or (bear_Alert_flag==1):
        cv2.putText(image, Alert_animal + ' detected', (10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
        

    
    cv2.rectangle(image, (round(2*Width/3),0), (round(2*Width/3),Height),(0,0,0), 2)

    db.child("Farm_monitoring").child("Cow Count").set(Cow_count)
    db.child("Farm_monitoring").child("Sheep Count").set(Sheep_count)
    db.child("Farm_monitoring").child("Drinking Cow Count").set(Drinking_cow_count)
    db.child("Farm_monitoring").child("Drinking sheep Count").set(Drinking_sheep_count)
    db.child("Farm_monitoring").child("alert animal").set(Alert_animal)
    db.child("Farm_monitoring").child("alert animal flag").set(Alert_animal_flag)
    

    cv2.imshow('object detection', image)
    if(cv2.waitKey(1) == ord('q')):
        cv2.imwrite('object-detection.jpg', image)
        break
    
cam.release()        
cv2.destroyAllWindows()
