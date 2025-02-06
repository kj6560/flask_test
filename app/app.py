from flask import Flask, jsonify, request,send_from_directory
from flaskext.mysql import MySQL
import os
from nudenet import NudeDetector
import cv2
import os
myapp = Flask(__name__)

# Create necessary directories for storing the video and frames
UPLOAD_FOLDER = '/var/www/shiwkesh/nudity/app/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
# Initialize NudeDetector
detector = NudeDetector()

mysql = MySQL()
myapp.config['MYSQL_DATABASE_USER'] = 'keshav_sr'
myapp.config['MYSQL_DATABASE_PASSWORD'] = 'ProKj!@12'
myapp.config['MYSQL_DATABASE_DB'] = 'nudity'
myapp.config['MYSQL_DATABASE_HOST'] = '114.69.243.150'
myapp.config['MYSQL_DATABASE_PORT'] = 47849
mysql.init_app(myapp)

@myapp.route('/', methods=['GET'])
def home():
    conn = mysql.connect()
    cursor =conn.cursor()

    cursor.execute("SELECT * from users")
    data = cursor.fetchall()
    return jsonify({
        'users':data
    })
@myapp.route('/uploads/<path:filename>')
def get_uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@myapp.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        # Save the file to the uploads directory
        image_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(image_path)

    # Run Nude Detection on the image
    classification_result = detector.detect(image_path)
    # Analyze the results
    result = is_explicit_content(classification_result)

    # Remove the saved image after processing
    # os.remove(image_path)

    # Return response
    return jsonify({
        "details": result,
        "explicit_content": True if len(result) > 0 else False
        
    })


def extract_frames(video_path, frame_interval=5):
    """
    Extracts frames from a video at a given interval.
    """
    frames = []
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))  # Frames per second
    frame_count = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        # Capture frame every `frame_interval` seconds
        if frame_count % (frame_interval * fps) == 0:
            timestamp = frame_count / fps  # Calculate timestamp for the frame
            timestamp_str = f"{timestamp:.2f}"  # Format timestamp for filename
            frame_filename = os.path.join(UPLOAD_FOLDER, f"frame_{timestamp_str}.jpg")
            cv2.imwrite(frame_filename, frame)
            frames.append((timestamp_str, frame_filename))  # Save timestamp and frame path

        frame_count += 1

    cap.release()
    return frames

def is_explicit_content(predictions, threshold=0.50):
    explicit_classes = {"FEMALE_BREAST_EXPOSED", "BUTTOCKS_EXPOSED", "FEMALE_GENITALIA_EXPOSED", "MALE_GENITALIA_EXPOSED"}
    result = []

    for item in predictions:
        if item["score"] > threshold and item["class"] in explicit_classes:
            data = {
                "class": item["class"],
                "score_percentage": item["score"]*100,
                "explicit": True
            }
            result.append(data)  # Append to the list instead of overwriting

    return result  # Return a list of explicit content matches

def is_explicit_video_content(predictions, threshold=0.50):
    explicit_classes = {"FEMALE_BREAST_EXPOSED", "BUTTOCKS_EXPOSED", "FEMALE_GENITALIA_EXPOSED", "MALE_GENITALIA_EXPOSED"}
    for item in predictions:
        if item["score"] > threshold and item["class"] in explicit_classes:
            return True  # Return True if explicit content is detected
    return False  # Return False if no explicit content is detected
@myapp.route('/predict_video', methods=['POST'])
def predict_video():
    try:
        # Check if video file is provided
        if 'video' not in request.files:
            return jsonify({"error": "No video file provided"}), 400

        video_file = request.files['video']
        video_path = os.path.join(UPLOAD_FOLDER, video_file.filename)

        # Save the video file
        video_file.save(video_path)
        print(f"Video saved to: {video_path}")  # Debug statement

        # Extract frames from video
        frames = extract_frames(video_path, frame_interval=1)
        print(f"Extracted {len(frames)} frames")  # Debug statement

        flagged_frames = []

        # Process each frame for nudity detection
        for timestamp, frame_path in frames:
            detections = detector.detect(frame_path)
            flagged_detections = is_explicit_content(detections, threshold=0.50)

            if flagged_detections:
                flagged_frames.append({
                    "timestamp": timestamp,
                    "frame_path": frame_path,
                    "detections": flagged_detections
                })
            else:
                os.remove(frame_path)  # Delete frame after processing

        # Clean up the uploaded video file
        os.remove(video_path)

        # Prepare response with only flagged classes and frame paths
        responseData = []
        for frame_data in flagged_frames:
            for item in frame_data["detections"]:
                responseData.append({
                    "timestamp": frame_data["timestamp"],
                    "class": item["class"],
                    "score_percentage": item["score_percentage"],
                    "frame_path": frame_data["frame_path"]
                })

        return jsonify({
            "flagged_timestamps": responseData,
            "explicit_detected": len(flagged_frames) > 0
        })

    except Exception as e:
        print(f"Error in /predict_video: {str(e)}")  # Debug statement
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    myapp.run(debug=True)
