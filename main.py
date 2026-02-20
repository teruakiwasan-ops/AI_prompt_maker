import streamlit as st
import pandas as pd
from google import genai
import io

# --- 1. セキュリティ設定 ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error("【設定エラー】StreamlitのSecretsに 'GEMINI_API_KEY' を登録してください。")
    st.stop()

# --- 2. 画面構成 ---
st.set_page_config(page_title="AIプロンプト・デザイナー", page_icon="🪄", layout="wide")

st.title("🪄 AI専用プロンプト・デザイナー")
st.markdown("""
### 「AI監査」サポートツール
ファイルをアップロードすると、そのデータ構造をAIが分析し、Googleスプレッドシート等のGeminiサイドバーで使える**「最強の指示文」**を生成します。
""")

# --- 3. ファイルアップロード ---
uploaded_file = st.file_uploader("Excel(xlsx/xls) または CSV を選択してください", type=["xlsx", "xls", "csv"])

if uploaded_file:
    with st.spinner("AIがデータの構造を解析中..."):
        data_summary = ""
        
        try:
            # ファイル読み込み
            if uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
                data_summary = f"Excelファイル。列名: {df.columns.tolist()} \n先頭データサンプル: \n{df.head(5).to_csv()}"
            elif uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, encoding='cp932')
                data_summary = f"CSVファイル。列名: {df.columns.tolist()} \n先頭データサンプル: \n{df.head(5).to_csv()}"

            # --- 4. プロンプト生成ボタン ---
            if st.button("このシート専用のプロンプトを生成する"):
                # AIへのメタ指示
                instruction = f"""
                あなたは世界最高峰のプロンプトエンジニアです。
                以下のデータの構造を分析し、GoogleスプレッドシートのGeminiサイドバーで
                「入力漏れ・数値矛盾・期限切れ」を完璧に見つけるための指示文（プロンプト）を執筆してください。

                【解析対象データ構造】
                {data_summary}

                【プロンプトへの要求】
                1. 「以下のルールでこのシートを監査してください」から始めること。
                2. 具体的にどの列（案件名、予算、実算など）に注目すべきか明記すること。
                3. 「予算欄に計上Noが入っている可能性」や「注文済みと言いつつ日付がない」といった施設管理特有のミスを突く内容にすること。
                4. 指示は箇条書きで分かりやすく。
                """

                # モデルは安定性を重視して1.5-flashを指定
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=instruction
                )

                # --- 5. 結果表示 ---
                st.divider()
                st.subheader("📋 生成された専用プロンプト")
                st.info("下の枠内をコピーして、スプレッドシートの右側にあるGeminiに貼り付けてください。")
                st.code(response.text, language="text")
                st.success("作成完了！このプロンプトを使うと、AIがシートの不備を的確に指摘します。")

        except Exception as e:
            st.error(f"解析中にエラーが発生しました: {e}")

st.divider()
st.caption("© 2026 Facility Management Support Tool")
