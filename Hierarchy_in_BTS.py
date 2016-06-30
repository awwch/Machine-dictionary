
# coding: utf-8

# In[224]:

import re


# In[225]:

with open('BTS_original.txt', 'r', encoding='utf-8') as f:
    test = f.readlines() 


# In[226]:

strong_tags = ['l','~','v','z','}','{','|'] #подчиняют целые блоки
middle_tags = ['M','N','O','Б','a','d','e','h','j','t','u','w','x','y','п','\\'] #подчиняют некоторые тэги
humble_tags = ['B','C','D','E','F','G','H','I','J','K','L','P','Q','R','S','T','U','V','W','Y','Z','b','c','g',
               'i','k','o','q','r','s','[','_','^','\'','`','m','n'] #ничего не подчиняют
obeying_tags = ['f','p'] #всегда подчиняются предыдущему тэгу

#надо доработать тэги @m и @n


# ### На строке открываем и закрываем каждый тэг. Случай @A прорабатываем отдельно

# In[227]:

bag_with_BTS = []
for line in test:
    line =  re.sub('@.', '<' + line[0:2] + '>', line) #открываем тэг
    #line =  re.sub('<\~>','', line)
    if line[1:3] != '@A' and line not in ['\n', '\r\n']:
        line = (line + '</'  + line[1:3] + '>' + '\n') #закрываем тэг, если это не @A (с ним работаем отдельно)
    bag_with_BTS.append(line) 


# ### Корректируем закрытие тэгов группы middle

# In[228]:

#список тэгов, подчиняемых данным
middle_dependeny = {
            'M': ('I'),
            'N': ('c'),
            'O': ('x'),
            'Б': ('п','y'),
            'a': ('t'),
            'd': ('e'),
            'e': ('f','g'),
            'h': ('i','j', 'k'),
            'j': ('i','k'),
            't': ('y'),
            'u': ('D','E','I','J','K','L','N','O','R','S','A','B','F','H','a','b','e','q','r','\\','_'),
            'w': ('p','x','Б'),
            'x': ('w'),
            'y': ('x'),
            'п': ('Б'),
            '\\': ('P')}

for i, line in enumerate(bag_with_BTS):
    cur_tag = line[2:3]
    if cur_tag in middle_tags and bag_with_BTS[i+1] not in ['\n', '\r\n']:
        #смотрим, подчиняется ли следующий тэг текущему
        if bag_with_BTS[i+1][2:3] in middle_dependeny[cur_tag]:
            #убираем закрытие middle тэга на его собственной строке
            bag_with_BTS[i] =  re.sub('<...>' ,'', bag_with_BTS[i])  
            #закрываем на строке подчиняющегося тэга
            bag_with_BTS[i+1] = (bag_with_BTS[i+1] + '</@'  + cur_tag + '>' + '\n') 
        else: pass
    else:
        pass


# #### Особые случаи ( w + x + w )       и        ( x + w + x ), обработка которых может подвергаться изменениям

# In[229]:

for i, line in enumerate(bag_with_BTS):
    cur_tag = line[2:3]
    if cur_tag == 'w' and bag_with_BTS[i+1][2:3] == 'x' and bag_with_BTS[i+2][2:3] == 'w':
        bag_with_BTS[i+1] = (bag_with_BTS[i+1] + '\n' + '</@x>')
        bag_with_BTS[i+2] = re.sub('<.@x>' ,'', bag_with_BTS[i+2]) 
        
for i, line in enumerate(bag_with_BTS):
    cur_tag = line[2:3]
    if cur_tag == 'x' and bag_with_BTS[i+1][2:3] == 'w' and bag_with_BTS[i+2][2:3] == 'x':
        bag_with_BTS[i+1] = (bag_with_BTS[i+1] + '\n' + '</@w>')
        bag_with_BTS[i+2] = re.sub('<.@w>' ,'', bag_with_BTS[i+2])
        bag_with_BTS[i+2] = (bag_with_BTS[i+2] + '</@x>' + '\n')


# ### Корректируем закрытие тэгов группы strong

# In[230]:

#сильный тэг подчиняет весь блок вплоть до следующих тэгов
strong_dependeny = {
            'l': ('l'),
            '~': ('l','v', '~'),
            'v': ('l','v', '~'),
            'z': ('l','v','~','z'),
            '}': ('l','v','~','}'),
            '{': ('l','v','~','z','}','{'),
            '|': ('l','v','~','z','{','|','}')}

j=0   
for i, line in enumerate(bag_with_BTS):
    cur_tag = line[2:3]
    if cur_tag in strong_tags:
        j=i
        #смотрим каждый следующий тэг, пока не дойдем до того места, где заканчивается блок
        while bag_with_BTS[j+1][2:3] not in strong_dependeny[cur_tag]  and bag_with_BTS[j+1] not in ['\n', '\r\n'] and (j+2) != len(bag_with_BTS):
            j = j+1 
        #закрываем strong тэг на строке подчиняющегося тэга 
        bag_with_BTS[i] =  re.sub('<...>' ,'', bag_with_BTS[i])
        bag_with_BTS[j] = (bag_with_BTS[j] + '</@'  + cur_tag + '>' + '\n')
    else:
        pass 

