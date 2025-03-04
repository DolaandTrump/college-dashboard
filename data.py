import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

#Improve width
st.set_page_config(
    page_title="College Dashboard",
    layout="wide"
)


# Load Excel files
df_main = pd.read_excel("Data.xlsx")
df_strength = pd.read_excel("Data_Strength_Adm.xlsx")
df_gender_cat = pd.read_excel("Data1_Str_Gender_CatWise.xlsx")

# Merge datasets
df_combined = df_main.merge(df_strength[['College', 'Strength', 'Admission']], on='College', how='left')
df_combined = df_combined.merge(df_gender_cat[['College', 'Male', 'Female', 'SC', 'ST', 'Gen']], on='College', how='left')

# Compute Vacancy for each college
df_combined['Vacancy'] = df_combined['Strength'] - df_combined['Admission']

# Round off numeric columns safely
for col in ['Male', 'Female', 'SC', 'ST', 'Gen']:
    df_combined[col] = df_combined[col].apply(lambda x: np.round(x) if pd.notna(x) else None)

# Set up the page title
st.title("College Dashboard")

# Create a horizontal layout for the three dropdowns
col1, col2, col3 = st.columns(3)

# District Dropdown: get unique districts and sort them
unique_districts = sorted(df_combined['District Name'].dropna().unique())
selected_district = col1.selectbox("Select a District", unique_districts)

# Filter the DataFrame based on the selected district
if selected_district:
    district_df = df_combined[df_combined['District Name'] == selected_district]
    # Block Dropdown: get unique blocks within the selected district
    block_options = sorted(district_df['Block/ULB Name'].dropna().unique())
    block_options = ["Select Block"] + block_options
    selected_block = col2.selectbox("", block_options, index=0)
else:
    district_df = pd.DataFrame()
    selected_block = "Select Block"

# College Dropdown: update available colleges based on selected block and district
if selected_block != "Select Block":
    block_df = district_df[district_df['Block/ULB Name'] == selected_block]
    college_options = sorted(block_df['College'].unique())
    college_options = ["Select College"] + college_options
    selected_college = col3.selectbox("", college_options, index=0)
else:
    selected_college = "Select College"

# Displaying total colleges and blocks
if selected_district and not district_df.empty:
    total_colleges = district_df['College'].nunique()
    total_blocks = district_df['Block/ULB Name'].nunique()
    st.markdown(f"**Total Colleges in {selected_district}: {total_colleges}**")
    st.markdown(f"**Total Blocks in {selected_district}: {total_blocks}**")

district_df = district_df.drop_duplicates(subset=['College'])

plot_config = {"displayModeBar": False}

# Display District-level Charts
if selected_district:
    # Count colleges per block in the selected district
    block_counts = district_df['Block/ULB Name'].value_counts()
    
    # Bar Chart: Number of Colleges per Block
bar_fig = px.bar(
    x=block_counts.index,
    y=block_counts.values,
    text=block_counts.values,
    labels={'x': 'Block', 'y': 'Number of Colleges'},
    title=f"Number of Colleges in {selected_district}",
    color=block_counts.values,
    color_continuous_scale='Blues',
    template='plotly_white'
)
bar_fig.update_traces(textposition='outside', cliponaxis=False, hoverinfo="none", hovertemplate=None)

# Pie Chart: Distribution of Colleges among Blocks
pie_fig = px.pie(
    names=block_counts.index,
    values=block_counts.values,
    title=f"College Distribution in {selected_district}",
    hole=0.4,
    template="plotly_white",
    color_discrete_sequence=px.colors.qualitative.Set3
)
pie_fig.update_traces(hovertemplate='District=%{label}<br>No. of Colleges=%{value}<extra></extra>')

# Display the two charts side by side using columns
chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.plotly_chart(bar_fig, use_container_width=True, config=plot_config)
with chart_col2:
    st.plotly_chart(pie_fig, use_container_width=True, config=plot_config)


# Display College-specific Charts if a college is selected
if selected_college != "Select College":
    college_df = df_combined[df_combined['College'] == selected_college]
    if not college_df.empty:
        # Safely extract values for the selected college
        strength = college_df['Strength'].values[0] if 'Strength' in college_df and not college_df['Strength'].isna().all() else None
        admission = college_df['Admission'].values[0] if 'Admission' in college_df and not college_df['Admission'].isna().all() else None
        vacancy = college_df['Vacancy'].values[0] if 'Vacancy' in college_df and not college_df['Vacancy'].isna().all() else None
        male = college_df['Male'].values[0] if 'Male' in college_df and not college_df['Male'].isna().all() else None
        female = college_df['Female'].values[0] if 'Female' in college_df and not college_df['Female'].isna().all() else None
        sc = college_df['SC'].values[0] if 'SC' in college_df and not college_df['SC'].isna().all() else None
        st_val = college_df['ST'].values[0] if 'ST' in college_df and not college_df['ST'].isna().all() else None
        gen = college_df['Gen'].values[0] if 'Gen' in college_df and not college_df['Gen'].isna().all() else None

        missing_data_messages = []

        st.subheader("College Details")
        # Create three columns for detailed charts
        dcol1, dcol2, dcol3 = st.columns(3)

        # Student Data Bar Chart: Strength, Admission, Vacancy
        if strength is not None and admission is not None and vacancy is not None:
            fig_data = px.bar(
                x=['Strength', 'Admission', 'Vacancy'],
                y=[strength, admission, vacancy],
                labels={'x': '', 'y': 'Number of Seats'},
                title="Student Data",
                text_auto=True,
                template='plotly_white',
                color=['#3498db', '#2ecc71', '#e74c3c']
            )
            fig_data.update_layout(showlegend=False)
            fig_data.update_traces(hoverinfo="none", hovertemplate=None)
            dcol1.plotly_chart(fig_data, use_container_width=True, config=plot_config)
        else:
            missing_data_messages.append("Student data not available")

        # Gender Pie Chart
        if male is not None and female is not None:
            fig_gender = px.pie(
                names=['Male', 'Female'],
                values=[male, female],
                title="Gender Distribution",
                template='plotly_white',
                color_discrete_sequence=['#2980b9', '#e74c3c']
            )
            dcol2.plotly_chart(fig_gender, use_container_width=True, config=plot_config)
            fig_gender.update_traces(
        hovertemplate='Gender = %{label}<br>No. of Students = %{value}<extra></extra>'
    )
        else:
            missing_data_messages.append("Gender data not available")

        # Category Pie Chart
        if sc is not None and st_val is not None and gen is not None:
            fig_category = px.pie(
                names=['SC', 'ST', 'General'],
                values=[sc, st_val, gen],
                title="Category Distribution",
                template='plotly_white',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_category.update_traces(hovertemplate='Category = %{label}<br>No. of Students = %{value}<extra></extra>')
            dcol3.plotly_chart(fig_category, use_container_width=True, config=plot_config)
        else:
            missing_data_messages.append("Category data not available")
            
        if missing_data_messages:
            st.error(" | ".join(missing_data_messages))
