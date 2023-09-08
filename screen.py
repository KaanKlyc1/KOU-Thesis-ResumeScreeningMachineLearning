import glob
import os
import warnings

from flask import (Flask, json, Blueprint, jsonify, redirect, render_template, request,
                   url_for)
from gensim.summarization import summarize
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.neighbors import NearestNeighbors,KernelDensity
from sklearn.neural_network import BernoulliRBM
from sklearn import linear_model
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from werkzeug.utils import secure_filename
from text_process import STOPWORDS

from pdfminer import high_level


warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')

tr_stopwords = list(STOPWORDS)


class ResultElement:
    def __init__(self, rank, name, phone, mail, filename):
         #BİLGİLERİ EKLE
        self.name = name
        self.phone = phone
        self.mail = mail
        self.rank = rank
        self.filename = filename


def getfilepath(loc):
    temp = str(loc)
    temp = temp.replace('\\', '/')
    return temp


def res(jobfile):
    Resume_Vector = []
    Ordered_list_Resume = []
    Ordered_list_Resume_Score = []
    Names = []
    PhoneNos = []
    Mails = []
    LIST_OF_FILES = []
    LIST_OF_FILES_PDF = []
    
    Resumes = []
    Temp_pdf = []

    os.chdir('./Tr_Resumes')
    for file in glob.glob('**/*.pdf', recursive=True):
        LIST_OF_FILES_PDF.append(file)
    

    LIST_OF_FILES =LIST_OF_FILES_PDF
    # LIST_OF_FILES.remove("antiword.exe")
    print("This is LIST OF FILES")
    print(LIST_OF_FILES)

    # print("Total Files to Parse\t" , len(LIST_OF_PDF_FILES))
    print("####### PARSING ########")
    for nooo,i in enumerate(LIST_OF_FILES):
        Ordered_list_Resume.append(i)
        Temp = i.split(".")
        if Temp[1] == "pdf" or Temp[1] == "Pdf" or Temp[1] == "PDF":
            try:
                print("This is PDF" , nooo)
                print("DOSYA:")
                print(i)
###############################################################################                
                
                read_pdf2=high_level.extract_text(i)
                print("DENEME:")
                print(read_pdf2)
                    # page = read_pdf.getPage(0)
                    # page_content = page.extractText()
                    # Resumes.append(Temp_pdf)

                Temp_pdf = read_pdf2.replace("\n", " ")
                    
                Temp_pdf = (Temp_pdf)+ ""
                        # Temp_pdf.append(page_content)
                        # print(Temp_pdf)
                Resumes.extend([Temp_pdf])

                #BURADA BİLGİ ÇIKART
                x = Temp_pdf.split(" ")
                y = read_pdf2.split("\n")
                cv_name = y[0]
                iter = 0
                for i in x:
                 if i == "Telefon:" or i == "Tel:" or i == "Tel No:" or i == "Telefon":
                  cv_tel = x[iter+1]
                  if (x[iter+2]).isnumeric():
                   cv_tel = cv_tel + x[iter+2]
                 if i.isnumeric() and len(i) == 11:
                     cv_tel = i  
                 if i == "E-posta:" or i == "Eposta:" or i == "E-mail:" or i == "Email:" or i == "Mail:"  or i == "Posta:" or i == "Email":       
                   cv_mail = x[iter+1]
                 if "@gmail.com" in i:
                     cv_mail = i  
      
                 iter+= 1
                Names.append(cv_name)
                PhoneNos.append(cv_tel)  
                Mails.append(cv_mail)      
                print(cv_name)
                print(cv_tel)
                print(cv_mail)
                Temp_pdf = ''
                iter = 0
                cv_name = ''
                cv_tel = ""
                cv_mail = ""
                    # f = open(str(i)+str("+") , 'w')
                    # f.write(page_content)
                    # f.close()
            except Exception as e: print(e)
###########################################################            
       

   
   
    print("Done Parsing.")



    Job_Desc = 0
    LIST_OF_TXT_FILES = []
    os.chdir('../Job_Description')
    f = open(jobfile , 'r', encoding='utf-8')
    text = f.read()
        
    try:
        tttt = str(text)
        tttt.replace("\n"," ")
        tttt = summarize(tttt, word_count=100)
        print("İŞ AÇIKLAMASI ÖZET:")
        print(tttt)
        text = [tttt]
    except:
        text = 'None'

    f.close()
    print("İŞ AÇIKLAMASI:")
    print(text)
    vectorizer = TfidfVectorizer(stop_words=tr_stopwords)
    
    vectorizer.fit(text)
    
    vector = vectorizer.transform(text)
    
    Job_Desc = vector.toarray()
    # print("\n\n")
    print(Job_Desc)

    os.chdir('../')
    for i in Resumes:

        text = i
        tttt = str(text)
        try:
            tttt = summarize(tttt, word_count=100) 
            text = [tttt]
            print("CV ÖZET:")
            print(text)
            vector = vectorizer.transform(text)

            aaa = vector.toarray()
            Resume_Vector.append(vector.toarray())
        except:
            pass
    # print(Resume_Vector)
    #
    for i in Resume_Vector:

        samples = i
        print("SAMPLES:")
        print(samples)
        neigh = NearestNeighbors(n_neighbors=1)
        neigh.fit(samples) 
        NearestNeighbors(algorithm='auto', leaf_size=30)
        print("ALGORİTMAYA VERİLEN:")
        print(neigh.kneighbors(Job_Desc)[0][0])
        Ordered_list_Resume_Score.extend(neigh.kneighbors(Job_Desc)[0][0].tolist())
    ################################################################################## 
    Z = [x for _,x in sorted(zip(Ordered_list_Resume_Score,Ordered_list_Resume))]

    y = sorted(zip(Ordered_list_Resume_Score, zip(Names,PhoneNos,Mails,Ordered_list_Resume)))
    w = [n for n in zip(*y)]
    print("SIRALANMIŞ LİSTELER:")
    print(list(w[0]),list(w[1]),tuple(list(a) for a in zip(*w[1])))

    print(Ordered_list_Resume)
    print("SKORLAR:")
    print(Ordered_list_Resume_Score)
    flask_return = []
    # for n,i in enumerate(Z):
    #     print("Rankkkkk\t" , n+1, ":\t" , i)
    for n,i in enumerate(list(w[1])):
        # print("Rank\t" , n+1, ":\t" , i)
        # flask_return.append(str("Rank\t" , n+1, ":\t" , i))
        name = i[0]
        phoneno = i[1]
        mail = i[2]
        filename = getfilepath(i[3])
        #name = name.split('.')[0]
        rank = n+1
         #BİLGİLERİ EKLE
        res = ResultElement(rank,name,phoneno,mail, filename)
        flask_return.append(res)
        # res.printresult()
        print(f"Rank{res.rank} :\t {res.filename}")
    return flask_return



if __name__ == '__main__':
    inputStr = input("")
    set(inputStr)

