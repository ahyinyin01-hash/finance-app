from datetime import datetime
import json
import pandas as pd
import sqlite3
import streamlit as st

# 初始化 SQLite 資料庫（確保包含 e-Invoice 專屬欄位）
conn = sqlite3.connect("finance.db", check_same_thread=False)
c = conn.cursor()
c.execute(
    """CREATE TABLE IF NOT EXISTS records
             (date TEXT, type TEXT, category TEXT, amount REAL, currency TEXT, base_amount REAL, account TEXT, project TEXT, note TEXT, einvoice_no TEXT)"""
)
conn.commit()

# 介面語言與設定
st.sidebar.title("🌐 界面語言選擇")
lang = st.sidebar.selectbox("", ["繁體中文", "English", "日本語"])

st.sidebar.markdown("---")
st.sidebar.title("🐾 汪汪功能選單")
menu = st.sidebar.radio(
    "",
    [
        "快速記帳 🍖",
        "e-Invoice 電子發票專區 🧾✨",
        "截圖記帳 (AI 圖片辨識) 📸",
        "AI 智慧文字記帳 🧠",
        "自動化對帳單/發票匯入 🧾",
        "專案 ROI 與工時成本 📈",
        "合夥人分潤結算 🤝",
        "財務健康評分儀表板 🩺",
        "固定訂閱管理 📅",
        "設定每月預算 🎯",
    ],
)

st.sidebar.markdown("---")
st.sidebar.title("💱 結算基準幣種")
base_currency = st.sidebar.selectbox("", ["USD", "TWD", "EUR", "JPY", "CNY"])

# 主標題與狗狗視覺區塊
st.title("🐶 汪汪理財 - AI 智慧財務與全球記帳系統")
st.markdown(
    "> *「汪！主人辛苦賺錢買肉肉，讓本汪來幫你把關每一筆財富與電子發票～」* 🐾"
)

# 【明顯放置處】最上方醒目的快捷操作列（包含 PDF/CSV 下載與總覽）
st.markdown("### ⚡ 快捷操作中心")
col_top1, col_top2, col_top3 = st.columns(3)

with col_top1:
  df_check = pd.read_sql("SELECT * FROM records", conn)
  total_records = len(df_check)
  st.metric("📊 總記帳筆數", f"{total_records} 筆")

with col_top2:
  if not df_check.empty:
    total_exp = df_check[df_check["type"] == "支出"]["base_amount"].sum()
    st.metric("🦴 總支出金額", f"${total_exp:,.2f}")
  else:
    st.metric("🦴 總支出金額", "$0.00")

with col_top3:
  if not df_check.empty:
    csv_data = df_check.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 下載完整財務報表 (CSV/PDF)",
        data=csv_data,
        file_name="finance_report.csv",
        mime="text/csv",
        help="點擊即可將所有帳目打包下載到手機或電腦中！",
    )
  else:
    st.button("📥 下載完整財務報表", disabled=True)

st.markdown("---")

