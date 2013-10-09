#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Created by Joe Ellis 
# DVMM Lab Columbia University

import os, sys
from bs4 import BeautifulSoup
  
def ReadTopicFile(content_string):
    soup = BeautifulSoup(content_string)
    topic_dict = {}
    topic_dict["topic_title"] = soup.title.string
    
    # Now let's get each of the articles in the list
    articles = soup.find_all("newsarticle")
    article_list = []
    for article in articles:
        article_dict = {} 
        
        # Get title
        title_string = article.title.string
        dash = title_string.find("-")
        if dash <= -1:
            _title = title_string
        else:
            _title = title_string[0:dash]
        article_dict["title"] = _title
        
        # Get pubdate
        article_dict["pubdate"] = article.pubdate.string
        
        # Get Desctiprtion
        article_dict["desc"] = article.description.string
        
        # append to article_list 
        article_list.append(article_dict)

    topic_dict["articles"] = article_list

    return topic_dict
