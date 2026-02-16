import gradio as gr
import random
import datetime
import csv
import os
import matplotlib.pyplot as plt
import pandas as pd
import speech_recognition as sr
from pydub import AudioSegment

# Theme
from gradio.themes.base import Base
from gradio.themes.utils import colors

custom_theme = Base(
    primary_hue=colors.indigo,
    secondary_hue=colors.fuchsia,
    neutral_hue=colors.gray,
    font=["Comic Sans MS", "sans-serif"]
)

# Mood classification simulation
def predict_mood(text):
    text_lower = text.lower()
    if any(word in text_lower for word in ["sad", "down", "unhappy", "depressed"]):
        mood = "Negative 😔"
        song = ("Someone Like You - Adele", "https://open.spotify.com/track/4kflIGfjdZJW4ot2ioixTB")
        products = [("Tissues", "https://www.amazon.in/s?k=tissues"),
                    ("Journal", "https://www.amazon.in/s?k=journal"),
                    ("Comfort food", "https://www.amazon.in/s?k=comfort+food")]
        tip = "It’s okay to feel down. Take a deep breath. ❤️"
    elif any(word in text_lower for word in ["happy", "great", "excited", "joyful"]):
        mood = "Positive 😊"
        song = ("Happy - Pharrell Williams", "https://open.spotify.com/track/6NPVjNh8Jhru9xOmyQigds")
        products = [("Sunglasses", "https://www.amazon.in/s?k=sunglasses"),
                    ("Party Lights", "https://www.amazon.in/s?k=party+lights"),
                    ("Travel Backpack", "https://www.amazon.in/s?k=travel+backpack")]
        tip = "You’re on fire! 🔥 Maybe share your joy with someone?"
    else:
        mood = "Neutral 😐"
        song = ("Weightless - Marconi Union", "https://open.spotify.com/track/1bDbXMyjaUIooNwFE9wn0N")
        products = [("Notebook", "https://www.amazon.in/s?k=notebook"),
                    ("Indoor Plant", "https://www.amazon.in/s?k=indoor+plant"),
                    ("Scented Candle", "https://www.amazon.in/s?k=scented+candle")]
        tip = "Balance is good. Keep it steady 💪"

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("mood_history.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, text, mood])

    return mood, f"[{song[0]}]({song[1]})", format_product_links(products), tip

def format_product_links(products):
    return "  ".join([f"[{name}]({url})" for name, url in products])

def visualize_moods():
    if not os.path.exists("mood_history.csv"):
        return None

    df = pd.read_csv("mood_history.csv", header=None, names=["timestamp", "text", "mood"])
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    fig, axs = plt.subplots(1, 2, figsize=(12, 5))

    # Pie Chart
    mood_counts = df['mood'].value_counts()
    axs[0].pie(mood_counts, labels=mood_counts.index, autopct='%1.1f%%', startangle=90)
    axs[0].set_title("Mood Distribution")

    # Timeline Chart
    df_grouped = df.groupby([df['timestamp'].dt.date, 'mood']).size().unstack(fill_value=0)
    df_grouped.plot(ax=axs[1], marker='o')
    axs[1].set_title("Mood Over Time")
    axs[1].set_xlabel("Date")
    axs[1].set_ylabel("Count")
    plt.tight_layout()

    plt.savefig("mood_chart.png")
    return "mood_chart.png"

def export_csv():
    return "mood_history.csv" if os.path.exists("mood_history.csv") else None

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    try:
        sound = AudioSegment.from_file(audio_path)
        wav_path = audio_path + ".converted.wav"
        sound.export(wav_path, format="wav")

        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        return "Sorry, couldn't understand your speech."
    except sr.RequestError:
        return "Speech recognition service is unavailable."
    except Exception as e:
        return f"Error: {str(e)}"

# Gradio UI
with gr.Blocks(theme=custom_theme) as demo:
    gr.Markdown("# 🛒 MoodMart - Mood-Based Recommendations")

    with gr.Row():
        with gr.Column():
            user_input = gr.Textbox(label="How are you feeling today?")
            voice_input = gr.Audio(label="Or speak your mood", type="filepath")
            transcribe_btn = gr.Button("🎙️ Transcribe Voice")
            submit_btn = gr.Button("Get Suggestions")
            mood_output = gr.Textbox(label="Detected Mood")

        with gr.Column():
            music_output = gr.Markdown()
            product_output = gr.Markdown()
            tip_output = gr.Textbox(label="Wellness Tip")

    with gr.Column():
        gr.Markdown("## 📊 Mood Visualizations")
        chart_btn = gr.Button("Show Mood Chart")
        chart_output = gr.Image()

    with gr.Column():
        gr.Markdown("## 💾 Export Mood History")
        export_btn = gr.Button("Download CSV")
        csv_output = gr.File()

    transcribe_btn.click(transcribe_audio, inputs=voice_input, outputs=user_input)
    submit_btn.click(predict_mood, inputs=user_input, outputs=[mood_output, music_output, product_output, tip_output])
    chart_btn.click(visualize_moods, outputs=chart_output)
    export_btn.click(export_csv, outputs=csv_output)

demo.launch()
