import hashlib
import hmac
import os

import database as db


def hash_password(password):
    salt=os.urandom(16)
    digest=hashlib.pbkdf2_hmac('sha256',password.encode('utf-8'),salt,200_000)
    return f'{salt.hex()}:{digest.hex()}'


def verify_password(password,stored):
    try:
        s,d=stored.split(':',1)
        salt=bytes.fromhex(s); expected=bytes.fromhex(d)
        actual=hashlib.pbkdf2_hmac('sha256',password.encode('utf-8'),salt,200_000)
        return hmac.compare_digest(actual,expected)
    except Exception:
        return False


def authenticate(username,password):
    user=db.get_user_by_username(username)
    if not user or not verify_password(password,user['password_hash']):
        return False,'Sai tên đăng nhập hoặc mật khẩu.',None
    if user['status']!='active':
        return False,'Tài khoản đang bị khóa.',None
    return True,'Đăng nhập thành công.',user


def register_reader(username,password,full_name,email='',phone=''):
    if len(username.strip())<4: return False,'Tên đăng nhập cần ít nhất 4 ký tự.'
    if len(password)<6: return False,'Mật khẩu cần ít nhất 6 ký tự.'
    if not full_name.strip(): return False,'Vui lòng nhập họ tên.'
    return db.create_user(username,hash_password(password),full_name,email,phone,'reader')


def ensure_demo_accounts():
    if not db.get_user_by_username('admin'):
        db.create_user('admin',hash_password('admin123'),'Quản trị viên Hệ thống','admin@library.local','','admin')
    if not db.get_user_by_username('thuthu'):
        db.create_user('thuthu',hash_password('thuthu123'),'Thủ thư Demo','thuthu@library.local','','librarian')
    if not db.get_user_by_username('docgia'):
        db.create_user('docgia',hash_password('reader123'),'Độc giả Demo','reader@library.local','0900000000','reader')
    if not db.get_user_by_username('docgia2'):
        db.create_user('docgia2',hash_password('reader123'),'Nguyễn Minh Anh','minhanh@library.local','0912345678','reader')
    if not db.get_user_by_username('docgia3'):
        db.create_user('docgia3',hash_password('reader123'),'Trần Hoàng Nam','hoangnam@library.local','0987654321','reader')
