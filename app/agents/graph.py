from typing import TypedDict
from langgraph.graph import StateGraph, END

# 1. استيراد الخدمات الجاهزة من الـ Container بتاعك مباشرة
from app.containers.services import memory_service, hybrid_service, llm_service


class GraphState(TypedDict):
    session_id: str
    question: str
    history: list
    documents: list
    context: str
    answer: str


def load_memory_node(state: GraphState):
    # جلب الذاكرة من النسخة المركزية
    history = memory_service.get_last_messages(state["session_id"], limit=10)
    
    # التعديل: نرجع فقط المفتاح الذي نريد تحديثه
    return {"history": history}


def retrieve_node(state: GraphState):
    # استخدام الـ hybrid_service الجاهزة المتصلة بـ Qdrant و BM25
    docs = hybrid_service.search(query=state["question"])
    context = "\n\n".join(doc.page_content for doc in docs)
    
    # التعديل: نرجع القاموس المحدث فقط
    return {
        "documents": docs,
        "context": context
    }


def llm_node(state: GraphState):
    prompt = f"""
    Conversation History:
    {state["history"]}

    Context:
    {state["context"]}

    Question:
    {state["question"]}
    """
    answer = llm_service.generate(prompt)
    
    # التعديل: نرجع الإجابة فقط
    return {"answer": answer}


def save_memory_node(state: GraphState):
    # حفظ رسالة المستخدم ورسالة المساعد في الـ Redis بأمان
    memory_service.save_message(state["session_id"], "user", state["question"])
    memory_service.save_message(state["session_id"], "assistant", state["answer"])
    
    # بما أن الدالة دي في نهاية الجراف ومبتحدثش بيانات تانية في الـ State، بنرجع قاموس فارغ أو None
    return {}


# ==========================
# بناء وتوصيل الجراف
# ==========================
builder = StateGraph(GraphState)

builder.add_node("load_memory", load_memory_node)
builder.add_node("retrieve", retrieve_node)
builder.add_node("llm", llm_node)
builder.add_node("save", save_memory_node)

builder.set_entry_point("load_memory")

builder.add_edge("load_memory", "retrieve")
builder.add_edge("retrieve", "llm")
builder.add_edge("llm", "save")
builder.add_edge("save", END)

graph = builder.compile()