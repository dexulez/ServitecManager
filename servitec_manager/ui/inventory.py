import customtkinter as ctk
from tkinter import messagebox
from .import_dialog import ImportDialog
from .theme import Theme

class InventoryFrame(ctk.CTkFrame):
    def __init__(self, parent, logic, current_user):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.logic = logic
        self.current_user = current_user

        # Título Principal
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=Theme.PADDING_LARGE, padx=Theme.PADDING_LARGE)
        ctk.CTkLabel(header, text="📦 GESTIÓN DE INVENTARIO", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H1, "bold"), text_color=Theme.TEXT_PRIMARY).pack()
        
        ctk.CTkFrame(self, height=2, fg_color=Theme.DIVIDER).pack(fill="x", pady=(0, Theme.PADDING_MEDIUM))

        self.tabview = ctk.CTkTabview(self, fg_color=Theme.SURFACE, segmented_button_fg_color=Theme.BACKGROUND_LIGHT, segmented_button_selected_color=Theme.PRIMARY, text_color=Theme.TEXT_PRIMARY, corner_radius=Theme.RADIUS_LARGE, border_width=2, border_color=Theme.BORDER)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_prod = self.tabview.add("PRODUCTOS (VENTA POS)")
        self.tab_parts = self.tabview.add("REPUESTOS (TALLER)")
        self.tab_serv = self.tabview.add("SERVICIOS (MANO OBRA)")

        self.setup_crud_tab(self.tab_prod, "PRODUCTO", self.load_products, self.open_product_form, self.delete_product)
        self.setup_crud_tab(self.tab_parts, "REPUESTO", self.load_parts, self.open_part_form, self.delete_part)
        self.setup_crud_tab(self.tab_serv, "SERVICIO", self.load_services, self.open_service_form, self.delete_service)
        
        # Inicializar flags de carga
        self.tabs_loaded = {"PRODUCTOS (VENTA POS)": False, "REPUESTOS (TALLER)": False, "SERVICIOS (MANO OBRA)": False}
        
        # Event handler para cargar pestañas bajo demanda
        self.tabview.configure(command=self.on_tab_change)
        
        # Cargar solo la primera pestaña inicialmente
        self.load_products()
        self.tabs_loaded["PRODUCTOS (VENTA POS)"] = True

    def refresh(self):
        # Recargar solo la pestaña activa
        current_tab = self.tabview.get()
        if current_tab == "PRODUCTOS (VENTA POS)":
            self.load_products()
        elif current_tab == "REPUESTOS (TALLER)":
            self.load_parts()
        elif current_tab == "SERVICIOS (MANO OBRA)":
            self.load_services()
    
    def on_tab_change(self):
        """Cargar datos de la pestaña solo cuando se selecciona por primera vez"""
        current_tab = self.tabview.get()
        if not self.tabs_loaded.get(current_tab, False):
            if current_tab == "PRODUCTOS (VENTA POS)":
                self.load_products()
            elif current_tab == "REPUESTOS (TALLER)":
                self.load_parts()
            elif current_tab == "SERVICIOS (MANO OBRA)":
                self.load_services()
            self.tabs_loaded[current_tab] = True

    def setup_crud_tab(self, parent, label_type, load_func, add_func, del_func):
        # Toolbar
        top = ctk.CTkFrame(parent, **Theme.get_card_style())
        top.pack(fill="x", pady=Theme.PADDING_MEDIUM, padx=Theme.PADDING_MEDIUM)
        
        ctk.CTkLabel(top, text=f"📋 {label_type}S", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, "bold"), text_color=Theme.TEXT_PRIMARY).pack(side="left", padx=15, pady=10)
        
        # Botones
        ctk.CTkButton(top, text=f"➕ NUEVO {label_type}", command=lambda: add_func(None), **Theme.get_button_style("success"), height=35).pack(side="right", padx=5, pady=5)
        ctk.CTkButton(top, text="📥 IMPORTAR", command=lambda: ImportDialog(self, self.logic), **Theme.get_button_style("accent"), height=35).pack(side="right", padx=5, pady=5)
        ctk.CTkButton(top, text="🔄", command=load_func, **Theme.get_button_style("secondary"), width=45, height=35).pack(side="right", padx=5, pady=5)

        # Buscador
        search_var = ctk.StringVar()
        search_var.trace("w", lambda *a: self.filter_list(parent, search_var.get()))
        ctk.CTkEntry(top, textvariable=search_var, placeholder_text="🔍 BUSCAR...", width=200, height=35, border_color=Theme.BORDER, corner_radius=Theme.RADIUS_SMALL).pack(side="right", padx=15, pady=5)

        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=Theme.PADDING_MEDIUM, pady=Theme.PADDING_SMALL)
        parent.scroll_frame = scroll

    # --- PRODUCTOS (POS) ---
    def load_products(self):
        self.clear_scroll(self.tab_prod.scroll_frame)
        items = self.logic.inventory.get_products_with_provider()
        self.tab_prod.items_cache = items
        self.render_products(items)

    def render_products(self, items):
        self.clear_scroll(self.tab_prod.scroll_frame)
        header = ctk.CTkFrame(self.tab_prod.scroll_frame, fg_color=Theme.PRIMARY, corner_radius=Theme.RADIUS_SMALL)
        header.pack(fill="x", pady=(0, 5))
        self.make_cell(header, "NOMBRE", 180, Theme.WHITE, True)
        self.make_cell(header, "CATEGORÍA", 90, Theme.WHITE, True)
        self.make_cell(header, "PROVEEDOR", 120, Theme.WHITE, True)
        self.make_cell(header, "PRECIO", 70, Theme.WHITE, True)
        self.make_cell(header, "STOCK", 50, Theme.WHITE, True)
        for i in items:
            row = ctk.CTkFrame(self.tab_prod.scroll_frame, fg_color=Theme.SURFACE, corner_radius=Theme.RADIUS_SMALL)
            row.pack(fill="x", pady=2)
            self.make_cell(row, i['nombre'], 180)
            self.make_cell(row, i['categoria'], 90)
            # Proveedor
            proveedor_text = i.get('proveedor_nombre') or "SIN PROVEEDOR"
            color = Theme.TEXT_SECONDARY if i.get('proveedor_nombre') else "#999999"
            self.make_cell(row, proveedor_text, 120, color)
            self.make_cell(row, f"${int(i['precio']):,}".replace(",", "."), 70, Theme.PRIMARY, True)
            self.make_cell(row, str(i['stock']), 50)
            ctk.CTkButton(row, text="✏️", width=40, **Theme.get_button_style("secondary"), command=lambda x=i: self.open_product_form(x)).pack(side="right", padx=2, pady=3)
            ctk.CTkButton(row, text="🗑️", width=40, **Theme.get_button_style("danger"), command=lambda x=i['id']: self.delete_product(x)).pack(side="right", padx=2, pady=3)

    def open_product_form(self, data=None):
        """Formulario para productos con proveedor obligatorio"""
        # Obtener lista de proveedores
        proveedores = self.logic.proveedores.OBTENER_TODOS_PROVEEDORES()
        if not proveedores:
            messagebox.showerror("Error", "Debe registrar al menos un proveedor antes de crear productos")
            return
        
        win = ctk.CTkToplevel(self)
        title = f"{'EDITAR' if data else 'NUEVO'} PRODUCTO"
        win.title(title)
        win.geometry("500x800")
        win.attributes("-topmost", True)
        win.configure(fg_color=Theme.BACKGROUND)
        
        # Centrar
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (250)
        y = (win.winfo_screenheight() // 2) - (400)
        win.geometry(f"500x800+{x}+{y}")
        
        # Header
        header = ctk.CTkFrame(win, fg_color=Theme.PRIMARY if not data else Theme.ACCENT, corner_radius=0)
        header.pack(fill="x")
        icon = "➕" if not data else "✏️"
        ctk.CTkLabel(header, text=f"{icon} {title}", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), text_color=Theme.WHITE).pack(pady=20)
        
        # Container
        container = ctk.CTkFrame(win, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=Theme.PADDING_LARGE, pady=Theme.PADDING_LARGE)
        
        # Variables
        v_nom = ctk.StringVar(value=data.get('nombre', '') if data else "")
        v_cat = ctk.StringVar(value=data.get('categoria', '') if data else "")
        v_cost = ctk.StringVar(value=str(int(data.get('costo', 0))) if data else "0")
        v_price = ctk.StringVar(value=str(int(data.get('precio', 0))) if data else "0")
        v_stock = ctk.StringVar(value=str(data.get('stock', 1)) if data else "1")
        
        # Proveedor - obtener ID actual si existe
        proveedor_actual_id = data.get('proveedor_id', 0) if data else 0
        proveedor_nombres = {str(p['id']): p['nombre'] for p in proveedores}
        proveedor_ids = list(proveedor_nombres.keys())
        proveedor_values = [proveedor_nombres[pid] for pid in proveedor_ids]
        
        # Seleccionar proveedor actual
        try:
            proveedor_idx = proveedor_ids.index(str(proveedor_actual_id)) if proveedor_actual_id else 0
        except ValueError:
            proveedor_idx = 0
        
        v_proveedor = ctk.StringVar(value=proveedor_values[proveedor_idx] if proveedor_values else "")
        
        v_nom.trace("w", lambda *a: v_nom.set(v_nom.get().upper()))
        v_cat.trace("w", lambda *a: v_cat.set(v_cat.get().upper()))
        
        def add_field(label, variable, is_combo=False, combo_values=None):
            frame = ctk.CTkFrame(container, **Theme.get_card_style())
            frame.pack(fill="x", pady=8)
            ctk.CTkLabel(frame, text=label, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), 
                        text_color=Theme.TEXT_PRIMARY, anchor="w").pack(fill="x", padx=15, pady=(10, 5))
            if is_combo:
                combo = ctk.CTkComboBox(frame, values=combo_values, variable=variable, height=40, 
                                       border_color=Theme.BORDER, button_color=Theme.PRIMARY, 
                                       dropdown_fg_color=Theme.SURFACE)
                combo.pack(fill="x", padx=15, pady=(0, 10))
                return combo
            else:
                ctk.CTkEntry(frame, textvariable=variable, height=40, border_color=Theme.BORDER, 
                           corner_radius=Theme.RADIUS_SMALL).pack(fill="x", padx=15, pady=(0, 10))
        
        add_field("📝 NOMBRE:", v_nom)
        
        # Categorías dinámicas
        cats = self.logic.bd.OBTENER_TODOS("SELECT nombre FROM categorias WHERE tipo = 'PRODUCTO' ORDER BY nombre", ())
        cat_list = [c[0] for c in cats] if cats else ["FUNDAS", "CARGADORES", "MICAS", "AUDIFONOS", "OTROS"]
        
        # Frame para categoría con botón de crear
        cat_frame = ctk.CTkFrame(container, **Theme.get_card_style())
        cat_frame.pack(fill="x", pady=8)
        ctk.CTkLabel(cat_frame, text="🏷️ CATEGORÍA:", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), 
                    text_color=Theme.TEXT_PRIMARY, anchor="w").pack(fill="x", padx=15, pady=(10, 5))
        cat_inner = ctk.CTkFrame(cat_frame, fg_color="transparent")
        cat_inner.pack(fill="x", padx=15, pady=(0, 10))
        
        combo_cat = ctk.CTkComboBox(cat_inner, values=cat_list, variable=v_cat, height=40, 
                                   border_color=Theme.BORDER, button_color=Theme.PRIMARY, 
                                   dropdown_fg_color=Theme.SURFACE)
        combo_cat.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def crear_categoria():
            nueva_cat = ctk.CTkInputDialog(text="Ingrese el nombre de la nueva categoría:", title="Nueva Categoría").get_input()
            if nueva_cat:
                nueva_cat = nueva_cat.strip().upper()
                if nueva_cat:
                    try:
                        self.logic.bd.EJECUTAR_CONSULTA("INSERT INTO categorias (nombre, tipo) VALUES (?, 'PRODUCTO')", (nueva_cat,))
                        # Actualizar lista
                        cats = self.logic.bd.OBTENER_TODOS("SELECT nombre FROM categorias WHERE tipo = 'PRODUCTO' ORDER BY nombre", ())
                        cat_list = [c[0] for c in cats]
                        combo_cat.configure(values=cat_list)
                        v_cat.set(nueva_cat)
                        messagebox.showinfo("Éxito", f"Categoría '{nueva_cat}' creada")
                    except:
                        messagebox.showerror("Error", "La categoría ya existe")
        
        ctk.CTkButton(cat_inner, text="➕", width=40, command=crear_categoria, 
                     **Theme.get_button_style("accent"), height=40).pack(side="left")
        add_field("💵 COSTO COMPRA ($):", v_cost)
        add_field("💲 PRECIO VENTA ($):", v_price)
        add_field("📦 STOCK:", v_stock)
        add_field("🏭 PROVEEDOR (OBLIGATORIO):", v_proveedor, True, proveedor_values)
        
        def guardar():
            try:
                n = v_nom.get().strip()
                cat = v_cat.get().strip()
                c = float(v_cost.get())
                p = float(v_price.get())
                s = int(v_stock.get())
                
                # Obtener ID del proveedor seleccionado
                proveedor_nombre = v_proveedor.get()
                proveedor_id = None
                for pid, pname in proveedor_nombres.items():
                    if pname == proveedor_nombre:
                        proveedor_id = int(pid)
                        break
                
                if not proveedor_id:
                    messagebox.showerror("Error", "Debe seleccionar un proveedor válido")
                    return
                
                if not n:
                    messagebox.showerror("Error", "El nombre es obligatorio")
                    return
                
                if data:
                    self.logic.inventory.ACTUALIZAR_PRODUCTO(data['id'], n, cat, c, p, s, proveedor_id)
                else:
                    self.logic.inventory.AGREGAR_PRODUCTO(n, c, p, s, cat, proveedor_id)
                
                win.destroy()
                self.load_products()
            except Exception as e:
                messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
        
        ctk.CTkButton(container, text="💾 GUARDAR", command=guardar, 
                     **Theme.get_button_style("success"), height=50).pack(pady=20, fill="x")

    def delete_product(self, pid):
        if messagebox.askyesno("Confirmar", "Eliminar producto?"):
            self.logic.inventory.ELIMINAR_PRODUCTO(pid)
            self.load_products()

    # --- REPUESTOS (TALLER) ---
    def load_parts(self):
        self.clear_scroll(self.tab_parts.scroll_frame)
        items = self.logic.parts.get_parts_with_provider()
        self.tab_parts.items_cache = items
        self.render_parts(items)

    def render_parts(self, items):
        self.clear_scroll(self.tab_parts.scroll_frame)
        header = ctk.CTkFrame(self.tab_parts.scroll_frame, fg_color=Theme.PRIMARY, corner_radius=Theme.RADIUS_SMALL)
        header.pack(fill="x", pady=(0, 5))
        self.make_cell(header, "NOMBRE", 180, Theme.WHITE, True)
        self.make_cell(header, "CATEGORÍA", 90, Theme.WHITE, True)
        self.make_cell(header, "PROVEEDOR", 120, Theme.WHITE, True)
        self.make_cell(header, "P. SUGERIDO", 80, Theme.WHITE, True)
        self.make_cell(header, "STOCK", 50, Theme.WHITE, True)
        for i in items:
            row = ctk.CTkFrame(self.tab_parts.scroll_frame, fg_color=Theme.SURFACE, corner_radius=Theme.RADIUS_SMALL)
            row.pack(fill="x", pady=2)
            self.make_cell(row, i['nombre'], 180)
            self.make_cell(row, i['categoria'], 90)
            
            proveedor_text = i.get('proveedor_nombre') or "SIN PROVEEDOR"
            color = Theme.TEXT_SECONDARY if i.get('proveedor_nombre') else "#999999"
            self.make_cell(row, proveedor_text, 120, color)
            self.make_cell(row, f"${int(i['precio_sugerido']):,}".replace(",", "."), 80, Theme.PRIMARY, True)
            self.make_cell(row, str(i['stock']), 50)
            ctk.CTkButton(row, text="✏️", width=40, **Theme.get_button_style("secondary"), command=lambda x=i: self.open_part_form(x)).pack(side="right", padx=2, pady=3)
            ctk.CTkButton(row, text="🗑️", width=40, **Theme.get_button_style("danger"), command=lambda x=i['id']: self.delete_part(x)).pack(side="right", padx=2, pady=3)

    def open_part_form(self, data=None):
        """Formulario para repuestos con proveedor obligatorio"""
        # Obtener lista de proveedores
        proveedores = self.logic.proveedores.OBTENER_TODOS_PROVEEDORES()
        if not proveedores:
            messagebox.showerror("Error", "Debe registrar al menos un proveedor antes de crear repuestos")
            return
        
        win = ctk.CTkToplevel(self)
        title = f"{'EDITAR' if data else 'NUEVO'} REPUESTO"
        win.title(title)
        win.geometry("500x800")
        win.attributes("-topmost", True)
        win.configure(fg_color=Theme.BACKGROUND)
        
        # Centrar
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (250)
        y = (win.winfo_screenheight() // 2) - (400)
        win.geometry(f"500x800+{x}+{y}")
        
        # Header
        header = ctk.CTkFrame(win, fg_color=Theme.PRIMARY if not data else Theme.ACCENT, corner_radius=0)
        header.pack(fill="x")
        icon = "➕" if not data else "✏️"
        ctk.CTkLabel(header, text=f"{icon} {title}", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), text_color=Theme.WHITE).pack(pady=20)
        
        # Container
        container = ctk.CTkFrame(win, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=Theme.PADDING_LARGE, pady=Theme.PADDING_LARGE)
        
        # Variables
        v_nom = ctk.StringVar(value=data.get('nombre', '') if data else "")
        v_cat = ctk.StringVar(value=data.get('categoria', '') if data else "")
        v_cost = ctk.StringVar(value=str(int(data.get('costo', 0))) if data else "0")
        v_price = ctk.StringVar(value=str(int(data.get('precio_sugerido', 0))) if data else "0")
        v_stock = ctk.StringVar(value=str(data.get('stock', 1)) if data else "1")
        
        # Proveedor
        proveedor_actual_id = data.get('proveedor_id', 0) if data else 0
        proveedor_nombres = {str(p['id']): p['nombre'] for p in proveedores}
        proveedor_ids = list(proveedor_nombres.keys())
        proveedor_values = [proveedor_nombres[pid] for pid in proveedor_ids]
        
        try:
            proveedor_idx = proveedor_ids.index(str(proveedor_actual_id)) if proveedor_actual_id else 0
        except ValueError:
            proveedor_idx = 0
        
        v_proveedor = ctk.StringVar(value=proveedor_values[proveedor_idx] if proveedor_values else "")
        
        v_nom.trace("w", lambda *a: v_nom.set(v_nom.get().upper()))
        v_cat.trace("w", lambda *a: v_cat.set(v_cat.get().upper()))
        
        def add_field(label, variable, is_combo=False, combo_values=None):
            frame = ctk.CTkFrame(container, **Theme.get_card_style())
            frame.pack(fill="x", pady=8)
            ctk.CTkLabel(frame, text=label, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), 
                        text_color=Theme.TEXT_PRIMARY, anchor="w").pack(fill="x", padx=15, pady=(10, 5))
            if is_combo:
                combo = ctk.CTkComboBox(frame, values=combo_values, variable=variable, height=40, 
                                       border_color=Theme.BORDER, button_color=Theme.PRIMARY, 
                                       dropdown_fg_color=Theme.SURFACE)
                combo.pack(fill="x", padx=15, pady=(0, 10))
                return combo
            else:
                ctk.CTkEntry(frame, textvariable=variable, height=40, border_color=Theme.BORDER, 
                           corner_radius=Theme.RADIUS_SMALL).pack(fill="x", padx=15, pady=(0, 10))
        
        add_field("📝 NOMBRE:", v_nom)
        
        # Categorías dinámicas
        cats = self.logic.bd.OBTENER_TODOS("SELECT nombre FROM categorias WHERE tipo = 'REPUESTO' ORDER BY nombre", ())
        cat_list = [c[0] for c in cats] if cats else ["PANTALLAS", "BATERIAS", "PINES CARGA", "FLEX", "OTROS"]
        
        # Frame para categoría con botón de crear
        cat_frame = ctk.CTkFrame(container, **Theme.get_card_style())
        cat_frame.pack(fill="x", pady=8)
        ctk.CTkLabel(cat_frame, text="🏷️ CATEGORÍA:", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), 
                    text_color=Theme.TEXT_PRIMARY, anchor="w").pack(fill="x", padx=15, pady=(10, 5))
        cat_inner = ctk.CTkFrame(cat_frame, fg_color="transparent")
        cat_inner.pack(fill="x", padx=15, pady=(0, 10))
        
        combo_cat = ctk.CTkComboBox(cat_inner, values=cat_list, variable=v_cat, height=40, 
                                   border_color=Theme.BORDER, button_color=Theme.PRIMARY, 
                                   dropdown_fg_color=Theme.SURFACE)
        combo_cat.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def crear_categoria():
            nueva_cat = ctk.CTkInputDialog(text="Ingrese el nombre de la nueva categoría:", title="Nueva Categoría").get_input()
            if nueva_cat:
                nueva_cat = nueva_cat.strip().upper()
                if nueva_cat:
                    try:
                        self.logic.bd.EJECUTAR_CONSULTA("INSERT INTO categorias (nombre, tipo) VALUES (?, 'REPUESTO')", (nueva_cat,))
                        # Actualizar lista
                        cats = self.logic.bd.OBTENER_TODOS("SELECT nombre FROM categorias WHERE tipo = 'REPUESTO' ORDER BY nombre", ())
                        cat_list = [c[0] for c in cats]
                        combo_cat.configure(values=cat_list)
                        v_cat.set(nueva_cat)
                        messagebox.showinfo("Éxito", f"Categoría '{nueva_cat}' creada")
                    except:
                        messagebox.showerror("Error", "La categoría ya existe")
        
        ctk.CTkButton(cat_inner, text="➕", width=40, command=crear_categoria, 
                     **Theme.get_button_style("accent"), height=40).pack(side="left")
        add_field("💵 COSTO COMPRA ($):", v_cost)
        add_field("💲 PRECIO SUGERIDO ($):", v_price)
        add_field("📦 STOCK:", v_stock)
        add_field("🏭 PROVEEDOR (OBLIGATORIO):", v_proveedor, True, proveedor_values)
        
        def guardar():
            try:
                n = v_nom.get().strip()
                cat = v_cat.get().strip()
                c = float(v_cost.get())
                p = float(v_price.get())
                s = int(v_stock.get())
                
                # Obtener ID del proveedor
                proveedor_nombre = v_proveedor.get()
                proveedor_id = None
                for pid, pname in proveedor_nombres.items():
                    if pname == proveedor_nombre:
                        proveedor_id = int(pid)
                        break
                
                if not proveedor_id:
                    messagebox.showerror("Error", "Debe seleccionar un proveedor válido")
                    return
                
                if not n:
                    messagebox.showerror("Error", "El nombre es obligatorio")
                    return
                
                if data:
                    self.logic.parts.ACTUALIZAR_REPUESTO(data['id'], n, cat, c, p, s, proveedor_id)
                else:
                    self.logic.parts.AGREGAR_REPUESTO(n, c, p, s, cat, proveedor_id)
                
                win.destroy()
                self.load_parts()
            except Exception as e:
                messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
        
        ctk.CTkButton(container, text="💾 GUARDAR", command=guardar, 
                     **Theme.get_button_style("success"), height=50).pack(pady=20, fill="x")

    def delete_part(self, pid):
        if messagebox.askyesno("Confirmar", "Eliminar repuesto?"):
            self.logic.parts.ELIMINAR_REPUESTO(pid)
            self.load_parts()

    # --- SERVICIOS ---
    def load_services(self):
        self.clear_scroll(self.tab_serv.scroll_frame)
        items = self.logic.services.get_all_services()
        self.tab_serv.items_cache = items
        self.render_services(items)

    def render_services(self, items):
        self.clear_scroll(self.tab_serv.scroll_frame)
        header = ctk.CTkFrame(self.tab_serv.scroll_frame, fg_color=Theme.PRIMARY, corner_radius=Theme.RADIUS_SMALL)
        header.pack(fill="x", pady=(0, 5))
        self.make_cell(header, "SERVICIO", 250, Theme.WHITE, True)
        self.make_cell(header, "CATEGORÍA", 100, Theme.WHITE, True)
        self.make_cell(header, "COSTO M.O.", 100, Theme.WHITE, True)
        for i in items:
            row = ctk.CTkFrame(self.tab_serv.scroll_frame, fg_color=Theme.SURFACE, corner_radius=Theme.RADIUS_SMALL)
            row.pack(fill="x", pady=2)
            self.make_cell(row, i[1], 250)
            self.make_cell(row, i[2], 100)
            self.make_cell(row, f"${int(i[3]):,}".replace(",", "."), 100, Theme.PRIMARY, True)
            ctk.CTkButton(row, text="✏️", width=40, **Theme.get_button_style("secondary"), command=lambda x=i: self.open_service_form(x)).pack(side="right", padx=2, pady=3)
            ctk.CTkButton(row, text="🗑️", width=40, **Theme.get_button_style("danger"), command=lambda x=i[0]: self.delete_service(x)).pack(side="right", padx=2, pady=3)

    def open_service_form(self, data=None):
        self.open_generic_form("SERVICIO", data, self.save_service, has_cost=False, has_stock=False)

    def save_service(self, win, data, v_nom, v_cat, v_cost, v_price, v_stock):
        try:
            n = v_nom.get()
            cat = v_cat.get()
            cost_mo = float(v_price.get())
            if data:
                self.logic.services.update_service(data[0], n, cat, cost_mo)
            else:
                self.logic.services.add_service(n, cost_mo, cat)
            win.destroy()
            self.load_services()
        except Exception as e:
            messagebox.showerror("Error", f"Datos inválidos: {str(e)}")

    def delete_service(self, sid):
        if messagebox.askyesno("Confirmar", "Eliminar servicio?"):
            self.logic.services.delete_service(sid)
            self.load_services()

    # --- UTILS ---
    def make_cell(self, parent, text, w, color=None, bold=False):
        if color is None: color = Theme.TEXT_PRIMARY
        font_weight = "bold" if bold else "normal"
        ctk.CTkLabel(parent, text=str(text), width=w, anchor="w", text_color=color, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, font_weight)).pack(side="left", padx=5, pady=6)

    def clear_scroll(self, scroll):
        for w in scroll.winfo_children():
            w.destroy()

    def filter_list(self, parent, query):
        if not hasattr(parent, "items_cache"):
            return
        filtered = [item for item in parent.items_cache if query.lower() in str(item).lower()]
        if parent == self.tab_prod:
            self.render_products(filtered)
        elif parent == self.tab_parts:
            self.render_parts(filtered)
        elif parent == self.tab_serv:
            self.render_services(filtered)

    def open_generic_form(self, type_name, data, save_cb, has_cost=True, has_stock=True):
        win = ctk.CTkToplevel(self)
        title = f"{'EDITAR' if data else 'NUEVO'} {type_name}"
        win.title(title)
        win.geometry("500x650")
        win.attributes("-topmost", True)
        win.configure(fg_color=Theme.BACKGROUND)
        # Centrar ventana
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (500 // 2)
        y = (win.winfo_screenheight() // 2) - (650 // 2)
        win.geometry(f"500x650+{x}+{y}")

        # Header
        header = ctk.CTkFrame(win, fg_color=Theme.PRIMARY if not data else Theme.ACCENT, corner_radius=0)
        header.pack(fill="x")
        icon = "➕" if not data else "✏️"
        ctk.CTkLabel(header, text=f"{icon} {'NUEVO' if not data else 'EDITAR'} {type_name}", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), text_color=Theme.WHITE).pack(pady=20)

        # Contenedor
        container = ctk.CTkFrame(win, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=Theme.PADDING_LARGE, pady=Theme.PADDING_LARGE)

        v_nom = ctk.StringVar(value=data[1] if data else "")
        v_cat = ctk.StringVar(value=data[2] if data else "")
        v_cost = ctk.StringVar(value=str(int(data[3])) if data and has_cost else "0")
        idx_price = 4 if type_name != "SERVICIO" else 3
        v_price = ctk.StringVar(value=str(int(data[idx_price])) if data else "0")
        v_stock = ctk.StringVar(value=str(data[5]) if data and has_stock else "1")

        v_nom.trace("w", lambda *a: v_nom.set(v_nom.get().upper()))
        v_cat.trace("w", lambda *a: v_cat.set(v_cat.get().upper()))

        def add_field(label, variable, is_combo=False, combo_values=None):
            frame = ctk.CTkFrame(container, **Theme.get_card_style())
            frame.pack(fill="x", pady=8)
            ctk.CTkLabel(frame, text=label, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color=Theme.TEXT_PRIMARY, anchor="w").pack(fill="x", padx=15, pady=(10, 5))
            if is_combo:
                ctk.CTkComboBox(frame, values=combo_values, variable=variable, height=40, border_color=Theme.BORDER, button_color=Theme.PRIMARY, dropdown_fg_color=Theme.SURFACE).pack(fill="x", padx=15, pady=(0, 10))
            else:
                ctk.CTkEntry(frame, textvariable=variable, height=40, border_color=Theme.BORDER, corner_radius=Theme.RADIUS_SMALL).pack(fill="x", padx=15, pady=(0, 10))

        add_field("📝 NOMBRE:", v_nom)

        cats = ["GENERAL"]
        if type_name == "PRODUCTO":
            cats = ["FUNDAS", "CARGADORES", "MICAS", "AUDIFONOS", "OTROS"]
        if type_name == "REPUESTO":
            cats = ["PANTALLAS", "BATERIAS", "PINES CARGA", "FLEX", "OTROS"]
        if type_name == "SERVICIO":
            cats = ["SOFTWARE", "HARDWARE", "MANTENIMIENTO"]
        add_field("🏷️ CATEGORÍA:", v_cat, True, cats)

        if has_cost:
            add_field("💵 COSTO COMPRA ($):", v_cost)

        lbl_p = "💲 PRECIO VENTA ($):" if type_name != "SERVICIO" else "🛠️ COSTO MANO OBRA ($):"
        add_field(lbl_p, v_price)

        if has_stock:
            add_field("📦 STOCK:", v_stock)

        ctk.CTkButton(container, text="💾 GUARDAR", command=lambda: save_cb(win, data, v_nom, v_cat, v_cost, v_price, v_stock), **Theme.get_button_style("success"), height=50).pack(pady=20, fill="x")
