import streamlit as st
import requests
import main 

st.header("BOOKINGS WEBCRAWLER")
st.subheader("About")
st.write("""
    A webcrawler that searches for available hotels from bookings.com and returns it
""")

st.subheader("Search for hotels")
location = st.text_input("Enter the location you want to search for hotels in:")
check_in = st.date_input("Check-in date")
check_out = st.date_input("Check-out date")

if st.button("Search"):
    if location and check_in and check_out:
        with st.spinner("Searching for hotels..."):
            try:
                payload = {
                    "location": location,
                    "checkin_date": check_in.strftime('%Y-%m-%d'),
                    "checkout_date": check_out.strftime('%Y-%m-%d')
                }
                response = requests.post("http://localhost:8080/search_hotels", json=payload)
                if response.status_code == 200:
                    hotels = response.json()
                    st.success("Hotels found!")
                    for i, name in enumerate(hotels["hotel_name"]):
                        st.write(f"Hotel Name: {name}")
                        st.write(f"Price: {hotels['hotel_price'][i]}")
                        st.write(f"Rating: {hotels['hotel_rating'][i]}")
                        st.write(f"Review Count: {hotels['hotel_review'][i]}")
                        st.write(f"Facilities: {hotels['hotel_facilities'][i]}")
                else:
                    st.warning("No hotels found.")
            except Exception as e:
                st.error(f"An error occurred: {e}")