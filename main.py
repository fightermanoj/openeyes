import streamlit as st 
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from streamlit_js_eval import streamlit_js_eval, copy_to_clipboard, create_share_link, get_geolocation
from streamlit_folium import st_folium
import io 
import os
import json
import folium
import pandas as pd


loc = False
done = False
re_run = False

def canvas_to_image(canvas_result):
    canvas_data = canvas_result.image_data.astype("uint8")
    return Image.fromarray(canvas_data, "RGBA")

@st.experimental_dialog("Please Provide Context")
def user_input():
    st.image(combined_image)
    st.write(f"What is the Illegal Factor of the Image")
    context = st.text_input("Because...")
    if st.button("Submit"):
        st.session_state.user_input = context
        re_run = True
        # Close the pop-up dialog by rerunning the script
        st.experimental_rerun()
    return(context)


st.write('# Open Eyes ')
st.write(' An Ai Based Solution for solving **Visiual Pollution**')
st.divider()
captured = st.camera_input("### locate the Illegal Hoarding")

st.divider()

if captured:
    st.write("## Please Mask the Illegal Hoarding")
    stroke_width = st.slider("Stroke width: ", 1, 10, 2)
    drawing_mode = st.selectbox(
    "Drawing tool:",
    ("rect", "line", "freedraw", "circle", "transform", "polygon", "point"),
    )

    # Create a canvas component
    canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.15)",  # Fixed fill color with some opacity
    stroke_width= stroke_width,
    stroke_color= "#FF0000",
    background_color= "#EEEEEE",
    background_image=Image.open(captured),
    update_streamlit=True,
    height=400,
    drawing_mode=drawing_mode,
    key="canvas",
    )

    if canvas_result.json_data is not None:        
        objects = pd.json_normalize(canvas_result.json_data["objects"]) # need to convert obj to str because PyArrow
        for col in objects.select_dtypes(include=['object']).columns:
            objects[col] = objects[col].astype("str")
        st.dataframe(objects)
    
    overlay_image = canvas_to_image(canvas_result)



    if st.button("Done" , type="primary"):
        if canvas_result.json_data:
            # Open the captured image
            captured_image = Image.open(captured).convert("RGBA")
            overlay_image = overlay_image.resize(captured_image.size)
            combined_image = Image.alpha_composite(captured_image, overlay_image)
            # st.image(combined_image)
            user_input()
        
    
    if st.session_state.user_input:
        st.divider()
        st.write("### User Context")
        st.write(f"```\n{st.session_state.user_input}   ")

    st.divider()
    st.write("### Share Your Current Location")

    if st.toggle("Get Location"):
        loc = get_geolocation()
        
        # Check if loc is not None
        if loc:
            # Extracting latitude and longitude
            latitude = loc['coords']['latitude']
            longitude = loc['coords']['longitude']
            
            # Displaying the coordinates
            st.write(f"Your coordinates are (Latitude: {latitude}, Longitude: {longitude})")
            # center on Liberty Bell, add marker
            m = folium.Map(location=[latitude, longitude], zoom_start=16)
            folium.Marker([latitude, longitude], popup="Liberty Bell", tooltip="Liberty Bell").add_to(m)
            # call to render Folium map in Streamlit
            st_data = st_folium(m, width=725)

        else:
            st.write("Could not retrieve location data.")
    



# git config --global user.email "you@example.com"
#git config --global user.name "Your Name"
