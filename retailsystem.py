
from collections import deque
from datetime import datetime
import random
import sys



class Product:
    def __init__(self, product_id: int, name: str, category: str, price: float, stock: int):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock
        self.total_sold = 0  

    def __repr__(self):
        return f"Product({self.product_id}, {self.name}, {self.category}, {self.price:.2f}, stock={self.stock}, sold={self.total_sold})"


class SaleItem:
    def __init__(self, product_id: int, quantity: int):
        self.product_id = product_id
        self.quantity = quantity


class Transaction:
    def __init__(self, transaction_id: int, customer_id: int, items: list[SaleItem], total_amount: float, timestamp: datetime):
        self.transaction_id = transaction_id
        self.customer_id = customer_id
        self.items = items
        self.total_amount = total_amount
        self.timestamp = timestamp

    def __repr__(self):
        return f"Transaction(id={self.transaction_id}, customer={self.customer_id}, total={self.total_amount:.2f}, time={self.timestamp.isoformat(timespec='seconds')})"


class Customer:
    def __init__(self, customer_id: int, name: str):
        self.customer_id = customer_id
        self.name = name
        self.purchase_history_stack: list[Transaction] = []  # Stack (LIFO)
        self.preferences: dict[str, int] = {}  # category -> count

    def __repr__(self):
        return f"Customer({self.customer_id}, {self.name})"



class StockChangeNode:
    def __init__(self, product_id: int, change: int, note: str, timestamp: datetime = None):
        self.product_id = product_id
        self.change = change
        self.note = note
        self.timestamp = timestamp or datetime.now()
        self.next = None


class StockChangeLinkedList:
    def __init__(self):
        self.head = None

    def add_change(self, product_id: int, change: int, note: str):
        node = StockChangeNode(product_id, change, note)
        node.next = self.head
        self.head = node

    def to_list_latest_n(self, n: int = 20):
        out = []
        cur = self.head
        while cur and len(out) < n:
            out.append(cur)
            cur = cur.next
        return out




class AVLNode:
    def __init__(self, key: int, product: Product):
        self.key = key
        self.product = product
        self.height = 1
        self.left = None
        self.right = None


class AVLTree:
    def __init__(self):
        self.root = None

    def get_height(self, node: AVLNode | None):
        return node.height if node else 0

    def update_height(self, node: AVLNode):
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))

    def get_balance(self, node: AVLNode | None):
        return 0 if not node else self.get_height(node.left) - self.get_height(node.right)

    def rotate_right(self, y: AVLNode):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        self.update_height(y)
        self.update_height(x)
        return x

    def rotate_left(self, x: AVLNode):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        self.update_height(x)
        self.update_height(y)
        return y

    def insert(self, node: AVLNode | None, key: int, product: Product) -> AVLNode:
        if not node:
            return AVLNode(key, product)
        if key < node.key:
            node.left = self.insert(node.left, key, product)
        elif key > node.key:
            node.right = self.insert(node.right, key, product)
        else:
            # Update product if key exists
            node.product = product
            return node

        self.update_height(node)
        balance = self.get_balance(node)

        # LL
        if balance > 1 and key < node.left.key:
            return self.rotate_right(node)
        # RR
        if balance < -1 and key > node.right.key:
            return self.rotate_left(node)
        # LR
        if balance > 1 and key > node.left.key:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)
        # RL
        if balance < -1 and key < node.right.key:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)

        return node

    def min_value_node(self, node: AVLNode):
        cur = node
        while cur.left:
            cur = cur.left
        return cur

    def delete(self, node: AVLNode | None, key: int) -> AVLNode | None:
        if not node:
            return node
        if key < node.key:
            node.left = self.delete(node.left, key)
        elif key > node.key:
            node.right = self.delete(node.right, key)
        else:
            # node with one child or none
            if not node.left:
                return node.right
            elif not node.right:
                return node.left
            # node with two children
            temp = self.min_value_node(node.right)
            node.key = temp.key
            node.product = temp.product
            node.right = self.delete(node.right, temp.key)

        self.update_height(node)
        balance = self.get_balance(node)

        # LL
        if balance > 1 and self.get_balance(node.left) >= 0:
            return self.rotate_right(node)
        # LR
        if balance > 1 and self.get_balance(node.left) < 0:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)
        # RR
        if balance < -1 and self.get_balance(node.right) <= 0:
            return self.rotate_left(node)
        # RL
        if balance < -1 and self.get_balance(node.right) > 0:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)

        return node

    def inorder(self, node: AVLNode | None, out: list[Product]):
        if not node:
            return
        self.inorder(node.left, out)
        out.append(node.product)
        self.inorder(node.right, out)

    def search(self, node: AVLNode | None, key: int) -> Product | None:
        if not node:
            return None
        if key == node.key:
            return node.product
        branch = node.left if key < node.key else node.right
        return self.search(branch, key)


