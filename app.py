import time
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.graph_objects as go

# --- 1. CẤU HÌNH GIAO DIỆN TRANG WEB ---
st.set_page_config(
    page_title="BMS OCC - Sân vận động 20.000 Chỗ (Đề tài 13)",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://www.facebook.com/hoangducchinh',
        'Report a Bug': "https://www.facebook.com/hoangducchinh",
        'About': "Đồ án BMS | Nhóm Đề số 13 - ĐH Mở Hà Nội | TS. Hoàng Đức Chính"
    }
)

# --- 2. TÙY CHỈNH CSS ĐỒ HỌA SÁNG SỦA, CÂN ĐỐI ---
st.markdown("""
<style>
    header {visibility: hidden;}
    .main {background-color: #f8f9fa;}
    .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
    h1 {color: #111827; font-weight: 800 !important; font-size: 2.2rem;}
    h3 {color: #0d6efd; font-size: 1.2rem; font-weight: 700;}
    p, span, label, .stMarkdown {color: #212529 !important;}
</style>
""", unsafe_allow_html=True)


# --- 3. HÀM GIẢ LẬP DỮ LIỆU ĐỘNG HOÀN TOÀN THEO THANH TRƯỢT KHÁN GIẢ ---
def get_mock_data(audience_val, fan_val):
  df = pd.DataFrame({
      'Thời gian': [f"T-{i}s" for i in range(60, 0, -1)],
      'Nồng độ CO2 (ppm)': np.zeros(60),
      'Tần số Quạt (%)': np.zeros(60),
  })

  # CO2 bám sát tuyệt đối theo giá trị khán giả trên thanh trượt ở mọi thời điểm
  base_co2 = 420 + (audience_val / 20000) * 850
  df['Nồng độ CO2 (ppm)'] = np.clip(
      np.random.normal(base_co2, 12, 60) + np.linspace(0, audience_val * 0.004, 60),
      400,
      1500,
  )
  df['Tần số Quạt (%)'] = np.clip(
      np.random.normal(fan_val, 2, 60), 15, 100
  )

  return df


# --- 4. TIÊU ĐỀ TRANG CHỦ ---
st.title("🏛️ TRUNG TÂM ĐIỀU HÀNH HỆ THỐNG BMS (OCC)")
st.markdown(
    "<span style='color: #0d6efd; font-weight: 700;'>Đề tài số 13:</span> Thiết"
    " kế sơ bộ hệ thống BMS cho Sân vận động / Nhà thi đấu đa năng 20.000"
    " chỗ &nbsp;|&nbsp; <span style='color: #0d6efd; font-weight:"
    " 700;'>SVTH:</span> Ngô Văn Quang (K25-TĐH2) &nbsp;|&nbsp;"
    " <span style='color: #0d6efd; font-weight: 700;'>GVHD:</span> TS. Hoàng Đức"
    " Chính",
    unsafe_allow_html=True,
)
st.divider()


# --- 5. BẢNG ĐIỀU KHIỂN & CÀI ĐẶT TRỰC QUAN ---
with st.container(border=True):
  st.markdown("### 🎛️ BẢNG ĐIỀU KHIỂN VẬN HÀNH & CÀI ĐẶT HỆ THỐNG (7 PHÂN HỆ)")
  
  c1, c2, c3 = st.columns(3)
  with c1:
    event_mode = st.checkbox("📡 Bật Chế độ Sự kiện (Tự động hóa DCV)", value=True)
  with c2:
    fire_alarm = st.checkbox("🚨 Giả lập Sự cố Khẩn cấp PCCC & Hút khói", value=False)
  with c3:
    grid_failure = st.checkbox("⚡ Giả lập Mất điện Lưới (Kích hoạt ATS)", value=False)

  st.markdown("---")
  s1, s2, s3 = st.columns(3)
  with s1:
    target_temp = st.slider("🌡️ Setpoint Nhiệt độ Khán đài (°C)", 20.0, 26.0, 23.0, 0.5)
  with s2:
    fan_speed_manual = st.slider("💨 Tần số VFD Quạt PAU/AHU (%)", 0, 100, 85 if event_mode else 30, 5)
  with s3:
    audience_count = st.slider("👥 Lưu lượng Khán giả thực tế", 0, 20000, 18450 if event_mode else 3500, 500)

st.markdown("<br>", unsafe_allow_html=True)


