import io
import re
import pandas as pd
import streamlit as st

# Setări pagină
st.set_page_config(page_title="LITERĂ – Coduri produs", layout="wide")

st.title("LITERĂ")
st.write("Încarcă fișierul Excel (sheet 1) și îți generez tabelul PROMOTER – COD PRODUS – LITERĂ.")

uploaded_file = st.file_uploader(
    "Încarcă fișierul Excel (.xlsx / .xls)", 
    type=["xlsx", "xls"]
)

def detect_product_code_columns(df):
    """
    Identifică automat coloanele care par a fi coduri de produs,
    bazat pe header (numele coloanei).

    Heuristica:
    - numele coloanei începe cu 1–5 litere urmate de cel puțin 1 cifră
      ex: UE98DU9072UXXH, RS57DG46B0MEPC, V15SA5003TRJ/A, WD10T634RBS/EP etc.
    - fără spații la început
    """
    pattern = re.compile(r'^[A-Z]{1,5}\d+', re.IGNORECASE)
    cols = []
    for c in df.columns:
        if isinstance(c, str) and pattern.match(c.strip()):
            cols.append(c)
    return cols

if uploaded_file is not None:
    try:
        # Citim primul sheet (sheet 1)
        # pandas va folosi openpyxl pentru .xlsx dacă e instalat
        df = pd.read_excel(uploaded_file, sheet_name=0)

        # Verificăm dacă există coloana PROMOTER
        if "PROMOTER" not in df.columns:
            st.error("Nu am găsit coloana 'PROMOTER' în fișier. Verifică structura fișierului.")
        else:
            # Detectăm automat coloanele de cod produs
            detected_cols = detect_product_code_columns(df)

            st.markdown("### Coloane de cod produs detectate automat")
            if detected_cols:
                st.write(", ".join(detected_cols))
            else:
                st.warning(
                    "Nu am detectat automat nicio coloană de cod produs. "
                    "Verifică dacă headerele coloanelor au forma codurilor (ex: UE98..., RS57..., V15S..., WD10...)."
                )
                st.stop()

            # Permitem utilizatorului să deselecteze anumite coloane, dacă vrea
            selected_cols = st.multiselect(
                "Alege coloanele de cod produs pe care vrei să le folosești:",
                options=detected_cols,
                default=detected_cols
            )

            if not selected_cols:
                st.warning("Selectează cel puțin o coloană de cod produs pentru a continua.")
                st.stop()

            # Transformăm tabelul în format lung: PROMOTER | COD PRODUS | LITERA
            out = df.melt(
                id_vars=["PROMOTER"],
                value_vars=selected_cols,
                var_name="COD PRODUS",
                value_name="LITERA"
            )

            # Păstrăm doar rândurile cu LITERA nenulă și negoală
            out = out[out["LITERA"].notna() & (out["LITERA"].astype(str).str.strip() != "")]

            # Sortăm după PROMOTER apoi COD PRODUS
            out_sorted = out.sort_values(by=["PROMOTER", "COD PRODUS"])

            st.subheader("Previzualizare tabel rezultat")
            st.dataframe(out_sorted, use_container_width=True)

            # Pregătim pentru download CSV
            csv_bytes = out_sorted.to_csv(index=False).encode("utf-8-sig")

            # Pregătim pentru download Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                out_sorted.to_excel(writer, index=False, sheet_name="Tabel")
            output.seek(0)

            st.download_button(
                label="⬇️ Descarcă tabelul în format CSV",
                data=csv_bytes,
                file_name="tabel_promoter_cod_litera.csv",
                mime="text/csv"
            )

            st.download_button(
                label="⬇️ Descarcă tabelul în format Excel",
                data=output,
                file_name="tabel_promoter_cod_litera.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"A apărut o eroare la prelucrarea fișierului: {e}")
else:
    st.info("Încarcă fișierul Excel ca să începem prelucrarea.")
