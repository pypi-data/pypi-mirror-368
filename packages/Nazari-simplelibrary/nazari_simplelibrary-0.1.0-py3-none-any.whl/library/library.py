
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  3 10:03:38 2025

@author: Mahjoobe Nazari
"""

class Library():
    
    
    def __init__(self, books=None):
        if books== None :
            self.books=[]
        else:
            self.books=books
       
        
        
    def Add_book(self, title , auther):
        self.books.append({"title" : title ,  "auther" : auther})
        print(f"book of {title} writen by {auther} is added.")
    
   
    
    def remove_book(self , title):
        for book in self.books:
        
            if book["title"].lower() == title.lower() :
                self.books.remove(book)
                print(f"book {title} deleted")
                return
        print(f"book {title} not founded.")
       
        
        
    
    def search_book(self , title):
        result=[book for book in self.books if title.lower() in book["title"].lower() ]
        if result :
            print("the search result is:")
            for book in result :
                print(f" book is {book['title']} written by {book['auther']}")
        else :
            print("book is not found")
                
            
    
    def show_books(self):
        if self.books== None :
            print("the is no books in library.")
        else:
            print("list of books :")
            for book in self.books:
               ## print(book.keys() , book.values())
                print(f" - book : {book['title']} , auther : {book['auther']}")
              
          
        
