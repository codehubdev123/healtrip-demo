import os
import json
import sqlite3
from typing import List, Optional
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
import config

# DOCTOR FORMATER DATA FROM DATABASE
class DoctorHospitalInfo(BaseModel):
    name_ar: str = Field(description="Doctor's name in Arabic")
    name_en: str = Field(description="Doctor's name in English")
    hospital_ar: str = Field(description="Hospital / Clinic name in Arabic")
    hospital_en: str = Field(description="Hospital / Clinic name in English")
    city_ar: str = Field(description="City in Arabic")
    city_en: str = Field(description="City in English")


# TO FORCE LLM RESPONSE IN THIS FORMAT
class HealTripTriageResponse(BaseModel):
    urgency_level: str = Field(
        description="Urgency level: 'EMERGENCY' for life-threatening/red-flags or 'ROUTINE' for stable symptoms."
    )
    recommended_specialty: Optional[str] = Field(
        default=None,
        description="Medical specialty recommended based on symptoms (e.g., Orthopedics, Cardiology).",
    )
    clarifying_questions: Optional[List[str]] = Field(
        default=None,
        description="Questions to clarify symptoms if needed. NEVER ask about location or fees.",
    )
    response_text: str = Field(
        description="Main empathetic Arabic or English response text explaining the assessment."
    )
    doctors_list: Optional[List[DoctorHospitalInfo]] = Field(
        default=None,
        description="List of matching doctors/hospitals returned from the search tool.",
    )


# TOOL TO SEARCH IN MY DEMO SQLITE DATABASE BY SPECIALTY
@tool
def search_doctors_tool(specialty: str) -> str:
    """
    Searches doctors and hospitals in the SQLite database based ONLY on medical specialty.
    """
    db_path = "healtrip.db"
    if not os.path.exists(db_path):
        return json.dumps([])

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
        SELECT name_ar, name_en, hospital_ar, hospital_en, city_ar, city_en
        FROM doctors
        WHERE (LOWER(specialty_en) LIKE LOWER(?) OR specialty_ar LIKE ?)
    """
    search_term = f"%{specialty}%"
    cursor.execute(query, (search_term, search_term))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        results.append(
            {
                "name_ar": r[0],
                "name_en": r[1],
                "hospital_ar": r[2],
                "hospital_en": r[3],
                "city_ar": r[4] if r[4] else "غير محدد",
                "city_en": r[5] if r[5] else "N/A",
            }
        )

    return json.dumps(results, ensure_ascii=False)


# SYSTEM PROMPT TO CONTROL THE LLM FROM HALLUCINATION
SYSTEM_PROMPT = """
You are "HealTrip AI", an expert bilingual (Arabic/English) medical triage assistant.

CORE RULES:
1. FOCUS ONLY ON SYMPTOMS: Ask ONLY about symptoms (pain duration, location on body, severity, associated fever/nausea/numbness, triggers).
2. NEVER ASK FOR LOCATION / CITY: Do not ask where the patient lives or where they want to see a doctor.
3. NO CONSULTATION FEES: Do not mention or ask about prices, budgets, or consultation fees.
4. DOCTOR/HOSPITAL SEARCH: Once symptoms are sufficiently clear, identify the correct specialty (e.g., Orthopedics, Cardiology) and execute `search_doctors_tool(specialty=...)` to retrieve available doctors and hospitals.

NO DATA FOUND RULE (CRITICAL & STRICT):
If `[SYSTEM DB RESULT]` shows an empty list `[]` (no doctors/hospitals found in database for the requested specialty):
- DO NOT invent, fabricate, or hallucinate any doctor names, hospital names, or cities.
- Set `doctors_list` to null or an empty list in the structured JSON output.
- Politely inform the patient in `response_text` that this specific specialty is currently not available in our network/database.
- Advise them to visit a general hospital or consult an offline emergency department if their condition worsens.

5. MATCH USER LANGUAGE: Always answer in the same language the user uses (Arabic or English).

SAFETY MANDATE (CRITICAL):
If red-flag emergency symptoms are detected (e.g., severe crushing chest pain, numbness in arm, acute right-lower abdominal pain with fever, severe shortness of breath):
1. Set urgency_level = "EMERGENCY".
2. Direct the patient immediately to the nearest ER or emergency services in `response_text`.
3. DO NOT execute `search_doctors_tool`.
4. DO NOT provide or list any doctor or hospital options.
"""


# AGENT EXCUTIO
def run_healtrip_agent(user_input: str, chat_history: Optional[List] = None) -> dict:
    if chat_history is None:
        chat_history = []

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite", # ONLY BETTER RATE LIMMTERS 
        temperature=0.0,
    )

    tools = [search_doctors_tool]
    llm_with_tools = llm.bind_tools(tools)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )

    chain = prompt | llm_with_tools
    response_msg = chain.invoke({"input": user_input, "chat_history": chat_history})

    doctors_found = None
    tool_was_called = False

    # CHECK IF TOOL WAS INVOKED
    if response_msg.tool_calls:
        for tool_call in response_msg.tool_calls:
            if tool_call["name"] == "search_doctors_tool":
                tool_was_called = True
                specialty_arg = tool_call["args"].get("specialty", "")
                raw_json = search_doctors_tool.invoke({"specialty": specialty_arg})
                doctors_found = json.loads(raw_json)

    # FINAL STEP: ENFORCE PYDANTIC STRUCTURED OUTPUT
    structured_llm = llm.with_structured_output(HealTripTriageResponse)

    # CONTEXT INJECTION FOR SECOND PASS
    context_input = user_input
    if tool_was_called:
        context_input += f"\n\n[SYSTEM DB RESULT]: Found doctors/hospitals in SQLite: {json.dumps(doctors_found, ensure_ascii=False)}"

    final_structured_response: HealTripTriageResponse = prompt | structured_llm
    output: HealTripTriageResponse = final_structured_response.invoke(
        {"input": context_input, "chat_history": chat_history}
    )

    # 🚨 STRICT SAFETY OVERRIDE (FORCE NO DOCTORS ON EMERGENCY)
    if output.urgency_level == "EMERGENCY":
        output.doctors_list = []
    elif doctors_found and len(doctors_found) > 0:
        output.doctors_list = [DoctorHospitalInfo(**doc) for doc in doctors_found]
    else:
        output.doctors_list = []

    return output.model_dump()