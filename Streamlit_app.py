import streamlit as st
from ultralytics import YOLO
from PIL import Image
from ultralytics.utils.plotting import Annotator, colors
import glob
import dotenv 
import os 
from database_center import db_transaction
from cloudhands import CloudHandsPayment
import uuid
dotenv.load_dotenv()

payment_key=os.environ['Payment_Key']
# Load the model once
model = YOLO("Dental_model.pt")
names = model.model.names
def complete_payment():
    if st.session_state.token :
        chPay=st.session_state.chPay
        try:
            result = chPay.charge(
                charge=0.5,
                event_name="Sample cloudhands charge",
            )
            st.success(f"You payment is succeeded")
            
            db_transaction.add({
            'id':str(uuid.uuid4()),
            'app':'app_title',
            'transaction-id':result.transaction_id,
            'price':0.5

            })
            st.session_state.transaction_id=result.transaction_id
        except Exception as e:
            st.error(f"Charge failed: {e}")
    else:
        st.error('Please generate your Tokens.')


@st.dialog("Payment link")
def pay():
    chPay = st.session_state.chPay

    # Step 1: Show auth link only once
    auth_url = chPay.get_authorization_url()
    st.link_button("Authenticate", url=auth_url)

    # Step 2: User pastes the code
    code = st.text_input("Place your code")

    if st.button("Exchange Code"):
        try:
            token = chPay.exchange_code_for_token(code)
            st.session_state.token = token
            st.success("Code exchanged successfully! Token stored.")
        except Exception as e:
            st.error(f"Failed: {e}")


if "chPay" not in st.session_state:
    st.session_state.chPay = CloudHandsPayment(
        author_key=payment_key
    )

if "token" not in st.session_state:
    st.session_state.token = None
if 'transaction_id' not in st.session_state:
    st.session_state.transaction_id = None
# Function to perform object detection
def detect_objects(image):
    image1 = image.copy()
    results = model.predict(image)
    classes = results[0].boxes.cls.cpu().tolist()
    boxes = results[0].boxes.xyxy.cpu()

    annotator = Annotator(image, line_width=3)
    annotator1 = Annotator(image1, line_width=3)

    for box, cls in zip(boxes, classes):
        annotator.box_label(box, label=names[int(cls)], color=colors(int(cls)))
        annotator1.box_label(box, label=None, color=colors(int(cls)))

    return Image.fromarray(annotator.result()), Image.fromarray(annotator1.result())

# Sidebar for upload
st.sidebar.title("Dental Image Uploader")
st.sidebar.write("Upload a dental image (JPG or PNG) to analyze it with AI.")
authorize = st.sidebar.button("Authorize Payment")
if authorize:
    pay()
uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Main area
st.title("🦷 Dental Image Analyzer")
st.markdown("This AI-powered app analyzes your dental images and highlights regions of interest using a trained YOLO model.")
pay_button = st.button("0.3 / Generation", type='secondary')
if uploaded_file is not None and pay_button:
    complete_payment()
    if st.session_state.transaction_id not in [None, ""]:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        st.success("Image uploaded successfully. Running analysis...")

        result_with_labels, result_without_labels = detect_objects(image)

        st.subheader("🧪 Analysis Results")
        col1, col2 = st.columns(2)

        with col1:
            st.image(result_with_labels, caption="Detected (with labels)", use_column_width=True)

        with col2:
            st.image(result_without_labels, caption="Detected (no labels)", use_column_width=True)
else:
    st.info("Please upload an image to start the analysis. or Charge your credit.")
