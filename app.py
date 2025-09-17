import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import tempfile
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode, RTCConfiguration
import av
import os
from datetime import datetime
import altair as alt

st.set_page_config(
    page_title="SAI Talent Assessment",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏆"
)

# Custom CSS
st.markdown("""
<style>
    /* Main body background and text */
    .main, .st-emotion-cache-18ni7ap {
        background-color: #2c3e50;
        color: #ecf0f1;
    }
    .st-emotion-cache-18ni7ap {
        background-color: #2c3e50;
    }
    
    /* Titles and headers */
    .st-emotion-cache-10trblm {
        color: #ecf0f1;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1f2c38;
        border-right: 1px solid #34495e;
    }
    [data-testid="stSidebar"] .st-emotion-cache-163tt8u {
        color: #ecf0f1;
    }
    
    /* Containers and Cards */
    .st-emotion-cache-13ln4j9 {
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        background-color: #34495e;
        margin-bottom: 2rem;
    }

    /* Buttons */
    .st-emotion-cache-16ids9s {
        background-color: #3498db;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.2s ease;
    }
    .st-emotion-cache-16ids9s:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: bold;
        color: #ecf0f1;
    }
    [data-testid="stMetricLabel"] {
        color: #bdc3c7;
        font-size: 1.2rem;
    }
    
    /* Info/Warning boxes */
    .stAlert {
        border-radius: 8px;
        padding: 1rem;
    }
    .stAlert.st-emotion-cache-16x1m8v {
        background-color: #2e86c1;
        border-left: 5px solid #3498db;
    }
    .stAlert.st-emotion-cache-1457p2d {
        background-color: #d68910;
        border-left: 5px solid #f39c12;
    }

    /* Input fields */
    .st-emotion-cache-1wivf2l {
        background-color: #49637e;
        color: #ecf0f1;
    }
    .st-emotion-cache-1wivf2l:focus {
        border-color: #3498db;
    }
    
    /* New Login/Signup Style */
    .login-container {
        padding: 2rem;
        background-color: #1f2c38;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        max-width: 500px;
        margin: auto;
    }
    .stTabs [data-testid="stTabContent"] {
        background-color: #1f2c38;
        padding-top: 1rem;
    }
    .stTabs [data-testid="stTab"] {
        font-size: 1.2rem;
        font-weight: bold;
    }
    .stTabs [data-testid="stTab"]:hover {
        color: #3498db;
    }
</style>
""", unsafe_allow_html=True)

# ----- Multilingual Support and Role Mapping -----
# We use canonical names for roles and tests to avoid breaking logic
# when the language changes.
CANONICAL_ROLES = {
    "athlete": "athlete",
    "sai_member": "sai_member"
}
CANONICAL_TESTS = {
    "jumps": "jumps",
    "situps": "situps",
    "pushups": "pushups",
    "pullups": "pullups"
}

