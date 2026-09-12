import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import io

# 🎨 注入現代化美化 CSS 樣式
st.markdown("""
    <style>
    /* 全局樣式微調 */
    .main {
        background-color: #f8fafc;
    }
    /* 卡片容器設計 */
    .stCard {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    /* 按鈕美化 */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        border: none;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
    }
    /* 側邊欄背景優化 */
    [data-testid="stSidebar"] {
        background-color: #f1f5f9;
        border-right: 1px solid #e2e8f0;
    }
    /* 標題與文字精緻化 */
    h1, h2, h3 {
        letter-spacing: -0.025em;
        color: #1e293b;
    }
    </style>
""", unsafe_allow_html=True)

# 🌐 多國語言字典
TRANSLATIONS = {
    "繁體中文": {
        "title": "💡 AI 智慧財務與全球記帳系統",
        "subtitle": "輕鬆管理多幣種資產、專案成本與自動化對帳",
        "menu": "功能選單",
        "menu_items": ["快速記帳", "截圖記帳 (AI 圖片辨識)", "AI 智慧文字記帳", "自動化對帳單/發票匯入", "專案 ROI 與工時成本", "合夥人分潤結算", "財務健康評分儀表板", "固定訂閱管理", "設定每月預算"],
        "base_curr_title": "💱 結算基準幣種",
        "lang_title": "🌐 介面語言選擇",
        "quick_entry": "快速新增記帳",
        "statement_import": "📥 自動化對帳單批次匯入",
        "statement_desc": "上傳各銀行、信用卡或行動支付（如 PayPal, Stripe）匯出的 CSV 對帳單檔案，系統將自動批量解析。",
        "upload_csv": "選擇對帳單 CSV / TXT 檔案",
        "preview_import": "對帳單資料預覽與確認",
        "import_success": "成功批次匯入對帳單資料！",
        "date": "日期",
        "type": "類型",
        "expense": "支出",
        "income": "收入",
        "account": "資金帳戶",
        "project": "專案歸屬",
        "category": "分類",
        "currency": "幣種",
        "orig_amount": "原始金額",
        "exchange_rate": "對匯率",
        "doc_status": "單據狀態",
        "tax_amount": "估算稅額",
        "payment_status": "收付狀態",
        "note": "備註說明",
        "submit": "確認並寫入資料庫",
        "success_msg": "記錄成功！"
    },
    "English": {
        "title": "💡 AI Smart Finance & Global Accounting",
        "subtitle": "Effortlessly manage multi-currency assets and automated statements.",
        "menu": "Navigation",
        "menu_items": ["Quick Entry", "Screenshot AI Entry", "AI Smart Text Entry", "Auto Bank Statement Import", "Project ROI & Labor Cost", "Partner Profit Sharing", "Financial Health Dashboard", "Fixed Subscriptions", "Monthly Budget Settings"],
        "base_curr_title": "💱 Base Currency",
        "lang_title": "🌐 Language",
        "quick_entry": "Quick Manual Entry",
        "statement_import": "📥 Automated Statement Batch Import",
        "statement_desc": "Upload CSV statements from banks or e-wallets (e.g., PayPal, Stripe) for instant batch import.",
        "upload_csv": "Select Statement File",
        "preview_import": "Statement Preview",
        "import_success": "Successfully imported statements!",
        "date": "Date",
        "type": "Type",
        "expense": "Expense",
        "income": "Income",
        "account": "Account",
        "project": "Project",
        "category": "Category",
        "currency": "Currency",
        "orig_amount": "Original Amount",
        "exchange_rate": "Exchange Rate",
        "doc_status": "Doc Status",
        "tax_amount": "Tax",
        "payment_status": "Payment Status",
        "note": "Note",
        "submit": "Save to Database",
        "success_msg": "Recorded Successfully!"
    },
    "简体中文": {
        "title": "💡 AI 智能财务与全球记账系统",
        "subtitle": "轻松管理多币种资产、项目成本与自动化对账",
        "menu": "功能菜单",
        "menu_items": ["快速记账", "截图记账 (AI 图片识别)", "AI 智能文字记账", "自动化对账单/发票导入", "项目 ROI 与工时成本", "合伙人分润结算", "财务健康评分仪表板", "固定订阅管理", "设定每月预算"],
        "base_curr_title": "💱 结算基准币种",
        "lang_title": "🌐 界面语言选择",
        "quick_entry": "快速新增记账",
        "statement_import": "📥 自动化对账单批量导入",
        "statement_desc": "上传各银行、信用卡或移动支付导出的 CSV 对账单文件，系统将自动批量解析。",
        "upload_csv": "选择对账单 CSV 文件",
        "preview_import": "对账单数据预览与确认",
        "import_success": "成功批量导入对账单数据！",
        "date": "日期",
        "type": "类型",
        "expense": "支出",
        "income": "收入",
        "account": "资金账户",
        "project": "项目归属",
        "category": "分类",
        "currency": "币种",
        "orig_amount": "原始金额",
        "exchange_rate": "对汇率",
        "doc_status": "单据状态",
        "tax_amount": "估算税额",
        "payment_status": "收付状态",
        "note": "备注说明",
        "submit": "确认并写入数据库",
        "success_msg": "记录成功！"
    },
    "Melayu": {
        "title": "💡 Kewangan Pintar AI & Perakaunan Global",
        "subtitle": "Urus aset pelbagai mata wang dan import penyata automatik.",
        "menu": "Menu",
        "menu_items": ["Kemasukan Pantas", "Kemasukan Tangkapan Skrin AI", "Kemasukan Teks AI", "Import Penyata", "Kos & ROI Projek", "Perkongsian Untung", "Papan Pemuka Kesihatan", "Langganan Tetap", "Belanjawan Bulanan"],
        "base_curr_title": "💱 Mata Wang Asas",
        "lang_title": "🌐 Bahasa",
        "quick_entry": "Kemasukan Pantas",
        "statement_import": "📥 Import Kelompok Penyata",
        "statement_desc": "Muat naik fail CSV penyata bank atau e-dompet untuk import kelompok.",
        "upload_csv": "Pilih Fail CSV",
        "preview_import": "Pratonton Penyata",
        "import_success": "Berjaya mengimport!",
        "date": "Tarikh",
        "type": "Jenis",
        "expense": "Perbelanjaan",
        "income": "Pendapatan",
        "account": "Akaun",
        "project": "Projek",
        "category": "Kategori",
        "currency": "Mata Wang",
        "orig_amount": "Jumlah Asal",
        "exchange_rate": "Kadar Pertukaran",
        "doc_status": "Status Dokumen",
        "tax_amount": "Cukai",
        "payment_status": "Status Bayaran",
        "note": "Nota",
        "submit": "Simpan",
        "success_msg": "Berjaya!"
    },
    "日本語": {
        "title": "💡 AIスマート財務＆グローバル会計",
        "subtitle": "多通貨資産、プロジェクト費用、自動明細をシンプルに管理。",
        "menu": "メニュー",
        "menu_items": ["クイック入力", "スクショAI入力", "AIテキスト入力", "自動明細インポート", "プロジェクトROI", "パートナー分配", "財務健康ダッシュボード", "固定サブスク", "月次予算設定"],
        "base_curr_title": "💱 基準通貨",
        "lang_title": "🌐 言語選択",
        "quick_entry": "クイック手動入力",
        "statement_import": "📥 明細 CSV 一括インポート",
        "statement_desc": "銀行やウォレットのCSV明細をアップロードし、自動で一括記帳します。",
        "upload_csv": "CSV ファイルを選択",
        "preview_import": "明細プレビュー",
        "import_success": "インポートしました！",
        "date": "日付",
        "type": "タイプ",
        "expense": "支出",
        "income": "収入",
        "account": "口座",
        "project": "プロジェクト",
        "category": "カテゴリ",
        "currency": "通貨",
        "orig_amount": "元金額",
        "exchange_rate": "為替レート",
        "doc_status": "証憑",
        "tax_amount": "税額",
        "payment_status": "支払状態",
        "note": "備考",
        "submit": "データベースに保存",
        "success_msg": "保存しました！"
    },
    "한국어": {
        "title": "💡 AI 스마트 회계 & 글로벌 금융",
        "subtitle": "다중 통화 자산 및 자동 명세서 관리를 간편하게.",
        "menu": "메뉴",
        "menu_items": ["빠른 입력", "캡처 AI 입력", "AI 텍스트 입력", "자동 명세서 가져오기", "프로젝트 ROI", "파트너 수익 배분", "재무 건강 대시보드", "고정 구독", "월간 예산 설정"],
        "base_curr_title": "💱 기준 통화",
        "lang_title": "🌐 언어 선택",
        "quick_entry": "빠른 수동 입력",
        "statement_import": "📥 명세서 CSV 일괄 가져오기",
        "statement_desc": "은행 및 월렛의 CSV 파일을 업로드하여 자동으로 장부에 반영합니다.",
        "upload_csv": "CSV 파일 선택",
        "preview_import": "명세서 미리보기",
        "import_success": "성공적으로 가져왔습니다!",
        "date": "날짜",
        "type": "유형",
        "expense": "지출",
        "income": "수입",
        "account": "계정",
        "project": "프로젝트",
        "category": "카테고리",
        "currency": "통화",
        "orig_amount": "원래 금액",
        "exchange_rate": "환율",
        "doc_status": "증빙",
        "tax_amount": "세액",
        "payment_status": "지급 상태",
        "note": "비고",
        "submit": "데이터베이스에 저장",
        "success_msg": "저장되었습니다!"
    },
    "Español": {
        "title": "💡 Finanzas Inteligentes AI y Contabilidad",
        "subtitle": "Administra activos multidivisa y estados de cuenta automáticos.",
        "menu": "Menú",
        "menu_items": ["Entrada rápida", "Entrada de captura AI", "Entrada de texto AI", "Importar extractos", "ROI y Costos", "Distribución de socios", "Panel de salud financiera", "Suscripciones", "Presupuesto mensual"],
        "base_curr_title": "💱 Moneda Base",
        "lang_title": "🌐 Idioma",
        "quick_entry": "Entrada Rápida",
        "statement_import": "📥 Importación de Extractos",
        "statement_desc": "Sube archivos CSV de tus bancos o billeteras para importar en lote.",
        "upload_csv": "Seleccionar Archivo CSV",
        "preview_import": "Vista Previa",
        "import_success": "¡Importado con éxito!",
        "date": "Fecha",
        "type": "Tipo",
        "expense": "Gasto",
        "income": "Ingreso",
        "account": "Cuenta",
        "project": "Proyecto",
        "category": "Categoría",
        "currency": "Moneda",
        "orig_amount": "Monto Original",
        "exchange_rate": "Tasa",
        "doc_status": "Doc Status",
        "tax_amount": "Impuesto",
        "payment_status": "Estado",
        "note": "Nota",
        "submit": "Guardar",
        "success_msg": "¡Éxito!"
    },
    "Français": {
        "title": "💡 Finance Intelligente AI & Comptabilité",
        "subtitle": "Gérez vos actifs multidevises et vos relevés automatiques.",
        "menu": "Menu",
        "menu_items": ["Saisie rapide", "Saisie capture AI", "Saisie texte AI", "Import de relevés", "ROI & Coûts", "Partage des bénéfices", "Tableau de bord financier", "Abonnements", "Budget mensuel"],
        "base_curr_title": "💱 Devise de Base",
        "lang_title": "🌐 Langue",
        "quick_entry": "Saisie Rapide",
        "statement_import": "📥 Importation de Relevés",
        "statement_desc": "Téléchargez vos fichiers CSV bancaires pour un import en masse.",
        "upload_csv": "Sélectionner le Fichier CSV",
        "preview_import": "Aperçu",
        "import_success": "Importé avec succès !",
        "date": "Date",
        "type": "Type",
        "expense": "Dépense",
        "income": "Revenu",
        "account": "Compte",
        "project": "Projet",
        "category": "Catégorie",
        "currency": "Devise",
        "orig_amount": "Montant",
        "exchange_rate": "Taux",
        "doc_status": "Statut Doc",
        "tax_amount": "Taxe",
        "payment_status": "Paiement",
        "note": "Note",
        "submit": "Enregistrer",
        "success_msg": "Succès !"
    }
}

