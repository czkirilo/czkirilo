import os

def main():
    scholar_url = os.getenv("GOOGLE_SCHOLAR_URL")
    print("Iniciando script...")
    if not scholar_url:
        print("❌ GOOGLE_SCHOLAR_URL não encontrada.")
        exit(1)

    print(f"✅ URL recebida: {scholar_url}")
    # Aqui normalmente viria a chamada de scraping...
    print("✅ Finalizou com sucesso.")

if __name__ == "__main__":
    main()

