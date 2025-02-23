import streamlit as st
import pandas as pd
import os
from io import BytesIO
import plotly.express as px
from summary_data import generate_summary


st.set_page_config(page_title="Data Sweeper!", layout="wide")
st.title("Data Sweeper")
st.write("Transform your files between CSV and Excel format with built-in data cleaning and visualzaition!")

uploaded_files = st.file_uploader("Upload Files", type=["csv", "xlsx", "json"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_extension = os.path.split(file.name)[-1].split('.')[-1]

        if(file_extension == "csv"):
            
            df = pd.read_csv(file)
        elif file_extension == "xlsx":
            df = pd.read_excel(file)
        elif file_extension == "json":
            df = pd.read_json(file)
        else: 
            st.error(f"Unsupported File Format .{file_extension}")
            continue

        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size/1024}")

        st.write("Preview the head of data")
        st.dataframe(df.head())
        st.write("Overview of Data")
        st.dataframe(df.describe())

        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean data for {file.name}"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Remove Duplicates"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed!")
            with col2:
                if st.button("Fill Missing Values"):
                        numeric_cols = df.select_dtypes(include=["number"]).columns
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.write("Missing Values Filled!")
            

            st.subheader("🛠️ Advanced Data Cleaning Options")
            if st.checkbox("Drop Columns with Too Many Missing Values"):

                threshold = st.slider("Set missing value threshold (%)", 10, 90, 50)

                missing_percent = df.isnull().mean() * 100

                cols_to_drop = missing_percent[missing_percent > threshold].index

                df.drop(columns=cols_to_drop, inplace=True)
                st.write(f"Dropped Columns: {list(cols_to_drop)}")

            if st.checkbox("Handle Outliers (Using IQR Method)"):
                num_cols = df.select_dtypes(include=["number"]).columns
                selected_col = st.selectbox("Select a column to remove outliers", num_cols)
                
                Q1 = df[selected_col].quantile(0.25)
                Q3 = df[selected_col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                df = df[(df[selected_col] >= lower_bound) & (df[selected_col] <= upper_bound)]
                st.write(f"Outliers removed from {selected_col}")

            if st.checkbox("Convert Data Types"):
                num_cols = df.select_dtypes(include=["number"]).columns
                col = st.selectbox("Choose a column to convert", num_cols)
                new_type = st.radio("Convert to:", ["Integer", "Float", "String", "Date"])
                
                try:
                    if new_type == "Integer":
                        df[col] = df[col].astype(int)
                    elif new_type == "Float":
                        df[col] = df[col].astype(float)
                    elif new_type == "String":
                        df[col] = df[col].astype(str)
                    elif new_type == "Date":
                        df[col] = pd.to_datetime(df[col], errors="coerce")
                    st.success(f"Converted {col} to {new_type}")
                except Exception as e:
                    st.error(f"Conversion failed: {e}")
            st.dataframe(df.head())
                    
        st.subheader("Select columns to convert")
        columns = st.multiselect("Choose Columns to keep", df.columns, default=df.columns)
        df = df[columns]



        st.subheader("Data Visualization")
        if st.checkbox("Show Visualization"):
            numeric_cols = df.select_dtypes(include=["number"]).columns
            selected_cols = st.multiselect("Select Columns to Visualize", numeric_cols, default=numeric_cols[:1])
            
            chart_type = st.radio("Select Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart"])

            if selected_cols:
                if chart_type == "Bar Chart":
                    fig = px.bar(df, x=df.index, y=selected_cols, title="Bar Chart")
                elif chart_type == "Line Chart":
                    fig = px.line(df, x=df.index, y=selected_cols, title="Line Chart")
            
                elif chart_type == "Scatter Plot":
                    fig = px.scatter(df, x=selected_cols[0], y=selected_cols[1] if len(selected_cols) > 1 else selected_cols[0], title="Line Chart")
                elif chart_type == "Pie Chart":
                    if len(selected_cols) == 1: 
                        fig = px.pie(df, names=df.index, values=selected_cols[0], title="Pie Chart")
                    else:
                        st.warning("Pie Chart can only be created with one column. Please Select atleast one column.")
                st.plotly_chart(fig, True)
            else:
                st.warning("Please select at least on column for visualization.")


        st.subheader("Generate Summary!")
        if st.button("Generate Detailed Summary"):
            st.write_stream(generate_summary(df))


        st.subheader("Conversion Options")
        conversion_types = st.radio("Convert file to ", ["CSV", "Excel", "JSON"], key=file.name)
        if st.button("Start Conversion"):
            buffer = BytesIO()
            
            if conversion_types == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_extension, conversion_types.lower())
                mime_type = "text/csv"

            elif conversion_types == "Excel":
                df.to_excel(buffer, index=False)
                file_name = file.name.replace(file_extension, "xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


            elif conversion_types == "JSON":
                df.to_json(buffer)
                file_name = file.name.replace(file_extension, conversion_types.lower())
                mime_type = "application/json"
            else:
                st.error("Got Issue on Conversion")
            buffer.seek(0)



            st.download_button("Download Now", buffer, file_name, mime=mime_type)
            st.success("File is ready to download!")
            