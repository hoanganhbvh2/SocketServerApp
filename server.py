import socketio
import aiohttp
from aiohttp import web
import asyncio
from module import phu
from module import tuan
from module import tuananh
from module import thai

# Khởi tạo Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

# Dùng dictionary để lưu thông tin user và các tác vụ đang chờ
users = {}  # {sid: username}
pending_disconnect_tasks = {}  # {sid: task}
chat_history = []  # Lưu trữ lịch sử trò chuyện: [{'username': username, 'message': message}, ...]

# Hàm gửi danh sách người dùng đã cập nhật cho tất cả client
async def update_user_list():
    online_users = list(users.values())
    print(f"Cập nhật danh sách người dùng: {online_users}")
    await sio.emit('update_user_list', {'users': online_users})

# Hàm xử lý ngắt kết nối có độ trễ
async def delayed_disconnect(sid):
    await asyncio.sleep(5)  # Đợi 5 giây
    if sid in pending_disconnect_tasks:  # Kiểm tra xem user có kết nối lại trong lúc chờ không
        username = users.pop(sid, None)
        if username:
            print(f"Người dùng {username} ({sid}) đã thực sự rời đi.")
            await update_user_list()
            await sio.emit('user_left', {'username': username})
        del pending_disconnect_tasks[sid]

@sio.event
async def connect(sid, environ):
    print(f"Client kết nối tạm thời: {sid}")

@sio.event
async def disconnect(sid):
    if sid in users:
        print(f"Client {users[sid]} ({sid}) ngắt kết nối. Đang chờ xác nhận...")
        # Tạo một tác vụ ngắt kết nối có độ trễ thay vì xóa ngay lập tức
        task = asyncio.create_task(delayed_disconnect(sid))
        pending_disconnect_tasks[sid] = task
    else:
        print(f"Client không xác định ({sid}) ngắt kết nối.")

@sio.event
async def join(sid, data):
    username = data.get('username')
    if not username:
        return

    # KIỂM TRA QUAN TRỌNG: Nếu người dùng này vừa kết nối lại (reload trang)
    # Tìm xem có sid cũ nào có cùng username không
    old_sid = None
    for s, u in users.items():
        if u == username:
            old_sid = s
            break
    
    # Nếu có, hủy tác vụ chờ ngắt kết nối của sid cũ đó
    if old_sid and old_sid in pending_disconnect_tasks:
        print(f"Người dùng {username} đã kết nối lại. Hủy tác vụ ngắt kết nối.")
        pending_disconnect_tasks[old_sid].cancel()
        del pending_disconnect_tasks[old_sid]

    # Cập nhật thông tin user với sid mới
    users[sid] = username
    print(f"{username} ({sid}) đã tham gia phòng chat.")
    print(chat_history)
    # Gửi lịch sử trò chuyện cho người dùng vừa tham gia
    await sio.emit('chat_history', {'history': chat_history}, room=sid)
    
    # Thông báo cho người khác và cập nhật danh sách
    await sio.emit('user_joined', {'username': username}, skip_sid=sid)
    await update_user_list()

@sio.event
async def chat_message(sid, data):
    if sid in users:
        username = users[sid]
        message = data.get('message')
        print(f"Tin nhắn từ {username}: {message}")
        # Lưu tin nhắn vào lịch sử
        chat_history.append({'username': username, 'message': message})
        # Chỉ gửi cho những người khác, không gửi lại cho người gửi
        await sio.emit('new_message', 
                       {'username': username, 'message': message}, 
                       skip_sid=sid)

if __name__ == '__main__':
    print("Server đang khởi chạy tại http://localhost:5000")
    web.run_app(app, host='localhost', port=5000)