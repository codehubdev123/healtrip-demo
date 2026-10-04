# 🏥 HealTrip AI — مساعد الفرز الطبي الذكي

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-latest-green)
![Gemini](https://img.shields.io/badge/Google-Gemini-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

**مساعد ذكاء اصطناعي ثنائي اللغة (عربي/إنجليزي) يحلّل الأعراض، يحدد الطوارئ، ويقترح الأطباء والمستشفيات**

</div>

---

## 📋 جدول المحتويات

- [نظرة عامة](#-نظرة-عامة)
- [المميزات](#-المميزات)
- [كيف يعمل النظام](#-كيف-يعمل-النظام)
- [مخطط سير العمل](#-مخطط-سير-العمل-workflow-diagram)
- [سيناريوهات المحادثة](#-سيناريوهات-المحادثة)
- [المتطلبات](#-المتطلبات)
- [التثبيت](#-التثبيت)
- [الإعداد](#-الإعداد)
- [قاعدة البيانات](#-قاعدة-البيانات)
- [الاستخدام](#-الاستخدام)
- [هيكل المشروع](#-هيكل-المشروع)
- [بروتوكولات الأمان](#-بروتوكولات-الأمان)
- [التقنيات المستخدمة](#-التقنيات-المستخدمة)
- [المساهمة](#-المساهمة)
- [الترخيص](#-الترخيص)

---

## 🎯 نظرة عامة

**HealTrip AI** هو وكيل ذكاء اصطناعي (AI Agent) متخصص في **الفرز الطبي التفاعلي**. المستخدم يصف الأعراض التي يشعر بها، والنظام يتخذ سلسلة قرارات ذكية:

1. 🔍 هل الأعراض **واضحة بما يكفي** لتحديد التخصص؟
2. 🚨 هل الأعراض **تستدعي الطوارئ**؟
3. 💬 إذا كانت الأعراض **غامضة أو عامة**، يسأل أسئلة توضيحية قبل اتخاذ أي قرار.
4. 🩺 عند وضوح الأعراض، يبحث في قاعدة البيانات عن الطبيب أو المستشفى المناسب.
5. ❌ إذا لم يجد التخصص، يعتذر بأدب ويخبر المستخدم أن التخصص غير متوفر.

النظام مبني على **محادثة متعددة الأدوار (Multi-turn Conversation)** وليس مجرد سؤال → جواب.

---

## ✨ المميزات

- 🩺 **فرز طبي ذكي متعدد الأدوار**: يحاور المستخدم لتوضيح الأعراض
- 🚨 **كشف تلقائي للطوارئ**: بدون اقتراح أي مستشفى عند الخطر
- 🌍 **ثنائي اللغة بالكامل**: يرد بلغة المستخدم تلقائيًا
- 🛠️ **Tool Calling**: يستدعي `search_doctors_tool` للبحث في SQLite
- 📊 **مخرجات منظمة**: JSON ثابت عبر Pydantic
- 🧠 **أسئلة توضيحية ذكية**: متابعة تلقائية عند الأعراض العامة
- 🚫 **حماية كاملة من الهلوسة**: عند عدم وجود نتائج → اعتذار واضح
- 🔐 **حماية الخصوصية**: لا يسأل عن الموقع الجغرافي أو الرسوم الطبية

---

## 🔄 كيف يعمل النظام

يدخل المستخدم بوصف الأعراض، ثم يمر الطلب عبر سلسلة من الفحوصات المنطقية:

1. **فحص الطوارئ** 🚨 — إذا كانت الأعراض خطرة، رسالة إسعاف فورية.
2. **فحص الوضوح** 🔍 — إذا كانت غامضة، أسئلة توضيحية.
3. **تحديد التخصص** 🩺 — إذا كانت واضحة، تحديد التخصص المناسب.
4. **البحث في DB** 🗄️ — استدعاء أداة البحث.
5. **الاستجابة النهائية** ✅ — أطباء متاحون أو اعتذار.

---

## 📊 مخطط سير العمل (Workflow Diagram)

```mermaid
flowchart TD
    Start([👤 المستخدم يرسل الأعراض]) --> Analyze[🧠 تحليل الأعراض<br/>بواسطة LLM]
    
    Analyze --> Emergency{🚨 هل الأعراض<br/>طارئة؟}
    
    Emergency -->|نعم| EmergencyResponse[📞 رسالة طوارئ فورية<br/>توجيه لأقرب مستشفى]
    EmergencyResponse --> End1([❌ لا اقتراح أطباء])
    
    Emergency -->|لا| Clarity{🔍 هل الأعراض<br/>واضحة؟}
    
    Clarity -->|لا - غامضة| AskQuestions[💬 طرح أسئلة توضيحية<br/>المدة، المكان، الشدة]
    AskQuestions --> WaitReply[⏳ انتظار رد المستخدم]
    WaitReply --> Analyze
    
    Clarity -->|نعم - واضحة| DetermineSpecialty[🩺 تحديد التخصص<br/>الطبي المناسب]
    
    DetermineSpecialty --> SearchDB[(🗄️ البحث في<br/>SQLite DB)]
    
    SearchDB --> Found{🔎 هل وُجد<br/>أطباء؟}
    
    Found -->|نعم| ReturnDoctors[✅ إرجاع قائمة<br/>الأطباء والمستشفيات]
    ReturnDoctors --> End2([🎯 استجابة نهائية<br/>منظمة JSON])
    
    Found -->|لا| Apologize[🙏 اعتذار بأدب<br/>التخصص غير متوفر]
    Apologize --> End3([📭 doctors_list فارغة])
    
    style Start fill:#e1f5ff,stroke:#0288d1,stroke-width:2px
    style Emergency fill:#ffebee,stroke:#c62828,stroke-width:2px
    style EmergencyResponse fill:#ffcdd2,stroke:#c62828,stroke-width:2px
    style End1 fill:#ffcdd2,stroke:#c62828,stroke-width:2px
    style Clarity fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style AskQuestions fill:#fff9c4,stroke:#f9a825,stroke-width:2px
    style DetermineSpecialty fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style SearchDB fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    style ReturnDoctors fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style End2 fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style Apologize fill:#ffe0b2,stroke:#e65100,stroke-width:2px
    style End3 fill:#ffe0b2,stroke:#e65100,stroke-width:2px
```

---

## 💬 سيناريوهات المحادثة

### 🚨 سيناريو 1: طوارئ

```
👤 المستخدم: عندي ألم شديد في صدري وضيق في النفس وتنميل في ذراعي اليسرى

🤖 HealTrip AI:
   urgency_level: "EMERGENCY"
   response_text: "⚠️ هذه أعراض قد تشير إلى نوبة قلبية!
                   اتجه فورًا إلى أقرب قسم طوارئ."
   doctors_list: []
```

### 💬 سيناريو 2: أعراض غامضة

```
👤 المستخدم: عندي ألم في جسمي

🤖 HealTrip AI:
   clarifying_questions:
     - "أين تشعر بالألم بالتحديد؟"
     - "منذ متى بدأ الألم؟"
     - "هل يوجد تورم أو احمرار؟"
```

### ✅ سيناريو 3: أعراض واضحة

```
👤 المستخدم: عندي ألم في الركبة منذ 3 أيام بعد الرياضة

🤖 HealTrip AI:
   recommended_specialty: "Orthopedics"
   doctors_list: [ {اسم، مستشفى، مدينة} ]
```

### ❌ سيناريو 4: تخصص غير موجود

```
👤 المستخدم: عندي ألم في أسناني

🤖 HealTrip AI:
   response_text: "أعتذر، تخصص طب الأسنان غير متوفر حاليًا."
   doctors_list: []
```

---

## 🛠️ المتطلبات

- Python 3.10+
- مفتاح Google AI Studio (Gemini)
- SQLite 3
- RAM ≥ 4GB

---

## 📦 التثبيت

```bash
git clone https://github.com/USERNAME/healtrip-ai.git
cd healtrip-ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**requirements.txt:**

```txt
langchain-core>=0.3.0
langchain-google-genai>=2.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

---

## ⚙️ الإعداد

### `.env`

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### `config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
```

---

## 🗄️ قاعدة البيانات

```sql
CREATE TABLE doctors (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name_ar       TEXT NOT NULL,
    name_en       TEXT NOT NULL,
    hospital_ar   TEXT NOT NULL,
    hospital_en   TEXT NOT NULL,
    specialty_ar  TEXT NOT NULL,
    specialty_en  TEXT NOT NULL,
    city_ar       TEXT,
    city_en       TEXT
);
```

---

## 🚀 الاستخدام

```python
from agent import run_healtrip_agent

response = run_healtrip_agent(
    user_input="عندي ألم في الركبة منذ 3 أيام"
)

print(response["urgency_level"])         # ROUTINE
print(response["recommended_specialty"]) # Orthopedics
print(response["doctors_list"])
```

---

## 📁 هيكل المشروع

```
healtrip-ai/
├── agent.py                # المنطق الكامل للوكيل
├── config.py               # تحميل المتغيرات البيئية
├── healtrip.db             # قاعدة بيانات SQLite
├── requirements.txt
├── .env
├── README.md
├── tests/
└── data/
```

---

## 🛡️ بروتوكولات الأمان

### 1. الطوارئ لها الأولوية المطلقة

```python
if output.urgency_level == "EMERGENCY":
    output.doctors_list = []
```

### 2. لا هلوسة عند غياب البيانات

- ✅ `doctors_list = []`
- ✅ رسالة اعتذار واضحة
- ❌ ممنوع اختلاق أسماء

### 3. حماية خصوصية المستخدم

- ❌ لا سؤال عن المدينة
- ❌ لا سؤال عن الرسوم
- ✅ التركيز على الأعراض

---

## 🧰 التقنيات المستخدمة

| المكوّن | التقنية |
|---------|---------|
| اللغة | Python 3.10+ |
| إطار العمل | LangChain Core |
| النموذج اللغوي | Google Gemini |
| Structured Output | Pydantic v2 |
| قاعدة البيانات | SQLite 3 |
| Tool Calling | @tool Decorator |

---

## 🤝 المساهمة

1. Fork المشروع
2. `git checkout -b feature/NewFeature`
3. `git commit -m 'Add NewFeature'`
4. `git push origin feature/NewFeature`
5. افتح Pull Request

---

## ⚠️ إخلاء مسؤولية

> هذا النظام **أداة مساعدة للفرز الأولي فقط**، ولا يُعد بديلًا عن استشارة طبيب مختص.

---

## 📄 الترخيص

مرخّص تحت **MIT License** — راجع [LICENSE](LICENSE).

---

<div align="center">

**صُنع بـ ❤️ لخدمة الرعاية الصحية**

⭐ إذا أعجبك المشروع، لا تنسَ إعطاءه نجمة!

</div>
