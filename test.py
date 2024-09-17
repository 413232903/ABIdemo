import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from vanna.remote import VannaDefault
import requests
import json
import time

# 设置页面配置
st.set_page_config(page_title="AI数据分析助手", layout="wide")

# 自定义CSS来美化页面
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans SC', sans-serif;
    }
    
    .main {
        padding: 2rem 3rem;
        background-color: #f8fafc;
    }
    
    .block-container {
        max-width: 1200px !important;
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: white;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    h1 {
        color: #1e3a8a;
        text-align: center;
        padding: 1.5rem 1rem;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 25%, #1d4ed8 50%, #1d4ed8 75%, #1e3a8a 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
        position: relative;
        overflow: hidden;
    }
    
    h1::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            to bottom right,
            rgba(255, 255, 255, 0.3) 0%,
            rgba(255, 255, 255, 0.1) 50%,
            transparent 50%
        );
        transform: rotate(30deg);
        animation: shine 3s infinite linear;
    }
    
    h1 span {
        position: relative;
        z-index: 1;
        background: linear-gradient(90deg, #ffffff, #f0f9ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
    }
    
    @keyframes shine {
        0% {
            top: -50%;
            left: -50%;
        }
        100% {
            top: 150%;
            left: 150%;
        }
    }
    
    h3 {
        color: #2563eb;
        border-left: 5px solid #2563eb;
        padding-left: 10px;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        background-color: #2563eb;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #1e40af;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .dataframe {
        border: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-radius: 10px;
        font-size: 0.9em;
    }
    
    .stPlotlyChart {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stDataFrame, .stTable {
        margin: 0 auto;
    }
    
    .centered-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    
    .dataframe {
        margin: 0 auto;
        border-collapse: separate;
        border-spacing: 0;
        text-align: center;
    }
    
    .dataframe th, .dataframe td {
        padding: 10px;
        border: 1px solid #e5e7eb;
    }
    
    .dataframe th {
        background-color: #f3f4f6;
        font-weight: bold;
        color: #1e3a8a;
    }
    
    .dataframe tr:nth-child(even) {
        background-color: #f9fafb;
    }
</style>
""", unsafe_allow_html=True)

# 创建侧边栏
st.sidebar.title("功能选择")
selected_function = st.sidebar.radio("选择功能", ["报表检索", "AI数据分析助手"])

if selected_function == "报表检索":
    st.markdown("<h1><span>报表检索</span></h1>", unsafe_allow_html=True)
    
    # 添加对话框
    user_query = st.text_input("请输入您的报表检索问题：")
    
    if user_query:
        url = 'http://15.204.101.64:4000/v1/chat/completions'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'sk-1KmuS4WYgzK7314XA64dB74c56C347F1AdD19872AdF62d76'
        }
        data = {
            "model": "gpt-4-turbo",
            "messages": [{"role": "user", "content": user_query}],
            "stream": False
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=data, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        ai_response = result['choices'][0]['message']['content']
                        if ai_response.startswith('http://') or ai_response.startswith('https://'):
                            st.success("AI已生成报表URL")
                            st.markdown(f"[点击查看报表]({ai_response})")
                            
                            # 显示报表
                            st.subheader("报表展示")
                            st.components.v1.iframe(ai_response, height=600, scrolling=True)
                        else:
                            st.warning("AI未能生成有效的报表URL。以下是AI的回复：")
                            st.write(ai_response)
                    else:
                        st.error("AI响应格式不正确，请稍后重试。")
                    break
                else:
                    st.error(f"请求失败，状态码：{response.status_code}")
            except Exception as e:
                if attempt < max_retries - 1:
                    st.warning(f"请求失败，3秒后重试（尝试 {attempt + 2}/{max_retries}）")
                    time.sleep(3)
                else:
                    st.error(f"多次尝试后仍然失败，请稍后重试。错误信息：{str(e)}")

elif selected_function == "AI数据分析助手":
    # 标题
    st.markdown("<h1><span>AI数据分析助手</span></h1>", unsafe_allow_html=True)

    st.subheader("数据分析")
    user_question = st.text_input("请输入您的数据分析问题：")

    # 初始化Vanna
    vn = VannaDefault(model='chinook', api_key='e079afa307f449af98681bf802688b88')
    vn.connect_to_sqlite('https://vanna.ai/Chinook.sqlite')

    if user_question:
        try:
            # 获取生成的SQL查询
            sql = vn.generate_sql(user_question)
            st.subheader("生成的SQL查询")
            st.code(sql, language="sql")

            # 执行SQL查询
            result = vn.run_sql(sql)
            
            if isinstance(result, pd.DataFrame) and not result.empty:
                data = result
                st.subheader("查询结果数据")
                st.dataframe(data, use_container_width=True)

                csv = data.to_csv(index=False)
                st.download_button(
                    label="下载查询结果数据为CSV",
                    data=csv,
                    file_name="query_result.csv",
                    mime="text/csv",
                )

                # 数据可视化
                st.subheader("数据可视化")

                # 使用 st.form 来防止自动重新运行
                with st.form("visualization_form"):
                    # 选择要可视化的列
                    all_columns = data.columns.tolist()
                    numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()

                    x_column = st.selectbox("选择X轴数据", all_columns)
                    y_columns = [col for col in all_columns if col != x_column]
                    y_column = st.selectbox("选择Y轴数据", y_columns)

                    chart_type = st.selectbox("选择图表类型", ["折线图", "柱状图", "散点图"])

                    # 添加生成图表按钮
                    submit_button = st.form_submit_button("生成图表")

                if submit_button:
                    # 确保使用最新的数据
                    current_data = data.copy()
                    
                    # 处理非数值类型的列，但保持原始值
                    if x_column not in numeric_columns:
                        x_values = current_data[x_column]
                    else:
                        x_values = current_data[x_column]

                    if y_column not in numeric_columns:
                        y_values = current_data[y_column]
                    else:
                        y_values = current_data[y_column]

                    if chart_type == "折线图":
                        fig = px.line(x=x_values, y=y_values, title=f"{y_column}与{x_column}的关系")
                    elif chart_type == "柱状图":
                        fig = px.bar(x=x_values, y=y_values, title=f"{y_column}与{x_column}的关系")
                    elif chart_type == "散点图":
                        fig = px.scatter(x=x_values, y=y_values, title=f"{y_column}与{x_column}的关系",
                                         trendline="ols", trendline_color_override="red")

                    fig.update_layout(
                        font=dict(family="Noto Sans SC"),
                        title_font_size=20,
                        title_x=0.5,
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        xaxis_title=x_column,
                        yaxis_title=y_column
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # 数据统计
                st.subheader("数据统计")
                stats_df = data.describe().reset_index()
                st.table(stats_df)

                # 结果摘要
                st.subheader("结果摘要")
                st.write(f"查询返回了 {len(data)} 行数据，包含以下列：{', '.join(data.columns)}")
            elif isinstance(result, pd.DataFrame) and result.empty:
                st.warning("查询结果为空DataFrame。请尝试其他问题。")
            else:
                st.subheader("查询结果")
                st.write(result)  # 直接显示非DataFrame格式的结果
                st.subheader("结果摘要")
                st.write("查询未返回表格数据。")

        except Exception as e:
            st.error(f"处理问题时出错：{str(e)}")
            st.error("错误详情：")
            st.exception(e)
    else:
        st.info("请输入一个数据分析问题来开始。")