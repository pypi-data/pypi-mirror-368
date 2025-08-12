import argparse
import base64
import concurrent.futures
import hashlib
import json
import os
import signal
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
import tarfile
import random
import logging
import threading
from threading import Lock

import base58
import requests
from Cryptodome.Cipher import DES
from Cryptodome.Util import Padding


# 全局变量用于控制上传中断
upload_interrupted = False
interrupt_count = 0
current_operation = None  # 'upload' 或 'download'
resume_enabled = False    # 是否启用了断点续传

# 多线程下载相关全局变量
download_lock = Lock()  # 用于线程安全的进度更新
total_downloaded = 0    # 总下载字节数
chunk_download_status = {}  # 分块下载状态
active_connections = {}  # 活跃连接状态
download_speed_history = []  # 下载速度历史

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

_apiBaseUrl = 'https://www.wenshushu.cn'

def signal_handler(signum, frame):
    """处理Ctrl+C中断信号"""
    global upload_interrupted, interrupt_count, current_operation, resume_enabled
    interrupt_count += 1
    
    if interrupt_count == 1:
        upload_interrupted = True
        # 根据当前操作显示相应的中断消息
        if current_operation == 'download':
            print(f"\n{_('download_interrupted')}")
        else:
            print(f"\n{_('upload_interrupted')}")
        
        # 只在启用断点续传时显示保存信息
        if resume_enabled:
            print(_('saving_resume_info'))
        # 第一次Ctrl+C，优雅退出
    elif interrupt_count >= 2:
        # 第二次Ctrl+C，强制退出
        print(f"\n{_('force_exit')}")
        import os
        os._exit(1)

# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)

# 断点续传信息存储

# 语言系统
LANG = 'zh'  # 默认语言

TRANSLATIONS = {
    'zh': {
        'file_expires': '文件过期时间:{}天{}时{}分{}秒',
        'file_size': '文件大小:{} MB',
        'file_name': '文件名:{}',
        'detected_resume_with_progress': '检测到断点续传，已下载: {} ({}%)',
        'detected_resume': '检测到断点续传，已下载: {}',
        'starting_download': '开始下载!',
        'download_complete': '下载完成!',
        'download_error': '下载出错: {}',
        'download_cancelled': '下载已取消，断点续传信息已保存',
        'download_cancelled_no_resume': '下载已取消',
        'download_interrupted': '检测到中断信号，正在停止下载...',
        'resume_info_saved': '已保存断点续传信息，下次可使用 -c 参数继续下载',
        'share_traffic_insufficient': '对方的分享流量不足',
        'used_space': '当前已用空间:{}GB,剩余空间:{}GB,总空间:{}GB',
        'too_fast': '操作太快啦！请{}秒后重试',
        'need_verification': '需要滑动验证码',
        'personal_link': '个人管理链接：{}',
        'public_link': '公共链接：{}',
        'instant_transfer': '文件{}可以被秒传！',
        'file_chunked_upload': '文件正在被分块上传！',
        'upload_complete': '上传完成!',
        'upload_error': '上传出错: {}',
        'file_single_upload': '文件被整块上传！',
        'upload_complete_100': '上传完成:100%',
        'upload_interrupted': '检测到中断信号，正在停止上传...',
        'saving_resume_info': '正在保存断点续传信息...',
        'upload_cancelled': '上传已取消',
        'force_exit': '强制退出程序...',
        'days': '天',
        'hours': '时',
        'minutes': '分',
        'seconds': '秒',
        'trying_saved_token': '尝试使用已保存的token登录',
        'logged_in': '已登录 "{}"',
        'saved_token_invalid': '已保存的token无效，使用匿名登录',
        'no_saved_token': '未找到已保存的token，使用匿名登录',
        'using_anonymous': '使用匿名登录',
        'parameter_error': '参数错误，使用 -h 查看帮助',
        'login_success_saved': '登录成功并已保存！',
        'login_failed': '登录失败，请检查token是否正确',
        'current_login_status': '=== 当前登录状态 ===',
        'currently_logged_user': '当前已登录用户',
        'username': '用户名',
        'email': '邮箱',
        'phone': '手机号',
        'current_token_invalid': '当前token无效',
        'token_cleaned': '已自动清理无效token',
        'not_logged_in': '当前未登录',
        'login_options': '=== 登录选项 ===',
        'enter_new_token': '1. 输入新的TOKEN登录',
        'select_saved_account': '2. 从已保存账户中选择',
        'view_tutorial': '3. 查看TOKEN获取教程',
        'cancel': '0. 取消',
        'please_choose': '请选择',
        'enter_token': '请输入X-TOKEN',
        'no_saved_accounts': '没有保存的账户信息',
        'choose_option1_or_3': '请选择选项1输入新TOKEN，或选择选项3查看获取教程',
        'switch_login_success': '切换登录成功！',
        'account_token_expired': '该账户token已失效',
        'cancelled': '已取消',
        'invalid_choice': '无效选择',
        'operation_failed': '操作失败',
        'current_user_info': '=== 当前登录用户信息 ===',
        'token_invalid_expired': '当前token无效或已过期',
        'confirm_logout': '确定要退出当前账户吗？(y/N)',
        'logout_success': '已成功退出账户',
        'logout_cancelled': '已取消退出',
        'no_account_logged': '当前未登录任何账户',
        'error_provide_command': '错误: 请提供命令 (upload/download/login/unlogin)',
        'use_help': '使用 -h 查看帮助',
        'error_target_required': '错误: {} 命令需要提供目标参数',
        'using_proxy': '使用代理',
        'using_pickup_code': '使用取件码',
        'random_pickup_code': '随机生成取件码',
        'no_saved_user_tokens': '没有保存的用户token',
        'saved_user_accounts': '已保存的用户账户',
        'last_login': '最后登录',
        'select_account_number': '请选择账户编号 (0=取消)',
        'invalid_input': '无效输入',
        'removed_invalid_account': '已删除无效账户',
        'multithread_download': '多线程下载模式 ({}线程)',
        'single_thread_download': '单线程下载模式',
        'server_no_range_support': '服务器不支持多线程下载，使用单线程模式',
        'file_too_small': '文件较小，使用单线程下载',
        'multithread_resume_detected': '检测到多线程断点续传，已完成 {}/{} 个分块',
        'multithread_complete': '多线程下载完成!',
        'multithread_failed': '多线程下载失败',
        'chunk_download_failed': '分块下载失败',
        'fallback_single_thread': '多线程下载失败，尝试单线程下载...',
        'invalid_thread_count': '错误: 线程数必须在1-16之间',
        'idm_style_download': 'IDM风格多连接下载: {} 个并行连接',
        'connection_status': '活跃连接状态',
        'download_stream_mode': '无法获取文件大小，使用流式下载',
        'file_already_complete': '文件已经下载完成',
        'download_incomplete': '下载不完整: {}/{}',
        'multiconnection_failed': '多连接下载失败，尝试单线程下载...',
        'active_connections': '活跃',
        'chunk_status': '块状态',
        'chunk': '块',
        'server_range_support_yes': '服务器Range支持: 是',
        'server_range_support_no': '服务器Range支持: 否',
        'starting_threads': '启动 {} 个线程...',
        'merging_chunks': '开始合并 {} 个块...',
        'merge_complete': '合并完成! 文件大小: {}',
        'integrity_verified': '✓ 文件完整性验证通过',
        'temp_files_cleaned': '✓ 临时文件已清理',
        'temp_files_clean_failed': '注意: 临时文件清理失败',
        'file_size_mismatch': '⚠ 文件大小不匹配: 期望{}，实际{}',
        'download_interrupted': '下载已中断',
        'partial_chunks_incomplete': '警告: 部分块未完成下载',
        'chunk_file_missing': '  警告: 块{}文件不存在',
        'merge_error': '合并文件时出错: {}',
        'resume_detected': '断点续传',
        'downloaded_so_far': '已下载'
    },
    'en': {
        'file_expires': 'File expires in: {} days {} hours {} minutes {} seconds',
        'file_size': 'File size: {} MB',
        'file_name': 'File name: {}',
        'detected_resume_with_progress': 'Detected resume, downloaded: {} ({}%)',
        'detected_resume': 'Detected resume, downloaded: {}',
        'starting_download': 'Starting download!',
        'download_complete': 'Download complete!',
        'download_error': 'Download error: {}',
        'download_cancelled': 'Download interrupted, saving resume info...',
        'download_cancelled_no_resume': 'Download cancelled',
        'download_interrupted': 'Download interrupted, stopping download...',
        'resume_info_saved': 'Resume info saved, you can continue with -c parameter',
        'share_traffic_insufficient': 'Share traffic insufficient',
        'used_space': 'Current used space: {} GB, remaining space: {} GB, total space: {} GB',
        'too_fast': 'Too fast! Please try again after {} seconds',
        'need_verification': 'Need to slide verification code',
        'personal_link': 'Personal management link: {}',
        'public_link': 'Public link: {}',
        'instant_transfer': 'File {} can be transferred instantly!',
        'file_chunked_upload': 'File is being chunked up!',
        'upload_complete': 'Upload complete!',
        'upload_error': 'Upload error: {}',
        'file_single_upload': 'File is being uploaded in one go!',
        'upload_complete_100': 'Upload complete: 100%',
        'upload_interrupted': 'Upload interrupted, saving resume info...',
        'saving_resume_info': 'Saving resume info...',
        'upload_cancelled': 'Upload cancelled',
        'force_exit': 'Force exit program...',
        'days': 'days',
        'hours': 'hours', 
        'minutes': 'minutes',
        'seconds': 'seconds',
        'trying_saved_token': 'Trying to login with saved token',
        'logged_in': 'Logged in "{}"',
        'saved_token_invalid': 'Saved token invalid, using anonymous login',
        'no_saved_token': 'No saved token found, using anonymous login',
        'using_anonymous': 'Using anonymous login',
        'parameter_error': 'Parameter error, use -h for help',
        'login_success_saved': 'Login successful and saved!',
        'login_failed': 'Login failed, please check if token is correct',
        'current_login_status': '=== Current Login Status ===',
        'currently_logged_user': 'Currently logged in user',
        'username': 'Username',
        'email': 'Email',
        'phone': 'Phone',
        'current_token_invalid': 'Current token is invalid',
        'token_cleaned': 'Invalid token has been automatically cleaned',
        'not_logged_in': 'Not logged in',
        'login_options': '=== Login Options ===',
        'enter_new_token': '1. Enter new TOKEN to login',
        'select_saved_account': '2. Select from saved accounts',
        'view_tutorial': '3. View TOKEN tutorial',
        'cancel': '0. Cancel',
        'please_choose': 'Please choose (0-3)',
        'enter_token': 'Please enter X-TOKEN',
        'no_saved_accounts': 'No saved account information',
        'choose_option1_or_3': 'Please choose option 1 to enter new TOKEN, or option 3 to view tutorial',
        'switch_login_success': 'Switch login successful!',
        'account_token_expired': 'This account token has expired',
        'cancelled': 'Cancelled',
        'invalid_choice': 'Invalid choice',
        'operation_failed': 'Operation failed',
        'current_user_info': '=== Current User Info ===',
        'token_invalid_expired': 'Current token is invalid or expired',
        'confirm_logout': 'Are you sure to logout? (y/N)',
        'logout_success': 'Successfully logged out',
        'logout_cancelled': 'Logout cancelled',
        'no_account_logged': 'No account currently logged in',
        'error_provide_command': 'Error: Please provide a command (upload/download/login/unlogin)',
        'use_help': 'Use -h for help',
        'error_target_required': 'Error: {} command requires target parameter',
        'using_proxy': 'Using proxy',
        'using_pickup_code': 'Using pickup code',
        'random_pickup_code': 'Random pickup code',
        'no_saved_user_tokens': 'No saved user tokens',
        'saved_user_accounts': 'Saved user accounts',
        'last_login': 'Last login',
        'select_account_number': 'Please select account number (0=cancel)',
        'invalid_input': 'Invalid input',
        'removed_invalid_account': 'Removed invalid account',
        'multithread_download': 'Multi-thread download mode ({} threads)',
        'single_thread_download': 'Single-thread download mode',
        'server_no_range_support': 'Server does not support multi-thread download, using single-thread mode',
        'file_too_small': 'File is too small, using single-thread download',
        'multithread_resume_detected': 'Detected multi-thread resume, completed {}/{} chunks',
        'multithread_complete': 'Multi-thread download complete!',
        'multithread_failed': 'Multi-thread download failed',
        'chunk_download_failed': 'Chunk download failed',
        'fallback_single_thread': 'Multi-thread download failed, trying single-thread download...',
        'invalid_thread_count': 'Error: Thread count must be between 1-16',
        'idm_style_download': 'IDM-style multi-connection download: {} parallel connections',
        'connection_status': 'Active connection status',
        'download_stream_mode': 'Unable to get file size, using streaming download',
        'file_already_complete': 'File already downloaded',
        'download_incomplete': 'Download incomplete: {}/{}',
        'multiconnection_failed': 'Multi-connection download failed, trying single-thread download...',
        'active_connections': 'Active',
        'chunk_status': 'Chunk status',
        'chunk': 'Chunk',
        'server_range_support_yes': 'Server Range support: Yes',
        'server_range_support_no': 'Server Range support: No',
        'starting_threads': 'Starting {} threads...',
        'merging_chunks': 'Merging {} chunks...',
        'merge_complete': 'Merge complete! File size: {}',
        'integrity_verified': '✓ File integrity verified',
        'temp_files_cleaned': '✓ Temporary files cleaned',
        'temp_files_clean_failed': 'Note: Temporary files cleanup failed',
        'file_size_mismatch': '⚠ File size mismatch: Expected {}, actual {}',
        'download_interrupted': 'Download interrupted',
        'partial_chunks_incomplete': 'Warning: Partial chunks incomplete',
        'chunk_file_missing': '  Warning: Chunk {} file not found',
        'merge_error': 'Merge error: {}',
        'resume_detected': 'Resume detected',
        'downloaded_so_far': 'Downloaded so far'
    }
}