# -----------------------------
# Inventory Manager (combines AVL + HashTable + LinkedList)
# -----------------------------

class InventoryManager:
    def __init__(self):
        self.tree = AVLTree()
        self.map: dict[int, Product] = {}  # product_id -> Product
        self.stock_changes = StockChangeLinkedList()

    def add_product(self, product_id: int, name: str, category: str, price: float, stock: int):
        if product_id in self.map:
            print(f"[WARN] Product ID {product_id} already exists. Updating.")
        product = Product(product_id, name, category, price, stock)
        self.map[product_id] = product
        self.tree.root = self.tree.insert(self.tree.root, product_id, product)
        self.stock_changes.add_change(product_id, stock, f"Initial add: {name}")

    def remove_product(self, product_id: int):
        prod = self.map.get(product_id)
        if not prod:
            print(f"[WARN] Product ID {product_id} not found.")
            return
        self.tree.root = self.tree.delete(self.tree.root, product_id)
        self.map.pop(product_id, None)
        self.stock_changes.add_change(product_id, -prod.stock, f"Removed: {prod.name}")

    def restock(self, product_id: int, quantity: int):
        product = self.map.get(product_id)
        if not product:
            print(f"[ERROR] Product {product_id} not found.")
            return False
        product.stock += quantity
        self.stock_changes.add_change(product_id, quantity, "Restock")
        return True

    def deduct_stock(self, product_id: int, quantity: int):
        product = self.map.get(product_id)
        if not product:
            return False, "Product not found."
        if product.stock < quantity:
            return False, "Insufficient stock."
        product.stock -= quantity
        product.total_sold += quantity
        self.stock_changes.add_change(product_id, -quantity, "Sale")
        return True, "OK"

    def get_product(self, product_id: int) -> Product | None:
        return self.map.get(product_id)

    def list_inventory(self) -> list[Product]:
        out: list[Product] = []
        self.tree.inorder(self.tree.root, out)
        return out

    def low_stock_alerts(self, threshold: int = 5) -> list[Product]:
        inventory = self.list_inventory()
        return [p for p in inventory if p.stock <= threshold]

    def slow_movers(self, sold_threshold: int = 2) -> list[Product]:
        inventory = self.list_inventory()
        return [p for p in inventory if p.total_sold <= sold_threshold]

    def predictive_restocking(self, min_stock: int = 10) -> list[tuple[Product, int]]:
        # Simple heuristic: if stock < min_stock and product has sold > 0, recommend restock to reach min_stock + sold
        recs = []
        for p in self.list_inventory():
            if p.stock < min_stock and p.total_sold > 0:
                target = min_stock + p.total_sold
                recs.append((p, max(0, target - p.stock)))
        return recs


# -----------------------------
# Sales Manager (Queue + Stack)
# -----------------------------

