import pandas as pd
import streamlit as st
import plotly.express as px
import requests
import config
from openai_utils import check_business_type_similarity

st.set_page_config(page_title="Clients information", page_icon=":bar_chart:")

df = pd.read_excel(
    "C:/Users/Qalam/PycharmProjects/pythonProject2/pythonWorkProjects/12_06_2024ExcelDataST/dataSet"
    "/fake_data_with_city.xlsx"
)

st.dataframe(df)

if 'city' not in st.session_state:
    st.session_state['city'] = df["City"].unique().tolist()
if 'gender' not in st.session_state:
    st.session_state['gender'] = df["Gender"].unique().tolist()
if 'nation' not in st.session_state:
    st.session_state['nation'] = df["Nation"].unique().tolist()
if 'education' not in st.session_state:
    st.session_state['education'] = df["Образование"].unique().tolist()
if 'product' not in st.session_state:
    st.session_state['product'] = df["Product line"].unique().tolist()
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = config.SUPPORTED_MODELS[0]

st.sidebar.header("Please filter here:")

city = st.sidebar.multiselect("Select the City:", options=df["City"].unique(), default=st.session_state['city'])
gender = st.sidebar.multiselect("Select the Gender:", options=df["Gender"].unique(), default=st.session_state['gender'])
nation = st.sidebar.multiselect("Select the Nation:", options=df["Nation"].unique(), default=st.session_state['nation'])
education = st.sidebar.multiselect("Select the Education:", options=df["Образование"].unique(),
                                   default=st.session_state['education'])
product = st.sidebar.multiselect("Select the Product line:", options=df["Product line"].unique(),
                                 default=st.session_state['product'])

# Update session state with current filter values
st.session_state['city'] = city
st.session_state['gender'] = gender
st.session_state['nation'] = nation
st.session_state['education'] = education
st.session_state['product'] = product

df_selection = df[
    (df["City"].isin(city)) &
    (df["Gender"].isin(gender)) &
    (df["Nation"].isin(nation)) &
    (df["Образование"].isin(education)) &
    (df["Product line"].isin(product))
    ]

st.dataframe(df_selection)

st.title(":bar_chart: Sales Dashboard")
st.markdown("##")

if not df_selection.empty:
    total_sales = int(df_selection["Total"].sum())
    average_rating = round(df_selection["Rating"].mean(), 1)
    star_rating = ":star:" * int(round(average_rating, 0))
    average_sale_by_transaction = round(df_selection["Total"].mean(), 2)

    left_column, middle_column, right_column = st.columns(3)
    with left_column:
        st.subheader("Total Sales:")
        st.subheader(f"US $ {total_sales:,}")
    with middle_column:
        st.subheader("Average Rating:")
        st.subheader(f"{average_rating} {star_rating}")
    with right_column:
        st.subheader("Average Sales Per Transaction:")
        st.subheader(f"US $ {average_sale_by_transaction}")

    st.markdown('---')

    if "Product line" in df.columns and "Total" in df.columns:
        sales_by_product_line = df_selection.groupby(by=["Product line"])["Total"].sum().sort_values()
        fig_product_sales = px.bar(
            sales_by_product_line,
            x=sales_by_product_line.values,
            y=sales_by_product_line.index,
            orientation="h",
            title="<b>Sales by product line</b>",
            color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
            template="plotly_white",
        )
        st.plotly_chart(fig_product_sales)
    else:
        st.write("The dataset does not contain 'Product line' or 'Total' columns.")
else:
    st.write("No data available for the selected filters.")

url = 'http://127.0.0.1:8000/date-check/'

model_name = st.sidebar.radio("Выберите модель для использования:", config.SUPPORTED_MODELS,
                              index=config.SUPPORTED_MODELS.index(st.session_state['model_name']))

# Update session state with current model name
st.session_state['model_name'] = model_name

# Контейнер для пользовательского ввода и ответов AI
input_container = st.container()

if 'responses' not in st.session_state:
    st.session_state['responses'] = []

with input_container:
    user_input_date = st.date_input('Выберите дату').strftime('%d/%m/%Y')
    user_query = st.text_area('Введите ваш запрос:')

    if st.button('Отправить запрос'):
        if user_input_date and user_query:
            json_data = {"user_input_date": user_input_date}
            response = requests.post(url, json=json_data)

            if response.status_code == 200:
                response_data = response.json()

                context = f'''
                Информация о фильтрации:
                Города: {city}
                Пол: {gender}
                Нация: {nation}
                Образование: {education}
                Линия продукции: {product}

                Date info: {response_data}
                Отфильтрованные данные:
                {df_selection.to_string(index=False)}
                '''
                context += f'Пользовательский запрос: {user_query}. '
                context += f'Дата: {user_input_date}. '

                AI_response = check_business_type_similarity(context, st.session_state['model_name'])

                st.success("Запрос выполнен успешно!")

                st.session_state.responses.append((user_query, AI_response))

                # Удаление старых записей
                if len(st.session_state.responses) > 4000:
                    st.session_state.responses = st.session_state.responses[-4000:]

            else:
                st.error(f"Ошибка! Код ответа: {response.status_code}")
                st.error(f"Сообщение об ошибке: {response.text}")
        else:
            st.error("Пожалуйста, заполните оба поля.")

# Отображение текущих ответов AI
for query, response in st.session_state.responses:
    st.markdown("**Запрос:**")
    st.write(query)
    st.markdown("**Ответ AI:**")
    st.write(response)
    st.markdown("---")
