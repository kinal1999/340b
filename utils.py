import base64
import streamlit as st
def convert_image_to_base64(uploaded_file):
    if uploaded_file is None:
        return None
    file_content = uploaded_file.getvalue()
    base64_encoded_string = base64.b64encode(file_content).decode()
    return base64_encoded_string

def convert_base64_to_image(base64_encoded_string):
    if base64_encoded_string is None:
        return None
    return base64.b64decode(base64_encoded_string)

def upload_image():
    uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        return uploaded_file
    return None

def upload_images():
    """
    Upload multiple images via Streamlit's file uploader.
    """
    help = "Add pictures here for the chatbot to look at when you ask a question or type a comment. Remember, when you press the 'Enter' key, the chatbot will see all the pictures you've put here. If there's a picture you don't want to send, just take it out before you ask your question."
    st.sidebar.markdown("## Upload image(s)", help=help)
    
    uploaded_files = st.sidebar.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if uploaded_files is not None:
        return uploaded_files
    else:
        return None
    
def convert_images_to_base64_payload(uploaded_files):
    """
    Convert a list of uploaded files (images) to a list of base64 payloads that can be sent via the OpenAI API.
    """
    if uploaded_files is None:
        return None
    else:
        base64_payloads = []
        for image in uploaded_files:
            base64_encoding = convert_image_to_base64(image)
            base64_payloads.append(f"data:{image.type};base64,{base64_encoding}")
        return base64_payloads