class SalesManager:
    def __init__(self, inventory: InventoryManager):
        self.inventory = inventory
        self.checkout_queue: deque[tuple[int, list[SaleItem]]] = deque()  # (customer_id, items)
        self.transactions_stack: list[Transaction] = []  # Stack
        self.next_transaction_id = 1000
        self.total_revenue = 0.0
        self.sales_by_hour: dict[int, float] = {}  # hour -> revenue

    def enqueue_checkout(self, customer_id: int, items: list[SaleItem]):
        self.checkout_queue.append((customer_id, items))

    def process_next_checkout(self) -> bool:
        if not self.checkout_queue:
            print("[INFO] Queue is empty.")
            return False
        customer_id, items = self.checkout_queue.popleft()
        # Validate and compute total
        total = 0.0
        validated: list[tuple[SaleItem, Product]] = []
        for item in items:
            product = self.inventory.get_product(item.product_id)
            if not product:
                print(f"[ERROR] Product {item.product_id} missing. Skipping checkout.")
                return False
            if product.stock < item.quantity:
                print(f"[ERROR] Insufficient stock for {product.name}. Needed {item.quantity}, available {product.stock}.")
                return False
            validated.append((item, product))

        # Deduct stock
        for item, product in validated:
            ok, msg = self.inventory.deduct_stock(item.product_id, item.quantity)
            if not ok:
                print("[ERROR]", msg)
                return False
            total += product.price * item.quantity

        txn = Transaction(self.next_transaction_id, customer_id, items, total, datetime.now())
        self.next_transaction_id += 1
        self.transactions_stack.append(txn)
        self.total_revenue += total
        hour = txn.timestamp.hour
        self.sales_by_hour[hour] = self.sales_by_hour.get(hour, 0.0) + total
        print(f"[OK] Processed {txn}")
        return True

    def refund_last_transaction(self) -> bool:
        if not self.transactions_stack:
            print("[INFO] No transactions to refund.")
            return False
        txn = self.transactions_stack.pop()
        # Reverse stock deductions
        for item in txn.items:
            self.inventory.restock(item.product_id, item.quantity)
            # reverse sold count
            p = self.inventory.get_product(item.product_id)
            if p:
                p.total_sold = max(0, p.total_sold - item.quantity)
        self.total_revenue -= txn.total_amount
        hour = txn.timestamp.hour
        self.sales_by_hour[hour] = max(0.0, self.sales_by_hour.get(hour, 0.0) - txn.total_amount)
        print(f"[OK] Refunded {txn}")
        return True

    def sales_report(self):
        print("\n== Sales Report ==")
        print(f"Total revenue: {self.total_revenue:.2f}")
        # Peak hour
        if self.sales_by_hour:
            peak_hour, peak_revenue = max(self.sales_by_hour.items(), key=lambda kv: kv[1])
            print(f"Peak hour: {peak_hour}:00 with revenue {peak_revenue:.2f}")
        else:
            print("No sales yet.")
        print("Recent transactions (top 5):")
        for txn in self.transactions_stack[-5:][::-1]:
            print(f" - {txn}")


# -----------------------------
# CRM Manager (LinkedList + Stack + HashMap)
# -----------------------------

class InteractionNode:
    def __init__(self, customer_id: int, note: str, timestamp: datetime = None):
        self.customer_id = customer_id
        self.note = note
        self.timestamp = timestamp or datetime.now()
        self.next = None


class InteractionLinkedList:
    def __init__(self):
        self.head = None

    def add(self, customer_id: int, note: str):
        node = InteractionNode(customer_id, note)
        node.next = self.head
        self.head = node

    def to_list_latest_n(self, n: int = 20):
        out = []
        cur = self.head
        while cur and len(out) < n:
            out.append(cur)
            cur = cur.next
        return out


class CRMManager:
    def __init__(self):
        self.customers: dict[int, Customer] = {}  # HashMap
        self.interactions = InteractionLinkedList()

    def add_customer(self, customer_id: int, name: str):
        if customer_id in self.customers:
            print(f"[WARN] Customer {customer_id} exists. Updating name.")
        self.customers[customer_id] = Customer(customer_id, name)

    def record_purchase(self, customer_id: int, txn: Transaction, inventory: InventoryManager):
        cust = self.customers.get(customer_id)
        if not cust:
            print(f"[WARN] Unknown customer {customer_id}. Auto-creating.")
            cust = Customer(customer_id, f"Customer {customer_id}")
            self.customers[customer_id] = cust
        cust.purchase_history_stack.append(txn)
        # Update preferences
        prefs = cust.preferences
        for item in txn.items:
            p = inventory.get_product(item.product_id)
            if p:
                prefs[p.category] = prefs.get(p.category, 0) + item.quantity
        self.interactions.add(customer_id, f"Purchase: total {txn.total_amount:.2f}")

    def recent_interactions(self):
        print("\n== Recent CRM Interactions ==")
        for node in self.interactions.to_list_latest_n():
            print(f" - [{node.timestamp.isoformat(timespec='seconds')}] Customer {node.customer_id}: {node.note}")

    def customer_profile(self, customer_id: int):
        cust = self.customers.get(customer_id)
        if not cust:
            print(f"[INFO] Customer {customer_id} not found.")
            return
        print(f"\n== Customer Profile: {cust.name} (ID: {cust.customer_id}) ==")
        print("Preferences:", cust.preferences or "{}")
        print("Recent purchases (top 5):")
        for txn in cust.purchase_history_stack[-5:][::-1]:
            print(f" - {txn}")