# 初始化 SQLite 資料庫
def init_db():
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(transactions)")
    columns = [row[1] for row in c.fetchall()]
    
    if not columns:
        c.execute('''CREATE TABLE transactions
                     (date TEXT, type TEXT, account TEXT, project TEXT, category TEXT, currency TEXT, original_amount REAL, exchange_rate REAL, amount REAL, invoice_status TEXT, tax_amount REAL, payment_status TEXT, note TEXT)''')
    elif 'invoice_status' not in columns:
        old_data = pd.read_sql("SELECT * FROM transactions", conn)
        c.execute('DROP TABLE transactions')
        c.execute('''CREATE TABLE transactions
                     (date TEXT, type TEXT, account TEXT, project TEXT, category TEXT, currency TEXT, original_amount REAL, exchange_rate REAL, amount REAL, invoice_status TEXT, tax_amount REAL, payment_status TEXT, note TEXT)''')
        if not old_data.empty:
            for _, row in old_data.iterrows():
                c.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (row['date'], row['type'], row['account'], row['project'], row['category'], row['currency'], 
                           row['original_amount'], row['exchange_rate'], row['amount'], "不適用", 0.0, "已結清", row['note']))
        
    c.execute('''CREATE TABLE IF NOT EXISTS budgets (category TEXT PRIMARY KEY, limit_amount REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions (name TEXT, type TEXT, account TEXT, project TEXT, category TEXT, amount REAL, day_of_month INT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS partners (name TEXT PRIMARY KEY, share_ratio REAL, investment REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS project_hours (project TEXT PRIMARY KEY, hours_spent REAL, hourly_cost REAL, outsourced_cost REAL)''')
    conn.commit()
    conn.close()