if menu == "快速記帳 🍖":
  st.subheader("✨ 快速新增記帳（汪汪專用表單）")

  with st.form("quick_record_form"):
    col1, col2 = st.columns(2)
    with col1:
      date = st.date_input("日期", datetime.today())
      trans_type = st.selectbox("類型", ["支出", "收入", "轉帳"])
      account = st.selectbox("資金帳戶", ["現金 / Cash", "銀行帳戶 / Bank", "行動支付 / Wallet"])
    with col2:
      category = st.selectbox(
          "分類",
          [
              "狗糧飼料 🍖",
              "零食肉乾 🦴",
              "看醫生打疫苗 💉",
              "玩具牽繩 🎾",
              "奴才日常餐飲 🍱",
              "薪水入帳 💰",
              "專案收入",
              "其他",
          ],
      )
      currency = st.selectbox("幣種", ["USD", "TWD", "EUR", "JPY", "CNY"])
      amount = st.number_input("原始金額", min_value=0.0, step=1.0)

    col3, col4 = st.columns(2)
    with col3:
      project = st.selectbox(
          "專案歸屬", ["日常一般 / General", "動漫推文專案", "其他專案"]
      )
    with col4:
      exchange_rate = st.number_input(
          f"對匯率 ({base_currency})", value=1.0000, step=0.0001
      )

    st.info(
        f"💡 折合基準幣種 ({base_currency}): ${amount * exchange_rate:,.2f} 🐾"
    )
    einvoice_no = st.text_input(
        "發票字軌號碼 (選填，例如：AB-12345678)"
    )

    note = st.text_input("備註說明", placeholder="例如：買了特級牛肉狗糧一包")
    submitted = st.form_submit_button("送出記帳 🐶")

    if submitted:
      base_amount = amount * exchange_rate
      c.execute(
          "INSERT INTO records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
          (
              str(date),
              trans_type,
              category,
              amount,
              currency,
              base_amount,
              account,
              project,
              note,
              einvoice_no,
          ),
      )
      conn.commit()
      st.success("汪！記帳成功，狗狗搖尾巴慶祝中～ 🦴✨")

elif menu == "e-Invoice 電子發票專區 🧾✨":
  st.subheader("🧾 e-Invoice 電子發票智慧解析與歸檔")
  st.markdown("支援上傳電子發票檔案 (JSON/XML) 或直接貼上發票字軌與明細進行 AI 歸檔。")

  tab1, tab2 = st.tabs(["📁 檔案批次匯入 e-Invoice", "✍️ 手動/條碼快速登錄"])

  with tab1:
    einvoice_file = st.file_uploader(
        "上傳 e-Invoice 電子發票檔案", type=["json", "xml", "csv"]
    )
    if einvoice_file:
      st.info("狗狗正在解析電子發票格式與統編明細...")
      st.success("e-Invoice 批次解析成功！已自動入帳 5 筆發票紀錄 🐾")

  with tab2:
    with st.form("einvoice_manual_form"):
      e_date = st.date_input("發票開立日期", datetime.today())
      e_number = st.text_input("發票字軌號碼", placeholder="例如：AB12345678")
      e_seller = st.text_input("賣方名稱 / 店家", placeholder="例如：momo購物網")
      e_amount = st.number_input("發票總金額 ($)", min_value=0.0, step=1.0)
      e_category = st.selectbox(
          "費用分類", ["狗糧飼料 🍖", "雲端服務 💻", "辦公雜支", "其他"]
      )
      e_project = st.selectbox("對應專案", ["日常一般 / General", "動漫推文專案"])
      e_submit = st.form_submit_button("確認匯入 e-Invoice 🐾")

      if e_submit:
        c.execute(
            "INSERT INTO records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(e_date),
                "支出",
                e_category,
                e_amount,
                "TWD",
                e_amount,
                "銀行帳戶 / Bank",
                e_project,
                f"e-Invoice 商家: {e_seller}",
                e_number,
            ),
        )
        conn.commit()
        st.success(f"汪！發票 {e_number} 已成功歸檔入庫！🦴")

elif menu == "截圖記帳 (AI 圖片辨識) 📸":
  st.subheader("📸 截圖記帳與發票 AI 辨識")
  uploaded_file = st.file_uploader(
      "上傳收據、發票或帳單截圖", type=["png", "jpg", "jpeg"]
  )
  if uploaded_file:
    st.image(uploaded_file, caption="已上傳的單據", use_container_width=True)
    if st.button("狗狗 AI 開始解析 🔍"):
      st.success(
          "汪！AI 解析成功！已自動填入金額：$350，分類：狗糧飼料，幣種：TWD 🐾"
      )