LANGUAGES = {
    "English": {
        "dashboard": "🏆 SAI Talent Assessment Platform (Khel Setu)",
        "subheader": "### Assess your performance with AI-based metrics, badges, and leaderboard tracking!",
        "athlete_submission": "👤 Athlete Submission",
        "leaderboard": "🏅 Leaderboard",
        "video_upload": "Video Upload",
        "real_time": "Real-Time Camera",
        "generate_report": "Generate Report",
        "submit_report": "Submit Report to SAI",
        "tips": "💡 Tips for best performance",
        "warning_tip": "⚠️ Ensure full body visibility and stable lighting.",
        "jump_tip": "Try to jump with knees fully extended for consistent detection.",
        "pullup_tip": "Ensure your chin clears the bar on each pull-up.",
        "pushup_tip": "Keep your back straight and lower yourself until your elbows are at a 90-degree angle.",
        "situp_tip": "Bring your chest to your knees and go all the way back down until your back is flat on the ground.",
        "navigation": "Navigation",
        "name": "Name",
        "age": "Age",
        "gender": "Gender",
        "test_mode": "Test Mode",
        "test_type": "Test Type",
        "male": "Male",
        "female": "Female",
        "other": "Other",
        "video_upload_option": "Video Upload",
        "real_time_option": "Real-Time Camera",
        "warning_person_not_detected": "⚠️ Person not detected!",
        "score": "Score",
        "warnings": "Warnings",
        "badge": "Badge",
        "segments": "Segments",
        "segment_label": "Segment",
        "submit_report_success": "✅ Report Submitted!",
        "report_deleted": "✅ Report Deleted!",
        "video_not_available": "Video not available.",
        "please_provide_name_video": "Please provide your name and upload a video file.",
        "please_provide_name_generate_report": "Please enter your name to generate a report.",
        "saving_processing_video": "Saving and processing video...",
        "analyzing_video": "Analyzing video...",
        "report_generated": "✅ Report Generated!",
        "real_time_report_generated": "✅ Real-Time Report Generated!",
        "saimember_dashboard": "📝 SAI Member Dashboard",
        "no_submissions": "No athlete submissions yet.",
        "delete_report_button": "Delete This Report",
        "ensure_visible_camera": "Ensure full body is visible in camera frame!",
        "jumps_title": "Jumps",
        "situps_title": "Sit-ups",
        "pushups_title": "Push-ups",
        "pullups_title": "Pull-ups",
        "no_video_data": "Video data not available for real-time mode.",
        "login_page": "👤 Login / Registration",
        "my_dashboard": "My Dashboard",
        "username": "Username",
        "password": "Password",
        "login": "Login",
        "register": "Register",
        "logout": "Logout",
        "login_success": "✅ Logged in successfully!",
        "registration_success": "✅ Registration successful! You can now log in.",
        "invalid_credentials": "❌ Invalid username or password.",
        "user_exists": "❌ Username already exists. Please choose another one.",
        "user_dashboard_title": "My Performance Dashboard",
        "your_score": "Your Score",
        "your_badge": "Your Badge",
        "welcome": "Welcome",
        "email_address": "Email Address",
        "forgot_password": "Forgot password?",
        "not_a_member": "Not a member?",
        "signup_now": "Signup now",
        "your_performance_summary": "Your Performance Summary",
        "all_your_reports": "All Your Reports",
        "athlete_info": "Athlete Information",
        "test_configuration": "Test Configuration",
        "no_scores_to_show": "No scores to show.",
        "too_many_warnings": "⚠️ Too many warnings received. Please adjust your position and lighting.",
        "try_to_improve_score": "💡 Try to increase your score for better results!",
        "please_upload_video": "Please upload a video file.",
        "current_realtime_score": "Current Real-Time Score",
        "real_time_warnings": "Warnings",
        "performance_report": "Performance Report",
        "video_player_title": "Video Player",
        "video_playback": "Video Playback",
        "timeline": "Timeline",
        "submission_status": "Submission Status",
        "submit_report_to_sai": "Submit Report to SAI",
        "sai_member_dashboard": "📝 SAI Member Dashboard",
        "review_pending": "Pending Review",
        "approved_by_sai": "Approved by SAI",
        "report_detail": "Report Details",
        "athlete_name": "Athlete Name",
        "sai_status": "SAI Status",
        "delete_report": "Delete This Report",
        "select_role": "Select Your Role",
        "athlete_role": "Athlete",
        "sai_member_role": "SAI Member",
        "role_mismatch": "❌ Role does not match the username."
    },
    "Hindi": {
        "dashboard": "🏆 एसएआई प्रतिभा मूल्यांकन प्लेटफ़ॉर्म (खेल सेतु)",
        "subheader": "### एआई आधारित मेट्रिक्स, बैज और लीडरबोर्ड ट्रैकिंग के साथ अपना प्रदर्शन मूल्यांकन करें!",
        "athlete_submission": "👤 एथलीट सबमिशन",
        "leaderboard": "🏅 लीडरबोर्ड",
        "video_upload": "वीडियो अपलोड करें",
        "real_time": "रीयल-टाइम कैमरा",
        "generate_report": "रिपोर्ट बनाएं",
        "submit_report": "एसएआई को रिपोर्ट जमा करें",
        "tips": "💡 बेहतर प्रदर्शन के सुझाव",
        "warning_tip": "⚠️ पूरा शरीर कैमरे में दिखे और रोशनी पर्याप्त हो।",
        "jump_tip": "जंप करते समय घुटनों को सीधा रखें ताकि सही डिटेक्शन हो।",
        "pullup_tip": "प्रत्येक पुल-अप पर अपनी ठोड़ी को बार से ऊपर ले जाएं।",
        "pushup_tip": "अपनी पीठ सीधी रखें और अपने आप को तब तक नीचे करें जब तक कि आपकी कोहनी 90 डिग्री के कोण पर न हो जाए।",
        "situp_tip": "अपनी छाती को घुटनों तक लाएं और फिर अपनी पीठ को पूरी तरह से ज़मीन पर सपाट होने तक वापस जाएं।",
        "navigation": "नेविगेशन",
        "name": "नाम",
        "age": "आयु",
        "gender": "लिंग",
        "test_mode": "टेस्ट मोड",
        "test_type": "टेस्ट प्रकार",
        "male": "पुरुष",
        "female": "महिला",
        "other": "अन्य",
        "video_upload_option": "वीडियो अपलोड करें",
        "real_time_option": "रीयल-टाइम कैमरा",
        "warning_person_not_detected": "⚠️ व्यक्ति नहीं दिख रहा!",
        "score": "स्कोर",
        "warnings": "चेतावनी",
        "badge": "बैज",
        "segments": "सेगमेंट",
        "segment_label": "सेगमेंट",
        "submit_report_success": "✅ रिपोर्ट जमा किया गया!",
        "report_deleted": "✅ रिपोर्ट हटा दी गई!",
        "video_not_available": "वीडियो उपलब्ध नहीं है।",
        "please_provide_name_video": "कृपया अपना नाम दें और वीडियो अपलोड करें।",
        "please_provide_name_generate_report": "रिपोर्ट बनाने के लिए कृपया अपना नाम दर्ज करें।",
        "saving_processing_video": "वीडियो सहेजा और संसाधित किया जा रहा है...",
        "analyzing_video": "वीडियो विश्लेषण किया जा रहा है...",
        "report_generated": "✅ रिपोर्ट बनाई गई!",
        "real_time_report_generated": "✅ रीयल-टाइम रिपोर्ट बनाई गई!",
        "saimember_dashboard": "📝 एसएआई सदस्य डैशबोर्ड",
        "no_submissions": "कोई एथलीट सबमिशन नहीं हैं।",
        "delete_report_button": "इस रिपोर्ट को हटाएं",
        "ensure_visible_camera": "कैमरे के फ्रेम में पूरा शरीर दिखना सुनिश्चित करें!",
        "jumps_title": "जंप्स",
        "situps_title": "सिट-अप्स",
        "pushups_title": "पुश-अप्स",
        "pullups_title": "पुल-अप्स",
        "no_video_data": "रीयल-टाइम मोड के लिए वीडियो डेटा उपलब्ध नहीं है।",
        "login_page": "👤 लॉग इन / पंजीकरण",
        "my_dashboard": "मेरा डैशबोर्ड",
        "username": "यूजरनेम",
        "password": "पासवर्ड",
        "login": "लॉग इन",
        "register": "पंजीकरण",
        "logout": "लॉग आउट",
        "login_success": "✅ लॉग इन सफल रहा!",
        "registration_success": "✅ पंजीकरण सफल रहा! अब आप लॉग इन कर सकते हैं।",
        "invalid_credentials": "❌ अमान्य उपयोगकर्ता नाम या पासवर्ड।",
        "user_exists": "❌ उपयोगकर्ता नाम पहले से मौजूद है। कृपया कोई दूसरा चुनें।",
        "user_dashboard_title": "मेरा प्रदर्शन डैशबोर्ड",
        "your_score": "आपका स्कोर",
        "your_badge": "आपका बैज",
        "welcome": "स्वागत है",
        "email_address": "ईमेल पता",
        "forgot_password": "पासवर्ड भूल गए?",
        "not_a_member": "सदस्य नहीं हैं?",
        "signup_now": "अभी साइन अप करें",
        "your_performance_summary": "आपका प्रदर्शन सारांश",
        "all_your_reports": "आपकी सभी रिपोर्ट",
        "athlete_info": "एथलीट जानकारी",
        "test_configuration": "परीक्षण विन्यास",
        "no_scores_to_show": "दिखाने के लिए कोई स्कोर नहीं है।",
        "too_many_warnings": "⚠️ बहुत सारी चेतावनियाँ मिलीं। कृपया अपनी स्थिति और प्रकाश व्यवस्था को ठीक करें।",
        "try_to_improve_score": "💡 बेहतर परिणामों के लिए अपना स्कोर बढ़ाने का प्रयास करें!",
        "please_upload_video": "कृपया एक वीडियो फ़ाइल अपलोड करें।",
        "current_realtime_score": "वर्तमान रियल-टाइम स्कोर",
        "real_time_warnings": "चेतावनी",
        "performance_report": "प्रदर्शन रिपोर्ट",
        "video_player_title": "वीडियो प्लेयर",
        "video_playback": "वीडियो प्लेबैक",
        "timeline": "टाइमलाइन",
        "submission_status": "जमा करने की स्थिति",
        "submit_report_to_sai": "एसएआई को रिपोर्ट जमा करें",
        "sai_member_dashboard": "📝 एसएआई सदस्य डैशबोर्ड",
        "review_pending": "समीक्षा लंबित है",
        "approved_by_sai": "एसएआई द्वारा स्वीकृत",
        "report_detail": "रिपोर्ट विवरण",
        "athlete_name": "एथलीट का नाम",
        "sai_status": "एसएआई स्थिति",
        "delete_report": "इस रिपोर्ट को हटाएं",
        "select_role": "अपनी भूमिका चुनें",
        "athlete_role": "एथलीट",
        "sai_member_role": "एसएआई सदस्य",
        "role_mismatch": "❌ भूमिका उपयोगकर्ता नाम से मेल नहीं खाती।"
    }
}

