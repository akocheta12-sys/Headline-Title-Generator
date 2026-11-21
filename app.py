
import os
import json
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai

# ==========================
# CONFIGURATION
# ==========================
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="AI Headline Studio",
    page_icon="📰",
    layout="wide"
)

# ==========================
# CUSTOM CSS
# ==========================
st.markdown("""
<style>
.main {
    padding-top: 1.5rem;
}
.block-container {
    max-width: 1100px;
    padding-top: 2rem;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px;
}
.headline-title {
    font-size: 34px;
    font-weight: 800;
}
.subtitle {
    color: #888888;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# ==========================
# SIDEBAR
# ==========================
with st.sidebar:
    st.title("📰 AI Headline Studio")

    st.markdown("---")

    st.markdown("### About")
    st.write(
        "Generate creative, relevant headlines for articles "
        "and evaluate them using AI-based clarity scores."
    )

    st.markdown("### How to use")
    st.markdown("""
    1. Paste an article or topic.
    2. Click Generate Headlines.
    3. Review 10 headline suggestions.
    4. Compare clarity scores.
    5. Download the results.
    """)

    st.markdown("---")
    st.caption("Generative AI Mini Project")
    st.caption("Roll No. 10")

# ==========================
# HEADER
# ==========================
st.markdown(
    '<div class="headline-title">✨ AI Headline Generator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Transform articles and topics into engaging headlines '
    'with AI-powered clarity evaluation.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")

# ==========================
# API CHECK
# ==========================
if not API_KEY:
    st.error("API key missing. Please check your .env file.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# ==========================
# INPUT SECTION
# ==========================
st.subheader("📝 Enter your article or topic")

article = st.text_area(
    "Article / Topic",
    height=230,
    placeholder="Paste your article or describe your topic here...",
    label_visibility="collapsed"
)

col1, col2 = st.columns([1, 5])

with col1:
    generate_button = st.button(
        "✨ Generate Headlines",
        type="primary",
        use_container_width=True
    )

with col2:
    st.caption(
        "The AI will generate 10 headlines, evaluate clarity "
        "and sort them from highest to lowest score."
    )

# ==========================
# GENERATION FUNCTION
# ==========================
def generate_headlines(article_text):

    prompt = f"""
You are a professional headline writer and editor.

Analyze the article or topic below and generate exactly 10 unique headlines.

For every headline:
- Make it engaging, relevant and clear.
- Do not invent facts.
- Assign a clarity score from 1 to 10.
- Provide a short reason for the clarity score.

Return ONLY valid JSON in the following structure:

{{
    "headlines": [
        {{
            "headline": "Example headline",
            "clarity_score": 9,
            "reason": "This headline clearly explains the topic."
        }}
    ]
}}

Generate exactly 10 headlines.
Scores must be integers between 1 and 10.

Article or topic:
{article_text}
"""

    max_retries = 3
    response = None

    for attempt in range(max_retries):

        try:

            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )

            break

        except Exception:

            if attempt == max_retries - 1:
                raise

            wait_time = 2 ** (attempt + 1)

            time.sleep(wait_time)

    if response is None or not response.text:
        raise ValueError("Empty response received from AI.")

    result = json.loads(response.text)

    headlines = result.get("headlines", [])

    # Sort by clarity score
    headlines = sorted(
        headlines,
        key=lambda x: int(x["clarity_score"]),
        reverse=True
    )

    return headlines

# ==========================
# DISPLAY RESULTS
# ==========================
if generate_button:

    if not article.strip():

        st.warning("Please enter an article or topic.")

    else:

        try:

            with st.spinner("✨ AI is analyzing your content..."):

                headlines = generate_headlines(article)

            st.success("Headlines generated successfully!")

            st.markdown("---")
            st.subheader("🏆 Your Generated Headlines")

            st.caption(
                f"{len(headlines)} headline suggestions "
                "sorted by clarity score."
            )

            for i, item in enumerate(headlines, start=1):

                score = int(item["clarity_score"])

                with st.container(border=True):

                    left, right = st.columns([5, 1])

                    with left:

                        st.markdown(
                            f"**{i}. {item['headline']}**"
                        )

                        st.caption(item["reason"])

                    with right:

                        st.metric(
                            "Clarity",
                            f"{score}/10"
                        )

            # ==========================
            # DOWNLOAD
            # ==========================
            output_text = "\n\n".join(
                [
                    f"{i}. {item['headline']}\n"
                    f"Clarity Score: {item['clarity_score']}/10\n"
                    f"Reason: {item['reason']}"
                    for i, item in enumerate(headlines, start=1)
                ]
            )

            st.markdown("---")

            st.download_button(
                label="📥 Download All Headlines",
                data=output_text,
                file_name="AI_generated_headlines.txt",
                mime="text/plain",
                use_container_width=True
            )

        except Exception as e:

            st.error("Unable to generate headlines.")

            st.write("Error details:", str(e))

            st.info(
                "Please check your API connection or try again later."
            )

# ==========================
# FOOTER
# ==========================
st.markdown("---")

st.markdown(
    "<center>Built with Python, Streamlit and Generative AI</center>",
    unsafe_allow_html=True
)
