# TrendPulse - System Flowcharts

## 1. System Architecture Overview

```mermaid
flowchart TB
    subgraph CLIENT["🖥️ Frontend (Next.js)"]
        UI[Web Application]
        AUTH_UI[Auth Pages]
        DASH[Dashboard]
        SEARCH[Search & Filters]
        DETAIL[Trend Detail]
        FAV[Favorites]
        ALERTS_UI[Alerts Management]
    end

    subgraph API["⚡ Backend API (FastAPI)"]
        GATEWAY[API Gateway]
        AUTH_SVC[Auth Service]
        TREND_SVC[Trends Service]
        FAV_SVC[Favorites Service]
        ALERT_SVC[Alerts Service]
        EXPORT_SVC[Export Service]
        SCORE_ENGINE[Scoring Engine]
    end

    subgraph WORKERS["⚙️ Background Workers (Celery)"]
        COLLECTOR[Data Collector]
        SCORER[Score Calculator]
        NOTIFIER[Notification Worker]
        EXPORTER[Export Worker]
        CACHE_WORKER[Cache Updater]
    end

    subgraph DATA_SOURCES["🌐 External APIs"]
        GOOGLE[Google Trends<br/>Pytrends]
        YOUTUBE[YouTube API v3]
        REDDIT[Reddit API]
    end

    subgraph STORAGE["💾 Data Storage"]
        POSTGRES[(PostgreSQL)]
        REDIS[(Redis Cache)]
    end

    subgraph NOTIFICATIONS["📬 Notification Services"]
        EMAIL[Email<br/>Resend/SendGrid]
        TELEGRAM[Telegram Bot]
        PUSH[Web Push]
    end

    UI --> GATEWAY
    AUTH_UI --> AUTH_SVC
    DASH --> TREND_SVC
    SEARCH --> TREND_SVC
    DETAIL --> TREND_SVC
    FAV --> FAV_SVC
    ALERTS_UI --> ALERT_SVC

    GATEWAY --> AUTH_SVC
    GATEWAY --> TREND_SVC
    GATEWAY --> FAV_SVC
    GATEWAY --> ALERT_SVC
    GATEWAY --> EXPORT_SVC

    TREND_SVC --> SCORE_ENGINE
    TREND_SVC --> POSTGRES
    TREND_SVC --> REDIS

    AUTH_SVC --> POSTGRES
    AUTH_SVC --> REDIS

    FAV_SVC --> POSTGRES
    ALERT_SVC --> POSTGRES
    EXPORT_SVC --> POSTGRES

    COLLECTOR --> GOOGLE
    COLLECTOR --> YOUTUBE
    COLLECTOR --> REDDIT
    COLLECTOR --> POSTGRES
    COLLECTOR --> REDIS

    SCORER --> POSTGRES
    SCORER --> SCORE_ENGINE

    NOTIFIER --> EMAIL
    NOTIFIER --> TELEGRAM
    NOTIFIER --> PUSH

    EXPORTER --> POSTGRES
    CACHE_WORKER --> REDIS
    CACHE_WORKER --> POSTGRES
```

---

## 2. User Authentication Flow

