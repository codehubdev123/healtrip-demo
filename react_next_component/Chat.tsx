"use client";

import React, { useState, useRef, useEffect } from "react";

interface Response {
  urgency_level: string;
  recommended_specialty?: string;
  clarifying_questions?: string[];
  response_text: string;
  doctors_list?: Array<{
    name_ar: string;
    name_en: string;
    hospital_ar: string;
    hospital_en: string;
    city_ar: string;
    city_en: string;
  }>;
}

interface Message {
  sender: "user" | "bot";
  data: string | Response;
}

export default function Chat() {
  const [lang, setLang] = useState<"ar" | "en">("ar");

  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "bot",
      data:
        lang === "ar"
          ? "مرحباً بك في مساعد HealTrip الطبي. كيف يمكنني مساعدتك اليوم؟"
          : "Hello! Welcome to HealTrip Medical Assistant. How can I help you today?",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleLanguageToggle = (selectedLang: "ar" | "en") => {
    if (selectedLang === lang) return;
    setLang(selectedLang);
    setMessages([
      {
        sender: "bot",
        data:
          selectedLang === "ar"
            ? "مرحباً بك في مساعد HealTrip الطبي. كيف يمكنني مساعدتك اليوم؟"
            : "Hello! Welcome to HealTrip Medical Assistant. How can I help you today?",
      },
    ]);
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput("");

    const historyPayload = messages.map((m) => ({
      role: m.sender === "user" ? "user" : "assistant",
      content: typeof m.data === "string" ? m.data : m.data.response_text,
    }));

    const newHistory: Message[] = [
      ...messages,
      { sender: "user", data: userMsg },
    ];
    setMessages(newHistory);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_input: userMsg,
          chat_history: historyPayload,
        }),
      });

      if (!res.ok) {
        throw new Error(`Server returned status ${res.status}`);
      }

      const structuredData: Response = await res.json();
      setMessages([...newHistory, { sender: "bot", data: structuredData }]);
    } catch (err) {
      setMessages([
        ...newHistory,
        {
          sender: "bot",
          data:
            lang === "ar"
              ? "تعذر الاتصال بالسيرفر. يرجى التأكد من تشغيل FastAPI."
              : "Error connecting to server. Please ensure FastAPI is running.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="max-w-2xl mx-auto my-8 p-4 border rounded-2xl shadow-lg bg-white flex flex-col h-[650px]"
      dir={lang === "ar" ? "rtl" : "ltr"}
    >
      <div className="border-b pb-3 mb-3 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-blue-600">
            HealTrip AI Assistant
          </h2>
          <p className="text-xs text-gray-500">
            {lang === "ar"
              ? "المساعد الطبي الرقمي لاتخاذ القرار"
              : "AI Patient Triage & Decision Assistant"}
          </p>
        </div>

        <div className="flex bg-gray-100 p-1 rounded-xl border border-gray-200">
          <button
            onClick={() => handleLanguageToggle("ar")}
            className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
              lang === "ar"
                ? "bg-blue-600 text-white shadow-sm"
                : "text-gray-600 hover:text-black"
            }`}
          >
            عربي
          </button>
          <button
            onClick={() => handleLanguageToggle("en")}
            className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
              lang === "en"
                ? "bg-blue-600 text-white shadow-sm"
                : "text-gray-600 hover:text-black"
            }`}
          >
            English
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 p-2">
        {messages.map((m, idx) => {
          const isUser = m.sender === "user";
          const isString = typeof m.data === "string";
          const res = isString ? null : (m.data as Response);

          return (
            <div
              key={idx}
              className={`flex ${isUser ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] p-3.5 rounded-2xl text-lg whitespace-pre-wrap ${
                  isUser
                    ? "bg-blue-600 text-white rounded-br-none"
                    : `bg-gray-100 text-gray-800 rounded-bl-none border border-gray-200 ${
                        res?.urgency_level === "EMERGENCY"
                          ? "bg-red-100 text-red-900 border-red-300"
                          : ""
                      }`
                }`}
              >
                {isString ? (
                  (m.data as string)
                ) : (
                  <div className="space-y-2">
                    {res?.urgency_level === "EMERGENCY" && (
                      <span className="inline-block bg-red-600 text-white text-xs px-2.5 py-1 rounded-md font-bold mb-1 animate-bounce">
                        {lang === "ar"
                          ? "🚨 حالة طوارئ عاجلة"
                          : "🚨 EMERGENCY MEDICAL ALERT"}
                      </span>
                    )}

                    <p
                      className={`leading-relaxed ${res?.urgency_level === "EMERGENCY" ? "bg-red-100" : ""}`}
                    >
                      {res?.response_text}
                    </p>

                    {res?.doctors_list && res.doctors_list.length > 0 && (
                      <div className="mt-3 pt-2 border-t border-gray-300 space-y-2">
                        <p className="font-semibold text-xs text-blue-700">
                          {lang === "ar"
                            ? "الخيارات الطبية والمستشفيات المتاحة:"
                            : "Recommended Options & Hospitals:"}
                        </p>
                        <ul className="space-y-2 text-xs">
                          {res.doctors_list.map((doc, dIdx) => (
                            <li
                              key={dIdx}
                              className="bg-white p-2.5 rounded-xl border border-gray-200 shadow-sm"
                            >
                              <div className="font-bold text-gray-900">
                                {lang === "ar" ? doc.name_ar : doc.name_en}
                              </div>
                              <div className="text-gray-600 text-[11px] mt-0.5">
                                {lang === "ar"
                                  ? doc.hospital_ar
                                  : doc.hospital_en}
                              </div>
                              <div className="text-blue-600 font-medium text-[11px] mt-1">
                                <span>
                                  {lang === "ar" ? "المدينة:" : "City:"}{" "}
                                  {lang === "ar" ? doc.city_ar : doc.city_en}
                                </span>
                              </div>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 border p-3 rounded-2xl text-xs text-gray-500 animate-pulse">
              {lang === "ar"
                ? "جاري تقييم الأعراض والبحث عن التخصص المناسب..."
                : "HealTrip AI is evaluating symptoms & searching DB..."}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="border-t pt-3 flex gap-2">
        <input
          type="text"
          className="flex-1 border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder={
            lang === "ar" ? "قم بوصف اعراضك هنا" : "Describe your symptoms"
          }
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button
          onClick={handleSend}
          disabled={loading}
          className="bg-blue-600 text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-blue-700 disabled:opacity-50 transition-all"
        >
          {lang === "ar" ? "إرسال" : "Send"}
        </button>
      </div>
    </div>
  );
}
