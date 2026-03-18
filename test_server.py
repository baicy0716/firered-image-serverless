#!/usr/bin/env python3
"""
简化的 API 服务器 - 用于测试
"""

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <html>
    <head><title>FireRed API Test</title></head>
    <body>
        <h1>✅ API 服务器运行正常</h1>
        <p>端口: 8080</p>
    </body>
    </html>
    '''

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({'status': 'ok', 'message': 'API is working'})

if __name__ == '__main__':
    import subprocess
    import os

    # 清理端口
    try:
        result = subprocess.run(
            "lsof -i :8080 | grep LISTEN | awk '{print $2}'",
            shell=True,
            capture_output=True,
            text=True
        )
        pids = result.stdout.strip().split('\n')
        for pid in pids:
            if pid and pid.isdigit():
                os.kill(int(pid), 9)
                print(f"✅ 已杀死进程 {pid}")
    except:
        pass

    print("🚀 启动 API 服务器在 http://0.0.0.0:8080")
    app.run(host='0.0.0.0', port=8080, debug=False)