```mermaid
flowchart TD
    START([User Visits App]) --> CHECK{Has Session?}
    
    CHECK -->|Yes| VALIDATE[Validate JWT Token]
    CHECK -->|No| LOGIN_PAGE[Show Login Page]
    
    VALIDATE -->|Valid| DASHBOARD[Go to Dashboard]
    VALIDATE -->|Expired| REFRESH[Try Refresh Token]
    VALIDATE -->|Invalid| LOGIN_PAGE
    
    REFRESH -->|Success| DASHBOARD
    REFRESH -->|Fail| LOGIN_PAGE
    
    LOGIN_PAGE --> CHOICE{User Choice}
    
    CHOICE -->|Login| LOGIN_FORM[Email + Password]
    CHOICE -->|Register| REGISTER_FORM[Registration Form]
    CHOICE -->|OAuth| OAUTH[Google/GitHub OAuth]
    CHOICE -->|Forgot| FORGOT[Forgot Password]
    
    LOGIN_FORM --> VERIFY_CREDS{Verify Credentials}
    VERIFY_CREDS -->|Valid| CREATE_SESSION[Create Session + JWT]
    VERIFY_CREDS -->|Invalid| ERROR[Show Error]
    ERROR --> LOGIN_PAGE
    
    REGISTER_FORM --> VALIDATE_INPUT{Validate Input}
    VALIDATE_INPUT -->|Valid| CREATE_USER[Create User Account]
    VALIDATE_INPUT -->|Invalid| REG_ERROR[Show Validation Error]
    REG_ERROR --> REGISTER_FORM
    
    CREATE_USER --> SEND_VERIFY[Send Verification Email]
    SEND_VERIFY --> VERIFY_NOTICE[Show Verify Email Notice]
    
    OAUTH --> OAUTH_PROVIDER[Redirect to Provider]
    OAUTH_PROVIDER --> OAUTH_CALLBACK[OAuth Callback]
    OAUTH_CALLBACK --> FIND_USER{User Exists?}
    FIND_USER -->|Yes| CREATE_SESSION
    FIND_USER -->|No| CREATE_OAUTH_USER[Create OAuth User]
    CREATE_OAUTH_USER --> CREATE_SESSION
    
    CREATE_SESSION --> STORE_TOKEN[Store in Cookie/LocalStorage]
    STORE_TOKEN --> DASHBOARD
    
    FORGOT --> SEND_RESET[Send Reset Email]
    SEND_RESET --> RESET_LINK[User Clicks Link]
    RESET_LINK --> NEW_PASSWORD[Enter New Password]
    NEW_PASSWORD --> UPDATE_PASSWORD[Update Password]
    UPDATE_PASSWORD --> LOGIN_PAGE
```

---

## 3. Data Collection Pipeline

```mermaid
flowchart TD
    subgraph SCHEDULER["⏰ Scheduler"]
        CRON[Cron Job<br/>Every 6 Hours]
    end

    subgraph COLLECTION["📥 Data Collection"]
        CRON --> DISPATCH[Dispatch Collection Jobs]
        
        DISPATCH --> GT_JOB[Google Trends Job]
        DISPATCH --> YT_JOB[YouTube Job]
        DISPATCH --> RD_JOB[Reddit Job]
        
        GT_JOB --> GT_CHECK{Rate Limit OK?}
        GT_CHECK -->|Yes| GT_FETCH[Fetch Trending Topics]
        GT_CHECK -->|No| GT_WAIT[Wait & Retry]
        GT_WAIT --> GT_CHECK
        
        YT_JOB --> YT_CHECK{Quota Available?}
        YT_CHECK -->|Yes| YT_FETCH[Fetch Trending Videos]
        YT_CHECK -->|No| YT_SKIP[Skip Until Tomorrow]
        
        RD_JOB --> RD_CHECK{Rate Limit OK?}
        RD_CHECK -->|Yes| RD_FETCH[Fetch Hot Posts]
        RD_CHECK -->|No| RD_WAIT[Wait 60s & Retry]
        RD_WAIT --> RD_CHECK
    end

    subgraph PROCESSING["⚙️ Data Processing"]
        GT_FETCH --> NORMALIZE[Normalize Keywords]
        YT_FETCH --> NORMALIZE
        RD_FETCH --> NORMALIZE
        
        NORMALIZE --> DEDUPE[Deduplicate]
        DEDUPE --> CATEGORIZE[Auto-Categorize by Niche]
        CATEGORIZE --> MERGE[Merge Multi-Source Data]
    end

    subgraph SCORING["📊 Scoring"]
        MERGE --> CALC_GROWTH[Calculate Growth Rate]
        CALC_GROWTH --> CALC_VOLUME[Calculate Volume Level]
        CALC_VOLUME --> CALC_CONSIST[Calculate Consistency]
        CALC_CONSIST --> CALC_MULTI[Calculate Multi-Platform Score]
        CALC_MULTI --> CALC_FRESH[Calculate Freshness]
        CALC_FRESH --> FINAL_SCORE[Compute Final Score<br/>Weighted Average]
    end

    subgraph STORAGE["💾 Storage"]
        FINAL_SCORE --> UPSERT[Upsert Trend Record]
        UPSERT --> SNAPSHOT[Create Daily Snapshot]
        SNAPSHOT --> UPDATE_CACHE[Update Redis Cache]
        UPDATE_CACHE --> TRIGGER_ALERTS[Check Alert Rules]
    end

    subgraph ALERTS["🔔 Alert Processing"]
        TRIGGER_ALERTS --> MATCH{Matches Any Alert?}
        MATCH -->|Yes| QUEUE_NOTIF[Queue Notification]
        MATCH -->|No| DONE([Collection Complete])
        QUEUE_NOTIF --> DONE
    end
```

