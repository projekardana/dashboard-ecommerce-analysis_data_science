#  E-Commerce Dashboard Analysis 

Proyek ini merupakan analisis data berbasis Python terhadap dataset publik e-commerce Brazil. Melalui eksplorasi data dan visualisasi interaktif menggunakan **Streamlit**, dashboard ini dirancang untuk memberikan wawasan mendalam terkait perilaku pelanggan, performa pelanggan, pengiriman, rating pengguna maupun analisis lokasi pelanggan.

---
## Tujuan Proyek
- Menganalisis distribusi geografis pelanggan dan penjual
- Mengidentifikasi kategori produk paling populer
- Mengevaluasi keterlambatan pengiriman dan kepuasan pelanggan
- Menyediakan dashboard interaktif agar user non-teknis bisa mengeksplorasi data dengan mudah
---

## Setup Environtment - Miniconda

```
conda create --name main-ds python=3.10
conda activate main-ds
pip install -r requirements.txt
```
---
##  Setup Environtment - Shell/Terminal
```
mkdir e-commerce
cd e-commerce
pipenv install
pipenv shell
pip install -r requirements.txt
```
---

## Tools & Libraries
- **Python** (v3.10+)
- **pandas** – manipulasi data
- **matplotlib**, **seaborn**, **plotly** – visualisasi
- **streamlit** – deploy dashboard interaktif
- **Platform Google Colab** – eksplorasi awal dan EDA
- **pycharm** - membangun dashboard analysis

## ![img.png](img.png) Run Streamlit APP
```
streamlit run dashboard.py
```
----

## Sumber Dataset

- Dataset yang digunakan berasal dari Kaggle yaitu Brazilian E-Commerce Public Dataset
- Link dataset :
   https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce


***Dataset mencakup:**
- Pelanggan
- Informasi pesanan pelanggan dan penjual 
- Detail produk dan kategori 
- Waktu pengiriman 
- Ulasan pelanggan
- Geolocation Analysis
---

## Contact

Proyek ini dikembangkan untuk keperluan pembelajaran dan eksplorasi data analitik sekaligus dalam memperkuat
portofolio di bidang Data Science

Silakan hubungi saya jika ada keperluan :

- Email: mdendiardana@gmail.com
- LinkedIn: linkedin.com/in/mdendiardana
- GitHub: github.com/projekardana