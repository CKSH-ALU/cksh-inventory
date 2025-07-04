from collections import OrderedDict
from flask import Flask, request, jsonify, session, render_template, redirect, url_for, send_file, send_from_directory
from datetime import datetime
import pymysql
import os
from openpyxl import Workbook
from dotenv import load_dotenv
from config import db_config, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

LOG_FILE = 'log.txt'
RELOG_FILE = 'relog.txt'


# MySQL 資料庫連線設定
load_dotenv()

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='1118',
        database='inventory_system',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


def load_inventory():
    conn = pymysql.connect(**db_config)
    try:
        with conn.cursor() as cursor:
            # 取得所有商品基本資訊
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()

            # 取得所有樣式（尺寸與庫存）
            cursor.execute("SELECT * FROM inventory")
            inventory_rows = cursor.fetchall()

        # 整理資料成 dict 結構
        inventory = OrderedDict()
        for product in products:
            name = product['name']
            if name not in inventory:
                inventory[name] = {
                    'name': name,
                    'category': product['category'],
                    'price': product['price'],
                    'styles': OrderedDict()
                }

        for row in inventory_rows:
            name = row['product_name']
            size = row['size']
            inventory[name]['styles'][size] = {
                'center': row['center_stock'],
                'warehouse': row['warehouse_stock']
            }

        return inventory

    finally:
        conn.close()


# 寫入 log.txt
def log_sale(name, identity, channel, order_id, total, items):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{now}] 【銷售】{name} 身分:{identity} 通路:{channel} 單號:{order_id} 金額:${total}\n")
        for item in items:
            f.write(f" - {item['name']} {item['size']} x{item['qty']}\n")

def load_staff():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT account, name, password FROM staff")
    staff = cursor.fetchall()
    conn.close()
    return {row['account']: {'name': row['name'], 'password': row['password']} for row in staff}

@app.route('/')
def root_redirect():
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/home')
def home_page():
    if 'account' not in session:
        return redirect(url_for('login_page'))
    return render_template('home.html', name=session['name'])


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    account = data.get('account')
    password = data.get('password')

    conn = pymysql.connect(**db_config)
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM staff WHERE account = %s AND password = %s"
            cursor.execute(sql, (account, password))
            result = cursor.fetchone()
            if result:
                session['account'] = result['id']
                session['name'] = result['name']
                return jsonify({'status': 'success', 'name': result['name']})
            else:
                return jsonify({'status': 'fail', 'message': '帳號或密碼錯誤'})
    finally:
        conn.close()


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'status': 'logged_out'})


@app.route('/api/check-login', methods=['GET'])
def check_login():
    if 'account' in session:
        return jsonify({'logged_in': True, 'account': session['account'], 'name': session['name']})
    return jsonify({'logged_in': False})

@app.route('/sale')
def sale_page():
    if 'account' not in session:
        return redirect(url_for('login_page'))
    return render_template('sale.html', name=session['name'])

@app.route('/manage')
def manage_page():
    if 'account' not in session:
        return redirect(url_for('login_page'))
    return render_template('manage.html')

@app.route('/log')
def log_page():
    if 'account' not in session:
        return redirect(url_for('login_page'))
    return render_template('log.html')


