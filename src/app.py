from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import threading
import time
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# In-memory "база данных" с предзаполненными данными
images = {
    "1": {
        "id": "1",
        "status": "processed",
        "metadata": {"location": "55.7558, 37.6176", "capturedAt": "2025-03-01T09:50:00Z"},
        "uploadedAt": "2025-03-01T10:00:00Z",
        "file": "sample1.jpg",
        "analysis": {
            "segmentationResult": "result_1.png",
            "classification": "техногенные трансформации"
        }
    }
}
reports = {
    "rpt1": {
        "id": "rpt1",
        "imageId": "1",
        "summary": "Обнаружены техногенные трансформации в зоне A",
        "details": "Подробное описание результатов анализа",
        "createdAt": "2025-03-01T11:00:00Z"
    }
}
image_id_counter = 2  # следующий id для изображений
report_id_counter = 2  # следующий id для отчетов

def process_image(image_id):
    # Симуляция обработки изображения (например, сегментация и классификация)
    time.sleep(1)  # Имитация задержки обработки
    image = images.get(image_id)
    if image:
        image['status'] = 'processed'
        image['analysis'] = {
            "segmentationResult": f"result_{image_id}.png",
            "classification": "техногенные трансформации"
        }

# ===== Endpoints для изображений =====

# POST /api/v1/images – загрузка снимка
@app.route('/api/v1/images', methods=['POST'])
def upload_image():
    global image_id_counter
    if 'image' not in request.files:
        return jsonify({"message": "Файл изображения не найден"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"message": "Не выбран файл"}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    metadata = request.form.get('metadata')
    try:
        metadata = json.loads(metadata) if metadata else {}
    except Exception:
        metadata = {}
    image_id = str(image_id_counter)
    image_id_counter += 1
    image = {
        "id": image_id,
        "status": "processing",
        "metadata": metadata,
        "uploadedAt": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "file": filename
    }
    images[image_id] = image
    threading.Thread(target=process_image, args=(image_id,)).start()
    return jsonify({
        "id": image_id,
        "status": image["status"],
        "message": "Изображение загружено и обработка запущена"
    }), 201

# GET /api/v1/images – получение списка снимков
@app.route('/api/v1/images', methods=['GET'])
def get_images():
    return jsonify(list(images.values()))

# GET /api/v1/images/<image_id> – получение информации о конкретном снимке
@app.route('/api/v1/images/<image_id>', methods=['GET'])
def get_image(image_id):
    image = images.get(image_id)
    if not image:
        return jsonify({"message": "Изображение не найдено"}), 404
    return jsonify(image)

# PUT /api/v1/images/<image_id> – обновление информации о снимке
@app.route('/api/v1/images/<image_id>', methods=['PUT'])
def update_image(image_id):
    image = images.get(image_id)
    if not image:
        return jsonify({"message": "Изображение не найдено"}), 404
    data = request.get_json()
    if 'metadata' in data:
        image['metadata'] = data['metadata']
    if 'status' in data:
        image['status'] = data['status']
    return jsonify({"message": "Данные успешно обновлены"})

# DELETE /api/v1/images/<image_id> – удаление снимка
@app.route('/api/v1/images/<image_id>', methods=['DELETE'])
def delete_image(image_id):
    if image_id not in images:
        return jsonify({"message": "Изображение не найдено"}), 404
    del images[image_id]
    return jsonify({"message": "Изображение успешно удалено"})

# ===== Endpoints для отчетов =====

# GET /api/v1/reports – получение списка отчетов
@app.route('/api/v1/reports', methods=['GET'])
def get_reports():
    return jsonify(list(reports.values()))

# POST /api/v1/reports – создание отчета
@app.route('/api/v1/reports', methods=['POST'])
def create_report():
    global report_id_counter
    data = request.get_json()
    report_id = f"rpt{report_id_counter}"
    report_id_counter += 1
    report = {
        "id": report_id,
        "imageId": data.get("imageId"),
        "summary": data.get("summary"),
        "details": data.get("details"),
        "createdAt": time.strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    reports[report_id] = report
    return jsonify({
        "id": report_id,
        "message": "Отчет успешно создан"
    }), 201

# PUT /api/v1/reports/<report_id> – обновление отчета
@app.route('/api/v1/reports/<report_id>', methods=['PUT'])
def update_report(report_id):
    report = reports.get(report_id)
    if not report:
        return jsonify({"message": "Отчет не найден"}), 404
    data = request.get_json()
    if 'summary' in data:
        report['summary'] = data['summary']
    if 'details' in data:
        report['details'] = data['details']
    return jsonify({"message": "Отчет успешно обновлен"})

# DELETE /api/v1/reports/<report_id> – удаление отчета
@app.route('/api/v1/reports/<report_id>', methods=['DELETE'])
def delete_report(report_id):
    if report_id not in reports:
        return jsonify({"message": "Отчет не найден"}), 404
    del reports[report_id]
    return jsonify({"message": "Отчет успешно удален"})

if __name__ == '__main__':
    app.run(debug=True, port=3000)
