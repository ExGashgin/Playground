import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import os
from datetime import datetime

# 1. Gemini API Ayarları (Bura öz API açarınızı daxil edin)
# API açarını https://aistudio.google.com/ ünvanından pulsuz ala bilərsiniz
os.environ["GOOGLE_API_KEY"] = "AIzaSyDdUpgfLfcRnjeSsNhIlzYkx5BT9rcWvVA"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# 2. Lokal Database (CSV) Faylı
DB_FILE = "ehtiyyat_hisseleri.csv"

def save_to_csv(data):
    if not os.path.isfile(DB_FILE):
        df = pd.DataFrame([data])
        df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    else:
        df = pd.read_csv(DB_FILE)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

def analyze_image(image):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = """
    Bu avtomobil ehtiyyat hissəsinin şəklidir. Zəhmət olmasa şəkli analiz et və aşağıdakı formatda məlumat ver:
    Hissənin adı: 
    Artikul/Kod: 
    Parametrlər (texniki): 
    Təxmini Bazar Qiyməti (AZN): 
    Yalnız bu formatda cavab yaz.
    """
    response = model.generate_content([prompt, image])
    return response.text

# --- Streamlit İnterfeysi ---
st.set_page_config(page_title="Ehtiyyat Hissəsi Katalogu", layout="wide")
st.title("🚗 Avtomatlaşdırılmış Ehtiyyat Hissəsi Qeydiyyatı")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Şəkil Yüklə")
    uploaded_file = st.file_uploader("Hissənin şəklini seçin...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Yüklənmiş şəkil', use_column_width=True)
        
        if st.button("Analiz et və Yadda saxla"):
            with st.spinner('Süni intellekt analiz edir...'):
                try:
                    # Analiz
                    result = analyze_image(image)
                    lines = result.split('\n')
                    
                    # Məlumatları parçalamaq
                    data_entry = {
                        "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Məlumat": result.replace('\n', ' | ')
                    }
                    
                    # Lokal CSV-yə yazmaq
                    save_to_csv(data_entry)
                    st.success("Məlumatlar uğurla qeyd edildi!")
                    st.write(result)
                except Exception as e:
                    st.error(f"Xəta baş verdi: {e}")

with col2:
    st.subheader("Qeydiyyat Tarixçəsi (Lokal Log)")
    if os.path.isfile(DB_FILE):
        df_display = pd.read_csv(DB_FILE)
        st.dataframe(df_display, use_container_width=True)
        
        # CSV-ni yükləmə düyməsi
        csv = df_display.to_csv(index=False).encode('utf-8-sig')
        st.download_button("Excel/CSV kimi yüklə", data=csv, file_name="anbar_data.csv", mime="text/csv")
    else:
        st.info("Hələ heç bir qeyd yoxdur.")