# -----------------------------
# Recommendation Engine (Sorting + Searching)
# -----------------------------

class RecommendationEngine:
    def __init__(self, inventory: InventoryManager, crm: CRMManager):
        self.inventory = inventory
        self.crm = crm

    def popular_products(self, top_n: int = 5) -> list[Product]:
        # Sort by total_sold desc, then stock availability
        products = self.inventory.list_inventory()
        products.sort(key=lambda p: (p.total_sold, p.stock), reverse=True)
        return products[:top_n]

    def recommend_for_customer(self, customer_id: int, top_n: int = 5) -> list[Product]:
        cust = self.crm.customers.get(customer_id)
        if not cust:
            # default popular products
            return self.popular_products(top_n)
        # Recommend based on preferred categories, fallback to popular
        # Gather categories ordered by preference
        preferred = sorted(cust.preferences.items(), key=lambda kv: kv[1], reverse=True)
        recommended: list[Product] = []
        seen: set[int] = set()
        products = self.inventory.list_inventory()
        # First pass: preferred categories
        for cat, _count in preferred:
            for p in products:
                if p.category == cat and p.stock > 0 and p.product_id not in seen:
                    recommended.append(p)
                    seen.add(p.product_id)
                    if len(recommended) >= top_n:
                        return recommended
        # Second pass: popular products
        for p in self.popular_products(top_n * 2):
            if p.product_id not in seen and p.stock > 0:
                recommended.append(p)
                seen.add(p.product_id)
                if len(recommended) >= top_n:
                    break
        return recommended[:top_n]


# -----------------------------
# Simple Console UI / Dashboard
# -----------------------------

