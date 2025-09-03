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
    return all_data

all_data = load_data()

# ====================== Sidebar Logo ====================== #
with st.sidebar:
    st.image(
        "https://raw.githubusercontent.com/projekardana/dashboard-ecommerce-analysis_data_science/main/dashboard/img/Logo.png"
    )
    st.title("Dashboard E-Commerce")

# ====================== Filter Sidebar ====================== #
st.sidebar.subheader("Filter Data")

# Filter tanggal
if "order_purchase_timestamp" in all_data.columns:
    all_data["order_purchase_timestamp"] = pd.to_datetime(all_data["order_purchase_timestamp"])
    min_date = all_data["order_purchase_timestamp"].min()
    max_date = all_data["order_purchase_timestamp"].max()

    date_range = st.sidebar.date_input(
        "Pilih Rentang Tanggal",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date,
    )
    if len(date_range) == 2:
        start_date, end_date = date_range
        all_data = all_data[
            (all_data["order_purchase_timestamp"] >= pd.to_datetime(start_date))
            & (all_data["order_purchase_timestamp"] <= pd.to_datetime(end_date))
        ]

# Filter kategori
if "product_category_name_english" in all_data.columns:
    categories = all_data["product_category_name_english"].dropna().unique()
    selected_categories = st.sidebar.multiselect(
        "Pilih Kategori Produk",
        sorted(categories),
        default=None,
    )
    if selected_categories:
        all_data = all_data[all_data["product_category_name_english"].isin(selected_categories)]

# ====================== Sidebar Menu ====================== #
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

    if "order_purchase_timestamp" in all_data.columns:
        all_data["order_month"] = all_data["order_purchase_timestamp"].dt.to_period("M").astype(str)
        orders_per_month = all_data.groupby("order_month")["order_id"].nunique().reset_index()
        orders_per_month.columns = ["Month", "Total Orders"]

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=orders_per_month, x="Month", y="Total Orders", marker="o", ax=ax)
        ax.set_title("Tren Jumlah Pesanan Bulanan")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.warning("Kolom order_purchase_timestamp tidak tersedia di dataset.")

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

# ============================== Top Categories ======================================== #
elif page == "Top Categories":
    st.title("10 Kategori Produk Teratas yang Paling Banyak Terjual")

    # Load dataset tambahan
    @st.cache_data
    def load_top_categories():
        return pd.read_csv(
            "https://raw.githubusercontent.com/projekardana/dashboard-ecommerce-analysis_data_science/main/dashboard/orders_item_with_category.csv"
        )

    top_cat = load_top_categories()

    if "product_category_name_english" in top_cat.columns:
        # Hitung jumlah order per kategori
        top10 = (
            top_cat.groupby("product_category_name_english")["order_id"]
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
        st.warning("Kolom kategori tidak ditemukan di dataset top_categories.")

# ============================== Review Score ======================================== #
elif page == "Review Score":
    st.title("Distribusi Skor Review Pelanggan")

    @st.cache_data
    def load_reviews():
        return pd.read_csv(
            "https://raw.githubusercontent.com/projekardana/dashboard-ecommerce-analysis_data_science/main/dashboard/orders_item_with_category.csv"
        )

    reviews = load_reviews()

    if "review_score" in reviews.columns:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.countplot(data=reviews, x="review_score", palette="Set2", ax=ax)
        ax.set_title("Distribusi Skor Review")
        ax.set_xlabel("Skor Review")
        ax.set_ylabel("Jumlah")
        st.pyplot(fig)

        st.metric("Rata-rata Skor Review", round(reviews["review_score"].mean(), 2))
    else:
        st.warning("Kolom review_score tidak ditemukan di dataset reviews.")

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