import csv
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright, TimeoutError
import unicodedata
import time

INPUT_CSV = "arquivos/cnpjs.csv"
OUTPUT_CSV = "arquivos/resultados.csv"
URL_BASE = "https://www8.receita.fazenda.gov.br/simplesnacional/aplicacoes.aspx?id=21"

CLEAR_INTERVAL = timedelta(minutes=10)
CLEAR_EVERY_N_CNPJS = 50

def load_cnpjs():
    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        return [row[0].strip() for row in csv.reader(f) if row]

def salvar_resultado(cnpj, situacao):
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([cnpj, situacao])
    print(f"✅ Salvo: {cnpj} -> {situacao}")

def normalize_situacao(texto):
    # Remove acentos e transforma em minúsculas
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII').casefold()
    print(f"Situação normalizada: {texto}")
    if "nao optante pelo simples nacional" in texto:
        return False
    return True

def wait_and_fill(frame, selector, value, timeout=20000):
    for _ in range(3):
        try:
            el = frame.wait_for_selector(selector, timeout=timeout, state="visible")
            el.fill(value)
            return True
        except TimeoutError:
            print(f"⚠️ Tentativa de preencher {selector} falhou, retry...")
    return False

def click_and_wait(frame, selector, wait_selector=None, timeout=10000):
    for _ in range(3):
        try:
            btn = frame.wait_for_selector(selector, timeout=timeout, state="visible")
            btn.click()
            if wait_selector:
                frame.wait_for_selector(wait_selector, timeout=timeout)
            return True
        except TimeoutError:
            print(f"⚠️ Tentativa de clicar {selector} falhou, retry...")
    return False

def main():
    cnpjs = load_cnpjs()
    last_cookies_clear = datetime.now()
    processed_count = 0

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        page.goto(URL_BASE)

        frame = page.frame("frame")
        if not frame:
            print("❌ Iframe #frame não encontrado")
            return

        for cnpj in cnpjs:
            processed_count += 1

            # Limpa cookies se necessário
            if (datetime.now() - last_cookies_clear > CLEAR_INTERVAL) or (processed_count % CLEAR_EVERY_N_CNPJS == 0):
                page.context.clear_cookies()
                print("🍪 Cookies limpos automaticamente")
                page.reload()
                frame = page.frame("frame")
                frame.wait_for_selector("#Cnpj", timeout=15000)
                last_cookies_clear = datetime.now()

            # Preenche input
            if not wait_and_fill(frame, "#Cnpj", cnpj):
                salvar_resultado(cnpj, False)
                continue

            # Clica em Consultar e espera resultado
            click_and_wait(frame, "button.btn-verde.h-captcha", wait_selector="div.panel-body, div.alert.alert-danger")

            # Verifica alerta
            alert = frame.query_selector("div.alert.alert-danger")
            if alert:
                close_btn = alert.query_selector("button.close")
                if close_btn:
                    close_btn.click()
                salvar_resultado(cnpj, False)
                continue

            # Pega painel de identificação do contribuinte
            painel_ident = frame.query_selector("div.panel-success:has(h3.panel-title:has-text('Identificação do Contribuinte'))")
            cnpj_texto = nome_texto = ""
            if painel_ident:
                spans = painel_ident.query_selector_all("span.spanValorVerde")
                if len(spans) >= 2:
                    cnpj_texto = spans[0].inner_text().strip()
                    nome_texto = spans[1].inner_text().strip()

            # Pega painel de situação
            painel_situacao = frame.query_selector("div.panel-success:has(h3.panel-title:has-text('Situação Atual'))")
            situacao = False
            if painel_situacao:
                spans_sit = painel_situacao.query_selector_all("span.spanValorVerde")
                if spans_sit:
                    situacao_texto = spans_sit[0].inner_text()
                    situacao = normalize_situacao(situacao_texto)

            salvar_resultado(cnpj, situacao)

            # Volta
            click_and_wait(frame, "a.btn.btn-verde[href='/consultaoptantes']", wait_selector="#Cnpj")
            time.sleep(0.5)
            frame = page.frame("frame")

    print("Processamento finalizado.")

if __name__ == "__main__":
    main()
