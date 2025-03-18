list = ["hello" , "hey" , 'hi']
input = {'n' : 'bye',
         'hi':'hello'
        }
print(all(word if word in list else False for word in input))