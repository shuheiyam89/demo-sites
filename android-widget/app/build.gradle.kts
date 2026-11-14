plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "jp.hatoru.roomwidget"
    compileSdk = 34

    defaultConfig {
        applicationId = "jp.hatoru.roomwidget"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

// 外部ライブラリは使わない（Kotlin標準ライブラリのみ。ネットワーク=HttpURLConnection、JSON=org.json）
dependencies {
}
