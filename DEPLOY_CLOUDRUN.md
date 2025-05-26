# Google Cloud Run デプロイ手順

## 前提条件
- Google Cloud SDK (gcloud) がインストールされていること
- Google Cloud プロジェクトが作成されていること
- Cloud Run API が有効化されていること
- Cloud SQL (PostgreSQL) インスタンスが作成されていること（オプション）

## 自動デプロイ設定（GitHub Actions）

### 1. GitHub Secrets の設定
GitHubリポジトリの Settings > Secrets and variables > Actions で以下のシークレットを設定：

- `GCP_PROJECT_ID`: Google Cloud プロジェクトID
- `GCP_SA_KEY`: サービスアカウントキー（JSON形式）
- `DATABASE_URL`: PostgreSQL データベースの接続URL

### 2. Google Cloud サービスアカウントの作成
```bash
# サービスアカウントを作成
gcloud iam service-accounts create github-actions \
  --display-name "GitHub Actions"

# 必要な権限を付与
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# キーファイルを生成
gcloud iam service-accounts keys create key.json \
  --iam-account github-actions@$PROJECT_ID.iam.gserviceaccount.com
```

### 3. GitHub Secretsへの設定
1. `key.json` の内容をコピーして `GCP_SA_KEY` に設定
2. Google Cloud プロジェクトIDを `GCP_PROJECT_ID` に設定
3. データベース接続URLを `DATABASE_URL` に設定

### 4. 自動デプロイの動作
- `main` ブランチにpushまたはプルリクエストがマージされると自動的にCloud Runにデプロイされます

## 手動デプロイ手順

### 1. Google Cloud プロジェクトの設定
```bash
# プロジェクトを設定
gcloud config set project YOUR_PROJECT_ID

# Cloud Run API を有効化
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2. 簡単デプロイ（推奨）
```bash
# ソースコードから直接デプロイ
gcloud run deploy flask-markdown-memo \
  --source . \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL="your_database_url_here"
```

### 3. Dockerイメージのビルドとプッシュ（手動の場合）
```bash
# Container Registry に認証
gcloud auth configure-docker

# Dockerイメージをビルド
docker build -t gcr.io/YOUR_PROJECT_ID/flask-markdown-memo .

# イメージをプッシュ
docker push gcr.io/YOUR_PROJECT_ID/flask-markdown-memo
```

### 4. Cloud Run にデプロイ（手動の場合）
```bash
# Cloud Run にデプロイ
gcloud run deploy flask-markdown-memo \
  --image gcr.io/YOUR_PROJECT_ID/flask-markdown-memo \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL="your_database_url_here"
```

### 5. Cloud SQL を使用する場合
```bash
# Cloud SQL インスタンスを作成
gcloud sql instances create memo-db \
  --database-version POSTGRES_14 \
  --tier db-f1-micro \
  --region asia-northeast1

# データベースを作成
gcloud sql databases create memo_app --instance memo-db

# Cloud Run からCloud SQL に接続
gcloud run deploy flask-markdown-memo \
  --image gcr.io/YOUR_PROJECT_ID/flask-markdown-memo \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --add-cloudsql-instances YOUR_PROJECT_ID:asia-northeast1:memo-db \
  --set-env-vars DATABASE_URL="postgresql://username:password@/memo_app?host=/cloudsql/YOUR_PROJECT_ID:asia-northeast1:memo-db"
```

## 環境変数の設定
- `DATABASE_URL`: PostgreSQL データベースの接続URL
- `PORT`: ポート番号（Cloud Run では自動設定されるため通常不要）

## 注意事項
- YOUR_PROJECT_ID を実際のGoogle Cloud プロジェクトIDに置き換えてください
- データベースのユーザー名・パスワードを適切に設定してください
- Cloud SQL を使用しない場合は、外部のPostgreSQLサービスを使用してください
