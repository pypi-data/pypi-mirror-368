from groq import Groq
from app import Analysischartbot

launcher = Analysischartbot()
client = Groq(api_key=launcher.get_groq_api_key())

def understand_query(query:str,model_:str = "Llama3-70b-8192"):
    try:
        template = f"""Your an helpful assistant to get understanding about the userquery based on the given conditions.
                    <userquery>{query}</userquery>. from the user query i want you to check the following conditions.
                    {{
                        "ifchart" : "if the user want to create a chart or not. value yes/no",
                        "type_of_chart" : "if the user want to create a chart,identify the type of chart user want to create eg (pie,bar,histogram) if no chart then 'None'.\
                                        Sometime user not explicitely tell which type of chart, for example,if user want to understand contribution (pie best option), likely understand which type of chart is suitable in that condition and return the same",
                        "ifdetails" : "Identify wheather the user asking for, understand the data through summary like , shape of the dataframe, null values or counts,value should yes or no.",
                        "type_of_details" : "which details user wants to understand, maybe dataframe summary, null values,shapes, understand acocrdingly and add the value,Put 'None' if ifdetails is no"
                        "None_of_above" : "if user query is not related to either charts or details about the data. value yes or no"
                    }}.output shoud be only the json with the same key as given in example, with the values understood from user query.
                    Output should only a json without any explanation.
                    """
        completion = client.chat.completions.create(
            model=model_,   
            messages=[
                {
                    "role": "user",
                    "content": template
                }
            ],
            temperature=0.9,
            max_tokens=1024,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error occured: {str(e)}"

def fn_create_chart(query:str,columns:dict,model_:str = "Llama3-70b-8192"):
    try:
        completion = client.chat.completions.create(
            model=model_, 
            messages=[
                {
                    "role": "system",
                    "content": f"""your a helpful assistant to help user to process with the dataframe df.\
                        Your job is to create a python pandas code, to process the data based on user query.\
                        Data is already loaded into df (pandas Dataframe). column are {columns}.you should create a python code to create a chart using matplotlib or seaborn,
                        then each line of code you can create in an array like.include the import statements if you use matplotlib or seaborn.
                        Do not include plt.show() in the code.
                        [
                            'chart = df["chapterName"].value_counts().plot(kind="bar")',
                            'chart.set_xlabel("Chapter Name")',
                            'chart.set_ylabel("Count")',
                            'chart.set_title("Chapter Name Distribution")',
                        ]. the code need to execute should always in array, and if you generating any chart , give the variable name 'chart'.
                        """
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            temperature=0.9,
            max_tokens=1024,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error occured: {str(e)}" 

def fn_create_summary(query:str,columns:dict,model_:str = "Llama3-70b-8192"):
    try:
        completion = client.chat.completions.create(
            model=model_,  
            messages=[
                {
                    "role": "system",
                    "content": f"""your a helpful assistant to help user to process with the dataframe df.\
                        Your job is to create a python pandas code, to process the data based on user query.\
                        Data is already loaded into df (pandas Dataframe). column are {columns}.you should create a python code to analyze the df based on the user query,
                        then each line of code you can create in an array like.Python code should create a variable 'output' which will have the results in '[(),(),...]' format (tuples inside array).
                        for an example if user asking about the null values in one column output variable should have [(column name,count of null values)].
                        then each line of code you can create in an array like, for an example if i want to calculate the missing value count in chapterName column
                        [
                            'missing_count = df['chapterName'].isna().sum()',
                            'output = [('Total missing value in chapterName is: ',missing_count)',..]'
                        ]. the code need to execute should always in array, and if you generating any output , give the variable name 'output'.
                        Do not include any explanation in output with the array.
                        """
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            temperature=0.9,
            max_tokens=1024,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error occured: {str(e)}" 

def fn_final_summary(query:str,model_:str = "Llama3-70b-8192"):
    try:
        completion = client.chat.completions.create(
            model=model_,   
            messages=[
                {
                    "role": "system",
                    "content": f"""Your an helpful assistant to explain the answer to the user based on the \
                        Data available and the user query.Output should be just the short explanation, \
                        without giving input Data available in the response.
                        """
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            temperature=0.9,
            max_tokens=1024,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error occured: {str(e)}" 

def fn_non_of_above(query:str,model_:str = "Llama3-70b-8192"):
    try:
        completion = client.chat.completions.create(
            model=model_,  
            messages=[
                {
                    "role": "system",
                    "content": f"""Your an helpful assistant to visualize and explain the data.Keep the response short as possible
                        """
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            temperature=0.9,
            max_tokens=1024,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error occured: {str(e)}" 