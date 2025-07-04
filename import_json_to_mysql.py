import json
import pymysql

# 資料庫連線設定
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='1118',
    database='inventory_system',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

with conn:
    with conn.cursor() as cursor:
        # 匯入 staff.json
        with open('staff.json', 'r', encoding='utf-8') as f:
            staff_data = json.load(f)
            for staff in staff_data.values():
                cursor.execute("SELECT id FROM staff WHERE name=%s", (staff['name'],))
                result = cursor.fetchone()
                if result:
                    cursor.execute(
                        "UPDATE staff SET password=%s WHERE id=%s",
                        (staff['password'], result['id'])
                    )
                else:
                    cursor.execute(
                        "INSERT INTO staff (name, password) VALUES (%s, %s)",
                        (staff['name'], staff['password'])
                    )

        # 匯入 inventory.json
        with open('inventory.json', 'r', encoding='utf-8') as f:
            inventory_data = json.load(f)
            for product in inventory_data.values():
                cursor.execute("SELECT id FROM products WHERE name=%s", (product['name'],))
                product_row = cursor.fetchone()
                if product_row:
                    product_id = product_row['id']
                    cursor.execute(
                        "UPDATE products SET category=%s, price=%s WHERE id=%s",
                        (product['category'], product['price'], product_id)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO products (name, category, price) VALUES (%s, %s, %s)",
                        (product['name'], product['category'], product['price'])
                    )
                    product_id = cursor.lastrowid

                # 處理 styles
                for style, stock in product['styles'].items():
                    cursor.execute("""
                        SELECT id FROM product_styles 
                        WHERE product_id=%s AND style_name=%s
                    """, (product_id, style))
                    style_row = cursor.fetchone()
                    if style_row:
                        cursor.execute("""
                            UPDATE product_styles 
                            SET center_stock=%s, warehouse_stock=%s 
                            WHERE id=%s
                        """, (stock['center'], stock['warehouse'], style_row['id']))
                    else:
                        cursor.execute("""
                            INSERT INTO product_styles 
                            (product_id, style_name, center_stock, warehouse_stock)
                            VALUES (%s, %s, %s, %s)
                        """, (product_id, style, stock['center'], stock['warehouse']))

    conn.commit()