---

## 4. Scoring Algorithm Flow

```mermaid
flowchart TD
    START([Trend Data Input]) --> EXTRACT[Extract Raw Metrics]
    
    EXTRACT --> G_RATE[Growth Rate<br/>% Change 30 Days]
    EXTRACT --> VOLUME[Search Volume<br/>Relative Index]
    EXTRACT --> CONSIST[Consistency<br/>Std Deviation]
    EXTRACT --> MULTI[Multi-Platform<br/>Source Count]
    EXTRACT --> FRESH[Freshness<br/>Days Since First Seen]
    
    G_RATE --> NORM_G[Normalize 0-100]
    VOLUME --> NORM_V[Normalize 0-100]
    CONSIST --> NORM_C[Normalize 0-100]
    MULTI --> NORM_M[Normalize 0-100]
    FRESH --> NORM_F[Normalize 0-100]
    
    NORM_G --> WEIGHT_G["× 0.35 (35%)"]
    NORM_V --> WEIGHT_V["× 0.25 (25%)"]
    NORM_C --> WEIGHT_C["× 0.20 (20%)"]
    NORM_M --> WEIGHT_M["× 0.15 (15%)"]
    NORM_F --> WEIGHT_F["× 0.05 (5%)"]
    
    WEIGHT_G --> SUM[Sum Weighted Scores]
    WEIGHT_V --> SUM
    WEIGHT_C --> SUM
    WEIGHT_M --> SUM
    WEIGHT_F --> SUM
    
    SUM --> ROUND[Round to Integer]
    ROUND --> CLAMP[Clamp 0-100]
    
    CLAMP --> CLASSIFY{Score Range}
    
    CLASSIFY -->|80-100| HOT[🔥 Hot Opportunity]
    CLASSIFY -->|60-79| STRONG[💪 Strong Potential]
    CLASSIFY -->|40-59| WATCH[👀 Worth Watching]
    CLASSIFY -->|20-39| EARLY[🌱 Early Signal]
    CLASSIFY -->|0-19| LOW[⬇️ Low Priority]
    
    HOT --> OUTPUT([Final Score + Label])
    STRONG --> OUTPUT
    WATCH --> OUTPUT
    EARLY --> OUTPUT
    LOW --> OUTPUT
```

---

## 5. User Search & Filter Flow

