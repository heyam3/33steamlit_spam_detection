# Import Necessary Libraries
import numpy as np
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split  
from sklearn.metrics import accuracy_score 
from sklearn.metrics import confusion_matrix
from sklearn. metrics import classification_report, roc_auc_score, roc_curve
import pickle
import streamlit as st
import matplotlib.pyplot as plt
from sklearn import metrics
import seaborn as sns

# 1. Read data
data = pd.read_csv("spam.csv", encoding='latin-1')

#--------------
# GUI
st.markdown(
    """
<style>
span[data-baseweb="tag"] {
  background-color: blue !important;
}
</style>
""",
    unsafe_allow_html=True,
)
st.title("Spam Detection in SMS (text) data using Machine Learning")
st.write("## Ham vs Spam")

# Upload file
uploaded_file = st.file_uploader("Choose a file", type=['csv'])
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file, encoding="latin-1")
    data.to_csv("spam_new.csv", index=False)


# 2. Data pre-processing
source = data['v2']
target = data['v1']
# ham = 0, spam = 1
target = target.replace("ham", 0)
target = target.replace("spam", 1)

text_data = np.array(source)

count = CountVectorizer(max_features=6000)
count.fit(text_data)
bag_of_words = count.transform(text_data)

X = bag_of_words.toarray()

y = np.array(target)

# 3. Build model
df_spam  = data[data.v1 == 'spam'].copy()
df_ham = data[data.v1 == 'ham'].copy()

import wordcloud

def generate_wordcloud(data_frame, v1):
    text = ' '.join(data_frame['v2'].astype(str).tolist())
    stopwords = set(wordcloud.STOPWORDS)
    
    fig_wordcloud = wordcloud.WordCloud(stopwords=stopwords,background_color='lightgrey',
                    colormap='viridis', width=800, height=600).generate(text)
    
    plt.figure(figsize=(10,7), frameon=True)
    plt.imshow(fig_wordcloud)  
    plt.axis('off')
    plt.title(v1, fontsize=20 )
    plt.show()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=0) 

clf = MultinomialNB()
model = clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

#4. Evaluate model
score_train = model.score(X_train,y_train)
score_test = model.score(X_test,y_test)
acc = accuracy_score(y_test,y_pred)
cm = confusion_matrix(y_test, y_pred, labels=[0, 1])

cr = classification_report(y_test, y_pred)

y_prob = model.predict_proba(X_test)
roc = roc_auc_score(y_test, y_prob[:, 1])

#5. Save models
# model classication
pkl_filename = "ham_spam_model.pkl"  
with open(pkl_filename, 'wb') as file:  
    pickle.dump(model, file)
  
# model CountVectorizer (count)
pkl_count = "count_model.pkl"  
with open(pkl_count, 'wb') as file:  
    pickle.dump(count, file)


#6. Load models 
# Đọc model
# import pickle
with open(pkl_filename, 'rb') as file:  
    ham_spam_model = pickle.load(file)
# doc model count len
with open(pkl_count, 'rb') as file:  
    count_model = pickle.load(file)

# GUI
menu = ["Business Objective", "Build Project", "New Prediction"]
choice = st.sidebar.selectbox("Menu", menu)
if choice == "Business Objective":
    st.subheader("Business Objective")
    st.write("""
	    ###### The quickest and most convenient sources of information today are the internet and social media. 
	    The most important information sources are reviews, opinions, feedback, communications, and suggestions.
	    We may now extract useful information from such data by utilizing technological advancements like Natural 
	    Language Processing (NLP) approaches.NLP, a subfield of artificial intelligence (AI), uses computers and 
	    human natural language to generate useful data. We employ NLP for text classification tasks like document 
	    categorization, sentiment analysis, text generation, and spam detection.
	    Classifying spam and ham messages is one of the most common natural language processing tasks for emails and chat engines.
	    With the advancements in machine learning and natural language processing techniques, it is now possible to separate spam 
	    messages from ham messages with a high degree of accuracy.
	    """)  
    st.write("""###### => Problem/ Requirement: Use Machine Learning algorithms in Python for ham and spam message classification.""")
    st.image("ham_spam.jpg")
    
elif choice == "Build Project":
    st.subheader("Build Project")
    st.write("##### 1.Using head() and tail() function ")
    st.dataframe(data[["v2", "v1"]].head(3))
    st.dataframe(data[["v2", "v1"]].tail(3))

    st.write("##### 2. Visuzlize Ham and Spam")
    fig1 = sns.countplot(data=data[["v1"]], x="v1")
    st.pyplot(fig1.figure)

    st.write("##### 3. Word Cloud Generation...")
    st.set_option('deprecation.showPyplotGlobalUse', False)
    fig4 = generate_wordcloud(df_spam, 'SPAM')
    st.write(" ")
    st.pyplot(fig4)
    fig5 = generate_wordcloud(df_ham, 'HAM')
    st.pyplot(fig5)
    st.write("##### 4. Evaluation")
    st.code("Score train:" + str(round(score_train, 2)) +  "vs Score test:" + str(round(score_test, 2)))
    st.code("Accuracy:" + str(round(acc, 2)))
    st.write("###### Classification report:")
    st.code(cr)
    st.write("###### Confusion matrix:")
    st.code(cm)
    st.write("###### Heapmap of Conusion matrix:")
    
    group_names = ['True Neg','False Pos','False Neg','True Pos']
    group_counts = ["{0:0.0f}".format(value) for value in
                cm.flatten()]
    group_percentages = ["{0:.2%}".format(value) for value in
                     cm.flatten()/np.sum(cm)]
    labels = [f"{v1}\n{v2}\n{v3}" for v1, v2, v3 in
          zip(group_names,group_counts,group_percentages)]
    labels = np.asarray(labels).reshape(2,2)
    fig2=sns.heatmap(cm, annot=labels,fmt='', cmap='Blues')
    st.pyplot(fig2.figure)
    
    
    # Calculate ROC Curve
    st.write("###### ROC Curve")
    fpr, tpr, threholds = roc_curve(y_test, y_prob[:, 1])
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1], linestyle="--")
    ax.plot(fpr, tpr, marker=".")
    st.pyplot(fig)
    st.code("ROC AUC Score:" + str(round(roc, 2)))

    st.write("##### 5. Summary: This model is good enough for Ham vs Spam classification.")

elif choice =="New Prediction":
    st.subheader("Select data")
    flag = False
    lines = None
    type = st.radio("Upload data or Input data?", options=("Upload", "Input"))
    if type == "Upload":
        # Upload file
        uploaded_file_1 = st.file_uploader("Choose a file", type=["txt", "csv"])
        if uploaded_file_1 is not None:
            lines = pd.read_csv(uploaded_file_1, header=None)
            st.dataframe(lines)
            # st.write(lines.columns)
            lines = lines[0]
            flag = True
        if flag:
            st.write("Content:")
            if len(lines)>0:
                st.code(lines)
                x_new = count_model.transform(lines)
                y_pred_new = ham_spam_model.predict(x_new)
                st.code("New predictions (0: Ham, 1: Spam): " + str(y_pred_new))    
    if type == "Input":
        email = st.text_area(label="Input your content:")
        if email != "":
            lines = np.array([email])
            flag = True

        if flag:
            st.write("Content:")
            if len(lines)>0:
                st.code(lines)
                x_new = count_model.transform(lines)
                y_pred_new = ham_spam_model.predict(x_new)
                st.code("New predictions (0: Ham, 1: Spam): " + str(y_pred_new))
        