# Mapping of display text to canonical role ID
ROLE_MAP_ENG_HINDI = {
    "Athlete": "athlete",
    "SAI Member": "sai_member",
    "एथलीट": "athlete",
    "एसएआई सदस्य": "sai_member",
}

# Get the language selection at the top of the script
with st.sidebar:
    selected_lang = st.selectbox("🌐 Select Language / भाषा चुनें", list(LANGUAGES.keys()))

T = LANGUAGES[selected_lang]

# ------------------ Session State ------------------
if 'athlete_data' not in st.session_state:
    st.session_state.athlete_data = pd.DataFrame(
        columns=['Name', 'Age', 'Gender', 'Test', 'Score', 'Warning Count', 'Video Path', 'SAI Status', 'Badge', 'Username']
    )
if 'temp_video_path' not in st.session_state:
    st.session_state.temp_video_path = None
if 'processed_report' not in st.session_state:
    st.session_state.processed_report = None
if 'live_score' not in st.session_state:
    st.session_state.live_score = 0
if 'live_warning_count' not in st.session_state:
    st.session_state.live_warning_count = 0
if 'person_detected' not in st.session_state:
    st.session_state.person_detected = False
if 'leaderboard' not in st.session_state:
    st.session_state.leaderboard = []
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'role' not in st.session_state:
    st.session_state.role = ""