```mermaid
flowchart TD
    START([User Opens Dashboard]) --> LOAD_GLOBAL[Load Global Trending<br/>From Cache]
    
    LOAD_GLOBAL --> DISPLAY[Display Trend Cards]
    DISPLAY --> USER_ACTION{User Action}
    
    USER_ACTION -->|Apply Filter| FILTER_PANEL[Open Filter Panel]
    USER_ACTION -->|Search Keyword| SEARCH_BOX[Enter Search Term]
    USER_ACTION -->|Click Trend| DETAIL_VIEW[Open Trend Detail]
    USER_ACTION -->|Save Favorite| SAVE_FAV[Add to Favorites]
    USER_ACTION -->|Set Alert| CREATE_ALERT[Create Alert]
    
    FILTER_PANEL --> SELECT_FILTERS[Select Filters]
    SELECT_FILTERS --> F_NICHE[Niche Category]
    SELECT_FILTERS --> F_REGION[Region]
    SELECT_FILTERS --> F_LANG[Language]
    SELECT_FILTERS --> F_TIME[Time Range]
    SELECT_FILTERS --> F_SCORE[Min Score]
    SELECT_FILTERS --> F_SOURCE[Data Source]
    
    F_NICHE --> BUILD_QUERY[Build Query Params]
    F_REGION --> BUILD_QUERY
    F_LANG --> BUILD_QUERY
    F_TIME --> BUILD_QUERY
    F_SCORE --> BUILD_QUERY
    F_SOURCE --> BUILD_QUERY
    
    SEARCH_BOX --> BUILD_QUERY
    
    BUILD_QUERY --> CHECK_CACHE{In Cache?}
    CHECK_CACHE -->|Yes| RETURN_CACHED[Return Cached Results]
    CHECK_CACHE -->|No| QUERY_DB[Query Database]
    
    QUERY_DB --> APPLY_FILTERS[Apply All Filters]
    APPLY_FILTERS --> SORT_RESULTS[Sort by Score DESC]
    SORT_RESULTS --> PAGINATE[Paginate Results]
    PAGINATE --> CACHE_RESULTS[Cache for 5 Min]
    CACHE_RESULTS --> RETURN_RESULTS[Return Results]
    
    RETURN_CACHED --> UPDATE_UI[Update UI]
    RETURN_RESULTS --> UPDATE_UI
    
    UPDATE_UI --> SAVE_HISTORY[Save Search to History]
    SAVE_HISTORY --> DISPLAY
    
    DETAIL_VIEW --> FETCH_DETAIL[Fetch Full Trend Data]
    FETCH_DETAIL --> FETCH_HISTORY[Fetch Historical Snapshots]
    FETCH_HISTORY --> FETCH_RELATED[Fetch Related Topics]
    FETCH_RELATED --> RENDER_DETAIL[Render Detail Page]
    
    SAVE_FAV --> CHECK_AUTH{Authenticated?}
    CHECK_AUTH -->|Yes| INSERT_FAV[Insert Favorite Record]
    CHECK_AUTH -->|No| PROMPT_LOGIN[Prompt Login]
    INSERT_FAV --> SHOW_SUCCESS[Show Success Toast]
    
    CREATE_ALERT --> ALERT_FORM[Show Alert Form]
    ALERT_FORM --> SAVE_ALERT[Save Alert Config]
    SAVE_ALERT --> CONFIRM_ALERT[Confirm Alert Created]
```

---

## 6. Alert & Notification Flow

