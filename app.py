import streamlit as st
import pandas as pd
import plotly.express as px

# 设置网页标题
st.set_page_config(page_title="物流时效监控系统", layout="wide")
st.title("🚚 物流全链路时效看板")

# 1. 文件上传
uploaded_file = st.file_uploader("请上传物流时效 CSV 或 Excel 文件", type=["csv", "xlsx"])

if uploaded_file:
    # 加载数据
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # 2. 核心计算逻辑
    date_cols = ['下单日期', '送仓日期', '实际开船日期', '实际到港日期', '卡派时间', '海外仓到货时间']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    # 计算各阶段天数 (如果没有预设值则自动计算)
    df['等待开船'] = (df['实际开船日期'] - df['送仓日期']).dt.days
    df['头程运输'] = (df['实际到港日期'] - df['实际开船日期']).dt.days
    df['到港转换'] = (df['卡派时间'] - df['实际到港日期']).dt.days
    df['尾程派送'] = (df['海外仓到货时间'] - df['卡派时间']).dt.days
    df['总时效'] = (df['海外仓到货时间'] - df['下单日期']).dt.days

    # 3. 数据展示
    st.subheader("📊 物流时效明细")
    st.dataframe(df[['物流商单号', '服务商', '物流渠道', '等待开船', '头程运输', '到港转换', '尾程派送', '总时效']])

    # 4. 可视化图表生成
    st.subheader("📈 全链路阶段耗时分析 (堆叠条形图)")
    
    # 准备画图数据
    plot_df = df.dropna(subset=['等待开船', '头程运输', '到港转换', '尾程派送'])
    fig = px.bar(plot_df, 
                 x="物流商单号", 
                 y=["等待开船", "头程运输", "到港转换", "尾程派送"],
                 title="单票订单各阶段耗时分布",
                 labels={"value": "天数", "variable": "物流阶段"},
                 barmode="stack")
    st.plotly_chart(fig, use_container_width=True)

    # 5. 服务商时效对比
    st.subheader("对比各服务商平均时效")
    avg_df = df.groupby('服务商')['总时效'].mean().reset_index()
    fig2 = px.bar(avg_df, x='服务商', y='总时效', color='服务商', text_auto=True)
    st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("💡 请先在上方上传您的物流表格进行分析。")