class RetailSystem:
    def __init__(self):
        self.inventory = InventoryManager()
        self.sales = SalesManager(self.inventory)
        self.crm = CRMManager()
        self.reco = RecommendationEngine(self.inventory, self.crm)
        self.seed_sample_data()

    def seed_sample_data(self):
        # Products
        sample_products = [
            (101, "Laptop Pro 14", "Electronics", 1200.00, 12),
            (102, "Wireless Mouse", "Electronics", 25.50, 50),
            (103, "Coffee Beans 1kg", "Grocery", 12.99, 30),
            (104, "Notebook A5", "Stationery", 3.20, 100),
            (105, "Headphones ANC", "Electronics", 199.99, 20),
            (106, "Green Tea 200g", "Grocery", 5.49, 40),
            (107, "Mechanical Keyboard", "Electronics", 89.00, 15),
            (108, "Water Bottle 1L", "Grocery", 7.99, 60),
        ]
        for pid, name, cat, price, stock in sample_products:
            self.inventory.add_product(pid, name, cat, price, stock)

        # Customers
        customers = [(1, "Aly"), (2, "Sara"), (3, "Omar")]
        for cid, name in customers:
            self.crm.add_customer(cid, name)

        # Seed a few sales
        for _ in range(4):
            cid = random.choice([1, 2, 3])
            items = [
                SaleItem(random.choice([101, 102, 105, 107]), random.choice([1, 1, 2])),
                SaleItem(random.choice([103, 106, 108, 104]), random.choice([1, 2]))
            ]
            self.sales.enqueue_checkout(cid, items)
            if self.sales.process_next_checkout():
                txn = self.sales.transactions_stack[-1]
                self.crm.record_purchase(cid, txn, self.inventory)

    def dashboard(self):
        print("\n=== Retail Dashboard ===")
        print(f"Products: {len(self.inventory.map)} | Customers: {len(self.crm.customers)} | Revenue: {self.sales.total_revenue:.2f}")
        lows = self.inventory.low_stock_alerts()
        if lows:
            print("Low-stock alerts:", ", ".join([f"{p.name}({p.stock})" for p in lows]))
        else:
            print("Low-stock alerts: None")
        print("Top popular products:")
        for p in self.reco.popular_products():
            print(f" - {p.name} | Sold: {p.total_sold} | Stock: {p.stock}")

    def menu(self):
        while True:
            self.dashboard()
            print("\nMenu:")
            print(" 1) Add product")
            print(" 2) Restock product")
            print(" 3) Remove product")
            print(" 4) Enqueue checkout")
            print(" 5) Process next checkout")
            print(" 6) Refund last transaction")
            print(" 7) Sales report")
            print(" 8) View inventory")
            print(" 9) CRM: customer profile")
            print("10) CRM: recent interactions")
            print("11) Recommendations for customer")
            print("12) Predictive restocking suggestions")
            print("13) Exit")
            choice = input("Choose: ").strip()
            try:
                choice_int = int(choice)
            except ValueError:
                print("[ERROR] Invalid input.")
                continue

            if choice_int == 1:
                try:
                    pid = int(input("Product ID: "))
                    name = input("Name: ")
                    cat = input("Category: ")
                    price = float(input("Price: "))
                    stock = int(input("Initial stock: "))
                    self.inventory.add_product(pid, name, cat, price, stock)
                except Exception as e:
                    print("[ERROR]", e)

            elif choice_int == 2:
                try:
                    pid = int(input("Product ID: "))
                    qty = int(input("Quantity to add: "))
                    ok = self.inventory.restock(pid, qty)
                    if ok:
                        print("[OK] Restocked.")
                except Exception as e:
                    print("[ERROR]", e)

            elif choice_int == 3:
                try:
                    pid = int(input("Product ID to remove: "))
                    self.inventory.remove_product(pid)
                except Exception as e:
                    print("[ERROR]", e)

            elif choice_int == 4:
                try:
                    cid = int(input("Customer ID: "))
                    items = []
                    while True:
                        pid = int(input(" Product ID (0 to stop): "))
                        if pid == 0:
                            break
                        qty = int(input(" Quantity: "))
                        items.append(SaleItem(pid, qty))
                    self.sales.enqueue_checkout(cid, items)
                    print("[OK] Enqueued.")
                except Exception as e:
                    print("[ERROR]", e)

            elif choice_int == 5:
                ok = self.sales.process_next_checkout()
                if ok:
                    txn = self.sales.transactions_stack[-1]
                    self.crm.record_purchase(txn.customer_id, txn, self.inventory)

            elif choice_int == 6:
                self.sales.refund_last_transaction()

            elif choice_int == 7:
                self.sales.sales_report()

            elif choice_int == 8:
                print("\n== Inventory ==")
                for p in self.inventory.list_inventory():
                    print(f" - {p.product_id}: {p.name} | {p.category} | {p.price:.2f} | Stock={p.stock} | Sold={p.total_sold}")

            elif choice_int == 9:
                try:
                    cid = int(input("Customer ID: "))
                    self.crm.customer_profile(cid)
                except Exception as e:
                    print("[ERROR]", e)

            elif choice_int == 10:
                self.crm.recent_interactions()

            elif choice_int == 11:
                try:
                    cid = int(input("Customer ID: "))
                    recs = self.reco.recommend_for_customer(cid)
                    print("\n== Recommendations ==")
                    for p in recs:
                        print(f" - {p.name} ({p.category}) | Price {p.price:.2f} | Stock {p.stock}")
                except Exception as e:
                    print("[ERROR]", e)

            elif choice_int == 12:
                recs = self.inventory.predictive_restocking()
                print("\n== Predictive Restocking ==")
                if not recs:
                    print("No recommendations. Stocks look healthy or no sales yet.")
                for p, qty in recs:
                    print(f" - {p.name}: Recommend restock {qty} units (current {p.stock}, sold {p.total_sold})")

            elif choice_int == 13:
                print("Goodbye.")
                break
            else:
                print("[INFO] Invalid choice.")

def main():
    system = RetailSystem()
    system.menu()

if __name__ == "__main__":
    # Ensure Python 3.10+ for type hints, but code runs on 3.8+ if you ignore typing
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting...")
        sys.exit(0)