```mermaid
flowchart TD
    subgraph TRIGGERS["🎯 Alert Triggers"]
        NEW_TREND[New Trend Discovered]
        SCORE_CHANGE[Score Changed]
        EXPLOSION[Growth > 200% in 24h]
    end

    subgraph MATCHING["🔍 Alert Matching"]
        NEW_TREND --> LOAD_ALERTS[Load Active Alerts]
        SCORE_CHANGE --> LOAD_ALERTS
        EXPLOSION --> LOAD_ALERTS
        
        LOAD_ALERTS --> LOOP{For Each Alert}
        
        LOOP --> CHECK_TYPE{Alert Type}
        
        CHECK_TYPE -->|Keyword| MATCH_KW{Keyword Matches?}
        CHECK_TYPE -->|Niche| MATCH_NICHE{Niche Matches?}
        CHECK_TYPE -->|Score| MATCH_SCORE{Score >= Threshold?}
        CHECK_TYPE -->|Explosion| MATCH_EXPLODE{Growth > 200%?}
        
        MATCH_KW -->|Yes| QUEUE[Add to Notification Queue]
        MATCH_NICHE -->|Yes| QUEUE
        MATCH_SCORE -->|Yes| QUEUE
        MATCH_EXPLODE -->|Yes| QUEUE
        
        MATCH_KW -->|No| NEXT[Next Alert]
        MATCH_NICHE -->|No| NEXT
        MATCH_SCORE -->|No| NEXT
        MATCH_EXPLODE -->|No| NEXT
        
        NEXT --> LOOP
    end

    subgraph DELIVERY["📬 Notification Delivery"]
        QUEUE --> CHECK_CHANNELS[Get User Channels]
        CHECK_CHANNELS --> HAS_EMAIL{Email Enabled?}
        CHECK_CHANNELS --> HAS_TELEGRAM{Telegram Enabled?}
        CHECK_CHANNELS --> HAS_PUSH{Push Enabled?}
        CHECK_CHANNELS --> HAS_INAPP{In-App Enabled?}
        
        HAS_EMAIL -->|Yes| SEND_EMAIL[Send Email]
        HAS_TELEGRAM -->|Yes| SEND_TELEGRAM[Send Telegram]
        HAS_PUSH -->|Yes| SEND_PUSH[Send Web Push]
        HAS_INAPP -->|Yes| SAVE_NOTIF[Save to Notifications Table]
        
        SEND_EMAIL --> LOG[Log Delivery]
        SEND_TELEGRAM --> LOG
        SEND_PUSH --> LOG
        SAVE_NOTIF --> LOG
        
        LOG --> UPDATE_ALERT[Update Alert Last Triggered]
    end

    subgraph DIGEST["📋 Digest Mode"]
        QUEUE --> CHECK_FREQ{Frequency Setting}
        CHECK_FREQ -->|Instant| CHECK_CHANNELS
        CHECK_FREQ -->|Daily| STORE_DIGEST[Store for Daily Digest]
        CHECK_FREQ -->|Weekly| STORE_WEEKLY[Store for Weekly Digest]
        
        STORE_DIGEST --> DAILY_JOB[Daily Cron Job]
        STORE_WEEKLY --> WEEKLY_JOB[Weekly Cron Job]
        
        DAILY_JOB --> COMPILE_DIGEST[Compile Digest Email]
        WEEKLY_JOB --> COMPILE_DIGEST
        
        COMPILE_DIGEST --> SEND_EMAIL
    end
```

---

## 7. Export Flow

```mermaid
flowchart TD
    START([User Requests Export]) --> SELECT_TYPE{Export Type}
    
    SELECT_TYPE -->|Current View| EXPORT_VIEW[Export Filtered Trends]
    SELECT_TYPE -->|Favorites| EXPORT_FAV[Export Favorites]
    SELECT_TYPE -->|Single Trend| EXPORT_SINGLE[Export Trend Report]
    
    EXPORT_VIEW --> SELECT_FORMAT[Select Format]
    EXPORT_FAV --> SELECT_FORMAT
    EXPORT_SINGLE --> SELECT_FORMAT
    
    SELECT_FORMAT --> FORMAT{Format Choice}
    
    FORMAT -->|CSV| GEN_CSV[Generate CSV]
    FORMAT -->|JSON| GEN_JSON[Generate JSON]
    FORMAT -->|PDF| GEN_PDF[Generate PDF Report]
    FORMAT -->|XLSX| GEN_XLSX[Generate Excel]
    FORMAT -->|PNG/SVG| GEN_IMAGE[Generate Chart Image]
    
    GEN_CSV --> CREATE_JOB[Create Export Job]
    GEN_JSON --> CREATE_JOB
    GEN_PDF --> CREATE_JOB
    GEN_XLSX --> CREATE_JOB
    GEN_IMAGE --> CREATE_JOB
    
    CREATE_JOB --> QUEUE_WORKER[Queue to Export Worker]
    QUEUE_WORKER --> SHOW_PROGRESS[Show Progress UI]
    
    QUEUE_WORKER --> WORKER_PROCESS[Worker Processes Job]
    WORKER_PROCESS --> FETCH_DATA[Fetch Required Data]
    FETCH_DATA --> TRANSFORM[Transform to Format]
    TRANSFORM --> GENERATE_FILE[Generate File]
    GENERATE_FILE --> UPLOAD_STORAGE[Upload to Storage]
    UPLOAD_STORAGE --> UPDATE_STATUS[Update Job Status]
    
    UPDATE_STATUS --> NOTIFY_USER[Notify User]
    NOTIFY_USER --> PROVIDE_LINK[Provide Download Link]
    
    SHOW_PROGRESS --> POLL_STATUS[Poll Job Status]
    POLL_STATUS --> CHECK_DONE{Completed?}
    CHECK_DONE -->|No| POLL_STATUS
    CHECK_DONE -->|Yes| SHOW_DOWNLOAD[Show Download Button]
    
    PROVIDE_LINK --> USER_DOWNLOAD[User Downloads File]
    SHOW_DOWNLOAD --> USER_DOWNLOAD
    
    USER_DOWNLOAD --> SET_EXPIRY[File Expires in 24h]
```

