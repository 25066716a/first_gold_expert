from flask import Flask, render_template, request, redirect, url_for, session
import csv
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 問卷問題
questions = [
    "是否能接受排班（選否 則傾向彈性時間）？",
    "是否具有駕照？",
    "是否排斥與人交際？",
    "是否傾向遠程辦公？",
    "是否能接受晝夜顛倒？",
    "是否對寵物過敏？",
    "是否介意工作需學習一些特殊技能？",
    "傾向與餐飲業相關的工作？",
    "傾向依據額外表現獲得額外薪水？",
    "傾向有提供員工福利？",
    "希望離學校或家裡較方便的地方？",
    "希望能在多少小時內達成一百萬目標？",
    "是否傾向以自身實力決定薪資，而非固定薪水？",
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
    "是否具有藝術相關才能（美術/舞蹈）？"
]

condition_keywords = [
    ["排班"], ["駕照"], ["交際"], ["遠程"], ["晝夜顛倒"],
    ["寵物"], ["特殊技能"], ["餐飲"], ["表現"], ["福利", "折扣"],
    ["地點便利"], ["效率要求"], ["實力薪資"], ["室內"],
    ["孩子"], ["久站"], ["下廚"], ["音樂"], ["體育"],
    ["學科才藝"], ["語言才藝"], ["專業才藝"], ["銷售"], ["勞力"],
    ["制服"], ["服飾"], ["地區"], ["藝術"]
]

question_weights = [
    1.2, 0.8, 1.0, 1.3, 1.0, 0.9, 1.2, 1.4,
    1.5, 1.2, 1.6, 2.0, 1.5, 1.3, 1.5,
    1.1, 1.2, 1.3, 1.3, 1.4, 1.3, 1.5,
    1.4, 1.5, 1.1, 1.2, 1.0, 1.3
]

