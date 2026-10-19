import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import importlib.util
import os


def _load_retail_system_class():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidate_paths = [
        os.path.join(base_dir, "retailsystem.py"),
        os.path.join(base_dir, " retailsystem.py"),
    ]
    module_path = next((p for p in candidate_paths if os.path.exists(p)), None)
    if not module_path:
        raise ModuleNotFoundError("Could not find retailsystem.py in the same folder as retail_gui.py")

    spec = importlib.util.spec_from_file_location("retailsystem", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to load module spec from {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "RetailSystem"):
        raise AttributeError("RetailSystem class not found in retailsystem.py")
    return module.RetailSystem


RetailSystem = _load_retail_system_class()

class RetailSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Retail Management System")
        self.root.geometry("1000x700")
        
        # Initialize the retail system
        self.retail_system = RetailSystem()
        
        # Configure style
        self.palette = {
            "bg": "#0b1220",
            "panel": "#111b2e",
            "panel2": "#0f1a2b",
            "text": "#eaf2ff",
            "muted": "#b8c7e6",
            "accent": "#7c3aed",
            "accent2": "#06b6d4",
            "ok": "#22c55e",
            "warn": "#f59e0b",
            "danger": "#ef4444",
            "row_a": "#0f1a2b",
            "row_b": "#0c1524",
            "header": "#1b2a45",
        }

        self.root.configure(bg=self.palette["bg"])

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("TFrame", background=self.palette["bg"])
        self.style.configure("TLabelframe", background=self.palette["bg"], foreground=self.palette["text"])
        self.style.configure("TLabelframe.Label", background=self.palette["bg"], foreground=self.palette["muted"], font=("Helvetica", 10, "bold"))
        self.style.configure("TLabel", background=self.palette["bg"], foreground=self.palette["text"])
        self.style.configure(
            "TButton",
            padding=(10, 6),
            background=self.palette["accent"],
            foreground=self.palette["text"],
            bordercolor=self.palette["accent"],
            focusthickness=3,
            focuscolor=self.palette["accent2"],
        )
        self.style.map(
            "TButton",
            background=[("active", self.palette["accent2"]), ("disabled", self.palette["header"])],
            foreground=[("disabled", self.palette["muted"])],
        )

        self.style.configure(
            "TNotebook",
            background=self.palette["bg"],
            borderwidth=0,
        )
        self.style.configure(
            "TNotebook.Tab",
            font=("Helvetica", 10, "bold"),
            padding=(12, 8),
            background=self.palette["panel"],
            foreground=self.palette["muted"],
            bordercolor=self.palette["header"],
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", self.palette["accent"]), ("active", self.palette["accent2"])],
            foreground=[("selected", self.palette["text"]), ("active", self.palette["bg"])],
        )

        self.style.configure(
            "Treeview",
            background=self.palette["panel2"],
            fieldbackground=self.palette["panel2"],
            foreground=self.palette["text"],
            rowheight=26,
            bordercolor=self.palette["header"],
        )
        self.style.configure(
            "Treeview.Heading",
            background=self.palette["header"],
            foreground=self.palette["text"],
            font=("Helvetica", 10, "bold"),
        )
        self.style.map("Treeview", background=[("selected", self.palette["accent2"])], foreground=[("selected", self.palette["bg"])])
        
        # Create main container
        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_inventory_tab()
        self.create_sales_tab()
        self.create_reports_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(
            root,
            textvariable=self.status_var,
            anchor=tk.W,
            bg=self.palette["panel"],
            fg=self.palette["text"],
            padx=10,
            pady=6,
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initial refresh
        self.refresh_all()
    
    def create_dashboard_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Dashboard")
        
        # Dashboard widgets
        title = tk.Label(
            tab,
            text="Retail Management System",
            font=("Helvetica", 18, "bold"),
            bg=self.palette["bg"],
            fg=self.palette["text"],
        )
        title.pack(pady=10)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(tab, text="Quick Stats", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.total_products_var = tk.StringVar()
        self.total_sales_var = tk.StringVar()
        self.revenue_var = tk.StringVar()
        
        ttk.Label(stats_frame, text="Total Products:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Label(stats_frame, textvariable=self.total_products_var).grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(stats_frame, text="Total Sales:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Label(stats_frame, textvariable=self.total_sales_var).grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(stats_frame, text="Total Revenue:").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Label(stats_frame, textvariable=self.revenue_var).grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)
        
        # Recent activity frame
        activity_frame = ttk.LabelFrame(tab, text="Recent Activity", padding=10)
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.activity_text = scrolledtext.ScrolledText(
            activity_frame,
            height=10,
            bg=self.palette["panel2"],
            fg=self.palette["text"],
            insertbackground=self.palette["text"],
        )
        self.activity_text.pack(fill=tk.BOTH, expand=True)
    
    def create_inventory_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Inventory")
        
        # Toolbar
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Add Product", command=self.show_add_product_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Edit Product", command=self.edit_product).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Delete Product", command=self.delete_product).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Refresh", command=self.refresh_inventory).pack(side=tk.LEFT, padx=2)
        
        # Search
        search_frame = ttk.Frame(tab)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.filter_products())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Inventory treeview
        columns = ("ID", "Name", "Category", "Price", "Stock", "Sold")
        self.inventory_tree = ttk.Treeview(tab, columns=columns, show='headings', selectmode='browse')
        
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=100)
        
        self.inventory_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.inventory_tree, orient="vertical", command=self.inventory_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
    
    def create_sales_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Sales")
        
        # Left frame for products
        left_frame = ttk.Frame(tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Available Products").pack()
        
        # Products treeview
        columns = ("ID", "Name", "Price", "Stock")
        self.products_tree = ttk.Treeview(left_frame, columns=columns, show='headings', selectmode='browse')
        
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=100)
        
        self.products_tree.pack(fill=tk.BOTH, expand=True)
        
        # Right frame for cart
        right_frame = ttk.Frame(tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(right_frame, text="Shopping Cart").pack()
        
        # Cart treeview
        columns = ("ID", "Name", "Price", "Qty", "Total")
        self.cart_tree = ttk.Treeview(right_frame, columns=columns, show='headings')
        
        for col in columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=80)
        
        self.cart_tree.pack(fill=tk.BOTH, expand=True)
        
        # Cart controls
        cart_controls = ttk.Frame(right_frame)
        cart_controls.pack(fill=tk.X, pady=5)
        
        ttk.Button(cart_controls, text="Add to Cart", command=self.add_to_cart).pack(side=tk.LEFT, padx=2)
        ttk.Button(cart_controls, text="Remove from Cart", command=self.remove_from_cart).pack(side=tk.LEFT, padx=2)
        
        # Checkout frame
        checkout_frame = ttk.LabelFrame(right_frame, text="Checkout", padding=10)
        checkout_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(checkout_frame, text="Customer ID:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.customer_id_var = tk.StringVar()
        ttk.Entry(checkout_frame, textvariable=self.customer_id_var, width=20).grid(row=0, column=1, padx=5, pady=2)
        
        self.total_var = tk.StringVar(value="Total: $0.00")
        ttk.Label(checkout_frame, textvariable=self.total_var, font=('Helvetica', 10, 'bold')).grid(
            row=1, column=0, columnspan=2, pady=5)
            
        ttk.Button(checkout_frame, text="Process Sale", command=self.process_sale).grid(
            row=2, column=0, columnspan=2, pady=5, sticky=tk.EW)
    
    def create_reports_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Reports")
        
        # Report type selection
        report_frame = ttk.LabelFrame(tab, text="Generate Report", padding=10)
        report_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.report_type = tk.StringVar(value="sales")
        ttk.Radiobutton(report_frame, text="Sales Report", variable=self.report_type, value="sales").pack(anchor=tk.W)
        ttk.Radiobutton(report_frame, text="Inventory Report", variable=self.report_type, value="inventory").pack(anchor=tk.W)
        
        ttk.Button(report_frame, text="Generate", command=self.generate_report).pack(pady=5)
        
        # Report display
        report_display = ttk.LabelFrame(tab, text="Report Output", padding=10)
        report_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.report_text = scrolledtext.ScrolledText(
            report_display,
            height=15,
            bg=self.palette["panel2"],
            fg=self.palette["text"],
            insertbackground=self.palette["text"],
        )
        self.report_text.pack(fill=tk.BOTH, expand=True)
    
    # ====== Helper Methods ======
    
    def refresh_all(self):
        self.refresh_inventory()
        self.refresh_products()
        self.update_dashboard()
    
    def refresh_inventory(self):
        # Clear existing items
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Add products to treeview
        for idx, product in enumerate(self.retail_system.inventory.list_inventory()):
            tag = "row_a" if idx % 2 == 0 else "row_b"
            self.inventory_tree.insert("", tk.END, tags=(tag,), values=(
                product.product_id,
                product.name,
                product.category,
                f"${product.price:.2f}",
                product.stock,
                product.total_sold
            ))

        self.inventory_tree.tag_configure("row_a", background=self.palette["row_a"])
        self.inventory_tree.tag_configure("row_b", background=self.palette["row_b"])
    
    def refresh_products(self):
        # Clear existing items
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Add products to treeview
        idx = 0
        for product in self.retail_system.inventory.list_inventory():
            if product.stock > 0:  # Only show products with stock
                tag = "row_a" if idx % 2 == 0 else "row_b"
                self.products_tree.insert("", tk.END, tags=(tag,), values=(
                    product.product_id,
                    product.name,
                    f"${product.price:.2f}",
                    product.stock
                ))
                idx += 1

        self.products_tree.tag_configure("row_a", background=self.palette["row_a"])
        self.products_tree.tag_configure("row_b", background=self.palette["row_b"])
    
    def update_dashboard(self):
        # Update stats
        products = self.retail_system.inventory.list_inventory()
        self.total_products_var.set(str(len(products)))
        
        # Calculate total sales and revenue
        total_sales = sum(p.total_sold for p in products)
        total_revenue = sum(p.price * p.total_sold for p in products)
        
        self.total_sales_var.set(str(total_sales))
        self.revenue_var.set(f"${total_revenue:.2f}")
        
        # Update activity log
        self.activity_text.delete(1.0, tk.END)
        self.activity_text.insert(tk.END, "Recent Activity:\n\n")
        # Add some sample activity - you can replace with real data
        self.activity_text.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - System started\n")
        if products:
            self.activity_text.insert(tk.END, f"{len(products)} products loaded\n")
    
    def filter_products(self):
        search_term = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Filter and add matching products
        idx = 0
        for product in self.retail_system.inventory.list_inventory():
            if (search_term in str(product.product_id).lower() or
                search_term in product.name.lower() or
                search_term in product.category.lower()):
                tag = "row_a" if idx % 2 == 0 else "row_b"
                self.inventory_tree.insert("", tk.END, tags=(tag,), values=(
                    product.product_id,
                    product.name,
                    product.category,
                    f"${product.price:.2f}",
                    product.stock,
                    product.total_sold
                ))
                idx += 1

        self.inventory_tree.tag_configure("row_a", background=self.palette["row_a"])
        self.inventory_tree.tag_configure("row_b", background=self.palette["row_b"])
    
    def show_add_product_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Product")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Product ID:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        id_entry = ttk.Entry(dialog)
        id_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Name:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Category:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        category_entry = ttk.Entry(dialog)
        category_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Price:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        price_entry = ttk.Entry(dialog)
        price_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Initial Stock:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        stock_entry = ttk.Entry(dialog)
        stock_entry.insert(0, "0")
        stock_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        def save_product():
            try:
                product_id = int(id_entry.get())
                name = name_entry.get()
                category = category_entry.get()
                price = float(price_entry.get())
                stock = int(stock_entry.get())
                
                if not all([name, category]):
                    messagebox.showerror("Error", "All fields are required!")
                    return
                
                self.retail_system.inventory.add_product(product_id, name, category, price, stock)
                self.refresh_inventory()
                self.refresh_products()
                self.status_var.set(f"Added product: {name}")
                dialog.destroy()
                
            except ValueError as e:
                messagebox.showerror("Error", "Please enter valid values for all fields!")
        
        ttk.Button(dialog, text="Save", command=save_product).grid(row=5, column=0, columnspan=2, pady=10)
    
    def edit_product(self):
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to edit.")
            return
        
        # Get product ID from the selected row
        item = self.inventory_tree.item(selected[0])
        product_id = int(item['values'][0])
        
        # Find the product
        product = self.retail_system.inventory.get_product(product_id)
        if not product:
            messagebox.showerror("Error", "Product not found!")
            return
        
        # Create edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Product")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        name_var = tk.StringVar(value=product.name)
        ttk.Entry(dialog, textvariable=name_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Category:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        category_var = tk.StringVar(value=product.category)
        ttk.Entry(dialog, textvariable=category_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(dialog, text="Price:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        price_var = tk.StringVar(value=str(product.price))
        ttk.Entry(dialog, textvariable=price_var).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Stock:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        stock_var = tk.StringVar(value=str(product.stock))
        ttk.Entry(dialog, textvariable=stock_var).grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        def save_changes():
            try:
                # Update the product
                product.name = name_var.get()
                product.category = category_var.get()
                product.price = float(price_var.get())
                product.stock = int(stock_var.get())
                
                # Refresh the views
                self.refresh_inventory()
                self.refresh_products()
                self.status_var.set(f"Updated product: {product.name}")
                dialog.destroy()
                
            except ValueError as e:
                messagebox.showerror("Error", "Please enter valid values for all fields!")
        
        ttk.Button(dialog, text="Save Changes", command=save_changes).grid(row=4, column=0, columnspan=2, pady=10)
    
    def delete_product(self):
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to delete.")
            return
        
        item = self.inventory_tree.item(selected[0])
        product_id = int(item['values'][0])
        product_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {product_name}?"):
            self.retail_system.inventory.remove_product(product_id)
            self.refresh_inventory()
            self.refresh_products()
            self.status_var.set(f"Deleted product: {product_name}")
    
    def add_to_cart(self):
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product to add to cart.")
            return
        
        # Get product details
        item = self.products_tree.item(selected[0])
        product_id = int(item['values'][0])
        product_name = item['values'][1]
        price = float(item['values'][2].replace('$', ''))
        stock = int(item['values'][3])
        
        # Check if already in cart
        for child in self.cart_tree.get_children():
            cart_item = self.cart_tree.item(child)
            if cart_item['values'][0] == product_id:
                # Update quantity if already in cart
                qty = cart_item['values'][3] + 1
                if qty > stock:
                    messagebox.showwarning("Warning", f"Not enough stock for {product_name}")
                    return
                
                self.cart_tree.item(child, values=(
                    product_id,
                    product_name,
                    f"${price:.2f}",
                    qty,
                    f"${price * qty:.2f}"
                ))
                self.update_cart_total()
                return
        
        # Add new item to cart
        if stock > 0:
            self.cart_tree.insert("", tk.END, values=(
                product_id,
                product_name,
                f"${price:.2f}",
                1,
                f"${price:.2f}"
            ))
            self.update_cart_total()
        else:
            messagebox.showwarning("Warning", f"{product_name} is out of stock!")
    
    def remove_from_cart(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to remove from cart.")
            return
        
        self.cart_tree.delete(selected)
        self.update_cart_total()
    
    def update_cart_total(self):
        total = 0.0
        for child in self.cart_tree.get_children():
            item = self.cart_tree.item(child)
            total += float(item['values'][4].replace('$', ''))
        
        self.total_var.set(f"Total: ${total:.2f}")
    
    def process_sale(self):
        if not self.cart_tree.get_children():
            messagebox.showwarning("Warning", "Cart is empty!")
            return
        
        try:
            customer_id = int(self.customer_id_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid customer ID.")
            return
        
        # Create sale items
        sale_items = []
        for child in self.cart_tree.get_children():
            item = self.cart_tree.item(child)
            product_id = item['values'][0]
            quantity = item['values'][3]
            sale_items.append((product_id, quantity))
        
        # Process sale (this would be connected to your retail system)
        # For now, just show a success message
        total = sum(float(self.cart_tree.item(child)['values'][4].replace('$', '')) 
                   for child in self.cart_tree.get_children())
        
        # Clear the cart
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        self.total_var.set("Total: $0.00")
        self.customer_id_var.set("")
        
        messagebox.showinfo("Success", f"Sale processed successfully! Total: ${total:.2f}")
        self.status_var.set(f"Processed sale for customer {customer_id}")
        
        # Refresh inventory and dashboard
        self.refresh_inventory()
        self.refresh_products()
        self.update_dashboard()
    
    
    def generate_report(self):
        report_type = self.report_type.get()
        self.report_text.delete(1.0, tk.END)
        
        if report_type == "sales":
            self.generate_sales_report()
        elif report_type == "inventory":
            self.generate_inventory_report()
    
    def generate_sales_report(self):
        self.report_text.insert(tk.END, "SALES REPORT\n")
        self.report_text.insert(tk.END, "=" * 50 + "\n\n")
        
        # Add sample data (replace with actual data)
        self.report_text.insert(tk.END, f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Sales summary
        self.report_text.insert(tk.END, "SALES SUMMARY\n")
        self.report_text.insert(tk.END, "-" * 50 + "\n")
        self.report_text.insert(tk.END, f"Total Revenue: $1,250.75\n")
        self.report_text.insert(tk.END, f"Total Transactions: 15\n")
        self.report_text.insert(tk.END, f"Average Sale: $83.38\n\n")
        
        # Top products
        self.report_text.insert(tk.END, "TOP SELLING PRODUCTS\n")
        self.report_text.insert(tk.END, "-" * 50 + "\n")
        self.report_text.insert(tk.END, "Product ID\tProduct Name\t\tQty Sold\tRevenue\n")
        self.report_text.insert(tk.END, "1001\t\tLaptop\t\t\t8\t\t$9,599.92\n")
        self.report_text.insert(tk.END, "1002\t\tSmartphone\t\t12\t\t$8,388.00\n")
        self.report_text.insert(tk.END, "1003\t\tHeadphones\t\t15\t\t$1,196.25\n\n")
        
        # Sales by hour
        self.report_text.insert(tk.END, "SALES BY HOUR\n")
        self.report_text.insert(tk.END, "-" * 50 + "\n")
        self.report_text.insert(tk.END, "Hour\t\tSales\t\t% of Total\n")
        self.report_text.insert(tk.END, "12:00 PM\t$325.50\t\t26.0%\n")
        self.report_text.insert(tk.END, " 2:00 PM\t$275.25\t\t22.0%\n")
        self.report_text.insert(tk.END, " 4:00 PM\t$198.75\t\t15.9%\n")
    
    def generate_inventory_report(self):
        self.report_text.insert(tk.END, "INVENTORY REPORT\n")
        self.report_text.insert(tk.END, "=" * 50 + "\n\n")
        
        # Add sample data (replace with actual data)
        self.report_text.insert(tk.END, f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Inventory summary
        self.report_text.insert(tk.END, "INVENTORY SUMMARY\n")
        self.report_text.insert(tk.END, "-" * 80 + "\n")
        self.report_text.insert(tk.END, "ID\tName\t\t\tCategory\t\tPrice\t\tIn Stock\tValue\n")
        self.report_text.insert(tk.END, "-" * 80 + "\n")
        
        # Sample inventory items
        inventory_items = [
            (1001, "Laptop", "Electronics", 1199.99, 5, 5999.95),
            (1002, "Smartphone", "Electronics", 699.00, 8, 5592.00),
            (1003, "Headphones", "Accessories", 79.75, 12, 957.00),
            (1004, "Mouse", "Accessories", 24.99, 20, 499.80),
            (1005, "Keyboard", "Accessories", 49.99, 15, 749.85)
        ]
        
        for item in inventory_items:
            self.report_text.insert(tk.END, f"{item[0]}\t{item[1]}\t\t\t{item[2]}\t")
            self.report_text.insert(tk.END, f"${item[3]:.2f}\t\t{item[4]}\t\t${item[5]:.2f}\n")
        
        # Calculate totals
        total_items = sum(item[4] for item in inventory_items)
        total_value = sum(item[5] for item in inventory_items)
        
        self.report_text.insert(tk.END, "-" * 80 + "\n")
        self.report_text.insert(tk.END, f"TOTAL\t\t\t\t\t\t\t\t{total_items}\t\t${total_value:.2f}\n\n")
        
        # Low stock alert
        low_stock = [item for item in inventory_items if item[4] < 10]
        if low_stock:
            self.report_text.insert(tk.END, "\nLOW STOCK ALERTS\n")
            self.report_text.insert(tk.END, "-" * 50 + "\n")
            for item in low_stock:
                self.report_text.insert(tk.END, f"{item[1]} (ID: {item[0]}) - Only {item[4]} left in stock!\n")
    
def main():
    root = tk.Tk()
    app = RetailSystemGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
