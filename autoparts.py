import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import os
from datetime import datetime
import io

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Hissə Tanıma Sistemi", layout="wide", page_icon="🚗")

# API Key Təhlükəsizliyi (Streamlit Cloud və ya Lokal üçün)
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    # Bura öz real API açarınızı daxil edin
    api_key = "SİZİN_API_AÇARINIZ"

genai.configure(api_key=api_key)
DB_FILE = "ehtiyyat_hisseleri.csv"

# --- 2. KÖMƏKÇİ FUNKSİYALAR ---

def save_to_csv(data):
    """Məlumatları CSV faylına qeyd edir."""
    try:
        if not os.path.isfile(DB_FILE):
            df = pd.DataFrame([data])
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
        else:
            df = pd.read_csv(DB_FILE)
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
            df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    except Exception as e:
        st.error(f"Bazaya yazarkən xəta: {e}")

def analyze_image(img_input):
    """Şəkli optimallaşdırır və Gemini 1.5 Flash-a göndərir."""
    # SÜRƏT ÜÇÜN: Şəkli oxu və ölçüsünü kiçilt (Low-res analiz sürətlidir)
    image = Image.open(img_input)
    image.thumbnail((600, 600), Image.LANCZOS)
    
    # Model seçimi (Flash modeli sürət üçün ən yaxşısıdır)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    prompt = """
    Sən peşəkar bir avtomobil ehtiyyat hissələri anbar mütəxəssisisən.
    Şəkildəki detalı dərhal tanı və bu formatda cavab ver:
    Hissənin adı: (Məs: Əyləc bəndi)
    Artikul/Kod: (Varsa kodu
