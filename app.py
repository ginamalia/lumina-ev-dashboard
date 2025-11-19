import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# -----------------------------------------------------------------------------
# 1. KONFIGURASI HALAMAN & CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Lumina EV Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Palet Warna Konsisten (Nuansa Biru/Cyan untuk Dark Mode)
COLOR_PALETTE = px.colors.sequential.Blues[::-1]
PRIMARY_COLOR = "#00D4FF" # Cyan terang untuk highlight
SECONDARY_COLOR = "#007BFF" # Biru untuk elemen sekunder

st.markdown("""
<style>
    /* Mengatur warna background global agar sesuai dark mode */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Header Styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FFFFFF;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0px 0px 10px rgba(0, 212, 255, 0.5);
    }
    
    .sub-text {
        text-align: center; 
        color: #A0AAB5; 
        font-size: 1.1rem; 
        margin-bottom: 2rem;
    }

    .section-header {
        font-size: 1.5rem;
        color: #FFFFFF;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #00D4FF;
        padding-left: 10px;
    }

    /* Insight Box Styling (Menyesuaikan Referensi Image) */
    .insight-box {
        background-color: #0F2838; /* Dark Blue Background */
        border: 1px solid #1E3D53;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
        color: #E0E0E0;
        font-size: 0.95rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Metric Cards Styling */
    div[data-testid="stMetric"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        padding: 15px;
        border-radius: 10px;
        color: white;
    }
    div[data-testid="stMetricLabel"] {
        color: #A0AAB5;
    }
    div[data-testid="stMetricValue"] {
        color: #00D4FF;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #A0AAB5;
    }
    .stTabs [aria-selected="true"] {
        background-color: #161B22;
        color: #00D4FF;
        border-bottom: 2px solid #00D4FF;
    }
    
    /* PERBAIKAN: Mengubah warna chip multiselect dari merah ke biru */
    /* Menargetkan chip yang dipilih (selected) */
    .stMultiSelect [data-testid="stStatusWidget"] {
        background-color: #007BFF; /* Warna background chip (Biru) */
        border: 1px solid #00D4FF; 
        color: white; /* Warna teks chip */
    }
    
    /* Menargetkan tombol 'X' di dalam chip */
    .stMultiSelect [data-testid="stStatusWidget"] svg {
        fill: white; /* Warna ikon 'X' */
    }
    
    /* Menargetkan tombol 'X' pada saat hover (agar tidak kembali ke merah) */
    .stMultiSelect [data-testid="stStatusWidget"]:hover svg {
        fill: #FFDD00; /* Warna kuning agar terlihat interaktif saat hover */
    }

    /* Styling untuk container foto mobil di Tab Merek */
    .car-photo-container {
        border: 1px solid #30363D;
        background-color: #161B22;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        margin-bottom: 10px;
        height: 100%; /* Agar tinggi container konsisten */
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .model-name {
        font-weight: bold;
        color: #00D4FF;
        margin-top: 5px;
    }
    .model-image {
        max-width: 100%;
        height: auto;
        border-radius: 5px;
    }
    
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. FUNGSI LOAD DATA & UTILS
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("https://raw.githubusercontent.com/ginamalia/dataset/refs/heads/main/Electric_Vehicle_Population_Data.csv")
    
    df_clean = df.copy()
    cols_to_drop = [
        'Base MSRP', 'Electric Range', 'Legislative District', 
        'VIN (1-10)', 'DOL Vehicle ID', '2020 Census Tract',
        'Vehicle Location'
    ]
    
    df_clean = df_clean.drop(columns=[col for col in cols_to_drop if col in df_clean.columns], errors='ignore')
    
    df_clean = df_clean.dropna()
    
    if 'Postal Code' in df_clean.columns:
        df_clean['Postal Code'] = df_clean['Postal Code'].astype(float).astype(int).astype(str)
    
    return df_clean

def apply_dark_theme(fig):
    """Helper function untuk menerapkan tema dark konsisten ke semua plot"""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="sans-serif", color="white"),
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified"
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#30363D')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#30363D')
    return fig

def display_insight(text):
    """Helper untuk menampilkan kotak insight"""
    st.markdown(f"""
    <div class="insight-box">
        <span style="font-size: 1.2rem;">💡</span> <strong>Insight:</strong><br>
        {text}
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. MAIN APP LOGIC
# -----------------------------------------------------------------------------

# Load data
with st.spinner('Memuat data...'):
    df_clean = load_data()

# Sidebar
with st.sidebar:
    st.markdown("## ⚡ Filter Data")
    
    min_year = int(df_clean['Model Year'].min())
    max_year = int(df_clean['Model Year'].max())
    
    year_range = st.slider(
        "Rentang Tahun Model",
        min_value=min_year,
        max_value=max_year,
        value=(2015, max_year)
    )
    
    ev_types = st.multiselect(
        "Tipe Kendaraan",
        options=df_clean['Electric Vehicle Type'].unique(),
        default=df_clean['Electric Vehicle Type'].unique()
    )
    
    counties = st.multiselect(
        "Pilih County (Opsional)",
        options=sorted(df_clean['County'].unique()),
        default=None
    )
    
    st.markdown("---")
    st.markdown("### 📊 Tentang Dashboard")
    st.info("""
    Dashboard ini menganalisis data kendaraan listrik di Washington State, USA.
    Sumber Data: Dataset Kaggle - Global Electric Vehicle Trends
    
    **Kelompok Lumina:**
    - Alma Alifya Zafira
    - Alustina Suci Manah
    - Ridhaka Gina Amalia
    """)

# Filter Logic
df_filtered = df_clean[
    (df_clean['Model Year'] >= year_range[0]) & 
    (df_clean['Model Year'] <= year_range[1]) &
    (df_clean['Electric Vehicle Type'].isin(ev_types))
]

if counties and not df_filtered[df_filtered['County'].isin(counties)].empty:
    df_filtered = df_filtered[df_filtered['County'].isin(counties)]
elif counties and df_filtered[df_filtered['County'].isin(counties)].empty:
    st.warning("Kombinasi filter saat ini (termasuk County) menghasilkan data kosong. Menampilkan data hanya berdasarkan filter Tahun dan Tipe EV.")

if df_filtered.empty:
    st.error("Semua filter menghasilkan data kosong. Silakan sesuaikan filter Anda.")
    df_filtered = df_clean

# Judul Utama
st.markdown('<div class="main-header">⚡ Dashboard Analisis Kendaraan Listrik</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Analisis Tren Adopsi EV di Negara Bagian Washington, USA</div>', unsafe_allow_html=True)

# Metrics
m1, m2, m3, m4 = st.columns(4)

total_ev_filtered = len(df_filtered)
total_ev_clean = len(df_clean)
bev_count_filtered = len(df_filtered[df_filtered['Electric Vehicle Type'] == 'Battery Electric Vehicle (BEV)'])
phev_count_filtered = len(df_filtered[df_filtered['Electric Vehicle Type'] == 'Plug-in Hybrid Electric Vehicle (PHEV)'])

m1.metric("Total Kendaraan", f"{total_ev_filtered:,}", delta=f"{(total_ev_filtered/total_ev_clean*100):.1f}% dari total" if total_ev_clean > 0 else "N/A")
m2.metric("Total BEV", f"{bev_count_filtered:,}", delta=f"{(bev_count_filtered/total_ev_filtered*100):.1f}%" if total_ev_filtered > 0 else "0.0%")
m3.metric("Total PHEV", f"{phev_count_filtered:,}", delta=f"{(phev_count_filtered/total_ev_filtered*100):.1f}%" if total_ev_filtered > 0 else "0.0%")
m4.metric("Merek Unik", f"{df_filtered['Make'].nunique()}", delta=f"{df_filtered['Model'].nunique()} model")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Geografis", "📈 Tren", "🚗 Merek", "⚡ Tipe EV", "📊 Lanjutan"
])

