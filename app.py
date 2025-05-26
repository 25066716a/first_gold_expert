from flask import Flask, render_template, request, redirect, url_for, session
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 讀取工作資料
def load_jobs():
    jobs = []
    with open('jobs.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            jobs.append(row)
    return jobs

# 篩選問題清單
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
    "希望能在多少小時內達成一百萬目標?"
]

# 問題對應的特徵鍵值（與 jobs.csv 對應邏輯）
question_keys = [
    "彈性時間", "可接受排班", "駕照", "專業技能", "排斥交際", "遠程辦公", "晝夜顛倒",
    "寵物過敏", "特殊技能", "餐飲業", "表現加薪", "員工福利", "地點便利", "效率要求"
]

# 每個回答的分數轉換方式
def calculate_score(answers, job):
    score = 0
    for idx, answer in enumerate(answers):
        key = question_keys[idx]
        # 簡單匹配文字與備註欄、條件限制、時間要求的內容
        content = job['條件限制'] + job['備注'] + job['時間要求']
        if answer == 'yes' and key in content:
            score += 1
        elif answer == 'no' and key not in content:
            score += 1
        elif key == "效率要求":
            try:
                min_hour = float(job['賺到一百萬時間(下限)'])
                target = float(answer)
                if min_hour <= target:
                    score += 1
            except:
                pass
    return score

@app.route('/')
def index():
    session['answers'] = []
    return redirect(url_for('question', qid=0))

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
    return render_template(
    'question.html',
    qid=qid,
    question=questions[qid],
    questions=questions  # 這一行是關鍵
)


@app.route('/result')
def result():
    jobs = load_jobs()
    answers = session.get('answers', [])
    scored_jobs = []
    for job in jobs:
        score = calculate_score(answers, job)
        job['score'] = score
        scored_jobs.append(job)
    # 根據分數排序
    scored_jobs.sort(key=lambda x: x['score'], reverse=True)
    return render_template('result.html', jobs=scored_jobs[:5])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