@app.route('/api/products', methods=['GET'])
def get_products():
    if 'account' not in session:
        return jsonify({'error': '未登入'}), 403

    conn = pymysql.connect(**db_config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 先查主商品
    cursor.execute("SELECT id, name, category, price FROM products")
    products = cursor.fetchall()

    # 查詢所有款式
    cursor.execute("SELECT product_id, style_name, center_stock, warehouse_stock FROM product_styles")
    styles = cursor.fetchall()

    # 整理成原本 JSON 結構
    result = {}
    for product in products:
        pid = str(product['id'])
        result[pid] = {
            'name': product['name'],
            'category': product['category'],
            'price': product['price'],
            'styles': {}
        }

    for style in styles:
        pid = str(style['product_id'])
        if pid in result:
            result[pid]['styles'][style['style_name']] = {
                'center': style['center_stock'],
                'warehouse': style['warehouse_stock']
            }

    cursor.close()
    conn.close()
    return jsonify(result)


@app.route('/api/log')
def get_log():
    if not os.path.exists(LOG_FILE):
        return ''
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def save_staff(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    for staff_id, info in data.items():
        cursor.execute("""
            INSERT INTO staff (id, name, password)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE name=VALUES(name), password=VALUES(password)
        """, (staff_id, info['name'], info['password']))
    conn.commit()
    conn.close()

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    name = data.get('name', '').strip()
    account = data.get('account', '').strip()
    password = data.get('password', '').strip()

    if not name or not account or not password:
        return jsonify({'status': 'fail', 'message': '請填寫完整資訊'}), 400

    # 連線資料庫並檢查帳號是否存在
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM staff WHERE account = %s", (account,))
        result = cursor.fetchone()
        if result:
            conn.close()
            return jsonify({'status': 'fail', 'message': '此帳號已存在'}), 400

        # 新增使用者
        cursor.execute("INSERT INTO staff (name, account, password) VALUES (%s, %s, %s)", (name, account, password))
        conn.commit()
    conn.close()

    return jsonify({'status': 'success'})




@app.route('/api/sale', methods=['POST'])
def sale():
    if 'name' not in session:
        return jsonify({'error': '未登入'}), 403

    data = request.json
    identity = data.get('identity')
    channel = data.get('channel')
    order_id = data.get('order_id')
    items = data.get('items', [])

    discount_total = 0
    nondiscount_total = 0

    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            for item in items:
                name = item['name']
                size = item['size']
                qty = item['qty']

                cursor.execute("""
                    SELECT p.price, p.category, s.center_stock 
                    FROM products p
                    JOIN product_styles s ON p.id = s.product_id
                    WHERE p.name = %s AND s.style_name = %s
                """, (name, size))

                result = cursor.fetchone()
                if not result:
                    return jsonify({'error': f'找不到商品或尺寸：{name} {size}'}), 400
                if result['center_stock'] < qty:
                    return jsonify({'error': f'{name} {size} 庫存不足'}), 400

                cursor.execute("""
                    UPDATE product_styles 
                    SET center_stock = center_stock - %s
                    WHERE product_id = (SELECT id FROM products WHERE name = %s) 
                    AND style_name = %s
                """, (qty, name, size))

                price = result['price']
                category = result['category']
                subtotal = price * qty

                if category in ['新品', '預購']:
                    nondiscount_total += subtotal
                else:
                    discount_total += subtotal

            if identity in ['校友會員', '在校生', '師長']:
                discount_total = int(discount_total * 0.9)

            total = discount_total + nondiscount_total
            conn.commit()
    finally:
        conn.close()

    log_sale(session['name'], identity, channel, order_id, total, items)
    return jsonify({'status': 'success', 'total': total})




@app.route('/api/gift', methods=['POST'])
def gift():
    if 'name' not in session:
        return jsonify({'error': '未登入'}), 403

    data = request.json
    giver = data.get('giver')
    items = data.get('items', [])

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            for item in items:
                name = item['name']
                size = item['size']
                qty = item['qty']

                cursor.execute("""
                    SELECT p.id, s.center_stock
                    FROM products p
                    JOIN product_styles s ON p.id = s.product_id
                    WHERE p.name = %s AND s.style_name = %s
                """, (name, size))
                result = cursor.fetchone()

                if not result:
                    conn.rollback()
                    return jsonify({'error': f'找不到商品或尺寸：{name} {size}'}), 400

                product_id = result['id']
                center_qty = int(result['center_stock'])

                if center_qty < qty:
                    conn.rollback()
                    return jsonify({'error': f'{name} {size} 庫存不足'}), 400

                cursor.execute("""
                    UPDATE product_styles
                    SET center_stock = center_stock - %s
                    WHERE product_id = %s AND style_name = %s
                """, (qty, product_id, size))

            conn.commit()
    finally:
        conn.close()

    def log_gift(name, giver, items):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{now}] 【贈與】{name} 贈與人:{giver}\n")
            for item in items:
                f.write(f" - {item['name']} {item['size']} x{item['qty']}\n")

    log_gift(session['name'], giver, items)
    return jsonify({'status': 'success'})





@app.route('/api/return', methods=['POST'])
def return_goods():
    if 'name' not in session:
        return jsonify({'error': '未登入'}), 403

    data = request.json
    identity = data.get('identity')
    channel = data.get('channel')
    items = data.get('items', [])

    total = 0
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        for item in items:
            name = item['name']
            size = item['size']
            qty = item['qty']

            cursor.execute("""
                SELECT s.id, p.price, s.center_stock FROM product_styles s
                JOIN products p ON s.product_id = p.id
                WHERE p.name = %s AND s.style_name = %s
            """, (name, size))
            row = cursor.fetchone()
            if not row:
                conn.rollback()
                return jsonify({'error': f'找不到商品或尺寸：{name} {size}'}), 400

            new_qty = row['center_stock'] + qty
            cursor.execute("""
                UPDATE product_styles SET center_stock = %s WHERE id = %s
            """, (new_qty, row['id']))

            total += row['price'] * qty

        if identity in ['校友會員', '在校生', '師長']:
            total = int(total * 0.9)

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_text = f"[{now}] 【退貨】{session['name']} 身分:{identity} 通路:{channel} 退還金額：$-{total}\n退回：\n"
        for item in items:
            log_text += f" - {item['name']} {item['size']} x-{item['qty']}\n"

        with open(RELOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_text)
        with open("log.txt", 'a', encoding='utf-8') as f:
            f.write(log_text)

        conn.commit()
        return jsonify({'status': 'success', 'total': total})

    finally:
        conn.close()




@app.route('/api/relog-latest')
def relog_latest():
    if not os.path.exists(RELOG_FILE):
        return jsonify([])

    with open(RELOG_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    logs = []
    current = None
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()

        if line.startswith('退回：'):
            # 開始收集一筆新紀錄的 items
            current = {'time': '', 'items': []}
            j = i + 1
            while j < len(lines) and lines[j].startswith(' - '):
                parts = lines[j].strip().split()
                name = parts[1]
                size = parts[2]
                qty = int(parts[3][2:])
                current['items'].append({'name': name, 'size': size, 'qty': qty})
                j += 1

            # 找上一行的時間資訊
            if i > 0:
                time_line = lines[i - 1]
                time = time_line.split(']')[0][1:]
                current['time'] = time
                logs.append(current)

    return jsonify(logs[:3])



@app.route('/api/exchange', methods=['POST'])
def exchange():
    if 'name' not in session:
        return jsonify({'error': '未登入'}), 403

    data = request.json
    identity = data.get('identity')
    channel = data.get('channel')
    order_id = data.get('order_id')
    old_items = data.get('old_items', [])
    new_items = data.get('new_items', [])

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    old_total = 0
    new_total = 0

    try:
        # 退舊商品
        for item in old_items:
            name, size, qty = item['name'], item['size'], item['qty']
            cursor.execute("""
                SELECT p.price, s.id, s.center_stock FROM products p
                JOIN product_styles s ON p.id = s.product_id
                WHERE p.name = %s AND s.style_name = %s
            """, (name, size))
            result = cursor.fetchone()
            if not result:
                conn.rollback()
                return jsonify({'error': f'退回商品不存在：{name} {size}'}), 400

            old_total += result['price'] * qty
            cursor.execute("""
                UPDATE product_styles SET center_stock = center_stock + %s WHERE id = %s
            """, (qty, result['id']))

            if cursor.rowcount == 0:
                conn.rollback()
                return jsonify({'error': f'更新退貨商品失敗：{name} {size}'}), 500

        # 新商品
        for item in new_items:
            name, size, qty = item['name'], item['size'], item['qty']
            cursor.execute("""
                SELECT p.price, s.id, s.center_stock FROM products p
                JOIN product_styles s ON p.id = s.product_id
                WHERE p.name = %s AND s.style_name = %s
            """, (name, size))
            result = cursor.fetchone()
            if not result:
                conn.rollback()
                return jsonify({'error': f'新商品不存在：{name} {size}'}), 400
            if result['center_stock'] < qty:
                conn.rollback()
                return jsonify({'error': f'{name} {size} 庫存不足'}), 400

            new_total += result['price'] * qty
            cursor.execute("""
                UPDATE product_styles SET center_stock = center_stock - %s WHERE id = %s
            """, (qty, result['id']))

            if cursor.rowcount == 0:
                conn.rollback()
                return jsonify({'error': f'更新新商品失敗：{name} {size}'}), 500

        if identity in ['校友會員', '在校生', '師長']:
            old_total = int(old_total * 0.9)
            new_total = int(new_total * 0.9)

        diff = new_total - old_total
        conn.commit()

    except Exception as e:
        conn.rollback()
        return jsonify({'error': f'錯誤：{str(e)}'}), 500
    finally:
        conn.close()

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{now}] 【換貨】{session['name']} 身分:{identity} 通路:{channel} 單號:{order_id} 舊商品退額:{old_total} 新商品金額:{new_total} 差額:{diff}\n")
        f.write("退回：\n")
        for item in old_items:
            f.write(f" - {item['name']} {item['size']} x-{item['qty']}\n")
        f.write("換出：\n")
        for item in new_items:
            f.write(f" - {item['name']} {item['size']} x{item['qty']}\n")

    return jsonify({'status': 'success', 'diff': diff})





def log_transfer(name, items):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(f"[{now}] 【中心補貨】{name}\n")
        for item in items:
            f.write(f" - {item['name']} {item['size']} x{item['qty']}\n")


@app.route('/api/transfer', methods=['POST']) 
def transfer():
    if 'name' not in session:
        return jsonify({'error': '未登入'}), 403

    data = request.json
    items = data.get('items', [])

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        for item in items:
            name = item.get('name')
            size = item.get('size')
            qty = item.get('qty')

            if not name or not size or qty is None:
                return jsonify({'error': '資料不完整'}), 400

            cursor.execute("""
                SELECT s.id, s.warehouse_stock, s.center_stock FROM product_styles s
                JOIN products p ON s.product_id = p.id
                WHERE p.name = %s AND s.style_name = %s
            """, (name, size))
            row = cursor.fetchone()

            if not row:
                return jsonify({'error': f'找不到商品：{name} {size}'}), 400

            if row['warehouse_stock'] < qty:
                return jsonify({'error': f'{name} {size} 倉庫庫存不足'}), 400

            cursor.execute("""
                UPDATE product_styles
                SET warehouse_stock = warehouse_stock - %s, center_stock = center_stock + %s
                WHERE id = %s
            """, (qty, qty, row['id']))

        conn.commit()
        log_transfer(session['name'], items)
        return jsonify({'status': 'success'})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': f'錯誤：{str(e)}'}), 500

    finally:
        conn.close()




def log_restock(name, items):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(f"[{now}] 【倉庫補貨/歸還】{name}\n")
        for item in items:
            f.write(f" - {item['name']} {item['size']} x{item['qty']}\n")

@app.route('/api/restock', methods=['POST'])
def restock():
    if 'name' not in session:
        return jsonify({'error': '未登入'}), 403

    data = request.json
    items = data.get('items', [])

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        for item in items:
            name = item.get('name')
            size = item.get('size')
            qty = item.get('qty')

            if not name or not size or qty is None:
                return jsonify({'error': '資料不完整'}), 400

            cursor.execute("""
                SELECT s.id FROM product_styles s
                JOIN products p ON s.product_id = p.id
                WHERE p.name = %s AND s.style_name = %s
            """, (name, size))
            row = cursor.fetchone()

            if not row:
                return jsonify({'error': f'{name} 無此尺寸：{size}'}), 400

            cursor.execute("""
                UPDATE product_styles
                SET warehouse_stock = warehouse_stock + %s
                WHERE id = %s
            """, (qty, row['id']))

        conn.commit()
        log_restock(session['name'], items)
        return jsonify({'status': 'success'})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        conn.close()




def log_usage(name, reason, items):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(f"[{now}] 【工用】{name} 用途:{reason}\n")
        for item in items:
            f.write(f" - {item['name']} {item['size']} x{item['qty']}\n")

@app.route('/api/usage', methods=['POST'])
def usage():
    if 'name' not in session:
        return jsonify({'error': '未登入'}), 403

    data = request.json
    reason = data.get('reason')
    items = data.get('items', [])

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        for item in items:
            name = item.get('name')
            size = item.get('size')
            qty = item.get('qty')

            if not name or not size or qty is None:
                return jsonify({'error': '資料不完整'}), 400

            cursor.execute("""
                SELECT s.id, s.warehouse_stock FROM product_styles s
                JOIN products p ON s.product_id = p.id
                WHERE p.name = %s AND s.style_name = %s
            """, (name, size))
            row = cursor.fetchone()

            if not row:
                return jsonify({'error': f'{name} 無此尺寸：{size}'}), 400

            if row['warehouse_stock'] < qty:
                return jsonify({'error': f'{name} {size} 倉庫庫存不足'}), 400

            cursor.execute("""
                UPDATE product_styles SET warehouse_stock = warehouse_stock - %s WHERE id = %s
            """, (qty, row['id']))

        conn.commit()
        log_usage(session['name'], reason, items)
        return jsonify({'status': 'success'})

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        conn.close()




@app.route('/api/add-product', methods=['POST'])
def add_product():
    if 'name' not in session:
        return jsonify({'status': 'fail', 'message': '未登入'}), 403

    data = request.json
    name = data.get('name')
    category = data.get('category')
    price = data.get('price')
    styles = data.get('styles')

    if not name or not category or not price or not styles:
        return jsonify({'status': 'fail', 'message': '資料不完整'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 檢查是否已有相同名稱商品
        cursor.execute("SELECT id FROM products WHERE name = %s", (name,))
        if cursor.fetchone():
            return jsonify({'status': 'fail', 'message': '已有相同名稱商品'}), 400

        # 新增商品
        cursor.execute("INSERT INTO products (name, category, price) VALUES (%s, %s, %s)", (name, category, price))
        product_id = cursor.lastrowid

        for style_name, stock in styles.items():
            center = stock.get('center', 0)
            warehouse = stock.get('warehouse', 0)
            cursor.execute(
                "INSERT INTO product_styles (product_id, style_name, center_stock, warehouse_stock) VALUES (%s, %s, %s, %s)",
                (product_id, style_name, center, warehouse)
            )

        conn.commit()

        # 紀錄 log
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open("log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{now}] 【新增】{session['name']}\n")
            f.write(f" - {name}｜{category}｜$ {price}\n")
            for style, stock in styles.items():
                f.write(f"   ・{style}：中心 {stock.get('center', 0)}／倉庫 {stock.get('warehouse', 0)}\n")

        return jsonify({'status': 'success', 'message': f'成功新增 {name}'})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'fail', 'message': str(e)}), 500
    
    finally:
        conn.close()





@app.route('/api/message', methods=['POST'])
def leave_message():
    if 'name' not in session:
        return jsonify({'error': '未登入'}), 403

    data = request.get_json()
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()

    if not title or not content:
        return jsonify({'error': '資料不完整'}), 400

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('message.txt', 'a', encoding='utf-8') as f:
        f.write(f"[{now}] {session['name']}：{title}\n{content}\n")

    return jsonify({'status': 'success'})

@app.route('/api/messages')
def get_messages():
    if not os.path.exists('message.txt'):
        return ''
    with open('message.txt', 'r', encoding='utf-8') as f:
        return f.read()
    
LOG_FILE = "log.txt"
@app.route('/api/monthly-summary', methods=['POST'])
def monthly_summary():
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not start_date or not end_date:
        return jsonify({'status': 'error', 'message': '缺少日期'}), 400

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    if not os.path.exists(LOG_FILE):
        return jsonify({'status': 'error', 'message': '找不到 log.txt'}), 400

    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    blocks = []
    current_block = []
    for line in lines:
        if line.startswith('['):
            if current_block:
                blocks.append(current_block)
            current_block = [line]
        else:
            current_block.append(line)
    if current_block:
        blocks.append(current_block)

    sales_data = {}   # 商品名 → 數量、金額
    total = 0
    return_total = 0
    exchange_total = 0

    for block in blocks:
        time_str = block[0].split(']')[0][1:]
        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        if not (start_dt <= dt <= end_dt):
            continue

        header = block[0]
        if "【銷售】" in header:
            for line in block[1:]:
                if line.strip().startswith("-"):
                    parts = line.strip().split()
                    name = parts[1]
                    size = parts[2]
                    qty = int(parts[3].replace("x", ""))
                    key = f"{name} {size}"
                    if key not in sales_data:
                        sales_data[key] = {'qty': 0, 'subtotal': 0}
                    sales_data[key]['qty'] += qty
            if "金額:$" in header:
                try:
                    amt = int(header.split("金額:$")[1].strip())
                    total += amt
                except:
                    pass

        elif "【退貨】" in header:
            if "退還金額：$-" in header:
                try:
                    amt = int(header.split("退還金額：$-")[1].strip())
                    return_total += amt
                except:
                    pass

        elif "【換貨】" in header:
            if "新商品金額:" in header:
                try:
                    amt = int(header.split("新商品金額:")[1].strip())
                    exchange_total += amt
                except:
                    pass

    if not sales_data:
        return jsonify({'status': 'error', 'message': '此區間無資料'}), 200

    # 建立 Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "月結報表"

    ws.append(["商品", "數量", "小計"])
    for name_size, info in sales_data.items():
        ws.append([name_size, info['qty'], info['qty'] * 0])  # 單價未知，暫填 0

    ws.append([])
    ws.append(["總金額", total])
    ws.append(["退貨金額", return_total])
    ws.append(["換貨新商品金額", exchange_total])

    filename = f"summary_{start_date}_{end_date}.xlsx"
    filepath = os.path.join("static", filename)
    wb.save(filepath)

    return jsonify({'status': 'success', 'file': filename})


@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory('static', filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, port=5050)
