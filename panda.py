import pandas as pd

# Carregar os dois CSVs
status = pd.read_csv("arquivos/resultados.csv", names=["cnpj", "ativo"], dtype={"cnpj": str})
empresas = pd.read_csv("arquivos/gui.csv", dtype={"cnpj": str})

empresas["cnpj"] = empresas["cnpj"].str.replace(r"\D", "", regex=True)

resultado = empresas.merge(status, on="cnpj", how="left")

# Salvar em um novo CSV
resultado.to_csv("empresas_com_status.csv", index=False)
