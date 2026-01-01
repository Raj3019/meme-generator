"""
AI Meme Generator - Streamlit Application
Using Groq for captions and Stability AI for images.
"""

import streamlit as st
from PIL import Image
from io import BytesIO
import colorsys

from ai_utils import generate_caption, generate_image_stability, generate_image_stability_v1
from meme_creator import create_meme, image_to_bytes


# Page config
st.set_page_config(
    page_title="Meme Generator AI",
    page_icon="🎭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif !important; }
    
    #MainMenu, footer, header, .stDeployButton { display: none !important; }
    
    .stApp { background: #0f0f0f; }
    
    .block-container { padding: 2rem 1rem; max-width: 650px; }
    
    h1, h2, h3, h4, p, span, div, label { color: #fff !important; }
    
    /* Inputs */
    .stTextInput input {
        background: #1a1a1a !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
        color: #fff !important;
        padding: 12px !important;
    }
    
    .stTextInput input:focus {
        border-color: #a855f7 !important;
    }
    
    /* Select */
    .stSelectbox > div > div {
        background: #1a1a1a !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(90deg, #a855f7, #ec4899) !important;
        border: none !important;
        border-radius: 8px !important;
        color: #fff !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
    }
    
    .stDownloadButton button {
        background: #22c55e !important;
        border: none !important;
        border-radius: 8px !important;
        color: #fff !important;
        font-weight: 600 !important;
    }
    
    /* Caption display */
    .caption-display {
        background: #000;
        border: 2px solid #f59e0b;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
        text-align: center;
    }
    
    .caption-display p {
        font-family: Impact, sans-serif !important;
        color: #f59e0b !important;
        font-size: 18px;
        text-transform: uppercase;
        margin: 4px 0;
    }
    
    /* Footer */
    .app-footer { text-align: center; color: #444 !important; font-size: 12px; margin-top: 32px; }
    
    /* Style info box */
    .style-info {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        font-size: 14px;
    }
    
    .style-info span { color: #a855f7 !important; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# Style descriptions
STYLE_INFO = {
    "Sarcastic 😏": "Savage, ironic, and mocking. Makes fun of the situation.",
    "Relatable 😅": "Universal experiences everyone has. 'OMG that's so me!'",
    "Absurd 🤪": "Random, nonsensical, surreal humor. Completely unexpected.",
    "Wholesome 😊": "Positive twist, heartwarming, subverts with kindness.",
    "Dark 💀": "Dark humor, existential comedy, self-deprecating about struggles."
}


def init_state():
    defaults = {'meme': None, 'caption': None, 'groq_key': '', 'stability_key': '', 'ready': False}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def fallback_image(topic):
    from PIL import ImageDraw
    h = hash(topic) % 360
    img = Image.new('RGB', (800, 800))
    draw = ImageDraw.Draw(img)
    for y in range(800):
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h/360, 0.6 - y/2000, 0.4 - y/4000)]
        draw.line([(0, y), (800, y)], fill=(max(0,r), max(0,g), max(0,b)))
    return img


def main():
    init_state()
    
    # Header
    st.title("🎭 Meme Generator AI")
    st.caption("Create viral memes in seconds")
    
    st.divider()
    
    # API Setup
    if not st.session_state.ready:
        st.subheader("🔑 Setup API Keys")
        
        groq = st.text_input("Groq API Key", type="password", placeholder="Enter Groq API key...", key="groq_input")
        stability = st.text_input("Stability AI Key", type="password", placeholder="Enter Stability API key...", key="stability_input")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("[Get Groq Key](https://console.groq.com/keys)")
        with col2:
            st.markdown("[Get Stability Key](https://platform.stability.ai/account/keys)")
        
        st.markdown("")  # Spacer
        
        # Continue button
        if st.button("Continue →", width="stretch", disabled=not (groq and stability)):
            st.session_state.groq_key = groq
            st.session_state.stability_key = stability
            st.session_state.ready = True
            st.rerun()
        
        if not (groq and stability):
            st.caption("Enter both API keys to continue")
        
        st.divider()
        
        # How it works
        st.subheader("How it works")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**1️⃣ Enter Topic**")
            st.caption("Type your idea")
        with col2:
            st.markdown("**2️⃣ AI Creates**")
            st.caption("Caption + Image")
        with col3:
            st.markdown("**3️⃣ Download**")
            st.caption("Share anywhere")
        return
    
    # Settings
    if st.button("⚙️ Reset API Keys"):
        st.session_state.ready = False
        st.rerun()
    
    st.divider()
    
    # Input section
    st.subheader("💡 Create Your Meme")
    
    topic = st.text_input("Enter your meme topic", placeholder="e.g., college life, Monday mornings, coding bugs...")
    
    # Style selection with description
    style = st.selectbox("Select Humor Style", list(STYLE_INFO.keys()))
    
    # Show style description
    st.markdown(f'<div class="style-info">🎯 <span>{style.split()[0]}:</span> {STYLE_INFO[style]}</div>', unsafe_allow_html=True)
    
    st.markdown("")  # Spacer
    
    generate = st.button("✨ Generate Meme", width="stretch")
    
    # Generate meme
    if generate:
        if not topic:
            st.warning("Please enter a topic first!")
        else:
            style_name = style.split()[0].lower()
            
            progress = st.progress(0, text="Starting...")
            
            try:
                progress.progress(20, text=f"📝 Generating {style_name} caption about '{topic}'...")
                caption = generate_caption(topic, style_name, st.session_state.groq_key)
                st.session_state.caption = caption
                
                progress.progress(50, text="🎨 Creating image...")
                try:
                    img = generate_image_stability(caption['image_prompt'], st.session_state.stability_key)
                except:
                    try:
                        img = generate_image_stability_v1(caption['image_prompt'], st.session_state.stability_key)
                    except:
                        img = fallback_image(topic)
                
                progress.progress(80, text="🔧 Making meme...")
                st.session_state.meme = create_meme(img, caption['top_text'], caption['bottom_text'])
                
                progress.progress(100, text="✅ Done!")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Display result
    if st.session_state.meme:
        st.divider()
        st.subheader("🖼️ Your Meme")
        
        # Caption preview
        if st.session_state.caption:
            c = st.session_state.caption
            st.markdown(f"""
            <div class="caption-display">
                <p>{c['top_text']}</p>
                <p style="color: #666 !important; font-size: 14px !important;">───</p>
                <p>{c['bottom_text']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Meme image
        st.image(st.session_state.meme, width="stretch")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                "📥 Download", 
                image_to_bytes(st.session_state.meme), 
                "meme.png", 
                "image/png", 
                width="stretch"
            )
        
        with col2:
            if st.button("🔄 Regenerate", width="stretch"):
                st.session_state.meme = None
                st.rerun()
        
        with col3:
            if st.button("🆕 New Meme", width="stretch"):
                st.session_state.meme = None
                st.session_state.caption = None
                st.rerun()
    
    # Footer
    st.markdown('<p class="app-footer">Powered by Groq & Stability AI</p>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
