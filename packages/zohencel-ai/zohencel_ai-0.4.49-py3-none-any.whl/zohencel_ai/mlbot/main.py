import json,os
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import pandas as pd
import subprocess,traceback
from fastapi import FastAPI, File, UploadFile, logger,Request
from fastapi.middleware.cors import CORSMiddleware
from template_class import Templates
from common import get_file_path,create_test_script,\
                    format_code,read_accuracy,get_file_name,register,saved_models,\
                    get_model_zip_path,get_scripts_and_text,clear_directory
import datetime
from bot import ZohencelmlBot

bot = ZohencelmlBot()  
temps = Templates(groq_api=bot.get_groq_api_key(),model_name =bot.get_groq_model())

app = FastAPI(title="API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

messages = [{"role": "system", "content": temps.stage_1_sysprmt}]

utils_folder = "utils"
step_1 = ""
algorithm = ""
accuracy = None
target_column = ""
pipeline = ""
df_statistics = ""
duplicated_anlysis = ""
outlier_treatment = ""
skew_treatment = ""
encode_treatment = ""
corr_treatment = ""
scale_treatment = ""
df = pd.DataFrame()

current_file_location = os.path.dirname(os.path.abspath(__file__))
utils_folder_path = os.path.join(current_file_location, 'utils')
if not os.path.exists(utils_folder_path):
    os.makedirs(utils_folder_path)

models_folder_path = os.path.join(current_file_location, 'models')
if not os.path.exists(models_folder_path):
    os.makedirs(models_folder_path)

@app.post("/chat")
def chatbot_endpoint(query: str):
    global step_1, algorithm,target_column,pipeline,accuracy,df,df_statistics,\
            duplicated_anlysis,outlier_treatment,skew_treatment,encode_treatment,corr_treatment,scale_treatment
    try:
        try:
            get_file_name()
        except:
            return {'response':temps.RTS('Please upload a file first (expected csv or excel file).')}
        if step_1 == '':
            messages.append({"role" : "user" , "content" : query})
            response_ = temps.stage_1(messages)
            try:
                output = eval(response_[response_.find('{'):response_.rfind('}') + 1])
            except:
                output = {"assistant_response": response_, "status": ""}
            if output['status'].lower() != 'done':
                print(output['assistant_response'])
                messages.append({"role" : "assistant" , "content" : output['assistant_response']})
                filename = get_file_name()
                if filename.split('.')[1] == 'csv':
                    df = pd.read_csv(os.path.join('.','utils',filename))
                elif filename.split('.')[1] == 'xlsx':
                    df = pd.read_excel(os.path.join('.','utils',filename))
                messages.append({"role" : "assistant" , "content" : f"All columns in my dataframe for your reference. {df.columns}"})
                return {'response':output['assistant_response'],'algorithm' : ''}
            else:
                step_1 = output['status']
                algorithm = output['algorithm']
                target_column = output['target_column']
                return {'response':output['assistant_response'],'algorithm' : algorithm}
        else:
            filename = get_file_name()
            if filename.split('.')[1] == 'csv':
                df = pd.read_csv(os.path.join('.','utils',filename))
            elif filename.split('.')[1] == 'xlsx':
                df = pd.read_excel(os.path.join('.','utils',filename))
            if query=='1':
                df_statistics = temps.analyze_missing_data(df)
                df_statistics = temps.RTS(df_statistics)
                return {'response': df_statistics}
            elif query=='2':
                duplicated_count = df.duplicated().sum()
                duplicated_anlysis = temps.RTS(f"The data frame have {duplicated_count} duplicate rows.Kept the first one and deleted the duplicates.")
                return {'response': duplicated_anlysis}
            elif query=='3':
                df_outlier = temps.analyze_outliers(df)
                outlier_template = f"""
                                    Here given an outliers analysis of few column from a dataframe.
                                    <data>{df_outlier.to_dict(orient='records')}</data>Analyze and give the insights in words to user in few words.
                                    .If data have no significant outliers, elaborate that as well in few words."""
                outlier_treatment = temps.groq_assistant(outlier_template)
                return {'response': outlier_treatment}
            elif query=='4': # error
                skew_n_dist = temps.analyze_skewness_and_variability(df)
                skew_template = f"""## Skewness Analysis
                                Here given the skew analysis for columns in a dataframe. Your duty is to underand and tell user in short words.
                                <data>{skew_n_dist.to_dict(orient='records')}</data>"""
                skew_treatment = temps.groq_assistant(skew_template)
                return {'response': skew_treatment}
            elif query=='5':
                encode_methods = temps.analyze_encoding_methods(df)
                encode_template = f"""## Encoding Analysis
                                Here given the encode analysis for columns in a dataframe. Your duty is to underand and tell user in short words.
                                <data>{encode_methods.to_dict(orient='records')}</data>"""
                encode_treatment = temps.groq_assistant(encode_template)
                return {'response': encode_treatment}
            elif query=='6':
                corr_data = temps.analyze_correlation(df, target_column)
                corr_template = f"""## Correlation Analysis
                                Here given the correlation analysis for columns in a dataframe. Your duty is to underand and tell user in short words why these column nede to remove.
                                <data>{corr_data}</data>"""
                corr_treatment = temps.groq_assistant(corr_template)
                return {'response': corr_treatment}
            elif query=='7':
                scaling_analysis = temps.analyze_scaling(df)
                scale_template = f"""## Feature Scaling Analysis
                                Here given the scaling analysis for columns in a dataframe. Your duty is to underand and tell user in short words.
                                <data>{scaling_analysis.to_dict(orient='records')}</data>"""
                scale_treatment = temps.groq_assistant(scale_template)
                return {'response': scale_treatment}
            elif query=='8':
                descriptive_analysis = {
                    "algorithm" : algorithm,
                    "target_column" : target_column,
                    "missing data" : df_statistics, 
                    "duplicated_anlysis" : duplicated_anlysis,
                    "outlier analysis" : outlier_treatment,
                    "skew analysis" : skew_treatment,
                    "encoding analysis" : encode_treatment,
                    "correlation analysis" : corr_treatment, 
                    "feature scaling analysis" : scale_treatment
                }
                with open('utils\\descriptive_analysis.json', 'w') as json_file:
                    json.dump(descriptive_analysis, json_file, indent=4)
                import_dataset = ['import os,pickle','import pandas as pd','import numpy as np', get_file_path()]
                handle_label = [f"try:df['{target_column}'] = df['{target_column}'].str.replace(r'[^a-zA-Z0-9 ]', '', regex=True).str.strip().replace('', None)","except: pass",f"try: df['{target_column}'] = df['{target_column}'].astype(float)","except: pass"]
                save_artifacts = ["with open(os.path.join('.','utils','accuracy.txt'), 'w') as file:","    file.write(str(accuracy))","if pipeline:","    with open('utils/pipeline_model.pkl', 'wb') as f:","        pickle.dump(pipeline, f)"]
                a = 0
                while True:
                    a += 1
                    if a < 4:
                        try:
                            filename = get_file_name()
                            if filename.split('.')[1] == 'csv':
                                df = pd.read_csv(os.path.join('.','utils',filename))
                            elif filename.split('.')[1] == 'xlsx':
                                df = pd.read_excel(os.path.join('.','utils',filename))
                            trained = temps.zai_training(descriptive_analysis, df.columns)
                            code_list = eval(trained[trained.find('['):trained.rfind(']')+1])
                            code_list = import_dataset + handle_label + code_list + save_artifacts
                            train_file_path = os.path.join('utils', 'train.py')
                            os.makedirs('utils', exist_ok=True) 
                            with open(train_file_path, 'w') as f:
                                for line in code_list:
                                    f.write(line + '\n')
                            try:
                                format_code()
                            except:
                                logger.error("Error in formatting the code")
                                pass
                            process = subprocess.run(['python', train_file_path], capture_output=True, text=True)
                            if process.returncode != 0:
                                print("Error in train.py execution:")
                                print(process.stderr)
                            else:
                                print("train.py executed successfully")
                                print(process.stdout)
                            accuracy = read_accuracy()
                            if accuracy is not None:
                                return   {'response': temps.RTS(accuracy)}  
                        except Exception as error:
                            print(traceback.format_exc()) 
                    else:
                        return {'response':temps.RTS('Unable to process now. Please try after sometime.')}
            elif query=='9':
                print("Invoked number 9...")
                current_time = datetime.datetime.now()
                name = f'{target_column}_{algorithm}_{current_time.hour}{current_time.minute}{current_time.second}{current_time.year}'
                create_test_script()
                register(name)
                return {'response': temps.RTS(f'Model saved successfully with name: {name}, go to models tab to download or use the model, training script and the descriptive analysis.')}
            else:
                return {'response':temps.RTS('Model has been trained and saved successfully.Please restart the api to start with a new model develpoment.')}
    except Exception as e:
        return {'response':temps.RTS('Your using a inbuilt groq api. It must have beem reached the ratelimit.\
                   Don\'t worry, you can get free groq api your own at https://console.groq.com/keys.')}


@app.get("/saved_models")
def get_saved_models():
    try:
        saved_models_list = saved_models()
        if len(saved_models_list) > 0:
            return {"response": saved_models_list}
        else:
            return {"response": "No models saved yet."}
    except Exception as e:
        return {"response": "error in fetching saved models."}

@app.get("/files/{model_name}")
def download_file(model_name: str):
    zip_path = get_model_zip_path(model_name)
    if os.path.isfile(zip_path):
        return FileResponse(zip_path, media_type="application/zip", filename=f"{model_name}.zip")
    else:
        return JSONResponse(content={"response": "File not found."}, status_code=404)

@app.get("/model_artifacts/{model_name}")
def get_associated_files(model_name: str):
    scripts_n_text = get_scripts_and_text(model_name)
    return JSONResponse(scripts_n_text)

#oooooooooooooooooooooooooooooooooooooooooooooooo
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    clear_directory()
    file_extension = file.filename.split('.')[-1]
    save_path = os.path.join(utils_folder, f"data.{file_extension}")
    with open(save_path, "wb") as f:
        f.write(file.file.read())
    return {"message": "File uploaded successfully"}

@app.get("/test_api")
def test_api():
    return {"response": 200}
