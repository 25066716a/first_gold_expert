from flask import Flask, render_template, request, redirect, url_for, session
import csv
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 問卷問題
questions = [
    "是否能接受排班（否則傾向彈性時間）？",
    "是否具有駕照？",
    "是否排斥與人交際？",
    "是否傾向遠程辦公？",
    "是否能接受晝夜顛倒？",
    "是否對寵物過敏？",
    "是否介意工作需學習一些特殊技能？",
    "傾向與餐飲業相關的工作？",
    "傾向依據額外表現獲得額外薪水？",
    "傾向有員工福利？",
    "希望離學校或家裡較方便的地方？",
    "希望能在多少小時內達成一百萬目標？",
    "是否傾向以自身實力決定薪資，而非固定薪水？",
    "是否傾向提供員工折扣？",
    "是否傾向室內工作？",
    "是否擅長與孩子相處？",
    "是否能夠久站？",
    "是否能夠接受要下廚的工作？",
    "是否具有音樂相關才藝？",
    "是否具有體育相關才藝？",
    "是否具有學科相關才藝？",
    "是否具有語言相關才藝？",
    "是否具有專業科目才藝（微積分/程式語言）？",
    "是否擅長進行銷售？",
    "是否能夠接受勞力工作？",
    "是否能夠接受需要穿著制服？",
    "是否傾向做與服飾配件相關的工作？",
    "你生活的地方在新竹以北嗎？",
    "是否具有舞蹈相關才能？"
]

condition_keywords = [
    ["排班"], ["駕照"], ["交際"], ["遠程"], ["晝夜顛倒"],
    ["寵物"], ["特殊技能"], ["餐飲"], ["表現"], ["福利"],
    ["地點便利"], ["效率要求"], ["實力薪資"], ["員工折扣"], ["室內"],
    ["孩子"], ["久站"], ["下廚"], ["音樂"], ["體育"],
    ["學科才藝"], ["語言才藝"], ["專業才藝"], ["銷售"], ["勞力"],
    ["制服"], ["服飾"], ["地區"], ["舞蹈"]
]

question_weights = [
    1.2, 0.8, 1.0, 1.3, 1.0, 0.9, 1.2, 1.4,
    1.5, 1.2, 1.6, 2.0, 1.5, 1.2, 1.3, 1.5,
    1.1, 1.2, 1.3, 1.3, 1.4, 1.3, 1.5, 1.4,
    1.5, 1.1, 1.2, 1.0, 1.3
]

def load_jobs():
    jobs = []
    with open('jobs.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            jobs.append(row)
    return jobs

def calculate_score(answers, job, region_answer):
    score = 0.0
    content = (job.get('條件限制') or '') + (job.get('備注') or '') + (job.get('時間要求') or '') + job.get('工作', '')

    # 強制排除條件
    exclusion_rules = {
        1: ["駕照", "外送", "Uber", "熊貓"],       # 沒駕照 → 排除這些
        18: ["鋼琴", "吉他"],                     # 沒音樂才藝 → 排除音樂職位
        28: ["舞蹈"],                             # 沒舞蹈才藝 → 排除舞蹈職位
        19: ["體育", "羽球", "游泳"],              # 沒體育才藝
        20: ["家教", "數學", "理化", "學科"],       # 沒學科才藝
        21: ["英文", "日文", "韓文", "語言"],       # 沒語言才藝
        22: ["程式", "微積分", "專業科目"]          # 沒專業才藝
    }

    for idx, keywords in exclusion_rules.items():
        if answers[idx].strip().lower() == 'no':
            if any(k.lower() in content.lower() for k in keywords):
                return 0.0  # 硬性排除職缺

    # 正常加分流程
    for idx, answer in enumerate(answers):
        weight = question_weights[idx]
        keywords = condition_keywords[idx]
        ans = answer.strip().lower()
        point = 0

        if idx == 11:  # 賺百萬時間
            try:
                user_limit = float(answer)
                job_limit = float(job.get('賺到一百萬時間(下限)', 999999))
                if job_limit <= user_limit:
                    point = 1
            except:
                continue
        elif idx in [2, 5]:
            if ans == 'no' and not any(k in content for k in keywords):
                point = 1
            elif ans == 'yes' and any(k in content for k in keywords):
                point = 1
        else:
            if ans == 'yes' and any(k in content for k in keywords):
                point = 1
            elif ans == 'no' and not any(k in content for k in keywords):
                point = 1

        score += weight * point

    # 區域加分
    job_name = job['工作']
    base_name = re.sub(r"\(.*?\)", "", job_name)
    if not re.search(r"\((南部|北部|台南|台北|高雄|新北|台中|桃園)\)", job_name):
        if '貳樓' in base_name:
            score += 1.0 if region_answer == '是' else 0.5
        elif '一風堂' in base_name:
            score += 1.5 if region_answer == '是' else 1.0
        elif '寶雅' in base_name:
            score += 0.5 if region_answer == '是' else 0.2

    # 工時相關加分
    try:
        work_hours = float(answers[11])
        if job_name.strip() == '瓦城(外場服務員)' and work_hours >= 40:
            score += 1.0
        elif job_name.strip() in ['一風堂(台南)', '一風堂(北部)']:
            if work_hours >= 140:
                score += 1.0
            elif work_hours >= 120:
                score += 0.5
    except:
        pass

    job['搜尋連結'] = f"https://www.104.com.tw/jobs/search/?keyword={job_name}"
    return round(score, 2)

@app.route('/')
def index():
    session.clear()
    session['answers'] = []
    return redirect(url_for('question', idx=0))

@app.route('/question/<int:idx>', methods=['GET', 'POST'])
def question(idx):
    if request.method == 'POST':
        answer = request.form.get('answer')
        if answer is None:
            return redirect(url_for('question', idx=idx))

        answers = session.get('answers', [])
        answers.append(answer)
        session['answers'] = answers

        if idx + 1 < len(questions):
            return redirect(url_for('question', idx=idx + 1))
        else:
            return redirect(url_for('submit'))

    progress = int((idx / len(questions)) * 100)
    return render_template('question.html', idx=idx, question=questions[idx], questions=questions, progress=progress)

@app.route('/submit', methods=['GET'])
def submit():
    answers = session.get('answers', [])
    jobs = load_jobs()

    region_answer = answers[27] if len(answers) > 27 else '否'
    scored_jobs = []

    for job in jobs:
        score = calculate_score(answers, job, region_answer)
        scored_jobs.append((job, score))

    scored_jobs.sort(key=lambda x: x[1], reverse=True)
    top_jobs = scored_jobs[:5]

    return render_template('results.html', jobs=top_jobs)

if __name__ == '__main__':
    app.run(debug=True)


