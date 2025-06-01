from flask import Flask, render_template, request, redirect, url_for, session
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 問卷問題
questions = [
    "時間是否要求為彈性?",
    "是否可接受排班或是完全彈性時間?",
    "是否具有駕照?",
    "是否具備專業技能?",
    "是否排斥與人交際?",
    "是否傾向遠程辦公?",
    "是否能接受晝夜顛倒?",
    "是否對寵物過敏?",
    "是否介意工作需學習一些特殊技能?",
    "傾向與餐飲業相關的工作?",
    "傾向依據額外表現獲得額外薪水?",
    "傾向有員工福利?",
    "希望離學校或家裡較方便的地方?",
    "希望能在多少小時內達成一百萬目標?",
    "是否傾向以自身實力決定薪資，而非固定薪水?",
    "是否傾向提供員工折扣?",
    "是否傾向室內工作?",
    "是否擅長與孩子相處?",
    "是否能夠久站?",
    "是否能夠接受要下廚的工作?",
    "是否具有音樂相關才藝?",
    "是否具有體育相關才藝?",
    "是否具有學科相關才藝?",
    "是否具有語言相關才藝?",
    "是否具有專業科目才藝(微積分/程式語言)?",
    "是否擅長進行銷售?",
    "是否能夠接受勞力工作?",
    "是否能夠接受需要穿著制服?",
    "是否傾向做與服飾配件相關的工作?",
    "你生活的地方在新竹以北嗎?"
]

condition_keywords = [
    ["彈性"], ["排班"], ["駕照"], ["技術"], ["交際"], ["遠程"], ["晝夜顛倒"],
    ["寵物"], ["特殊技能"], ["餐飲"], ["表現"], ["福利"], ["地點便利"], ["效率要求"],
    ["實力薪資"], ["員工折扣"], ["室內"], ["孩子"], ["久站"], ["下廚"],
    ["音樂"], ["體育"], ["學科才藝"], ["語言才藝"], ["專業才藝"],
    ["銷售"], ["勞力"], ["制服"], ["服飾"], ["地區"]
]

question_weights = [
    1.2, 1.1, 0.8, 1.4, 1.0, 1.3, 1.0, 0.9, 1.2, 1.4,
    1.5, 1.2, 1.6, 2.0, 1.5, 1.2, 1.3, 1.5, 1.1, 1.2,
    1.3, 1.3, 1.4, 1.3, 1.5, 1.4, 1.5, 1.1, 1.2, 1.0
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
    content = (job.get('條件限制') or '') + (job.get('備注') or '') + (job.get('時間要求') or '')

    for idx, answer in enumerate(answers):
        weight = question_weights[idx]
        keywords = condition_keywords[idx]
        ans = answer.strip().lower()
        point = 0

        if idx == 13:
            try:
                user_limit = float(answer)
                job_limit = float(job.get('賺到一百萬時間(下限)', 999999))
                if job_limit <= user_limit:
                    point = 1
            except:
                continue
        elif idx in [4, 7]:
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

    if region_answer == '是':
        if '貳樓' in job['工作']:
            score += 1.0
        elif '一風堂' in job['工作']:
            score += 1.5
        elif '寶雅' in job['工作']:
            score += 0.5
    else:
        if '貳樓' in job['工作']:
            score += 0.5
        elif '一風堂' in job['工作']:
            score += 1.0
        elif '寶雅' in job['工作']:
            score += 0.2

    if '瓦城' in job['工作']:
        try:
            if float(answers[13]) >= 40:
                score += 1.0
        except:
            pass

    return score

@app.route('/')
def index():
    return render_template('index.html', questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    answers = [request.form.get(f'q{i}') for i in range(len(questions))]
    jobs = load_jobs()

    region_answer = answers[29]  # 第30題為地區
    scored_jobs = []

    for job in jobs:
        score = calculate_score(answers, job, region_answer)
        scored_jobs.append((job, score))

    scored_jobs.sort(key=lambda x: x[1], reverse=True)
    top_jobs = scored_jobs[:5]  # 取前五名

    return render_template('results.html', jobs=top_jobs)

if __name__ == '__main__':
    app.run(debug=True)
