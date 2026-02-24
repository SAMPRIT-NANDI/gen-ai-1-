# ...existing code...
import streamlit as st

st.title("Form Example")

# camera disabled — do not import or call camera_input_live
st.info("Camera import disabled. To enable, restore camera_input_live import and its button.")

st.chat_message("me", avatar="🦖").write("HI, this is me")
st.chat_message("you", avatar="👩‍🦰").write("HI, this is you")

user_text = st.chat_input(placeholder="Type your message here...", key="formInput")
if user_text:
    st.write("You typed:", user_text)

st.balloons()
#