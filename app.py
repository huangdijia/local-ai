import os
import base64
import streamlit as st
from openai import OpenAI

# 设置环境变量和OpenAI客户端
token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = st.sidebar.selectbox("选择模型:", ["gpt-4o", "gpt-4o-mini"])

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

def get_image_data_url(image_file, image_format):
    """将图片文件转换为数据URL字符串"""
    try:
        return f"data:image/{image_format};base64,{base64.b64encode(image_file.read()).decode('utf-8')}"
    except Exception as e:
        st.error(f"读取图片时出错: {e}")
        return None

def text_chat():
    """处理文字聊天"""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

    for message in st.session_state.messages[1:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("请输入你的问题:")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("AI正在思考..."):
            try:
                response = client.chat.completions.create(
                    messages=st.session_state.messages,
                    model=model_name,
                )
                assistant_response = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                with st.chat_message("assistant"):
                    st.markdown(assistant_response)
            except Exception as e:
                st.error(f"处理消息时发生错误: {e}")

def image_chat():
    """处理图片聊天"""
    if "image_messages" not in st.session_state:
        st.session_state.image_messages = [
            {"role": "system", "content": "You are a helpful assistant that describes images in details."}
        ]

    uploaded_file = st.file_uploader("选择一张图片", type=["png", "jpg", "jpeg"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="上传的图片", use_column_width=True)
        
        if "image_url" not in st.session_state:
            image_url = get_image_data_url(uploaded_file, uploaded_file.type.split('/')[1])
            if image_url:
                st.session_state.image_url = image_url

    for message in st.session_state.image_messages[1:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("请输入关于图片的提示词:")
    
    if prompt and "image_url" in st.session_state:
        st.session_state.image_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("AI正在分析图片..."):
            try:
                response = client.chat.completions.create(
                    messages=st.session_state.image_messages + [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": st.session_state.image_url, "detail": "low"}},
                            ],
                        },
                    ],
                    model=model_name,
                )
                assistant_response = response.choices[0].message.content
                st.session_state.image_messages.append({"role": "assistant", "content": assistant_response})
                with st.chat_message("assistant"):
                    st.markdown(assistant_response)
            except Exception as e:
                st.error(f"处理图片时发生错误: {e}")

def main():
    st.title("AI聊天助手")
    
    chat_mode = st.radio("选择聊天模式:", ("文字聊天", "图片聊天"))
    
    if chat_mode == "文字聊天":
        text_chat()
    else:
        image_chat()

    if st.button("清除对话历史"):
        if "messages" in st.session_state:
            del st.session_state.messages
        if "image_messages" in st.session_state:
            del st.session_state.image_messages
        if "image_url" in st.session_state:
            del st.session_state.image_url
        st.success("对话历史已清除")

if __name__ == "__main__":
    main()