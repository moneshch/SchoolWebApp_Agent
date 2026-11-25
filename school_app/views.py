import json
import time

from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required

from .models import (
    UploadedDocument,
    ChatSession,
    ChatMessage,
    AgentLog
)

from .ai.agents import get_agent
from .ai.rag import ingest_pdf


# =========================================================
# HOME PAGE
# =========================================================

def home(request):

    return render(
        request,
        "home.html"
    )


# =========================================================
# CHATBOT PAGE
# =========================================================

@login_required
def chatbot(request):

    # =====================================================
    # HANDLE POST REQUEST
    # =====================================================

    if request.method == "POST":
        response_text = ""

        uploaded_filename = ""

        session = None

        try:

            # =================================================
            # JSON REQUEST
            # =================================================

            if request.content_type == "application/json":

                data = json.loads(request.body)

                user_message = data.get(
                    "message",
                    ""
                )

                session_id = data.get(
                    "session_id"
                )

                # Sanitize: treat "undefined" / "null" / "" as no session
                if not session_id or str(session_id).strip() in ("undefined", "null", ""):
                    session_id = None

                prompt_mode = data.get(
                    "prompt_mode",
                    "normal"
                )

                uploaded_file = None

            # =================================================
            # FORM-DATA REQUEST
            # =================================================

            else:

                user_message = request.POST.get(
                    "message",
                    ""
                )

                session_id = request.POST.get(
                    "session_id"
                )

                # Sanitize: treat "undefined" / "null" / "" as no session
                if not session_id or str(session_id).strip() in ("undefined", "null", ""):
                    session_id = None

                prompt_mode = request.POST.get(
                    "prompt_mode",
                    "normal"
                )
                print("**********************************")
                print(prompt_mode)

                uploaded_file = request.FILES.get(
                    "file"
                )

            # =================================================
            # GET OR CREATE CHAT SESSION
            # =================================================

            if session_id:

                try:

                    session = ChatSession.objects.get(
                        id=session_id,
                        user=request.user
                    )

                except ChatSession.DoesNotExist:

                    return JsonResponse({
                        "error": "Invalid session there"
                    }, status=404)

            else:

                session = ChatSession.objects.create(
                    user=request.user,
                    title=user_message[:50]
                )

            # =================================================
            # FILE UPLOAD + RAG INGESTION
            # =================================================

            if uploaded_file:

                try:

                    fs = FileSystemStorage()

                    filename = fs.save(
                        uploaded_file.name,
                        uploaded_file
                    )

                    file_path = fs.path(filename)

                    uploaded_filename = filename

                    # =========================================
                    # SAVE FILE RECORD
                    # =========================================

                    uploaded_doc = UploadedDocument.objects.create(
                        title=uploaded_file.name,
                        file=filename,
                        uploaded_by=request.user.username,
                        processed=False
                    )

                    # =========================================
                    # PDF INGESTION
                    # =========================================

                    if file_path.lower().endswith(".pdf"):

                        chunk_count = ingest_pdf(
                            file_path
                        )

                        uploaded_doc.processed = True

                        uploaded_doc.summary = (
                            f"Indexed successfully with "
                            f"{chunk_count} chunks."
                        )

                        uploaded_doc.save()

                        response_text += (
                            "<b>PDF uploaded and indexed "
                            "successfully.</b><br><br>"
                        )

                    else:

                        response_text += (
                            "<b>Only PDF files are currently "
                            "supported.</b><br><br>"
                        )

                except Exception as e:

                    response_text += (
                        f"<b>File upload error:</b> "
                        f"{str(e)}<br><br>"
                    )

            # =================================================
            # SAVE USER MESSAGE
            # =================================================

            if user_message:

                ChatMessage.objects.create(
                    session=session,
                    role="user",
                    content=user_message
                )

            # =================================================
            # LOAD CHAT HISTORY
            # =================================================

            previous_messages = (
                session.messages
                .all()
                .order_by("created_at")[:20]
            )

            messages_for_agent = []

            for msg in previous_messages:

                messages_for_agent.append({

                    "role": msg.role,

                    "content": msg.content
                })

            # =================================================
            # AI AGENT
            # =================================================

            if user_message:

                try:

                    # =========================================
                    # START TIMER
                    # =========================================

                    start_time = time.time()

                    # =========================================
                    # AGENT INVOCATION
                    # =========================================

                    response = get_agent(prompt_mode).invoke({

                        "messages":
                            messages_for_agent
                    })

                    # =========================================
                    # END TIMER
                    # =========================================

                    end_time = time.time()

                    execution_time = (
                        end_time - start_time
                    )

                    # =========================================
                    # FINAL RESPONSE
                    # =========================================

                    assistant_reply = (
                        response["messages"][-1].content
                    )
                    print(response)

                    # =========================================
                    # SAVE ASSISTANT MESSAGE
                    # =========================================

                    ChatMessage.objects.create(
                        session=session,
                        role="assistant",
                        content=assistant_reply
                    )

                    # =========================================
                    # TOOL LOGGING
                    # =========================================

                    tool_used = ""

                    tool_input = ""

                    tool_output = ""

                    for msg in response["messages"]:

                        # =====================================
                        # TOOL CALLS
                        # =====================================

                        if hasattr(
                            msg,
                            "tool_calls"
                        ):

                            if msg.tool_calls:

                                tool_used = (
                                    msg.tool_calls[0]
                                    ["name"]
                                )

                                tool_input = str(
                                    msg.tool_calls[0]
                                    ["args"]
                                )

                        # =====================================
                        # TOOL OUTPUT
                        # =====================================

                        if (
                            msg.__class__.__name__
                            == "ToolMessage"
                        ):

                            tool_output = (
                                msg.content
                            )

                    # =========================================
                    # SAVE AGENT LOG
                    # =========================================

                    AgentLog.objects.create(

                        user=request.user,

                        session=session,

                        user_message=user_message,

                        tool_used=tool_used,

                        tool_input=tool_input,

                        tool_output=tool_output,

                        final_response=assistant_reply,

                        execution_time=execution_time
                    )

                    # =========================================
                    # APPEND RESPONSE
                    # =========================================

                    response_text += (
                        assistant_reply
                    )

                except Exception as e:

                    response_text += (
                        f"<b>AI Agent Error:</b> "
                        f"{str(e)}"
                    )

            # =================================================
            # RETURN JSON RESPONSE
            # =================================================

            return JsonResponse({

                "response":
                    response_text,

                "uploaded_filename":
                    uploaded_filename,

                "session_id":
                    session.id
            })

        except Exception as e:

            return JsonResponse({

                "error": str(e)

            }, status=500)

    # =====================================================
    # HANDLE GET REQUEST
    # =====================================================

    return render(
        request,
        "chatbot_V2.html"
    )


# =========================================================
# CHAT HISTORY API
# =========================================================

@login_required
def chat_history(request):

    sessions = (

        ChatSession.objects

        .filter(user=request.user)

        .order_by("-updated_at")
    )

    data = []

    for session in sessions:

        data.append({

            "id":
                session.id,

            "title":
                session.title,

            "created_at":
                session.created_at.strftime(
                    "%Y-%m-%d %H:%M"
                )
        })

    return JsonResponse({

        "sessions": data
    })


# =========================================================
# CHAT SESSION API
# =========================================================

@login_required
def chat_session(request, session_id):

    try:

        session = ChatSession.objects.get(

            id=session_id,

            user=request.user
        )

    except ChatSession.DoesNotExist:

        return JsonResponse({

            "error": "Session not found"

        }, status=404)

    messages = session.messages.all().order_by(
        "created_at"
    )

    data = []

    for msg in messages:

        data.append({

            "role":
                msg.role,

            "content":
                msg.content,

            "created_at":
                msg.created_at.strftime(
                    "%Y-%m-%d %H:%M"
                )
        })

    return JsonResponse({

        "session_id":
            session.id,

        "title":
            session.title,

        "messages":
            data
    })