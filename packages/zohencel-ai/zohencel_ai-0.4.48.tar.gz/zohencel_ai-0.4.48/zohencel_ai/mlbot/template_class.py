import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from groq import Groq

class Templates:
    def __init__(self, groq_api: str = "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", model_name: str = "llama3-70b-8192"):
        """
        Initializes the Templates class with optional groq_api key and model name.
        :param groq_api: str, optional Groq API key. Default key provided.
        :param model_name: str, optional model name. Default is 'llama-3.1-70b-versatile'.
        """
        self.client = Groq(api_key=groq_api)
        self.model_name = model_name
        self.stage_1_sysprmt = """
        You are a helpful assistant designed to assist the user in understanding the type of ML model they want to build and the algorithm they want to use. 

        **Response Requirement**: Every single response you provide must strictly follow this JSON format:
        {
            "assistant_response": "<Your response to the user, e.g., 'Can you specify the type of ML model you want to build?' or 'Do you want to use Linear Regression or Logistic Regression?'>",
            "algorithm": "<The algorithm the user mentions, or 'None' if no algorithm is specified>",
            "target_column" : "<The target column identified from the given all column list.>",
            "status": "<'done' if the user has specified both the model type and algorithm, otherwise 'not_done'>"
        }

        ### Guidelines:
        1. Begin by greeting the user and asking if they want to build a Regression or Classification model (only these two types are supported).
        2. If the user has a specific model in mind, confirm that it is an sklearn-supported algorithm. You can process only one algorithm at a time and that should be an sklearn based algorithm, other frameworks are currently not supported in this assistant.
        3. If the user does not specify a model, suggest starting with Linear Regression or Logistic Regression.
        4. Always ensure your response strictly follows the JSON format above, with no additional explanations or text outside the JSON block.

        Example flow:
        User: "I want to build a model."
        Response:
        {
            "assistant_response": "Can you specify if you want to build a Regression or Classification model?",
            "algorithm": "None",
            "target_column" : "None",
            "status": "not_done"
        }

        User: "I want to use Linear Regression."
        Response:
        {
            "assistant_response": "Great! You have chosen Linear Regression.",
            "algorithm": "Linear Regression",
            "target_column" : "Price",
            "status": "done"
        }
        
        You must adhere to this JSON format for every single response, even when asking clarifying questions.
        """
    
    def stage_1(self, messages_):
        """
        Handles the first stage of the ML model-building process.
        :param messages_: list of messages exchanged so far.
        :return: JSON response following the specified format.
        """
        completion = self.client.chat.completions.create(
            model=self.model_name,   
            messages=messages_,
            temperature=0.9,
            max_tokens=1024,
        )
        return completion.choices[0].message.content

    def RTS(self, query):
        """
        Rephrases user input.
        :param query: str, user input query.
        :return: Rephrased user query.
        """
        completion = self.client.chat.completions.create(
            model=self.model_name,   
            messages=[
                {
                    "role": "system",
                    "content": "Your an helpful assistant to rephrase the user input. The output should be \
                                only the rephrased user input without any explanation.Also do not mention anything about rephrazing in response."
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

    def groq_assistant(self, query):
        """
        Generates responses based on the user query.
        :param query: str, user input query.
        :return: Assistant's response.
        """
        completion = self.client.chat.completions.create(
            model=self.model_name,   
            messages=[
                {
                    "role": "user",
                    "content": query
                }
            ],
            temperature=0.9,
            max_tokens=1024,
        )
        return completion.choices[0].message.content


    def analyze_missing_data(self,df):
        output = "Next step is understand the missing values in data and perform missing value treatment as the first step of our machine learning project. "
        missing_data = df.isnull().sum()
        total_rows = len(df)
        for column in df.columns:
            missing_count = missing_data[column]
            if missing_count > 0:
                missing_percentage = (missing_count / total_rows) * 100
                if df[column].dtype in ["float64", "int64"]:
                    data_type = "Numerical"
                    if missing_percentage < 5:
                        suggestion = "Drop rows with missing values."
                    elif missing_percentage < 30:
                        suggestion = "Consider replacing with mean/median."
                    else:
                        suggestion = "Too many missing values; consider dropping this column."
                else:
                    data_type = "Categorical"
                    if missing_percentage < 5:
                        suggestion = "Drop rows with missing values."
                    elif missing_percentage < 25:
                        suggestion = "Consider replacing with mode or constant."
                    else:
                        suggestion = "Too many missing values; consider dropping this column."
                output += (
                    f"Column: {column}\n"
                    f" - Data Type: {data_type}\n"
                    f" - Missing Values: {missing_count} ({missing_percentage:.2f}%)\n"
                    f" - Suggestion: {suggestion}\n\n"
                )
        if not output:
            output = None
        return output

    def analyze_outliers(self,df, method="IQR", threshold=1.5):
        """
        Analyze outliers in a DataFrame and propose treatment plans for numerical columns.
        
        Parameters:
            df (pd.DataFrame): The input DataFrame.
            method (str): The method to use for outlier detection ("IQR" or "zscore").
            threshold (float): The threshold for detecting outliers.
                - For IQR: Multiple of IQR (default is 1.5).
                - For zscore: Z-score threshold (default is 3).
        
        Returns:
            pd.DataFrame: A summary of outlier statistics and proposed treatments.
        """
        # Filter for numerical columns
        num_cols = df.select_dtypes(include=[np.number]).columns
        outlier_summary = []

        for col in num_cols:
            data = df[col].dropna()  # Drop NaN values
            if method == "IQR":
                # Interquartile Range (IQR) method
                Q1 = np.percentile(data, 25)
                Q3 = np.percentile(data, 75)
                IQR = Q3 - Q1
                lower_bound = Q1 - (threshold * IQR)
                upper_bound = Q3 + (threshold * IQR)
                outliers = ((data < lower_bound) | (data > upper_bound))
            elif method == "zscore":
                # Z-score method
                mean = np.mean(data)
                std = np.std(data)
                lower_bound = mean - (threshold * std)
                upper_bound = mean + (threshold * std)
                z_scores = (data - mean) / std
                outliers = (np.abs(z_scores) > threshold)
            else:
                raise ValueError("Invalid method. Use 'IQR' or 'zscore'.")
            
            # Calculate outlier statistics
            outlier_count = np.sum(outliers)
            total_count = len(data)
            outlier_percentage = (outlier_count / total_count) * 100
            
            # Propose a treatment plan
            if outlier_percentage > 5:  # Arbitrary threshold for "significant" outliers
                treatment = "Consider capping or imputing values"
            elif outlier_percentage > 1:
                treatment = "Review outliers, capping might suffice"
            else:
                treatment = "No significant action needed"
            
            outlier_summary.append({
                "Column": col,
                "Outlier Percentage": round(outlier_percentage, 2),
                "Lower Bound": round(lower_bound, 2),
                "Upper Bound": round(upper_bound, 2),
                "Treatment Suggestion": treatment
            })
        
        # Convert summary to a DataFrame
        outlier_df = pd.DataFrame(outlier_summary)
        return outlier_df

    #updated
    def analyze_correlation(self, df, target_column):
        low_corr_list = []
        df.columns = df.columns.str.strip()
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(exclude=[np.number]).columns
        target_is_categorical = target_column in categorical_cols
        suggestions = {}

        if not target_is_categorical:
            correlation_matrix = df[numerical_cols].corr()
            corr_with_target = correlation_matrix[target_column].sort_values(ascending=False)
            low_corr_columns = corr_with_target[corr_with_target.abs() < 0.1].index.tolist()
            if low_corr_columns:
                suggestions['low_correlation_numerical'] = low_corr_columns
                low_corr_list += low_corr_columns
        else:
            label_encoder = LabelEncoder()
            encoded_target = label_encoder.fit_transform(df[target_column].astype(str))
            numerical_corr_with_target = df[numerical_cols].apply(
                lambda x: pd.Series(x).corr(pd.Series(encoded_target))
            ).sort_values(ascending=False)
            low_corr_columns = numerical_corr_with_target[numerical_corr_with_target.abs() < 0.1].index.tolist()
            if low_corr_columns:
                suggestions['low_correlation_numerical_with_categorical_target'] = low_corr_columns
                low_corr_list += low_corr_columns

        encoded_df = df.copy()
        label_encoders = {}
        for col in categorical_cols:
            if col != target_column:
                label_encoders[col] = LabelEncoder()
                encoded_df[col] = label_encoders[col].fit_transform(df[col].astype(str))

        if not target_is_categorical:
            categorical_corr_with_target = encoded_df[categorical_cols].apply(
                lambda x: x.corr(encoded_df[target_column])
            ).sort_values(ascending=False)
            low_corr_categorical_cols = categorical_corr_with_target[
                categorical_corr_with_target.abs() < 0.1
            ].index.tolist()
            if low_corr_categorical_cols:
                suggestions['low_correlation_categorical'] = low_corr_categorical_cols
                low_corr_list += low_corr_categorical_cols

        high_cardinality_cols = [col for col in categorical_cols if df[col].nunique() > 10]
        if high_cardinality_cols:
            suggestions['high_cardinality_categorical'] = high_cardinality_cols
            low_corr_list += high_cardinality_cols

        total_low_corr = len(low_corr_list)
        if total_low_corr > 0.2 * len(df.columns):
            suggestions['too_many_low_corr_columns'] = True

        suggestions['all'] = list(set(low_corr_list))
        return suggestions


    def analyze_skewness_and_variability(self,df):
        """
        Analyze each numerical column in the DataFrame for skewness and standard deviation.
        Provide suggestions to improve skewness and variability for model training.
        
        Parameters:
            df (pd.DataFrame): Input DataFrame.
            
        Returns:
            pd.DataFrame: Summary DataFrame with skewness, std deviation, and insights.
        """
        summary = []

        # Iterate through all numerical columns
        for col in df.select_dtypes(include=[np.number]).columns:
            std_dev = df[col].std()  # Standard Deviation
            skewness = df[col].skew()  # Skewness
            
            # Provide transformation suggestions based on skewness
            if skewness > 1:
                skew_insight = "Highly Positively Skewed: Apply log transformation."
            elif skewness > 0.5:
                skew_insight = "Moderately Positively Skewed: Consider square root transformation."
            elif skewness < -1:
                skew_insight = "Highly Negatively Skewed: Use power transformation (e.g., square)."
            elif skewness < -0.5:
                skew_insight = "Moderately Negatively Skewed: Consider square root transformation."
            else:
                skew_insight = "Approximately Symmetric: No transformation needed."
            
            # Spread handling (normalization/standardization suggestions)
            if std_dev > 1.5 * df[col].mean():
                spread_insight = "High Variability: Apply normalization or standardization."
            else:
                spread_insight = "Low Variability: Spread looks reasonable."

            # Append results
            summary.append({
                'Column': col,
                'Skewness': round(skewness, 2),
                'Standard Deviation': round(std_dev, 2),
                'Skewness Insight': skew_insight,
                'Spread Insight': spread_insight
            })

        # Convert summary into DataFrame
        summary_df = pd.DataFrame(summary)
        return summary_df

    def analyze_encoding_methods(self,df, is_ordinal=None):
        """
        Analyze and recommend encoding methods for categorical columns.

        Parameters:
            df (pd.DataFrame): Input DataFrame.
            is_ordinal (dict, optional): Dictionary indicating whether each column is ordinal.
                                        Example: {'col_name': True, 'col_name2': False}

        Returns:
            pd.DataFrame: Recommendations for each categorical column.
        """
        if is_ordinal is None:
            is_ordinal = {}
        
        summary = []
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        if len(categorical_cols) == 0:
            print("No categorical columns found.")
            return pd.DataFrame()
        
        for col in categorical_cols:
            unique_values = df[col].nunique()
            category_type = "Ordinal" if is_ordinal.get(col, False) else "Nominal"
            
            # Recommend encoding based on cardinality and type
            if unique_values <= 10:
                encoding = "One-Hot Encoding" if category_type == "Nominal" else "Label Encoding"
            else:
                encoding = "Label Encoding" if category_type == "Ordinal" else "Target Encoding"
            
            summary.append({
                'Column': col,
                'Unique Values': unique_values,
                'Category Type': category_type,
                'Recommended Encoding': encoding,
                'Sample Values': df[col].unique()[:5]  # Display first 5 unique values
            })
        
        summary_df = pd.DataFrame(summary)
        return summary_df

    def analyze_scaling(self,df):
        # Clean column names
        df.columns = df.columns.str.strip()

        # Selecting numerical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        # Store scaling suggestions and summary statistics
        scaling_suggestions = []

        # Analyze each numerical column
        for col in numerical_cols:
            # Check if the column has any missing values
            missing_values = df[col].isnull().sum()
            if missing_values > 0:
                scaling_suggestions.append({
                    'Column': col,
                    'Skewness': 'N/A',
                    'Mean': 'N/A',
                    'Standard Deviation': 'N/A',
                    'Min': 'N/A',
                    'Max': 'N/A',
                    'Scaling Suggestion': "Contains missing values, consider imputing or dropping"
                })
                continue

            # Descriptive statistics
            mean = df[col].mean()
            std = df[col].std()
            min_val = df[col].min()
            max_val = df[col].max()

            # Skewness
            skewness = df[col].skew()

            # Suggest scaling method based on skewness and distribution
            if abs(skewness) > 1:
                scaling_suggestion = "Highly skewed, consider applying a transformation (e.g., log transformation)"
            else:
                # Check if scaling is necessary based on standard deviation
                if std > 1:
                    scaling_suggestion = "Standardize (Z-score normalization)"
                else:
                    scaling_suggestion = "Min-Max Scaling or Robust Scaling"

            # Append the analysis for this column
            scaling_suggestions.append({
                'Column': col,
                'Skewness': round(skewness, 2),
                'Mean': round(mean, 2),
                'Standard Deviation': round(std, 2),
                'Min': round(min_val, 2),
                'Max': round(max_val, 2),
                'Scaling Suggestion': scaling_suggestion
            })

        # Convert the suggestions to a DataFrame for easy viewing
        scaling_suggestions_df = pd.DataFrame(scaling_suggestions)
        return scaling_suggestions_df


    def zai_training(self,report,columns):
        completion = self.client.chat.completions.create(
            model=self.model_name,   
            messages=[
                {
                    "role": "system",
                    "content": f"""your a helpful assistant to help user to Generate code for ML model training.\
                            Your job is to create a python code, to train a model by analyzing the analysis report of the data.
                            Data is already loaded into df (pandas Dataframe). column are {columns}.you should create a python code to train a model using pandas as sklearn (version 1.3.2) libraries.
                            then each line of code you can create in an array like.include the import statements if you use sklearn (pandas already imported).
                            Before removing duplicate or drop null values or any operation go exactly as the report.
                            [
                                'df = df.drop(columns=["Student", "address", "pincode"])',
                                'ohe = OneHotEncoder(sparse=False)',
                                'from sklearn.preprocessing import LabelEncoder',
                                'label_encoders[col] = LabelEncoder()',
                            ]. the code need to execute should always in array.Output should be an array without any explanation.
                            Use the below given template to generate the code. 
                            python```
                            import numpy as np; import pandas as pd; from sklearn.compose import ColumnTransformer; from sklearn.pipeline import Pipeline; from sklearn.preprocessing import StandardScaler, OneHotEncoder, FunctionTransformer; from sklearn.model_selection import train_test_split; from sklearn import algorithm; from sklearn.metrics import precision_score, recall_score, f1_score

                            def drop_columns(df): return df.drop(columns=["column1", "column2"], errors="ignore")
                            def handle_missing_values(df): column_name = "column_with_na"; df[column_name] = df[column_name].fillna(df[column_name].mean()); return df
                            def log_transform(X): return np.log(X + 1)

                            numerical_features = ["numerical_feature1", "numerical_feature2"]; categorical_features = ["categorical_feature1", "categorical_feature2"]
                            numerical_transformer = Pipeline(steps=[("log_transform", FunctionTransformer(log_transform, validate=False)), ("scaler", StandardScaler())])
                            categorical_transformer = Pipeline(steps=[("onehot", OneHotEncoder(handle_unknown="ignore"))])
                            preprocessor = Pipeline(steps=[("drop_columns", FunctionTransformer(drop_columns, validate=False)), ("handle_missing", FunctionTransformer(handle_missing_values, validate=False)), ("column_transform", ColumnTransformer(transformers=[("num", numerical_transformer, numerical_features), ("cat", categorical_transformer, categorical_features)]))])
                            model = algorithm(random_state=42); pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", model)])

                            df = pd.read_csv("your_dataset.csv"); X = df.drop(columns=["target_column"]); y = df["target_column"]
                            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42); pipeline.fit(X_train, y_train); y_pred = pipeline.predict(X_test)

                            accuracy = pipeline.score(X_test, y_test); precision = precision_score(y_test, y_pred); recall = recall_score(y_test, y_pred); f1 = f1_score(y_test, y_pred)
                            accuracy = ('Accuracy:', accuracy, 'Precision:', precision, 'Recall:', recall, 'F1 Score:', f1); print(accuracy)
                            Note: Do not drop the target column from the dataframe. Use the algorithm name given by user. 
                            The code need to execute should always in array.Output should be an array without any explanation.
                            """
                },
                {
                    "role": "user",
                    "content": f"""Here is the Descriptive analysis report of a dataframe.
                                <report>{report}</report>,Analyze and create a code for training the model in an array.
                                When you create the code understand the report and after removing the null values and duplicate, first understand the columns which is not required for training and perform imputation.
                                followed by that write the code for necessary feature engineering methods as described in the report.
                                After that Create a sklearn pipeline where transformations and model is there like 
                                pipeline = Pipeline(steps=[
                                    ('preprocessor', preprocessor),
                                    ('classifier', model)
                                ]).
                                After that write code for perform the validation of model and the metrics store in variable named 'accuracy' as a string variale.    
                                All this code should be in an single array.Each item in array will be single line code.Use the intentation required properly in code.                       
                                """
                }
            ],
            temperature=0.9,
            max_tokens=1024,
        )
        return completion.choices[0].message.content
