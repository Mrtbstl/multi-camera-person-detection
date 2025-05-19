from flask import Flask, Response
import cv2

app = Flask(__name__)
camera = cv2.VideoCapture(0)
#Variables for cameras
faces_detected_1 = 0
faces_detected_2 = 0

#Video stream generator function
def frame_generation(cam_index):
    global faces_detected_1, faces_detected_2
    #Load OpenCV face detection model
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    #Open the indexed camera
    camera = cv2.VideoCapture(cam_index)
    frame_count = 0
    last_faces = []

    while True:
        success, frame = camera.read()
        if not success:
            break

        frame_count += 1

        if True: #Analyze every 5 frame to reduce CPU usage
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=6,     #This part is added for eliminating false faces and ignoring small areas
                minSize=(60, 60)    
            )

            #Update face count for each camera
            if cam_index == 0:
                faces_detected_1 = len(faces)
            elif cam_index == 1:
                faces_detected_2 = len(faces)
        else:
            faces = last_faces.copy()                                                           

        #Draw boxes around faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        #Encode and send
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index(): #HTML with some simple CSS for better looks and JavaScript for face count under camera feed
    return '''   
    <html>
    <head>
        <title>Multi-Camera Stream for Face Detection</title>
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
            function updateFaces() {
                fetch('/status')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('face-count-1').innerText = "Faces detected (Camera 1): " + data.faces_detected_1;
                        document.getElementById('face-count-2').innerText = "Faces detected (Camera 2): " + data.faces_detected_2;
                    });
            }
            setInterval(updateFaces, 1000);
        </script>
    </head>
    <body>
        <h1>Multi-Camera Face Detection</h1>
        <div class="container">
            <div class="camera-block">
                <h2>Camera 1 (iPhone)</h2>
                <img src="/video_feed_1"><br>
                <h3 id="face-count-1">Faces detected (Camera 1): ...</h3>
            </div>
            <div class="camera-block">
                <h2>Camera 2 (MacBook)</h2>
                <img src="/video_feed_2"><br>
                <h3 id="face-count-2">Faces detected (Camera 2): ...</h3>
            </div>
        </div>
    </body>
    </html>
    '''

#Define routes
@app.route('/video_feed_1')
def video_feed_1():
    return Response(frame_generation(0), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_2')
def video_feed_2():
    return Response(frame_generation(1), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/status')
def status():
    return {
        "status": "Running",
        "faces_detected_1": faces_detected_1,
        "faces_detected_2": faces_detected_2
    }

#Start the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