# --- 6. XỬ LÝ TRẠNG THÁI NGHIỆP VỤ & TÍNH TOÁN DỰA TRÊN THANH TRƯỢT ---
if fire_alarm:
  status_pccc = "BÁO CHÁY MỨC 1"
  pccc_desc = "🔴 NGUY HIỂM - ĐANG XẢ KHÓI & SƠ TÁN"
  co2_value = 380
  co2_delta = -570
  hvac_status = "**🔴 HVAC NGỪNG KHẨN CẤP**\n• Đã ngắt toàn bộ AHU/PAU.\n• Kích hoạt quạt hút khói & tăng áp."
  ats_status = "🔴 Chuyển nguồn Máy phát 1500 kVA (< 10s)"
  turnstile_status = "🔴 MỞ HOÀN TOÀN 16 CỔNG THOÁT HIỂM"
  total_power = 1200
  effective_aud = audience_count
elif grid_failure:
  status_pccc = "An toàn (Mất điện lưới)"
  pccc_desc = "⚡ ĐANG CHẠY MÁY PHÁT DỰ PHÒNG"
  effective_aud = audience_count
  co2_value = int(420 + (effective_aud / 20000) * 400)
  co2_delta = -100
  hvac_status = f"🟡 Chế độ Tiết kiệm máy phát.\n• Setpoint: {target_temp}°C."
  ats_status = "🔴 Đã chuyển sang Máy phát 1.500 kVA qua ATS"
  turnstile_status = f"🟢 Kiểm soát lối vào ({effective_aud:,} người)"
  total_power = int(700 + fan_speed_manual * 10)
else:
  effective_aud = audience_count
  status_pccc = "An toàn (Chế độ Sự kiện)" if event_mode else "An toàn (Normal Mode)"
  pccc_desc = f"🟢 ĐANG PHỤC VỤ {effective_aud:,} KHÁN GIẢ" if event_mode else "🔵 VẬN HÀNH TIÊU CHUẨN (TIẾT KIỆM)"
  
  co2_value = int(420 + (effective_aud / 20000) * 850)
  co2_delta = int((effective_aud / 20000) * 530)
  
  actual_room_temp = round(target_temp - (fan_speed_manual/100)*0.8, 1)
  hvac_status = f"**🟢 Thuật toán DCV đang chạy**\n• Nhiệt độ: {actual_room_temp}°C (Set: {target_temp}°C)\n• VFD Quạt PAU: {fan_speed_manual}%."
  
  ats_status = "🟢 Nguồn lưới chính ổn định (MSB)"
  turnstile_status = f"🟢 Kiểm soát lối vào ({effective_aud:,} người)"
  total_power = int(700 + (effective_aud / 20000) * 1300 + fan_speed_manual * 5)


# --- 7. HIỂN THỊ CÁC THÔNG SỐ CHÍNH (SCADA OVERVIEW CARDS) ---
st.subheader("📊 Màn hình Giám sát Trọng tâm (SCADA Overview)")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
  with st.container(border=True):
    st.markdown("**Trạng thái PCCC**")
    if fire_alarm or grid_failure:
      st.error(f"{status_pccc}\n\n*{pccc_desc}*")
    else:
      st.success(f"{status_pccc}\n\n*{pccc_desc}*")

with col2:
  with st.container(border=True):
    st.metric(label="Nồng độ CO2 Khán đài", value=f"{co2_value} ppm", delta=f"+{co2_delta} ppm" if co2_delta >=0 else f"{co2_delta} ppm")

with col3:
  with st.container(border=True):
    st.metric(label="Áp suất Bơm Sinh hoạt", value="3.5 bar", delta="Ổn định VFD")

with col4:
  with st.container(border=True):
    st.metric(label="Hệ số Công suất (cos φ)", value="0.95", delta="Đã bù 1.200 kVAr")

with col5:
  with st.container(border=True):
    st.metric(label="Tổng Công suất (Peak Load)", value=f"{total_power} kW", delta="Đỉnh 2.500 kW")

st.markdown("<br>", unsafe_allow_html=True)


# --- 8. PHÂN TÍCH BIẾN ĐỘNG & HVAC ---
col_left, col_right = st.columns([2, 1])

with col_left:
  with st.container(border=True):
    st.subheader("📈 Thuật toán Điều khiển Kín PI & Vòng DCV (CO2 Trend)")
    chart_data = get_mock_data(effective_aud, fan_speed_manual)
    
    chart_co2 = alt.Chart(chart_data).mark_area(opacity=0.6, interpolate='basis').encode(
        x=alt.X('Thời gian', sort=None, title='Trục thời gian mô phỏng'),
        y=alt.Y('Nồng độ CO2 (ppm)', title='Nồng độ CO2 (ppm)', scale=alt.Scale(domain=[350, 1600])),
        color=alt.condition(alt.datum['Nồng độ CO2 (ppm)'] > 1000, alt.value('#dc3545'), alt.value('#0d6efd'))
    ).properties(title='Phản ứng VFD Quạt PAU theo Biến động Nồng độ CO2 thực tế', height=260)

    chart_fan = alt.Chart(chart_data).mark_line(color='#ff9f43', strokeWidth=3, interpolate='basis').encode(
        x=alt.X('Thời gian', sort=None),
        y=alt.Y('Tần số Quạt (%)', scale=alt.Scale(domain=[0, 100])),
    )

    st.altair_chart(chart_co2 + chart_fan, use_container_width=True)

