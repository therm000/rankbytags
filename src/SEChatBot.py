
from nmd import NMD
import msnp

import random

class SEChatBot:
    
    __unknown = [':S', ':(', ':|', ':)', 'uh', 'ok', '?']
    
    def __init__(self, nsed=None, context='chat transcripts'):
        if not nsed:
            nsed = NMD()        
        self.__nsed = nsed
        self.__context = context
        
    def __extract_response(self, snippet):
        if snippet.count(':') >= 2:
            separator = ':'
        elif snippet.count('--') >= 2:
            separator = '--'
        else:
            separator = '- '
        chats = snippet.split(separator)
        for i in range(len(chats)-1):
            chat = chats[i]
            if self.__string in chat.lower():
                response = chats[i+1]
                if i + 2 < len(chats):
                    name = response.strip().split(' ')[-1]
                    if name == 'asks':
                        name = response.strip().split(' ')[-2]
                        response = ' '.join(response.strip().split(' ')[:-2])
                    else:
                        response = ' '.join(response.strip().split(' ')[:-1])
                    response = response.replace(name, 'man')
                return response.strip()
        return ''
            
    def __good(self, snippet):
        return snippet.count(':') >= 2 or snippet.count('--') >= 2 or snippet.count('- ') >= 2
    
    def __extract_responses(self, snippets):
        snippets = filter(self.__good, snippets)
        responses = map(self.__extract_response, snippets)
        return responses
    
    def input(self, string):
        self.__string = string.strip().lower()
        snippets = self.__nsed.snippets(self.__string, self.__context)
        responses = filter(lambda x:x!='', self.__extract_responses(snippets))
        #responses.sort(lambda x,y:len(x)-len(y))
        if len(responses) > 0:
            rand_pos = random.randint(0,len(responses)-1)    
            return responses[rand_pos]
        else:
            rand_pos = random.randint(0,len(self.__unknown)-1)    
            return self.__unknown[rand_pos]
    
    def start(self):
        msg = ''
        while msg!='bye':
            msg = raw_input('You: ')
            print 'Bot: %s' % self.input(msg)
        print 'end of chat.'

    def start_msn(self):
        pass
    
if __name__=='__main__':
    
    #proxy = {'192.168.254.254':80}
    #proxy = {'proxy.itba.edu.ar':8080}
    proxy = {}
    nmd = NMD(proxy)    
    bot = SEChatBot(nmd)
    bot.start()
#    print bot.input('hello')
