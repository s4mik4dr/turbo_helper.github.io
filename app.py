from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
import os
import json
import uuid
import io
import qrcode
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import tempfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parser')
def parser():
    return render_template('parser.html')

@app.route('/qr')
def qr_generator():
    return render_template('qr.html')

@app.route('/ai')
def ai():
    return render_template('ai.html')

@app.route('/api/load_news', methods=['POST'])
def load_news():
    data = request.json
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    
    results = []
    
    # === emis-kip.ru ===
    try:
        url_emis = "https://emis-kip.ru/company/sob/news/"
        html_emis = requests.get(url_emis, timeout=10).text
        emis_news = parse_emis_kip(html_emis, url_emis, start_date, end_date)
        if emis_news:
            results.append({
                "site": "ЭМИС",
                "news": emis_news
            })
    except Exception as e:
        results.append({
            "site": "ЭМИС",
            "error": str(e)
        })

    # === ktkprom.com ===
    try:
        url_ktk = "https://ktkprom.com/novosti-i-sobytija/"
        html_ktk = requests.get(url_ktk, timeout=10).text
        ktk_news = parse_ktkprom(html_ktk, start_date, end_date)
        if ktk_news:
            results.append({
                "site": "КТКПРОМ",
                "news": ktk_news
            })
    except Exception as e:
        results.append({
            "site": "КТКПРОМ",
            "error": str(e)
        })

    # === vzljot.ru ===
    try:
        url_vzljot = "https://vzljot.ru/kompaniya/novosti/"
        html_vzljot = requests.get(url_vzljot, timeout=10).text
        vzljot_news = parse_vzljot(html_vzljot, url_vzljot, start_date, end_date)
        if vzljot_news:
            results.append({
                "site": "ВЗЛЁТ",
                "news": vzljot_news
            })
    except Exception as e:
        results.append({
            "site": "ВЗЛЁТ",
            "error": str(e)
        })

    return jsonify(results)

def parse_emis_kip(html, base_url, start_date, end_date):
    soup = BeautifulSoup(html, 'html.parser')
    news_blocks = soup.select(".news-list__item")
    results = []

    month_map = {
        "января": "January", "февраля": "February", "марта": "March",
        "апреля": "April", "мая": "May", "июня": "June",
        "июля": "July", "августа": "August", "сентября": "September",
        "октября": "October", "ноября": "November", "декабря": "December"
    }

    for item in news_blocks:
        try:
            date_str = item.select_one(".news-list__item-period-date").text.strip()
            for ru, en in month_map.items():
                date_str = date_str.replace(ru, en)
            date = datetime.strptime(date_str, "%d %B %Y").date()

            if start_date <= date <= end_date:
                title_tag = item.select_one(".news-list__item-title a")
                title = title_tag.text.strip()
                href = title_tag['href']
                full_link = urljoin(base_url, href)
                results.append({"date": date.strftime("%d.%m.%Y"), "title": title, "link": full_link})
        except Exception:
            continue

    return results

def parse_ktkprom(html, start_date, end_date):
    soup = BeautifulSoup(html, 'html.parser')
    news_blocks = soup.select(".news_item")
    results = []

    for item in news_blocks:
        try:
            date_str = item.select_one("meta[itemprop='datePublished']")["content"]
            date = datetime.strptime(date_str, "%Y-%m-%d").date()

            if start_date <= date <= end_date:
                title_tag = item.select_one("span[itemprop='headline']")
                title = title_tag.text.strip()
                link_tag = item.select_one("a.news_item_title")
                link = link_tag['href'].strip()
                results.append({"date": date.strftime("%d.%m.%Y"), "title": title, "link": link})
        except Exception:
            continue

    return results

def parse_vzljot(html, base_url, start_date, end_date):
    soup = BeautifulSoup(html, 'html.parser')
    news_blocks = soup.select(".news-card")
    results = []

    month_map = {
        "января": "January", "февраля": "February", "марта": "March",
        "апреля": "April", "мая": "May", "июня": "June",
        "июля": "July", "августа": "August", "сентября": "September",
        "октября": "October", "ноября": "November", "декабря": "December"
    }

    for item in news_blocks:
        try:
            title = item.select_one(".news-card__title").text.strip()
            href = item.select_one("a.news-card__link")["href"]
            full_link = urljoin(base_url, href)
            date_str = item.select_one(".news-card__date").text.strip()
            for ru, en in month_map.items():
                date_str = date_str.replace(ru, en)
            date = datetime.strptime(date_str, "%d %B %Y").date()

            if start_date <= date <= end_date:
                results.append({
                    "date": date.strftime("%d.%m.%Y"),
                    "title": title,
                    "link": full_link
                })
        except Exception:
            continue

    return results

@app.route('/api/generate_qr', methods=['POST'])
def generate_qr():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "URL отсутствует"}), 400
    
    # Генерация уникального QR-кода для каждого запроса даже для одинаковых URL
    unique_data = f"{url}_{uuid.uuid4()}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(unique_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Создаем директорию для QR-кодов, если она не существует
    qr_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)
    
    # Генерируем имя файла и сохраняем QR-код
    filename = f"qr_{uuid.uuid4()}.png"
    file_path = os.path.join(qr_dir, filename)
    img.save(file_path)
    
    return jsonify({"qr_code": filename, "file_path": file_path})

@app.route('/qr_codes/<filename>')
def serve_qr_code(filename):
    qr_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qr_codes')
    return send_file(os.path.join(qr_dir, filename), mimetype='image/png')

@app.route('/api/ai_chat', methods=['POST'])
def ai_chat():
    data = request.json
    model = data.get('model')
    message = data.get('message')
    api_key = data.get('api_key')
    
    if not all([model, message, api_key]):
        return jsonify({"error": "Не все необходимые данные предоставлены"}), 400
    
    # Здесь будет код для обращения к различным API моделям
    # В качестве заглушки вернем эхо-ответ
    response = {
        "model": model,
        "response": f"Ответ от модели {model}: {message}"
    }
    
    return jsonify(response)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Файл не найден"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Имя файла отсутствует"}), 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    return jsonify({"success": True, "filename": file.filename, "path": file_path})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000) 