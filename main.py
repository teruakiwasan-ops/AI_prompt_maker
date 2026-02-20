import streamlit as st
import pandas as pd
from google import genai  # ここが requirements.txt の google-genai と対応します
import io

# --- 1. セキュリティ設定 ---
# APIキーはGitHubには書かず、Streamlit CloudのSecretsから読み込みます
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error("【エラー】APIキーが設定されていません。StreamlitのSecretsに 'GEMINI_API_KEY' を追加してください。")
    st.stop()

# --- 2. 画面構成 ---
st.set_page_config(page_title="AIプロンプト・デザイナー", page_icon="🪄", layout="wide")

st.title("🪄 AI専用プロンプト・デザイナー")
st.markdown("""
誰もが「プロ級のAI監査」をできるようにするためのツールです。  
ファイルをアップロードすると、**そのデータ専用の指示文（プロンプト）**をAIが執筆します。
""")

# --- 3. ファイルアップロード ---
uploaded_file = st.file_uploader("解析したいExcel、CSV、またはPDFを選択してください", type=["xlsx", "xls", "csv", "pdf"])

if uploaded_file:
    with st.spinner("AIがデータの構造を読み取っています..."):
        data_summary = ""
        
        # ファイル形式ごとの処理
        try:
            if uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
                data_summary = f"Excelファイルです。列名: {df.columns.tolist()} \nデータの先頭5件: \n{df.head(5).to_csv()}"
            elif uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, encoding='cp932')
                data_summary = f"CSVファイルです。列名: {df.columns.tolist()} \nデータの先頭5件: \n{df.head(5).to_csv()}"
            else:
                data_summary = "PDFまたは非構造化ドキュメントです。内容を推測してプロンプトを作成します。"

            # --- 4. AIによるプロンプト設計 ---
            # ここで「AIに、AIへの指示を作らせる」メタプロンプトを実行
            instruction = f"""
            あなたは世界最高峰のプロンプトエンジニアです。
            以下のデータの構造を分析し、GoogleスプレッドシートのGeminiサイドバーで
            「ミスや不整合を100%見つける」ための最高精度の指示文（プロンプト）を執筆してください。

            【データの構造・サンプル】
            {data_summary}

            【プロンプト作成のルール】
            1. スプレッドシートのGeminiにそのままコピペして使える形式にする。
            2. 「どの列とどの列を比較して矛盾を探すべきか」を具体的に指定する。
            3. 施設管理や事務の専門家として、厳しく、かつ具体的なアクション（業者督促など）を促す内容にする。
            4. 冒頭は「以下のルールに従って、このシートを徹底的に監査してください」で始める。
            """

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=instruction
            )

            # --- 5. 結果の表示 ---
            st.divider()
            st.subheader("📋 生成された専用プロンプト")
            st.info("この文章をコピーして、Googleシート右側のGeminiパネルに貼り付けてください。")
            
            st.code(response.text, language="text")
            
            st.success("作成完了！このプロンプトは、今アップロードされたファイルに完全に最適化されています。")

        except Exception as e:
            st.error(f"解析中にエラーが発生しました: {e}")

st.divider()
st.caption("© 2026 Facility Management AI Prompt Designer")
