import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ============================== Load Dataset ======================================== #
@st.cache_data
def load_data():
    all_data = pd.read_csv("all_data.csv")
    all_data["order_purchase_timestamp"] = pd.to_datetime(all_data["order_purchase_timestamp"])
    all_data["order_delivered_customer_date"] = pd.to_datetime(all_data["order_delivered_customer_date"], errors='coerce')
    all_data["order_month"] = all_data["order_purchase_timestamp"].dt.to_period("M").astype(str)
    return all_data

all_data = load_data()

# ============================== Hitung RFM ======================================== #
all_data["order_purchase_timestamp"] = pd.to_datetime(all_data["order_purchase_timestamp"])

latest_date = all_data["order_purchase_timestamp"].max()

# Hitung Recency
recency_df = all_data.groupby("customer_unique_id")["order_purchase_timestamp"].max().reset_index()
recency_df["Recency"] = (latest_date - recency_df["order_purchase_timestamp"]).dt.days
recency_df = recency_df[["customer_unique_id", "Recency"]]

# Hitung Frequency
frequency_df = all_data.groupby("customer_unique_id")["order_id"].nunique().reset_index()
frequency_df.columns = ["customer_unique_id", "Frequency"]

# Hitung Monetary
monetary_df = all_data.groupby("customer_unique_id")["payment_value"].sum().reset_index()
monetary_df.columns = ["customer_unique_id", "Monetary"]

# Gabungkan RFM
rfm_table = recency_df.merge(frequency_df, on="customer_unique_id")
rfm_table = rfm_table.merge(monetary_df, on="customer_unique_id")

rfm_table["Monetary"] = rfm_table["Monetary"].fillna(0)

