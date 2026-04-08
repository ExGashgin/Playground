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
    # Şəkli açırıq
    raw_image = Image.open(img_input)
    
    # 1. FORMATI SİĞORTALAYIN: Mütləq RGB-yə çevir (HEIC və ya PNG-alpha xətalarını aradan qaldırır)
    image = raw_image.convert("RGB")
    
    # 2. ÖLÇÜNÜ KİÇİLDİN: Sürət üçün vacibdir
    image.thumbnail((512, 512), Image.LANCZOS)
    
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    prompt = "Avtomobil detalı: Ad, Kod, Parametr, Qiymət (AZN). Qısa yaz."
    
    # 3. SORĞUNU GÖNDƏR
    response = model.generate_content([prompt, image])
    return response.text

# --- 3. İNTERFEYS ---
st.title("🚗 Süni İntellektli Ehtiyyat Hissəsi Katalogu")
st.markdown("---")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📸 Detalı Tanıt")
    
    # İki seçim: Ya fayl yüklə, ya da dərhal şəkil çək
    input_type = st.radio("Mənbə seçin:", ["Kamera ilə çək (Mobil/Webcam)", "Qalereyadan seç"], horizontal=True)
    
    img_data = None
    if input_type == "Kamera ilə çək (Mobil/Webcam)":
        img_data = st.camera_input("Hissənin şəklini mərkəzə gətirin")
    else:
        img_data = st.file_uploader("Şəkli bura yükləyin...", type=["jpg", "jpeg", "png"])

    if img_data is not None:
        if st.button("ANALİZ ET VƏ QEYD ET", type="primary", use_container_width=True):
            with st.spinner('Süni intellekt analiz edir...'):
                try:
                    # Analiz
                    result = analyze_image(img_data)
                    
                    # Nəticəni göstər
                    st.success("Analiz tamamlandı!")
                    st.markdown(f"**Nəticə:**\n\n{result}")
                    
                    # Bazaya hazırlıq
                    data_entry = {
                        "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Analiz": result.replace('\n', ' | ')
                    }
                    save_to_csv(data_entry)
                    st.rerun() # Tarixçəni yeniləmək üçün
                except Exception as e:
                    st.error(f"Xəta baş verdi: {str(e)}")

with col2:
    st.subheader("📋 Qeydiyyat Tarixçəsi")
    if os.path.isfile(DB_FILE):
        df = pd.read_csv(DB_FILE)
        st.dataframe(df, use_container_width=True, height=500)
        
        # Yükləmə düymələri
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("Excel/CSV kimi yüklə", data=csv, file_name="anbar_log.csv", mime="text/csv")
        
        if st.button("Tarixçəni sıfırla"):
            os.remove(DB_FILE)
            st.rerun()
    else:
        st.info("Hələ heç bir qeyd yoxdur. Şəkil analiz etdikdən sonra burada görünəcək.")

# --- FOOTER ---
st.markdown("---")
st.caption("v2.0 Beta | Sürətli Analiz və Kamera Dəstəyi aktivdir.")