init_db()

# 🌐 側邊欄：語言與設定
st.sidebar.markdown(f"### {TRANSLATIONS['繁體中文']['lang_title']}")
languages_list = ["繁體中文", "English", "简体中文", "Melayu", "日本語", "한국어", "Español", "Français"]
selected_lang = st.sidebar.selectbox("Language", languages_list, index=0, label_visibility="collapsed")
t = TRANSLATIONS[selected_lang]

# 頁面主標題（更簡潔美觀）
st.title(t["title"])
st.markdown(f"*{t['subtitle']}*")
st.markdown("---")

# 側邊欄選單
menu = st.sidebar.radio(t["menu"], t["menu_items"])

# 讀取現有資料
conn = sqlite3.connect('finance.db')
df = pd.read_sql("SELECT * FROM transactions", conn)
budget_df = pd.read_sql("SELECT * FROM budgets", conn)
sub_df = pd.read_sql("SELECT * FROM subscriptions", conn)
partner_df = pd.read_sql("SELECT * FROM partners", conn)
hours_df = pd.read_sql("SELECT * FROM project_hours", conn)
conn.close()

# 🌐 全球基準幣種選擇
st.sidebar.markdown("---")
st.sidebar.subheader(t["base_curr_title"])
ALL_CURRENCIES = ["USD", "EUR", "TWD", "MYR", "CNY", "SGD", "HKD", "JPY", "GBP", "AUD", "CAD", "CHF", "NZD", "KRW", "THB", "VND", "IDR", "PHP"]
base_currency = st.sidebar.selectbox("Currency", ALL_CURRENCIES, index=0, key="global_base_curr", label_visibility="collapsed")

