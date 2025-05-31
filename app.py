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
    "是否傾向做與服飾配件相關的工作?"
]

# 每題對應的關鍵詞（用來從工作敘述中比對）
condition_keywords = [
    ["彈性"], ["排班"], ["駕照"], ["技術"], ["交際"], ["遠程"], ["晝夜顛倒"],
    ["寵物"], ["特殊技能"], ["餐飲"], ["表現"], ["福利"], ["地點便利"], ["效率要求"],
    ["實力薪資"], ["員工折扣"], ["室內"], ["孩子"], ["久站"], ["下廚"],
    ["音樂"], ["體育"], ["學科才藝"], ["語言才藝"], ["專業才藝"],
    ["銷售"], ["勞力"], ["制服"], ["服飾"]
]

# 每題權重（0.8～2.0，自由發揮設計）
question_weights = [
    1.2, 1.1, 0.8, 1.4, 1.0, 1.3, 1.0, 0.9, 1.2, 1.4,
    1.5, 1.2, 1.6, 2.0,  # 原14題
    1.5, 1.2, 1.3, 1.5, 1.1, 1.2,  # 新增條件
    1.3, 1.3, 1.4, 1.3, 1.5,
    1.4, 1.5, 1.1, 1.2
]

# 載入 jobs.csv
def load_jobs():
    jobs = []
    with open('jobs.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            jobs.append(row)
    return jobs

# 計算推薦加權分數
def calculate_score(answers, job):
    score = 0.0
    content = (job.get('條件限制') or '') + (job.get('備注') or '') + (job.get('時間要求') or '')

    for idx, answer in enumerate(answers):
        weight = question_weights[idx]
        keywords = condition_keywords[idx]
        ans = answer.strip().lower()
        point = 0

        # 效率問題（第14題，數值型）
        if idx == 13:
            try:
                user_limit = float(answer)
                job_limit = float(job.get('賺到一百萬時間(下限)', 999999))
                if job_limit <= user_limit:
                    point = 1
            except:
                continue
        # 否定偏好（如：不喜歡交際、不喜歡動物）
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
    return score

# 問卷開始
@app.route('/')
def index():
    session['answers'] = []
    return redirect(url_for('question', qid=0))

# 問卷頁
@app.route('/question/<int:qid>', methods=['GET', 'POST'])
def question(qid):
    if request.method == 'POST':
        answer = request.form['answer']
        session['answers'].append(answer)
        session.modified = True
        if qid + 1 < len(questions):
            return redirect(url_for('question', qid=qid + 1))
        else:
            return redirect(url_for('result'))
    return render_template('question.html', qid=qid, question=questions[qid], questions=questions)

# 結果頁
@app.route('/result')
def result():
    jobs = load_jobs()
    answers = session.get('answers', [])
    scored_jobs = []

    for job in jobs:
        score = calculate_score(answers, job)
        job['score'] = score
        scored_jobs.append(job)

    sorted_jobs = sorted(scored_jobs, key=lambda x: x['score'], reverse=True)
    return render_template('result.html', jobs=sorted_jobs[:5])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