if 'users' not in st.session_state:
    # Use canonical role IDs in the fake user database
    st.session_state.users = {
        "sai_admin": {"password": "admin123", "role": CANONICAL_ROLES["sai_member"]},
        "athlete_1": {"password": "pass1", "role": CANONICAL_ROLES["athlete"]}
    }
    
# Initialize selected_test if it doesn't exist
if 'selected_test' not in st.session_state:
    st.session_state.selected_test = CANONICAL_TESTS["jumps"]

# ------------------ Badge System ------------------
def assign_badge(score, benchmark):
    if score >= benchmark:
        return "🏅 Gold"
    elif score >= benchmark * 0.75:
        return "🥈 Silver"
    elif score >= benchmark * 0.5:
        return "🥉 Bronze"
    else:
        return "Participant"

def calculate_angle(a, b, c):
    a = np.array(a)  # First point
    b = np.array(b)  # Middle point
    c = np.array(c)  # End point
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

# ------------------ AI/ML Real-Time Processor ------------------
class ExerciseProcessor(VideoProcessorBase):
    def __init__(self, exercise_type):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.exercise_type = exercise_type
        self.score_counter = 0
        self.stage = "down"
        self.warning_counter = 0
        self.last_warning_time = datetime.now()

    def process_jumps(self, landmarks):
        hip_y = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y
        if hip_y < 0.4 and self.stage == "down":
            self.stage = "up"
        if hip_y >= 0.5 and self.stage == "up":
            self.stage = "down"
            self.score_counter += 1
    
    def process_pushups(self, landmarks):
        shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]

        angle = calculate_angle(shoulder, elbow, wrist)

        if angle > 160:
            self.stage = "up"
        if angle < 90 and self.stage == "up":
            self.stage = "down"
            self.score_counter += 1
            
    def process_situps(self, landmarks):
        shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value].y]
        knee = [landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value].y]

        angle = calculate_angle(shoulder, hip, knee)
        
        if angle > 160:
            self.stage = "down"
        if angle < 80 and self.stage == "down":
            self.stage = "up"
            self.score_counter += 1
            
    def process_pullups(self, landmarks):
        left_shoulder_y = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
        left_ear_y = landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].y

        if left_shoulder_y < left_ear_y:
            if self.stage == "down":
                self.stage = "up"
                self.score_counter += 1
        elif left_shoulder_y > left_ear_y:
            self.stage = "down"

    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")
        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)

        if results.pose_landmarks:
            st.session_state.person_detected = True
            landmarks = results.pose_landmarks.landmark

            # Use canonical test names for logic
            if self.exercise_type == CANONICAL_TESTS["jumps"]:
                self.process_jumps(landmarks)
            elif self.exercise_type == CANONICAL_TESTS["situps"]:
                self.process_situps(landmarks)
            elif self.exercise_type == CANONICAL_TESTS["pushups"]:
                self.process_pushups(landmarks)
            elif self.exercise_type == CANONICAL_TESTS["pullups"]:
                self.process_pullups(landmarks)

            mp.solutions.drawing_utils.draw_landmarks(
                image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
            )
        else:
            st.session_state.person_detected = False
            if (datetime.now() - self.last_warning_time).seconds >= 1:
                self.warning_counter += 1
                self.last_warning_time = datetime.now()
            cv2.putText(image, T["warning_person_not_detected"], (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        st.session_state.live_score = self.score_counter
        st.session_state.live_warning_count = self.warning_counter

        cv2.putText(image, f'{T["score"]}: {self.score_counter}', (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(image, f'{T["warnings"]}: {self.warning_counter}', (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        return av.VideoFrame.from_ndarray(image, format="bgr24")

# ------------------ Video Upload Processing ------------------
def process_video_for_exercise(video_path, exercise_type):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error(f"{T['video_not_available']}: {video_path}")
        return 0, 0, []

    score_counter = 0
    warning_counter = 0
    stage = "down"
    segments = []
    segment_start_frame = None

    with mp.solutions.pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        frame_idx = 0
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                # Logic for each exercise type
                if exercise_type == CANONICAL_TESTS["jumps"]:
                    hip_y = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value].y
                    if hip_y < 0.4 and stage == "down":
                        stage = "up"
                        segment_start_frame = frame_idx
                    if hip_y >= 0.5 and stage == "up":
                        stage = "down"
                        score_counter += 1
                        if segment_start_frame:
                            segments.append((segment_start_frame / fps, frame_idx / fps))
                            segment_start_frame = None

                elif exercise_type == CANONICAL_TESTS["pushups"]:
                    shoulder = [landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    elbow = [landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value].y]
                    wrist = [landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value].y]
                    angle = calculate_angle(shoulder, elbow, wrist)
                    if angle > 160:
                        stage = "up"
                    if angle < 90 and stage == "up":
                        stage = "down"
                        score_counter += 1

                elif exercise_type == CANONICAL_TESTS["situps"]:
                    shoulder = [landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    hip = [landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value].y]
                    knee = [landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value].y]
                    angle = calculate_angle(shoulder, hip, knee)
                    if angle > 160:
                        stage = "down"
                    if angle < 80 and stage == "down":
                        stage = "up"
                        score_counter += 1

                elif exercise_type == CANONICAL_TESTS["pullups"]:
                    left_shoulder_y = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].y
                    left_ear_y = landmarks[mp.solutions.pose.PoseLandmark.LEFT_EAR.value].y
                    if left_shoulder_y < left_ear_y:
                        if stage == "down":
                            stage = "up"
                            score_counter += 1
                    elif left_shoulder_y > left_ear_y:
                        stage = "down"

            frame_idx += 1

    cap.release()
    return score_counter, warning_counter, segments

# ------------------ Login/Registration Logic ------------------
def login_page():
    st.markdown("<h2 style='text-align: center;'>Login Form</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs([T["login"], T["register"]])
        
        with tab1:
            login_username = st.text_input(f"**{T['username']}**", key="login_username")
            login_password = st.text_input(f"**{T['password']}**", type="password", key="login_password")
            # Map display text to canonical role ID
            login_role_display = st.selectbox(f"**{T['select_role']}**", [T['athlete_role'], T['sai_member_role']], key="login_role_select")
            login_role = ROLE_MAP_ENG_HINDI[login_role_display]
            
            st.markdown(f"<p style='text-align: right; font-size: 0.9em; color: #3498db;'>{T['forgot_password']}</p>", unsafe_allow_html=True)
            
            if st.button(T["login"], use_container_width=True):
                if login_username in st.session_state.users:
                    user_data = st.session_state.users[login_username]
                    if user_data["password"] == login_password and user_data["role"] == login_role:
                        st.session_state.logged_in = True
                        st.session_state.username = login_username
                        st.session_state.role = login_role
                        st.success(T["login_success"])
                        st.rerun()
                    else:
                        st.error(T["invalid_credentials"])
                else:
                    st.error(T["invalid_credentials"])

        with tab2:
            register_username = st.text_input(f"**{T['username']}**", key="register_username")
            register_password = st.text_input(f"**{T['password']}**", type="password", key="register_password")
            # Map display text to canonical role ID
            register_role_display = st.selectbox(f"**{T['select_role']}**", [T['athlete_role'], T['sai_member_role']], key="register_role_select")
            register_role = ROLE_MAP_ENG_HINDI[register_role_display]
            
            if st.button(T["register"], use_container_width=True):
                if register_username in st.session_state.users:
                    st.error(T["user_exists"])
                else:
                    st.session_state.users[register_username] = {"password": register_password, "role": register_role}
                    st.success(T["registration_success"])

        st.markdown('</div>', unsafe_allow_html=True)

# ------------------ Main UI ------------------
if not st.session_state.logged_in:
    login_page()
else:
    st.title(T["dashboard"])
    st.markdown(f"### {T['welcome']}, {st.session_state.username.capitalize()}!")
    
    with st.sidebar:
        st.button(f"🚪 {T['logout']}", on_click=lambda: st.session_state.update(logged_in=False, username=""))
    
    # Dynamic navigation based on canonical role
    if st.session_state.role == CANONICAL_ROLES["sai_member"]:
        menu = [T["saimember_dashboard"]]
    else: # Athlete
        menu = [T["my_dashboard"], T["athlete_submission"]]
    
    choice = st.sidebar.selectbox(T["navigation"], menu)

    def get_processor():
        selected_test = st.session_state.selected_test if 'selected_test' in st.session_state else CANONICAL_TESTS["jumps"]
        return ExerciseProcessor(selected_test)

    if choice == T["my_dashboard"]:
        st.header(T["user_dashboard_title"])
        
        my_data = st.session_state.athlete_data[st.session_state.athlete_data['Username'] == st.session_state.username]
        
        if my_data.empty:
            st.info(T["no_submissions"])
        else:
            st.subheader(T["your_performance_summary"])
            
            latest_report = my_data.iloc[-1]
            
            col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
            with col_metrics1:
                st.metric(T["your_score"], latest_report['Score'])
            with col_metrics2:
                st.metric(T["your_badge"], latest_report['Badge'])
            with col_metrics3:
                st.metric(T["warnings"], latest_report['Warning Count'])
            
            st.markdown("---")
            st.subheader(T["all_your_reports"])
            st.dataframe(my_data[['Test', 'Score', 'Warning Count', 'Badge', 'SAI Status']])
            
    elif choice == T["athlete_submission"]:
        st.header(T["athlete_submission"])
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            with st.container():
                st.subheader(T["athlete_info"])
                name = st.text_input(f"**{T['name']}**", value=st.session_state.username.capitalize(), disabled=True)
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    age = st.number_input(f"**{T['age']}**", 5, 99)
                with col_info2:
                    gender = st.selectbox(f"**{T['gender']}**", [T["male"], T["female"], T["other"]])
                
                st.markdown("---")
                st.subheader(T["test_configuration"])
                test_mode = st.radio(f"**{T['test_mode']}**", [T["video_upload_option"], T["real_time_option"]])
                
                # Use canonical tests for internal logic, and display translated names
                test_options = {
                    T["jumps_title"]: CANONICAL_TESTS["jumps"],
                    T["situps_title"]: CANONICAL_TESTS["situps"],
                    T["pushups_title"]: CANONICAL_TESTS["pushups"],
                    T["pullups_title"]: CANONICAL_TESTS["pullups"]
                }
                
                selected_test_display = st.selectbox(
                    f"**{T['test_type']}**", 
                    list(test_options.keys())
                )
                st.session_state.selected_test = test_options[selected_test_display]
            
        with col2:
            with st.container():
                st.header(T["leaderboard"])
                leaderboard_df = pd.DataFrame(st.session_state.leaderboard, columns=['Name', 'Test', 'Score'])
                leaderboard_df = leaderboard_df.sort_values('Score', ascending=False)
                
                if not leaderboard_df.empty:
                    chart = alt.Chart(leaderboard_df.head(5)).mark_bar(
                        cornerRadiusTopLeft=3,
                        cornerRadiusTopRight=3
                    ).encode(
                        x=alt.X('Score', title='Score'),
                        y=alt.Y('Name', sort='-x', title=''),
                        color=alt.Color('Name', legend=None),
                        tooltip=['Name', 'Test', 'Score']
                    ).properties(
                        height=250,
                        title="Top 5 Scores"
                    ).interactive()
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info(T["no_scores_to_show"])
            
            st.markdown("---")
            with st.expander(T["tips"]):
                st.info(f"💡 {T['warning_tip']}")
                if st.session_state.selected_test == CANONICAL_TESTS["jumps"]:
                    st.info(f"💡 {T['jump_tip']}")
                elif st.session_state.selected_test == CANONICAL_TESTS["situps"]:
                    st.info(f"💡 {T['situp_tip']}")
                elif st.session_state.selected_test == CANONICAL_TESTS["pushups"]:
                    st.info(f"💡 {T['pushup_tip']}")
                elif st.session_state.selected_test == CANONICAL_TESTS["pullups"]:
                    st.info(f"💡 {T['pullup_tip']}")
            
                if st.session_state.live_warning_count > 3:
                    st.warning(T["too_many_warnings"])
                if 0 < st.session_state.live_score < 5:
                    st.info(T["try_to_improve_score"])

        if test_mode == T["video_upload_option"]:
            video_file = st.file_uploader(T["video_upload_option"], type=['mp4', 'mov'])
            if st.button(f"🚀 {T['generate_report']}", use_container_width=True):
                if video_file:
                    st.info(T["saving_processing_video"])
                    temp_file_path = os.path.join(tempfile.gettempdir(), video_file.name)
                    with open(temp_file_path, "wb") as f:
                        f.write(video_file.read())
                    st.session_state.temp_video_path = temp_file_path

                    with st.spinner(T["analyzing_video"]):
                        score, warnings, segments = process_video_for_exercise(st.session_state.temp_video_path, st.session_state.selected_test)
                        benchmark = 10 + age * 0.2
                        badge = assign_badge(score, benchmark)
                    st.session_state.processed_report = {
                        'Name': st.session_state.username.capitalize(), 'Age': age, 'Gender': gender, 'Test': f"{selected_test_display} ({T['video_upload_option']})",
                        'Score': score, 'Warning Count': warnings, 'Video Path': st.session_state.temp_video_path,
                        'SAI Status': T['review_pending'], 'Badge': badge, 'Benchmark': benchmark,
                        'Segments': segments, 'Username': st.session_state.username
                    }
                    st.success(T["report_generated"])
                else:
                    st.warning(T["please_upload_video"])

        elif test_mode == T["real_time_option"]:
            st.warning(T["ensure_visible_camera"])
            RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
            
            webrtc_streamer(
                key="realtime",
                mode=WebRtcMode.SENDRECV,
                rtc_configuration=RTC_CONFIG,
                video_processor_factory=get_processor
            )

            col_rt1, col_rt2 = st.columns(2)
            with col_rt1:
                st.metric(T["current_realtime_score"], st.session_state.live_score)
            with col_rt2:
                st.metric(T["real_time_warnings"], st.session_state.live_warning_count)
            
            if st.button(f"📊 {T['generate_report']}", use_container_width=True):
                benchmark = 10 + age * 0.2
                badge = assign_badge(st.session_state.live_score, benchmark)
                st.session_state.processed_report = {
                    'Name': st.session_state.username.capitalize(), 'Age': age, 'Gender': gender, 'Test': f"{selected_test_display} ({T['real_time_option']})",
                    'Score': st.session_state.live_score, 'Warning Count': st.session_state.live_warning_count,
                    'Video Path': 'N/A', 'SAI Status': T['review_pending'], 'Badge': badge, 'Benchmark': benchmark, 'Username': st.session_state.username
                }
                st.success(T["real_time_report_generated"])

        if st.session_state.processed_report and st.session_state.processed_report['Username'] == st.session_state.username:
            report = st.session_state.processed_report
            st.markdown("---")
            st.subheader(T["performance_report"])
            col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
            with col_metrics1:
                st.metric(T["score"], report['Score'], delta=f"{report['Score'] - report['Benchmark']} vs Benchmark", delta_color="normal")
            with col_metrics2:
                st.metric(T["warnings"], report['Warning Count'])
            with col_metrics3:
                st.metric(T["badge"], report['Badge'])

            if report.get('Segments') and test_mode == T["video_upload_option"]:
                st.subheader(T["video_player_title"])
                st.video(report['Video Path'])
                st.caption(f"**{T['video_playback']}**: {T['timeline']}")
                
                segment_df = pd.DataFrame(
                    [
                        {"start": start, "end": end, "label": f"{T['segment_label']} {i+1}"}
                        for i, (start, end) in enumerate(report['Segments'])
                    ]
                )
                
                segment_chart = alt.Chart(segment_df).mark_bar(
                    height=20,
                    size=10
                ).encode(
                    x=alt.X('start', title='Time (s)'),
                    x2='end',
                    color=alt.value('#3498db'),
                    tooltip=['start', 'end', 'label']
                ).properties(
                    title=f"{T['segments']} ({selected_test_display})",
                    height=50
                )
                
                st.altair_chart(segment_chart, use_container_width=True)

            st.markdown("---")
            st.subheader(T["submission_status"])
            
            if st.button(f"📥 {T['submit_report_to_sai']}", use_container_width=True):
                st.session_state.athlete_data = pd.concat([
                    st.session_state.athlete_data,
                    pd.DataFrame([report])
                ], ignore_index=True)
                st.session_state.leaderboard = [
                    {'Name': r['Name'], 'Test': r['Test'], 'Score': r['Score']} 
                    for _, r in st.session_state.athlete_data.iterrows()
                ]
                st.success(T["submit_report_success"])
                st.session_state.processed_report = None
    
    elif choice == T["saimember_dashboard"]:
        st.header(T["saimember_dashboard"])
        if st.session_state.athlete_data.empty:
            st.info(T["no_submissions"])
        else:
            for index, row in st.session_state.athlete_data.iterrows():
                with st.container():
                    col_sai1, col_sai2, col_sai3 = st.columns([1, 1, 3])
                    with col_sai1:
                        st.subheader(f"#{index + 1}")
                    with col_sai2:
                        st.metric(T["athlete_name"], row['Name'])
                    with col_sai3:
                        st.metric(T["test_type"], row['Test'])
                        st.metric(T["sai_status"], row['SAI Status'])

                    with st.expander(T["report_detail"]):
                        st.dataframe(pd.DataFrame(row).T)
                        if row['Video Path'] != 'N/A':
                            st.video(row['Video Path'])
                        
                        col_actions1, col_actions2 = st.columns(2)
                        with col_actions1:
                            if st.button(T['approved_by_sai'], key=f"approve_{index}"):
                                st.session_state.athlete_data.at[index, 'SAI Status'] = 'Approved by SAI'
                                st.success(f"{row['Name']}'s report has been approved.")
                                st.rerun()
                        with col_actions2:
                            if st.button(T['delete_report_button'], key=f"delete_{index}"):
                                st.session_state.athlete_data = st.session_state.athlete_data.drop(index).reset_index(drop=True)
                                st.session_state.leaderboard = [
                                    {'Name': r['Name'], 'Test': r['Test'], 'Score': r['Score']} 
                                    for _, r in st.session_state.athlete_data.iterrows()
                                ]
                                st.success(T["report_deleted"])
                                st.rerun()
