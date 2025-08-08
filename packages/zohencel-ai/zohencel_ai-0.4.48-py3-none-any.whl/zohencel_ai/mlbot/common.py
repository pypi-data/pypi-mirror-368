import json
import os,shutil,subprocess,zipfile

def clear_directory():
    save_dir = 'utils' 
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for filename in os.listdir(save_dir):
        file_path = os.path.join(save_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            raise str(e)

def get_file_path():
    utils_dir = os.path.join('.', 'utils')
    csv_path = os.path.join(utils_dir, 'data.csv')
    excel_path = os.path.join(utils_dir, 'data.xlsx')
    try:
        if os.path.isfile(csv_path):
            return "df = pd.read_csv(os.path.join('.', 'utils', 'data.csv'))"
        elif os.path.isfile(excel_path):
            return "df = pd.read_excel(os.path.join('.', 'utils', 'data.xlsx'))"
        else:
            raise FileNotFoundError("No data file found. Please upload either 'data.csv' or 'data.xlsx'.")
    except Exception as e:
        raise Exception(f"Error: {str(e)}")

def format_code():
    subprocess.run(['black', './utils/train.py'], check=True)

def read_accuracy():
    try:
        with open('utils\\accuracy.txt', 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return None
    except Exception as e:
        return None

import requests

def mlbot_api(query):
    url = "http://127.0.0.1:8000/chat"
    headers = {"accept": "application/json"}
    params = {"query": query}
    try:
        response = requests.post(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise str(e)

def register(name):
    current_file_location = os.path.dirname(os.path.abspath(__file__))
    utils_folder = f'{current_file_location}\\utils'
    models_folder = f'{current_file_location}\\models'
    zip_filename = f"{name}.zip"
    zip_filepath = os.path.join(utils_folder, zip_filename)
    with zipfile.ZipFile(zip_filepath, 'w') as zipf:
        for root, dirs, files in os.walk(utils_folder):
            for file in files:
                if file != zip_filename:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), utils_folder))
    model_folder = os.path.join(models_folder, name)
    os.makedirs(model_folder, exist_ok=True)
    with zipfile.ZipFile(zip_filepath, 'r') as zipf:
        zipf.extractall(model_folder)
    shutil.copy(zip_filepath, model_folder)

def saved_models():
    current_file_path = os.path.abspath(__file__)
    current_folder = os.path.dirname(current_file_path)
    models_folder = os.path.join (current_folder,'models')
    return [f for f in os.listdir(models_folder) if os.path.isdir(os.path.join(models_folder, f))]

def generate_overview(model_name):
    json_file_path = os.path.join("models", model_name, "descriptive_analysis.json")
    markdown_content = f"# Model '{model_name}' Overview\n\n"
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as file:
            data = json.load(file)
            for key, value in data.items():
                markdown_content += f"### {key}\n{value}\n\n"
    else:
        markdown_content += "No descriptive analysis found for this model."
    return markdown_content

def convert_object_to_numerical(validation_dict, df):
    for col in validation_dict:
        type =str(validation_dict[col]['data_type'])
        if type == 'object':
            try:
                df[col] = df[col].astype('float64')
            except Exception as e:
                special_char = str(e).split(':')[1].replace("'",'').strip()
                try:
                    if special_char.isalnum() == False and len(special_char)==1:
                        print(col,special_char)
                        df = df.replace(special_char,None)
                        df[col] = df[col].astype('float64')
                    pass
                except:
                    pass
    return df

def get_file_name():
    utils_dir = os.path.join('.', 'utils')
    csv_path = os.path.join(utils_dir, 'data.csv')
    excel_path = os.path.join(utils_dir, 'data.xlsx')
    try:
        if os.path.isfile(csv_path):
            return 'data.csv'
        elif os.path.isfile(excel_path):
            return 'data.xlsx'
        else:
            raise FileNotFoundError("No data file found. Please upload either 'data.csv' or 'data.xlsx'.")
    except Exception as e:
        raise Exception(f"Error: {str(e)}")
    
def create_test_script():
    current_file_location = os.path.dirname(os.path.abspath(__file__))
    txt_file_path = f"{current_file_location}\\test_script.py"
    py_file_path = os.path.join(current_file_location,"utils", "test.py")
    os.makedirs(f"{current_file_location}\\utils", exist_ok=True)
    with open(txt_file_path, "r") as txt_file:
        content = txt_file.read()
    with open(py_file_path, "w") as py_file:
        py_file.write(content)

def get_model_zip_path(model_name):
    current_file_path = os.path.abspath(__file__)
    current_folder = os.path.dirname(current_file_path)
    zip_path = os.path.join (current_folder,'models',model_name,f"{model_name}.zip")
    return zip_path

def get_scripts_and_text(model_name):
    current_file_path = os.path.abspath(__file__)
    current_folder = os.path.dirname(current_file_path)
    model_path = os.path.join (current_folder,'models',model_name)
    analysis_file_path = os.path.join(model_path, 'descriptive_analysis.json')
    train_script_path = os.path.join(model_path, 'train.py')
    test_script_path = os.path.join(model_path, 'test.py')
    try:
        with open(analysis_file_path, "r") as file:
            analysis_overview = file.read()
    except:
        analysis_overview = {"":"No descriptive analysis found for this model."}
    try:
        with open(train_script_path, "r") as file:
            train_script = file.read()
    except:
        train_script = "No training script found for this model."
    try:
        with open(test_script_path, "r") as file:
            test_script = file.read()
    except:
        test_script = "No testing script found for this model."
    return {
        "analysis_overview": analysis_overview,
        "train_script": train_script,
        "test_script": test_script
    }