def load_jobs():
    jobs = []
    with open('jobs.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            jobs.append(row)
    return jobs
job_question_mapping = {
    "7-11(非大夜)": [0, -2, -4, -6, 7, 9, 10, -12, 13, 15, 23, 24],
    "7-11(大夜)": [0, -2, 4, -6, 7, 9, 10, -12, 13, 15, 23, 24],
    "ok mart": [0, -2, -4, -6, 7, 9, 10, -12, 13, 15, 23, 24],
    "ok mart(晚班)": [0, -2, 4, -6, 7, 9, 10, -12, 13, 15, 23, 24],
    "麥當勞": [0, 1, -2, -4, -6, 7, 8, 9, 10, -12, 13, 24],
    "肯德基": [0, 1, -2, -4, -6, 7, 8, 9, 10, -12, 13, 24],
    "達美樂": [0, 1, -2, -4, -6, 7, 8, 9, 10, -12, 13, 24],
    "必勝客": [0, 1, -2, -4, -6, 7, 8, 9, 10, -12, 13, 24],
    "麥當勞(半夜後)": [0, 1, -2, 4, -6, 7, 8, 9, 10, -12, 13, 24],
    "爭鮮": [0, -2, -4, -6, 7, 9, 10, -12, 13, 15, 16, 23, 24],
    "八方雲集": [0, -2, -4, -6, 7, 9, 10, -12, 13, 15, 16, 23, 24],
    "四海遊龍": [0, -2, -4, -6, 7, 9, 10, -12, 13, 15, 16, 23, 24],
    "星巴克": [0, -2, -4, -6, 7, 9, 10, -12, 13, 15, 16, 23, 24],
    "路易莎": [0, -2, -4, -6, 7, 9, 10, -12, 13, 15, 16, 23, 24],
    "早安美之城": [0, -2, -4, -6, 7, 9, 10, -12, 13, 15, 16, 23, 24],
    "永和豆漿大王": [0, -2, -4, -6, 7, 9, 10, -12, 13, 15, 16, 23, 24],
    "拿坡里": [0, -2, -4, -6, 7, 9, -10, -12, 13, 15, -16, 23, 24],
    "三商巧福": [0, -2, -4, -6, 7, 9, -10, -12, 13, 15, -16, 23, 24],
    "福聖亭": [0, -2, -4, -6, 7, 9, -10, -12, 13, 15, -16, 23, 24],
    "饗食天堂": [0, -2, -4, -6, 7, 9, -10, -12, 13, 15, -16, 23, 24],
    "果然匯": [0, -2, -4, -6, 7, 9, -10, -12, 13, 15, -16, 23, 24],
    "陶板屋": [0, -2, -4, -6, 7, 9, -10, -12, 13, 15, -16, 23, 24],
    "石二鍋": [0, -2, -4, -6, 7, 9, -10, -12, 13, 15, -16, 23, 24],
    "西堤": [0, -2, -4, -6, 7, 9, -10, -12, 13, 15, -16, 23, 24],
    "酷聖石": [0, -2, -4, -6, 7, 9, -10, -12, 13, 15, -16, 23, 24],
    "mister donut": [0, -2, -4, -6, 7, 9, -10, -12, 13, 15, -16, 23, 24],
    "哈根達斯": [0, -2, -4, -6, 7, 9, -10, -12, 13, 15, -16, 23, 24],
    "乾杯": [0, -2, -4, -6, 7, 9, -10, -12, 13, 15, -16, 23, 24],
    "貳樓": [0, -2, -4, -6, 7, 9, -10, -12, 13, 15, -16, 23, 24],
    "新馬辣": [0, -2, -4, -6, 7, 9, -10, -12, 13, 15, -16, 23, 24],
    "海底撈": [0, -2, -4, -6, 7, 9, -10, -12, 13, 15, -16, 23, 24],
    "瓦城 外場服務員": [0, -2, -4, -6, 7, 9, -10, -12, 13, 15, -16, 23, 24],
    "鼎泰豐 餐飲人員": [0, -2, -4, -6, 7, 9, -10, -12, 13, 15, -16, 23, 24],
    "50嵐": [0, -2, -4, -6, 7, 9, 10, -12, 13, 15, -16, 23, 24],
    "茶湯會": [0, -2, -4, -6, 7, 9, 10, -12, 13, 15, -16, 23, 24],
    "迷客夏": [0, -2, -4, -6, 7, 9, 10, -12, 13, 15, -16, 23, 24],
    "龜記": [0, -2, -4, -6, 7, 9, 10, -12, 13, 15, -16, 23, 24],
    "社群小編": [-0, -2, 3, -6, -7, 10, 13, -15, -16, 22, -23, -24],
    "校內工讀": [0, -2, -3, -4, -6, -7, -8, 10, -12, 13, -15, 23, -24],
    "家樂福": [0, -2, -4, -6, -7, -8, 9, -10, -12, 13, 15, -16, 23, 24],
    "大潤發": [0, -2, -4, -6, -7, -8, 9, -10, -12, 13, 15, -16, 23, 24],
    "大潤發(大夜)": [0, -2, 4, -6, -7, -8, 9, -10, -12, 13, 15, -16, 23, 24],
    "寶雅": [0, -2, -4, -6, -7, -8, 9, 10, -12, 13, 15, -16, 23, 24],
    "全聯": [0, -2, -4, -6, -7, -8, 9, 10, -12, 13, 15, -16, 23, 24],
    "屈臣氏": [0, -2, -4, -6, -7, -8, 9, 10, -12, 13, 15, -16, 23, 24],
    "康是美": [0, -2, -4, -6, -7, -8, 9, 10, -12, 13, 15, -16, 23, 24],
    "蝦皮 理貨": [0, 2, -4, 6, -7, -8, 10, -12, -13, 15, -16, -22, 23, 24],
    "momo電商": [0, 2, -4, 6, -7, -8, -10, -12, -13, 15, -16, -22, 23, 24],
    "蝦皮理貨(大夜)": [0, 2, 4, 6, -7, -8, 10, -12, -13, 15, -16, -22, 23, 24],
    "家教(二手拍)": [-0, -2, -7, 8, 12, 13, 14, 19, -23],
    "補習班老師": [0, -2, -7, 8, 12, 13, 14, 15, 19, -23],
    "補習班行政工讀": [0, -2, -3, -4, -7, -8, -9, -12, 13, -15, 23, -24],
    "文字編輯": [-0, 2, 3, -6, -7, -8, 10, 13, -15, -23, -24],
    "寵物陪玩": [-0, -2, -5, -6, -7, 8, 12, 13, -24],
    "遊戲陪玩": [-0, -2, 3, -6, -7, 8, 10, 12, 13, -23, -24],
    "影音剪輯": [-0, 2, 3, -6, 10, -12, -15, -24],
    "傳單派發": [-0, -2, -13, 15, 22, 23, -24],
    "電話問卷訪談員": [0, -2, -7, 13, -15, 22, -23, -24],
    "實地問卷面談員": [-0, -2, -7, 8, 12, -13, 15, 22, 23],
    "兼職銷售": [0, -2, -7, 8, 12, 13, 15, -16, 22, 23, 24],
    "uniqlo": [0, -2, -4, -7, -10, 13, 15, 22, 23, 25],
    "H&M": [0, -2, -4, -7, -10, 13, 15, 22, 23, 25],
    "Nike": [0, -2, -4, -7, -10, 13, 15, 22, 23, 25],
    "愛迪達": [0, -2, -4, -7, -10, 13, 15, 22, 23, 25],
    "神秘客": [-0, 1, -2, 12, -13, 23, -24],
    "資訊助理": [0, -2, 3, -4, -6, 13, -15, -23],
    "伴讀": [-0, -2, -7, 8, 12, 13, 14, -15],
    "Uber eat": [-0, 1, -2, 8, -9, 12, -13, 15, 23, 24],
    "熊貓": [-0, 1, -2, 8, -9, 12, -13, 15, 23, 24],
    "診所工讀": [0, -2, -4, 10, 13, -15, -23],
    "燦坤": [0, 2, -4, 9, 10, -12, 15, 23, 24],
    "鋼琴家教": [-0, -2, 8, 12, 13, 14, 17, -23, -24],
    "吉他家教": [-0, -2, 8, 12, 13, 14, 17, -23, -24],
    "游泳家教": [-0, -2, 8, 12, 13, 14, 18, -23, -24],
    "羽球家教": [-0, -2, 8, 12, 13, 14, 18, -23, -24],
    "日文家教": [-0, -2, 8, 12, 13, 14, 20, -23, -24],
    "韓文家教": [-0, -2, 8, 12, 13, 14, 20, -23, -24],
    "英文家教": [-0, -2, 8, 12, 13, 14, 19, -23, -24],
    "數理家教": [-0, -2, 8, 12, 13, 14, 19, -23, -24],
    "程式語言家教": [-0, -2, 8, 12, 13, 14, 21, -23, -24],
    "微積分家教": [-0, -2, 8, 12, 13, 14, 21, -23, -24],
    "舞蹈家教": [-0, -2, 8, 12, 13, 14, -23, -24, 27],
    "美術家教": [-0, -2, 8, 12, 13, 14, -23, -24, 27],
    "壽司郎": [0, -2, -4, -6, 7, 9, -10, -12, 13, 15, -16, 23, 24],
}

def calculate_score(answers, job, region_answer):
    total_score = 0.0
    content = (job.get('條件限制') or '') + (job.get('備注') or '') + (job.get('時間要求') or '') + job.get('工作', '')
    job_name = job['工作']
    base_name = re.sub(r"\(.*?\)", "", job_name).strip()

    # --- 檢查 job_question_mapping 條件 ---
    if base_name in job_question_mapping:
        for q_index in job_question_mapping[base_name]:
            idx = abs(q_index)
            if idx >= len(answers):
                return 0.0
            answer = answers[idx].strip().lower()
            if (q_index > 0 and answer != 'yes') or (q_index < 0 and answer != 'no'):
                return 0.0

    # --- 特殊題（第11題：多少小時達成百萬） ---
    try:
        user_limit = float(answers[11])
        job_limit = float(job.get('賺到一百萬時間(下限)', 999999))
        if abs(user_limit - job_limit) <= 500:
            total_score += 2.0
    except:
        pass

    # --- 其他題目均分 8 分 ---
    other_question_indices = [i for i in range(len(answers)) if i != 11]
    per_question_score = 8.0 / len(other_question_indices)

    exclusion_rules = {
        1: ["駕照", "外送", "Uber", "熊貓"],
        17: ["鋼琴", "吉他"],
        18: ["體育", "羽球", "游泳"],
        19: ["家教", "數學", "理化", "學科"],
        20: ["英文", "日文", "韓文", "語言"],
        21: ["程式", "微積分", "專業科目"],
        27: ["美術家教", "舞蹈家教"]
    }

    for idx in other_question_indices:
        if idx >= len(condition_keywords):
            continue
        answer = answers[idx].strip().lower()
        keywords = condition_keywords[idx]
        point = 0

        # 排除條件：關鍵字存在 + 使用者回答 no → 直接淘汰
        if idx in exclusion_rules and answer == 'no':
            if any(k.lower() in content.lower() for k in exclusion_rules[idx]):
                return 0.0

        # 特殊題目處理：避免反向邏輯誤判
        if idx in [2, 5]:
            if answer == 'no' and not any(k in content for k in keywords):
                point = 1
            elif answer == 'yes' and any(k in content for k in keywords):
                point = 1
        else:
            if answer == 'yes' and any(k in content for k in keywords):
                point = 1
            elif answer == 'no' and not any(k in content for k in keywords):
                point = 1

        total_score += per_question_score * point

    # --- 地區加分 ---
    if not re.search(r"\((南部|北部|台南|台北|高雄|新北|台中|桃園)\)", job_name):
        if '貳樓' in base_name:
            total_score += 1.0 if region_answer == '是' else 0.5
        elif '一風堂' in base_name:
            total_score += 1.5 if region_answer == '是' else 1.0
        elif '寶雅' in base_name:
            total_score += 0.5 if region_answer == '是' else 0.2

    # --- 特定職缺加分邏輯 ---
    try:
        work_hours = float(answers[11])
        if job_name.strip() == '瓦城(外場服務員)' and work_hours >= 40:
            total_score += 1.0
        elif job_name.strip() in ['一風堂(台南)', '一風堂(北部)']:
            if work_hours >= 140:
                total_score += 1.0
            elif work_hours >= 120:
                total_score += 0.5
    except:
        pass

    job['搜尋連結'] = f"https://www.104.com.tw/jobs/search/?keyword={job_name}"
    return round(total_score, 2)

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
        # 將滑桿的值轉換為整數
        if idx == 11:
            try:
                answer = int(answer)
            except ValueError:
                return redirect(url_for('question', idx=idx))
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

    region_answer = answers[26] if len(answers) > 26 else '否'
    scored_jobs = []

    for job in jobs:
        score = calculate_score(answers, job, region_answer)
        scored_jobs.append((job, score))

    scored_jobs.sort(key=lambda x: x[1], reverse=True)
    top_jobs = scored_jobs[:5]

    return render_template('results.html', jobs=top_jobs)

if __name__ == '__main__':
    app.run(debug=True)
