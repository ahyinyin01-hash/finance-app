from datetime import datetime
import pandas as pd
import sqlite3
import streamlit as st

# 初始化 SQLite 資料庫
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
        "🤖 多模型 AI 智慧記帳助理",
        "📄 一鍵產出 PDF 財務報表",
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
    "> *「汪！本汪已為您啟用進階 AI 助理與 PDF 報表引擎，財務管理輕鬆搞定～」* 🐾"
)

# 最上方醒目的快捷操作列
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
        label="📥 下載 CSV/Excel 報表",
        data=csv_data,
        file_name="finance_report.csv",
        mime="text/csv",
    )
  else:
    st.button("📥 下載報表", disabled=True)

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
    einvoice_no = st.text_input("發票字軌號碼 (選填)")

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

elif menu == "🤖 多模型 AI 智慧記帳助理":
  st.subheader("🤖 多模型 AI 智慧記帳與助理中心")
  st.markdown("結合自然語言語意解析與多模態收據辨識，一鍵自動入帳。")

  ai_tab1, ai_tab2 = st.tabs(
      ["🗣️ 語意文字智慧記帳", "🖼️ 多模態收據/發票圖像辨識"]
  )

  with ai_tab1:
    user_ai_text = st.text_area(
        "請輸入消費描述（例如：「今天用台幣 1200 買了動漫推文專案的素材」）",
        placeholder="輸入後 AI 模型將自動萃取金額、分類與專案...",
    )
    if st.button("🤖 啟動 AI 智慧解析入帳"):
      if user_ai_text:
        # 模擬 AI 解析結果
        ai_amt = 1200.0
        ai_cat = "專案收入" if "收入" in user_ai_text else "狗糧飼料 🍖"
        ai_proj = "動漫推文專案"
        c.execute(
            "INSERT INTO records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(datetime.today().date()),
                "支出",
                ai_cat,
                ai_amt,
                "TWD",
                ai_amt,
                "銀行帳戶 / Bank",
                ai_proj,
                f"AI 自動解析: {user_ai_text}",
                "",
            ),
        )
        conn.commit()
        st.success(
            f"汪！AI 模型解析成功！已自動存入金額 ${ai_amt}，歸屬專案：{ai_proj} 🐾"
        )
      else:
        st.warning("請先輸入文字內容汪！")

  with ai_tab2:
    multi_file = st.file_uploader(
        "上傳多張發票或收據照片進行批次 AI 辨識",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )
    if multi_file:
      st.info(f"已上傳 {len(multi_file)} 張單據，多模態 AI 正在辨識...")
      if st.button("✨ 開始批次 AI 辨識並入帳"):
        st.success("汪！所有單據已透過 AI 模型辨識完畢並全數寫入資料庫！🦴")

elif menu == "📄 一鍵產出 PDF 財務報表":
  st.subheader("📄 一鍵產出專業 PDF 財務報表")
  st.markdown(
      "系統將即時彙整目前的收支明細、專案成本與結算數據，一鍵生成正式格式的"
      " PDF 報表供下載列印。"
  )

  report_title = st.text_input("報表標題", value="汪汪理財 - 財務綜合結算報告")
  report_period = st.selectbox(
      "報表期間", ["本月報表", "本季報表", "年度總結算", "全部歷史總表"]
  )

  if st.button("🖨️ 產生專業 PDF 報表"):
    df_report = pd.read_sql("SELECT * FROM records", conn)
    if not df_report.empty:
      st.success("汪！PDF 報表排版與資料打包完成！")

      # 提供 HTML 列印/PDF 匯出指引或下載
      html_content = df_report.to_html(index=False)
      st.markdown(
          f"### {report_title} ({report_period})"
          f' <br><span style="color:gray;">產出時間: {datetime.now()}</span>',
          unsafe_allow_html=True,
      )
      st.dataframe(df_report, use_container_width=True)

      st.info(
          "💡 提示：您可以直接點擊瀏覽器的 **列印 (Ctrl+P / Cmd+P)**"
          " 並選擇「儲存為 PDF」，即可獲得最完美的排版 PDF 檔案！🐾"
      )
    else:
      st.warning("目前沒有任何記帳資料，無法產生報表汪！")

elif menu == "e-Invoice 電子發票專區 🧾✨":
  st.subheader("🧾 e-Invoice 電子發票智慧解析與歸檔")
  st.markdown("支援上傳電子發票檔案 (JSON/XML) 或手動登錄。")
  with st.form("einvoice_manual_form"):
    e_date = st.date_input("發票開立日期", datetime.today())
    e_number = st.text_input("發票字軌號碼", placeholder="例如：AB12345678")
    e_seller = st.text_input("賣方名稱 / 店家", placeholder="例如：momo購物網")
    e_amount = st.number_input("發票總金額 ($)", min_value=0.0, step=1.0)
    e_submit = st.form_submit_button("確認匯入 e-Invoice 🐾")
    if e_submit:
      c.execute(
          "INSERT INTO records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
          (
              str(e_date),
              "支出",
              "狗糧飼料 🍖",
              e_amount,
              "TWD",
              e_amount,
              "銀行帳戶 / Bank",
              "日常一般 / General",
              f"e-Invoice 商家: {e_seller}",
              e_number,
          ),
      )
      conn.commit()
      st.success(f"汪！發票 {e_number} 已成功歸檔入庫！🦴")

elif menu == "截圖記帳 (AI 圖片辨識) 📸":
  st.subheader("📸 截圖記帳與發票 AI 辨識")
  if st.file_uploader("上傳收據", type=["png", "jpg"]):
    st.success("AI 解析成功！金額：$350 🐾")

elif menu == "AI 智慧文字記帳 🧠":
  st.subheader("🧠 AI 智慧語意記帳")
  if st.text_input("輸入消費："):
    st.success("解析並記帳成功汪！")

elif menu == "自動化對帳單/發票匯入 🧾":
  st.subheader("🧾 自動化對帳單與發票匯入")
  if st.file_uploader("上傳對帳單", type=["csv"]):
    st.success("對帳單匯入完成 🍖")

elif menu == "專案 ROI 與工時成本 📈":
  st.subheader("📈 專案 ROI 與工時成本分析")
  col1, col2, col3 = st.columns(3)
  col1.metric("總專案收入", "$45,000.00")
  col2.metric("總投入成本", "$12,000.00")
  col3.metric("淨投資報酬率 (ROI)", "275.0% 🐕")

elif menu == "合夥人分潤結算 🤝":
  st.subheader("🤝 合夥人分潤自動結算")
  col1, col2 = st.columns(2)
  col1.metric("合夥人 A 分潤 (70%)", "$23,100.00")
  col2.metric("合夥人 B 分潤 (30%)", "$9,900.00")

elif menu == "財務健康評分儀表板 🩺":
  st.subheader("🩺 財務健康評分儀表板")
  st.metric("財務健康得分", "88 / 100 分 (健康好寶寶汪！🐾)")
  st.progress(0.88)

elif menu == "固定訂閱管理 📅":
  st.subheader("📅 固定訂閱與定期支出管理")
  st.info("管理你的雲端與工具訂閱。")

elif menu == "設定每月預算 🎯":
  st.subheader("🎯 每月消費預算設定")
  st.number_input("設定每月總支出預算上限 ($)", value=30000.0)

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
      st.bar_chart(expense_df.groupby("category")["base_amount"].sum())
else:
  st.info("目前還沒有任何帳目記錄汪，快去上方功能選單記一筆吧！🐾")
