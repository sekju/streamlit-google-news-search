
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from datetime import datetime

def search_articles(query, domains, start_date, end_date, num_links):
    results = []
    headers_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    search_url = "https://www.google.com/search?q={query}+site:{domain}&tbs=cdr:1,cd_min:{start_date},cd_max:{end_date}&hl=en&start={start}"

    for domain in domains.split(","):
        for start in range(0, num_links, 10):
            try:
                url = search_url.format(query=query, domain=domain.strip(), start_date=start_date.strftime("%m/%d/%Y"), end_date=end_date.strftime("%m/%d/%Y"), start=start)
                headers = {"User-Agent": random.choice(headers_list)}
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                for g in soup.find_all(class_='g'):
                    if len(results) >= num_links:
                        break
                    link = g.find('a', href=True)
                    if link:
                        title = g.find('h3').text if g.find('h3') else link['href']
                        results.append({"summary": title, "link": link['href']})

                time.sleep(random.uniform(1, 3))  # Random delay to avoid being blocked
            except Exception as e:
                st.write(f"Błąd przy przetwarzaniu: {e}")
    return results

st.title("Wyszukiwarka Artykułów")

query = st.text_input("Temat wyszukiwania")
domains = st.text_input("Domeny (oddzielone przecinkiem)")
num_links = st.slider("Liczba linków", min_value=1, max_value=50, value=20)
start_date = st.date_input("Data początkowa")
end_date = st.date_input("Data końcowa")
file_format = st.selectbox("Format pliku", ["csv", "xlsx", "txt"])

if st.button("Szukaj"):
    if start_date > end_date:
        st.write("Data początkowa nie może być późniejsza niż data końcowa.")
    else:
        articles = search_articles(query, domains, start_date, end_date, num_links)
        if articles:
            df = pd.DataFrame(articles)
            st.write(df)
            file_name = f"search_results.{file_format}"
            if file_format == "csv":
                df.to_csv(file_name, index=False)
            elif file_format == "xlsx":
                df.to_excel(file_name, index=False)
            elif file_format == "txt":
                df.to_csv(file_name, index=False, sep='\t')
            with open(file_name, "rb") as file:
                btn = st.download_button(
                    label="Pobierz wyniki",
                    data=file,
                    file_name=file_name,
                    mime="application/octet-stream"
                )
        else:
            st.write("Nie znaleziono wyników.")
