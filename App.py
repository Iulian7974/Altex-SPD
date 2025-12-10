import io
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Tabel Promoter - Cod - Literă", layout="wide")

st.title("Generator tabel PROMOTER - COD PRODUS - LITERĂ")
st.write("Încarcă fișierul Excel (sheet 1) și îți generez tabelul cerut.")

uploaded_file = st.file_uploader(
    "Încarcă fișierul Excel (.xlsx / .xls)", 
    type=["xlsx", "xls"]
)

if uploaded_file is not None:
    try:
        # Citim primul sheet (sheet 1)
        df = pd.read_excel(uploaded_file, sheet_name=0)

        # Verificăm dacă există coloana PROMOTER
        if "PROMOTER" not in df.columns:
            st.error("Nu am găsit coloana 'PROMOTER' în fișier. Verifică structura fișierului.")
        else:
            # Identificăm coloanele de cod produs care încep cu UE sau QE
            code_cols = [
                c for c in df.columns 
                if isinstance(c, str) and (c.startswith("UE") or c.startswith("QE"))
            ]

            if not code_cols:
                st.error("Nu am găsit coloane de cod produs care încep cu 'UE' sau 'QE'.")
            else:
                # Transformăm tabelul în format lung: PROMOTER | COD PRODUS | LITERA
                out = df.melt(
                    id_vars=["PROMOTER"],
                    value_vars=code_cols,
                    var_name="COD PRODUS",
                    value_name="LITERA"
                )

                # Păstrăm doar rândurile cu LITERA nenulă și negoală
                out = out[out["LITERA"].notna() & (out["LITERA"].astype(str) != "")]

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