BASE_RATES_TO_USD = {
    "USD": 1.0, "EUR": 0.92, "TWD": 31.5, "MYR": 4.4, "CNY": 7.2, 
    "SGD": 1.35, "HKD": 7.8, "JPY": 150.0, "GBP": 0.78, "AUD": 1.5,
    "CAD": 1.38, "CHF": 0.88, "NZD": 1.65, "KRW": 1350.0, "THB": 35.0,
    "VND": 25000.0, "IDR": 15500.0, "PHP": 56.0
}

def convert_currency(amount_in_usd, target_currency):
    rate = BASE_RATES_TO_USD.get(target_currency, 1.0)
    return amount_in_usd * rate

# 1. 快速記帳
if menu in ["快速記帳", "Quick Entry", "快速记账", "Kemasukan Pantas", "クイック入力", "빠른 입력", "Entrada rápida", "Saisie rapide"]:
    st.subheader(f"✨ {t['quick_entry']}")
    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input(t["date"], datetime.now())
            t_type = st.selectbox(t["type"], [t["expense"], t["income"]])
            account = st.selectbox(t["account"], ["現金 / Cash", "銀行帳戶 / Bank", "信用卡 / Credit Card", "行動支付 / E-Wallet", "外幣帳戶 / Foreign", "其他 / Other"])
            project = st.selectbox(t["project"], ["日常一般 / General", "專案A / Project A", "專案B / Project B", "工作室共同成本 / Overhead"])
        with col2:
            category = st.selectbox(t["category"], ["餐飲 / Food", "交通 / Transport", "購物 / Shopping", "居住 / Housing", "娛樂 / Entertainment", "軟體訂閱 / Software", "設備材料 / Equipment", "其他 / Other"])
            currency = st.selectbox(t["currency"], ALL_CURRENCIES)
            original_amount = st.number_input(t["orig_amount"], min_value=0.0, step=10.0)
            
            default_rate = BASE_RATES_TO_USD.get(currency, 1.0) / BASE_RATES_TO_USD.get(base_currency, 1.0)
            exchange_rate = st.number_input(f"{t['exchange_rate']} ({base_currency})", min_value=0.0001, value=float(default_rate), format="%.4f")
        
        amount_in_usd = original_amount / exchange_rate if exchange_rate > 0 else original_amount
        display_converted_amount = convert_currency(amount_in_usd, base_currency)
        st.info(f"💱 折合基準貨幣 ({base_currency}): **${display_converted_amount:,.2f}**")
        
        with st.expander("🛠️ 進階單據與稅務設定 (選填)"):
            invoice_status = st.selectbox(t["doc_status"], ["不適用 / None", "已取得發票/收據 / Received", "尚未取得 / Pending"])
            calc_tax = display_converted_amount * 0.05 if "已取得" in invoice_status or "Received" in invoice_status else 0.0
            tax_amount = st.number_input(f"{t['tax_amount']} ({base_currency})", min_value=0.0, value=round(calc_tax, 2), step=1.0)
            payment_status = st.selectbox(t["payment_status"], ["已結清 / Settled", "尚未結清 / Unsettled"])
        
        note = st.text_input(t["note"])
        submitted = st.form_submit_button(t["submit"], use_container_width=True)

        if submitted:
            conn = sqlite3.connect('finance.db')
            c = conn.cursor()
            c.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (str(date), "支出" if t_type in ["支出", "Expense", "Perbelanjaan", "지출", "Gasto", "Dépense"] else "收入", account, project, category, currency, original_amount, exchange_rate, amount_in_usd, invoice_status if 'invoice_status' in locals() else "不適用", tax_amount if 'tax_amount' in locals() else 0.0, payment_status if 'payment_status' in locals() else "已結清", note))
            conn.commit()
            conn.close()
            st.success(t["success_msg"])
            st.rerun()

