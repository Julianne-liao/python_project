import pandas as pd
import tkinter as tk
from tkinter import ttk

# 讀取 CSV（UTF-8 BOM），第一列作為欄位名稱
df = pd.read_csv('各鄉鎮市區人口密度.csv', encoding='utf-8-sig')

# 刪除第一筆中文標題列與最後非資料列
df = df.iloc[1:-6].copy()

# 僅保留所需欄位並重新命名為中文
df = df[['site_id', 'people_total', 'area']].rename(
    columns={'site_id': '區域別', 'people_total': '人口數', 'area': '土地面積'}
)

# 轉換數值型態，移除空值
df['人口數'] = pd.to_numeric(df['人口數'], errors='coerce')
df['土地面積'] = pd.to_numeric(df['土地面積'], errors='coerce')
df = df.dropna()

# 新增人口密度欄位
df['人口密度'] = (df['人口數'] / df['土地面積']).round(2)
df['人口數'] = df['人口數'].astype(int)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title('台灣鄉鎮市區人口密度查詢系統')
        self.root.geometry('900x600')

        # 上方控制區
        control = ttk.Frame(root)
        control.pack(pady=10)

        ttk.Label(control, text='輸入區域名稱：').pack(side=tk.LEFT)
        self.entry = ttk.Entry(control, width=30)
        self.entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(control, text='查詢', command=self.query).pack(side=tk.LEFT)

        # 表格區
        frame = ttk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('區域別', '人口數', '土地面積', '人口密度')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings')

        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.CENTER)
            self.tree.column(col, width=180, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_data(df)

    def load_data(self, data):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for _, r in data.iterrows():
            self.tree.insert('', tk.END, values=(
                r['區域別'], r['人口數'], r['土地面積'], r['人口密度']
            ))

    def query(self):
        keyword = self.entry.get().strip()
        if keyword:
            filtered = df[df['區域別'].str.contains(keyword, na=False)]
        else:
            filtered = df
        self.load_data(filtered)

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
