import os
import tkinter.filedialog as fd
import customtkinter as ctk
from importer import SmartImporter

class ImportDialog(ctk.CTkToplevel):
    """Dialog to import products from Excel or PDF files.
    Allows preview, editing, and saving to Inventory or Parts.
    """

    def __init__(self, parent, logic):
        super().__init__(parent)
        self.title("Importar Productos")
        self.geometry("700x600")
        # Centrar ventana
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"700x600+{x}+{y}")
        self.logic = logic
        self.importer = SmartImporter()
        self.selected_target = ctk.StringVar(value="inventory")  # inventory or parts
        self.parsed_items = []  # list of dicts with name, cost
        self.check_vars = []
        self.name_vars = []
        self.cost_vars = []
        # Step 1: File selection
        ctk.CTkButton(self, text="Seleccionar Archivo", command=self.select_file).pack(pady=10)
        # Target selection
        target_frame = ctk.CTkFrame(self)
        target_frame.pack(pady=5)
        ctk.CTkLabel(target_frame, text="Destino:").pack(side="left", padx=5)
        ctk.CTkRadioButton(target_frame, text="Inventario (POS)", variable=self.selected_target, value="inventory").pack(side="left", padx=5)
        ctk.CTkRadioButton(target_frame, text="Repuestos (Taller)", variable=self.selected_target, value="parts").pack(side="left", padx=5)
        # Scrollable preview area
        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, pady=10, padx=10)
        # Save button
        ctk.CTkButton(self, text="Guardar Seleccionados", command=self.save_selected).pack(pady=10)

    def select_file(self):
        file_path = fd.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls"), ("PDF files", "*.pdf")])
        if not file_path:
            return
        try:
            self.parsed_items = self.importer.load_file(file_path)
        except Exception as e:
            import tkinter.messagebox
            tkinter.messagebox.showerror(title="Error", message=str(e))
            return
        self.populate_preview()

    def populate_preview(self):
        # Clear previous widgets
        for w in self.scroll.winfo_children():
            w.destroy()
        self.check_vars.clear()
        self.name_vars.clear()
        self.cost_vars.clear()
        # Header
        header = ctk.CTkFrame(self.scroll)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="Incluir", width=60).pack(side="left")
        ctk.CTkLabel(header, text="Nombre", width=250).pack(side="left")
        ctk.CTkLabel(header, text="Costo", width=100).pack(side="left")
        # Rows
        for item in self.parsed_items:
            row = ctk.CTkFrame(self.scroll)
            row.pack(fill="x", pady=2)
            var_chk = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(row, variable=var_chk).pack(side="left", padx=5)
            var_name = ctk.StringVar(value=item.get("name", ""))
            ctk.CTkEntry(row, textvariable=var_name, width=250).pack(side="left", padx=5)
            var_cost = ctk.StringVar(value=str(item.get("cost", 0)))
            ctk.CTkEntry(row, textvariable=var_cost, width=100).pack(side="left", padx=5)
            self.check_vars.append(var_chk)
            self.name_vars.append(var_name)
            self.cost_vars.append(var_cost)

    def save_selected(self):
        target = self.selected_target.get()
        for include, name_var, cost_var in zip(self.check_vars, self.name_vars, self.cost_vars):
            if not include.get():
                continue
            name = name_var.get().strip().upper()
            try:
                cost = float(cost_var.get())
            except ValueError:
                continue
            # Use default values for other fields
            if target == "inventory":
                # add_product(name, cost, price, stock, category)
                # price = cost * 1.5 as a simple default, stock = 0, category = "GENERAL"
                price = round(cost * 1.5, 2)
                self.logic.inventory.add_product(name, cost, price, 0, "GENERAL")
            else:
                # add_part(name, cost, suggested_price, stock, category)
                suggested = round(cost * 1.5, 2)
                self.logic.parts.add_part(name, cost, suggested, 0, "GENERAL")
        self.destroy()
