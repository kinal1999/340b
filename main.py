import streamlit as st
import os
from openai import OpenAI
from handle_TOS_violations import TOS_violations_in_text, handle_TOS_violations
from utils import convert_image_to_base64, convert_base64_to_image, upload_image, upload_images, convert_images_to_base64_payload
import time
import base64


MAX_COMPLETION_TOKENS = 4096

# Set to False to disable vision features; I'm leaving this option as the vision model is still in beta
# and struggles to give even general advice for many medical images.
GPT_VISION_FEATURES_ENABLED = False

st.set_page_config(page_title="Health Universe Agent", layout="centered", initial_sidebar_state="auto",)

with open( "style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

st.title("340B Program AI Assistant")
st.sidebar.write("Hello! I am an AI assistant knowledgeable about the 340B program.")
st.sidebar.write("For accurate and up-to-date information, my responses are based on the HRSA website.")
st.sidebar.write("This information is not a substitute for professional advice. Consult relevant authorities for legal or compliance matters.")
st.sidebar.write("By Health Universe 2024.")

if GPT_VISION_FEATURES_ENABLED:
    images = upload_images()
    base64_payloads = convert_images_to_base64_payload(images)
else:
    images = None
    base64_payloads = None

api_key = os.environ.get('OPENAI-KEY')

# Instantiate OpenAI client with the API key
client = OpenAI(api_key=api_key)

CONTENT = open('resources/system_prompt.txt', 'r').read()


def get_response():
    message_placeholder = st.empty()
    full_response = ""
    messages = [{"role": "system", "content": CONTENT}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    
    for chunk in client.chat.completions.create(model=st.session_state["openai_model"],
    messages= messages,
    stream=True, max_tokens=MAX_COMPLETION_TOKENS):
        if chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    return full_response

def initialize_session_state():
    if "openai_model" not in st.session_state:
        if GPT_VISION_FEATURES_ENABLED:
            st.session_state["openai_model"] = "gpt-4-vision-preview"
        else:
            st.session_state["openai_model"] = "gpt-4-1106-preview"
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content":"Hi! How can I help you today?"}]
    if "chatbot_violations_count" not in st.session_state:
        st.session_state.chatbot_violations_count = 0
    if "user_violations_count" not in st.session_state:
        st.session_state.user_violations_count = 0
def prevent_app_compromise_beta():
    if st.session_state.chatbot_violations_count >= 3:
        st.error("App produced harmful content. Please contact Health Universe to report this issue as this could mean that the app or underlying model was compromised.")
        st.stop()
    elif st.session_state.user_violations_count >= 6:
        st.error("You blatantly or repeatedly violated our content policy. It's critical to use this app responsibly. If you feel that this is a mistake, please contact Health Universe to report this issue.")
        st.stop()
def main():
    initialize_session_state()
    prevent_app_compromise_beta()
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            try:
                st.markdown(message["content"][0]["text"])
                for i in range(1, len(message["content"])):
                    if message["content"][i]["type"] == "text":
                        st.markdown(message["content"][i]["text"])
                    elif message["content"][i]["type"] == "image_url":
                        original_base64_encoded_string = message["content"][i]["image_url"]["url"].split("base64,", 1)[1]
                        img = convert_base64_to_image(original_base64_encoded_string)
                        st.image(img, use_column_width=True)
                st.image(img, use_column_width=True)
            except:
                st.markdown(message["content"])
            

    # chatting part
    if prompt := st.chat_input("How can I help you?"):
        # user input
        with st.chat_message("user"):
            st.markdown(prompt)
            if images:
                for image in images:
                    st.image(image, use_column_width=True)
            # time_initial = time.time()
            violations = TOS_violations_in_text(prompt, client)
            if "serious_violation" in violations:
                st.session_state.user_violations_count += 3
            elif "violation" in violations:
                st.session_state.user_violations_count += 1
            # time_intermediate = time.time()
            handle_TOS_violations(violations)
            # time_end = time.time()
            # print("Time elapsed: ", time_end - time_initial, time_end - time_intermediate, time_intermediate - time_initial)
            if images:
                content = [{"type": "text", "text": prompt}]
                for payload in base64_payloads:
                    content.append({"type": "image_url", "image_url": {"url": payload}})
                st.session_state.messages.append(
                    {"role": "user",
                     "content": content
                    }
                )
            else:
                st.session_state.messages.append({"role": "user", "content": prompt})
        # response
        with st.chat_message("assistant"):
            full_response = get_response()
            violations = TOS_violations_in_text(full_response, client)
            if "serious_violation" in violations or "critical_self_harm" in violations:
                st.session_state.chatbot_violations_count += 10
                st.error("App produced harmful content. Please contact Health Universe to report this issue as this could mean that the app or underlying model was compromised.")
                st.session_state.messages.pop()
                st.stop()
            elif "violation" in violations or "self_harm" in violations:
                st.session_state.chatbot_violations_count += 1
                st.error("The outputted message seems to violate our content policy. If this happens repeatedly, this could mean that the app is compromised; please contact Health Universe to report this issue.")
                st.session_state.messages.pop()
                st.stop()
            else:
                st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
