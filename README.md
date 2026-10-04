# 🏥 HealTrip AI — مساعد الفرز الطبي الذكي

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-latest-green)
![LangGraph](https://img.shields.io/badge/LangGraph-Planned-orange)
![Gemini](https://img.shields.io/badge/Google-Gemini-red)
![Status](https://img.shields.io/badge/Status-Demo-success)

**مساعد ذكاء اصطناعي ثنائي اللغة (عربي/إنجليزي) يحلّل الأعراض، يحدد الطوارئ، ويقترح الأطباء والمستشفيات**

</div>

---

## 📋 جدول المحتويات

- [نظرة عامة](#-نظرة-عامة)
- [المميزات](#-المميزات)
- [كيف يعمل النظام](#-كيف-يعمل-النظام)
- [مخطط سير العمل](#-مخطط-سير-العمل-workflow-diagram)
- [البنية المعمارية المستقبلية (LangGraph)](#-البنية-المعمارية-المستقبلية-langgraph)
- [سيناريوهات المحادثة](#-سيناريوهات-المحادثة)
- [المتطلبات](#-المتطلبات)
- [التثبيت](#-التثبيت)
- [الإعداد](#-الإعداد)
- [قاعدة البيانات](#-قاعدة-البيانات)
- [الاستخدام](#-الاستخدام)
- [هيكل المشروع](#-هيكل-المشروع)
- [بروتوكولات الأمان](#-بروتوكولات-الأمان)
- [التقنيات المستخدمة](#-التقنيات-المستخدمة)
- [خارطة التطوير](#-خارطة-التطوير)

---

## 🎯 نظرة عامة

**HealTrip AI** هو وكيل ذكاء اصطناعي (AI Agent) متخصص في **الفرز الطبي التفاعلي**. المستخدم يصف الأعراض التي يشعر بها، والنظام يتخذ سلسلة قرارات ذكية:

1. 🔍 هل الأعراض **واضحة بما يكفي** لتحديد التخصص؟
2. 🚨 هل الأعراض **تستدعي الطوارئ**؟
3. 💬 إذا كانت الأعراض **غامضة أو عامة**، يسأل أسئلة توضيحية قبل اتخاذ أي قرار.
4. 🩺 عند وضوح الأعراض، يبحث في قاعدة البيانات عن الطبيب أو المستشفى المناسب.
5. ❌ إذا لم يجد التخصص، يعتذر بأدب ويخبر المستخدم أن التخصص غير متوفر.

النظام مبني على **محادثة متعددة الأدوار (Multi-turn Conversation)** وليس مجرد سؤال → جواب.

> 📌 **ملاحظة**: هذه النسخة هي **Demo / Proof of Concept**، تم بناؤها باستخدام LangChain. النسخة الإنتاجية الكاملة ستُبنى على **LangGraph** لإدارة أفضل لتدفّق الحالات (State Machine) والعقد (Nodes).

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
- 🔄 **Context Injection**: حقن نتائج القاعدة في الـ Prompt لمنع الاختلاق

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

## 🏗️ البنية المعمارية المستقبلية (LangGraph)

هذه النسخة الحالية (Demo) مبنية على **LangChain** فقط، حيث تُدار سلسلة القرارات عبر شروط برمجية (if/else) داخل دالة `run_healtrip_agent`.

في **النسخة الإنتاجية الكاملة**، سيتم استخدام **LangGraph** لتحويل هذا التدفّق إلى **رسم بياني للحالات (State Graph)** يوفّر:

- ✅ **إدارة واضحة للعقد (Nodes)**: كل خطوة تصبح عقدة مستقلة (`triage_node`, `clarify_node`, `search_node`, `respond_node`)
- ✅ **انتقالات شرطية (Conditional Edges)**: تحكّم دقيق بمسار المحادثة بناءً على الحالة
- ✅ **ذاكرة محادثة دائمة (Persistent State)**: حفظ حالة المستخدم عبر عدة جلسات
- ✅ **Human-in-the-Loop**: إمكانية تدخل بشري عند الحاجة (مثلًا: تأكيد طوارئ)
- ✅ **إعادة المحاولة التلقائية (Retry)**: عند فشل استدعاء أداة أو LLM
- ✅ **قابلية المراقبة (Observability)**: تتبع كامل لكل خطوة عبر LangSmith

### 📊 البنية المقترحة بـ LangGraph

```mermaid
flowchart LR
    Start([START]) --> Triage[🚨 triage_node<br/>فحص الطوارئ]
    
    Triage --> TriageRouter{urgency?}
    
    TriageRouter -->|EMERGENCY| EmergencyNode[📞 emergency_node]
    TriageRouter -->|ROUTINE| ClarityNode[🔍 clarify_node]
    
    ClarityNode --> ClarityRouter{واضح؟}
    
    ClarityRouter -->|لا| AskNode[💬 ask_questions_node]
    AskNode --> WaitNode[⏳ human_input_node]
    WaitNode --> Triage
    
    ClarityRouter -->|نعم| SpecialtyNode[🩺 determine_specialty_node]
    
    SpecialtyNode --> SearchNode[🗄️ search_db_node]
    
    SearchNode --> ResultRouter{وُجد؟}
    
    ResultRouter -->|نعم| RespondNode[✅ respond_with_doctors_node]
    ResultRouter -->|لا| ApologizeNode[🙏 apologize_node]
    
    EmergencyNode --> End([END])
    RespondNode --> End
    ApologizeNode --> End
    
    style Start fill:#e1f5ff
    style End fill:#c8e6c9
    style Triage fill:#ffebee
    style EmergencyNode fill:#ffcdd2
    style ClarityNode fill:#fff3e0
    style SearchNode fill:#f3e5f5
    style RespondNode fill:#c8e6c9
```

### 🆚 مقارنة: LangChain vs LangGraph

| المعيار | LangChain (Demo) | LangGraph (Production) |
|---------|-------------------|------------------------|
| إدارة التدفّق | شروط داخل دالة | رسم بياني صريح |
| إضافة خطوة جديدة | تعديل الكود | إضافة Node |
| الذاكرة | يدوية (`chat_history`) | مُدمجة (Checkpointer) |
| إعادة المحاولة | يدوية | مُدمجة (Retry Policy) |
| التدخل البشري | صعب | `interrupt_before` |
| قابلية المراقبة | محدودة | LangSmith مدمج |

---

## 💬 سيناريوهات الاختبار (Test Scenarios)

يحتوي النظام على **3 سيناريوهات رئيسية** للاختبار، جميعها مدعومة بالعربية والإنجليزية لضمان دقة الأداء في اللغتين.

---

### 1️⃣ سيناريو التقييم العادي والفرز الطبي
**Routine Triage Scenario**

> **الهدف**: التأكد من تركيز الـ Agent على الأعراض فقط، واستدلال التخصص الصحيح، وعرض قائمة الأطباء من قاعدة البيانات.

#### 🇪🇬 بالعربية (Arabic)

| الدور | النص |
|------|------|
| 👤 **المستخدم** | "أشعر بآلام مستمرة في ظهري وزادت في الفترة الأخيرة." |
| 👤 **رد المريض بعد سؤال الـ AI** | "الألم يقتصر على أسفل الظهر بدون تنميل، وظهر تدريجياً بسبب الجلوس الطويل في العمل." |
| 🤖 **النتيجة المتوقعة** | `urgency_level: ROUTINE` · `recommended_specialty: Orthopedics / عظام` · `doctors_list: [أطباء عظام]` |

#### 🇬🇧 In English

| Role | Text |
|------|------|
| 👤 **User** | "I have been experiencing persistent back pain that recently got worse." |
| 👤 **User Reply** | "The pain is only in my lower back with no numbness, and it started gradually due to long hours of sitting at work." |
| 🤖 **Expected Result** | `urgency_level: ROUTINE` · `recommended_specialty: Orthopedics` · `doctors_list: [Orthopedic doctors]` |

---

### 2️⃣ سيناريو الطوارئ والخط الأحمر
**Emergency / Red-Flag Scenario**

> **الهدف**: التأكد من إظهار شارة الطوارئ وتفريغ قائمة الأطباء تماماً (**100% Zero-Doctors**) في اللغتين العربية والإنجليزية.

#### 🇪🇬 بالعربية (Arabic)

| الدور | النص |
|------|------|
| 👤 **المستخدم** | "أشعر بثقل شديد وألم ضاغط في منتصف صدري مع ضيق في التنفس وتنميل في الذراع الأيسر." |
| 🤖 **النتيجة المتوقعة** | `urgency_level: EMERGENCY` · `response_text: توجيه فوري للطوارئ` · `doctors_list: []` ✅ |

#### 🇬🇧 In English

| Role | Text |
|------|------|
| 👤 **User** | "I feel severe pressure and heavy pain in the center of my chest, along with shortness of breath and numbness in my left arm." |
| 🤖 **Expected Result** | `urgency_level: EMERGENCY` · `response_text: Immediate ER referral` · `doctors_list: []` ✅ |

---

### 3️⃣ سيناريو منع الهلوسة / التخصص غير المتوفر
**Zero-Hallucination Scenario**

> **الهدف**: إثبات ربط النظام الحقيقي بـ SQL؛ فعند طلب تخصص غير مسجّل (مثل الأطفال)، يرفض اختراع أسماء ويخبر المريض بعدم التوفر.

#### 🇪🇬 بالعربية (Arabic)

| الدور | النص |
|------|------|
| 👤 **المستخدم** | "طفلي عمره 5 سنوات يعاني من ارتفاع في درجة الحرارة وسعال خفيف منذ يومين." |
| 👤 **رد المريض بعد سؤال الـ AI** | "الحرارة 38.5 والسعال خفيف ولا توجد أعراض أخرى، نعم قم بالبحث عن طبيب مناسب." |
| 🤖 **النتيجة المتوقعة** | `urgency_level: ROUTINE` · `recommended_specialty: Pediatrics / أطفال` · `doctors_list: []` · `response_text: اعتذار + التخصص غير متوفر` ✅ |

#### 🇬🇧 In English

| Role | Text |
|------|------|
| 👤 **User** | "My 5-year-old child has a fever and mild cough for the past two days." |
| 👤 **User Reply** | "The fever is 38.5°C and cough is mild with no other symptoms. Yes, please search for a doctor." |
| 🤖 **Expected Result** | `urgency_level: ROUTINE` · `recommended_specialty: Pediatrics` · `doctors_list: []` · `response_text: Apology + specialty unavailable` ✅ |

---

### 📊 ملخص السيناريوهات

| # | السيناريو | الهدف الأساسي | عدد الأطباء المتوقع | مستوى الطوارئ |
|---|-----------|---------------|---------------------|---------------|
| 1 | Routine Triage | الفرز الطبي العادي | > 0 | `ROUTINE` |
| 2 | Emergency / Red-Flag | كشف الطوارئ | **0** | `EMERGENCY` |
| 3 | Zero-Hallucination | منع الهلوسة عند غياب البيانات | **0** | `ROUTINE` |

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
langchain-google-genai 
langchain-core 
fastapi  # backend server
uvicorn # local server like nodmon
python-dotenv
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
جدول واحد فقط بدون اي علاقات لانة فقط demo
```sql
CREATE TABLE doctors (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name_ar       TEXT NOT NULL,
    name_en       TEXT NOT NULL,
    hospital_ar   TEXT NOT NULL,
    hospital_en   TEXT NOT NULL,
    specialty_ar  TEXT NOT NULL,
    specialty_en  TEXT NOT NULL,
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

> 📌 **ملاحظة**: النسخة الحالية (Demo) مبنية بـ **Python + LangChain** لأغراض العرض السريع.
> البنية الإنتاجية الكاملة ستُبنى بـ **Node.js + TypeScript** مع تطبيق  Architecture.

```text
demo_node_app_strcuture/
├── package.json
├── src/
│   ├── app.ts
│   ├── config/
│   │   └── db.ts
│   ├── controllers/
│   │   └── auth/
│   │       └── RegisterController.ts
│   ├── middlewares/
│   │   ├── error.middleware.ts
│   │   └── validation.middleware.ts
│   ├── models/
│   │   └── schema.ts
│   ├── repositories/
│   │   └── UserRepository.ts
│   ├── routes/
│   │   └── authRoutes.ts
│   ├── server.ts
│   ├── services/
│   │   └── auth/
│   │       └── RegisterService.ts
│   ├── utils/
│   │   ├── AppError.ts
│   │   └── catchAsync.ts
│   └── validations/
│       └── auth.validation.ts
└── tsconfig.json
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
- ❌ ممنوع اختلاق أسماء أطباء أو مستشفيات

### 3. حماية خصوصية المستخدم

- ❌ لا سؤال عن المدينة
- ❌ لا سؤال عن الرسوم
- ✅ التركيز على الأعراض فقط

### 4. مطابقة اللغة تلقائيًا

يرد النظام بنفس لغة المستخدم تلقائيًا (عربي/إنجليزي).

---

## 🧰 التقنيات المستخدمة

| المكوّن | التقنية |
|---------|---------|
| اللغة | Python 3.10+ |
| إطار العمل الحالي | LangChain Core |
| إطار العمل المستقبلي | **LangGraph** (للإنتاج) |
| النموذج اللغوي | Google Gemini |
| Structured Output | Pydantic v2 |
| قاعدة البيانات | SQLite 3 |
| Tool Calling | `@tool` Decorator |
| إدارة الأسرار | python-dotenv |

---

## 🗺️ خارطة التطوير

- [x] فرز طبي أساسي
- [x] Tool Calling على SQLite
- [x] Structured Output مع Pydantic
- [x] حماية من الهلوسة
- [x] أسئلة توضيحية تلقائية
- [ ] **الانتقال إلى LangGraph** لإدارة العقد والحالات
- [ ] ذاكرة محادثة دائمة (Persistent Memory via Checkpointer)
- [ ] RAG على تقارير طبية PDF
- [ ] Human-in-the-Loop للطوارئ الحرجة
- [ ] واجهة FastAPI
- [ ] واجهة  React
- [ ] نظام تسجيل وتقييم (LangSmith)

---

## ⚠️ إخلاء مسؤولية

> هذا النظام **أداة مساعدة للفرز الأولي فقط**، ولا يُعد بديلًا عن استشارة طبيب مختص.
> في الحالات الطارئة، اتصل بالإسعاف فورًا.

---

<div align="center">
⭐ Demo Project — Production version powered by **LangGraph**
</div>
