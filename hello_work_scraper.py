import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import random

st.set_page_config(page_title="ハローワーク求人抽出ツール", layout="wide")
st.title("📋 ハローワーク求人抽出ツール")
st.markdown("URLを1行ずつ貼り付けてください。求人情報を抽出して表示します。")

with st.form("job_form"):
    urls_input = st.text_area("🔗 求人URLを入力", height=200)
    submitted = st.form_submit_button("▶️ 情報を抽出")

# 求人概要の生成（箇条書き版）
def generate_summary(desc, salary_min, salary_max, loc, time, welfare, holiday, notes, job_title):
    lines = []

    # 職種
    if job_title:
        lines.append(f"・職種：{job_title}")

    # 仕事内容（短めに整形）
    if desc:
        desc_part = desc[:40] + "…" if len(desc) > 40 else desc
        lines.append(f"・仕事内容：{desc_part}")

    # 休日
    if holiday:
        lines.append(f"・休日：{holiday}")

    # 福利厚生（辞書的に抽出）
    benefit_keywords = []
    if any(kw in welfare + notes for kw in ["社宅", "住宅手当", "退職金"]):
        benefit_keywords.append("充実した福利厚生")
    if any(kw in welfare + notes for kw in ["資格取得", "研修", "キャリア"]):
        benefit_keywords.append("スキルアップ支援あり")
    if any(kw in welfare + notes for kw in ["育児", "扶養", "子育て"]):
        benefit_keywords.append("育児支援制度あり")
    if any(kw in welfare + notes + loc for kw in ["マイカー", "車通勤", "駐車場"]):
        benefit_keywords.append("マイカー通勤OK")
    if any(kw in welfare + notes for kw in ["通勤手当", "資格手当", "役職手当", "処遇改善手当", "夜勤手当"]):
        benefit_keywords.append("各種手当あり")
    match = re.search(r"年間休日\s*(\d{2,3})日", welfare + notes)
    if match:
        benefit_keywords.append(f"年間休日{match.group(1)}日")

    if benefit_keywords:
        lines.append(f"・福利厚生：{'、'.join(benefit_keywords)}")

    return "\n".join(lines) if lines else "求人情報は現在準備中です。お気軽にお問い合わせください。"

# おすすめポイント抽出の拡張（最低3件保証）
def extract_recommendations(salary_min, welfare, notes, work_desc, location):
    recs = []
    try:
        if salary_min and int(salary_min) >= 250000:
            recs.append("高給与（月給25万円以上）")
    except ValueError:
        pass
    if "レア" in work_desc or "久しぶり" in work_desc:
        recs.append("希少なレア求人")
    if any(kw in (welfare + notes) for kw in ["社宅", "資格", "退職金", "扶養", "住宅"]):
        recs.append("福利厚生が充実")
    if any(kw in (work_desc + notes) for kw in ["夜勤なし", "残業なし", "日勤のみ"]):
        recs.append("働きやすい勤務体制")
    if any(kw in (welfare + notes + location) for kw in ["駅", "マイカー", "車通勤", "バス"]):
        recs.append("アクセス良好")

    fallback = ["ブランクOK", "研修制度あり", "チームワーク重視", "地域密着型", "シフト柔軟対応"]
    while len(recs) < 3:
        extra = random.choice(fallback)
        if extra not in recs:
            recs.append(extra)
    return recs

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

                job_summary = generate_summary(work_desc, salary_min, salary_max, location, work_time, welfare, holiday, notes, job_title)
                recommendations = extract_recommendations(salary_min, welfare, notes, work_desc, location)

                with st.expander(f"📄 求人 {i}: {job_title}", expanded=False):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("🗂️ 求人抽出情報")
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
                        st.markdown(job_summary)

                        st.subheader("🎯 おすすめポイント")
                        if recommendations:
                            st.markdown("【おすすめポイント】 " + " ".join([f"■{r}" for r in recommendations]))
                        else:
                            st.markdown("【おすすめポイント】 該当情報なし")

            except Exception as e:
                st.error(f"求人 {i} の取得に失敗しました: {e}")
