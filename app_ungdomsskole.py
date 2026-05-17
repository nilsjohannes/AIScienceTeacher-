# -*- coding: utf-8 -*-
import streamlit as st
import json
import urllib.request
import urllib.error
import base64
from PIL import Image

st.set_page_config(page_title="MentorAI - Ungdomsskole")
st.title("🎓 MentorAI: Ungdomsskole")
st.subheader("Få hjelp med matte og naturfag (8.-10. trinn)")

# 1. HUSK API-NØKKEL (Session State)
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# Hvis du vil, kan du lime inn din nøkkel her permanent:
HARDCODED_KEY = "DIN_API_N\u00d8KKEL_HER"

if HARDCODED_KEY != "DIN_API_N\u00d8KKEL_HER":
    st.session_state.api_key = HARDCODED_KEY.strip()

if not st.session_state.api_key:
    st.info("For \u00e5 starte m\u00e5 du legge inn din Google AI API-n\u00f8kkel under:")
    api_input = st.text_input("Lim inn API-n\u00f8kkel her:", type="password")
    if api_input:
        st.session_state.api_key = api_input.strip()
        st.rerun()

# 2. HVIS NØKKEL ER FUNNET, START APPEN
if st.session_state.api_key:
    
    # Velg fag for å spisse KI-en
    fag = st.selectbox(
        "Hvilket fag trenger du hjelp med i dag?",
        ["Matematikk", "Naturfag"]
    )
    
    # Skreddersydd personlighet for 13-16 åringer basert på LK20
    SYSTEM_PROMPT = (
        f"Du er en t\u00e5lmodig, engasjerende og superflink privatl\u00e6rer i faget {fag} "
        "for ungdomsskolen i Norge (8.-10. trinn). Du f\u00f8lger l\u00e6replanen LK20.\n"
        "Din jobb er \u00e5 f\u00e5 eleven til \u00e5 f\u00f8le mestring. Du skal ALDRI gi svaret med en gang.\n"
        "Bruk denne sokratiske metoden tilpasset ungdomsskoleelever:\n"
        "1. Se p\u00e5 bildet eller teksten eleven sender.\n"
        "2. Sjekk om eleven kan de grunnleggende begrepene (f.eks. hva et fortegn er i matte, "
        "eller hva en kjemisk forbindelse er i naturfag).\n"
        "3. Still ETT enkelt, l\u00e6rende sp\u00f8rsm\u00e5l av gangen. Ikke overveld dem med lange tekster.\n"
        "4. Bruk enkle, visuelle forklaringer og gjerne eksempler fra hverdagen.\n"
        "Snakk flytende, hyggelig og motiverende norsk."
    )

    uploaded_file = st.file_uploader("Ta bilde av oppgaven din i boka eller p\u00e5 skjermen:", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Oppgaven din", use_container_width=True)

    if "messages_us" not in st.session_state:
        st.session_state.messages_us = []

    for message in st.session_state.messages_us:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input(f"Hva lurer du på i {fag.lower()}?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages_us.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            fullstendig_tekst = f"KONTEKST: Eleven har valgt faget {fag}.\n{SYSTEM_PROMPT}\n\n--- ELEVENS SP\u00d8RSM\u00c5L ---\n{prompt}"
            parts = [{"text": fullstendig_tekst}]
            
            if uploaded_file:
                img_bytes = uploaded_file.getvalue()
                img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                parts.append({
                    "inlineData": {
                        "mimeType": uploaded_file.type,
                        "data": img_b64
                    }
                })
                
            payload = {"contents": [{"parts": parts}]}
            binary_data = json.dumps(payload, ensure_ascii=True).encode("utf-8")
            
            # Moderne 2026-modeller
            modeller_aa_proeve = ["gemini-2.0-flash", "gemini-2.5-flash"]
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={st.session_state.api_key}"
            
            suksess = False
            full_response = ""
            
            for modell in modeller_aa_proeve:
                if suksess: break
                url = f"https://generativelanguage.googleapis.com/v1/models/{modell}:generateContent?key={st.session_state.api_key}"
                try:
                    req = urllib.request.Request(
                        url,
                        data=binary_data,
                        headers={"Content-Type": "application/json"},
                        method="POST"
                    )
                    with urllib.request.urlopen(req) as response:
                        res_data = json.loads(response.read().decode("utf-8"))
                        full_response = res_data["candidates"][0]["content"]["parts"][0]["text"]
                        suksess = True
                except:
                    continue
            
            if suksess:
                message_placeholder.markdown(full_response)
                st.session_state.messages_us.append({"role": "assistant", "content": full_response})
            else:
                st.error("Kunne ikke opprette forbindelse. Sjekk at API-n\u00f8kkelen din er aktiv.")