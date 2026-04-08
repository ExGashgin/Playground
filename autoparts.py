import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import os
from datetime import datetime

# --- Konfiqurasiya və Təhlükəsizlik ---
# QEYD: Lokalda işlədərkən "GOOGLE_API_KEY"i sistem mühit dəyişəni olaraq təyin edin 
# və ya aşağıdakı st.secrets hissəsini öz açarınızla əvəz edin.
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # Lokal test üçün bura öz açarınızı yaza bilərsiniz (Lakin GitHub-a yükləməyin!)
    API_KEY = "SİZİN_API_AÇARINIZ_BURA"

genai.configure(api_key=API_KEY)

# Lokal Database (CSV) Faylı
DB_FILE = "ehtiyyat_hisseleri.csv"

def save_to_csv(data):
    """Məlumatları CSV faylına əlavə edir."""
    if not os.path.isfile(DB_FILE):
        df = pd.DataFrame([data])
        df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    else:
        df = pd.read_csv(DB_FILE)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

def analyze_image(image):
    """Gemini 1.5 Flash modelini istifadə edərək şəkli analiz edir."""
    # 'gemini-1.5-flash-latest' 404 xətalarının qarşısını almaq üçün ən etibarlı seçimdir
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    prompt = """
    Sən bir avtomobil ehtiyyat hissələri üzrə mütəxəssissən. 
    Şəkildəki detalı analiz et və aşağıdakı xanalara uyğun məlumat ver:
    
    Hissənin adı: 
    Artikul/Kod: 
    Parametrlər (texniki): 
    Təxmini Bazar Qiyməti (AZN): 
    
    Zəhmət olmasa yalnız bu formatda cavab ver, əlavə giriş cümlələri yazma.
    """
    
    response = model.generate_content([prompt, image])
    return response.text

# --- Streamlit İnterfeysi ---
st.set_page_config(page_title="Ehtiyyat Hissəsi Katalogu", layout="wide", page_icon="🚗")

st.title("🚗 Avtomatlaşdırılmış Ehtiyyat Hissəsi Qeydiyyatı")
st.markdown("---")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📸 Şəkil Yüklə və Analiz Et")
    uploaded_file = st.file_uploader("Hissənin şəklini seçin...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Yüklənmiş şəkil', use_container_width=True)
        
        analyze_button = st.button("Süni İntellektlə Analiz Et", type="primary")
        
        if analyze_button:
            with st.spinner('Süni intellekt detalı tanıyır...'):
                try:
                    # Analiz prosesi
                    result = analyze_image(image)
                    
                    # Nəticəni göstər
                    st.info("Analiz Nəticəsi:")
                    st.write(result)
                    
                    # Məlumatı bazaya hazırlamaq
                    data_entry = {
                        "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Detallar": result.replace('\n', ' | ')
                    }
                    
                    # Yadda saxla
                    save_to_csv(data_entry)
                    st.success("Məlumatlar tarixçəyə əlavə edildi!")
                    st.rerun() # Cədvəli yeniləmək üçün
                    
                except Exception as e:
                    st.error(f"Xəta baş verdi: {str(e)}")
                    st.warning("Məsləhət: API açarınızın aktiv olduğunu və 'google-generativeai' kitabxanasının son versiya olduğunu yoxlayın.")

with col2:
    st.subheader("📋 Qeydiyyat Tarixçəsi")
    if os.path.isfile(DB_FILE):
        df_display = pd.read_csv(DB_FILE)
        
        # Cədvəli göstər
        st.dataframe(df_display, use_container_width=True, height=400)
        
        # Excel/CSV yükləmə
        csv_data = df_display.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Tarixçəni Yüklə (CSV)",
            data=csv_data,
            file_name=f"anbar_tarixce_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        if st.button("Tarixçəni Təmizlə"):
            os.remove(DB_FILE)
            st.rerun()
    else:
        st.info("Hələ heç bir qeyd yoxdur. Analiz etdikdən sonra burada görünəcək.")

# --- Footer ---
st.markdown("---")
st.caption("Gemini 1.5 Flash tərəfindən dəstəklənir | 2026")
