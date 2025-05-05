import streamlit as st
from main import get_assistant
import os

# Thiết lập giao diện Streamlit
st.set_page_config(
    page_title="Trợ lý AI Phòng Nhân sự",
    page_icon="👨‍💼",
    layout="wide"
)

def main():
    # Khởi tạo assistant
    assistant = get_assistant()
    
    # Header
    st.title("Trợ lý AI Phòng Nhân sự")
    st.markdown("""
    Chào mừng bạn đến với Trợ lý AI của phòng Nhân sự. 
    Hãy đặt câu hỏi về chính sách nhân sự, quy trình tuyển dụng, đào tạo và phúc lợi.
    """)
    
    # Sidebar
    st.sidebar.title("Danh mục")
    category = st.sidebar.selectbox(
        "Chọn danh mục",
        ["Tất cả", "Tuyển dụng", "Onboarding", "Phúc lợi", "Đánh giá", "Quy định"]
    )
    
    # Chat container
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Hiển thị lịch sử chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
        # Thêm câu hỏi vào lịch sử
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Hiển thị đang xử lý
        with st.chat_message("assistant"):
            with st.spinner("Đang suy nghĩ..."):
                response = assistant.ask(prompt)
                st.markdown(response)
        
        # Thêm câu trả lời vào lịch sử
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
