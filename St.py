import streamlit as st
st.title("Hello Streamlit")
st.write("Hello world")

name = st. text_input (" Введiть ваше iм ’я:")
if st. button (" Привiтати "):
   st. success (f"Привiт , { name }!")
