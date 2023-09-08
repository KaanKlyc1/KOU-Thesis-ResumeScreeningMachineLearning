import glob
import os
import warnings

from flask import (Flask, json, Blueprint, jsonify, redirect, render_template, request,
                   url_for)
from gensim.summarization import summarize
from sklearn.neighbors import NearestNeighbors
from pdfminer import high_level


warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')

app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = 'Tr_Resumes/'
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


class ResultElement:
    def __init__(self, rank, name, phone, mail, filename):
         #BİLGİLERİ EKLE
        self.name = name
        self.phone = phone
        self.mail = mail
        self.rank = rank
        self.filename = filename


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']




import re, string, unicodedata
import nltk
import contractions
import inflect
from bs4 import BeautifulSoup
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer
from snowballstemmer import TurkishStemmer

def remove_non_ascii(words):
    """Remove non-ASCII characters from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    return new_words

def to_lowercase(words):
    """Convert all characters to lowercase from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = word.lower()
        new_words.append(new_word)
    return new_words

def remove_punctuation(words):
    """Remove punctuation from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = re.sub(r'[^\w\s]', '', word)
        if new_word != '':
            new_words.append(new_word)
    return new_words

def replace_numbers(words):
    """Replace all interger occurrences in list of tokenized words with textual representation"""
    p = inflect.engine()
    new_words = []
    for word in words:
        if word.isdigit():
            new_word = p.number_to_words(word)
            new_words.append(new_word)
        else:
            new_words.append(word)
    return new_words

def remove_stopwords(words):
    """Remove stop words from list of tokenized words"""
    new_words = []
    for word in words:
        # print(word)
        if word not in stopwords.words('turkish'):
            new_words.append(word)
    return new_words

def stem_words(words):
    """Stem words in list of tokenized words"""
    stemmer = TurkishStemmer()
    stems = []
    for word in words:
        stem = stemmer.stemWord(word)
        stems.append(stem)
    return stems

def lemmatize_verbs(words):
    """Lemmatize verbs in list of tokenized words"""
    lemmatizer = WordNetLemmatizer()
    lemmas = []
    for word in words:
        lemma = lemmatizer.lemmatize(word, pos='v')
        lemmas.append(lemma)
    return lemmas

def normalize(words):
    words = remove_non_ascii(words)
    words = to_lowercase(words)
    words = remove_punctuation(words)
    # words = replace_numbers(words)
    words = remove_stopwords(words)
    # words = stem_words(words)
    words = lemmatize_verbs(words)
    return words
def getfilepath(loc):
    temp = str(loc)
    temp = temp.replace('\\', '/')
    return temp

def res(jobfile):
    Final_Array = []
    
    def lcs(X, Y):
        try:
            mat = []
            for i in range(0,len(X)):
                row = []
                for j in range(0,len(Y)):
                    if X[i] == Y[j]:
                        if i == 0 or j == 0:
                            row.append(1)
                        else:
                            val = 1 + int( mat[i-1][j-1] )
                            row.append(val)
                    else:
                        row.append(0)
                mat.append(row)
            new_mat = []
            for r in  mat:
                r.sort()
                r.reverse()
                new_mat.append(r)
            lcs = 0
            for r in new_mat:
                if lcs < r[0]:
                    lcs = r[0]
            return lcs
        except:
            return -9999
    
    
    
    def semanticSearch(searchString, searchSentencesList):
        result = None
        bestScore = 0
        for i in searchSentencesList:
            score = lcs(searchString, i)
            print(score , i[0:100])
            print("")
            temp = [score]
            Final_Array.extend(temp)
            if score > bestScore:
                bestScore = score
                result = i
        return result
    
    app.config['UPLOAD_FOLDER'] = 'Tr_Resumes/'
    app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


    Resume_Vector = []
    Ordered_list_Resume = []
    Ordered_list_Resume_Score = []
    LIST_OF_FILES = []
    LIST_OF_FILES_PDF = []
    
    Resumes_File_Names = []
    Resumes = []
    Names = []
    PhoneNos = []
    Mails = []
    Temp_pdf = ''
    os.chdir('./Tr_Resumes')
    for file in glob.glob('**/*.pdf', recursive=True):
        LIST_OF_FILES_PDF.append(file)
    

    LIST_OF_FILES =  LIST_OF_FILES_PDF
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
                    
            except Exception as e: print(e)
        


    

    for m,i in enumerate(Resumes):
        Resumes[m] = nltk.word_tokenize(Resumes[m],'turkish')
        Resumes[m] = normalize(Resumes[m])
        Resumes[m] = ' '.join(map(str, Resumes[m]))

    jobfile = nltk.word_tokenize(jobfile,'turkish')
    jobfile = normalize(jobfile)
    jobfile = ' '.join(map(str, jobfile))
   
    print("This is len Resumes : " , len(Resumes))
    os.chdir('../')
        
    print("#############################################################")
    # a = input("Enter String to Search : ")
    print("\n\n")
    print("Printing Scores of all Resumes...")
    print("\n")
    result = semanticSearch(jobfile, Resumes)
    print("\n")
    print("Printing 1 Best Result.....")
    print("\n")
    print (result)
    print("\n\n")
    print("#########################################################")
    print("#########################################################")
    print("#########################################################")
    print("#########################################################")
    print("\n\n")
    print(Final_Array)
    print("This is len Final_Array : " , len(Final_Array))
    print(Ordered_list_Resume)
    print("This is len Ordered_list_Resume : " , len(Ordered_list_Resume))
    
    # print(Ordered_list_Resume)

    #Z = [x for _,x in sorted(zip(Final_Array,Ordered_list_Resume) , reverse=True)]

    y = sorted(zip(Final_Array, zip(Names,PhoneNos,Mails,Ordered_list_Resume)),reverse=True)
    w = [n for n in zip(*y)]
    print("Sıralanmış CVler:")
    print(list(w[0]),list(w[1]),tuple(list(a) for a in zip(*w[1])))
    #print(Z)

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
        #BİLGİLERİ EKLE
        #name = name.split('.')[0]
        rank = n
        res = ResultElement(rank,name,phoneno,mail, filename)
        flask_return.append(res)
        # res.printresult()
        # print(f"Rank{res.rank+1} :\t {res.filename}")
    return flask_return

