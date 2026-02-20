import streamlit as st
import pandas as pd
from google import genai
import io

# 1. 初期設定（APIキーはStreamlitのSecretsに保存するか、直書きします）
# ※ 20人が使うプロンプトを作るための「頭脳」として1つだけAPIキーを使います
GENAI_API_KEY = "AIzaSyBUZbZnfWmozRIbQN3tKTxbjNEE2qmNRXI"
client = genai.Client(api_key=GENAI_API_KEY)

st.set_page_config(page_title="AIプロンプト生成機", layout="wide")

st.title("🧙‍♂️ AI専用プロンプト・デザイナー")
st.markdown("ファイルを読み込み、そのデータを『Geminiサイドバー』で完璧に解析するための**専用指示文**を生成します。")

# ファイルアップローダー（PDF/Excel/Text対応）
uploaded_file = st.file_uploader("ファイルをアップロード (Excel, PDF, TXT)", type=["xlsx", "xls", "pdf", "txt", "csv"])

if uploaded_file:
    with st.spinner("AIがファイル構造を分析中..."):
        content_summary = ""
        
        # --- ファイル形式別の読み込み ---
        if uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
            content_summary = f"Excelデータ: 列名={df.columns.tolist()}, サンプル={df.head(5).to_csv()}"
        elif uploaded_file.name.endswith('.pdf'):
            content_summary = "PDFファイル（内容はファイル名を元に推測します）"
        else:
            content_summary = uploaded_file.read().decode("utf-8")[:1000]

        # --- AIへの依頼：最強のプロンプトを作らせる ---
        analysis_prompt = f"""
        あなたはプロンプトエンジニアです。
        以下のデータ（ファイル）を、GoogleスプレッドシートのGeminiサイドバーで解析させようとしています。
        
        【データの概要】
        {content_summary}
        
        このデータを読み込ませたGeminiが、
        1. 入力漏れや不整合を絶対に見逃さない
        2. データの構造（どの列が何を示しているか）を完璧に理解する
        3. 具体的で厳しいアドバイスを出す
        
        ようになるための「最強のプロンプト（指示文）」を1つ作成してください。
        出力はそのまま貼り付けられる形式にしてください。
        """

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=analysis_prompt
            )
            
            generated_prompt = response.text

            # 表示
            st.subheader("📋 生成された専用プロンプト")
            st.write("この文章をコピーして、Geminiサイドバーに貼り付けてください。")
            st.code(generated_prompt, language="text")
            
            st.success("このプロンプトは、アップロードされたファイル専用にカスタマイズされています。")

        except Exception as e:
            st.error(f"AI解析エラー: {e}")

st.divider()
st.caption("※20名のメンバーがそれぞれのファイルに合わせた『最強の聞き方』をこれで見つけられます。")
