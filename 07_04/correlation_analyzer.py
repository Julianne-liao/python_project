import sys
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]
plt.rcParams["axes.unicode_minus"] = False
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QMessageBox, QHeaderView, QFrame, QSizePolicy,
    QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QBrush, QFont, QPalette
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


STOCKS = {
    "台積電": "2330.TW",
    "聯電": "2303.TW",
    "聯發科": "2454.TW",
    "鴻海": "2317.TW",
    "台達電": "2308.TW",
    "中華電": "2412.TW",
    "國泰金": "2882.TW",
    "富邦金": "2881.TW",
    "中信金": "2891.TW",
    "兆豐金": "2886.TW",
    "日月光投控": "3711.TW",
    "廣達": "2382.TW",
    "華碩": "2357.TW",
    "中鋼": "2002.TW",
    "台塑": "1301.TW",
    "南亞": "1303.TW",
    "統一": "1216.TW",
    "台灣大": "3045.TW",
}

STOCK_KEYS = sorted(STOCKS.keys(), key=lambda x: (STOCKS[x], x))


class AnalysisThread(QThread):
    finished = Signal(object, object, object)
    error = Signal(str)

    def __init__(self, selected_tickers):
        super().__init__()
        self.selected_tickers = selected_tickers

    def run(self):
        try:
            tickers = [STOCKS[t] for t in self.selected_tickers]
            data = yf.download(tickers, start="2026-01-01", interval="1d", auto_adjust=True, progress=False)
            if data.empty:
                self.error.emit("無法取得股價資料，請檢查網路連線或股票代碼。")
                return
            close = data["Close"]
            if isinstance(close, pd.Series):
                close = close.to_frame()
            close = close.rename(columns={STOCKS[t]: t for t in self.selected_tickers})
            returns = close.pct_change().dropna()
            corr = returns.corr()
            self.finished.emit(close, returns, corr)
        except Exception as e:
            self.error.emit(f"分析時發生錯誤：{str(e)}")


class CorrelationAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("台股相關係數分析工具")
        self.setMinimumSize(1000, 750)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title = QLabel("台股相關係數分析工具")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; padding: 10px;")
        main_layout.addWidget(title)

        subtitle = QLabel("選擇最多四檔台灣股票，分析其日報酬率相關係數")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #7f8c8d; margin-bottom: 5px;")
        main_layout.addWidget(subtitle)

        group = QGroupBox("股票選擇")
        group.setStyleSheet("""
            QGroupBox { font-size: 14px; font-weight: bold; color: #2c3e50;
                         border: 2px solid #bdc3c7; border-radius: 8px;
                         margin-top: 10px; padding-top: 15px; }
            QGroupBox::title { subcontrol-origin: margin;
                                subcontrol-position: top left; padding: 0 8px; }
        """)
        grid = QGridLayout(group)
        grid.setSpacing(12)

        self.combos = []
        labels = ["第一檔", "第二檔", "第三檔", "第四檔"]
        for i in range(4):
            lbl = QLabel(labels[i])
            lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #34495e;")
            combo = QComboBox()
            combo.addItem("-- 請選擇 --", None)
            for name in STOCK_KEYS:
                display = f"{name} ({STOCKS[name]})"
                combo.addItem(display, name)
            combo.setStyleSheet("""
                QComboBox { padding: 6px 10px; font-size: 13px;
                            border: 1px solid #bdc3c7; border-radius: 5px;
                            background: white; min-width: 200px; }
                QComboBox:hover { border-color: #3498db; }
                QComboBox::drop-down { border: none; width: 30px; }
            """)
            self.combos.append(combo)
            grid.addWidget(lbl, i, 0, Qt.AlignLeft)
            grid.addWidget(combo, i, 1, Qt.AlignLeft)

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 5, 0, 5)
        main_layout.addWidget(group)
        main_layout.addLayout(btn_layout)

        self.analyze_btn = QPushButton("執行分析")
        self.analyze_btn.setMinimumSize(200, 50)
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px; font-weight: bold; color: white;
                background-color: #2980b9; border-radius: 8px;
                padding: 10px 30px;
            }
            QPushButton:hover { background-color: #3498db; }
            QPushButton:pressed { background-color: #1f618d; }
            QPushButton:disabled { background-color: #95a5a6; }
        """)
        self.analyze_btn.clicked.connect(self.run_analysis)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 13px; color: #e74c3c;")

        btn_layout.addStretch()
        btn_layout.addWidget(self.analyze_btn)
        btn_layout.addStretch()
        main_layout.addWidget(self.status_label)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #bdc3c7; border-radius: 5px;
                               background: white; padding: 5px; }
            QTabBar::tab { font-size: 13px; padding: 8px 20px;
                           border: 1px solid #bdc3c7; border-bottom: none;
                           border-top-left-radius: 5px; border-top-right-radius: 5px;
                           margin-right: 2px; background: #ecf0f1; }
            QTabBar::tab:selected { background: white; font-weight: bold; }
        """)
        self.tabs.setVisible(False)
        main_layout.addWidget(self.tabs)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget { background-color: #f5f6fa; font-family: "Microsoft JhengHei", "Segoe UI", sans-serif; }
        """)

    def run_analysis(self):
        selected = []
        for combo in self.combos:
            name = combo.currentData()
            if name is not None:
                if name in selected:
                    QMessageBox.warning(self, "重複選擇", f"「{name}」已被選取，請選擇不同的股票。")
                    return
                selected.append(name)

        if len(selected) < 1:
            QMessageBox.warning(self, "選擇不足", "請至少選擇一檔股票。")
            return

        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText("分析中...")
        self.status_label.setText("正在下載資料，請稍候...")
        self.tabs.setVisible(False)

        self.thread = AnalysisThread(selected)
        self.thread.finished.connect(self.on_analysis_done)
        self.thread.error.connect(self.on_analysis_error)
        self.thread.start()

    def on_analysis_done(self, close, returns, corr):
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("執行分析")
        self.status_label.setText("")
        self.show_results(close, returns, corr)

    def on_analysis_error(self, msg):
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("執行分析")
        self.status_label.setText(msg)

    def show_results(self, close, returns, corr):
        while self.tabs.count():
            self.tabs.removeTab(0)

        close_tab = self.build_table_tab(close, "收盤價", "#2ecc71")
        self.tabs.addTab(close_tab, "收盤價")

        corr_tab = self.build_corr_tab(corr)
        self.tabs.addTab(corr_tab, "相關係數")

        heatmap_tab = self.build_heatmap_tab(corr)
        self.tabs.addTab(heatmap_tab, "熱力圖")

        self.tabs.setVisible(True)

    def build_table_tab(self, df, title, color):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)

        header = QLabel(f"📊 {title}（最新 20 筆）")
        header.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {color}; padding: 5px;")
        layout.addWidget(header)

        table = QTableWidget()
        rows = min(len(df), 20)
        cols = len(df.columns)
        table.setRowCount(rows)
        table.setColumnCount(cols)
        table.setHorizontalHeaderLabels(list(df.columns))
        table.setAlternatingRowColors(True)

        values = df.values[-rows:]
        dates = df.index[-rows:]

        for r in range(rows):
            for c in range(cols):
                val = values[r, c]
                item = QTableWidgetItem(f"{val:.2f}" if not pd.isna(val) else "N/A")
                item.setTextAlignment(Qt.AlignCenter)
                item.setFont(QFont("Microsoft JhengHei", 10))
                table.setItem(r, c, item)

        table.setVerticalHeaderLabels([str(d.date()) for d in dates])
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setStyleSheet("""
            QTableWidget { border: 1px solid #ddd; border-radius: 4px; font-size: 12px; }
            QTableWidget::item { padding: 4px; }
            QHeaderView::section { background: #34495e; color: white; font-weight: bold;
                                   padding: 6px; border: 1px solid #2c3e50; }
        """)

        layout.addWidget(table)
        return tab

    def build_corr_tab(self, corr):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)

        header = QLabel("📈 日報酬率相關係數矩陣")
        header.setStyleSheet("font-size: 15px; font-weight: bold; color: #e67e22; padding: 5px;")
        layout.addWidget(header)

        table = QTableWidget()
        n = len(corr)
        table.setRowCount(n)
        table.setColumnCount(n + 1)
        headers = [""] + list(corr.columns)
        table.setHorizontalHeaderLabels(headers)
        table.setVerticalHeaderLabels(list(corr.index))
        table.setAlternatingRowColors(True)

        colors = {
            1.0: QColor(52, 152, 219, 200),
            0.9: QColor(46, 204, 113, 200),
            0.8: QColor(46, 204, 113, 160),
            0.7: QColor(46, 204, 113, 120),
            0.6: QColor(241, 196, 15, 120),
            0.5: QColor(241, 196, 15, 90),
            0.0: QColor(255, 255, 255, 50),
        }

        for r in range(n):
            for c in range(n):
                val = corr.iloc[r, c]
                item = QTableWidgetItem(f"{val:.4f}")
                item.setTextAlignment(Qt.AlignCenter)
                item.setFont(QFont("Microsoft JhengHei", 10))
                color = colors[1.0]
                abs_val = abs(val)
                if abs_val >= 0.95:
                    color = QColor(46, 204, 113, 200)
                elif abs_val >= 0.8:
                    color = QColor(46, 204, 113, 150)
                elif abs_val >= 0.6:
                    color = QColor(241, 196, 15, 150)
                elif abs_val >= 0.4:
                    color = QColor(241, 196, 15, 100)
                elif abs_val >= 0.2:
                    color = QColor(231, 76, 60, 100)
                else:
                    color = QColor(231, 76, 60, 150)
                if val >= 0.9:
                    color = QColor(39, 174, 96, 200)
                elif val >= 0.7:
                    color = QColor(46, 204, 113, 150)
                elif val >= 0.5:
                    color = QColor(241, 196, 15, 150)
                elif val >= 0.3:
                    color = QColor(230, 126, 34, 130)
                else:
                    color = QColor(231, 76, 60, 130)
                if r == c:
                    color = QColor(52, 152, 219, 200)
                item.setBackground(color)
                text_color = QColor(255, 255, 255) if val >= 0.5 or val < -0.5 or r == c else QColor(44, 62, 80)
                if val == 1.0 or r == c:
                    text_color = QColor(255, 255, 255)
                elif abs(val) < 0.3:
                    text_color = QColor(44, 62, 80)
                item.setForeground(text_color)
                table.setItem(r, c + 1, item)

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setDefaultSectionSize(36)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setStyleSheet("""
            QTableWidget { border: 1px solid #ddd; border-radius: 4px; font-size: 12px; }
            QTableWidget::item { padding: 4px; }
            QHeaderView::section { background: #34495e; color: white; font-weight: bold;
                                   padding: 6px; border: 1px solid #2c3e50; }
        """)

        layout.addWidget(table)

        info = QLabel("🔵 深藍 = 自身相關 | 🟢 綠 = 高度正相關 | 🟡 黃 = 中度相關 | 🔴 紅 = 低度相關")
        info.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 5px;")
        layout.addWidget(info)

        return tab

    def build_heatmap_tab(self, corr):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)

        header = QLabel("🗺️ 相關性熱力圖")
        header.setStyleSheet("font-size: 15px; font-weight: bold; color: #9b59b6; padding: 5px;")
        layout.addWidget(header)

        fig = Figure(figsize=(6, 5), dpi=100)
        fig.patch.set_facecolor("#f5f6fa")
        canvas = FigureCanvasQTAgg(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        ax = fig.add_subplot(111)
        labels = corr.columns.tolist()
        n = len(labels)
        matrix = corr.values

        im = ax.imshow(matrix, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")

        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels(labels, fontsize=10, rotation=45, ha="right")
        ax.set_yticklabels(labels, fontsize=10)

        for i in range(n):
            for j in range(n):
                val = matrix[i, j]
                color = "white" if abs(val) > 0.5 else "black"
                ax.text(j, i, f"{val:.3f}", ha="center", va="center",
                        fontsize=9, color=color, fontweight="bold")

        fig.colorbar(im, ax=ax, shrink=0.8, label="相關係數")
        fig.tight_layout()

        layout.addWidget(canvas)
        return tab


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = CorrelationAnalyzer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
