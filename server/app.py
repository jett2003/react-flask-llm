import firebase_admin
from firebase_admin import credentials, firestore

from flask import Flask, request, jsonify
from flask_cors import CORS

# 初始化 Firebase（第一次用）
cred = credentials.Certificate("molting-llm-firebase-adminsdk-fbsvc-f5642adbc4.json")  # Firebase 控制台下載的金鑰
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
CORS(app)  # 啟用跨域請求支持

@app.route('/api/habits',methods=['POST'])
def create_habits():
    # 從前端POST請求中讀取資料
    data = request.get_json()
    # 從data裡面拿到user_id 指哪個使用者下面存資料的 ID
    user_id = data.get('user_id')
    # 從data裡面拿到profile 儲存的某個習慣 (habit) 的 ID
    profile = data.get('profile')
    # 從data 拿到真正要寫進資料庫的習慣內容（也就是欄位資料）
    working_habit_data = data.get('working_habit_data')
    # 設定要寫進德位置(路徑)
    event_rel = db.collection('users').document(user_id).collection('working_habits').document(profile)
    # 將工作習慣塞進去
    event_rel.set(working_habit_data)

    return jsonify({'message': f'Event {user_id} created successfully'}), 200

@app.route('/api/habits',methods=['GET'])
def retrieve_habits():

    user_id = request.args.get('user_id')  # 從 URL 取得 ?user_id=xxxx
    # 如果沒有提供 user_id，回傳錯誤訊息
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400
    # 去找 users/{user_id}/working_habits 這個collection
    habits_ref = db.collection('users').document(user_id).collection('working_habits')

    # 從 Firestore 把所有 working_habits 的文件取出來
    habits = habits_ref.stream()

    result = []
    # 將每個 habit document 的資料加進結果 list
    for habit in habits:
        habit_data = habit.to_dict() # 把 document 資料轉成字典格式
        habit_data['id'] = habit.id  # 把每個 habit 的 document id 加進來，方便前端使用
        result.append(habit_data)

    return jsonify(result), 200

@app.route('/api/habits',methods=['PUT'])
def update_habits():

    data = request.get_json()

    # 取得需要的參數
    user_id = data.get('user_id')       # 使用者ID
    profile = data.get('profile')        # 要更新的 habit 的 document ID
    working_habit_data = data.get('working_habit_data') # 要更新的欄位內容（字典）

    # 檢查必要欄位
    if not user_id or not profile or not working_habit_data:
        return jsonify({'error': 'Missing user_id, profile or update_data'}), 400

    try:
        # 指定到 users/{user_id}/working_habits/{profile}
        habit_ref = db.collection('users').document(user_id).collection('working_habits').document(profile)
        
        # 更新指定欄位（不會整份覆蓋，只改特定欄位）
        habit_ref.update(working_habit_data)

        return jsonify({'message': f'Habit {profile} updated successfully for user {user_id}'}), 200

    except Exception as e:
        # 如果發生錯誤，回傳錯誤訊息
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)