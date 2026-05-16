from flask import Flask, render_template, request, jsonify, session
import random

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # ✏️ 원하는 문자열로 변경 가능

# =====================================================================
# ✏️  이미지 파일명 수정 방법
# 아래 리스트에 실제 파일명을 정확히 입력하세요.
# 파일은 static/images/ 폴더 안에 있어야 합니다.
# =====================================================================
ai_images    = ["ai1.jpg", "ai2.jpg", "ai3.jpg", "ai4.jpg"]
human_images = ["h1.jpg", "h2.jpg", "h3.jpg", "h4.jpg", "h5.jpg", "h6.jpg"]
# =====================================================================

TOTAL_ROUNDS = 3

def generate_round():
    # 세션에서 이미 사용한 이미지 목록 가져오기
    used_ai    = session.get('used_ai', [])
    used_human = session.get('used_human', [])

    # 아직 사용하지 않은 이미지만 후보로
    available_ai    = [img for img in ai_images    if img not in used_ai]
    available_human = [img for img in human_images if img not in used_human]

    # 남은 AI 이미지가 부족하면 풀 초기화
    if len(available_ai) < 1:
        available_ai = list(ai_images)
        used_ai = []

    # 남은 Human 이미지가 부족하면 풀 초기화
    if len(available_human) < 5:
        available_human = list(human_images)
        used_human = []

    ai_count    = random.randint(1, min(3, len(available_ai)))
    human_count = 6 - ai_count

    selected_ai    = random.sample(available_ai, ai_count)
    selected_human = random.sample(available_human, human_count)

    # 사용한 이미지 세션에 기록
    session['used_ai']    = used_ai    + selected_ai
    session['used_human'] = used_human + selected_human

    images = [{"file": img, "label": "AI"}    for img in selected_ai] + \
             [{"file": img, "label": "HUMAN"} for img in selected_human]

    random.shuffle(images)
    return images

@app.route('/')
def start():
    session.clear()  # 홈 화면에 오면 사용 이력 초기화
    return render_template('start.html')

@app.route('/game')
def game():
    images = generate_round()
    return render_template('game.html', images=images, total_rounds=TOTAL_ROUNDS)

@app.route('/check', methods=['POST'])
def check():
    data    = request.json
    selected = data['selected']
    images  = data['images']

    correct_indices = [i for i, img in enumerate(images) if img['label'] == 'AI']
    is_correct      = set(selected) == set(correct_indices)

    return jsonify({
        "is_correct":      is_correct,
        "correct_indices": correct_indices,
        "explanation":     "AI 이미지는 손, 텍스트, 배경 디테일에서 오류가 나타날 수 있지만 항상 구별 가능한 것은 아닙니다."
    })

if __name__ == '__main__':
    app.run(debug=True)