---

## 8. Application Pages Flow

```mermaid
flowchart TD
    subgraph PUBLIC["🌐 Public Pages"]
        LANDING[Landing Page]
        LOGIN[Login]
        REGISTER[Register]
        FORGOT[Forgot Password]
        RESET[Reset Password]
        VERIFY[Verify Email]
    end

    subgraph PROTECTED["🔒 Protected Pages (Require Auth)"]
        DASHBOARD[Dashboard<br/>Global Trending]
        SEARCH_PAGE[Search Results]
        TREND_DETAIL[Trend Detail]
        FAVORITES_PAGE[Favorites]
        ALERTS_PAGE[Alerts]
        HISTORY_PAGE[Search History]
        SETTINGS[Settings]
        PROFILE[Profile]
    end

    subgraph SETTINGS_SUB["⚙️ Settings Subpages"]
        SETTINGS --> PROFILE_SET[Profile Settings]
        SETTINGS --> NOTIF_SET[Notification Settings]
        SETTINGS --> LANG_SET[Language Settings]
        SETTINGS --> EXPORT_SET[Export Preferences]
    end

    LANDING -->|CTA| REGISTER
    LANDING -->|Login| LOGIN
    
    LOGIN -->|Success| DASHBOARD
    REGISTER -->|Success| VERIFY
    VERIFY -->|Verified| DASHBOARD
    FORGOT --> RESET
    RESET -->|Success| LOGIN
    
    DASHBOARD -->|Search| SEARCH_PAGE
    DASHBOARD -->|Click Trend| TREND_DETAIL
    DASHBOARD -->|Nav| FAVORITES_PAGE
    DASHBOARD -->|Nav| ALERTS_PAGE
    DASHBOARD -->|Nav| HISTORY_PAGE
    DASHBOARD -->|Nav| SETTINGS
    
    SEARCH_PAGE -->|Click Trend| TREND_DETAIL
    FAVORITES_PAGE -->|Click Trend| TREND_DETAIL
    HISTORY_PAGE -->|Re-run Search| SEARCH_PAGE
    
    TREND_DETAIL -->|Save| FAVORITES_PAGE
    TREND_DETAIL -->|Create Alert| ALERTS_PAGE
```

---

## 9. Database Entity Relationship

