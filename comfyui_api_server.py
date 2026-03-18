#!/usr/bin/env python3
"""
ComfyUI API 服务器
提供 REST API 接口来执行图像编辑工作流
"""

import json
import requests
import base64
import uuid
import time
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename
import threading
import queue

app = Flask(__name__)

# 配置
COMFYUI_SERVER = "http://localhost:8188"
UPLOAD_FOLDER = "/tmp/comfyui_uploads"
WORKFLOW_FILE = "/home/ihouse/projects/FireRed-Image/comfyui.json"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# 创建上传文件夹
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# 任务队列
task_queue = {}

def load_workflow():
    """加载工作流"""
    with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def submit_workflow_to_comfyui(workflow, images_data):
    """提交工作流到 ComfyUI"""
    try:
        # 上传图片到 ComfyUI
        for image_key, image_data in images_data.items():
            files = {'image': ('image.png', image_data, 'image/png')}
            response = requests.post(
                f"{COMFYUI_SERVER}/upload/image",
                files=files,
                timeout=30
            )
            if response.status_code != 200:
                return None, f"图片上传失败: {response.text}"

        # 提交工作流
        response = requests.post(
            f"{COMFYUI_SERVER}/prompt",
            json={"prompt": workflow},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return result.get('prompt_id'), None
        else:
            return None, f"工作流提交失败: {response.text}"

    except Exception as e:
        return None, str(e)

def get_workflow_status(prompt_id):
    """获取工作流执行状态"""
    try:
        response = requests.get(
            f"{COMFYUI_SERVER}/history/{prompt_id}",
            timeout=10
        )
        if response.status_code == 200:
            history = response.json()
            if prompt_id in history:
                return history[prompt_id]
        return None
    except Exception as e:
        return None

@app.route('/')
def index():
    """主页 - 测试界面"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/process', methods=['POST'])
def process_image():
    """处理图像编辑请求"""
    try:
        # 获取参数
        prompt = request.form.get('prompt', '')

        # 检查文件
        if 'person_image' not in request.files:
            return jsonify({'error': '缺少人物图片'}), 400
        if 'garment_image' not in request.files:
            return jsonify({'error': '缺少衣服图片'}), 400

        person_file = request.files['person_image']
        garment_file = request.files['garment_image']

        if person_file.filename == '':
            return jsonify({'error': '人物图片未选择'}), 400
        if garment_file.filename == '':
            return jsonify({'error': '衣服图片未选择'}), 400

        # 读取文件
        person_data = person_file.read()
        garment_data = garment_file.read()

        # 加载工作流
        workflow = load_workflow()

        # 更新工作流中的提示词
        for node in workflow['nodes']:
            if node['type'] == 'TextEncodeQwenImageEditPlus' and node.get('title') == 'TextEncodeQwenImageEditPlus (Positive)':
                node['widgets_values'][0] = prompt

        # 提交工作流
        prompt_id, error = submit_workflow_to_comfyui(
            workflow,
            {
                'person': person_data,
                'garment': garment_data
            }
        )

        if error:
            return jsonify({'error': error}), 500

        # 保存任务信息
        task_id = str(uuid.uuid4())
        task_queue[task_id] = {
            'prompt_id': prompt_id,
            'status': 'processing',
            'created_at': time.time()
        }

        return jsonify({
            'task_id': task_id,
            'prompt_id': prompt_id,
            'status': 'processing'
        }), 202

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<task_id>', methods=['GET'])
def get_status(task_id):
    """获取任务状态"""
    if task_id not in task_queue:
        return jsonify({'error': '任务不存在'}), 404

    task = task_queue[task_id]
    prompt_id = task['prompt_id']

    # 获取 ComfyUI 的执行状态
    history = get_workflow_status(prompt_id)

    if history is None:
        return jsonify({
            'task_id': task_id,
            'status': 'processing'
        }), 200

    # 检查是否完成
    if 'outputs' in history:
        return jsonify({
            'task_id': task_id,
            'status': 'completed',
            'output': history['outputs']
        }), 200
    else:
        return jsonify({
            'task_id': task_id,
            'status': 'processing'
        }), 200

@app.route('/api/result/<task_id>', methods=['GET'])
def get_result(task_id):
    """获取处理结果"""
    if task_id not in task_queue:
        return jsonify({'error': '任务不存在'}), 404

    task = task_queue[task_id]
    prompt_id = task['prompt_id']

    history = get_workflow_status(prompt_id)

    if history is None or 'outputs' not in history:
        return jsonify({'error': '结果未就绪'}), 202

    # 获取输出图片
    outputs = history['outputs']
    images = []

    for node_id, output in outputs.items():
        if 'images' in output:
            for img_info in output['images']:
                img_path = f"{COMFYUI_SERVER}/view?filename={img_info['filename']}&subfolder={img_info.get('subfolder', '')}&type=output"
                images.append(img_path)

    return jsonify({
        'task_id': task_id,
        'status': 'completed',
        'images': images
    }), 200

# HTML 测试模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FireRed 图像编辑 - 测试页面</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }

        .card {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }

        .card h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            color: #555;
            margin-bottom: 8px;
            font-weight: 500;
        }

        .form-group input[type="file"],
        .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-family: inherit;
            font-size: 1em;
            transition: border-color 0.3s;
        }

        .form-group input[type="file"]:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .form-group textarea {
            resize: vertical;
            min-height: 100px;
        }

        .image-preview {
            width: 100%;
            height: 250px;
            border: 2px dashed #e0e0e0;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f9f9f9;
            margin-top: 10px;
            overflow: hidden;
        }

        .image-preview img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }

        .image-preview.empty {
            color: #999;
            font-size: 0.9em;
        }

        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 30px;
        }

        button {
            flex: 1;
            padding: 14px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }

        .btn-submit {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }

        .btn-submit:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .btn-reset {
            background: #f0f0f0;
            color: #333;
        }

        .btn-reset:hover {
            background: #e0e0e0;
        }

        .results {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }

        .results h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
        }

        .status-box {
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }

        .status-box.show {
            display: block;
        }

        .status-box.processing {
            background: #e3f2fd;
            color: #1976d2;
            border-left: 4px solid #1976d2;
        }

        .status-box.completed {
            background: #e8f5e9;
            color: #388e3c;
            border-left: 4px solid #388e3c;
        }

        .status-box.error {
            background: #ffebee;
            color: #c62828;
            border-left: 4px solid #c62828;
        }

        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(0, 0, 0, 0.1);
            border-radius: 50%;
            border-top-color: currentColor;
            animation: spin 0.8s linear infinite;
            margin-right: 8px;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .output-images {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .output-image {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .output-image img {
            width: 100%;
            height: auto;
            display: block;
        }

        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }

            .header h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 FireRed 图像编辑</h1>
            <p>AI 驱动的智能换装系统</p>
        </div>

        <div class="main-content">
            <!-- 输入表单 -->
            <div class="card">
                <h2>📤 上传图片</h2>
                <form id="uploadForm">
                    <div class="form-group">
                        <label for="personImage">👤 人物图片</label>
                        <input type="file" id="personImage" name="person_image" accept="image/*" required>
                        <div class="image-preview empty" id="personPreview">
                            <span>点击上方选择人物图片</span>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="garmentImage">👗 衣服图片</label>
                        <input type="file" id="garmentImage" name="garment_image" accept="image/*" required>
                        <div class="image-preview empty" id="garmentPreview">
                            <span>点击上方选择衣服图片</span>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="prompt">✍️ 编辑提示词</label>
                        <textarea id="prompt" name="prompt" placeholder="例如: 把模特换成穿着红色连衣裙，搭配黑色高跟鞋..." required></textarea>
                    </div>

                    <div class="button-group">
                        <button type="submit" class="btn-submit" id="submitBtn">🚀 开始处理</button>
                        <button type="reset" class="btn-reset">🔄 重置</button>
                    </div>
                </form>
            </div>

            <!-- 参数设置 -->
            <div class="card">
                <h2>⚙️ 参数设置</h2>
                <div class="form-group">
                    <label for="steps">推理步数</label>
                    <input type="number" id="steps" value="40" min="1" max="100">
                </div>
                <div class="form-group">
                    <label for="cfg">CFG 强度</label>
                    <input type="number" id="cfg" value="4" min="0" max="20" step="0.1">
                </div>
                <div class="form-group">
                    <label for="seed">随机种子</label>
                    <input type="number" id="seed" value="43" min="0">
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="useLora" checked>
                        使用加速 LoRA
                    </label>
                </div>
            </div>
        </div>

        <!-- 结果显示 -->
        <div class="results">
            <h2>📊 处理结果</h2>
            <div class="status-box" id="statusBox"></div>
            <div class="output-images" id="outputImages"></div>
        </div>
    </div>

    <script>
        const form = document.getElementById('uploadForm');
        const personInput = document.getElementById('personImage');
        const garmentInput = document.getElementById('garmentImage');
        const personPreview = document.getElementById('personPreview');
        const garmentPreview = document.getElementById('garmentPreview');
        const statusBox = document.getElementById('statusBox');
        const outputImages = document.getElementById('outputImages');
        const submitBtn = document.getElementById('submitBtn');

        // 图片预览
        personInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    personPreview.innerHTML = `<img src="${event.target.result}" alt="人物图片">`;
                    personPreview.classList.remove('empty');
                };
                reader.readAsDataURL(file);
            }
        });

        garmentInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    garmentPreview.innerHTML = `<img src="${event.target.result}" alt="衣服图片">`;
                    garmentPreview.classList.remove('empty');
                };
                reader.readAsDataURL(file);
            }
        });

        // 表单提交
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(form);
            submitBtn.disabled = true;

            try {
                // 提交请求
                const response = await fetch('/api/process', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const error = await response.json();
                    showStatus('error', `错误: ${error.error}`);
                    submitBtn.disabled = false;
                    return;
                }

                const result = await response.json();
                const taskId = result.task_id;

                showStatus('processing', '正在处理中... 请稍候');

                // 轮询获取结果
                pollResult(taskId);

            } catch (error) {
                showStatus('error', `请求失败: ${error.message}`);
                submitBtn.disabled = false;
            }
        });

        function showStatus(type, message) {
            statusBox.className = `status-box show ${type}`;
            if (type === 'processing') {
                statusBox.innerHTML = `<span class="spinner"></span>${message}`;
            } else {
                statusBox.innerHTML = message;
            }
        }

        async function pollResult(taskId) {
            const maxAttempts = 120; // 10 分钟
            let attempts = 0;

            const poll = async () => {
                try {
                    const response = await fetch(`/api/status/${taskId}`);
                    const data = await response.json();

                    if (data.status === 'completed') {
                        showStatus('completed', '✅ 处理完成!');
                        displayResults(data.output);
                        submitBtn.disabled = false;
                    } else if (attempts < maxAttempts) {
                        attempts++;
                        setTimeout(poll, 5000); // 每 5 秒检查一次
                    } else {
                        showStatus('error', '❌ 处理超时');
                        submitBtn.disabled = false;
                    }
                } catch (error) {
                    showStatus('error', `轮询失败: ${error.message}`);
                    submitBtn.disabled = false;
                }
            };

            poll();
        }

        function displayResults(output) {
            outputImages.innerHTML = '';

            // 从输出中提取图片
            for (const [nodeId, nodeOutput] of Object.entries(output)) {
                if (nodeOutput.images) {
                    nodeOutput.images.forEach((img, index) => {
                        const imgDiv = document.createElement('div');
                        imgDiv.className = 'output-image';
                        imgDiv.innerHTML = `<img src="${img}" alt="输出图片 ${index + 1}">`;
                        outputImages.appendChild(imgDiv);
                    });
                }
            }
        }
    </script>
</body>
</html>
'''

def check_and_kill_port(port):
    """检查并杀死占用指定端口的进程"""
    import subprocess
    import os

    try:
        # 查找占用该端口的进程
        result = subprocess.run(
            f"lsof -i :{port} | grep LISTEN | awk '{{print $2}}'",
            shell=True,
            capture_output=True,
            text=True
        )

        pids = result.stdout.strip().split('\n')
        for pid in pids:
            if pid and pid.isdigit():
                try:
                    os.kill(int(pid), 9)
                    print(f"✅ 已杀死占用端口 {port} 的进程 (PID: {pid})")
                except Exception as e:
                    print(f"⚠️  无法杀死进程 {pid}: {e}")
    except Exception as e:
        print(f"⚠️  检查端口失败: {e}")

if __name__ == '__main__':
    PORT = 8080

    print("=" * 60)
    print("ComfyUI API 服务器启动")
    print("=" * 60)
    print(f"ComfyUI 服务器: {COMFYUI_SERVER}")
    print(f"工作流文件: {WORKFLOW_FILE}")
    print(f"上传文件夹: {UPLOAD_FOLDER}")

    # 检查并清理端口
    print(f"\n🔍 检查端口 {PORT}...")
    check_and_kill_port(PORT)

    print(f"\n🚀 API 服务器启动在 http://0.0.0.0:{PORT}")
    print(f"📱 访问测试页面: http://localhost:{PORT}")
    print("=" * 60)

    app.run(host='0.0.0.0', port=PORT, debug=False)
