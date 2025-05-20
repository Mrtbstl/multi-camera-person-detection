from flask import Flask, Response, request, jsonify
from ultralytics import YOLO
import threading
import cv2

#Initialize Flask for REST API communication
app = Flask(__name__)

#Variables for cameras
people_detected_1 = 0
people_detected_2 = 0

#Flags to start/stop streams
stream_flags = {0: True, 1: True}

#Load YOLOv5n model for person detection
model = YOLO("yolov5n.pt")  

def frame_generation(cam_index):  #Video stream generator function
    global people_detected_1, people_detected_2

    #Open the indexed camera
    camera = cv2.VideoCapture(cam_index)
    frame_count = 0

    while True:
        if not stream_flags[cam_index]:  #Skip processing if stream is stopped
            continue

        success, frame = camera.read()
        if not success:
            break

        frame_count += 1

        #Detect people using the model
        results = model(frame)
        boxes = results[0].boxes

        person_boxes = []
        for box in boxes:
            cls = int(box.cls[0])  #Extract class label
            if cls == 0:  #Class 0 corresponds to person in YOLO
                x1, y1, x2, y2 = map(int, box.xyxy[0])  #Get bounding box coordinates
                person_boxes.append((x1, y1, x2 - x1, y2 - y1))  #Transforming xyxy format to (x, y, w, h)

        #Update detected count for the indexed camera
        if cam_index == 0:
            people_detected_1 = len(person_boxes)
        elif cam_index == 1:
            people_detected_2 = len(person_boxes)

        #Draw boxes around people
        for (x, y, w, h) in person_boxes:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        #Encode frame as JPEG and yield for streaming
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')  #HTML + CSS + basic Javascript to add person counts beneath the cam feeds and to improve looks
def index():
    return '''   
    <html>
    <head>
        <title>Multi-Camera Stream for Person Detection</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                background-color: #f9f9f9;
            }
            .container {
                display: flex;
                justify-content: center;
                gap: 40px;
                margin-top: 30px;
            }
            .camera-block {
                background-color: #fff;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            h1 {
                text-align: center;
            }
            img {
                max-width: 100%;
                height: auto;
                border-radius: 6px;
            }
        </style>
        <script>
            function updatePeople() {
                fetch('/status')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('people-count-1').innerText = "People detected (Camera 1): " + data.people_detected_1;
                        document.getElementById('people-count-2').innerText = "People detected (Camera 2): " + data.people_detected_2;
                    });
            }
            setInterval(updatePeople, 1000);  // Update person count every second
        </script>
    </head>
    <body>
        <h1>Multi-Camera Person Detection</h1>
        <div class="container">
            <div class="camera-block">
                <h2>Camera 1 (iPhone)</h2>
                <img src="/video_feed_1"><br>
                <h3 id="people-count-1">People detected (Camera 1): ...</h3>
            </div>
            <div class="camera-block">
                <h2>Camera 2 (MacBook)</h2>
                <img src="/video_feed_2"><br>
                <h3 id="people-count-2">People detected (Camera 2): ...</h3>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/video_feed_1')  #Route for first cam
def video_feed_1():
    return Response(frame_generation(0), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_2')  #Route for second cam
def video_feed_2():
    return Response(frame_generation(1), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')  #REST endpoint for returning current people count
def status():
    return {
        "status": "Running",
        "people_detected_1": people_detected_1,
        "people_detected_2": people_detected_2
    }

@app.route('/control', methods=['POST'])  #REST endpoint to control stream on/off
def control():
    cam = int(request.args.get('cam', -1))  #Get camera index from query string
    action = request.args.get('action', '')  #Get action string: start or stop
    if cam not in stream_flags:
        return jsonify({"error": "Invalid camera index"}), 400
    if action == 'start':
        stream_flags[cam] = True
    elif action == 'stop':
        stream_flags[cam] = False
    else:
        return jsonify({"error": "Invalid action"}), 400
    return jsonify({"message": f"Camera {cam} stream {action}ed."})

if __name__ == '__main__':
    #Start Flask app in a background thread
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5050)).start()
