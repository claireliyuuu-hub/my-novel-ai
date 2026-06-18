import streamlit as st
import google.generativeai as genai
import json,os,time

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

st.set_page_config(
    page_title="Flash文学创作引擎",
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
        "history":st.session_state.history,
        "bible":st.session_state.bible,
        "example":st.session_state.example,
        "style":st.session_state.style,
        "male":st.session_state.male,
        "female":st.session_state.female,
        "bg":st.session_state.bg
    }

    with open(
        SAVE_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def send(chat,text):
    for i in range(5):
        try:
            return chat.send_message(text)
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                time.sleep((i+1)*8)
            else:
                raise e
    return None


data=load_data()

if "history" not in st.session_state:
    st.session_state.history=data.get("history",[])
    st.session_state.bible=data.get("bible","")
    st.session_state.example=data.get("example","")
    st.session_state.style=data.get("style","")
    st.session_state.male=data.get("male","")
    st.session_state.female=data.get("female","")
    st.session_state.bg=data.get("bg","")


st.title("✍️ Flash文学创作引擎")


with st.expander(
    "📚 设置",
    expanded=True
):

    st.session_state.example=st.text_area(
        "参考例文:",
        st.session_state.example,
        height=200
    )

    st.session_state.style=st.text_area(
        "文风档案:",
        st.session_state.style,
        height=150
    )

    st.session_state.bible=st.text_area(
        "剧情档案:",
        st.session_state.bible,
        height=150
    )


    c1,c2=st.columns(2)

    st.session_state.male=c1.text_input(
        "男主",
        st.session_state.male
    )

    st.session_state.female=c2.text_input(
        "女主",
        st.session_state.female
    )

    st.session_state.bg=c1.text_input(
        "背景",
        st.session_state.bg
    )


    if st.button("保存设置"):
        save_data()
        st.success("保存完成")



if st.button(
    "🧠 分析参考例文"
):

    try:

        ai=genai.GenerativeModel(
            "gemini-2.5-flash"
        )


        r=ai.generate_content(
f"""
你是小说编辑。

分析以下小说。

不要续写。

生成文风档案。


总结：

1.叙事视角
2.句式节奏
3.语言特点
4.环境描写
5.人物动作
6.心理描写
7.对白方式
8.情绪推进


文本：

{st.session_state.example[-3000:]}
"""
        )


        st.session_state.style=r.text

        save_data()

        st.success(
            "文风档案生成成功"
        )


    except Exception as e:

        st.error(
            f"分析失败:{e}"
        )




system=f"""
你是一名小说作者。

只输出小说正文。

用户输入是导演指令，
不是正文。

禁止复制用户提示词。

禁止：
好的
以下是
根据你的要求
续写如下


必须直接进入故事。


参考文风：

{st.session_state.style}


参考文本：

{st.session_state.example[-1000:]}


写作要求：

加入：

环境
声音
气味
动作
微表情
心理
对白潜台词


人物：

男主:
{st.session_state.male}

女主:
{st.session_state.female}

背景:
{st.session_state.bg}


剧情档案:

{st.session_state.bible}


结束添加：

【档案更新】

只记录发生事实。
"""


model=genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction=system
)



for m in st.session_state.history[-10:]:

    with st.chat_message(m["role"]):
        st.markdown(m["text"])



prompt=st.text_area(
    "✨输入剧情",
    height=180
)


if st.button(
    "✨开始创作"
):

    if prompt:

        history=[
            {
            "role":x["role"],
            "parts":[x["text"]]
            }
            for x in st.session_state.history[-5:]
        ]


        chat=model.start_chat(
            history=history
        )


        with st.spinner(
            "创作中..."
        ):

            r=send(
                chat,
                prompt
            )


        if r:

            text=r.text

            st.session_state.history.append(
                {
                "role":"user",
                "text":prompt
                }
            )

            st.session_state.history.append(
                {
                "role":"model",
                "text":text
                }
            )


            if "【档案更新】" in text:

                update=text.split(
                    "【档案更新】",
                    1
                )[1]

                st.session_state.bible += (
                    "\n"+update
                )


            save_data()

            st.rerun()