# 4. 自動化對帳單/發票匯入
elif menu in ["自動化對帳單/發票匯入", "Auto Bank Statement Import", "自动化对账单/发票导入", "Import Penyata", "自動明細インポート", "자동 명세서 가져오기", "Importar extractos", "Import de relevés"]:
    st.subheader(t["statement_import"])
    st.markdown(t["statement_desc"])
    
    uploaded_csv = st.file_uploader(t["upload_csv"], type=["csv", "txt"])
    
    if uploaded_csv is not None:
        try:
            preview_df = pd.read_csv(uploaded_csv)
            st.markdown(f"### {t['preview_import']}")
            st.dataframe(preview_df.head(10), use_container_width=True)
            
            if st.button("確認並批量寫入資料庫", use_container_width=True):
                conn = sqlite3.connect('finance.db')
                c = conn.cursor()
                
                imported_count = 0
                for _, row in preview_df.iterrows():
                    date_val = str(datetime.now().date())
                    orig_amt = 100.0
                    note_val = "對帳單自動批次匯入"
                    
                    for col in preview_df.columns:
                        col_lower = str(col).lower()
                        if 'date' in col_lower or '日期' in col_lower:
                            date_val = str(row[col])
                        elif 'amount' in col_lower or 'amt' in col_lower or '金額' in col_lower or '交易金額' in col_lower:
                            try:
                                orig_amt = float(str(row[col]).replace(',', ''))
                            except:
                                pass
                        elif 'desc' in col_lower or 'note' in col_lower or '摘要' in col_lower or '備註' in col_lower or '說明' in col_lower:
                            note_val = str(row[col])
                    
                    t_type = "支出" if orig_amt < 0 else "支出"
                    orig_amt = abs(orig_amt)
                    amount_in_usd = orig_amt / BASE_RATES_TO_USD.get(base_currency, 1.0)
                    
                    c.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                              (date_val, t_type, "銀行帳戶 / Bank", "日常一般 / General", "其他 / Other", base_currency, orig_amt, 1.0, amount_in_usd, "不適用", 0.0, "已結清", note_val))
                    imported_count += 1
                
                conn.commit()
                conn.close()
                st.success(f"✨ {t['import_success']} (共匯入 {imported_count} 筆資料)")
                st.rerun()
        except Exception as e:
            st.error(f"檔案解析失敗，請確認 CSV 格式是否正確。錯誤訊息: {e}")

