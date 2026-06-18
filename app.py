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

            with open(
                SAVE_FILE,
                "r",
                encoding="utf-8"
            ) as f:
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



def send_message(chat,text):

    for i in range(5):

        try:

            return chat.send_message(text)

        except Exception as e:

            if "429" in str(e):

                time.sleep(
                    (i+1)*8
                )

            else:

                raise e

    return None




data=load_data()


if "history" not in st.session_state:

    st.session_state.history=data.get(
        "history",
        []
    )

    st.session_state.bible=data.get(
        "bible",
        ""
    )

    st.session_state.example=data.get(
        "example",
        ""
    )

    st.session_state.style=data.get(
        "style",
        ""
    )

    st.session_state.male=data.get(
        "male",
        ""
    )

    st.session_state.female=data.get(
        "female",
        ""
    )

    st.session_state.bg=data.get(
        "bg",
        ""
    )



st.title(
    "✍️ Flash文学创作引擎"
)



with st.sidebar:

    st.header(
        "🛡️备份"
    )


    if st.button(
        "保存当前"
    ):

        save_data()

        st.success(
            "已保存"
        )


    export=json.dumps(
        st.session_state.history,
        ensure_ascii=False,
        indent=2
    )


    st.download_button(
        "下载JSON备份",
        export,
        "novel_backup.json"
    )




with st.expander(
    "📚设定中心",
    expanded=True
):

    st.session_state.example=st.text_area(
        "参考例文:",
        st.session_state.example,
        height=250
    )


    st.session_state.style=st.text_area(
        "文风档案:",
        st.session_state.style,
        height=180
    )


    st.session_state.bible=st.text_area(
        "剧情档案:",
        st.session_state.bible,
        height=180
    )


    c1,c2=st.columns(2)


    st.session_state.male=c1.text_input(
        "男主:",
        st.session_state.male
    )


    st.session_state.female=c2.text_input(
        "女主:",
        st.session_state.female
    )


    st.session_state.bg=c1.text_input(
        "背景:",
        st.session_state.bg
    )



    if st.button(
        "💾保存设定"
    ):

        save_data()

        st.success(
            "保存成功"
        )





if st.button(
    "🧠分析参考例文"
):

    ai=genai.GenerativeModel(
        "gemini-2.5-flash"
    )


    r=ai.generate_content(
f"""

你是专业小说编辑。

分析下面小说片段。

不要续写。

生成【文风档案】。


总结：

1.叙事视角
2.句式节奏
3.语言习惯
4.环境描写特点
5.人物动作特点
6.心理描写方式
7.对白特点
8.情绪推进方式


文本：

{st.session_state.example[-3000:]}

"""
    )


    st.session_state.style=r.text

    save_data()

    st.success(
        "文风档案完成"
    )





system=f"""

你是一名顶级商业小说作者。

你的任务只有一个：

输出小说正文。


用户输入的是剧情指令。

不是正文。


【禁止】

禁止复制用户提示词。

禁止重新描述用户要求。

禁止解释你要怎么写。


禁止出现：

好的

以下是

根据你的要求

续写如下


必须直接进入故事。


【最高风格标准】

参考例文决定：

语言节奏、
句式、
叙事方式、
情绪表达。


不要写普通AI文章。


【文学描写强制要求】


禁止流水账。


每一段必须有具体描写。


【环境描写】

必须加入：

天气、
光线、
空间、
声音、
气味、
温度、
触感。

环境必须影响人物情绪。



【人物动作】

禁止：

他很生气。
她很难过。


必须通过：

手指、
眼神、
呼吸、
姿态、
停顿、
动作变化

表现。



【微表情】

加入：

眉眼、
嘴角、
目光、
脸色、
下意识动作。


【心理描写】

必须体现：

犹豫、
挣扎、
判断、
欲望、
恐惧、
克制。



【对白】

对白不能只是传递信息。

必须体现：

关系、
冲突、
试探、
隐藏目的。



【感官】

强化：

视觉、
听觉、
嗅觉、
触觉。


【节奏】

重要剧情必须展开。

关键动作、
情绪爆发、
关系变化，

不能一句带过。



【人物】

男主：

{st.session_state.male}


女主：

{st.session_state.female}


背景：

{st.session_state.bg}



【剧情档案】

{st.session_state.bible}



【参考文风档案】

{st.session_state.style}


结尾必须：

【档案更新】

只记录本段发生事实。

"""



model=genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction=system
)





for x in st.session_state.history[-10:]:

    with st.chat_message(
        x["role"]
    ):

        st.markdown(
            x["text"]
        )





prompt=st.text_area(
    "✨输入剧情",
    height=200
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


        r=send_message(
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