# --- TAB 1: GEOGRAFIS ---
with tab1:
    st.markdown('<div class="section-header">Distribusi Geografis</div>', unsafe_allow_html=True)
    
    col_map1, col_map2 = st.columns(2)
    
    with col_map1:
        top_counties = df_filtered['County'].value_counts().nlargest(10)
        fig_county = go.Figure()
        fig_county.add_trace(go.Bar(
            x=top_counties.index,
            y=top_counties.values,
            marker=dict(
                color=top_counties.values,
                colorscale='Blues',
                showscale=False,
                colorbar=dict(
                    title=dict(text="Jumlah", font=dict(color="white")),
                    tickfont=dict(color="white")
                )
            ),
            text=top_counties.values,
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Jumlah: %{y:,.0f}<extra></extra>'
        ))
        fig_county.update_layout(
            title="Top 10 County",
            xaxis_title="County",
            yaxis_title="Jumlah Kendaraan",
            height=450
        )
        st.plotly_chart(apply_dark_theme(fig_county), use_container_width=True)
        
    with col_map2:
        top_cities = df_filtered['City'].value_counts().nlargest(10)
        fig_city = go.Figure()
        fig_city.add_trace(go.Bar(
            x=top_cities.index,
            y=top_cities.values,
            marker=dict(
                color=top_cities.values,
                colorscale='Blues',
                showscale=False,
                colorbar=dict(
                    title=dict(text="Jumlah", font=dict(color="white")),
                    tickfont=dict(color="white")
                )
            ),
            text=top_cities.values,
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Jumlah: %{y:,.0f}<extra></extra>'
        ))
        fig_city.update_layout(
            title="Top 10 City",
            xaxis_title="City",
            yaxis_title="Jumlah Kendaraan",
            height=450
        )
        st.plotly_chart(apply_dark_theme(fig_city), use_container_width=True)

    if not top_counties.empty:
        display_insight(f"King County mendominasi dengan {top_counties.values[0]:,} kendaraan, jauh melampaui county lainnya. Ini menunjukkan konsentrasi adopsi EV di area metropolitan Seattle.")
    else:
        display_insight("Tidak ada data County yang tersedia berdasarkan filter saat ini.")