# Skoring R, F, M
rfm_table["R_Score"] = pd.qcut(rfm_table["Recency"], 4, labels=[4, 3, 2, 1])
rfm_table["F_Score"] = pd.qcut(rfm_table["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4])
rfm_table["M_Score"] = pd.qcut(rfm_table["Monetary"], 4, labels=[1, 2, 3, 4])

rfm_table["RFM_Score"] = rfm_table["R_Score"].astype(int) + \
                         rfm_table["F_Score"].astype(int) + \
                         rfm_table["M_Score"].astype(int)


def rfm_segment(score):
    if score >= 10:
        return "Champions"
    elif score >= 8:
        return "Loyal Customers"
    elif score >= 6:
        return "Potential Loyalist"
    elif score >= 4:
        return "At Risk"
    else:
        return "Lost"


rfm_table["Segment"] = rfm_table["RFM_Score"].apply(rfm_segment)



# ====================== Sidebar ====================== #
with st.sidebar:
    st.image("img/Logo.png")
    st.title("Dashboard E-Commerce")

    # Filter Tanggal
    st.subheader("Filter Tanggal")
    min_date = all_data["order_purchase_timestamp"].min().date()
    max_date = all_data["order_purchase_timestamp"].max().date()

    date_range = st.date_input(
        label="Rentang Tanggal",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        st.warning("Mohon pilih dua tanggal")
        st.stop()

    filtered_data = all_data.copy()
    filtered_data = filtered_data[
        (filtered_data["order_purchase_timestamp"].dt.date >= start_date) &
        (filtered_data["order_purchase_timestamp"].dt.date <= end_date)
    ]

    # Filter Kategori Produk
    st.subheader("Filter Kategori Produk")
    if "product_category_name_english" in filtered_data.columns:
        categories = filtered_data["product_category_name_english"].dropna().unique()
        selected_categories = st.multiselect(
            "Pilih Kategori Produk",
            sorted(categories)
        )

        if selected_categories:
            filtered_data = filtered_data[
                filtered_data["product_category_name_english"].isin(selected_categories)
            ]

    page = st.radio(
        "Pilih Halaman",
        [
            "Beranda",
            "Delivery Analysis",
            "Payment Methods",
            "Order Trend",
            "Top Categories",
            "Review Score",
            "RFM Analysis",
            "Geolocation Analysis"
        ],
    )

# ====================== Beranda ====================== #
if page == "Beranda":
    st.title("E-Commerce Dashboard")
    st.markdown("Dashboard ini menampilkan hasil analisis dari dataset `all_data.csv`")

    st.subheader("Preview Dataset")
    st.dataframe(all_data.head())

    st.subheader("Info Kolom Dataset")
    st.write(list(all_data.columns))

# ====================== Delivery Analysis ====================== #
elif page == "Delivery Analysis":
    st.title("Rata-rata Waktu Pengiriman")
    df = filtered_data.copy()
    df["delivery_duration"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.days

    delivery_df = df.dropna(subset=["delivery_duration"])
    avg_delivery = delivery_df["delivery_duration"].mean()
    st.metric("Rata-rata Waktu Pengiriman (Hari)", round(avg_delivery, 2))

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(delivery_df["delivery_duration"], bins=30, kde=True, color="steelblue")
    ax.set_title("Distribusi Lama Pengiriman ke Pelanggan (dalam hari)")
    ax.set_xlabel("Hari")
    ax.set_ylabel("Jumlah Pesanan")
    ax.set_xlim(0, delivery_df["delivery_duration"].quantile(0.95))
    st.pyplot(fig)

# ====================== Payment Methods ====================== #
elif page == "Payment Methods":
    st.title("Metode Pembayaran Populer")

    if "payment_type" in filtered_data.columns:
        payment_counts = filtered_data["payment_type"].value_counts().reset_index()
        payment_counts.columns = ["Payment Type", "Count"]

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(data=payment_counts, x="Count", y="Payment Type", palette="viridis", ax=ax)
        ax.set_title("Distribusi Metode Pembayaran")
        st.pyplot(fig)
    else:
        st.warning("Kolom payment_type tidak ditemukan.")

# ====================== Order Trend ====================== #
elif page == "Order Trend":
    st.title("Tren Jumlah Pesanan per Bulan")

    try:
        orders_per_month = filtered_data.groupby("order_month")["order_id"].nunique().reset_index()
        orders_per_month.columns = ["Month", "Total Orders"]

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(data=orders_per_month, x="Month", y="Total Orders", marker="o", ax=ax)
        ax.set_title("Tren Jumlah Pesanan Bulanan")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    except Exception as e:
        st.warning(f"Terjadi kesalahan: {e}")

# ====================== Top Categories ====================== #
elif page == "Top Categories":
    st.title("10 Kategori Produk Teratas")

    if "product_category_name_english" in filtered_data.columns:
        top10 = (
            filtered_data.groupby("product_category_name_english")["order_id"]
            .count()
            .reset_index()
        )
        top10 = top10.sort_values("order_id", ascending=False).head(10)

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(
            data=top10,
            x="order_id",
            y="product_category_name_english",
            palette="Blues_r",
            ax=ax,
        )
        ax.set_title("Top 10 Kategori Produk Terlaris")
        ax.set_xlabel("Jumlah Order")
        ax.set_ylabel("Kategori Produk")
        st.pyplot(fig)
    else:
        st.warning("Kolom kategori produk tidak tersedia.")

# ====================== Review Score ====================== #
elif page == "Review Score":
    st.title("Distribusi Skor Review")

    if "review_score" in filtered_data.columns:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.countplot(data=filtered_data, x="review_score", palette="Set2", ax=ax)
        ax.set_title("Distribusi Skor Review")
        ax.set_xlabel("Skor Review")
        ax.set_ylabel("Jumlah")
        st.pyplot(fig)

        st.metric("Rata-rata Skor Review", round(filtered_data["review_score"].mean(), 2))
    else:
        st.warning("Kolom review_score tidak tersedia.")

# ====================== RFM Analysis ====================== #
elif page == "RFM Analysis":
    st.title("Analysis RFM & Clustering Distribusi Segmentasi Pelanggan Berdasarkan RFM")

    @st.cache_data
    def load_rfm_df():
        return pd.read_csv("rfm_df.csv")

    rfm_data = load_rfm_df()

    st.subheader("RFM Analysis (Recency, Frequency, Monetary)")

    # Visualisasi 3 kolom: Recency, Frequency, Monetary
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

    # Top 5 by Recency (terkecil = terbaik)
    top_recency = rfm_data.sort_values(by="recency").head(5)
    sns.barplot(y="customer_unique_id", x="recency", data=top_recency, palette="Blues_r", ax=ax[0])
    ax[0].set_title("By Recency (days)", fontsize=16)
    ax[0].set_xlabel("Days")
    ax[0].set_ylabel("Customer ID")
    ax[0].bar_label(ax[0].containers[0], padding=3)

    # Top 5 by Frequency
    top_freq = rfm_data.sort_values(by="frequency", ascending=False).head(5)
    sns.barplot(y="customer_unique_id", x="frequency", data=top_freq, palette="Greens", ax=ax[1])
    ax[1].set_title("By Frequency", fontsize=16)
    ax[1].set_xlabel("Total Orders")
    ax[1].set_ylabel("")
    ax[1].bar_label(ax[1].containers[0], padding=3)

    # Top 5 by Monetary
    top_monetary = rfm_data.sort_values(by="monetary", ascending=False).head(5)
    sns.barplot(y="customer_unique_id", x="monetary", data=top_monetary, palette="Oranges", ax=ax[2])
    ax[2].set_title("By Monetary Value", fontsize=16)
    ax[2].set_xlabel("Total Spent")
    ax[2].set_ylabel("")
    ax[2].bar_label(ax[2].containers[0], padding=3)

    plt.suptitle("Best Customers Based on RFM Parameters", fontsize=20)
    plt.tight_layout()
    st.pyplot(fig)

    # ====================== Clustering ====================== #
    required_cols = [
        "order_id", "customer_id", "customer_unique_id",
        "order_purchase_timestamp", "payment_value"
    ]
    if not all(col in all_data.columns for col in required_cols):
        st.error("Dataset tidak memiliki semua kolom yang dibutuhkan untuk analisis RFM.")
        st.stop()
    st.subheader("Distribusi Segmen Pelanggan")

    fig1, ax1 = plt.subplots(figsize=(8, 5))
    sns.countplot(
        data=rfm_table,
        x="Segment",
        order=["Champions", "Loyal Customers", "Potential Loyalist", "At Risk", "Lost"],
        palette="viridis",
        ax=ax1
    )
    ax1.set_title("Distribusi Segmen Pelanggan Berdasarkan RFM")
    ax1.set_xlabel("Segment")
    ax1.set_ylabel("Jumlah Pelanggan")
    st.pyplot(fig1)

    st.subheader("Proporsi Segmen Pelanggan")
    seg_counts = rfm_table["Segment"].value_counts()
    fig2, ax2 = plt.subplots()
    ax2.pie(seg_counts, labels=seg_counts.index, autopct="%1.1f%%",
            colors=sns.color_palette("viridis", len(seg_counts)))
    st.pyplot(fig2)


# ============================== Geolocation Analysis ============================== #
elif page == "Geolocation Analysis":
    st.title("Sebaran Pesanan Pelanggan Berdasarkan Lokasi")

    @st.cache_data
    def load_geo_city():
        geo_city = pd.read_csv("https://raw.githubusercontent.com/projekardana/dashboard-ecommerce-analysis_data_science/main/dashboard/geo_city.csv")
        return geo_city

    geo_city = load_geo_city()

    if "customer_city" not in all_data.columns:
        st.error("Kolom 'customer_city' tidak tersedia di all_data.csv")
        st.stop()

    geo_agg = geo_city.groupby("city")[["lat", "lng"]].mean().reset_index()
    orders_geo = all_data.merge(geo_agg, left_on="customer_city", right_on="city", how="left")

    orders_geo = orders_geo.rename(columns={"lat": "lat", "lng": "lon"})
    orders_geo = orders_geo.dropna(subset=["lat", "lon"])

    st.markdown(f"Total pesanan dengan lokasi valid: **{len(orders_geo):,}**")

    # Batasi titik untuk performa peta
    if len(orders_geo) > 2000:
        orders_geo = orders_geo.sample(2000, random_state=42)
        st.info("Data ditampilkan sebagian (2000 titik) untuk menjaga performa.")

    st.map(orders_geo[["lat", "lon"]])
