string_list=["a","b","c","d","e"] #S
index_list=[1,2,3] #I

#ik zou het sorteren
#mem complexity
for idx in index_list[::-1]:
    del string_list[idx]

string_list.extend(string_list)
print(string_list)