for i,line in enumerate(bag_with_BTS):
    if line in ['\n', '\r\n']:
        bag_with_BTS[i-1] = (bag_with_BTS[i-1] + '</@A>' + '\n') #закрываем тэг @A


# #### Если strong тэги закрываются на одной строке, расставим их в правильном порядке

# In[231]:

strong_tags = ['l','~','v','z','}','{','|']

for i, line in enumerate(bag_with_BTS):
    #проходим по всем сильным тэгам
    for j in range(len(strong_tags)):
        #фиксируем сильный тэг, который сейчас ищем
        cur_tag = strong_tags[j] 
        if ('</@' + cur_tag + '>') in bag_with_BTS[i]:
            #фиксируем его позицию в строке
            index = strong_tags.index(cur_tag)
            index_next = index + 1
            #смотрим каждый следующий тэг, пока не дойдем до того места, где стоит более слабый тэг
            if index_next < 7:
                while strong_tags[index_next] not in bag_with_BTS[i] and index_next != 6:
                    index_next = index_next +1
                if index_next != 6:
                    #меняем их местами
                    bag_with_BTS[i] = bag_with_BTS[i].replace('</@'+ strong_tags[index+1] +'>', '</@' + cur_tag + '>')
                    bag_with_BTS[i] = bag_with_BTS[i].replace( '</@' + cur_tag + '>', '</@'+ strong_tags[index+1] +'>', 1)
                else: 
                    pass
            else:
                pass
        else:
            pass


# ### Добавим правило для случаев во скобками, когда один простой тэг может подчинять целый блок

# In[232]:

sign = ['(','[']
sign_dependeny = {
            '(': (')'),
            '[': (']')}


for i, line in enumerate(bag_with_BTS):
    cur_tag = line[2:3]
    #проверяем, если ли в строке ( или [, но не трогаем случаи, когда скобки открываются и закрываются на одной строке
    if line[5:6] in sign and sign_dependeny[line[5:6]] not in line: 
        cur_sign = line[5:6] 
        j=i
        #смотрим каждую следующую строку, пока не найдем закрытие скобки
        while sign_dependeny[cur_sign] not in bag_with_BTS[j]:
            j = j+1
        #делаем так, чтобы тэг закрывался в нужном месте: убираем его закрытие на прежнем месте
        bag_with_BTS[i] =  re.sub('<.@'  + cur_tag + '>','', bag_with_BTS[i])
        #закрываем его на строке, где закрывается скобка
        if ('</@'  + cur_tag + '>') not in bag_with_BTS[j]:
            bag_with_BTS[j] = (bag_with_BTS[j] + '</@'  + cur_tag + '>' + '\n')
        else:
            pass
        #убираем его на предыдущих строках, если есть
        while i+1<j:
            bag_with_BTS[j-1] =  re.sub('<.@'  + cur_tag + '>' ,'', bag_with_BTS[j-1])
            j=j-1
    else:
        pass


# ### Замена тэгов БТС на тэги TEI

# In[233]:

for i, line in enumerate(bag_with_BTS):
    
    if '<@A>' in line and '<orth>' not in bag_with_BTS[i-1]: 
        bag_with_BTS[i] = bag_with_BTS[i].replace(line, '<orth>' + keyword + '</orth>' + '\n')
    if '<@A>' in line and '\'' in line:
        bag_with_BTS[i] = bag_with_BTS[i].replace('\'', '' )
        bag_with_BTS[i] = bag_with_BTS[i].replace('\\', '' )
        bag_with_BTS[i] += ('\n' + '<stress>' + keyword + '</stress>' + '\n')
    if '</@A>' in line:
        bag_with_BTS[i] = bag_with_BTS[i].replace(line, '</superEntry>' + '\n''\n''\n' + '<superEntry>')
        
    if '<@w>' in line:
        bag_with_BTS[i] = bag_with_BTS[i].replace('<@w>',  '<def>')
    if '</@w>' in line:
        bag_with_BTS[i] = bag_with_BTS[i].replace('</@w>', '</def>')
        
    if '<@y>' in line and '<@y>' not in bag_with_BTS[i-2]: #окружение открывается только в первый раз
        bag_with_BTS[i] = bag_with_BTS[i].replace(line, '<cit type = ‘example’>' + '\n' + '<q>' + line[4:] )
    if '<@y>' in line:
        bag_with_BTS[i] = bag_with_BTS[i].replace(line, '<q>' + line[4:])
    try:
        if '</@y>' in line and '</@y>' not in bag_with_BTS[i+2]: #окружение закрывается только в последний раз
            bag_with_BTS[i] = bag_with_BTS[i].replace(line, '</q>' + '\n' + '</cit>')
    except:
        continue 

    if '</@y>' in line:
        bag_with_BTS[i] = bag_with_BTS[i].replace(line, '</q>')
        
    if '<@C>' in line:
        bag_with_BTS[i] = bag_with_BTS[i].replace(line, '<xr>' + '\n' + '<ref>' + line[4:] + '</ref>')
    if '</@C>' in line:
        bag_with_BTS[i] = bag_with_BTS[i].replace(line, '</xr>')


# ### Записываем БТС с иерархией в конечный файл

# In[234]:

with open('Hierarchy in BTS.txt', 'w', encoding = 'utf-8') as f:
     for line in bag_with_BTS:
            f.write(line)


# In[ ]:



