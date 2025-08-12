import os


class Config:
    """应用配置类"""
    TITLE_PREFIX = os.environ.get('TITLE_PREFIX', 'DemoLab | ')

    # 认证服务URL
    AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5000/auth')

    AUTH_SERVICE_PAYLOAD_USER_FIELD = os.environ.get('AUTH_SERVICE_PAYLOAD_USER_FIELD', 'username')

    AUTH_SERVICE_PAYLOAD_PASSWORD_FIELD = os.environ.get('AUTH_SERVICE_PAYLOAD_PASSWORD_FIELD', 'password')

    BASE64_ON_LOGIN_FIELD = os.environ.get('BASE64_ON_LOGIN_FIELD', 'TRUE')

    AUTH_SERVICE_LOGIN_METHOD = os.environ.get('AUTH_SERVICE_LOGIN_METHOD', 'FORM')

    # 初始化工作空间的脚本路径
    INIT_WORKSPACE_SCRIPT = os.environ.get('INIT_WORKSPACE_SCRIPT', '/path/to/init_script.sh')

    WORKSPACE_BASE_URL = os.environ.get('WORKSPACE_BASE_URL', 'http://localhost:8000')

    # 用户配置文件路径
    USER_CONFIG_PATH = os.environ.get('USER_CONFIG_PATH', os.path.join(os.path.dirname(__file__), 'userconfig.json'))

    # 日志文件路径
    WORKSPACE_LOG_PATH = os.environ.get('WORKSPACE_LOG_PATH', '/var/log/demolab/workspaces/')

    # 密钥，用于会话管理等
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-development-only')

    # 有效的初始化token（实际应用中应该更复杂）
    VALID_INIT_TOKENS = os.environ.get('VALID_INIT_TOKENS', 'dev_token,test_token').split(',')
