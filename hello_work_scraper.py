import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="ハローワーク求人抽出ツール", layout="wide")
st.title("📋 ハローワーク求人抽出ツール")
st.markdown("URLを1行ずつ貼り付けてください。求人情報を抽出して表示します。")

urls_input = st.text_area("🔗 求人URLを入力", height=200)

# 求人概要生成関数
def generate_summary(data):
    parts = []
    if data.get("location"):
        parts.append(f"{data['location']}にある")
    parts.append(f"{data.get('job_title', '介護職')}の求人です。")

    if "日勤" in data.get("work_time", ""):
        parts.append("日勤のみの勤務で、")
    elif "夜勤" in data.get("work_time", ""):
        parts.append("夜勤を含むシフト勤務で、")

    if "週3" in data.get("holiday", "") or "パート" in data.get("employment", ""):
        parts.append("週3日から勤務可能。")

    if "車" in data.get("welfare", ""):
        parts.append("マイカー通勤も可能で通勤しやすい環境です。")

    return "".join(parts)

# おすすめポイント生成関数
def generate_points(data):
    points = []
    if "未経験" in data.get("work_desc", "") + data.get("experience", ""):
        points.append("◾️未経験歓迎")
    if "資格" in data.get("qualification", ""):
        points.append("◾️資格取得支援あり")
    if "車" in data.get("welfare", ""):
        points.append("◾️マイカー通勤可能")
    if "日勤" in data.get("work_time", ""):
        points.append("◾️日勤のみで生活リズムが整いやすい")
    return points

if st.button("▶️ 情報を抽出"):
    urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
    if not urls:
        st.warning("URLを1件以上入力してください。")
    else:
        for i, url in enumerate(urls, 1):
            try:
                response = requests.get(url)
                response.encoding = response.apparent_encoding
                soup = BeautifulSoup(response.text, 'html.parser')

                def get_text(label):
                    elem = soup.find("th", string=label)
                    if elem and elem.find_next("td"):
                        return elem.find_next("td").get_text(strip=True)
                    return ""

                data = {
                    "job_title": soup.find("h2").get_text(strip=True) if soup.find("h2") else "",
                    "company": get_text("事業所名"),
                    "work_desc": get_text("仕事の内容"),
                    "location": get_text("就業場所"),
                    "employment": get_text("雇用形態"),
                    "salary": get_text("賃金"),
                    "salary_type": get_text("賃金形態"),
                    "work_time": get_text("就業時間"),
                    "holiday": get_text("休日等"),
                    "qualification": get_text("必要な免許・資格"),
                    "experience": get_text("必要な経験等"),
                    "welfare": get_text("加入保険等"),
                    "notes": get_text("備考")
                }

                salary_nums = re.findall(r"\d{3,5}", data["salary"].replace(",", ""))
                data["salary_min"] = salary_nums[0] if len(salary_nums) >= 1 else ""
                data["salary_max"] = salary_nums[1] if len(salary_nums) >= 2 else data["salary_min"]

                with st.expander(f"📄 求人 {i}: {data['job_title']}"):
                    st.markdown("### ✅ 求人概要")
                    st.markdown(generate_summary(data))

                    st.markdown("### ⭐️ おすすめポイント")
                    for point in generate_points(data):
                        st.markdown(point)

                    st.markdown("### 📌 抽出情報")
                    st.markdown(f"""
                    **会社名**: {data['company']}  
                    **仕事内容**: {data['work_desc']}  
                    **就業場所**: {data['location']}  
                    **雇用形態**: {data['employment']}  
                    **給与**: {data['salary']}  
                    **賃金形態**: {data['salary_type']}  
                    **給与下限**: {data['salary_min']}  
                    **給与上限**: {data['salary_max']}  
                    **勤務時間**: {data['work_time']}  
                    **休日・休暇**: {data['holiday']}  
                    **必須資格**: {data['qualification']}  
                    **経験要否**: {data['experience']}  
                    **福利厚生**: {data['welfare']}  
                    **備考**: {data['notes']}  
                    """)
            except Exception as e:
                st.error(f"求人 {i} の取得に失敗しました: {e}")