# --- TAB 2: TREN ---
with tab2:
    st.markdown('<div class="section-header">Tren Pertumbuhan</div>', unsafe_allow_html=True)
    
    trend_data = df_filtered.groupby('Model Year').size().reset_index(name='Count')
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=trend_data['Model Year'],
        y=trend_data['Count'],
        mode='lines+markers',
        name='Jumlah',
        line=dict(color=PRIMARY_COLOR, width=3),
        marker=dict(size=8, color='white', line=dict(width=1, color=PRIMARY_COLOR)),
        fill='tozeroy',
        fillcolor='rgba(0, 212, 255, 0.1)'
    ))
    
    if not trend_data.empty:
        peak_row = trend_data.loc[trend_data['Count'].idxmax()]
        fig_trend.add_annotation(
            x=peak_row['Model Year'],
            y=peak_row['Count'],
            text=f"Peak: {peak_row['Count']:,}",
            showarrow=True,
            arrowhead=2,
            arrowcolor="white",
            bgcolor="#0F2838",
            font=dict(color=PRIMARY_COLOR)
        )

    fig_trend.update_layout(
        title="Pertumbuhan Adopsi EV per Tahun Model",
        xaxis_title="Tahun Model",
        yaxis_title="Jumlah Kendaraan",
        height=500
    )
    st.plotly_chart(apply_dark_theme(fig_trend), use_container_width=True)
    
    if not trend_data.empty:
        display_insight(f"Adopsi EV mengalami lonjakan signifikan mulai tahun 2018, mencapai puncaknya pada tahun {int(peak_row['Model Year'])}.")
    else:
        display_insight("Tidak ada data tren yang tersedia berdasarkan filter saat ini.")

