import customtkinter as ctk
from tkinter import messagebox
from pdf_generator import GENERADOR_PDF
from .theme import Theme

class ReportsFrame(ctk.CTkFrame):
    def __init__(self, parent, logic, current_user):
        super().__init__(parent, fg_color=Theme.BACKGROUND)
        self.logic = logic
        self.current_user = current_user
        
        # Título Principal
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=Theme.PADDING_LARGE, padx=Theme.PADDING_LARGE)
        ctk.CTkLabel(header, text="📊 REPORTES Y ANÁLISIS", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H1, "bold"), text_color=Theme.TEXT_PRIMARY).pack()
        
        ctk.CTkFrame(self, height=2, fg_color=Theme.DIVIDER).pack(fill="x", pady=(0, Theme.PADDING_MEDIUM))
        
        self.tabview = ctk.CTkTabview(self, fg_color=Theme.SURFACE, segmented_button_fg_color=Theme.BACKGROUND_LIGHT, segmented_button_selected_color=Theme.PRIMARY, text_color=Theme.TEXT_PRIMARY, corner_radius=Theme.RADIUS_LARGE, border_width=2, border_color=Theme.BORDER)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        self.tab_tech = self.tabview.add("HISTORIAL POR TÉCNICO")
        self.tab_sales = self.tabview.add("VENTAS DIARIAS Y UTILIDAD")
        self.setup_tech_tab()
        self.setup_sales_tab()

    def refresh(self):
        self.load_sales_report()

    # --- PESTAÑA 1: TÉCNICOS ---
    def setup_tech_tab(self):
        try: from tkcalendar import DateEntry
        except: messagebox.showerror("Error", "Instale tkcalendar: pip install tkcalendar"); return

        # Panel superior con filtros
        top = ctk.CTkFrame(self.tab_tech, **Theme.get_card_style()); top.pack(fill="x", pady=Theme.PADDING_MEDIUM, padx=Theme.PADDING_MEDIUM)
        
        # Fila 1: Selector de Técnico
        row1 = ctk.CTkFrame(top, fg_color="transparent"); row1.pack(fill="x", pady=5, padx=10)
        ctk.CTkLabel(row1, text="👨‍🔧 TÉCNICO:", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color=Theme.TEXT_PRIMARY).pack(side="left", padx=5)
        techs = self.logic.get_technicians()
        self.tech_map = {t[1]: t[0] for t in techs}
        self.combo_tech = ctk.CTkComboBox(row1, values=list(self.tech_map.keys()), width=200, fg_color=Theme.SURFACE, border_color=Theme.BORDER, button_color=Theme.PRIMARY, dropdown_fg_color=Theme.SURFACE)
        self.combo_tech.pack(side="left", padx=5)

        # Fila 2: Filtros de Fecha
        row2 = ctk.CTkFrame(top, fg_color="transparent"); row2.pack(fill="x", pady=5, padx=10)
        ctk.CTkLabel(row2, text="📅 DESDE:", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color=Theme.TEXT_PRIMARY).pack(side="left", padx=5)
        self.date_from = DateEntry(row2, width=12, background=Theme.PRIMARY, foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.date_from.pack(side="left", padx=5)
        self.date_from.delete(0, "end")
        
        ctk.CTkLabel(row2, text="📅 HASTA:", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color=Theme.TEXT_PRIMARY).pack(side="left", padx=15)
        self.date_to = DateEntry(row2, width=12, background=Theme.PRIMARY, foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.date_to.pack(side="left", padx=5)
        self.date_to.delete(0, "end")

        # Botones
        ctk.CTkButton(row2, text="🔄 GENERAR", width=120, command=self.load_tech_report, **Theme.get_button_style("primary"), height=40).pack(side="left", padx=15)
        ctk.CTkButton(row2, text="🖨️ PDF (A5)", width=120, command=self.print_tech_report, **Theme.get_button_style("accent"), height=40).pack(side="left", padx=5)

        self.scroll_tech = ctk.CTkScrollableFrame(self.tab_tech, fg_color="transparent"); self.scroll_tech.pack(fill="both", expand=True, pady=10, padx=10)
        
        # Label de total
        total_frame = ctk.CTkFrame(self.tab_tech, fg_color=Theme.BACKGROUND_LIGHT, corner_radius=Theme.RADIUS_MEDIUM)
        total_frame.pack(pady=Theme.PADDING_LARGE, padx=Theme.PADDING_LARGE, fill="x")
        self.lbl_tech_total = ctk.CTkLabel(total_frame, text="TOTAL A PAGAR: $0", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), text_color=Theme.SUCCESS)
        self.lbl_tech_total.pack(pady=15)

    def load_tech_report(self):
        for w in self.scroll_tech.winfo_children(): w.destroy()
        name = self.combo_tech.get(); tid = self.tech_map.get(name)
        d_from = self.date_from.get(); d_to = self.date_to.get()
        
        if not tid: return
        data = self.logic.reports.get_tech_history(tid, d_from if d_from else None, d_to if d_to else None)
        self.current_report_data = data 
        self.current_tech_name = name
        self.current_date_range = f"{d_from} - {d_to}" if d_from and d_to else "HISTÓRICO"

        # Encabezados
        h = ctk.CTkFrame(self.scroll_tech, fg_color=Theme.PRIMARY, corner_radius=Theme.RADIUS_SMALL); h.pack(fill="x", pady=5)
        cols = [("FECHA", 90), ("EQUIPO", 180), ("TOTAL", 80), ("REP/ENV", 80), ("C.BANCO", 80), ("IVA", 80), ("COMISIÓN", 90)]
        for c, w in cols: ctk.CTkLabel(h, text=c, width=w, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"), text_color=Theme.WHITE).pack(side="left", padx=2, pady=8)
        
        # Acumuladores
        sum_total = 0; sum_costos = 0; sum_banco = 0; sum_iva = 0; sum_comision = 0

        for row in data:
            # 0:id, 1:equipo, 2:modelo, 3:fecha, 4:total, 5:rep, 6:comision, 7:debito, 8:credito, 9:iva, 10:envio
            fecha = row[3].split(" ")[0]
            equipo = f"{row[1]} {row[2]}"
            total = row[4]
            costos = row[5] + row[10]
            comision = row[6]
            
            m_tarjeta = (row[7] or 0) + (row[8] or 0)
            com_banco = m_tarjeta * 0.0295
            
            util_op = (total - com_banco - costos)
            m_iva = util_op * 0.19 if row[9] else 0
            
            sum_total += total
            sum_costos += costos
            sum_banco += com_banco
            sum_iva += m_iva
            sum_comision += comision
            
            f = ctk.CTkFrame(self.scroll_tech, fg_color=Theme.SURFACE, corner_radius=Theme.RADIUS_SMALL); f.pack(fill="x", pady=2)
            vals = [
                (fecha, 90, Theme.TEXT_PRIMARY),
                (equipo, 180, Theme.TEXT_PRIMARY),
                (f"${int(total):,}".replace(",", "."), 80, Theme.TEXT_PRIMARY),
                (f"${int(costos):,}".replace(",", "."), 80, Theme.ERROR),
                (f"${int(com_banco):,}".replace(",", "."), 80, Theme.ERROR),
                (f"${int(m_iva):,}".replace(",", "."), 80, Theme.ERROR),
                (f"${int(comision):,}".replace(",", "."), 90, Theme.SUCCESS)
            ]
            for txt, w, col in vals:
                ctk.CTkLabel(f, text=txt, width=w, text_color=col, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL)).pack(side="left", padx=2, pady=6)
        
        # FILA DE TOTALES
        ft = ctk.CTkFrame(self.scroll_tech, fg_color=Theme.BACKGROUND_LIGHT, corner_radius=Theme.RADIUS_MEDIUM); ft.pack(fill="x", pady=10)
        ctk.CTkLabel(ft, text="TOTALES:", width=270, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color=Theme.TEXT_PRIMARY, anchor="e").pack(side="left", padx=2, pady=8)
        
        t_vals = [
            (f"${int(sum_total):,}".replace(",", "."), 80),
            (f"${int(sum_costos):,}".replace(",", "."), 80),
            (f"${int(sum_banco):,}".replace(",", "."), 80),
            (f"${int(sum_iva):,}".replace(",", "."), 80),
            (f"${int(sum_comision):,}".replace(",", "."), 90)
        ]
        for txt, w in t_vals:
            ctk.CTkLabel(ft, text=txt, width=w, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, "bold"), text_color=Theme.TEXT_PRIMARY).pack(side="left", padx=2)

        self.lbl_tech_total.configure(text=f"TOTAL A PAGAR (COMISIONES): ${int(sum_comision):,}".replace(",", "."))

    def print_tech_report(self):
        if not hasattr(self, 'current_report_data') or not self.current_report_data:
            messagebox.showwarning("Aviso", "Primero genere un reporte con datos."); return
        
        try:
            pdf = GENERADOR_PDF()
            filename = f"reporte_{self.current_tech_name.replace(' ', '_')}.pdf"
            pdf.GENERAR_REPORTE_COMISIONES(filename, self.current_tech_name, self.current_date_range, self.current_report_data)
            messagebox.showinfo("Éxito", f"Reporte generado: {filename}")
            import os, platform, subprocess
            if platform.system() == 'Windows': os.startfile(filename)
            else: subprocess.call(('xdg-open', filename))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF: {e}")

    # --- PESTAÑA 2: VENTAS DIARIAS ---
    def setup_sales_tab(self):
        # Botón actualizar
        btn_frame = ctk.CTkFrame(self.tab_sales, fg_color="transparent")
        btn_frame.pack(pady=Theme.PADDING_MEDIUM)
        ctk.CTkButton(btn_frame, text="🔄 ACTUALIZAR REPORTE DE HOY", command=self.load_sales_report, **Theme.get_button_style("primary"), height=45, width=250).pack()
        
        self.scroll_sales = ctk.CTkScrollableFrame(self.tab_sales, fg_color="transparent"); self.scroll_sales.pack(fill="both", expand=True, pady=10, padx=10)
        
        # Label de total
        total_frame = ctk.CTkFrame(self.tab_sales, fg_color=Theme.PRIMARY_LIGHT, corner_radius=Theme.RADIUS_MEDIUM)
        total_frame.pack(pady=Theme.PADDING_LARGE, padx=Theme.PADDING_LARGE, fill="x")
        self.lbl_sales_total = ctk.CTkLabel(total_frame, text="VENTAS BRUTAS: $0  |  GANANCIA FINAL TIENDA: $0", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"), text_color=Theme.PRIMARY)
        self.lbl_sales_total.pack(pady=15)

    def load_sales_report(self):
        for w in self.scroll_sales.winfo_children(): w.destroy()
        data = self.logic.reports.get_daily_sales()
        
        # ENCABEZADOS
        h = ctk.CTkFrame(self.scroll_sales, fg_color=Theme.PRIMARY, corner_radius=Theme.RADIUS_SMALL); h.pack(fill="x", pady=5)
        ctk.CTkLabel(h, text="ORDEN / EQUIPO", width=250, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"), text_color=Theme.WHITE).pack(side="left", padx=2, pady=8)
        ctk.CTkLabel(h, text="TÉCNICO", width=120, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"), text_color=Theme.WHITE).pack(side="left", padx=2, pady=8)
        ctk.CTkLabel(h, text="COMISIÓN", width=100, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"), text_color=Theme.WHITE).pack(side="left", padx=2, pady=8)
        ctk.CTkLabel(h, text="COBRADO", width=100, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"), text_color=Theme.WHITE).pack(side="left", padx=2, pady=8)
        ctk.CTkLabel(h, text="GANANCIA NET", width=120, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold"), text_color=Theme.WHITE).pack(side="left", padx=2, pady=8)
        
        t_cobrado = 0; t_ganancia_neta = 0
        for row in data:
            # 1:oid, 2:equipo, 3:tecnico, 4:cobrado, 5:utilidad_op, 7:comision
            desc = f"#{row[1]} - {row[2]}"
            tec = row[3]
            cob = row[4]
            utilidad_operativa = row[5]
            comision = row[7] if row[7] else 0
            
            ganancia_tienda = utilidad_operativa - comision
            
            t_cobrado += cob
            t_ganancia_neta += ganancia_tienda
            
            f = ctk.CTkFrame(self.scroll_sales, fg_color=Theme.SURFACE, corner_radius=Theme.RADIUS_SMALL); f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=desc, width=250, text_color=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL), anchor="w").pack(side="left", padx=5, pady=6)
            ctk.CTkLabel(f, text=tec, width=120, text_color=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL)).pack(side="left", padx=2, pady=6)
            ctk.CTkLabel(f, text=f"- ${int(comision):,}".replace(",", "."), width=100, text_color=Theme.ERROR, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold")).pack(side="left", padx=2, pady=6)
            ctk.CTkLabel(f, text=f"${int(cob):,}".replace(",", "."), width=100, text_color=Theme.TEXT_PRIMARY, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold")).pack(side="left", padx=2, pady=6)
            ctk.CTkLabel(f, text=f"${int(ganancia_tienda):,}".replace(",", "."), width=120, text_color=Theme.SUCCESS, font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, "bold")).pack(side="left", padx=2, pady=6)
            
        self.lbl_sales_total.configure(text=f"VENTAS BRUTAS: ${int(t_cobrado):,}".replace(",", ".") + f"  |  GANANCIA FINAL TIENDA: ${int(t_ganancia_neta):,}".replace(",", "."))
