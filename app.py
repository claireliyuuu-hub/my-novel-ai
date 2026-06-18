import streamlit as st
import google.generativeai as genai
import json,os,time

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(
    page_title="文学创作引擎PRO",
    layout="wide"
)

SAVE_FILE="novel_save.json"

def load_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE,"r",encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data():
    data={
        "chat_history":st.session_state.chat_history,
        "bible_info":st.session_state.bible_info,
        "pre_text":st.session_state.pre_text,
        "style_bible":st.session_state.style_bible,
        "ml_info":st.session_state.ml_info,
        "fl_info":st.session_state.fl_info,
        "bg_info":st.session_state.bg_info
    }
    with open(SAVE_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

def safe_send(chat,text):
    for i in range(5):
        try:
            return chat.send_message(text)
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                time.sleep((i+1)*10)
            else:
                raise e
    return None

data=load_data()

if "chat_history" not in st.session_state:
    st.session_state.chat_history=data.get("chat_history",[])
    st.session_state.bible_info=data.get("bible_info","")
    st.session_state.pre_text=data.get("pre_text","")
    st.session_state.style_bible=data.get("style_bible","")
    st.session_state.ml_info=data.get("ml_info","")
    st.session_state.fl_info=data.get("fl_info","")
    st.session_state.bg_info=data.get("bg_info","")

st.title("✍️ 文学创作引擎 PRO")

with st.expander("设定与风格",expanded=True):

    st.session_state.pre_text=st.text_area(
        "参考例文:",
        st.session_state.pre_text,
        height=200
    )

    st.session_state.style_bible=st.text_area(
        "AI生成的文风档案:",
        st.session_state.style_bible,
        height=150
    )

    st.session_state.bible_info=st.text_area(
        "剧情档案:",
        st.session_state.bible_info,
        height=150
    )

    c1,c2=st.columns(2)

    st.session_state.ml_info=c1.text_input(
        "男主:",
        st.session_state.ml_info
    )

    st.session_state.fl_info=c2.text_input(
        "女主:",
        st.session_state.fl_info
    )

    st.session_state.bg_info=c1.text_input(
        "背景:",
        st.session_state.bg_info
    )

    if st.button("保存"):
        save_data()
        st.success("已保存")


if st.button("🧠 分析参考例文生成文风档案"):

    temp=genai.GenerativeModel(
        "gemini-2.5-flash"
    )

    r=temp.generate_content(
f"""
分析以下小说例文。

生成文风档案，不续写。

总结：
1叙事视角
2句式节奏
3环境描写
4人物描写
5对白特点
6情绪推进
7语言习惯

例文：
{st.session_state.pre_text[-10000:]}
"""
    )

    st.session_state.style_bible=r.text
    save_data()
    st.success("文风档案生成完成")

system_prompt=f"""
你是一名顶级小说作者。

你的任务是输出小说正文，不是解释。

【最高规则】
用户输入的是导演指令，不是正文。

禁止：
1.复制用户提示词原句。
2.改几个字重复用户表达。
3.用总结方式复述剧情要求。

用户指令只能转化为：
剧情方向、人物目的、冲突目标。

正文必须像小说书页。

【禁止AI语言】
不要出现：
好的
以下是
根据你的要求
续写如下

【文风规则】
最高参考：

{st.session_state.style_bible}

参考例文：

{st.session_state.pre_text[-3000:]}

必须保持：
句式
节奏
叙事视角
描写密度
对白习惯

【描写要求】
禁止流水账。

必须加入：
环境
声音
气味
动作
微表情
心理
潜台词

【人物】
男主：
{st.session_state.ml_info}

女主：
{st.session_state.fl_info}

背景：
{st.session_state.bg_info}

【剧情档案】
{st.session_state.bible_info}

结尾追加：

【档案更新】

只记录已经发生的事实。

禁止写：
用户要求
按照要求
本次续写
"""

model=genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction=system_prompt
)

for msg in st.session_state.chat_history[-10:]:
    with st.chat_message(
        "user" if msg["role"]=="user" else "assistant"
    ):
        st.markdown(msg["text"])


user_input=st.text_area(
    "✨ 输入剧情要求:",
    height=180
)


c1,c2,c3=st.columns(3)


if c1.button("✨立即创作"):

    if user_input:

        history=[
            {
                "role":"user" if x["role"]=="user" else "model",
                "parts":[x["text"]]
            }
            for x in st.session_state.chat_history[-5:]
        ]

        chat=model.start_chat(
            history=history
        )

        with st.spinner("创作中..."):

            response=safe_send(
                chat,
                user_input
            )

        if response:

            text=response.text

            st.session_state.chat_history.append(
                {
                "role":"user",
                "text":user_input
                }
            )

            if "【档案更新】" in text:

                body,update=text.split(
                    "【档案更新】",
                    1
                )

                st.session_state.chat_history.append(
                    {
                    "role":"model",
                    "text":body.strip()
                    }
                )

                st.session_state.bible_info+="\n"+update.strip()

            else:

                st.session_state.chat_history.append(
                    {
                    "role":"model",
                    "text":text
                    }
                )

            save_data()
            st.rerun()



if c2.button("↩️撤回上一段"):

    if len(st.session_state.chat_history)>=2:

        st.session_state.chat_history=(
            st.session_state.chat_history[:-2]
        )

        save_data()
        st.rerun()



if c3.button("🗑️清空"):

    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)

    st.session_state.chat_history=[]
    st.session_state.bible_info=""
    st.session_state.style_bible=""

    st.rerun()
