from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

ai_images    = ["Ai (1).jpg", "Ai (2).jpg", "Ai (3).jpg", "Ai (4).jpg", "Ai (5).jpg", "Ai (6).jpg", "Ai (7).jpg", "Ai (8).jpg", "Ai (9).jpg", "Ai (10).jpg", "Ai (11).jpg", "Ai (12).jpg", "Ai (13).jpg", "Ai (14).jpg", "Ai (15).jpg", "Ai (16).jpg", "Ai (1).png", "Ai (2).png", "Ai (3).png", "Ai (4).png", "Ai (5).png", "Ai (6).png", "Ai (7).png", "Ai (8).png", "Ai (9).png", "Ai (10).png", "Ai (11).png", "Ai (12).png", "Ai (1).webp", "Ai (2).webp"]
human_images = ["h (1).jpg", "h (2).jpg", "h (3).jpg", "h (4).jpg", "h (5).jpg", "h (6).jpg", "h (7).jpg", "h (8).jpg", "h (9).jpg", "h (10).jpg", "h (11).jpg", "h (12).jpg", "h (13).jpg", "h (14).jpg", "h (15).jpg", "h (16).jpg", "h (17).jpg", "h (18).jpg", "h (19).jpg", "h (20).jpg", "h (21).jpg", "h (22).jpg", "h (23).jpg", "h (24).jpg", "h (25).jpg", "h (26).jpg", "h (27).jpg", "h (28).jpg", "h (29).jpg", "h (30).jpg"]

TOTAL_ROUNDS = 3

def generate_round():
    used_ai    = session.get('used_ai', [])
    used_human = session.get('used_human', [])

    available_ai    = [img for img in ai_images    if img not in used_ai]
    available_human = [img for img in human_images if img not in used_human]

    if len(available_ai) < 1:
        available_ai = list(ai_images)
        used_ai = []
    if len(available_human) < 1:
        available_human = list(human_images)
        used_human = []

    is_ai = random.choice([True, False])
    if is_ai:
        selected = random.choice(available_ai)
        label = "AI"
        session['used_ai'] = used_ai + [selected]
    else:
        selected = random.choice(available_human)
        label = "HUMAN"
        session['used_human'] = used_human + [selected]

    session.modified = True
    return {"file": selected, "label": label}

@app.route('/')
def start():
    session.clear()
    return render_template('start.html')

@app.route('/game')
def game():
    # 계속하기 모드 진입: 점수/통계는 이월, 라운드 카운터만 리셋
    if request.args.get('continue') == '1':
        prev_score        = session.get('score', 0)
        prev_ai_correct   = session.get('ai_correct', 0)
        prev_ai_total     = session.get('ai_total', 0)
        prev_human_correct= session.get('human_correct', 0)
        prev_human_total  = session.get('human_total', 0)
        prev_used_ai      = session.get('used_ai', [])
        prev_used_human   = session.get('used_human', [])
        session.clear()
        session['continue_mode']  = True
        session['round']          = 1
        session['score']          = prev_score        # 이전 점수 이월
        session['ai_correct']     = prev_ai_correct
        session['ai_total']       = prev_ai_total
        session['human_correct']  = prev_human_correct
        session['human_total']    = prev_human_total
        session['used_ai']        = prev_used_ai
        session['used_human']     = prev_used_human
        session.modified = True

    # 게임이 이미 종료된 상태에서 /game 재접근 차단
    if session.get('game_ended'):
        return redirect(url_for('result'))

    continue_mode = session.get('continue_mode', False)
    current_round = session.get('round', 1)

    if not continue_mode and current_round > TOTAL_ROUNDS:
        return redirect(url_for('result'))

    image = generate_round()
    return render_template('game.html',
        image=image,
        total_rounds=TOTAL_ROUNDS,
        current_round=current_round,
        continue_mode=continue_mode,
        current_score=session.get('score', 0)
    )

@app.route('/check', methods=['POST'])
def check():
    # 이미 종료된 게임이면 무시
    if session.get('game_ended'):
        return jsonify({'is_correct': False, 'correct_label': '', 'game_over': True,
                        'score': session.get('score', 0)})

    data       = request.json
    answer     = data['answer']
    label      = data['label']
    is_correct = (answer == label)

    # 통계 업데이트
    if label == 'AI':
        session['ai_total']   = session.get('ai_total', 0) + 1
        if is_correct:
            session['ai_correct'] = session.get('ai_correct', 0) + 1
    else:
        session['human_total']   = session.get('human_total', 0) + 1
        if is_correct:
            session['human_correct'] = session.get('human_correct', 0) + 1

    if is_correct:
        session['score'] = session.get('score', 0) + 1

    session['round'] = session.get('round', 1) + 1
    session.modified = True

    continue_mode = session.get('continue_mode', False)

    if continue_mode:
        game_over = not is_correct          # 계속하기: 틀리면 즉시 종료
    else:
        game_over = session['round'] > TOTAL_ROUNDS  # 일반: 3라운드 완료 후 종료

    if game_over:
        session['game_ended'] = True
        session.modified = True

    return jsonify({
        'is_correct':    is_correct,
        'correct_label': label,
        'game_over':     game_over,
        'score':         session.get('score', 0)
    })

@app.route('/result')
def result():
    score         = session.get('score', 0)
    ai_correct    = session.get('ai_correct', 0)
    ai_total      = session.get('ai_total', 0)
    human_correct = session.get('human_correct', 0)
    human_total   = session.get('human_total', 0)
    continue_mode = session.get('continue_mode', False)
    all_correct   = (score == TOTAL_ROUNDS) and not continue_mode

    return render_template('result.html',
        score=score, total=TOTAL_ROUNDS,
        ai_correct=ai_correct, ai_total=ai_total,
        human_correct=human_correct, human_total=human_total,
        continue_mode=continue_mode,
        all_correct=all_correct
    )

if __name__ == '__main__':
    app.run(debug=True)
