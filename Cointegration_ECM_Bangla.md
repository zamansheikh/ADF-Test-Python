# Cointegration + ECM — সহজ বাংলায় ব্যাখ্যা

> **সমস্যাটা কী ছিল:** Dataset 1-এ GDP আর Gross Capital Formation প্রথম তো বটেই,
> **দ্বিতীয় difference নেওয়ার পরও stationary হয়নি**। আরও difference নিলে
> (over-differencing) ডেটা নষ্ট হয়, ফলাফল খারাপ হয়। তাই সঠিক পদ্ধতি ব্যবহার করেছি:
> **log রূপান্তর → Cointegration test → ECM**।

চালানোর কোড: `cointegration_ecm.py` — কমান্ড: `python cointegration_ecm.py`

---

## কেন এই পদ্ধতি? (এক লাইনে)

দুইটা সিরিজ আলাদাভাবে non-stationary হতে পারে, কিন্তু যদি তারা **একসাথে চলে** (long-run
সম্পর্ক থাকে), তাহলে তাদের মধ্যে রিগ্রেশন **spurious নয় — বৈধ**। এটা পরীক্ষা করার নাম
**Cointegration test**। আর স্বল্পমেয়াদি + দীর্ঘমেয়াদি সম্পর্ক একসাথে দেখায় **ECM**।

---

## ধাপ ১ — log নিয়ে Integration order (ADF)

বিলিয়ন ডলারের সিরিজগুলোর log নিয়েছি (trend ও variance শান্ত হয়):

| সিরিজ | ফলাফল | মানে |
|---|---|---|
| log_GDP Current | **I(1)** | একবার difference নিলেই stationary |
| log_Gross Capital Formation | **I(1)** | একবার difference নিলেই stationary |
| Inflation Rate | I(0) | লেভেলেই stationary |

➡️ **মূল কথা:** log নেওয়ার পর GDP আর Gross Capital Formation দুটোই সুন্দরভাবে **I(1)**
হয়ে গেছে — যা cointegration টেস্টের জন্য ঠিক যা দরকার। (আগে level-এ 2nd diff নিয়েও
stationary হচ্ছিল না — log সেই সমস্যা মিটিয়ে দিয়েছে।)

---

## ধাপ ২ — Long-run (দীর্ঘমেয়াদি) সম্পর্ক

`log_GDP = 1.66 + 0.895 × log_GCF + 0.0013 × log_Remittance − 0.014 × log_FDI + 0.0001 × Inflation`

- **R² = 0.9994**
- **ব্যাখ্যা:** Gross Capital Formation ১% বাড়লে GDP প্রায় **০.৯০% বাড়ে** (দীর্ঘমেয়াদে)।
  এটাই সবচেয়ে শক্তিশালী চালক।

---

## ধাপ ৩ — Cointegration Test (সবচেয়ে গুরুত্বপূর্ণ)

উপরের সম্পর্কের residual (অবশিষ্ট) stationary কিনা পরীক্ষা করেছি:

| টেস্ট | মান | সিদ্ধান্ত |
|---|---|---|
| Residual-এর ADF p-value | **0.0346** (< 0.05) | ✅ Residual Stationary |
| Engle-Granger p-value | **0.0162** (< 0.05) | ✅ **COINTEGRATED** |

➡️ **মূল কথা:** GDP আর তার নিয়ামকগুলোর মধ্যে **প্রকৃত দীর্ঘমেয়াদি সম্পর্ক আছে** —
এই রিগ্রেশন **spurious নয়, বৈধ**। (আগের spurious আশঙ্কা এখানে দূর হলো ✅)

---

## ধাপ ৪ — ECM (Error Correction Model)

স্বল্পমেয়াদি পরিবর্তন + ভারসাম্যে ফিরে আসার গতি একসাথে:

| পদ | coef | p-value | মানে |
|---|---|---|---|
| d(log_GCF) | **0.8145** | **0.000** ✅ | স্বল্পমেয়াদেও GCF সবচেয়ে শক্তিশালী চালক |
| d(log_Remittance) | −0.040 | 0.259 | সিগনিফিকেন্ট নয় |
| d(log_FDI) | −0.003 | 0.626 | সিগনিফিকেন্ট নয় |
| Inflation | 0.0005 | 0.380 | সিগনিফিকেন্ট নয় |
| **ECT_lag (সংশোধন গতি)** | **−0.5245** | **0.006** ✅ | নেগেটিভ ও সিগনিফিকেন্ট |

- **ECM R² = 0.957**
- **ECT = −0.52 মানে:** ভারসাম্য থেকে সরে গেলে, প্রতি বছর সেই ব্যবধানের প্রায় **৫২%
  স্বয়ংক্রিয়ভাবে সংশোধন হয়ে যায়**। নেগেটিভ ও সিগনিফিকেন্ট হওয়া = মডেল **সঠিক ও স্থিতিশীল**।

---

## Dataset 2 প্রসঙ্গে

Dataset 2-তে **GDP Growth লেভেলেই stationary (I(0))**, তাই এখানে cointegration লাগে না —
সাধারণ stationary OLS-ই যথেষ্ট। কিন্তু সেই মডেল দুর্বল:
**R² = 0.14, Adj R² = −0.06**, কোনো ভেরিয়েবল সিগনিফিকেন্ট নয়।

---

## চূড়ান্ত সিদ্ধান্ত — কোন Dataset নেবে?

| | Dataset 1 (log + Cointegration + ECM) | Dataset 2 (stationary OLS) |
|---|---|---|
| Long-run R² | **0.9994** | — |
| Cointegrated? | ✅ হ্যাঁ (p=0.016) | প্রযোজ্য নয় |
| ECM সংশোধন গতি | **−0.52 (p=0.006)** ✅ | — |
| সিগনিফিকেন্ট চালক | Gross Capital Formation | কোনোটিই নয় |
| ফলাফল spurious? | ❌ না (প্রমাণিত বৈধ) | — |

### 👉 সুপারিশ: **Dataset 1 নাও।**
এখন এটা শুধু "ভালো ফিট" নয় — **cointegration দিয়ে প্রমাণিত যে সম্পর্কটা আসল**, এবং
ECM দেখাচ্ছে স্বল্প ও দীর্ঘমেয়াদে **Gross Capital Formation-ই GDP-র মূল চালক**, আর
সিস্টেম প্রতি বছর ভারসাম্যে ফিরে আসে। এটাই পদ্ধতিগতভাবে সঠিক ও defensible ফলাফল।

---

### সহজ সারসংক্ষেপ (এক প্যারায়)
GDP non-stationary ছিল, difference নিয়েও ঠিক হচ্ছিল না। তাই log নিয়ে দেখলাম GDP ও
Gross Capital Formation দুটোই I(1)। Cointegration test বলল এদের মধ্যে আসল দীর্ঘমেয়াদি
সম্পর্ক আছে (spurious নয়)। ECM বলল প্রতি বছর ৫২% হারে ভারসাম্যে ফিরে আসে এবং Gross
Capital Formation-ই GDP-র প্রধান নির্ধারক। **তাই Dataset 1-ই সেরা পছন্দ।**
