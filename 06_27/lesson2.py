import streamlit as st
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Heiti TC', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

st.title('手機品牌市占率圓餅圖')

labels = ['Nokia', 'Samsung', 'Apple', 'Lumia']
sizes = [20, 30, 45, 10]
colors = ['yellow', 'green', 'red', 'blue']
explode = (0.3, 0, 0, 0)

fig, ax = plt.subplots()
ax.pie(sizes, explode=explode, labels=labels, colors=colors,
       autopct='%1.1f%%', shadow=True, startangle=180)

st.pyplot(fig)
