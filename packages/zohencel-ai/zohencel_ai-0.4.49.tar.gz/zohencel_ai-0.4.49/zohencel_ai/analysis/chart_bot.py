from io import BytesIO
import streamlit as st
import pandas as pd
from PIL import Image
from templates import *


st.title("Chart bot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image" in message:
            image_data = message["image"]
            image = Image.open(BytesIO(image_data))
            st.image(image, width=400)
        else:
            st.markdown(message["content"])

st.sidebar.title("Upload Options")
uploaded_file = st.sidebar.file_uploader("Upload CSV, Excel, or JSON file", type=["csv", "xlsx", "json"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith(".json"):
            df = pd.read_json(uploaded_file)
        else:
            st.sidebar.error("Unsupported file format.")
        
        st.sidebar.success("File uploaded successfully!")
    except Exception as e:
        st.sidebar.error(f"Error loading file: {e}")
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    retries = 3  
    success = False  
    for attempt in range(retries):
        try:
            with st.chat_message("assistant"):
                user_query = prompt
                output = understand_query(user_query)
                query_eval = eval(output[output.find('{'):output.rfind('}')+1])

                if query_eval['ifchart'] == 'yes':
                    query = f"""User_query: {user_query}
                                Expected chart type : {query_eval['type_of_chart']}"""
                    op_chart = fn_create_chart(query=query, columns=f"{df.columns}")
                    op_chart = op_chart[op_chart.find('['):op_chart.rfind(']')+1]
                    op_chart = eval(op_chart)
                    for i in op_chart:
                        exec(i)
                    fig = chart.get_figure()
                    buf = BytesIO()
                    fig.savefig(buf, format="PNG")
                    buf.seek(0)
                    image = Image.open(buf)
                    st.image(image, width=400)
                    # st.session_state.messages.append({"role": "assistant", "image": image})
                    st.session_state.messages.append({"role": "assistant", "image": buf.getvalue()})

                elif query_eval['ifdetails'] == 'yes':
                    op_sum = fn_create_summary(query=user_query, columns=f"{df.columns}")
                    op_sum = op_sum[op_sum.find('['):op_sum.rfind(']')+1]
                    op_sum = eval(op_sum)
                    for i in op_sum:
                        exec(i)
                    final_sum = fn_final_summary(f"User query: {user_query}.Data available: {output}")
                    st.write(final_sum)
                    st.session_state.messages.append({"role": "assistant", "content": final_sum})

                else:
                    fnl_op = fn_non_of_above(user_query)
                    st.write(fnl_op)
                    st.session_state.messages.append({"role": "assistant", "content": fnl_op})

                success = True 
                break 

        except Exception as e:
            pass

    if not success:
        st.session_state.messages.append({"role": "assistant", "content": "Error: Unable to process your request."})