```mermaid
erDiagram
    USER ||--o{ SESSION : has
    USER ||--o{ FAVORITE : has
    USER ||--o{ FOLDER : has
    USER ||--o{ ALERT : has
    USER ||--o{ ALERT_LOG : has
    USER ||--o{ SEARCH_HISTORY : has
    USER ||--o{ NOTIFICATION : has
    USER ||--o{ EXPORT : has
    
    TREND ||--o{ TREND_SNAPSHOT : has
    TREND ||--o{ TREND_SOURCE_DATA : has
    TREND ||--o{ FAVORITE : saved_in
    TREND ||--o{ ALERT_LOG : triggers
    
    FOLDER ||--o{ FAVORITE : contains
    ALERT ||--o{ ALERT_LOG : generates
    
    USER {
        uuid id PK
        string email UK
        string password_hash
        string name
        enum preferred_language
        boolean email_verified
        timestamp created_at
    }
    
    TREND {
        uuid id PK
        string keyword
        string normalized_keyword
        enum category
        int opportunity_score
        decimal growth_rate
        enum volume_level
        enum direction
        json sparkline_data
        json related_topics
        string region
        timestamp last_updated
    }
    
    TREND_SNAPSHOT {
        uuid id PK
        uuid trend_id FK
        int score
        decimal growth_rate
        date snapshot_date
    }
    
    FAVORITE {
        uuid id PK
        uuid user_id FK
        uuid trend_id FK
        uuid folder_id FK
        text notes
        int score_at_save
    }
    
    FOLDER {
        uuid id PK
        uuid user_id FK
        string name
        string color
    }
    
    ALERT {
        uuid id PK
        uuid user_id FK
        enum alert_type
        string keyword
        enum niche
        int threshold
        boolean is_active
    }
    
    ALERT_LOG {
        uuid id PK
        uuid alert_id FK
        uuid user_id FK
        uuid trend_id FK
        string message
        timestamp triggered_at
    }
```

---

## 10. Deployment Architecture

```mermaid
flowchart TB
    subgraph USERS["👥 Users"]
        BROWSER[Web Browser]
        MOBILE[Mobile Browser]
    end

    subgraph CDN["🌍 CDN (Vercel Edge)"]
        EDGE[Edge Network]
        STATIC[Static Assets]
    end

    subgraph FRONTEND["🖥️ Frontend (Vercel)"]
        NEXTJS[Next.js App]
        SSR[Server-Side Rendering]
        API_ROUTES[API Routes]
    end

    subgraph BACKEND["⚡ Backend (Railway)"]
        FASTAPI[FastAPI Server]
        CELERY_WORKER[Celery Workers]
        CELERY_BEAT[Celery Beat<br/>Scheduler]
    end

    subgraph DATABASE["💾 Database (Supabase/Neon)"]
        POSTGRES[(PostgreSQL)]
    end

    subgraph CACHE["⚡ Cache (Upstash)"]
        REDIS[(Redis)]
    end

    subgraph EXTERNAL["🌐 External Services"]
        RESEND[Resend<br/>Email]
        TELEGRAM_API[Telegram API]
        GOOGLE_TRENDS[Google Trends]
        YOUTUBE_API[YouTube API]
        REDDIT_API[Reddit API]
    end

    BROWSER --> EDGE
    MOBILE --> EDGE
    
    EDGE --> STATIC
    EDGE --> NEXTJS
    
    NEXTJS --> SSR
    NEXTJS --> API_ROUTES
    API_ROUTES --> FASTAPI
    
    FASTAPI --> POSTGRES
    FASTAPI --> REDIS
    
    CELERY_WORKER --> POSTGRES
    CELERY_WORKER --> REDIS
    CELERY_WORKER --> GOOGLE_TRENDS
    CELERY_WORKER --> YOUTUBE_API
    CELERY_WORKER --> REDDIT_API
    CELERY_WORKER --> RESEND
    CELERY_WORKER --> TELEGRAM_API
    
    CELERY_BEAT --> CELERY_WORKER
```

---

## Quick Reference

| Flowchart | Description |
|-----------|-------------|
| 1. System Architecture | High-level system components and connections |
| 2. Authentication | Login, register, OAuth, password reset flows |
| 3. Data Collection | How trends are collected from APIs |
| 4. Scoring Algorithm | How opportunity score is calculated |
| 5. Search & Filter | User search and filtering workflow |
| 6. Alerts | Alert matching and notification delivery |
| 7. Export | Export generation workflow |
| 8. Pages Flow | Application navigation structure |
| 9. ER Diagram | Database entity relationships |
| 10. Deployment | Cloud infrastructure architecture |
