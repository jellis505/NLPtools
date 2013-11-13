#!/usr/bin/env python
# Created by Joe Ellis
# Columbia University DVMM lab

### Libraries ###
import os,sys, getopt
from gensim import corpora, models, similarities
from gensim.models import ldamodel
sys.path.append("/ptvn/src/ellis_dev/speaker_diarization/dev/utility")
import FileReader as reader

### Global Variables ###
global topic_xml_dir, saved_models_dir
topic_xml_dir = "/ptvn/SocialMedia/GNews.Topics/"
saved_models_dir = "/ptvn/work/saved_lda_models"

class LDAmodel():

    def __init__(self, modelfile=None, dictfile=None, corpusfile=None):
        # If we want to initialize from a pre-loaded dictionary file do it here
        # Read in the dictionary file
        if dictfile != None:
            self.dict = corpora.Dictionary.load(dictfile)
        
        # Read in the modelfile
        if modelfile !=None:
            self.lda_model = ldamodel.LdaModel.load(modelfile)
        
         # Read in the modelfile
        if corpusfile !=None:
            self.corpus = corpora.mmcorpus.MmCorpus(corpusfile)
        return 

    def ReadinFiles(self,directory):
        # This function reads in a directory of files and gets them into strings in a list for creation of a corpora
        files = os.listdir(directory)
        self.filepaths = [os.path.join(directory,file)for file in files]

        # Now let's read each of them into a list of the strings
        documents = []
        for file in self.filepaths:
            documents.append(open(file,"r").read().replace(",",""))
        print "Finished Reading Docs"
        
        self.documents = documents
        return documents

    def Tokenize(self,documents=None):
        # This function tokenizes the documents that have been read into our list of string structure
        if documents == None:
            documents = self.documents

        # remove common words and tokenize
        stoplist = set('for a of the and to in because'.split())
        texts = [[word for word in document.lower().split() if word not in stoplist]
                 for document in documents]

        # remove words that appear only once
        all_tokens = sum(texts, [])
        tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
        texts = [[word for word in text if word not in tokens_once]
                 for text in texts]

        # Finished Tokenizing the files
        print "Finished Tokenize"

        self.texts = texts
        return texts

    def CreateDictionary(self,texts=None):
        # Check to see if we are saving these as class variables
        if texts == None:
            texts = self.texts

        # Creates a dictionary from our stuff
        bow_dict = corpora.Dictionary(texts)

        # Finished Creating the dictionary
        print "Finished Dictionary Creation"

        self.dict = bow_dict
        return bow_dict

    def SaveDictionaryandCorpus(self,dictfile,corpusfile,dict=None,corpus=None):
        if dict == None:
            dict = self.dict
        
        if corpus == None:
            corpus = self.corpus
        
        # Saves the dictionary to a file for future reference
        dict.save(dictfile)
        
        # Save the corpora in Market Matrix format
        corpora.mmcorpus.MmCorpus.serialize(corpusfile, corpus)
        
        return

    def CreateLDAModel(self,topic_num):
        # This function creates an LDA model from our give training set
        # Create a bow_corpus of our text elements with the dictionary
        bow_corpus = [self.dict.doc2bow(text) for text in self.texts]
        
        lda_model = ldamodel.LdaModel(bow_corpus, id2word=self.dict, num_topics=topic_num)

        self.lda_model = lda_model

        self.lda_texts = lda_model[self.texts]

        #Debug statement
        print "Finished LDA model creation"
        return
    
    def TrainLDA(self,documents,num_t):
        # This function trains a model for LDA
        # remove common words and tokenize
        stoplist = set('for a of the and to in because'.split())
        texts = [[word for word in document.lower().split() if word not in stoplist]
                 for document in documents]

        # remove words that appear only once
        all_tokens = sum(texts, [])
        tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
        texts = [[word for word in text if word not in tokens_once]
                 for text in texts]
        
        dictionary = corpora.Dictionary(texts)
        self.dict = dictionary
        corpus = [dictionary.doc2bow(text) for text in texts]
        self.corpus = corpus    

        # I can print out the documents and which is the most probable topics for each doc.
        lda = ldamodel.LdaModel(corpus, id2word=dictionary, num_topics=num_t)
        corpus_lda = lda[corpus]
        self.lda_model = lda
        
        return lda
    
    def ReturnSimilarArticles(self,document,num_returned=5):
        # This function returns the indices of the documents that are supposed
        # to be the most similar to our query
        
        # This gets the bag of word representation for our vocabulary for this topic
        doc_bow = self.dict.doc2bow(document.lower().split())
        print doc_bow
        # Now let's find the most similar results
        doc_lda = self.lda_model[doc_bow]
        print doc_lda
        
        # Now let's create the similarity structure for these values
        index = similarities.MatrixSimilarity(self.corpus)
        
        sims = index[doc_lda]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        
        results = sims[0:num_returned]
        
        return results
        
    def SaveModel(self,saved_name,model=None):
        if model == None:
            model = self.lda_model
        model.save(saved_name)
        return 

def run(argv):
    
    try:
        opts, args = getopt.getopt(argv,'hct:n:r:')
    except getopt.GetoptError:
        print "Usage Error: Please see help"
        sys.exit(1)
    
    # This section parses the input variables to the script
    create_model = False
    num_t = 100
    return_closest_articles = False
    for opt,arg in opts:
        if opt in ('-h'):
            print 'Help:'
            print '-c: Tells the program to create model file'
            print '-t: The topic number we want to process'
            print '-n: The number of topics to generate from LDA'
            print '-r: Tells us to return closes articles (default_number=5)'
        elif opt in ('-c'):
            create_model = True
        elif opt in ('-t'):
            topic_string = arg
            topic = int(topic_string)
        elif opt in ('-n'):
            num_t = int(arg)
        elif opt in ('-r'):
            return_closest_articles = True
            document = arg
    
    # Create the files that we want to use
    topic_xml_file = os.path.join(topic_xml_dir,topic_string + ".topic")
    saved_model_file = os.path.join(saved_models_dir, topic_string + ".lda")
    saved_dict_file = os.path.join(saved_models_dir, topic_string + ".dict")
    saved_corpus_file = os.path.join(saved_models_dir, topic_string + ".mm")
    
    if create_model:
        content = reader.ReadArticlesforTopic(topic_xml_file)
        # Read the articles and parsed them
        documents = [b for (a,b) in content]
        # Read the articles 
        lda_modeler = LDAmodel()
        lda = lda_modeler.TrainLDA(documents,num_t)
        lda_modeler.SaveModel(saved_model_file)
        lda_modeler.SaveDictionaryandCorpus(saved_dict_file,saved_corpus_file)
        print lda.show_topics()
    
    elif return_closest_articles:
        lda_modeler = LDAmodel(saved_model_file,saved_dict_file, saved_corpus_file)
        indices = lda_modeler.ReturnSimilarArticles(document,5)
        
        # Let's look at the title and description for each article based on the query
        content = reader.ReadArticlesforTopic(topic_xml_file)
        print indices
        for index in indices:
            print content[index[0]]
        
        
        
        
if __name__ == "__main__":
    run(sys.argv[1:])  