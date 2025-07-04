USE inventory_system;

SELECT * FROM staff;

SELECT p.name, ps.style_name, ps.center_stock, ps.warehouse_stock
FROM products p
JOIN product_styles ps ON p.id = ps.product_id;
ALTER TABLE staff ADD COLUMN account VARCHAR(50) UNIQUE;