# --- TAB 3: MEREK ---
with tab3:
    st.markdown('<div class="section-header">Analisis Merek (Make) dan Model</div>', unsafe_allow_html=True)
    
    # ----------------------------------------------------------------------
    # DEFINISI MAPPING URL FOTO 
    # ----------------------------------------------------------------------
    MODEL_IMAGE_MAP = {
        "MODEL Y": "https://digitalassets.tesla.com/tesla-contents/image/upload/f_auto,q_auto/Homepage-Card-Model-Y-Desktop-US-v2.jpg", 
        "MODEL 3": "https://digitalassets.tesla.com/tesla-contents/image/upload/f_auto,q_auto/Homepage-Card-Model-3-Desktop-US-v2.jpg",
        "LEAF": "https://dealernissandijakarta.com/wp-content/uploads/2021/08/nissan-leaf-1.jpg",
        "BOLT EV": "https://cdn.motor1.com/images/mgl/ow6gL/s1/2022-chevrolet-bolt-euv-interior.webp",
        "MODEL X": "https://digitalassets.tesla.com/tesla-contents/image/upload/f_auto,q_auto/Homepage-Card-Model-X-New-Desktop-US-v4.jpg",
    }

    # --- Baris 1: Top 15 Merek (Treemap - Full Width) ---
    st.markdown("### Distribusi Merek Kendaraan")
    top_makes = df_filtered['Make'].value_counts().nlargest(15)
    
    fig_make = go.Figure(go.Treemap(
        labels=top_makes.index,
        parents=[""] * len(top_makes), # Set parents to empty string list for top level
        values=top_makes.values,
        marker=dict(colorscale='Blues'),
        textposition='middle center',
        texttemplate='<b>%{label}</b><br>%{value:,.0f}',
        hovertemplate='<b>%{label}</b><br>Jumlah: %{value:,.0f}<br>Pangsa: %{percentParent:.1%}<extra></extra>'
    ))
    
    fig_make.update_layout(
        title="Top 15 Merek Kendaraan (Pangsa Pasar)",
        height=500
    )
    # Terapkan tema gelap dan tampilkan
    st.plotly_chart(apply_dark_theme(fig_make), use_container_width=True)

    st.markdown("---")

    # --- Baris 2: Top 15 Model (Sunburst Chart - Full Width) ---
    st.markdown("### Model Paling Populer")
    top_models = df_filtered['Model'].value_counts().nlargest(15)
    fig_model = go.Figure(go.Sunburst(
        labels=top_models.index,
        parents=[""] * len(top_models),
        values=top_models.values,
        marker=dict(colorscale='Blues'),
        hovertemplate='<b>%{label}</b><br>Jumlah: %{value:,.0f}<extra></extra>'
    ))
    fig_model.update_layout(
        title="Top 15 Model Kendaraan",
        height=500,
        margin=dict(t=50, b=20, l=20, r=20)
    )
    st.plotly_chart(apply_dark_theme(fig_model), use_container_width=True)
    
    # --- Insight & Foto Template ---
    st.markdown("---")
    if not top_makes.empty and not top_models.empty:
        display_insight(f"**{top_makes.index[0]}** mendominasi pasar, sementara model paling populer adalah **{top_models.index[0]}**.")
    else:
        display_insight("Tidak ada data Merek atau Model yang tersedia berdasarkan filter saat ini.")
    
    st.markdown("### 📷 Top 5 Model Kendaraan Terpopuler")
    
    # Mengatur layout foto dalam satu baris horizontal kecil
    top_5_model_names = df_filtered['Model'].value_counts().nlargest(5).index.tolist()[:5]
    cols_photo = st.columns(5)
    
    for i, model_name in enumerate(top_5_model_names):
        # Ambil URL dari mapping
        image_url = MODEL_IMAGE_MAP.get(model_name, "")
        
        with cols_photo[i]:
            st.markdown(f"""
            <div class="car-photo-container">
                <img src="{image_url}" class="model-image" alt="Foto {model_name}" />
                <div class="model-name">#{i+1}: {model_name}</div>
            </div>
            """, unsafe_allow_html=True)
            
# --- TAB 4: TIPE EV ---
with tab4:
    st.markdown('<div class="section-header">Perbandingan BEV vs PHEV</div>', unsafe_allow_html=True)
    
    col_type1, col_type2 = st.columns(2)
    
    with col_type1:
        type_counts = df_filtered['Electric Vehicle Type'].value_counts()
        fig_type_bar = go.Figure(go.Bar(
            x=type_counts.index.str.replace('Battery Electric Vehicle (BEV)', 'BEV').str.replace('Plug-in Hybrid Electric Vehicle (PHEV)', 'PHEV'),
            y=type_counts.values,
            marker=dict(color=[PRIMARY_COLOR, SECONDARY_COLOR]),
            text=type_counts.values,
            textposition='auto'
        ))
        fig_type_bar.update_layout(
            title="Jumlah Kendaraan per Tipe",
            height=400
        )
        st.plotly_chart(apply_dark_theme(fig_type_bar), use_container_width=True)
        
    with col_type2:
        top_5_counties = df_filtered['County'].value_counts().nlargest(5).index
        df_top5 = df_filtered[df_filtered['County'].isin(top_5_counties)]
        
        type_county = df_top5.groupby(['County', 'Electric Vehicle Type']).size().unstack().fillna(0)
        
        fig_stack = go.Figure()
        fig_stack.add_trace(go.Bar(
            name='BEV',
            x=type_county.index,
            y=type_county.get('Battery Electric Vehicle (BEV)', 0),
            marker_color=PRIMARY_COLOR
        ))
        fig_stack.add_trace(go.Bar(
            name='PHEV',
            x=type_county.index,
            y=type_county.get('Plug-in Hybrid Electric Vehicle (PHEV)', 0),
            marker_color=SECONDARY_COLOR
        ))
        
        fig_stack.update_layout(
            barmode='stack',
            title="Proporsi Tipe EV di 5 County Teratas",
            height=400,
            legend=dict(orientation="v", y=1.1)
        )
        st.plotly_chart(apply_dark_theme(fig_stack), use_container_width=True)

    if total_ev_filtered > 0:
        bev_pct = (bev_count_filtered / total_ev_filtered * 100)
        display_insight(f"Kendaraan Listrik Baterai Murni (BEV) jauh lebih populer dibandingkan Plug-in Hybrid (PHEV), mencakup {bev_pct:.1f}% dari total populasi EV yang difilter.")
    else:
        display_insight("Tidak ada data Tipe Kendaraan yang tersedia berdasarkan filter saat ini.")

