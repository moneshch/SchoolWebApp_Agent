from django.urls import path

from . import views


urlpatterns = [

    # =====================================
    # HOME
    # =====================================

    path(
        "",
        views.home,
        name="home"
    ),

    # =====================================
    # CHATBOT
    # =====================================

    path(
        "chat/",
        views.chatbot,
        name="chatbot"
    ),

    # =====================================
    # CHAT HISTORY API
    # =====================================

    path(
        "chat/history/",
        views.chat_history,
        name="chat_history"
    ),

    # =====================================
    # SINGLE CHAT SESSION API
    # =====================================

    path(
        "chat/session/<int:session_id>/",
        views.chat_session,
        name="chat_session"
    ),

]