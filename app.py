import streamlit as st

st.title("Unlock Download")

access_code = st.text_input("Access code", type="default")

if st.button("Unlock download"):
    valid_codes = st.secrets.get("codes", {})
    
    # --- DEBUG temporário ---
    st.write("Códigos válidos encontrados:", valid_codes)
    st.write("Código digitado:", repr(access_code))
    # ------------------------

    code_clean = access_code.strip()

    if code_clean in valid_codes:
        st.success("Code accepted! Here is your download:")
        st.download_button(
            label="Download file",
            data=open("caminho/real/do/ficheiro.pdf", "rb"),
            file_name="exercicios.pdf"
        )
    else:
        st.error("That code isn't recognized. Double-check it, or use the instructions above to get a valid one from the teacher.")