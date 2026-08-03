lst = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
print(type(lst).__name__, type(lst[0]).__name__)

str_lst = str(lst)
print(type(str_lst).__name__, type(str_lst[0]).__name__, str_lst)
#
# lst_back = list(str_lst)
# print(type(lst_back).__name__, type(lst_back[0]).__name__, lst_back)
#
# lst_back = [i for i in str_lst]
# print(type(lst_back).__name__, type(lst_back[0]).__name__, lst_back)
