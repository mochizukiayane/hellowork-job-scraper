import streamlit as st
import requests
from bs4 import BeautifulSoup

# スクレイピング処理
def scrape_hellowork(url):
    try:
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')

        data = {}
        # 各項目の抽出
        labels = soup.select('.kyujin_detail_label')
        values = soup.select('.kyujin_detail_value')

        for label, value in zip(labels, values):
            key = label.get_text(strip=True).replace('\u3000', '')
            val = value.get_text(strip=True).replace('\u3000', '')
            data[key] = val

        # 項目の整理（必要なものだけ抽出）
        extracted = {
            "職種": data.get("職種", ""),
            "仕事内容": data.get("仕事の内容", ""),
            "勤務地": data.get("就業場所", ""),
            "勤務時間": data.get("就業時間", ""),
            "勤務日数": data.get("週所定労働日数", ""),
            "通勤手段": data.get("マイカー通勤", ""),
            "特記事項": data.get("特記事項", "")
        }

        return extracted

    except Exception as e:
        st.error(f"スクレイピング中にエラーが発生しました: {e}")
        return {}

# おすすめポイント生成
def generate_recommend_points(data: dict) -> list:
    points = []

    if "日勤" in data.get("勤務時間", ""):
        points.append("◾️日勤のみで働きやすい勤務時間")

    if "マイカー" in data.get("通勤手段", "") or "車通勤" in data.get("特記事項", ""):
        points.append("◾️マイカー通勤OKで通勤便利")

    if "週3" in data.get("勤務日数", "") or "パート" in data.get("勤務日数", ""):
        points.append("◾️週3日から勤務可能")

    return points

# 求人概要生成
def generate_job_summary(data: dict) -> str:
    location = data.get("勤務地", "").replace("（", "").replace("）", "")
    job_type = data.get("職種", "介護職")
    work_time = data.get("勤務時間", "")
    work_days = data.get("勤務日数", "")
    commute = data.get("通勤手段", "") + data.get("特記事項", "")

    summary_parts = []
    if location:
        summary_parts.append(f"{location}にある")
    summary_parts.append(f"{job_type}の求人です。")

    if "日勤" in work_time:
        summary_parts.append("日勤のみの勤務で、")
    elif "夜勤" in work_time:
        summary_parts.append("夜勤を含むシフト勤務で、")

    if "週3" in work_days or "パート" in work_days:
        summary_parts.append("週3日から勤務可能。")

    if "マイカー" in commute or "車通勤" in commute:
        summary_parts.append("マイカー通勤も可能で通勤しやすい環境です。")

    return "".join(summary_parts)

# Streamlit UI
st.set_page_config(page_title="ハローワーク求人スクレイパー", layout="centered")

st.title("ハローワーク求人スクレイパー")
st.markdown("ハローワークの求人詳細URLを入力してください。")

url = st.text_input("求人ページのURL", placeholder="https://www.hellowork.mhlw.go.jp/kensaku/...")

if url:
    with st.spinner("情報を取得中..."):
        result = scrape_hellowork(url)

    if result:
        st.success("情報の取得が完了しました！")

        st.markdown("## 【抽出項目一覧】")
        for key, val in result.items():
            st.write(f"**{key}**: {val}")

        st.markdown("## 【おすすめポイント】")
        recommend_points = generate_recommend_points(result)
        for point in recommend_points:
            st.markdown(point)

        st.markdown("## 【求人概要】")
        job_summary = generate_job_summary(result)
        st.markdown(job_summary)
