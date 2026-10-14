import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os

class KasirApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Kasir Penjualan & Pembelian")
        self.root.geometry("1000x650")
        
        self.init_db()
        self.cart = []
        
        # Header Utama (Perbaikan: 'py=10' diubah menjadi 'pady=10')
        header_frame = tk.Frame(self.root, bg="#1e293b", pady=10)
        header_frame.pack(fill=tk.X)
        tk.Label(
            header_frame, 
            text="SISTEM KASIR POS & INVENTORY", 
            font=("Arial", 16, "bold"), 
            fg="white", 
            bg="#1e293b"
        ).pack()

        # Tab Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Inisialisasi Tab
        self.tab_penjualan = ttk.Frame(self.notebook)
        self.tab_pembelian = ttk.Frame(self.notebook)
        self.tab_stok = ttk.Frame(self.notebook)
        self.tab_riwayat = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_penjualan, text=" Penjualan (Stok Keluar) ")
        self.notebook.add(self.tab_pembelian, text=" Pembelian (Stok Masuk) ")
        self.notebook.add(self.tab_stok, text=" Master Stok Barang ")
        self.notebook.add(self.tab_riwayat, text=" Riwayat Transaksi ")

        self.setup_tab_penjualan()
        self.setup_tab_pembelian()
        self.setup_tab_stok()
        self.setup_tab_riwayat()

    def init_db(self):
        self.conn = sqlite3.connect("kasir_database.db")
        self.cursor = self.conn.cursor()
        
        # Tabel Barang
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS barang (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                harga_beli REAL DEFAULT 0,
                harga_jual REAL DEFAULT 0,
                stok INTEGER DEFAULT 0
            )
        ''')
        
        # Tabel Riwayat Transaksi
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaksi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                no_order TEXT NOT NULL,
                jenis TEXT NOT NULL,
                tanggal TEXT NOT NULL,
                detail TEXT NOT NULL,
                total REAL NOT NULL,
                bayar REAL DEFAULT 0,
                kembali REAL DEFAULT 0
            )
        ''')
        self.conn.commit()

    # ================= TAB PENJUALAN =================
    def setup_tab_penjualan(self):
        left_frame = tk.Frame(self.tab_penjualan)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_frame = tk.Frame(self.tab_penjualan, width=380)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        # Form Input Item
        input_frame = tk.LabelFrame(left_frame, text="Pilih Barang", padx=10, pady=10)
        input_frame.pack(fill=tk.X, pady=5)

        tk.Label(input_frame, text="Barang:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.cb_barang_jual = ttk.Combobox(input_frame, state="readonly", width=30)
        self.cb_barang_jual.grid(row=0, column=1, pady=2)

        tk.Label(input_frame, text="Catatan/Topping:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entry_topping = tk.Entry(input_frame, width=32)
        self.entry_topping.grid(row=1, column=1, pady=2)

        tk.Label(input_frame, text="Jumlah (Qty):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entry_qty_jual = tk.Entry(input_frame, width=32)
        self.entry_qty_jual.grid(row=2, column=1, pady=2)
        self.entry_qty_jual.insert(0, "1")

        btn_add = tk.Button(input_frame, text="Tambah ke Keranjang", bg="#0284c7", fg="white", command=self.add_to_cart)
        btn_add.grid(row=3, column=0, columnspan=2, pady=8, sticky=tk.EW)

        # Tabel Keranjang
        self.tree_cart = ttk.Treeview(left_frame, columns=("Nama", "Topping", "Harga", "Qty", "Subtotal"), show="headings", height=12)
        self.tree_cart.heading("Nama", text="Nama Barang")
        self.tree_cart.heading("Topping", text="Topping/Opsi")
        self.tree_cart.heading("Harga", text="Harga")
        self.tree_cart.heading("Qty", text="Qty")
        self.tree_cart.heading("Subtotal", text="Subtotal")
        self.tree_cart.column("Qty", width=50, anchor=tk.CENTER)
        self.tree_cart.pack(fill=tk.BOTH, expand=True, pady=5)

        # Detail Pembayaran & Preview Struk
        tk.Label(right_frame, text="Preview Struk", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        self.txt_struk = tk.Text(right_frame, width=42, font=("Courier", 9))
        self.txt_struk.pack(fill=tk.BOTH, expand=True, pady=5)

        pay_frame = tk.Frame(right_frame)
        pay_frame.pack(fill=tk.X, pady=5)

        tk.Label(pay_frame, text="Bayar (Rp):").grid(row=0, column=0, sticky=tk.W)
        self.entry_bayar = tk.Entry(pay_frame, width=15)
        self.entry_bayar.grid(row=0, column=1, padx=5)

        btn_proses = tk.Button(pay_frame, text="Proses & Cetak Struk", bg="#16a34a", fg="white", font=("Arial", 9, "bold"), command=self.proses_penjualan)
        btn_proses.grid(row=0, column=2, padx=5)

        self.refresh_combobox_barang()

    def refresh_combobox_barang(self):
        self.cursor.execute("SELECT id, nama, harga_jual, harga_beli, stok FROM barang")
        self.data_barang = self.cursor.fetchall()
        
        items = [f"{b[0]} - {b[1]} (Stok: {b[4]} | Rp{b[2]:,.0f})" for b in self.data_barang]
        self.cb_barang_jual['values'] = items
        if items:
            self.cb_barang_jual.current(0)

    def add_to_cart(self):
        sel_idx = self.cb_barang_jual.current()
        if sel_idx < 0:
            messagebox.showwarning("Peringatan", "Pilih barang terlebih dahulu.")
            return

        item_data = self.data_barang[sel_idx]
        b_id, nama, hg_jual, _, stok = item_data
        
        try:
            qty = int(self.entry_qty_jual.get())
            if qty <= 0 or qty > stok:
                messagebox.showerror("Gagal", "Jumlah melebihi stok yang tersedia.")
                return
        except ValueError:
            messagebox.showerror("Gagal", "Jumlah Qty harus berupa angka.")
            return

        topping = self.entry_topping.get().strip()
        subtotal = hg_jual * qty

        self.cart.append({
            "id": b_id,
            "nama": nama,
            "topping": topping,
            "harga": hg_jual,
            "qty": qty,
            "subtotal": subtotal
        })

        self.tree_cart.insert("", tk.END, values=(nama, topping, f"{hg_jual:,.0f}", qty, f"{subtotal:,.0f}"))
        self.entry_topping.delete(0, tk.END)
        self.entry_qty_jual.delete(0, tk.END)
        self.entry_qty_jual.insert(0, "1")
        self.update_struk_preview()

    def update_struk_preview(self, bayar=0, kembali=0):
        now = datetime.now()
        order_num = f"TO{now.strftime('%Y%m%d%H%M%S')}"
        
        subtotal_val = sum(x['subtotal'] for x in self.cart)
        tax = round(subtotal_val * 0.1)
        total = subtotal_val + tax

        struk_text = f"{'TOMORO COFFEE':^36}\n"
        struk_text += f"{'Sekartaji Kediri':^36}\n"
        struk_text += f"{'2260':^36}\n"
        struk_text += f"{'DI':^36}\n"
        struk_text += "=" * 36 + "\n"
        struk_text += f"Date:         {now.strftime('%d/%b/%Y %H:%M')}\n"
        struk_text += f"Channel:      SEL-POS\n"
        struk_text += f"Order Number: {order_num}\n"
        struk_text += "-" * 36 + "\n"

        for item in self.cart:
            struk_text += f"{item['nama'][:36]}\n"
            if item['topping']:
                struk_text += f"  +{item['topping']}\n"
            struk_text += f"  {item['harga']:>8,.0f} {item['qty']:>10} {item['subtotal']:>13,.0f}\n"

        struk_text += "-" * 36 + "\n"
        struk_text += f"SUBTOTAL: {subtotal_val:>26,.0f}\n"
        struk_text += f"Tax: {tax:>31,.0f}\n"
        struk_text += f"ROUNDING: {0:>26}\n"
        struk_text += f"TOTAL: {total:>29,.0f}\n"
        struk_text += "-" * 36 + "\n"
        struk_text += f"Cash: {bayar:>30,.0f}\n"
        struk_text += f"CHANGE: {kembali:>28,.0f}\n"
        struk_text += "=" * 36 + "\n"
        struk_text += f"{'All price are inclusive Tax':^36}\n\n"
        struk_text += f"{'[ QR CODE PLACEHOLDER ]':^36}\n"

        self.txt_struk.delete("1.0", tk.END)
        self.txt_struk.insert(tk.END, struk_text)
        return total, order_num, struk_text

    def proses_penjualan(self):
        if not self.cart:
            messagebox.showwarning("Peringatan", "Keranjang belanja masih kosong.")
            return

        try:
            bayar = float(self.entry_bayar.get())
        except ValueError:
            messagebox.showerror("Gagal", "Nominal bayar harus berupa angka.")
            return

        total, order_num, struk_text = self.update_struk_preview()

        if bayar < total:
            messagebox.showerror("Gagal", "Jumlah pembayaran kurang dari total tagihan.")
            return

        kembali = bayar - total
        self.update_struk_preview(bayar, kembali)

        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        detail_items = []
        
        for item in self.cart:
            self.cursor.execute("UPDATE barang SET stok = stok - ? WHERE id = ?", (item['qty'], item['id']))
            detail_items.append(f"{item['nama']} x{item['qty']}")

        detail_str = ", ".join(detail_items)
        self.cursor.execute(
            "INSERT INTO transaksi (no_order, jenis, tanggal, detail, total, bayar, kembali) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (order_num, "Penjualan (Keluar)", now_str, detail_str, total, bayar, kembali)
        )
        self.conn.commit()

        if not os.path.exists("struk"):
            os.makedirs("struk")
        with open(f"struk/{order_num}.txt", "w") as f:
            f.write(struk_text)

        messagebox.showinfo("Sukses", f"Transaksi berhasil dicatat!\nFile Struk tersimpan di struk/{order_num}.txt")
        
        self.cart.clear()
        for i in self.tree_cart.get_children():
            self.tree_cart.delete(i)
        self.entry_bayar.delete(0, tk.END)
        self.refresh_combobox_barang()
        self.load_stok_data()
        self.load_riwayat_data()

    # ================= TAB PEMBELIAN (BARANG MASUK) =================
    def setup_tab_pembelian(self):
        frame = tk.LabelFrame(self.tab_pembelian, text="Pencatatan Stok Masuk / Pembelian", padx=15, pady=15)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(frame, text="Pilih Barang:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.cb_barang_beli = ttk.Combobox(frame, state="readonly", width=35)
        self.cb_barang_beli.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Jumlah Tambah Stok:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_qty_beli = tk.Entry(frame, width=37)
        self.entry_qty_beli.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Total Biaya Pembelian (Rp):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_total_beli = tk.Entry(frame, width=37)
        self.entry_total_beli.grid(row=2, column=1, pady=5)

        btn_simpan_pembelian = tk.Button(frame, text="Simpan Pembelian (Stok Masuk)", bg="#2563eb", fg="white", font=("Arial", 10, "bold"), command=self.proses_pembelian)
        btn_simpan_pembelian.grid(row=3, column=0, columnspan=2, pady=15, sticky=tk.EW)

    def proses_pembelian(self):
        sel_idx = self.cb_barang_beli.current()
        if sel_idx < 0:
            messagebox.showwarning("Peringatan", "Pilih barang terlebih dahulu.")
            return

        item_data = self.data_barang[sel_idx]
        b_id, nama, _, _, _ = item_data

        try:
            qty = int(self.entry_qty_beli.get())
            total_biaya = float(self.entry_total_beli.get())
            if qty <= 0 or total_biaya < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Gagal", "Jumlah stok dan total biaya harus berupa angka positif.")
            return

        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        order_num = f"IN{datetime.now().strftime('%Y%m%d%H%M%S')}"

        self.cursor.execute("UPDATE barang SET stok = stok + ? WHERE id = ?", (qty, b_id))
        self.cursor.execute(
            "INSERT INTO transaksi (no_order, jenis, tanggal, detail, total, bayar, kembali) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (order_num, "Pembelian (Masuk)", now_str, f"{nama} (+{qty})", total_biaya, total_biaya, 0)
        )
        self.conn.commit()

        messagebox.showinfo("Sukses", f"Stok barang '{nama}' berhasil ditambah {qty} unit.")
        self.entry_qty_beli.delete(0, tk.END)
        self.entry_total_beli.delete(0, tk.END)
        self.refresh_combobox_barang()
        self.load_stok_data()
        self.load_riwayat_data()

    # ================= TAB MASTER STOK =================
    def setup_tab_stok(self):
        input_frame = tk.LabelFrame(self.tab_stok, text="Tambah Barang Baru", padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(input_frame, text="Nama Barang:").grid(row=0, column=0, sticky=tk.W)
        self.entry_nama_b = tk.Entry(input_frame, width=20)
        self.entry_nama_b.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Harga Beli:").grid(row=0, column=2, sticky=tk.W)
        self.entry_hbeli_b = tk.Entry(input_frame, width=15)
        self.entry_hbeli_b.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="Harga Jual:").grid(row=0, column=4, sticky=tk.W)
        self.entry_hjual_b = tk.Entry(input_frame, width=15)
        self.entry_hjual_b.grid(row=0, column=5, padx=5)

        tk.Label(input_frame, text="Stok Awal:").grid(row=0, column=6, sticky=tk.W)
        self.entry_stok_b = tk.Entry(input_frame, width=10)
        self.entry_stok_b.grid(row=0, column=7, padx=5)

        btn_tambah = tk.Button(input_frame, text="Tambah", bg="#16a34a", fg="white", command=self.tambah_master_barang)
        btn_tambah.grid(row=0, column=8, padx=10)

        self.tree_stok = ttk.Treeview(self.tab_stok, columns=("ID", "Nama", "Harga Beli", "Harga Jual", "Stok"), show="headings")
        self.tree_stok.heading("ID", text="ID")
        self.tree_stok.heading("Nama", text="Nama Barang")
        self.tree_stok.heading("Harga Beli", text="Harga Beli")
        self.tree_stok.heading("Harga Jual", text="Harga Jual")
        self.tree_stok.heading("Stok", text="Stok Tersedia")
        self.tree_stok.column("ID", width=50, anchor=tk.CENTER)
        self.tree_stok.column("Stok", width=100, anchor=tk.CENTER)
        self.tree_stok.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.load_stok_data()

    def tambah_master_barang(self):
        nama = self.entry_nama_b.get().strip()
        try:
            hbeli = float(self.entry_hbeli_b.get())
            hjual = float(self.entry_hjual_b.get())
            stok = int(self.entry_stok_b.get())
            if not nama:
                raise ValueError
        except ValueError:
            messagebox.showerror("Gagal", "Pastikan semua input data barang diisi dengan benar.")
            return

        self.cursor.execute("INSERT INTO barang (nama, harga_beli, harga_jual, stok) VALUES (?, ?, ?, ?)", (nama, hbeli, hjual, stok))
        self.conn.commit()

        self.entry_nama_b.delete(0, tk.END)
        self.entry_hbeli_b.delete(0, tk.END)
        self.entry_hjual_b.delete(0, tk.END)
        self.entry_stok_b.delete(0, tk.END)

        self.load_stok_data()
        self.refresh_combobox_barang()
        messagebox.showinfo("Sukses", "Barang baru berhasil ditambahkan.")

    def load_stok_data(self):
        for i in self.tree_stok.get_children():
            self.tree_stok.delete(i)
        self.cursor.execute("SELECT id, nama, harga_beli, harga_jual, stok FROM barang")
        for row in self.cursor.fetchall():
            self.tree_stok.insert("", tk.END, values=(row[0], row[1], f"Rp{row[2]:,.0f}", f"Rp{row[3]:,.0f}", row[4]))

    # ================= TAB RIWAYAT TRANSAKSI =================
    def setup_tab_riwayat(self):
        self.tree_riwayat = ttk.Treeview(self.tab_riwayat, columns=("No Order", "Jenis", "Tanggal", "Detail Barang", "Total"), show="headings")
        self.tree_riwayat.heading("No Order", text="No Order")
        self.tree_riwayat.heading("Jenis", text="Jenis Transaksi")
        self.tree_riwayat.heading("Tanggal", text="Tanggal")
        self.tree_riwayat.heading("Detail Barang", text="Detail Barang")
        self.tree_riwayat.heading("Total", text="Total Nilai")
        self.tree_riwayat.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.load_riwayat_data()

    def load_riwayat_data(self):
        for i in self.tree_riwayat.get_children():
            self.tree_riwayat.delete(i)
        self.cursor.execute("SELECT no_order, jenis, tanggal, detail, total FROM transaksi ORDER BY id DESC")
        for row in self.cursor.fetchall():
            self.tree_riwayat.insert("", tk.END, values=(row[0], row[1], row[2], row[3], f"Rp{row[4]:,.0f}"))

if __name__ == "__main__":
    root = tk.Tk()
    app = KasirApp(root)
    root.mainloop()