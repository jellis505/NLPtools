#!/bin/bash/env python
# Created by Joe Ellis
# Columbia University DVMM lab

import os
from gensim import corpora, models

class LDAmodel():

    def __init__(self, dictfile=None):
        # If we want to initialize from a pre-loaded dictionary file do it here
        if dictfile != None:
            self.dict = corpora.Dictionary.load(dictfile)


    def ReadinFiles(self,directory):
        # This function reads in a directory of files and gets them into strings in a list for creation of a corpora
        files = os.listdir(directory)
        self.filepaths = [os.path.join(directory,file)for file in files]

        # Now let's read each of them into a list of the strings
        documents = []
        for file in self.filepaths:
            documents.append(open(file,"r").read())
        print "Finished Reading Docs"
        self.documents = documents[0:30]

        return documents

    def Tokenize(self,documents=None):
        # This function tokenizes the documents that have been read into our list of string structure
        if documents == None:
            documents = self.documents

        stoplist = set('for a of the and to in because'.split())

        # Removes all stop words for the dictionary
        texts = [[word for word in document.lower().split() if word not in stoplist] for document in documents]

        #remove words that only appear once, which may or not be a great idea, but let's just run with it
        # comment this section out if you do not want to remove these type of words
        all_tokens = sum(texts,[])
        tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
        texts = [[word for word in text if word not in tokens_once] for text in texts]

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

    def SaveDictionary(self,dictfile,dict=None):
        if dict == None:
            dict = self.dict

        # Saves the dictionary to a file for future reference
        dict.save(dictfile)

        return

    def CreateLDAModel(self,topic_num):
        # This function creates an LDA model from our give training set
        # Create a bow_corpus of our text elements with the dictionary
        bow_corpus = [self.dict.doc2bow(text) for text in self.texts]

        lda_model = models.LdaModel(corpus=bow_corpus, id2word=self.dict , num_topics=topic_num)

        self.lda_model = lda_model

        self.lda_texts = lda_model[self.texts]

        #Debug statement
        print "Finished LDA model creation"
        return


if __name__ == "__main__":
    # Let's set up the function to see if we can't finish using and creating LDAmodels with this class
    # that I am creating here
    file_dir = "test_data"
    print "Got Here"
    lda_modeler = LDAmodel()
    lda_modeler.ReadinFiles(file_dir)
    lda_modeler.Tokenize()
    lda_modeler.CreateDictionary()
    lda_modeler.CreateLDAModel(2)