import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ============================== Load Dataset ======================================== #
@st.cache_data
def load_data():
    # Load all_data
    all_data = pd.read_csv(
        "https://raw.githubusercontent.com/projekardana/dashboard-ecommerce-analysis_data_science/main/dashboard/all_data.csv"
    )

    # Load translation
    translation = pd.read_csv(
        "https://raw.githubusercontent.com/projekardana/dashboard-ecommerce-analysis_data_science/main/dashboard/product_category_name_translation.csv"
    )

    # Merge supaya ada kolom kategori english
    if "product_category_name" in all_data.columns:
        all_data = all_data.merge(
            translation, on="product_category_name", how="left"
        )

    return all_data


all_data = load_data()

# ====================== Sidebar Menu ====================== #
with st.sidebar:
    st.image(
        "https://raw.githubusercontent.com/projekardana/dashboard-ecommerce-analysis_data_science/main/dashboard/img/Logo.png"
    )
    st.title("Dashboard E-Commerce")
page = st.sidebar.radio(
    "Pilih Halaman",
    [
        "Beranda",
        "Delivery Analysis",
        "Payment Methods",
        "Order Trend",
        "Geolocation Analysis",
        "Top Categories",
        "Review Score",
        "Analysis Lanjutan (RFM)",
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

    df = all_data.copy()
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["order_delivered_customer_date"] = pd.to_datetime(
        df["order_delivered_customer_date"]
    )

    # Kolom delivery_duration
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

    st.markdown(
        """
        **Insight:**
        - Rata-rata waktu pengiriman sekitar 10 hari.  
        - Sebagian besar pesanan dikirim 3–10 hari.  
        - Ada outlier >20 hari → kemungkinan keterlambatan logistik.  
        """
    )

# ====================== Payment Methods ====================== #
elif page == "Payment Methods":
    st.title("Metode Pembayaran Populer")

    if "payment_type" in all_data.columns:
        order_payment_df = all_data["payment_type"].value_counts().reset_index()
        order_payment_df.columns = ["Payment Type", "Count"]

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(data=order_payment_df, x="Count", y="Payment Type", palette="viridis")
        ax.set_title("Distribusi Metode Pembayaran")
        st.pyplot(fig)
    else:
        st.warning("Kolom payment_type tidak ditemukan di dataset.")

# ====================== Order Trend ====================== #
elif page == "Order Trend":
    st.title("Tren Jumlah Pesanan per Bulan")

    if "order_month" in all_data.columns:
        orders_per_month = all_data.groupby("order_month")["order_id"].nunique().reset_index()
        orders_per_month.columns = ["Month", "Total Orders"]

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=orders_per_month, x="Month", y="Total Orders", marker="o", ax=ax)
        ax.set_title("Tren Jumlah Pesanan Bulanan")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.warning("Kolom order_month tidak tersedia di dataset.")

# ============================== Geolocation Analysis ============================== #
elif page == "Geolocation Analysis":
    st.header("Sebaran Pesanan Pelanggan Berdasarkan Lokasi")

    orders = pd.read_csv(
        "https://raw.githubusercontent.com/projekardana/dashboard-ecommerce-analysis_data_science/main/dashboard/order_df.csv"
    )
    customers = pd.read_csv(
        "https://raw.githubusercontent.com/projekardana/dashboard-ecommerce-analysis_data_science/main/dashboard/customers.csv"
    )
    geolocation = pd.read_csv(
        "https://raw.githubusercontent.com/projekardana/dashboard-ecommerce-analysis_data_science/main/dashboard/geo_city.csv"
    )

    geo_agg = geolocation.groupby("city")[["lat", "lng"]].mean().reset_index()
    orders_customer = orders.merge(customers, on="customer_id", how="left")

    orders_geo = orders_customer.merge(
        geo_agg, left_on="customer_city", right_on="city", how="left"
    )
    orders_geo = orders_geo.rename(columns={"lat": "lat", "lng": "lon"})
    orders_geo = orders_geo.dropna(subset=["lat", "lon"])

    if len(orders_geo) > 2000:
        orders_geo = orders_geo.sample(2000, random_state=42)

    st.map(orders_geo[["lat", "lon"]])

# ====================== Top Categories ====================== #
elif page == "Top Categories":
    st.title("10 Kategori Produk Teratas yang Paling Banyak Terjual")

    if "product_category_name_english" in all_data.columns:
        top_categories = (
            all_data["product_category_name_english"].value_counts().reset_index()
        )
        top_categories.columns = ["Product Category", "Total Sold"]
        top10 = top_categories.head(10)

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(
            data=top10, x="Total Sold", y="Product Category", palette="Blues_r", ax=ax
        )
        ax.set_title("Top 10 Kategori Produk Terlaris")
        st.pyplot(fig)

        st.markdown(
            """
            **Insight:**
            - Kategori ini mendominasi penjualan.  
            - Dapat menjadi fokus utama strategi pemasaran & stok produk.  
            """
        )
    else:
        st.warning("Kolom kategori tidak ditemukan di dataset.")

# ====================== Review Score ====================== #
elif page == "Review Score":
    st.title("Distribusi Skor Review Pelanggan")

    if "review_score" in all_data.columns:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.countplot(data=all_data, x="review_score", palette="Set2", ax=ax)
        ax.set_title("Distribusi Skor Review")
        ax.set_xlabel("Review Score")
        ax.set_ylabel("Jumlah")
        st.pyplot(fig)

        avg_review = all_data["review_score"].mean()
        st.metric("Rata-rata Skor Review", round(avg_review, 2))

        st.markdown(
            """
            **Insight:**
            - Mayoritas pelanggan memberikan skor tinggi (4–5).  
            - Skor rendah (<3) perlu diperhatikan untuk evaluasi layanan & kualitas produk.  
            """
        )
    else:
        st.warning("Kolom review_score tidak ditemukan di dataset.")

# ====================== Analysis Lanjutan (RFM) ====================== #
elif page == "Analysis Lanjutan (RFM)":
    st.title("Analysis Lanjutan (RFM)")

    df = all_data.copy()
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])

    snapshot_date = df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    rfm = (
        df.groupby("customer_id")
        .agg(
            {
                "order_purchase_timestamp": lambda x: (snapshot_date - x.max()).days,
                "order_id": "count",
                "payment_value": "sum",
            }
        )
        .reset_index()
    )
    rfm.columns = ["customer_id", "Recency", "Frequency", "Monetary"]

    # Skor RFM
    rfm["R"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1])
    rfm["F"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4])
    rfm["M"] = pd.qcut(rfm["Monetary"], 4, labels=[1, 2, 3, 4])
    rfm["RFM_Segment"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)
    rfm["RFM_Score"] = rfm[["R", "F", "M"]].astype(int).sum(axis=1)

    rfm["Segment"] = "Regular"
    rfm.loc[rfm["RFM_Score"] >= 9, "Segment"] = "Best Customers"
    rfm.loc[rfm["RFM_Score"] <= 5, "Segment"] = "Lost Customers"

    st.subheader("Distribusi Segmen Pelanggan")
    seg_counts = rfm["Segment"].value_counts().reset_index()
    seg_counts.columns = ["Segment", "Count"]

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.barplot(data=seg_counts, x="Segment", y="Count", palette="Set2", ax=ax)
    ax.set_title("Distribusi Customer Segments")
    st.pyplot(fig)

    st.subheader("Data RFM")
    st.dataframe(rfm.head())