# --- TAB 5: LANJUTAN ---
with tab5:
    st.markdown('<div class="section-header">Analisis Lanjutan</div>', unsafe_allow_html=True)
    
    # --- Baris 1: Top 10 Electric Utility (Bar Chart) ---
    st.markdown("### Distribusi Berdasarkan Penyedia Listrik")
    top_utility = df_filtered['Electric Utility'].value_counts().nlargest(10)
    fig_utility = go.Figure(go.Bar(
        y=top_utility.index,
        x=top_utility.values,
        orientation='h',
        marker=dict(
            color=top_utility.values,
            colorscale='Blues',
            showscale=False
        ),
        text=top_utility.values,
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Jumlah Kendaraan: %{x:,.0f}<extra></extra>'
    ))
    
    fig_utility.update_layout(
        title="Top 10 Penyedia Listrik (Electric Utility)",
        xaxis_title="Jumlah Kendaraan",
        yaxis_title="Penyedia Listrik",
        height=500,
        yaxis=dict(autorange="reversed")
    )
    st.plotly_chart(apply_dark_theme(fig_utility), use_container_width=True)

    if not top_utility.empty:
        top_utility_count = df_filtered['Electric Utility'].value_counts().nlargest(1).iloc[0]
        display_insight(f"Penyedia listrik {top_utility.index[0]} melayani {top_utility_count:,} kendaraan listrik terbanyak, yang sebagian besar kemungkinan besar merupakan wilayah metropolitan King County.")
    else:
        display_insight("Tidak ada data Utility atau Heatmap yang tersedia berdasarkan filter saat ini.")

    st.markdown("---")

    # --- Baris 2: Heatmap Tahun vs Merek ---
    st.markdown("### Heatmap: Intensitas Model per Tahun vs Merek")
    top_makes_heat = df_filtered['Make'].value_counts().nlargest(10).index
    df_heat = df_filtered[df_filtered['Make'].isin(top_makes_heat)]
    heatmap_data = df_heat.groupby(['Make', 'Model Year']).size().reset_index(name='Count')
    
    heatmap_matrix = heatmap_data.pivot(index='Make', columns='Model Year', values='Count').fillna(0)
    
    fig_heat = go.Figure(data=go.Heatmap(
        z=heatmap_matrix.values,
        x=heatmap_matrix.columns,
        y=heatmap_matrix.index,
        colorscale='Blues',
        colorbar=dict(
            title=dict(text="Jumlah", font=dict(color="white")),
            tickfont=dict(color="white")
        )
    ))
    
    fig_heat.update_layout(
        title="Heatmap: Intensitas Model per Tahun vs Merek",
        xaxis_title="Tahun Model",
        yaxis_title="Merek",
        height=500
    )
    st.plotly_chart(apply_dark_theme(fig_heat), use_container_width=True)

    display_insight("Heatmap memperlihatkan bagaimana merek tertentu (seperti Tesla) mulai mendominasi di tahun-tahun belakangan, sementara merek lain memiliki pola pertumbuhan yang berbeda.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.8rem;">
    © 2025 Kelompok Lumina | Universitas Singaperbangsa Karawang<br>
    Data Source: Washington State Department of Licensing
</div>
""", unsafe_allow_html=True)