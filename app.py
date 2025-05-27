from flask import Flask, render_template, request, redirect, url_for, session
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 問題清單
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

# 對應條件關鍵字
condition_keywords = [
    "彈性", "排班", "駕照", "技術", "交際", "遠程", "晝夜顛倒",
    "寵物", "特殊技能", "餐飲", "表現", "福利", "地點便利", "效率要求"
]

# 讀取 CSV
def load_jobs():
    jobs = []
    with open('jobs.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            jobs.append(row)
    return jobs

# 計算推薦分數
def calculate_score(answers, job):
    score = 0
    content = (job.get('條件限制') or '') + (job.get('備注') or '') + (job.get('時間要求') or '')
    
    for idx, answer in enumerate(answers):
        key = condition_keywords[idx]
        # 第 14 題是數字輸入（效率要求）
        if key == "效率要求":
            try:
                limit = float(job.get('賺到一百萬時間(下限)', 999999))
                target = float(answer)
                if limit <= target:
                    score += 1
            except:
                continue
        else:
            if answer == "yes" and key in content:
                score += 1
            elif answer == "no" and key not in content:
                score += 1
    return score

# 問卷開始
@app.route('/')
def index():
    session['answers'] = []
    return redirect(url_for('question', qid=0))

# 顯示問題
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

# 顯示結果
@app.route('/result')
def result():
    jobs = load_jobs()
    answers = session.get('answers', [])
    scored_jobs = []

    for job in jobs:
        score = calculate_score(answers, job)
        job['score'] = score
        scored_jobs.append(job)

    # 排序取前五
    sorted_jobs = sorted(scored_jobs, key=lambda x: x['score'], reverse=True)
    return render_template('result.html', jobs=sorted_jobs[:5])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
