import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import pandas as pd
from .theme import Theme

class ProvidersUI(ctk.CTkFrame):
    def __init__(self, parent, logic_manager):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.logic = logic_manager
        
        # Inicializar variables antes de usarlas
        self.combo_prov_purchase = None
        self.combo_prov_pay = None
        self.combo_prov_prices = None
        self.btn_upload_prices = None
        self.btn_import_parts = None
        
        # Layout principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Título Principal
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=Theme.PADDING_LARGE, pady=(Theme.PADDING_LARGE, 0))
        ctk.CTkLabel(header, text="🏢 GESTIÓN DE PROVEEDORES", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H1, "bold"), text_color=Theme.TEXT_PRIMARY).pack()
        
        ctk.CTkFrame(self, height=2, fg_color=Theme.DIVIDER).grid(row=1, column=0, sticky="ew", padx=Theme.PADDING_LARGE, pady=Theme.PADDING_SMALL)
        
        self.tabview = ctk.CTkTabview(self, fg_color=Theme.SURFACE, segmented_button_fg_color=Theme.BACKGROUND_LIGHT, segmented_button_selected_color=Theme.PRIMARY, text_color=Theme.TEXT_PRIMARY, corner_radius=Theme.RADIUS_LARGE, border_width=2, border_color=Theme.BORDER)
        self.tabview.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        self.tab_providers = self.tabview.add("Proveedores")
        self.tab_purchases = self.tabview.add("Compras")
        self.tab_payments = self.tabview.add("Pagos / Cuentas")
        self.tab_prices = self.tabview.add("Listas de Precios")
        
        self.setup_providers_tab()
        self.setup_purchases_tab()
        self.setup_payments_tab()
        self.setup_prices_tab()
        
    def setup_providers_tab(self):
        # Frame Izquierdo: Formulario
        left_frame = ctk.CTkFrame(self.tab_providers)
        left_frame.pack(side="left", fill="y", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(left_frame, text="GESTIÓN DE PROVEEDORES", font=("Arial", 16, "bold")).pack(pady=(0, 10))
        
        self.entry_nombre = ctk.CTkEntry(left_frame, placeholder_text="NOMBRE EMPRESA")
        self.entry_nombre.pack(pady=5, fill="x")
        
        self.entry_telefono = ctk.CTkEntry(left_frame, placeholder_text="TELÉFONO")
        self.entry_telefono.pack(pady=5, fill="x")
        
        self.entry_email = ctk.CTkEntry(left_frame, placeholder_text="EMAIL")
        self.entry_email.pack(pady=5, fill="x")
        
        self.entry_direccion = ctk.CTkEntry(left_frame, placeholder_text="DIRECCIÓN")
        self.entry_direccion.pack(pady=5, fill="x")
        
        ctk.CTkButton(left_frame, text="GUARDAR PROVEEDOR", command=self.save_provider).pack(pady=10, fill="x")
        ctk.CTkButton(left_frame, text="LIMPIAR", command=self.clear_provider_form, fg_color="gray").pack(pady=5, fill="x")
        
        # Frame Derecho: Lista
        right_frame = ctk.CTkFrame(self.tab_providers)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=(0, 10))
        
        columns = ("ID", "NOMBRE", "TELÉFONO", "EMAIL", "SALDO")
        self.tree_providers = ttk.Treeview(right_frame, columns=columns, show="headings", height=35)
        for col in columns:
            self.tree_providers.heading(col, text=col)
            self.tree_providers.column(col, width=100)
            
        self.tree_providers.pack(fill="both", expand=True)
        self.tree_providers.bind("<Double-1>", self.on_provider_select)
        
        ctk.CTkButton(right_frame, text="ACTUALIZAR LISTA", command=self.load_providers).pack(pady=5)
        
        self.load_providers()

    def setup_purchases_tab(self):
        # Frame Superior: Formulario de Nueva Compra
        top_frame = ctk.CTkFrame(self.tab_purchases)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(top_frame, text="REGISTRAR COMPRA", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=4, pady=5)
        
        self.combo_prov_purchase = ctk.CTkComboBox(top_frame, values=["SELECCIONE PROVEEDOR"])
        self.combo_prov_purchase.grid(row=1, column=0, padx=5, pady=5)
        
        self.entry_doc_type = ctk.CTkComboBox(top_frame, values=["FACTURA", "BOLETA", "GUIA"])
        self.entry_doc_type.grid(row=1, column=1, padx=5, pady=5)
        
        self.entry_doc_num = ctk.CTkEntry(top_frame, placeholder_text="N° DOCUMENTO")
        self.entry_doc_num.grid(row=1, column=2, padx=5, pady=5)
        
        self.check_credit = ctk.CTkCheckBox(top_frame, text="COMPRA A CRÉDITO")
        self.check_credit.grid(row=1, column=3, padx=5, pady=5)
        
        # Items de la compra
        self.items_frame = ctk.CTkScrollableFrame(self.tab_purchases, height=200, label_text="Items de la Compra")
        self.items_frame.pack(fill="x", padx=10, pady=5)
        
        # Campos para agregar item
        item_input_frame = ctk.CTkFrame(self.items_frame)
        item_input_frame.pack(fill="x")
        
        self.combo_item_type = ctk.CTkComboBox(item_input_frame, values=["REPUESTO", "PRODUCTO"], width=100)
        self.combo_item_type.pack(side="left", padx=2)
        
        self.entry_item_id = ctk.CTkEntry(item_input_frame, placeholder_text="ID PROD", width=60)
        self.entry_item_id.pack(side="left", padx=2)
        
        self.entry_item_qty = ctk.CTkEntry(item_input_frame, placeholder_text="CANTIDAD", width=60)
        self.entry_item_qty.pack(side="left", padx=2)
        
        self.entry_item_cost = ctk.CTkEntry(item_input_frame, placeholder_text="COSTO UNIT", width=80)
        self.entry_item_cost.pack(side="left", padx=2)
        
        self.entry_item_price = ctk.CTkEntry(item_input_frame, placeholder_text="PRECIO VENTA", width=80)
        self.entry_item_price.pack(side="left", padx=2)
        
        ctk.CTkButton(item_input_frame, text="+", width=30, command=self.add_item_to_list).pack(side="left", padx=5)
        
        self.cart_list = []
        self.lbl_cart_summary = ctk.CTkLabel(self.items_frame, text="ITEMS: 0 | TOTAL: $0")
        self.lbl_cart_summary.pack(pady=5)
        
        ctk.CTkButton(self.tab_purchases, text="CONFIRMAR COMPRA", command=self.submit_purchase, fg_color="green").pack(pady=10)
        
        # Historial de Compras
        self.tree_purchases = ttk.Treeview(self.tab_purchases, columns=("ID", "PROVEEDOR", "FECHA", "TOTAL", "DOC", "ESTADO"), show="headings", height=5)
        for col in ("ID", "PROVEEDOR", "FECHA", "TOTAL", "DOC", "ESTADO"):
            self.tree_purchases.heading(col, text=col)
            self.tree_purchases.column(col, width=80)
        self.tree_purchases.pack(fill="both", expand=True, padx=10, pady=5)

    def setup_payments_tab(self):
        # Panel Superior: Estado de Cuentas
        status_frame = ctk.CTkFrame(self.tab_payments)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        self.combo_prov_pay = ctk.CTkComboBox(status_frame, values=["SELECCIONE PROVEEDOR"], command=self.update_provider_balance)
        self.combo_prov_pay.pack(side="left", padx=10, pady=10)
        
        self.lbl_balance = ctk.CTkLabel(status_frame, text="SALDO PENDIENTE: $0", font=("Arial", 16, "bold"), text_color="red")
        self.lbl_balance.pack(side="left", padx=20)
        
        # Formulario de Pago
        pay_frame = ctk.CTkFrame(self.tab_payments)
        pay_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(pay_frame, text="REGISTRAR PAGO").pack(side="left", padx=5)
        self.entry_pay_amount = ctk.CTkEntry(pay_frame, placeholder_text="MONTO")
        self.entry_pay_amount.pack(side="left", padx=5)
        
        self.combo_pay_method = ctk.CTkComboBox(pay_frame, values=["EFECTIVO", "TRANSFERENCIA", "CHEQUE"])
        self.combo_pay_method.pack(side="left", padx=5)
        
        self.entry_pay_ref = ctk.CTkEntry(pay_frame, placeholder_text="REFERENCIA/COMPROBANTE")
        self.entry_pay_ref.pack(side="left", padx=5)
        
        ctk.CTkButton(pay_frame, text="PAGAR", command=self.submit_payment).pack(side="left", padx=10)
        
        # Historial de Pagos
        ctk.CTkLabel(self.tab_payments, text="HISTORIAL DE PAGOS").pack(pady=5)
        self.tree_payments = ttk.Treeview(self.tab_payments, columns=("ID", "FECHA", "MONTO", "MÉTODO", "REF"), show="headings")
        for col in ("ID", "FECHA", "MONTO", "MÉTODO", "REF"):
            self.tree_payments.heading(col, text=col)
        self.tree_payments.pack(fill="both", expand=True, padx=10, pady=10)

    # --- LOGIC HANDLERS ---
    
    def load_providers(self):
        for i in self.tree_providers.get_children(): self.tree_providers.delete(i)
        provs = self.logic.providers.get_all_providers()
        prov_names = []
        for p in provs:
            self.tree_providers.insert("", "end", values=(p[0], p[1], p[2], p[3], f"${p[5]:,.0f}"))
            prov_names.append(f"{p[0]} - {p[1]}")
        
        if self.combo_prov_purchase:
            self.combo_prov_purchase.configure(values=prov_names)
        if self.combo_prov_pay:
            self.combo_prov_pay.configure(values=prov_names)
        if self.combo_prov_prices:
            self.combo_prov_prices.configure(values=prov_names)
            # Mantener botones deshabilitados hasta que se seleccione un proveedor
            if len(prov_names) > 0 and self.combo_prov_prices.get() not in prov_names:
                self.combo_prov_prices.set("SELECCIONE PROVEEDOR")

    def save_provider(self):
        name = self.entry_nombre.get()
        if not name: return
        
        # Check if updating or creating (simple check: if name exists in list logic could be better but for now create new)
        # TODO: Add edit logic properly. For now, just add.
        if self.logic.providers.add_provider(name, self.entry_telefono.get(), self.entry_email.get(), self.entry_direccion.get()):
            messagebox.showinfo("ÉXITO", "PROVEEDOR GUARDADO")
            self.clear_provider_form()
            self.load_providers()
        else:
            messagebox.showerror("ERROR", "NO SE PUDO GUARDAR (¿NOMBRE DUPLICADO?)")

    def clear_provider_form(self):
        self.entry_nombre.delete(0, 'end')
        self.entry_telefono.delete(0, 'end')
        self.entry_email.delete(0, 'end')
        self.entry_direccion.delete(0, 'end')

    def on_provider_select(self, event):
        item = self.tree_providers.selection()
        if not item: return
        vals = self.tree_providers.item(item)['values']
        # Load into form
        self.entry_nombre.delete(0, 'end'); self.entry_nombre.insert(0, vals[1])
        self.entry_telefono.delete(0, 'end'); self.entry_telefono.insert(0, vals[2])
        self.entry_email.delete(0, 'end'); self.entry_email.insert(0, vals[3])
        # Address not in tree, would need fetch. Skipping for MVP.

    def add_item_to_list(self):
        try:
            pid = int(self.entry_item_id.get())
            qty = int(self.entry_item_qty.get())
            cost = float(self.entry_item_cost.get())
            price = float(self.entry_item_price.get())
            tipo = self.combo_item_type.get()
            
            utilidad = ((price - cost) / cost * 100) if cost > 0 else 0
            
            self.cart_list.append((pid, tipo, qty, cost, price, utilidad))
            
            total = sum(i[2]*i[3] for i in self.cart_list)
            self.lbl_cart_summary.configure(text=f"ITEMS: {len(self.cart_list)} | TOTAL COSTO: ${total:,.0f}")
            
            # Visual feedback
            lbl = ctk.CTkLabel(self.items_frame, text=f"{tipo} ID:{pid} x{qty} | Costo: ${cost} | Venta: ${price} | Utilidad: {utilidad:.1f}%")
            lbl.pack()
            
            self.entry_item_id.delete(0, 'end')
            self.entry_item_qty.delete(0, 'end')
            self.entry_item_cost.delete(0, 'end')
            self.entry_item_price.delete(0, 'end')
        except ValueError:
            messagebox.showerror("ERROR", "DATOS INVÁLIDOS")

    def submit_purchase(self):
        prov_str = self.combo_prov_purchase.get()
        if "SELECCIONE" in prov_str: 
            messagebox.showwarning("AVISO", "SELECCIONE PROVEEDOR"); return
        
        pid = int(prov_str.split(" - ")[0])
        total = sum(i[2]*i[3] for i in self.cart_list)
        
        if not self.cart_list:
            messagebox.showwarning("AVISO", "AGREGUE ITEMS A LA COMPRA")
            return
        
        # Transformar items al formato que entiende register_purchase (id, type, qty, cost)
        items_for_purchase = [(item[0], item[1], item[2], item[3]) for item in self.cart_list]
        
        if self.logic.providers.register_purchase(
            pid, self.entry_doc_type.get(), self.entry_doc_num.get(),
            items_for_purchase, "COMPRA SISTEMA"
        ):
            # Actualizar precios de venta si es necesario
            for item in self.cart_list:
                prod_id, prod_type, qty, cost, price, utilidad = item
                if prod_type == "REPUESTO":
                    self.logic.parts.update_part_price(prod_id, price)
                elif prod_type == "PRODUCTO":
                    self.logic.inventory.update_product_price(prod_id, price)
            
            messagebox.showinfo("ÉXITO", "COMPRA REGISTRADA Y STOCK ACTUALIZADO")
            self.cart_list = []
            self.lbl_cart_summary.configure(text="ITEMS: 0 | TOTAL COSTO: $0")
            # Limpiar lista visual
            for widget in self.items_frame.winfo_children():
                if isinstance(widget, ctk.CTkLabel) and "Items:" not in widget.cget("text"):
                    widget.destroy()
            self.load_purchases_history(pid)
        else:
            messagebox.showerror("ERROR", "Falló el registro")

    def load_purchases_history(self, pid):
        for i in self.tree_purchases.get_children(): self.tree_purchases.delete(i)
        purchases = self.logic.providers.get_purchases_by_provider(pid)
        for p in purchases:
            self.tree_purchases.insert("", "end", values=(p[0], pid, p[2], f"${p[3]:,.0f}", f"{p[5]} {p[6]}", p[4].upper()))

    def update_provider_balance(self, choice):
        if "SELECCIONE" in choice: return
        pid = int(choice.split(" - ")[0])
        bal = self.logic.providers.get_provider_balance(pid)
        self.lbl_balance.configure(text=f"SALDO PENDIENTE: ${bal:,.0f}")
        self.load_payments_history(pid)

    def submit_payment(self):
        prov_str = self.combo_prov_pay.get()
        if "SELECCIONE" in prov_str: return
        pid = int(prov_str.split(" - ")[0])
        
        try:
            monto = float(self.entry_pay_amount.get())
            if self.logic.providers.register_payment(pid, monto, self.combo_pay_method.get(), self.entry_pay_ref.get(), ""):
                messagebox.showinfo("ÉXITO", "PAGO REGISTRADO")
                self.update_provider_balance(prov_str)
                self.entry_pay_amount.delete(0, 'end')
            else:
                messagebox.showerror("ERROR", "FALLO AL REGISTRAR PAGO")
        except ValueError:
            messagebox.showerror("ERROR", "MONTO INVÁLIDO")

    def load_payments_history(self, pid):
        for i in self.tree_payments.get_children(): self.tree_payments.delete(i)
        pays = self.logic.providers.get_payments_by_provider(pid)
        for p in pays:
            self.tree_payments.insert("", "end", values=(p[0], p[2], f"${p[3]:,.0f}", p[4].upper(), p[5]))

    # --- LISTAS DE PRECIOS ---
    
    def setup_prices_tab(self):
        """Interfaz para gestionar listas de precios por proveedor"""
        main_frame = ctk.CTkFrame(self.tab_prices)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Panel Superior: Seleccionar proveedor y cargar archivo
        top_frame = ctk.CTkFrame(main_frame)
        top_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(top_frame, text="CARGAR LISTA DE PRECIOS", font=("Arial", 14, "bold")).pack(anchor="w", pady=5)
        
        select_frame = ctk.CTkFrame(top_frame)
        select_frame.pack(fill="x", pady=5)
        
        self.combo_prov_prices = ctk.CTkComboBox(select_frame, values=["SELECCIONE PROVEEDOR"], width=250, command=self.toggle_price_buttons)
        self.combo_prov_prices.pack(side="left", padx=5)
        
        self.btn_upload_prices = ctk.CTkButton(select_frame, text="CARGAR ARCHIVO EXCEL", command=self.upload_price_list, state="disabled")
        self.btn_upload_prices.pack(side="left", padx=5)
        
        self.btn_import_parts = ctk.CTkButton(select_frame, text="📦 IMPORTAR REPUESTOS AL INVENTARIO", command=self.import_parts_from_excel, fg_color="#28a745", width=220, state="disabled")
        self.btn_import_parts.pack(side="left", padx=5)
        ctk.CTkButton(select_frame, text="📋 GENERAR PLANTILLA VACÍA", command=self.generate_empty_template, fg_color="#17a2b8", width=180).pack(side="left", padx=5)
        
        # Botones de descarga de plantillas
        download_frame = ctk.CTkFrame(select_frame)
        download_frame.pack(side="left", padx=5)
        
        ctk.CTkButton(download_frame, text="📥 PLANTILLA REPUESTOS", command=self.download_parts_template, fg_color="#2196F3", width=160).pack(side="left", padx=2)
        ctk.CTkButton(download_frame, text="📥 PLANTILLA PRODUCTOS", command=self.download_products_template, fg_color="#2196F3", width=160).pack(side="left", padx=2)
        
        # Información
        info_frame = ctk.CTkFrame(top_frame)
        info_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(info_frame, text="FORMATO ESPERADO: COLUMNAS 'REPUESTO' (NOMBRE) Y 'PRECIO' (VALOR)", text_color="gray").pack(anchor="w")
        
        # Panel Central: Vista previa de precios cargados
        ctk.CTkLabel(main_frame, text="PRECIOS ACTIVOS POR PROVEEDOR", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        
        self.tree_prices = ttk.Treeview(main_frame, columns=("ID", "REPUESTO", "PRECIO", "ÚLTIMA ACTUALIZACIÓN"), show="headings", height=15)
        for col in ("ID", "REPUESTO", "PRECIO", "ÚLTIMA ACTUALIZACIÓN"):
            self.tree_prices.heading(col, text=col)
            self.tree_prices.column(col, width=150)
        
        self.tree_prices.pack(fill="both", expand=True, pady=5)
        self.tree_prices.bind("<Double-1>", self.edit_price_entry)
        
        # Panel Inferior: Acciones
        bottom_frame = ctk.CTkFrame(main_frame)
        bottom_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(bottom_frame, text="ACTUALIZAR LISTA", command=self.load_provider_prices).pack(side="left", padx=5)
        ctk.CTkButton(bottom_frame, text="ELIMINAR PRECIO", command=self.delete_price_entry, fg_color="red").pack(side="left", padx=5)
        
        self.lbl_price_status = ctk.CTkLabel(bottom_frame, text="", text_color="green")
        self.lbl_price_status.pack(side="right", padx=10)

    def import_parts_from_excel(self):
        """Importar repuestos desde Excel al inventario"""
        # Obtener proveedor seleccionado
        prov_str = self.combo_prov_prices.get()
        if "SELECCIONE" in prov_str:
            messagebox.showwarning("AVISO", "PRIMERO SELECCIONE UN PROVEEDOR")
            return
        
        try:
            proveedor_id = int(prov_str.split(" - ")[0])
        except:
            messagebox.showerror("ERROR", "ERROR AL OBTENER ID DEL PROVEEDOR")
            return
        
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo con repuestos",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        import os
        if not os.path.exists(file_path):
            messagebox.showerror("ERROR", f"EL ARCHIVO NO EXISTE:\n{file_path}")
            return
        
        try:
            # Leer archivo
            try:
                if file_path.endswith('.csv'):
                    df = pd.read_excel(file_path, encoding='utf-8')
                else:
                    df = pd.read_excel(file_path, engine='openpyxl')
            except PermissionError:
                messagebox.showerror("ERROR", "NO SE PUEDE ACCEDER AL ARCHIVO.\nCierre el archivo Excel e intente nuevamente.")
                return
            except Exception as read_error:
                messagebox.showerror("ERROR", f"NO SE PUDO LEER EL ARCHIVO:\n{str(read_error)}")
                return
            
            if df.empty:
                messagebox.showerror("ERROR", "EL ARCHIVO ESTÁ VACÍO")
                return
            
            # Normalizar columnas
            df.columns = df.columns.str.upper().str.strip()
            
            # Buscar columnas necesarias
            nombre_col = None
            categoria_col = None
            precio_col = None
            stock_col = None
            
            for col in df.columns:
                if 'NOMBRE' in col or 'PRODUCTO' in col or 'REPUESTO' in col:
                    nombre_col = col
                if 'CATEGORIA' in col or 'CATEGORÍA' in col:
                    categoria_col = col
                if 'PRECIO' in col and 'PROVEEDOR' not in col:
                    if not precio_col:  # Tomar el primer precio que no sea de proveedor
                        precio_col = col
                if 'STOCK' in col and 'ACTUAL' in col:
                    stock_col = col
            
            if not nombre_col:
                messagebox.showerror("ERROR", f"NO SE ENCONTRÓ COLUMNA DE NOMBRE.\n\nCOLUMNAS: {', '.join(df.columns)}")
                return
            
            # Confirmar importación
            if not messagebox.askyesno("CONFIRMAR", f"¿Importar {len(df)} repuestos al inventario?\n\nEsto creará nuevos registros."):
                return
            
            # Importar repuestos
            importados = 0
            duplicados = 0
            errores = 0
            
            for idx, row in df.iterrows():
                try:
                    nombre = str(row[nombre_col]).strip()
                    if nombre == 'nan' or not nombre:
                        continue
                    
                    # Obtener categoría
                    categoria = 'GENERAL'
                    if categoria_col and categoria_col in row:
                        cat_val = str(row[categoria_col]).strip()
                        if cat_val and cat_val != 'nan':
                            categoria = cat_val
                    
                    # Obtener precio
                    precio = 0
                    if precio_col and precio_col in row:
                        try:
                            precio_val = row[precio_col]
                            if not pd.isna(precio_val):
                                precio = float(precio_val)
                        except:
                            pass
                    
                    # Obtener stock
                    stock = 0
                    if stock_col and stock_col in row:
                        try:
                            stock_val = row[stock_col]
                            if not pd.isna(stock_val):
                                stock = int(stock_val)
                        except:
                            pass
                    
                    # Verificar si ya existe
                    partes_existentes = self.logic.parts.get_all_parts()
                    existe = False
                    for parte in partes_existentes:
                        if parte[1].upper() == nombre.upper():
                            existe = True
                            duplicados += 1
                            break
                    
                    if existe:
                        continue
                    
                    # Agregar repuesto con el proveedor seleccionado
                    # Parámetros: (nombre, costo, precio_sugerido, stock, categoria, proveedor_id)
                    costo_repuesto = 0  # Por defecto, el usuario lo actualizará después
                    if self.logic.parts.add_part(nombre, costo_repuesto, precio, stock, categoria, proveedor_id):
                        importados += 1
                    else:
                        errores += 1
                        
                except Exception as e:
                    errores += 1
                    continue
            
            # Mostrar resultado
            mensaje = f"✓ IMPORTACIÓN COMPLETADA\n\n"
            mensaje += f"• Importados: {importados}\n"
            if duplicados > 0:
                mensaje += f"• Duplicados (omitidos): {duplicados}\n"
            if errores > 0:
                mensaje += f"• Errores: {errores}"
            
            messagebox.showinfo("RESULTADO", mensaje)
            
        except Exception as e:
            messagebox.showerror("ERROR", f"ERROR AL IMPORTAR:\n{str(e)}")

    def generate_empty_template(self):
        """Generar plantilla vacía para llenar precios manualmente"""
        try:
            # Obtener todos los repuestos del inventario
            parts = self.logic.parts.get_all_parts()
            
            if not parts:
                messagebox.showwarning("AVISO", "NO HAY REPUESTOS EN EL INVENTARIO.\n\nPrimero debe importar repuestos usando el botón verde.")
                return
            
            # Crear DataFrame con columnas para completar
            data = {
                'NOMBRE': [part[1] for part in parts],
                'CATEGORIA': [part[2] if len(part) > 2 else 'GENERAL' for part in parts],
                'PRECIO_ACTUAL': [part[4] if len(part) > 4 else 0 for part in parts],
                'PRECIO_PROVEEDOR': [''] * len(parts),  # Vacío para completar
                'COSTO': [''] * len(parts),  # Vacío para completar
                'STOCK_ACTUAL': [part[5] if len(part) > 5 else 0 for part in parts],
                'NOTAS': [''] * len(parts)
            }
            
            df = pd.DataFrame(data)
            
            # Guardar archivo
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile="PLANTILLA_PRECIOS_VACIA.xlsx"
            )
            
            if file_path:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Precios', index=False)
                    
                    # Crear hoja de instrucciones
                    instrucciones = pd.DataFrame({
                        'INSTRUCCIONES PARA LLENAR LA PLANTILLA': [
                            '',
                            '═══════════════════════════════════════════════════════════════',
                            '1. CÓMO USAR ESTA PLANTILLA',
                            '═══════════════════════════════════════════════════════════════',
                            '',
                            '• Complete las columnas PRECIO_PROVEEDOR y COSTO con los valores del proveedor',
                            '• La columna PRECIO_ACTUAL es solo referencia (precio actual en el sistema)',
                            '• Puede agregar NOTAS si lo desea (ejemplo: "Precio especial", "Descuento 10%")',
                            '• NO modifique la columna NOMBRE (debe coincidir exactamente con los repuestos)',
                            '',
                            '═══════════════════════════════════════════════════════════════',
                            '2. COLUMNAS IMPORTANTES',
                            '═══════════════════════════════════════════════════════════════',
                            '',
                            '• NOMBRE: Identificador del repuesto (NO MODIFICAR)',
                            '• CATEGORIA: Clasificación del producto',
                            '• PRECIO_ACTUAL: Precio de venta actual en el sistema',
                            '• PRECIO_PROVEEDOR: Complete con el precio del proveedor (REQUERIDO)',
                            '• COSTO: Complete con el costo de compra (OPCIONAL)',
                            '• STOCK_ACTUAL: Stock disponible actualmente',
                            '• NOTAS: Observaciones adicionales (OPCIONAL)',
                            '',
                            '═══════════════════════════════════════════════════════════════',
                            '3. PROCESO DE IMPORTACIÓN',
                            '═══════════════════════════════════════════════════════════════',
                            '',
                            'PASO 1: Complete los precios en PRECIO_PROVEEDOR',
                            'PASO 2: (Opcional) Complete los costos en COSTO',
                            'PASO 3: Guarde el archivo Excel',
                            'PASO 4: Cierre Excel completamente',
                            'PASO 5: En ServitecManager, seleccione el proveedor',
                            'PASO 6: Haga clic en "CARGAR ARCHIVO EXCEL"',
                            'PASO 7: Seleccione este archivo',
                            '',
                            '═══════════════════════════════════════════════════════════════',
                            '4. NOTAS IMPORTANTES',
                            '═══════════════════════════════════════════════════════════════',
                            '',
                            '• Si deja PRECIO_PROVEEDOR vacío, ese repuesto se omitirá',
                            '• Los precios deben ser números (sin símbolos $ ni comas)',
                            '• Ejemplo correcto: 15000',
                            '• Ejemplo incorrecto: $15.000',
                            '• El archivo debe estar CERRADO antes de importar',
                            '',
                            f'Total de repuestos en esta plantilla: {len(parts)}',
                            f'Fecha de generación: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                        ]
                    })
                    instrucciones.to_excel(writer, sheet_name='INSTRUCCIONES', index=False)
                
                messagebox.showinfo("ÉXITO", f"✓ PLANTILLA GENERADA EXITOSAMENTE\n\n{len(parts)} repuestos incluidos\n\nArchivo: {file_path}")
                
        except Exception as e:
            messagebox.showerror("ERROR", f"ERROR AL GENERAR PLANTILLA:\n{str(e)}")

    def toggle_price_buttons(self, choice=None):
        """Habilitar/deshabilitar botones según selección de proveedor"""
        prov_str = self.combo_prov_prices.get()
        if "SELECCIONE" in prov_str:
            if self.btn_upload_prices:
                self.btn_upload_prices.configure(state="disabled")
            if self.btn_import_parts:
                self.btn_import_parts.configure(state="disabled")
        else:
            if self.btn_upload_prices:
                self.btn_upload_prices.configure(state="normal")
            if self.btn_import_parts:
                self.btn_import_parts.configure(state="normal")

    def upload_price_list(self):
        """Cargar lista de precios desde archivo Excel con detección inteligente"""
        prov_str = self.combo_prov_prices.get()
        print(f"DEBUG upload_price_list: prov_str = '{prov_str}'")
        
        if "SELECCIONE" in prov_str:
            messagebox.showwarning("AVISO", "SELECCIONE UN PROVEEDOR")
            return
        
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de precios",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        # Validar que el archivo existe
        import os
        if not os.path.exists(file_path):
            messagebox.showerror("ERROR", f"EL ARCHIVO NO EXISTE:\n{file_path}")
            return
        
        try:
            pid = int(prov_str.split(" - ")[0])
            
            # Leer archivo con manejo de errores mejorado
            try:
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path, encoding='utf-8')
                else:
                    # Intentar leer con openpyxl primero
                    df = pd.read_excel(file_path, engine='openpyxl')
            except PermissionError:
                messagebox.showerror("ERROR", "NO SE PUEDE ACCEDER AL ARCHIVO.\n\nPosibles causas:\n• El archivo está abierto en Excel\n• No tiene permisos de lectura\n\nCierre el archivo e intente nuevamente.")
                return
            except Exception as read_error:
                messagebox.showerror("ERROR", f"NO SE PUDO LEER EL ARCHIVO:\n{str(read_error)}\n\nVerifique que el archivo sea válido y no esté corrupto.")
                return
            
            # Verificar que el DataFrame no esté vacío
            if df.empty:
                messagebox.showerror("ERROR", "EL ARCHIVO ESTÁ VACÍO")
                return
            
            # Normalizar nombres de columnas
            df.columns = df.columns.str.upper().str.strip()
            
            # Detección inteligente de columnas
            producto_col = None
            precio_col = None
            costo_col = None
            
            # Buscar columna de producto
            for col in df.columns:
                if any(keyword in col for keyword in ['PRODUCTO', 'REPUESTO', 'NOMBRE', 'DESCRIPCIÓN', 'ITEM', 'ARTÍCULO']):
                    producto_col = col
                    break
            
            # Buscar columna de precio (aceptar PRECIO_PROVEEDOR, PRECIO, etc.)
            for col in df.columns:
                if any(keyword in col for keyword in ['PRECIO_PROVEEDOR', 'PRECIO PROVEEDOR', 'PRECIO', 'VENTA', 'PRECIO VENTA', 'PVP', 'VALOR']):
                    precio_col = col
                    break
            
            # Buscar columna de costo
            for col in df.columns:
                if any(keyword in col for keyword in ['COSTO', 'COSTO UNITARIO', 'PRECIO COMPRA', 'COSTO COMPRA']):
                    costo_col = col
                    break
            
            if not producto_col:
                messagebox.showerror("ERROR", f"NO SE ENCONTRÓ COLUMNA DE PRODUCTO.\n\nCOLUMNAS DETECTADAS: {', '.join(df.columns)}\n\nESPERADO: PRODUCTO, REPUESTO, NOMBRE, ETC.")
                return
            
            if not precio_col:
                messagebox.showerror("ERROR", f"NO SE ENCONTRÓ COLUMNA DE PRECIO.\n\nCOLUMNAS DETECTADAS: {', '.join(df.columns)}\n\nESPERADO: PRECIO, VENTA, PVP, ETC.")
                return
            
            # Procesar y guardar precios
            imported_count = 0
            skipped_count = 0
            
            for idx, row in df.iterrows():
                # Obtener nombre del repuesto
                try:
                    repuesto_name = str(row[producto_col]).upper().strip()
                    if repuesto_name == 'NAN' or not repuesto_name:
                        skipped_count += 1
                        continue
                except:
                    skipped_count += 1
                    continue
                
                # Obtener precio
                try:
                    precio_val = row[precio_col]
                    if pd.isna(precio_val) or precio_val == '' or precio_val == 0:
                        skipped_count += 1
                        continue
                    precio = float(precio_val)
                except:
                    skipped_count += 1
                    continue
                
                # Obtener costo si existe
                costo = None
                if costo_col and costo_col in row:
                    try:
                        costo_val = row[costo_col]
                        if not pd.isna(costo_val) and costo_val != '' and costo_val != 0:
                            costo = float(costo_val)
                    except:
                        pass
                
                # Buscar repuesto existente
                parts = self.logic.parts.get_all_parts()
                for part in parts:
                    if part[1].upper() == repuesto_name:
                        # Guardar precio del proveedor
                        if self.logic.providers.add_provider_price(pid, part[0], precio):
                            imported_count += 1
                        
                        # Actualizar precio de venta si no está configurado o si queremos sobrescribir
                        if precio > 0 and part[3] == 0:  # Si precio actual es 0
                            self.logic.parts.update_part_price(part[0], precio)
                        
                        # Actualizar costo si se proporcionó
                        if costo and costo > 0:
                            self.logic.parts.update_part_cost(part[0], costo)
                        break
            
            # Mensaje de resultado
            mensaje = f"✓ SE IMPORTARON {imported_count} PRECIOS CORRECTAMENTE"
            if skipped_count > 0:
                mensaje += f"\n\n⚠ Se omitieron {skipped_count} registros:\n• Sin nombre\n• Sin precio\n• Precio en 0\n• Repuesto no encontrado en inventario"
            
            messagebox.showinfo("ÉXITO", mensaje)
            self.load_provider_prices()
            self.lbl_price_status.configure(text=f"✓ CARGADOS {imported_count} PRECIOS")
            
        except Exception as e:
            messagebox.showerror("ERROR", f"ERROR AL PROCESAR ARCHIVO: {str(e).upper()}")

    def download_parts_template(self):
        """Descargar plantilla Excel con lista de repuestos del inventario"""
        try:
            # Obtener proveedor seleccionado
            prov_str = self.combo_prov_prices.get()
            proveedor_nombre = "TODOS"
            
            if "SELECCIONE" not in prov_str:
                proveedor_nombre = prov_str.split(" - ")[1] if " - " in prov_str else prov_str
            
            # Obtener todos los repuestos
            parts = self.logic.parts.get_all_parts()
            
            if not parts:
                messagebox.showwarning("AVISO", "NO HAY REPUESTOS EN EL INVENTARIO")
                return
            
            # Crear DataFrame con información completa
            data = {
                'NOMBRE': [part[1] for part in parts],
                'CATEGORIA': [part[2] if len(part) > 2 else '' for part in parts],
                'PRECIO_ACTUAL': [part[3] if len(part) > 3 else 0 for part in parts],
                'PRECIO_PROVEEDOR': [''] * len(parts),  # Columna vacía para completar
                'COSTO': [''] * len(parts),  # Columna vacía para completar
                'STOCK_ACTUAL': [part[4] if len(part) > 4 else 0 for part in parts],
                'NOTAS': [''] * len(parts)
            }
            
            df = pd.DataFrame(data)
            
            # Guardar archivo
            filename = f"LISTA_REPUESTOS_{proveedor_nombre.replace(' ', '_')}.xlsx"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=filename
            )
            
            if file_path:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Repuestos', index=False)
                    
                    # Crear hoja de instrucciones
                    instrucciones = pd.DataFrame({
                        'INSTRUCCIONES': [
                            '1. Complete las columnas PRECIO_PROVEEDOR y COSTO con los valores del proveedor',
                            '2. La columna PRECIO_ACTUAL es solo referencia (precio actual en el sistema)',
                            '3. Puede agregar NOTAS si lo desea',
                            '4. NO modifique la columna NOMBRE (debe coincidir con los repuestos existentes)',
                            '5. Guarde el archivo y cárguelo desde la opción "CARGAR ARCHIVO EXCEL"',
                            '',
                            'FORMATOS ACEPTADOS:',
                            '- NOMBRE o PRODUCTO o REPUESTO: Nombre del repuesto',
                            '- PRECIO o PRECIO_PROVEEDOR: Precio de venta',
                            '- COSTO: Costo de compra (opcional)',
                            '',
                            f'Total de repuestos: {len(parts)}'
                        ]
                    })
                    instrucciones.to_excel(writer, sheet_name='Instrucciones', index=False)
                
                messagebox.showinfo("ÉXITO", f"PLANTILLA DESCARGADA:\n{file_path}\n\n✓ {len(parts)} repuestos incluidos")
                
        except Exception as e:
            messagebox.showerror("ERROR", f"ERROR AL GENERAR PLANTILLA:\n{str(e)}")

    def download_products_template(self):
        """Descargar plantilla Excel con lista de productos del inventario"""
        try:
            # Obtener proveedor seleccionado
            prov_str = self.combo_prov_prices.get()
            proveedor_nombre = "TODOS"
            
            if "SELECCIONE" not in prov_str:
                proveedor_nombre = prov_str.split(" - ")[1] if " - " in prov_str else prov_str
            
            # Obtener todos los productos
            products = self.logic.products.get_all_products()
            
            if not products:
                messagebox.showwarning("AVISO", "NO HAY PRODUCTOS EN EL INVENTARIO")
                return
            
            # Crear DataFrame con información completa
            data = {
                'NOMBRE': [prod[1] for prod in products],
                'CODIGO_BARRA': [prod[2] if len(prod) > 2 else '' for prod in products],
                'PRECIO_ACTUAL': [prod[3] if len(prod) > 3 else 0 for prod in products],
                'PRECIO_PROVEEDOR': [''] * len(products),  # Columna vacía para completar
                'COSTO': [''] * len(products),  # Columna vacía para completar
                'STOCK_ACTUAL': [prod[4] if len(prod) > 4 else 0 for prod in products],
                'NOTAS': [''] * len(products)
            }
            
            df = pd.DataFrame(data)
            
            # Guardar archivo
            filename = f"LISTA_PRODUCTOS_{proveedor_nombre.replace(' ', '_')}.xlsx"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=filename
            )
            
            if file_path:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Productos', index=False)
                    
                    # Crear hoja de instrucciones
                    instrucciones = pd.DataFrame({
                        'INSTRUCCIONES': [
                            '1. Complete las columnas PRECIO_PROVEEDOR y COSTO con los valores del proveedor',
                            '2. La columna PRECIO_ACTUAL es solo referencia (precio actual en el sistema)',
                            '3. Puede agregar NOTAS si lo desea',
                            '4. NO modifique la columna NOMBRE (debe coincidir con los productos existentes)',
                            '5. Guarde el archivo y cárguelo desde la opción "CARGAR ARCHIVO EXCEL"',
                            '',
                            'FORMATOS ACEPTADOS:',
                            '- NOMBRE o PRODUCTO: Nombre del producto',
                            '- PRECIO o PRECIO_PROVEEDOR: Precio de venta',
                            '- COSTO: Costo de compra (opcional)',
                            '- CODIGO_BARRA: Código de barras (opcional)',
                            '',
                            f'Total de productos: {len(products)}'
                        ]
                    })
                    instrucciones.to_excel(writer, sheet_name='Instrucciones', index=False)
                
                messagebox.showinfo("ÉXITO", f"PLANTILLA DESCARGADA:\n{file_path}\n\n✓ {len(products)} productos incluidos")
                
        except Exception as e:
            messagebox.showerror("ERROR", f"ERROR AL GENERAR PLANTILLA:\n{str(e)}")

    def download_price_template(self):
        """Descargar plantilla Excel para cargar precios"""
        try:
            # Obtener todos los repuestos
            parts = self.logic.parts.get_all_parts()
            
            data = {
                'PRODUCTO': [part[1] for part in parts],
                'COSTO': [part[3] for part in parts],
                'PRECIO': [part[2] for part in parts]
            }
            
            df = pd.DataFrame(data)
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile="lista_precios_plantilla.xlsx"
            )
            
            if file_path:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("ÉXITO", f"PLANTILLA DESCARGADA EN: {file_path}")
        except Exception as e:
            messagebox.showerror("ERROR", f"ERROR AL DESCARGAR PLANTILLA: {str(e)}")

    def load_provider_prices(self):
        """Cargar y mostrar precios del proveedor seleccionado"""
        prov_str = self.combo_prov_prices.get()
        if "SELECCIONE" in prov_str:
            return
        
        for i in self.tree_prices.get_children():
            self.tree_prices.delete(i)
        
        try:
            pid = int(prov_str.split(" - ")[0])
            prices = self.logic.providers.get_provider_prices(pid)
            
            for price in prices:
                # price: (id, proveedor_id, repuesto_id, precio, fecha_actualizacion)
                repuesto = self.logic.parts.get_part_by_id(price[2])
                repuesto_name = repuesto[1] if repuesto else "DESCONOCIDO"
                
                self.tree_prices.insert("", "end", values=(
                    price[0],
                    repuesto_name,
                    f"${price[3]:,.0f}",
                    price[4][:10] if price[4] else "-"
                ))
        except Exception as e:
            messagebox.showerror("ERROR", f"ERROR AL CARGAR PRECIOS: {str(e)}")

    def edit_price_entry(self, event):
        """Permitir editar precio al hacer doble clic"""
        selection = self.tree_prices.selection()
        if not selection:
            return
        
        values = self.tree_prices.item(selection[0])['values']
        price_id = values[0]
        current_price = float(values[2].replace("$", "").replace(",", ""))
        
        new_price = ctk.CTkInputDialog(
            text=f"NUEVO PRECIO PARA {values[1]}:",
            title="EDITAR PRECIO"
        ).get_input()
        
        if new_price:
            try:
                new_price = float(new_price)
                if self.logic.providers.update_provider_price(price_id, new_price):
                    messagebox.showinfo("ÉXITO", "PRECIO ACTUALIZADO")
                    self.load_provider_prices()
            except ValueError:
                messagebox.showerror("ERROR", "INGRESE UN VALOR NUMÉRICO VÁLIDO")

    def delete_price_entry(self):
        """Eliminar entrada de precio"""
        selection = self.tree_prices.selection()
        if not selection:
            messagebox.showwarning("AVISO", "SELECCIONE UN PRECIO PARA ELIMINAR")
            return
        
        if messagebox.askyesno("CONFIRMAR", "¿DESEA ELIMINAR ESTA ENTRADA DE PRECIO?"):
            values = self.tree_prices.item(selection[0])['values']
            price_id = values[0]
            
            if self.logic.providers.delete_provider_price(price_id):
                messagebox.showinfo("ÉXITO", "PRECIO ELIMINADO")
                self.load_provider_prices()
            else:
                messagebox.showerror("ERROR", "NO SE PUDO ELIMINAR EL PRECIO")
