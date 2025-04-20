import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="ハローワーク求人抽出ツール", layout="wide")
st.title("📋 ハローワーク求人抽出ツール")
st.markdown("URLを1行ずつ貼り付けてください。求人情報を抽出して表示します。")

with st.form("job_form"):
    urls_input = st.text_area("🔗 求人URLを入力（1行に1件）", height=200)
    submitted = st.form_submit_button("▶️ 情報を抽出")

if submitted:
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

                job_title = soup.find("h2").get_text(strip=True) if soup.find("h2") else ""
                company = get_text("事業所名")
                work_desc = get_text("仕事の内容")
                location = get_text("就業場所")
                employment = get_text("雇用形態")
                salary = get_text("賃金")
                salary_type = get_text("賃金形態")
                work_time = get_text("就業時間")
                holiday = get_text("休日等")
                qualification = get_text("必要な免許・資格")
                experience = get_text("必要な経験等")
                welfare = get_text("加入保険等")
                notes = get_text("備考")

                salary_nums = re.findall(r"\d{3,5}", salary.replace(",", ""))
                salary_min = salary_nums[0] if len(salary_nums) >= 1 else ""
                salary_max = salary_nums[1] if len(salary_nums) >= 2 else salary_min

                # おすすめポイント生成
                keywords = []
                if "未経験" in work_desc + experience:
                    keywords.append("未経験歓迎")
                if "資格" in qualification:
                    keywords.append("資格取得支援あり")
                if "車" in welfare or "車" in notes:
                    keywords.append("マイカー通勤可能")

                # 求人概要生成
                summary_parts = []
                if job_title:
                    summary_parts.append(f"{job_title}の募集です。")
                if employment:
                    summary_parts.append(f"雇用形態は{employment}です。")
                if location:
                    summary_parts.append(f"勤務地は{location}です。")
                if work_desc:
                    summary_parts.append(f"主な仕事内容は「{work_desc[:30]}…」となります。")
                if salary_min and salary_max:
                    summary_parts.append(f"給与は月給{salary_min}円〜{salary_max}円です。")
                job_summary = " ".join(summary_parts)

                # 表示ブロック
                with st.expander(f"📄 求人 {i}: {job_title}"):
                    col1, col2 = st.columns([3, 2])

                    with col1:
                        st.subheader("📌 求人抽出情報")
                        st.markdown(f"""
                        **求人タイトル**: {job_title}  
                        **会社名**: {company}  
                        **仕事内容**: {work_desc}  
                        **就業場所**: {location}  
                        **雇用形態**: {employment}  
                        **給与**: {salary}  
                        **賃金形態**: {salary_type}  
                        **給与下限**: {salary_min}  
                        **給与上限**: {salary_max}  
                        **勤務時間**: {work_time}  
                        **休日・休暇**: {holiday}  
                        **必須資格**: {qualification}  
                        **経験要否**: {experience}  
                        **福利厚生**: {welfare}  
                        **備考**: {notes}  
                        """)

                    with col2:
                        st.subheader("✨ 求人概要")
                        st.markdown(job_summary if job_summary else "概要情報が見つかりませんでした。")

                        st.subheader("🎯 おすすめポイント")
                        if keywords:
                            st.markdown(" ".join(f"◾️{kw}" for kw in keywords))
                        else:
                            st.markdown("該当情報なし")

            except Exception as e:
                st.error(f"求人 {i} の取得に失敗しました: {e}")