with col_right:
  with st.container(border=True):
    st.subheader("❄️ Phân hệ HVAC & Thông gió")
    st.info(hvac_status)
    if fire_alarm:
      st.error("⚠️ CẢNH BÁO: Kịch bản hút khói PCCC đang chiếm quyền điều khiển!")
    else:
      st.success("✅ Vòng điều khiển PI nồng độ CO2 đang bám sát Setpoint 1.000 ppm.")

st.markdown("<br>", unsafe_allow_html=True)


# --- 9. CHI TIẾT 7 PHÂN HỆ KỸ THUẬT ---
st.subheader("🛠️ Giám sát Chi tiết 7 Phân hệ Kỹ thuật (Full 7 Subsystems)")
col_a, col_b, col_c = st.columns([1, 1.1, 1])

with col_a:
  with st.container(border=True):
    st.markdown("### 1, 4 & 6. Điện, ATS & PCCC")
    st.write(f"• Trạng thái ATS: **{ats_status}**")
    st.write("• Máy phát dự phòng: **1.500 kVA (Sẵn sàng)**[cite: 17]")
    st.write("• Tủ MSB / Máy cắt ACB: **Đóng điện bình thường**")
    st.write("• Quạt hút khói & tăng áp: **Hoạt động tự động**")
    st.write(f"• Cửa Turnstile thoát hiểm: **{turnstile_status}**")

with col_b:
  with st.container(border=True):
    st.markdown("### 3 & 5. Cấp nước & Giám sát PMS")
    st.write("• Áp suất nước cấp: **3.5 bar (Chuẩn VFD)**[cite: 17]")
    st.write("• Bể ngầm / Bể mái: **Mức nước 85% (An toàn)**")
    st.write("• Tủ tụ bù 1.200 kVAr: **Đang đóng 5/6 cấp tự động**[cite: 17]")
    st.write("• Tổng công suất phản kháng Q: **Đã bù tối ưu**")
    st.markdown("<br>", unsafe_allow_html=True)
    
    vol_shift = int((total_power / 2500) * 3)
    volt_data = pd.DataFrame({
        'Pha': ['Pha A', 'Pha B', 'Pha C'],
        'Điện áp (V)': [230 - vol_shift, 228 - vol_shift, 232 - vol_shift]
    })
    base_volt = alt.Chart(volt_data).encode(
        x=alt.X('Pha', sort=None, title=''),
        y=alt.Y('Điện áp (V)', scale=alt.Scale(domain=[0, 270]))
    )
    bars_volt = base_volt.mark_bar(color='#0d6efd', width=24, cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
    text_volt = base_volt.mark_text(dy=-10, color='#111827', fontWeight='bold', fontSize=11).encode(text='Điện áp (V)')
    chart_volt = (bars_volt + text_volt).properties(title='Điện áp các pha MSB (V)', height=130)
    st.altair_chart(chart_volt, use_container_width=True)

with col_c:
  with st.container(border=True):
    st.markdown("### 2 & 7. Chiếu sáng DMX & An ninh")
    st.write("• Chiếu sáng sân đấu DMX512: **Kịch bản 1500 Lux**[cite: 17]")
    st.write("• Chiếu sáng khán đài DALI: **Hoạt động theo lịch**")
    st.write(f"• Lưu lượng qua cổng Turnstile: **{effective_aud:,} / 20.000**[cite: 17]")
    st.write("• Camera CCTV & Loa PA: **Đang trực tuyến**")
    
    fig_turnstile = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = effective_aud,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Tỷ lệ lấp đầy Sân (20k Chỗ)", 'font': {'color': '#111827', 'size': 13}},
        number = {'font': {'color': '#111827', 'size': 18}},
        gauge = {
            'axis': {'range': [0, 20000], 'tickfont': {'color': '#111827', 'size': 10}},
            'bar': {'color': "#0d6efd"},
            'steps': [
                {'range': [0, 10000], 'color': "#e9ecef"},
                {'range': [10000, 18000], 'color': "#ced4da"}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'value': 19000}
        }
    ))
    fig_turnstile.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=140, margin=dict(t=20, b=0, l=10, r=10))
    st.plotly_chart(fig_turnstile, use_container_width=True)

st.divider()
st.caption(
    "© 2026 - Đồ án Bài tập lớn Môn Hệ thống Quản lý Tòa nhà (BMS) | Đề tài số 13: Sân vận động 20.000 chỗ[cite: 17] | Trường Đại học Mở Hà Nội"
)