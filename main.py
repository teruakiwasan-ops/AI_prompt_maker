import streamlit as st
import pandas as pd
from google import genai
import io

# --- 1. APIキーの設定 (Secretsから読み込み) ---
try:
    # Streamlit Cloudの Settings > Secrets に登録したキーを使用
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error("【設定エラー】StreamlitのSecretsに 'GEMINI_API_KEY' を正しく登録してください。")
    st.stop()

# --- 2. アプリの基本設定 ---
st.set_page_config(page_title="AIプロンプト・デザイナー", page_icon="🪄", layout="wide")

st.title("🪄 AI専用プロンプト・デザイナー (1.5 Flash版)")
st.markdown("""
### ファイルを読み込み、Geminiサイドバー用の「最強指示文」を自動作成
20名のメンバーが誰でも精度の高い監査ができるよう、Excelの項目名から最適なプロンプトを生成します。
""")

# --- 3. ファイルのアップロード ---
uploaded_file = st.file_uploader("Excel(xlsx/xls) または CSV を選択", type=["xlsx", "xls", "csv"])

if uploaded_file:
    with st.spinner("AIがデータの構造（項目名）を分析しています..."):
        try:
            # ファイルの読み込み
            if uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.csv'):
                # 日本語の文字化け対策(cp932)
                try:
                    df = pd.read_csv(uploaded_file, encoding='cp932')
                except:
                    df = pd.read_csv(uploaded_file, encoding='utf-8')
            
            # 【重要】429エラー対策：データを最小限に絞る
            # 全データを送ると制限に引っかかるため、「列名」と「最初の5行」だけに限定します
            columns_list = df.columns.tolist()
            sample_rows = df.head(5).to_csv(index=False)
            
            st.success(f"読み込み成功！ 項目数: {len(columns_list)} / データ総数: {len(df)}件")

            # --- 4. プロンプト生成実行 ---
            if st.button("このシート専用のプロンプトを生成"):
                # メタ・プロンプト（AIに指示を作らせるための指示）
                system_instruction = f"""
                あなたは高度なプロンプトエンジニアです。
                ユーザーがアップロードした以下のデータの構造（列名）を分析し、
                GoogleスプレッドシートのGeminiサイドバーで「ミスを見つける」ための
                具体的で厳しい監査用プロンプト（指示文）を1つ作成してください。

                【解析対象の項目名】
                {columns_list}

                【データのサンプル（5行）】
                {sample_rows}

                【プロンプト作成の条件】
                1. 「以下のルールで、このシートのデータを厳格に監査してください」で始める。
                2. 具体的な列名を引用すること（例：「『案件名』が注文済なのに『発注日』が空欄のものを探せ」など）。
                3. 予算額の欄に計上Noが混じっていないか、期限が切れていないか等の視点を入れる。
                4. 初心者がコピペしてそのまま使える形式にすること。
                """

                # 制限の緩い 1.5-flash モデルを指定
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=system_instruction
                )

                # 結果の表示
                st.divider()
                st.subheader("📋 生成された専用プロンプト")
                st.info("この文章をコピーして、Googleシート右側のGeminiに貼り付けてください。")
                
                # コピーしやすいように st.code で表示
                st.code(response.text, language="text")
                
                st.success("作成が完了しました！このプロンプトは現在のファイル構造に最適化されています。")

        except Exception as e:
            st.error(f"解析中にエラーが発生しました。ファイル形式を確認してください。: {e}")

st.divider()
st.caption("© 2026 Facility Management AI Support Tool")
