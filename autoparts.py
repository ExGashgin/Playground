import streamlit as st
import pandas as pd
from PIL import Image
import os
from datetime import datetime
from groq import Groq
import base64
import io

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(page_title="Sürətli Hissə Analizi", layout="wide", page_icon="⚡")

# API Key (Streamlit Secrets və ya Lokal üçün)
if "GROQ_API_KEY" in st.secrets:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
else:
    GROQ_KEY = "SİZİN_GROQ_API_AÇARINIZ" # Bura açarınızı daxil edin

client = Groq(api_key=GROQ_KEY)
DB_FILE = "ehtiyyat_hisseleri.csv"

# --- 2. KÖMƏKÇİ FUNKSİYALAR ---

def encode_image(image):
    """Şəkli Groq-un oxuya biləcəyi Base64 formatına salır və ölçüsünü kiçildir."""
    # SÜRƏT ÜÇÜN: Şəkli RGB-yə çevir və kiçilt
    img = image.convert("RGB")
    img.thumbnail((512, 512), Image.LANCZOS)
    
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=80)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def analyze_with_groq(image):
    """Llama 3.2 Vision modelini istifadə edərək ildırım sürətli analiz edir."""
    base64_image = encode_image(image)
    
    # Groq-un Llama 3.2 11B Vision modeli çox sürətlidir
    completion = client.chat.completions.create(
        model="llama-3.2-11b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Bu avtomobil ehtiyyat hissəsini analiz et. Format: Hissənin adı, Artikul, Texniki parametr, Təxmini qiymət (AZN). Qısa və konkret ol."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        temperature=0.1,
        max_tokens=512,
    )
    return completion.choices[0].message.content

def save_to_csv(data):
    if not os.path.isfile(DB_FILE):
        pd.DataFrame([data]).to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    else:
        df = pd.read_csv(DB_FILE)
        pd.concat([df, pd.DataFrame([data])], ignore_index=True).to_csv(DB_FILE, index=False, encoding='utf-8-sig')

# --- 3. İNTERFEYS ---
st.title("⚡ Groq ilə İldırım Sürətli Hissə Analizi")
st.markdown("Llama 3.2 Vision modeli ilə saniyələr içində nəticə.")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📸 Şəkil Mənbəyi")
    source = st.radio("Seçin:", ["Kamera", "Qalereya"], horizontal=True)
    
    img_file = st.camera_input("Şəkil çək") if source == "Kamera" else st.file_uploader("Şəkil yüklə", type=["jpg", "png", "jpeg"])

    if img_file:
        if st.button("SÜRATLİ ANALİZ", type="primary", use_container_width=True):
            with st.spinner('Groq emal edir...'):
                try:
                    pil_img = Image.open(img_file)
                    result = analyze_with_groq(pil_img)
                    
                    st.success("Tamamlandı!")
                    st.write(result)
                    
                    # Log yazmaq
                    save_to_csv({
                        "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Məlumat": result.replace('\n', ' | ')
                    })
                    st.rerun()
                except Exception as e:
                    st.error(f"Xəta: {e}")

with col2:
    st.subheader("📋 Tarixçə")
    if os.path.isfile(DB_FILE):
        df = pd.read_csv(DB_FILE)
        st.dataframe(df, use_container_width=True, height=450)
        
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Yüklə (CSV)", data=csv, file_name="parts_data.csv")
    else:
        st.info("Hələ qeyd yoxdur.")

st.markdown("---")
st.caption("Powered by Groq | Llama 3.2 Vision")