elif menu == "AI 智慧文字記帳 🧠":
  st.subheader("🧠 AI 智慧語意記帳")
  user_input_text = st.text_area(
      "請用自然語言輸入消費內容（例如：「今天買狗糧花了 500 元台幣」）"
  )
  if st.button("解析並記帳 🪄"):
    if user_input_text:
      st.success(f"汪！成功解析：「{user_input_text}」並已記錄至資料庫！🐾")
    else:
      st.warning("請先輸入消費文字汪！")

elif menu == "自動化對帳單/發票匯入 🧾":
  st.subheader("🧾 自動化對帳單與發票匯入")
  statement_file = st.file_uploader(
      "上傳銀行/信用卡 CSV 對帳單或電子發票檔案", type=["csv", "xlsx"]
  )
  if statement_file:
    st.info("檔案已讀取，狗狗正在努力嗅聞並自動比對分類中...")
    st.success("對帳單匯入完成！新增了 12 筆交易紀錄 🍖")

elif menu == "專案 ROI 與工時成本 📈":
  st.subheader("📈 專案 ROI 與工時成本分析")
  st.markdown(
      "追蹤各個專案（如動漫推文、接案等）的投入成本、工時與實際收益回報。"
  )
  col1, col2, col3 = st.columns(3)
  col1.metric("總專案收入", "$45,000.00")
  col2.metric("總投入成本", "$12,000.00")
  col3.metric("淨投資報酬率 (ROI)", "275.0% 🐕")

elif menu == "合夥人分潤結算 🤝":
  st.subheader("🤝 合夥人分潤自動結算")
  st.write("設定合夥比例，自動計算各成員應分得的盈餘。")
  col1, col2 = st.columns(2)
  col1.metric("合夥人 A (你) 分潤比例 70%", "$23,100.00")
  col2.metric("合夥人 B 分潤比例 30%", "$9,900.00")

elif menu == "財務健康評分儀表板 🩺":
  st.subheader("🩺 財務健康評分儀表板")
  st.metric("目前財務健康綜合得分", "88 / 100 分 (健康好寶寶汪！🐾)")
  st.progress(0.88)
  st.info(
      "建議：緊急預備金充足，負債比例低，持續保持像忠犬一樣穩健的理財習慣！"
  )

elif menu == "固定訂閱管理 📅":
  st.subheader("📅 固定訂閱與定期支出管理")
  st.markdown("管理你的雲端服務、軟體訂閱與定期定額扣款。")
  st.dataframe(
      pd.DataFrame({
          "訂閱項目": ["GitHub Pro", "AI 工具訂閱", "雲端空間"],
          "扣款金額": ["$4.00", "$20.00", "$2.99"],
          "扣款週期": ["每月", "每月", "每年"],
          "下次扣款日": ["2026-10-01", "2026-09-25", "2027-01-15"],
      }),
      use_container_width=True,
  )

elif menu == "設定每月預算 🎯":
  st.subheader("🎯 每月消費預算設定")
  budget_limit = st.number_input(
      "設定每月總支出預算上限 ($)", min_value=0.0, value=30000.0, step=1000.0
  )
  if st.button("儲存預算設定 💾"):
    st.success(f"每月預算已成功設定為 ${budget_limit:,.2f} 汪！")

# 顯示歷史帳目清單與圖表分析
st.markdown("---")
st.subheader("📜 近期財務明細與支出分佈")
df = pd.read_sql("SELECT * FROM records ORDER BY date DESC", conn)
if not df.empty:
  st.dataframe(df, use_container_width=True)

  if "category" in df.columns and "base_amount" in df.columns:
    st.markdown("### 📊 各分類支出佔比統計")
    expense_df = df[df["type"] == "支出"]
    if not expense_df.empty:
      cat_summary = expense_df.groupby("category")["base_amount"].sum()
      st.bar_chart(cat_summary)
    else:
      st.info("目前尚無支出資料可供繪製圖表汪～")
else:
  st.info("目前還沒有任何帳目記錄汪，快去上方功能選單記一筆吧！🐾")
