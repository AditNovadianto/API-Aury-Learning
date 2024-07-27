import io
import logging
# import os
import streamlit as st
# from dotenv import load_dotenv
from google.oauth2 import service_account
from google.cloud import speech
from absl import logging as absl_logging
from pymongo import MongoClient

def upload_file():
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
        st.write(file_details)
        return uploaded_file
    return None

def transcribe_audio(uploaded_file):
    # Inisialisasi log absl
    absl_logging.set_verbosity(absl_logging.INFO)
    absl_logging.info('Inisialisasi logging absl')

    client_file = "./aury-430010-163224f89ca3.json"  # Jalur lengkap ke file JSON
    credentials = service_account.Credentials.from_service_account_file(client_file)
    client = speech.SpeechClient(credentials=credentials)

    # Load the audio file
    with io.BytesIO(uploaded_file.read()) as f:
        content = f.read()
        audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  # Perbaikan akses atribut
        sample_rate_hertz=16000,  # Sesuaikan dengan nilai yang ada di header file WAV
        language_code=option
    )

    response = client.recognize(config=config, audio=audio)

    mongo_uri = st.secrets["MONGO_URI"]
    if not mongo_uri:
        raise ValueError("MONGO_URI environment variable not set")

    # MongoDB connection
    client = MongoClient(mongo_uri)  # Replace with your MongoDB URI
    db = client['aury']  # Replace with your database name
    collection = db['data-transcript']  # Replace with your collection name

    data = []

    # Print only the transcript
    for result in response.results:
        for alternative in result.alternatives:
            data.append({
                "speaker": lectureName,
                "text": alternative.transcript,
                "for_nim": nim,
            })
            
            print(f"Transcript: {alternative.transcript}")

    # Insert data into MongoDB
    if data:
        result = collection.insert_many(data)
        st.write("Data successfully inserted into MongoDB")
        st.write(f"Inserted IDs: {result.inserted_ids}")
    else:
        st.write("No data to insert into MongoDB")

st.title("Aury Learning")
uploaded_file = upload_file()
lectureName = st.text_input("Speaker", value="")
nim = st.text_input("nim", value="")
option = st.selectbox(
    "Choose the language that audio you make?",
    ("id-ID", "en_US"),
)
buttonUpload = st.button("Click me")

if buttonUpload:    
    if uploaded_file is not None:
        transcribe_audio(uploaded_file)