# 其它選單 (儀表板 / 資料庫管理)
else:
    st.subheader(menu)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        total_inc_usd = df[df['type'].isin(['收入', 'Income'])]['amount'].sum()
        total_exp_usd = df[df['type'].isin(['支出', 'Expense', 'Perbelanjaan'])]['amount'].sum()
        net_usd = total_inc_usd - total_exp_usd
        
        inc_conv = convert_currency(total_inc_usd, base_currency)
        exp_conv = convert_currency(total_exp_usd, base_currency)
        net_conv = convert_currency(net_usd, base_currency)
        
        # 漂亮的 KPI 摘要指標卡片
        col1, col2, col3 = st.columns(3)
        col1.metric(f"總收入 ({base_currency})", f"${inc_conv:,.2f}")
        col2.metric(f"總支出 ({base_currency})", f"${exp_conv:,.2f}")
        col3.metric(f"總淨結餘 ({base_currency})", f"${net_conv:,.2f}", delta=f"${net_conv:,.2f}")

        st.markdown("---")
        st.markdown("### 📝 詳細明細資料庫")
        edited_df = st.data_editor(
            df.sort_values(by="date", ascending=False),
            num_rows="dynamic",
            use_container_width=True,
            key="finance_editor"
        )
        
        if st.button("儲存表格變更", use_container_width=True):
            conn = sqlite3.connect('finance.db')
            edited_df.to_sql('transactions', conn, if_exists='replace', index=False)
            conn.close()
            st.success("資料已成功更新！")
            st.rerun()
    else:
        st.info("目前尚無資料，請從左側欄位新增第一筆記帳或上傳對帳單。")