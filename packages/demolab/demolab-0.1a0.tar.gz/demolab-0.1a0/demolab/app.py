import logging
from http.client import responses

from flask import Flask, request, jsonify, redirect, render_template, abort, session
import json
import os
import base64
import requests
from datetime import datetime
from demolab.config import Config
from demolab.shell_runner import run_shell_script
from demolab.network_utils import get_free_port
from demolab.token_extraction import extract_token_from_user_workspace_creation_log

# 初始化Flask应用
app = Flask(__name__)
app.config.from_object(Config)
# 确保日志目录存在
os.makedirs(app.config['WORKSPACE_LOG_PATH'], exist_ok=True)
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# log to file
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(app.config['WORKSPACE_LOG_PATH'] + '/app.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def ensure_user_config_exists():
    """确保用户配置文件存在，如果不存在则创建"""
    if not os.path.exists(app.config['USER_CONFIG_PATH']):
        logger.info(f"User config file not found, creating at {app.config['USER_CONFIG_PATH']}")
        with open(app.config['USER_CONFIG_PATH'], 'w') as f:
            json.dump({"users": {}}, f, indent=2)
    else:
        logger.info(f"User config file found at {app.config['USER_CONFIG_PATH']}")


def load_user_config():
    """加载用户配置文件"""
    logger.info(f"Loading user config from {app.config['USER_CONFIG_PATH']}")
    ensure_user_config_exists()
    with open(app.config['USER_CONFIG_PATH'], 'r') as f:
        return json.load(f)


def save_user_config(config):
    """保存用户配置到文件"""
    logger.info(f"Saving user config to {app.config['USER_CONFIG_PATH']}")
    with open(app.config['USER_CONFIG_PATH'], 'w') as f:
        json.dump(config, f, indent=2)


# 登录页面
@app.route('/')
def login_page():
    return render_template('login.html')


# 本地测试登录接口
@app.route('/auth', methods=['POST'])
def local_auth():
    logger.info(f"DEBUG PURPOSE ONLY ::Local auth request received")
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if app.config['BASE64_ON_LOGIN_FIELD'] == 'TRUE':
        username = base64.b64decode(username.encode()).decode()
        password = base64.b64decode(password.encode()).decode()
    # 加载用户配置
    config = load_user_config()

    # 简单验证用户名密码
    if ((username == "test" and password == "test123")
            or (username == 'admin' and password == 'admin123')):
        return jsonify({"status": "success", "message": "DEBUG PURPOSE ONLY ::Local authentication successful"})
    else:
        return jsonify({"error": "Invalid credentials"}), 401


# 登录接口
@app.route('/api/login', methods=['POST'])
def login():
    # 获取表单数据
    logger.info(f"Login request received")
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    username_field = app.config['AUTH_SERVICE_PAYLOAD_USER_FIELD']
    password_field = app.config['AUTH_SERVICE_PAYLOAD_PASSWORD_FIELD']
    if app.config['BASE64_ON_LOGIN_FIELD'] == 'TRUE':
        auth_string = {
            f"{username_field}": base64.b64encode(username.encode()),
            f"{password_field}": base64.b64encode(password.encode())
        }
        # 构建认证信息
    else:
        auth_string = {
            f"{username_field}": base64.b64encode(username.encode()).decode(),
            f"{password_field}": base64.b64encode(password.encode()).decode()
        }

    # 发送请求到认证服务
    try:
        if app.config['AUTH_SERVICE_LOGIN_METHOD'] == 'BASIC_AUTH':
            logger.info(f"Basic auth request sent to {app.config['AUTH_SERVICE_URL']}")
            encoded_auth = base64.b64encode(f'{username}:{password}'.encode()).decode()
            response = requests.post(
                app.config['AUTH_SERVICE_URL'],
                headers={"Authorization": f"Basic {encoded_auth}"}
            )
        else:
            logger.info(f"Payload auth request sent to {app.config['AUTH_SERVICE_URL']}")
            response = requests.post(
                app.config['AUTH_SERVICE_URL'],
                data=auth_string
            )
        if response.status_code == 200:
            # return jsonify(response.json()), response.status_code
            session['username'] = username
            config = load_user_config()
            if 'admins' in config and username in config['admins']:
                return redirect('/admin')
            else:
                return redirect('/lab')
        else:
            return jsonify(
                {"error": f"Authentication service error: {responses[response.status_code]}"}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Authentication service error: {str(e)}"}), 500


@app.route('/logout')
def logout():
    """
    注销用户
    """
    logger.info(f"Logout request received")
    session.clear()
    return redirect('/')


@app.route('/admin')
def admin_panel():
    """
    管理员面板
    """
    logger.info(f"Admin panel request received")
    if 'username' not in session:
        return redirect('/')
    if session.get('username') not in load_user_config()['admins']:
        return redirect('/')
    logger.info(f"Admin panel request received, username: {session.get('username')}")
    config = load_user_config()
    return render_template('admin.html',
                           users=config['users'],
                           current_user=session.get('username'))


# lab初始化接口
@app.route('/lab_init/<token>/<user>/<u_redirect>')
def lab_init(token, user, u_redirect):
    logger.info(f"Lab init request received, user: {user}, u_redirect: {u_redirect}")
    # 校验token
    if token not in app.config['VALID_INIT_TOKENS']:
        abort(403, description="Invalid or expired token")

    # 加载用户配置
    config = load_user_config()

    # 检查用户是否已存在
    if user in config['users']:
        logger.info(f"User {user} already exists")
        # 用户已存在，重定向到工作空间
        if u_redirect == '1' or u_redirect.lower() == 'true':
            return redirect(config['users'][user]['workspaceUrl'])
        else:
            return "User workspace is already created", 200

    logger.info(f"User {user} does not exist, initializing workspace")
    # 用户不存在，初始化工作空间
    try:
        # 获取空闲端口
        port = get_free_port()

        # 运行初始化脚本
        return_code, stdout, stderr = run_shell_script(
            app.config['INIT_WORKSPACE_SCRIPT'],
            user,
            str(port)
        )

        if return_code != 0:
            return jsonify({
                "error": "Failed to initialize workspace",
                "stdout": stdout,
                "stderr": stderr
            }), 500

        # 从日志提取token
        log_file = os.path.join(app.config['WORKSPACE_LOG_PATH'], f"{user}.log")
        workspace_token = extract_token_from_user_workspace_creation_log(log_file)

        if not workspace_token:
            return jsonify({"error": "Failed to extract token from log"}), 500

        # 构建工作空间URL
        WORKSPACE_BASE_URL = app.config['WORKSPACE_BASE_URL']
        workspace_url = f"{WORKSPACE_BASE_URL}:{port}/tree?token={workspace_token}"
        logger.info(f"Workspace URL: {workspace_url}")

        # 更新用户配置
        config['users'][user] = {
            "workspaceUrl": workspace_url,
            "createdDate": datetime.now().strftime("%Y%m%d%H%M%S")
        }
        save_user_config(config)

        # 重定向到工作空间
        return redirect(workspace_url)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/demolab/<token>')
def demo_lab(token):
    logger.info(f"Demo lab request received, token: {token}")
    return render_template('demolab.html', config=app.config)


# 用户查询接口
@app.route('/users/<user>')
def get_user(user):
    config = load_user_config()
    if user in config['users']:
        return jsonify(config['users'][user])
    else:
        return jsonify({"error": "User not found"}), 404


def main():
    """应用入口点"""
    app.run(debug=True)


if __name__ == '__main__':
    main()
