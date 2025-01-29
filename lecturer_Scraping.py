import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import pandas as pd
import time

# URL halaman pertama dari daftar penulis di SINTA
url = "https://sinta.kemdikbud.go.id/affiliations/authors/2053" # anda bisa mengubah kampus dengan menganti kode angka pada tautan setelah authors
response = requests.get(url)

# Cek apakah permintaan berhasil dilakukan
if response.status_code == 200:
    html_content = response.text
else:
    print('Gagal mengambil halaman:', response.status_code)

# Parsing HTML menggunakan BeautifulSoup
html = response.text
soup = BeautifulSoup(html, 'html.parser')

# Menampilkan struktur HTML yang telah diambil
print(soup.prettify())

def scrape_page(page_number):
    """
    Fungsi untuk melakukan scraping data penulis dari halaman tertentu di SINTA.

    Parameter:
    - page_number: Nomor halaman yang akan diambil datanya.

    Return:
    - List berisi data penulis dari halaman yang diambil.
    """
    url = f"https://sinta.kemdikbud.go.id/affiliations/authors/2053?page={page_number}" # anda bisa mengubah kampus dengan menganti kode angka pada tautan setelah authors
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    authors_data = []  # List untuk menyimpan data penulis

    # Mencari semua item penulis di halaman
    for item in soup.select('.au-item'):
        name = item.select_one('.profile-name a').text.strip()  # Mengambil nama penulis
        dept = item.select_one('.profile-dept').text.strip()  # Mengambil nama departemen
        stats = item.select('.stat-num.text-center')  # Mengambil data skor SINTA

        # Menyimpan skor berdasarkan urutan tampilan di website
        sinta_score_3yr = stats[0].text.strip()
        sinta_score = stats[1].text.strip()
        affil_score_3yr = stats[2].text.strip()
        affil_score = stats[3].text.strip()

        # Menambahkan data ke dalam list
        authors_data.append({
            'name': name,
            'dept': dept,
            'sinta_score_3yr': sinta_score_3yr,
            'sinta_score': sinta_score,
            'affil_score_3yr': affil_score_3yr,
            'affil_score': affil_score
        })

    return authors_data  # Mengembalikan data yang telah dikumpulkan

def main(max_page=20):
    """
    Fungsi utama untuk menjalankan proses scraping hingga batas halaman tertentu.

    Parameters:
    max_page (int): Jumlah maksimal halaman yang akan di-scrape.
    """
    all_authors = []  # List untuk menyimpan semua data penulis
    page = 1  # Memulai dari halaman pertama

    while page <= max_page:  # Loop hanya sampai batas halaman yang ditentukan
        print(f"Scraping halaman {page}...")  # Menampilkan informasi proses scraping
        authors = scrape_page(page)  # Scraping data dari halaman saat ini
        if not authors:  # Jika tidak ada data, hentikan proses
            break
        all_authors.extend(authors)  # Menambahkan data ke dalam list utama
        page += 1  # Pindah ke halaman berikutnya

        # Memberikan jeda 10 detik sebelum berpindah ke halaman berikutnya
        if page <= max_page:  # Hanya tunggu jika masih ada halaman berikutnya
            time.sleep(10)

    # Membuat tabel untuk menampilkan data
    table = PrettyTable()
    table.field_names = ["Nama Penulis", "Departemen", "SINTA Score 3Yr", "SINTA Score", "Affil Score 3Yr", "Affil Score"]

    # Memasukkan data penulis ke dalam tabel
    for author in all_authors:
        table.add_row([author['name'], author['dept'], author['sinta_score_3yr'], author['sinta_score'], author['affil_score_3yr'], author['affil_score']])

    # Mencetak tabel ke terminal
    print(table)

    # Menyimpan data ke dalam file CSV
    df = pd.DataFrame(all_authors)  # Mengubah list ke dataframe pandas
    df.to_csv("sinta_authors.csv", index=False)  # Simpan sebagai CSV tanpa index

    print("Scraping selesai! Data disimpan di 'sinta_authors.csv'.")

if __name__ == '__main__':
    main(max_page=20)  # Ganti angka sesuai jumlah halaman yang ingin diambil
