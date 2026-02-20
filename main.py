import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="進捗管理AIプロンプター", layout="wide")

st.title("🏗️ 施設管理・進捗チェックアプリ")
st.markdown("Excelをアップロードして、Geminiへの指示文（プロンプト）を生成します。")

uploaded_file = st.file_uploader("管理表(Excel/CSV)を選択", type=["xlsx", "xls", "csv"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='cp932')
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"読み込み完了: {len(df)}件")

        # モード選択
        mode = st.selectbox("チェック内容を選択", [
            "1. 進捗の矛盾（注文済みなのに日付がない等）",
            "2. 予算・数値の精査（予算0で支出がある等）",
            "3. 担当者別のタスク抽出"
        ])

        # プロンプト生成（1222管理表の構造に特化）
        if "1." in mode:
            prompt = f"施設管理の専門家として、このデータの不備を指摘してください。\n・案件名に注文済とあるが日付が空欄の箇所\n・法定点検を過ぎて検収日が空欄の箇所\n\n対象データ:\n{df.head(30).to_csv()}"
        elif "2." in mode:
            prompt = f"財務監査官として数値の矛盾を指摘してください。\n・予算額の欄に計上No(305等)が入り金額と混同されている箇所\n・予算に対して実算が異常に高い箇所\n\n対象データ:\n{df.head(30).to_csv()}"
        else:
            prompt = f"担当者ごとに未完了（検収日が空欄）のタスクを整理し、次に業者督促と起票のどちらが必要かアドバイスしてください。\n\n対象データ:\n{df.head(30).to_csv()}"

        st.subheader("📋 Geminiに貼り付ける指示文")
        st.code(prompt, language="text")
        st.info("右上のコピーボタンを押して、スプレッドシートのGeminiパネルに貼り付けてください。")

    except Exception as e:
        st.error(f"エラー: {e}")