def _(key, *args):
    """翻译函数"""
    global LANG
    text = TRANSLATIONS.get(LANG, TRANSLATIONS['zh']).get(key, key)
    if args:
        return text.format(*args)
    return text

def format_size(size_bytes):
    """格式化文件大小显示"""
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:  # 字节
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.2f} {units[unit_index]}"

def format_speed(bytes_per_second):
    """格式化速度显示"""
    return f"{format_size(bytes_per_second)}/s"

def draw_progress_bar(current, total, width=30, start_time=None):
    """绘制进度条"""
    if total == 0:
        return "0.0% [" + " " * width + "] 0 B/0 B 0 B/s"
    
    # 计算百分比
    percentage = min(100.0, (current / total) * 100)
    
    # 计算进度条填充
    filled_width = int(width * current // total)
    bar = "█" * filled_width + "░" * (width - filled_width)
    
    # 计算速度
    speed_str = ""
    if start_time is not None:
        elapsed_time = time.time() - start_time
        if elapsed_time > 0:
            speed = current / elapsed_time
            speed_str = f" {format_speed(speed)}"
    
    # 格式化大小
    current_str = format_size(current)
    total_str = format_size(total)
    
    return f"{percentage:5.1f}% [{bar}] {current_str}/{total_str}{speed_str}"

def save_resume_info(filename, info):
    """保存断点续传信息"""
    resume_file = f"{filename}.resume"
    with open(resume_file, 'w', encoding='utf-8') as f:
        json.dump(info, f)

def load_resume_info(filename):
    """加载断点续传信息"""
    resume_file = f"{filename}.resume"
    if os.path.exists(resume_file):
        try:
            with open(resume_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def remove_resume_info(filename):
    """删除断点续传信息"""
    resume_file = f"{filename}.resume"
    if os.path.exists(resume_file):
        os.remove(resume_file)

def get_file_size(filename):
    """获取已下载文件大小"""
    if os.path.exists(filename):
        return os.path.getsize(filename)
    return 0


def save_multithread_resume_info(filename, info):
    """保存多线程断点续传信息"""
    resume_file = f"{filename}.mtresume"
    with open(resume_file, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2)

def load_multithread_resume_info(filename):
    """加载多线程断点续传信息"""
    resume_file = f"{filename}.mtresume"
    if os.path.exists(resume_file):
        try:
            with open(resume_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def remove_multithread_resume_info(filename):
    """删除多线程断点续传信息"""
    resume_file = f"{filename}.mtresume"
    if os.path.exists(resume_file):
        os.remove(resume_file)

def check_server_support_range(url, session):
    """检查服务器是否支持Range请求"""
    try:
        headers = {'Range': 'bytes=0-0'}
        response = session.head(url, headers=headers, timeout=10)
        return response.status_code == 206 or 'Accept-Ranges' in response.headers
    except:
        return False

def get_file_total_size(url, session):
    """获取文件总大小"""
    try:
        response = session.head(url, timeout=10)
        content_length = response.headers.get('Content-Length')
        if content_length:
            return int(content_length)
        else:
            # 如果HEAD请求不返回Content-Length，尝试GET请求
            response = session.get(url, stream=True, timeout=10)
            content_length = response.headers.get('Content-Length')
            response.close()
            return int(content_length) if content_length else 0
    except:
        return 0





def single_thread_download(url, filename, session, enable_resume=True):
    """单线程下载（原有逻辑的简化版本）"""
    global upload_interrupted
    
    # 首先检查文件是否已经完全下载（不管是否启用断点续传）
    if os.path.exists(filename):
        existing_size = get_file_size(filename)
        if existing_size > 0:
            # 获取文件总大小来检查是否已完全下载
            try:
                head_response = session.head(url, timeout=10)
                total_size = int(head_response.headers.get('Content-Length', 0))
                
                if total_size > 0 and existing_size >= total_size:
                    print(_('file_already_complete'))
                    # 如果启用了断点续传，清理断点续传信息
                    if enable_resume:
                        remove_resume_info(filename)
                    return True
                    
            except Exception:
                # 如果获取文件大小失败，继续正常的下载流程
                pass
    
    # 检查断点续传
    downloaded_size = 0
    mode = 'wb'
    headers = {}
    
    if enable_resume and os.path.exists(filename):
        downloaded_size = get_file_size(filename)
        if downloaded_size > 0:
            headers['Range'] = f'bytes={downloaded_size}-'
            mode = 'ab'
            print(_('detected_resume', format_size(downloaded_size)))
    
    print(_('single_thread_download'))
    
    try:
        response = session.get(url, stream=True, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 获取总大小
        if 'Content-Range' in response.headers:
            total_size = int(response.headers['Content-Range'].split('/')[-1])
        else:
            total_size = int(response.headers.get('Content-Length', 0)) + downloaded_size
        
        block_size = 2097152  # 2MB
        dl_count = downloaded_size
        start_time = time.time()
        last_update_time = start_time
        
        with open(filename, mode) as f:
            for chunk in response.iter_content(chunk_size=block_size):
                if upload_interrupted:
                    print(f"\n{_('download_interrupted')}")
                    return False
                
                f.write(chunk)
                dl_count += len(chunk)
                
                # 更新进度条
                current_time = time.time()
                if current_time - last_update_time >= 0.1:
                    progress_bar = draw_progress_bar(dl_count, total_size, start_time=start_time)
                    print(f'\r{progress_bar}', end='', flush=True)
                    last_update_time = current_time
        
        if not upload_interrupted:
            progress_bar = draw_progress_bar(total_size, total_size, start_time=start_time)
            print(f'\r{progress_bar}')
            print(f"\n{_('download_complete')}")
            # 下载完成，清理断点续传信息
            if enable_resume:
                remove_resume_info(filename)
            return True
            
    except Exception as e:
        print(f"\n{_('download_error', e)}")
        return False
    
    return False


def login_anonymous(session):
    try:
        r = session.post(
            url='https://www.wenshushu.cn/ap/login/anonymous',
            json={
                "dev_info": "{}"
            },
            timeout=30
        )
        r.raise_for_status()  # 检查HTTP状态码
        
        # 检查响应内容
        if not r.text.strip():
            raise Exception("服务器返回空响应")
        
        try:
            response_data = r.json()
        except ValueError as e:
            logging.error(f"JSON解析失败，响应内容: {r.text[:200]}")
            raise Exception(f"无法解析服务器响应: {e}")
        
        if 'data' not in response_data or 'token' not in response_data.get('data', {}):
            logging.error(f"响应格式错误: {response_data}")
            raise Exception("服务器响应格式错误，缺少token字段")
        
        return response_data['data']['token']
        
    except requests.exceptions.RequestException as e:
        logging.error(f"网络请求失败: {e}")
        raise Exception(f"匿名登录失败: 网络错误 - {e}")
    except Exception as e:
        logging.error(f"匿名登录失败: {e}")
        raise Exception(f"匿名登录失败: {e}")


def api_overseashow(session):
    """调用海外显示API"""
    try:
        r = session.post(
            url=_apiBaseUrl + '/ap/user/overseashow',
            json={
                "lang": "zh"
            },
            timeout=30
        )
        r.raise_for_status()
    except Exception as e:
        # 海外显示API失败不影响主要功能，记录日志即可
        logging.warning(f"海外显示API调用失败: {e}")
        pass

def display_login_instructions():
    """显示登录指导"""
    instructions = """获取X-TOKEN以便登录你自己的账号：
1. 打开浏览器，访问 https://www.wenshushu.cn
2. 登录你的账号
3. 按F12打开开发者工具
4. 切换到Network(网络)标签
5. 刷新页面或进行任意操作
6. 找到任意一个请求（打开过滤器（Filter）从Fetch/XHR类型中找，例如userinfo或storage或msg或current或ad等）
7. 查看Request Headers（请求标头），找到最下方的X-TOKEN字段
8. 复制X-TOKEN字段（大概率为27位，30或31开头的字符串）
9. 使用`python wss.py login "30xxxxxxxxxxxxxxxxxxxxxxxxx"`登录
10.使用账户上传或下载时不建议关闭获取token的浏览器，可能会被清除缓存导致token失效

Get X-TOKEN to log in to your own account:
1.Open the browser and visit https://www.wenshushu.cn
2.Log in to your account
3.Press F12 to open Developer Tools
4.Switch to the Network tab
5.Refresh the page or perform any action
6.Find any request (Open the Filter and look for it from the Fetch/XHR type, such as userinfo or storage or msg or current or ad)
7.Check the Request Headers and find the X-TOKEN field at the bottom
8.Copy the X-TOKEN field (highly probable strings starting with 27 bits, 30 or 31)
9.使用`python wss.py登录" 30xxxxxxxxxxxxxxxxxxxxxxxxxxxxx x"
10.When uploading or downloading an account, it is not recommended to close the browser to obtain the token. The cache may be cleared and the token is invalidated.
"""
    print(instructions)

def get_config_dir():
    """获取配置目录路径"""
    # 优先使用当前目录（向后兼容）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(current_dir, 'token.txt')) or os.path.exists(os.path.join(current_dir, 'user_tokens.json')):
        return current_dir
    
    # 使用用户配置目录
    if os.name == 'nt':  # Windows
        config_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'wssf')
    else:  # Unix/Linux/macOS
        config_dir = os.path.expanduser('~/.config/wssf')
    
    # 确保配置目录存在
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

def write_token(token):
    """保存token到文件"""
    config_dir = get_config_dir()
    with open(os.path.join(config_dir, 'token.txt'), 'w') as f:
        f.write(token)

    print(f"尝试使用 X-TOKEN: {token} 登录")
    return token


def save_user_token(token, user_info):
    """保存用户token到多用户文件"""
    config_dir = get_config_dir()
    tokens_file = os.path.join(config_dir, 'user_tokens.json')
    
    # 读取现有tokens
    if os.path.exists(tokens_file):
        try:
            with open(tokens_file, 'r', encoding='utf-8') as f:
                tokens_data = json.load(f)
        except:
            tokens_data = {}
    else:
        tokens_data = {}
    
    # 保存新token
    user_key = f"{user_info.get('name', '无名')}_{user_info.get('tel', user_info.get('email', 'unknown'))}"
    tokens_data[user_key] = {
        'token': token,
        'user_info': user_info,
        'last_login': time.time()
    }
    
    # 保存到文件
    with open(tokens_file, 'w', encoding='utf-8') as f:
        json.dump(tokens_data, f, ensure_ascii=False, indent=2)
    
    # 同时保存到单用户文件（兼容性）
    with open(os.path.join(config_dir, 'token.txt'), 'w') as f:
        f.write(token)
    
    return user_key

def load_user_tokens():
    """加载所有用户tokens"""
    config_dir = get_config_dir()
    tokens_file = os.path.join(config_dir, 'user_tokens.json')
    
    if os.path.exists(tokens_file):
        try:
            with open(tokens_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def get_current_user_info(session):
    """获取当前用户信息"""
    try:
        r = session.post(
            url=_apiBaseUrl + '/ap/user/userinfo',
            json={"plat": "pcweb"}
        )
        if r.json()["code"] == 0:
            return r.json()['data']
    except:
        pass
    return None

def display_user_tokens():
    """显示所有保存的用户tokens"""
    tokens_data = load_user_tokens()
    if not tokens_data:
        print(_('no_saved_user_tokens'))
        return False
    
    print(f"\n{_('saved_user_accounts')}:")
    print("-" * 50)
    for i, (user_key, data) in enumerate(tokens_data.items(), 1):
        user_info = data['user_info']
        last_login = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['last_login']))
        print(f"{i}. {user_info.get('name', '无名')} ({user_info.get('tel', user_info.get('email', 'unknown'))})")
        print(f"   {_('last_login')}: {last_login}")
    print("-" * 50)
    return True

def select_user_token():
    """让用户选择一个token"""
    tokens_data = load_user_tokens()
    if not tokens_data:
        return None
    
    display_user_tokens()
    
    try:
        choice = input(f"\n{_('select_account_number')}: ").strip()
        if choice == '0':
            return None
        
        choice_num = int(choice)
        user_keys = list(tokens_data.keys())
        
        if 1 <= choice_num <= len(user_keys):
            selected_key = user_keys[choice_num - 1]
            return tokens_data[selected_key]['token']
        else:
            print(_('invalid_choice'))
            return None
    except:
        print(_('invalid_input'))
        return None


def remove_invalid_token(token_to_remove):
    """从user_tokens.json中删除无效的token"""
    config_dir = get_config_dir()
    tokens_file = os.path.join(config_dir, 'user_tokens.json')
    
    if not os.path.exists(tokens_file):
        return False
    
    try:
        with open(tokens_file, 'r', encoding='utf-8') as f:
            tokens_data = json.load(f)
        
        # 查找并删除匹配的token
        user_key_to_remove = None
        for user_key, data in tokens_data.items():
            if data['token'] == token_to_remove:
                user_key_to_remove = user_key
                break
        
        if user_key_to_remove:
            user_info = tokens_data[user_key_to_remove]['user_info']
            del tokens_data[user_key_to_remove]
            
            # 保存更新后的数据
            with open(tokens_file, 'w', encoding='utf-8') as f:
                json.dump(tokens_data, f, ensure_ascii=False, indent=2)
            
            print(f"{_('removed_invalid_account')}: {user_info.get('name', '无名')}")
            return True
        
    except Exception as e:
        print(f"{_('operation_failed')}: {e}")
    
    return False


def try_login(session):
    """尝试登录"""
    config_dir = get_config_dir()
    token_file = os.path.join(config_dir, 'token.txt')
    
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            token = f.read().strip()
        print(f"尝试使用已保存的 X-TOKEN: {token} 登录")
        session.headers['X-TOKEN'] = token
        if get_current_user_info(session):
            print()
            return True
    
    print("未找到有效token，使用匿名登录")
    try:
        session.headers['X-TOKEN'] = login_anonymous(session)
        api_overseashow(session)
    except Exception as e:
        logging.error(f"匿名登录失败: {e}")
        raise
    return False

def patch_session_headers(session):
    """设置session headers"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0'
    ]
    ua = random.choice(user_agents)
    common_headers = {
        "Origin": "https://www.wenshushu.cn",
        "Priority": "u=1, i",
        "Prod": "com.wenshushu.web.pc",
        "Referer": "https://www.wenshushu.cn/",
        "Sec-Ch-Ua": '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": 'empty',
        "Sec-Fetch-Mode": 'cors',
        "Sec-Fetch-Site": 'same-origin',
        "User-Agent": ua,
        "Accept-Language": "zh-CN, en-um;q=0.9"
    }
    session.headers.update(common_headers)


def download(url, enable_resume=False, session=None, num_threads=1):
    global LANG
    if session is None:
        raise ValueError("Session is required")
    s = session
    
    def get_tid(token):
        r = s.post(
            url='https://www.wenshushu.cn/ap/task/token',
            json={
                'token': token
            }
        )
        return r.json()['data']['tid']

    def mgrtask(tid):
        global LANG
        r = s.post(
            url='https://www.wenshushu.cn/ap/task/mgrtask',
            json={
                'tid': tid,
                'password': ''
            }
        )
        rsp = r.json()
        expire = rsp['data']['expire']
        days, remainder = divmod(int(float(expire)), 3600*24)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(_('file_expires', days, hours, minutes, seconds))

        file_size = rsp['data']['file_size']
        print(_('file_size', round(int(file_size)/1024**2,2)))
        return rsp['data']['boxid'], rsp['data']['ufileid']  # pid

    def list_file(tid):
        global LANG
        bid, pid = mgrtask(tid)
        r = s.post(
            url='https://www.wenshushu.cn/ap/ufile/list',
            json={
                "start": 0,
                "sort": {
                    "name": "asc"
                },
                "bid": bid,
                "pid": pid,
                "type": 1,
                "options": {
                    "uploader": "true"
                },
                "size": 50
            }
        )
        rsp = r.json()
        filelist = rsp['data']['fileList']
        
        # 支持多文件下载
        for i, file_info in enumerate(filelist):
            filename = file_info['fname']
            fid = file_info['fid']
            print(f'[{i + 1}/{len(filelist)}] {_("file_name", filename)}')
            sign(bid, fid, filename)

    def down_handle(url, filename):
        global LANG
        
        # 根据线程数选择下载方式
        if num_threads > 1:
            # 使用智能多线程下载
            success = smart_multithread_download(url, filename, s, num_threads, enable_resume)
            if not success and not upload_interrupted:
                print("多连接下载失败，尝试单线程下载...")
                return single_thread_download(url, filename, s, enable_resume)
            return success
        else:
            # 使用单线程下载
            return single_thread_download(url, filename, s, enable_resume)
    


    def sign(bid, fid, filename):
        global LANG
        r = s.post(
            url='https://www.wenshushu.cn/ap/dl/sign',
            json={
                'consumeCode': 0,
                'type': 1,
                'ufileid': fid
            }
        )
        if r.json()['data']['url'] == "" and \
                r.json()['data']['ttNeed'] != 0:
            print(_('share_traffic_insufficient'))
            sys.exit(0)
        url = r.json()['data']['url']
        down_handle(url, filename)

    if len(url.split('/')[-1]) == 16:
        token = url.split('/')[-1]
        tid = get_tid(token)
    elif len(url.split('/')[-1]) == 11:
        tid = url.split('/')[-1]

    list_file(tid)


def upload(filePath, pwd="", session=None):
    global LANG
    if session is None:
        raise ValueError("Session is required")
    s = session
    
    # 目录处理相关函数
    def make_tar_gz(output_filename, source_dir):
        with tarfile.open(output_filename, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))

    def get_readable_size(file_path):
        size = os.path.getsize(file_path)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"
    
    # 处理目录上传
    need_del_file = False
    original_path = filePath
    
    if not os.path.exists(filePath):
        logging.error(f'{filePath} 不存在')
        return
        
    if os.path.isdir(filePath):
        filePath = os.path.normpath(filePath)
        new_filename = os.path.basename(filePath) + '.tar.gz'
        start_time = time.time()
        logging.warning(f'{filePath} 是一个目录，自动压缩为: {new_filename}')
        make_tar_gz(new_filename, filePath)
        end_time = time.time()
        logging.info(f"压缩耗时: {end_time - start_time:.4f} 秒，大小: {get_readable_size(new_filename)}")
        filePath = new_filename
        need_del_file = True
    elif os.path.isfile(filePath):
        need_del_file = False
    
    chunk_size = 2097152
    file_size = os.path.getsize(filePath)
    ispart = True if file_size > chunk_size else False

    def read_file(block_size=chunk_size):
        partnu = 0
        with open(filePath, "rb") as f:
            while True:
                block = f.read(block_size)
                partnu += 1
                if block:
                    yield block, partnu
                else:
                    return

    def sha1_str(s):
        cm = hashlib.sha1(s.encode()).hexdigest()
        return cm

    def calc_file_hash(hashtype, block=None):
        read_size = chunk_size if ispart else None
        if not block:
            with open(filePath, 'rb') as f:
                block = f.read(read_size)
        if hashtype == "MD5":
            hash_code = hashlib.md5(block).hexdigest()
        elif hashtype == "SHA1":
            hash_code = hashlib.sha1(block).hexdigest()
        return hash_code

    def get_epochtime():
        global LANG
        r = s.get(
            url='https://www.wenshushu.cn/ag/time',
            headers={
                "Prod": "com.wenshushu.web.pc",
                "Referer": "https://www.wenshushu.cn/"
            }
        )
        rsp = r.json()
        return rsp["data"]["time"]  # epochtime expires in 60s

    def get_cipherheader(epochtime, token, data):
        global LANG
        # cipherMethod: DES/CBC/PKCS7Padding
        json_dumps = json.dumps(data, ensure_ascii=False)
        md5_hash_code = hashlib.md5((json_dumps+token).encode()).hexdigest()
        base58_hash_code = base58.b58encode(md5_hash_code)
        key_iv = (
            # 时间戳逆序取5位并作为时间戳字串索引再次取值，最后拼接"000"
            "".join([epochtime[int(i)] for i in epochtime[::-1][:5]]) + "000"
        ).encode()
        cipher = DES.new(key_iv, DES.MODE_CBC, key_iv)
        cipherText = cipher.encrypt(
            Padding.pad(base58_hash_code, DES.block_size, style="pkcs7")
        )
        return base64.b64encode(cipherText)

    def storage():
        global LANG
        r = s.post(
            url='https://www.wenshushu.cn/ap/user/storage',
            json={}
        )
        rsp = r.json()
        rest_space = int(rsp['data']['rest_space'])
        send_space = int(rsp['data']['send_space'])
        storage_space = rest_space + send_space
        print(_('used_space',
            round(send_space / 1024**3, 2),
            round(rest_space / 1024**3, 2),
            round(storage_space / 1024**3, 2)
        ))

    def userinfo():
        global LANG
        s.post(
            url='https://www.wenshushu.cn/ap/user/userinfo',
            json={"plat": "pcweb"}
        )

    def addsend():
        global LANG
        userinfo()
        storage()
        epochtime = get_epochtime()
        req_data = {
            "sender": "",
            "remark": "",
            "isextension": False,
            "notSaveTo": False,
            "notDownload": False,
            "notPreview": False,
            "downPreCountLimit": 0,
            "trafficStatus": 0,
            "pwd": pwd,
            "expire": "1",
            "recvs": [
                "social",
                "public"
            ],
            "file_size": file_size,
            "file_count": 1,
            "fileDisplay": 0,
            "task_traffic_limit": ""
        }
        # POST的内容在服务端会以字串形式接受然后直接拼接X-TOKEN，不会先反序列化JSON字串再拼接
        # 加密函数中的JSON序列化与此处的JSON序列化的字串形式两者必须完全一致，否则校验失败
        r = s.post(
            url='https://www.wenshushu.cn/ap/task/addsend',
            json=req_data,
            headers={
                "A-code": get_cipherheader(epochtime, s.headers['X-TOKEN'], req_data),
                "Prod": "com.wenshushu.web.pc",
                "Referer": "https://www.wenshushu.cn/",
                "Origin": "https://www.wenshushu.cn",
                "Req-Time": epochtime,
            }
        )
        rsp = r.json()
        if rsp["code"] == 1021:
            print(_('too_fast', rsp["message"]))
            sys.exit(0)
        data = rsp["data"]
        assert data, _('need_verification')
        bid, ufileid, tid = data["bid"], data["ufileid"], data["tid"]
        upId = get_up_id(bid, ufileid, tid, file_size)
        return bid, ufileid, tid, upId

    def get_up_id(bid: str, ufileid: str, tid: str, file_size: int):
        global LANG
        r = s.post(
            url="https://www.wenshushu.cn/ap/uploadv2/getupid",
            json={
                "preid": ufileid,
                "boxid": bid,
                "linkid": tid,
                "utype": "sendcopy",
                "originUpid": "",
                "length": file_size,
                "count": 1
            }
        )
        return r.json()["data"]["upId"]

    def psurl(fname, upId, file_size, partnu=None):
        global LANG
        payload = {
            "ispart": ispart,
            "fname": fname,
            "fsize": file_size,
            "upId": upId,
        }
        if ispart:
            payload["partnu"] = partnu
        r = s.post(
            url="https://www.wenshushu.cn/ap/uploadv2/psurl",
            json=payload
        )
        rsp = r.json()
        url = rsp["data"]["url"]  # url expires in 600s (10 minutes)
        return url

    def copysend(boxid, taskid, preid):
        global LANG
        r = s.post(
            url='https://www.wenshushu.cn/ap/task/copysend',
            json={
                'bid': boxid,
                'tid': taskid,
                'ufileid': preid
            }
        )
        rsp = r.json()
        print(_('personal_link', rsp['data']['mgr_url']))
        pwd_info = f", 取件码：{pwd}" if pwd else ""
        print(_('public_link', rsp['data']['public_url']) + pwd_info)

    def fast():
        global LANG
        boxid, preid, taskid, upId = addsend()
        cm1, cs1 = calc_file_hash("MD5"), calc_file_hash("SHA1")
        cm = sha1_str(cm1)
        name = os.path.basename(filePath)

        payload = {
            "hash": {
                "cm1": cm1,  # MD5
                "cs1": cs1,  # SHA1
            },
            "uf": {
                "name": name,
                "boxid": boxid,
                "preid": preid
            },
            "upId": upId
        }

        if not ispart:
            payload['hash']['cm'] = cm  # 把MD5用SHA1加密
        for i in range(2):
            r = s.post(
                url='https://www.wenshushu.cn/ap/uploadv2/fast',
                json=payload
            )
            rsp = r.json()
            can_fast = rsp["data"]["status"]
            ufile = rsp['data']['ufile']
            if can_fast and not ufile:
                hash_codes = ''
                for block, partnu in read_file():
                    hash_codes += calc_file_hash("MD5", block)
                payload['hash']['cm'] = sha1_str(hash_codes)
            elif can_fast and ufile:
                print(_('instant_transfer', name))
                getprocess(upId)
                copysend(boxid, taskid, preid)
                sys.exit(0)

        return name, taskid, boxid, preid, upId

    def getprocess(upId: str):
        global LANG
        while True:
            r = s.post(
                url="https://www.wenshushu.cn/ap/ufile/getprocess",
                json={
                    "processId": upId
                }
            )
            if r.json()["data"]["rst"] == "success":
                return True
            time.sleep(1)

    def complete(fname, upId, tid, boxid, preid):
        global LANG
        s.post(
            url="https://www.wenshushu.cn/ap/uploadv2/complete",
            json={
                "ispart": ispart,
                "fname": fname,
                "upId": upId,
                "location": {
                    "boxid": boxid,
                    "preid": preid
                }
            }
        )
        copysend(boxid, tid, preid)

    def file_put(psurl_args, fn, offset=0, read_size=chunk_size, chunk_index=None):
        global LANG
        # 检查是否被中断
        if upload_interrupted:
            return None
            
        with open(fn, "rb") as fio:
            fio.seek(offset)
            try:
                # 设置较短的超时时间
                response = requests.put(url=psurl(*psurl_args), data=fio.read(read_size), timeout=30)
                response.raise_for_status()
                return chunk_index  # 返回成功上传的分块索引
            except Exception as e:
                if not upload_interrupted:
                    print(f'分块 {chunk_index} 上传失败: {e}')
                raise

    def upload_main():
        global LANG
        fname, tid, boxid, preid, upId = fast()
        
        if ispart:
            print(_('file_chunked_upload'))
            total_chunks = (file_size + chunk_size - 1)//chunk_size
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_list = []
                for i in range(total_chunks):
                    # 检查是否被中断
                    if upload_interrupted:
                        break
                        
                    ul_size = chunk_size if chunk_size*(i+1) <= file_size \
                        else file_size % chunk_size
                    future_list.append(executor.submit(
                        file_put, [fname, upId, ul_size, i+1],
                        filePath, chunk_size*i, ul_size, i+1
                    ))
                
                completed_futures = set()
                count = 0
                start_time = time.time()
                
                try:
                    # 非阻塞式检查完成的任务
                    while len(completed_futures) < len(future_list) and not upload_interrupted:
                        for future in future_list:
                            if future in completed_futures:
                                continue
                                
                            if future.done():
                                completed_futures.add(future)
                                try:
                                    result = future.result()
                                    if result is not None:
                                        count += 1
                                        # 计算已上传大小
                                        uploaded_size = count * chunk_size
                                        if count == total_chunks:
                                            uploaded_size = file_size
                                        
                                        progress_bar = draw_progress_bar(uploaded_size, file_size, start_time=start_time)
                                        print(f'\r{progress_bar}', end='', flush=True)
                                    
                                except Exception as e:
                                    if not upload_interrupted:
                                        print(f'分块上传失败: {e}')
                        
                        # 短暂休眠避免CPU占用过高
                        time.sleep(0.1)
                    
                    # 检查是否被中断
                    if upload_interrupted:
                        print()  # 换行
                        print(_('upload_cancelled'))
                        # 强制取消所有未完成的任务
                        for future in future_list:
                            future.cancel()
                        return
                    
                    # 上传完成
                    if count >= total_chunks:
                        print()  # 换行
                        print(_('upload_complete'))
                            
                except Exception as e:
                    if not upload_interrupted:
                        print(_('upload_error', e))
                    raise
        else:
            print(_('file_single_upload'))
            try:
                file_put([fname, upId, file_size], filePath, 0, file_size)
                if not upload_interrupted:
                    print(_('upload_complete_100'))
            except KeyboardInterrupt:
                print()  # 换行
                print(_('upload_cancelled'))
                return
        
        # 检查是否被中断，如果被中断则不执行完成操作
        if upload_interrupted:
            return

        complete(fname, upId, tid, boxid, preid)
        getprocess(upId)
        
        # 对于目录上传，上传完成后需要删除临时文件
        if need_del_file:
            os.remove(filePath)
            logging.warning(f'删除临时文件: {filePath}')
            
    upload_main()





def get_bilingual_help():
    """获取双语帮助文本"""
    help_text = """
文叔叔完整版工具 / Wenshushu Enhanced CLI Tool

使用方法 / Usage:
  python wss.py <命令/command> [选项/options]

命令 / Commands:
  upload/u <文件/路径>   上传文件或目录 / Upload file or directory
  download/d <链接>     下载文件 / Download file
  login [TOKEN]        登录账户管理 / Login account management
  unlogin             退出当前账户 / Logout current account

选项 / Options:
  -h, --help           显示帮助信息 / Show help message
  -e, --en             使用英文界面 / Use English interface
  -l, --login          使用已登录账户 / Use logged in account
  -c, --continue       启用断点续传(仅下载) / Enable resume download
  -t, --threads <数量> 设置下载线程数(1-16) / Set download threads (1-16)
  -k, --key <取件码>   设置取件码(4位数字) / Set pickup code (4 digits)
  -r, --randomkey      随机生成取件码 / Generate random pickup code
  -p, --proxy <地址>   设置代理服务器 / Set proxy server

示例 / Examples:
  python wss.py u file.txt                     # 上传文件 / Upload file
  python wss.py upload folder/                 # 上传目录 / Upload directory
  python wss.py u file.txt -k 1234             # 上传并设置取件码 / Upload with pickup code
  python wss.py upload file.txt -r             # 上传并随机取件码 / Upload with random code
  python wss.py u file.txt -l                  # 使用已登录账户上传 / Upload with logged in account
  python wss.py d "链接" -c                    # 断点续传下载 / Resume download
  python wss.py d "链接" -t 8                  # 8线程下载 / Download with 8 threads
  python wss.py d "链接" -t 4 -c               # 4线程断点续传下载 / 4-thread resume download
  python wss.py download "链接" -p http://proxy # 使用代理下载 / Download via proxy
  python wss.py u file.txt -e                  # 使用英文界面 / Use English interface
  python wss.py login                          # 账户登录管理 / Account login management
  python wss.py login "30Bxxxxx"               # 直接TOKEN登录 / Direct TOKEN login
  python wss.py unlogin                        # 退出账户 / Logout account

多用户功能 / Multi-user Features:
  - 支持保存多个用户账户 / Support multiple user accounts
  - 登录时可选择已保存账户 / Choose from saved accounts when login
  - 自动保存用户信息和登录时间 / Auto save user info and login time
  - 默认使用匿名账户上传下载 / Default anonymous upload/download

多线程下载功能 / Multi-thread Download Features:
  - IDM风格多连接并行下载 / IDM-style multi-connection parallel download
  - 支持1-16线程并行下载 / Support 1-16 threads parallel download
  - 每个线程独立HTTP连接 / Each thread uses independent HTTP connection
  - 自动适配Range和非Range服务器 / Auto adapt Range and non-Range servers
  - 智能分块和故障转移 / Smart chunking and failover
  - 多连接断点续传支持 / Multi-connection resume support
  - 实时连接状态显示 / Real-time connection status display

注意 / Notes:
  - 目录上传会自动压缩为tar.gz / Directories are auto-compressed to tar.gz
  - 断点续传支持单线程和多线程 / Resume works for both single and multi-thread
  - 取件码限制4位数字 / Pickup code limited to 4 digits
  - 登录后享有更大存储空间 / Larger storage after login
  - 多线程下载需要服务器支持Range请求 / Multi-thread requires server Range support
"""
    return help_text










def smart_multithread_download(url, filename, session, num_threads=4, enable_resume=True):
    """智能多线程下载器 - 自动适应服务器类型"""
    global total_downloaded, chunk_download_status, upload_interrupted, active_connections, LANG
    
    # 重置全局状态
    total_downloaded = 0
    chunk_download_status = {}
    active_connections = {}
    
    print(_("idm_style_download", num_threads))
    
    # 检测服务器能力
    server_supports_range = check_server_support_range(url, session)
    if server_supports_range:
        print(_('server_range_support_yes'))
    else:
        print(_('server_range_support_no'))
    
    # 直接使用parallel_stream_download处理所有情况
    return parallel_stream_download(url, filename, session, num_threads, enable_resume)




def parallel_stream_download(url, filename, session, num_threads=4, enable_resume=True):
    """真正的IDM风格分块下载 - 8个线程下载不同部分然后合并"""
    global total_downloaded, upload_interrupted, active_connections, download_lock
    
    total_downloaded = 0
    active_connections = {}
    
    # 先发起一个GET请求获取文件信息
    try:
        response = session.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        # 获取文件总大小（与单线程下载使用相同方法）
        total_size = int(response.headers.get('Content-Length', 0))
        response.close()
        
        if total_size <= 0:
            print("无法获取文件大小，回退到单线程下载")
            return single_thread_download(url, filename, session, enable_resume)
        
    except Exception as e:
        print(f"获取文件信息失败: {e}，回退到单线程下载")
        return single_thread_download(url, filename, session, enable_resume)
    
    # 检查是否已经有部分块文件
    temp_dir = f"{filename}.idm_parts"
    
    # 首先检查主文件是否已经完全下载
    if enable_resume and os.path.exists(filename):
        existing_size = get_file_size(filename)
        if existing_size >= total_size:
            print(_('file_already_complete'))
            # 清理可能存在的临时文件
            if os.path.exists(temp_dir):
                try:
                    for file in os.listdir(temp_dir):
                        os.remove(os.path.join(temp_dir, file))
                    os.rmdir(temp_dir)
                except:
                    pass
            return True
    
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # 计算每个块的大小
    chunk_size = total_size // num_threads
    remaining = total_size % num_threads
    
    # 为每个线程分配下载任务
    download_tasks = []
    current_pos = 0
    
    for i in range(num_threads):
        start_pos = current_pos
        if i == num_threads - 1:
            # 最后一个线程下载剩余的所有数据
            end_pos = total_size - 1
        else:
            end_pos = current_pos + chunk_size - 1
        
        chunk_filename = os.path.join(temp_dir, f"part_{i:02d}.tmp")
        download_tasks.append({
            'thread_id': i,
            'start_pos': start_pos,
            'end_pos': end_pos,
            'chunk_size': end_pos - start_pos + 1,
            'chunk_file': chunk_filename,
            'downloaded': 0,
            'completed': False
        })
        current_pos = end_pos + 1
    
    # 检查断点续传
    start_time = time.time()
    resume_info = []
    has_resume = False
    for task in download_tasks:
        if os.path.exists(task['chunk_file']):
            existing_size = get_file_size(task['chunk_file'])
            if existing_size > 0:
                task['downloaded'] = existing_size
                total_downloaded += existing_size
                resume_info.append(f"{_('chunk')}{task['thread_id']+1}: {format_size(existing_size)}")
                has_resume = True
            else:
                resume_info.append(f"{_('chunk')}{task['thread_id']+1}: 0 B")
        else:
            resume_info.append(f"{_('chunk')}{task['thread_id']+1}: 0 B")
    
    if has_resume:
        # 将块信息格式化为固定宽度的列对齐显示
        chunk_lines = []
        for i in range(0, len(resume_info), 4):
            chunk_group = resume_info[i:i+4]
            # 使用固定宽度格式化，确保每列对齐
            formatted_chunks = []
            for chunk in chunk_group:
                formatted_chunks.append(f"{chunk:<25}")  # 左对齐，宽度25
            chunk_lines.append("".join(formatted_chunks))  # 直接拼接，不加额外空格
        
        # 显示断点续传信息
        print(f"{_('resume_detected')}:")  # 标题后直接换行
        for line in chunk_lines:
            print(line.rstrip())  # 所有行都左对齐显示
        print(f"{_('downloaded_so_far')}: {format_size(total_downloaded)}")
    
    print("\n" * 4)  # 打印4个空行

    def download_chunk_thread(task):
        """下载单个块的线程函数"""
        thread_id = task['thread_id']
        start_pos = task['start_pos'] + task['downloaded']  # 断点续传
        end_pos = task['end_pos']
        chunk_file = task['chunk_file']
        
        if task['downloaded'] >= task['chunk_size']:
            task['completed'] = True
            return
        
        # 创建独立session
        thread_session = requests.Session()
        thread_session.headers.update(session.headers)
        thread_session.proxies.update(session.proxies)
        
        try:
            # 更新连接状态
            with download_lock:
                active_connections[thread_id] = {
                    'status': 'connecting',
                    'downloaded': task['downloaded'],
                    'total_chunk': task['chunk_size'],
                    'speed': 0,
                    'last_update': time.time()
                }
            
            # 尝试Range请求，如果失败则用其他方法
            try:
                headers = {'Range': f'bytes={start_pos}-{end_pos}'}
                response = thread_session.get(url, headers=headers, stream=True, timeout=30)
                
                if response.status_code not in [206, 200]:
                    raise Exception(f"Range请求失败: {response.status_code}")
                
                # 检查是否真的支持Range
                if response.status_code == 200:
                    use_skip_method = True
                else:
                    use_skip_method = False
                    
            except Exception as e:
                response = thread_session.get(url, stream=True, timeout=30)
                use_skip_method = True
            
            response.raise_for_status()
            
            with download_lock:
                active_connections[thread_id]['status'] = 'downloading'
            
            # 打开块文件进行写入
            with open(chunk_file, 'ab' if task['downloaded'] > 0 else 'wb') as f:
                if task['downloaded'] > 0:
                    f.seek(task['downloaded'])
                
                bytes_to_skip = start_pos if use_skip_method else 0
                bytes_to_download = task['chunk_size'] - task['downloaded']
                downloaded_this_chunk = task['downloaded']
                
                last_speed_time = time.time()
                last_downloaded = downloaded_this_chunk
                
                for data in response.iter_content(chunk_size=32768):
                    if upload_interrupted:
                        break
                    
                    # 如果需要跳过数据（服务器不支持Range）
                    if use_skip_method and bytes_to_skip > 0:
                        skip_amount = min(len(data), bytes_to_skip)
                        data = data[skip_amount:]
                        bytes_to_skip -= skip_amount
                        if not data:
                            continue
                    
                    if data:
                        # 检查是否超出块大小
                        if downloaded_this_chunk + len(data) > task['chunk_size']:
                            # 截断数据到块边界
                            remaining_bytes = task['chunk_size'] - downloaded_this_chunk
                            data = data[:remaining_bytes]
                        
                        if data:
                            f.write(data)
                            f.flush()
                            downloaded_this_chunk += len(data)
                            
                            # 更新统计
                            with download_lock:
                                global total_downloaded
                                old_downloaded = task['downloaded']
                                task['downloaded'] = downloaded_this_chunk
                                total_downloaded += (downloaded_this_chunk - old_downloaded)
                                
                                active_connections[thread_id]['downloaded'] = downloaded_this_chunk
                                active_connections[thread_id]['last_update'] = time.time()
                                
                                # 计算速度
                                current_time = time.time()
                                if current_time - last_speed_time >= 1.0:
                                    speed = (downloaded_this_chunk - last_downloaded) / (current_time - last_speed_time)
                                    active_connections[thread_id]['speed'] = speed
                                    last_speed_time = current_time
                                    last_downloaded = downloaded_this_chunk
                        
                        # 检查是否完成
                        if downloaded_this_chunk >= task['chunk_size']:
                            break
            
            response.close()
            task['completed'] = True
            
        except Exception as e:
            logging.error(f"块下载线程 {thread_id} 错误: {e}")
        finally:
            with download_lock:
                if thread_id in active_connections:
                    active_connections[thread_id]['status'] = 'finished'
    
    # 启动所有下载线程
    print(_('starting_threads', num_threads))
    threads = []
    for task in download_tasks:
        if not task['completed']:
            thread = threading.Thread(target=download_chunk_thread, args=(task,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
    
    # 监控下载进度
    last_update_time = time.time()

    while threads and not upload_interrupted:
        time.sleep(0.5)
        
        current_time = time.time()
        if current_time - last_update_time >= 1.0:
            elapsed = current_time - start_time
            speed = (total_downloaded / elapsed) if elapsed > 0 else 0
            
            # 显示进度条
            progress_bar = draw_progress_bar(total_downloaded, total_size, start_time=start_time)
            
            # 显示活跃连接
            active_count = sum(1 for conn in active_connections.values() 
                             if conn['status'] == 'downloading')
            total_speed = sum(conn.get('speed', 0) for conn in active_connections.values())
            
            # 准备块状态和速度信息
            chunk_info = []
            for i, task in enumerate(download_tasks):
                if task['completed']:
                    chunk_info.append(f"{_('chunk')}{i+1}:✓")
                else:
                    progress = (task['downloaded'] / task['chunk_size']) * 100 if task['chunk_size'] > 0 else 0
                    conn_speed = active_connections.get(i, {}).get('speed', 0)
                    if conn_speed > 0:
                        chunk_info.append(f"{_('chunk')}{i+1}:{progress:.0f}%({format_speed(conn_speed)})")
                    else:
                        chunk_info.append(f"{_('chunk')}{i+1}:{progress:.0f}%")
            
            # 将块状态分组，每行4个，使用固定宽度对齐
            chunk_lines = []
            for i in range(0, len(chunk_info), 4):
                chunk_group = chunk_info[i:i+4]
                # 使用固定宽度格式化，确保每列对齐
                formatted_chunks = []
                for chunk in chunk_group:
                    formatted_chunks.append(f"{chunk:<25}")  # 左对齐，宽度25
                chunk_lines.append("".join(formatted_chunks))  # 直接拼接，不加额外空格
            
            # 计算需要清除的行数（总进度条1行 + 块状态行数）
            total_lines = 1 + len(chunk_lines)
            
            # 简单的清屏方法：向上移动并清除
            if last_update_time != start_time:  # 不是第一次更新
                print(f'\033[{total_lines}A', end='')  # 向上移动到开始位置
            
            # 第一行：显示总进度条
            print(f'\033[K{progress_bar} [{_("active_connections")}: {active_count}/{num_threads}] [{format_speed(total_speed)}]')
            
            # 后续行：每行显示4个块的状态
            for line in chunk_lines:
                print(f'\033[K{line.rstrip()}')
            
            # 保持光标在最后一行
            print(end='', flush=True)

            last_update_time = current_time

        # 移除已完成的线程
        threads = [t for t in threads if t.is_alive()]

    # 等待所有线程完成
    for thread in threads:
        thread.join(timeout=5)
    
    if upload_interrupted:
        print(f"\n{_('download_interrupted')}")
        return False
    
    # 检查所有块是否下载完成
    all_completed = all(task['completed'] for task in download_tasks)
    if not all_completed:
        print(f"\n{_('partial_chunks_incomplete')}")
        for i, task in enumerate(download_tasks):
            if not task['completed']:
                print(f"  块{i+1}: {format_size(task['downloaded'])}/{format_size(task['chunk_size'])}")
    
    print(f'\n{_("merging_chunks", num_threads)}')
    
    # 合并所有块文件
    try:
        with open(filename, 'wb') as output_file:
            for i, task in enumerate(download_tasks):
                chunk_file = task['chunk_file']
                if os.path.exists(chunk_file):
                    with open(chunk_file, 'rb') as chunk:
                        while True:
                            data = chunk.read(1024*1024)  # 1MB chunks
                            if not data:
                                break
                            output_file.write(data)
                else:
                    print(_("chunk_file_missing", i+1))
        
        # 验证最终文件大小
        final_size = get_file_size(filename)
        print(_("merge_complete", format_size(final_size)))
        
        if final_size == total_size:
            print(_("integrity_verified"))
            # 清理临时文件
            try:
                for task in download_tasks:
                    if os.path.exists(task['chunk_file']):
                        os.remove(task['chunk_file'])
                os.rmdir(temp_dir)
                print(_("temp_files_cleaned"))
            except:
                print(_("temp_files_clean_failed"))
        else:
            print(_("file_size_mismatch", format_size(total_size), format_size(final_size)))
        
        return True
        
    except Exception as e:
        print(_("merge_error", e))
        traceback.print_exc()
        return False


def main():
    """主入口函数"""
    global LANG, current_operation, resume_enabled
    
    # 自定义帮助处理
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help']):
        print(get_bilingual_help())
        sys.exit(0)
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(add_help=False)  # 禁用默认help
    
    # 添加位置参数 - 命令
    parser.add_argument('command', nargs='?', choices=['upload', 'u', 'download', 'd', 'login', 'unlogin'], 
                       help='Command to execute')
    
    # 添加位置参数 - 文件路径或URL或TOKEN
    parser.add_argument('target', nargs='?', help='File path, download URL, or login TOKEN')
    
    # 添加选项参数
    parser.add_argument('-h', '--help', action='store_true', help='Show help message')
    parser.add_argument('-e', '--en', action='store_true', help='Use English interface')
    parser.add_argument('-l', '--login', action='store_true', help='Use logged in account')
    parser.add_argument('-c', '--continue', dest='resume', action='store_true', help='Enable resume download')
    parser.add_argument('-t', '--threads', type=int, help='Set download threads (1-16)', default=1)
    parser.add_argument('-k', '--key', help='Set pickup code (4 digits)')
    parser.add_argument('-r', '--randomkey', action='store_true', help='Generate random pickup code')
    parser.add_argument('-p', '--proxy', help='Set proxy server')
    
    try:
        args = parser.parse_args()
    except SystemExit:
        # 需要先设置语言才能使用翻译函数
        # 检查是否有-e参数
        temp_lang = 'en' if '-e' in sys.argv or '--en' in sys.argv else 'zh'
        LANG = temp_lang
        print(_('parameter_error'))
        sys.exit(1)
    
    # 处理帮助
    if args.help:
        print(get_bilingual_help())
        sys.exit(0)
    
    # 设置语言
    LANG = 'en' if args.en else 'zh'
    
    # 处理login命令
    if args.command == 'login':
        if args.target:
            # 提供了token
            token = args.target
            s = requests.Session()
            patch_session_headers(s)
            s.headers['X-TOKEN'] = token
            user_info = get_current_user_info(s)
            if user_info:
                # 保存token和用户信息
                user_key = save_user_token(token, user_info)
                print(f"{_('login_success_saved')} ({_('username')}: {user_info.get('name', '无名')})")
            else:
                print(_('login_failed'))
        else:
            # 没有提供token
            # 首先显示当前登录状态
            config_dir = get_config_dir()
            token_file = os.path.join(config_dir, 'token.txt')
            
            print(_('current_login_status'))
            if os.path.exists(token_file):
                with open(token_file, 'r') as f:
                    current_token = f.read().strip()
                s = requests.Session()
                patch_session_headers(s)
                s.headers['X-TOKEN'] = current_token
                user_info = get_current_user_info(s)
                if user_info:
                    print(_('logged_in', user_info.get('name', '无名')))
                    print(f"{_('currently_logged_user')}:")
                    print(f"{_('username')}: {user_info.get('name', '无名')}")
                    if user_info.get('email'):
                        print(f"{_('email')}: {user_info['email']}")
                    if user_info.get('tel'):
                        print(f"{_('phone')}: {user_info['tel']}")
                    print()
                else:
                    print(_('current_token_invalid'))
                    # 清理无效token
                    remove_invalid_token(current_token)
                    print(_('token_cleaned'))
                    print()
            else:
                print(_('not_logged_in'))
                print()
            
            # 显示可选操作
            print(_('login_options'))
            print(_('enter_new_token'))
            print(_('select_saved_account'))
            print(_('view_tutorial'))
            print(_('cancel'))
            
            try:
                choice = input(f"\n{_('please_choose')}: ").strip()
                
                if choice == '1':
                    # 输入新token
                    new_token = input(f"{_('enter_token')}: ").strip()
                    if new_token:
                        s = requests.Session()
                        patch_session_headers(s)
                        s.headers['X-TOKEN'] = new_token
                        user_info = get_current_user_info(s)
                        if user_info:
                            user_key = save_user_token(new_token, user_info)
                            print(f"{_('login_success_saved')} ({_('username')}: {user_info.get('name', '无名')})")
                        else:
                            print(_('login_failed'))
                
                elif choice == '2':
                    # 从已保存账户选择
                    tokens_data = load_user_tokens()
                    if not tokens_data:
                        print(_('no_saved_accounts'))
                        print(_('choose_option1_or_3'))
                    else:
                        selected_token = select_user_token()
                        if selected_token:
                            s = requests.Session()
                            patch_session_headers(s)
                            s.headers['X-TOKEN'] = selected_token
                            user_info = get_current_user_info(s)
                            if user_info:
                                # 更新最后登录时间
                                save_user_token(selected_token, user_info)
                                print(f"{_('switch_login_success')} ({_('username')}: {user_info.get('name', '无名')})")
                            else:
                                print(_('account_token_expired'))
                                # 删除无效token
                                remove_invalid_token(selected_token)
                
                elif choice == '3':
                    # 显示登录指导
                    display_login_instructions()
                
                elif choice == '0':
                    print(_('cancelled'))
                
                else:
                    print(_('invalid_choice'))
                    
            except KeyboardInterrupt:
                print(f"\n{_('cancelled')}")
            except Exception as e:
                print(f"{_('operation_failed')}: {e}")
        
        sys.exit(0)
    
    # 处理unlogin命令
    if args.command == 'unlogin':
        config_dir = get_config_dir()
        token_file = os.path.join(config_dir, 'token.txt')
        
        if os.path.exists(token_file):
            # 显示当前登录用户信息
            with open(token_file, 'r') as f:
                current_token = f.read().strip()
            
            s = requests.Session()
            patch_session_headers(s)
            s.headers['X-TOKEN'] = current_token
            user_info = get_current_user_info(s)
            
            print(_('current_user_info'))
            if user_info:
                print(f"{_('username')}: {user_info.get('name', '无名')}")
                if user_info.get('email'):
                    print(f"{_('email')}: {user_info['email']}")
                if user_info.get('tel'):
                    print(f"{_('phone')}: {user_info['tel']}")
                print()
            else:
                print(_('token_invalid_expired'))
                # 清理无效token
                remove_invalid_token(current_token)
                print(_('token_cleaned'))
                print()
            
            # 询问确认
            try:
                confirm = input(f"{_('confirm_logout')}: ").strip().lower()
                if confirm == 'y' or confirm == 'yes':
                    os.remove(token_file)
                    print(_('logout_success'))
                else:
                    print(_('logout_cancelled'))
            except KeyboardInterrupt:
                print(f"\n{_('logout_cancelled')}")
        else:
            print(_('no_account_logged'))
        
        sys.exit(0)
    
    # 验证命令和目标参数
    if not args.command:
        print(_('error_provide_command'))
        print(_('use_help'))
        sys.exit(1)
    
    if not args.target:
        print(_('error_target_required', args.command))
        print(_('use_help'))
        sys.exit(1)

    # 创建session并进行初始化
    s = requests.Session()
    patch_session_headers(s)
    
    # 设置代理
    if args.proxy:
        proxies = {
            'http': args.proxy,
            'https': args.proxy
        }
        s.proxies.update(proxies)
        logging.info(f'{_("using_proxy")}: {args.proxy}')
    else:
        s.proxies = {}
    
    # 处理登录逻辑
    if args.login:
        # 使用 -l 参数，尝试使用已保存的token
        config_dir = get_config_dir()
        token_file = os.path.join(config_dir, 'token.txt')
        
        if os.path.exists(token_file):
            with open(token_file, 'r') as f:
                token = f.read().strip()
            print(_('trying_saved_token'))
            s.headers['X-TOKEN'] = token
            user_info = get_current_user_info(s)
            if user_info:
                print(_('logged_in', user_info.get('name', '无名')))
            else:
                print(_('saved_token_invalid'))
                # 清理无效token
                remove_invalid_token(token)
                try:
                    s.headers['X-TOKEN'] = login_anonymous(s)
                    api_overseashow(s)
                except Exception as e:
                    print(f"匿名登录失败: {e}")
                    sys.exit(1)
        else:
            print(_('no_saved_token'))
            try:
                s.headers['X-TOKEN'] = login_anonymous(s)
                api_overseashow(s)
            except Exception as e:
                print(f"匿名登录失败: {e}")
                sys.exit(1)
    else:
        # 默认使用匿名登录
        print(_('using_anonymous'))
        try:
            s.headers['X-TOKEN'] = login_anonymous(s)
            api_overseashow(s)
        except Exception as e:
            print(f"匿名登录失败: {e}")
            sys.exit(1)
    
    try:
        if args.command == 'upload' or args.command == 'u':
            current_operation = 'upload'
            resume_enabled = False  # 上传操作不支持断点续传
            
            # 处理取件码
            pwd = ""
            if args.key:
                pwd = args.key[:4]  # 限制为4位
                print(f"{_('using_pickup_code')}: {pwd}")
            elif args.randomkey:
                pwd = str(random.randint(1000, 9999))
                print(f"{_('random_pickup_code')}: {pwd}")
            
            upload(args.target, pwd, s)
            
        elif args.command == 'download' or args.command == 'd':
            current_operation = 'download'
            resume_enabled = args.resume
            
            # 验证线程数
            num_threads = args.threads
            if num_threads < 1 or num_threads > 16:
                print(_('invalid_thread_count'))
                sys.exit(1)
            
            # 显示下载模式
            if num_threads > 1:
                print(_('multithread_download', num_threads))
            else:
                print(_('single_thread_download'))
            
            download(args.target, args.resume, s, num_threads)
            
    except Exception as e:
        traceback.print_exc()


if __name__ == "__main__":
    main()