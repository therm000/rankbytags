# --
# $CoreSDI: webcrawler.py,v 1.14 2006/06/12 21:44:25 francisco Exp $
#

import re               # regular expressions
import urllib2   # proxy support
import threading
import Queue            # synchronized queue class
from urlparse      import urlsplit, urljoin
from HTMLParser    import HTMLParser, HTMLParseError


################################################################################
class page_retriever(threading.Thread):
    
    # --------------------------------------------------------------------------
    def __init__(self, url_queue, proxy = None):

        threading.Thread.__init__(self)
        self._url_queue     = url_queue
        self.proxy          = proxy            # proxy = (target, port)
        self._fetch_history = {}
        self._stop          = False


    # --------------------------------------------------------------------------
    def stop(self):
        self._stop = True


    # --------------------------------------------------------------------------
    def get_page(self, url, proxy = None):
        
        # url = (target, depth)
        # url should contain the complete url structure:
        # scheme://netloc/path;parameters?query#fragment

        # get page
        if url:
            try:
                if self.proxy: 
                    proxy_str = r'http://' + proxy[0] + ':' + str(proxy[1])
                    opener = urllib2.build_opener(urllib2.ProxyHandler( { 'http' : proxy_str } ))
                else:
                    # don't use proxy
                    opener = urllib2.build_opener(urllib2.ProxyHandler( {} ))
                
                print('Depth %d: Getting %s' % (url[1], url[0]))
                # add user-agent header to avoid urllib to adding it as python/urllib
                request = urllib2.Request(url[0], None, { 'User-agent' : '' } )
                file = opener.open(request)
                page = file.read()
                file.close()
                return page

            except Exception, e:
                print('Error sending request for %s :\n %s' % (url[0], str(e)))
                return

        
    # --------------------------------------------------------------------------
    def run(self):

        while not self._stop:
            url = self._url_queue.get_next_url()    # url = (target, depth)
            if url:
                # remove trialing /
                if url[-1] == '/':
                    url = url[:-1]
                # get page if not already fetched
                if url not in self._fetch_history:
                    # this is not thread safe, a lock could be introduced here,
                    # but I prefer to avoid such overhead, and pay to fetch a page twice
                    self._fetch_history[url] = True
                    page = self.get_page(url, self.proxy)
                    if page:
                        self._url_queue.add_page(url[0], page, url[1])
                    else:
                        # url fetch failed
                        self._url_queue.decrement_fetching()
                else:
                    self._url_queue.decrement_fetching()




################################################################################
class html_parse_urls_and_data(HTMLParser):
    
    # --------------------------------------------------------------------------
    def __init__(self, url_base, compiled_regexps):
        
        # url_base is used to resolve relative links
        HTMLParser.__init__(self)
        self.found_urls = []
        self.found_data = []
        self.url_base   = url_base
        self._regexps   = compiled_regexps
        self._encoding  = None
        # TODO: add more valid extensions
        self.valid_extensions = [ 'asp', 'aspx', 'cgi', 'htm', 'html', 'jsp', 'mht', 'php', 'php3', 'shtm', 'shtml', 'txt', 'xml' ]


    # --------------------------------------------------------------------------
    def unknown_starttag(self, tag, attrs):
        pass


    # --------------------------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        # called for every start tag
        # attrs is a list of (attr, value) tuples
        if tag.upper() == 'A':
            for tuple in attrs:
                if tuple[0].upper() == 'HREF':
                    # determine if it has a valid extension (if not a mailto link)
                    split = urlsplit(tuple[1])
                    if split[0].upper() != 'MAILTO':
                        url_filename = split[2]
                        pos = url_filename.rfind('.')
                        valid = True
                        if pos != -1:
                            valid = False
                            for ext in self.valid_extensions:
                                if url_filename[pos+1:] == ext:
                                    valid = True
                                    break
                        if valid:
                            self.found_urls.append(urljoin(self.url_base, tuple[1]))
                    else:
                        self.handle_data(split[2])

        elif tag.upper() == 'META':
            # determine page encoding (charset)
            # i.e. <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />            
            for tuple in attrs:
                if tuple[0].upper() == 'CONTENT':
                    regex = r'charset\s*=\s*([\w+-{0,1}]+\w+)'
                    m = re.compile(regex, re.IGNORECASE).search(tuple[1])
                    if m:
                        self._encoding = m.group(1)
                        break       # exit for loop


    # --------------------------------------------------------------------------
    def handle_data(self, data):
        # called for every block of plain text
        # i.e. outside of any tag and not containing any character or entity references
        if self._encoding:
            data = data.decode(self._encoding, 'ignore')
        for regexp in self._regexps: 
            matches = regexp.findall(data)
            for match in matches:
                self.found_data.append(match)



################################################################################
class webcrawler:

    # usage example:
    # wc = webcrawler(urls, regexps, True, depth, proxy)
    # wc.crawl()
    # print wc.matches

    # --------------------------------------------------------------------------
    def __init__(self, urls, regexps, ignorecase = True, depth = 1, proxy = None):

        # urls should contain the complete url structure:
        # scheme://netloc/path;parameters?query#fragment
        # if not, assume the http scheme

        # create url_queue object        
        queue = []
        for url in urls:
            if url.find('://') == -1:
                url = 'http://' + url
            queue.append((url, depth))
        self.urls    = url_queue(queue)
        self.regexps = regexps
        self.depth   = depth
        self.proxy   = proxy    # proxy = (target, port)
        self.matches = []       # contains the result set

        # compile regexps for better performance
        self._compiled_regexps = []
        try:
            for regex in self.regexps:
                if ignorecase:
                    self._compiled_regexps.append(re.compile(regex, re.IGNORECASE))
                else:
                    self._compiled_regexps.append(re.compile(regex))

        except Exception, e:
            print('%s is an invalid regular expression and will be ignored: %s' % (regex, str(e)))
            pass

    # --------------------------------------------------------------------------
    def crawl(self):

        # launch page_retriever threads
        max_threads = 10
        threads = []
        for i in range(max_threads):
            thread = page_retriever(self.urls, self.proxy)
            thread.start()
            threads.append(thread)

        lastpend = self.urls.pending()
        while self.urls.pending() > 0:
            pend = self.urls.pending()
            if pend != lastpend:
                print('Pending (aprox.): %d' % pend)
                lastpend = pend

            # self.urls.get_next_page returns a fetched page
            next = self.urls.get_next_page()        # next = (url, page, depth)
            if next:
                self.parse_page(next[0], next[1], next[2])

        print('Finishing...')      # show message since thread stop takes some time
        # finish each thread
        for thread in threads:
            thread.stop()

        for thread in threads:
            thread.join()

    # --------------------------------------------------------------------------
    def parse_page(self, url, page, depth):
        
        parser = html_parse_urls_and_data(url, self._compiled_regexps)
        links = []
        try:
            parser.feed(page)
            parser.close()
            links = parser.found_urls
            self.matches += parser.found_data

        except HTMLParseError, msg:
            # some possible situations:
            #   unknown declaration
            #   malformed start tag
            print('HTMLParseError exception: %s\nParsing anyway, but ignoring links.' % str(msg))
            # don't loose it! parse anyway line by line, ignore links
            for regexp in self._compiled_regexps:
                #print page
                matches = regexp.findall(page)
                for match in matches:
                    self.matches.append(match)
                if len(matches) == 1:
                    print('Found 1 match in %s:\n%s' % (url, str(matches)))
                elif len(matches) > 1:
                    print('Found %i matches in %s:\n%s' % (len(matches), url, str(matches)))
            pass

        except Exception, e:
            print('Exception raised: %s' % str(e))
            pass

        if len(parser.found_data) == 1:
            print('Found 1 match in %s:\n%s' % (url, str(parser.found_data)))
        elif len(parser.found_data) > 1:
            print('Found %i matches in %s:\n%s' % (len(parser.found_data), url, str(parser.found_data)))
            
        # recursive search
        if depth > 0:
            for link in links:
                parts = urlsplit(link)
                # no error checking is neccessary
                # parts[0] = scheme, parts[1] = netloc, parts[2] = path;parameters
                # parts[3] = query, parts[4] = fragment
                url_filename = parts[2]
                if parts[3] != '':
                    url_filename += '?' + parts[3]

                self.urls.add_url(parts[0]  + r'://' + parts[1] + url_filename, depth - 1)



################################################################################
class url_queue:

    # --------------------------------------------------------------------------
    def __init__(self, urls = None):

        # urls is a list with pairs (url, depth)
        self.__timeout = 3             # constant
        self.pages = Queue.Queue(0)    # pages is a queue with tuples (url, page, depth)
        self.urls  = Queue.Queue(0)    # self.urls is a queue with pairs of (url, depth) 
        if urls:
            for url in urls:
                self.urls.put(url)
            self._pending_to_fetch = len(urls)  # indicates num ulrs in self.urls
        else:
            self._pending_to_fetch = 0

        self._pending_to_parse = 0     # indicates num pages in self.pages
        self._fetching = 0             # indicates pages that are being fetched (not in pending_to_fetch nor pending_to_parse)


    # --------------------------------------------------------------------------
    def decrement_fetching(self):
        # this function should only be called when a url fetch failed
        # because add_page does it
        self._fetching -= 1

    
    # --------------------------------------------------------------------------
    def pending_to_fetch(self):
        return self._pending_to_fetch


    # --------------------------------------------------------------------------
    def pending_to_parse(self):
        return self._pending_to_parse


    # --------------------------------------------------------------------------
    def pending(self):
        return self._pending_to_parse + self._pending_to_fetch + self._fetching

        
    # --------------------------------------------------------------------------
    def add_url(self, url, depth):
        try:
            self.urls.put((url, depth))
            self._pending_to_fetch += 1

        except Queue.Full:
            pass


    # --------------------------------------------------------------------------
    def add_page(self, url, page, depth):
        # add the fetched page to queue for parsing
        try:
            self.pages.put((url, page, depth))
            self._pending_to_parse += 1
            self._fetching -= 1

        except Queue.Full:
            pass


    # --------------------------------------------------------------------------
    def get_next_url(self):
        
        # return next url and remove it from queue
        url = None
        try:
            url = self.urls.get(True, self.__timeout)  
            self._pending_to_fetch -= 1
            self._fetching += 1
        
        except Queue.Empty:
            pass

        return url


    # --------------------------------------------------------------------------
    def get_next_page(self):
        
        # return first page and remove it from list        
        page = None
        if self._pending_to_parse > 0:
            try:
                page = self.pages.get(True, self.__timeout)  
                self._pending_to_parse -= 1
            
            except Queue.Empty:
                pass
            
        return page


# ------------------------------------------------------------------------------

#
#                  | pending_to_fetch    |   pending_to_parse  | fetching
# ------------------------------------------------------------------------
# add_url          |          +          |                     | 
# ------------------------------------------------------------------------
# add_page         |                     |           +         |    -
# ------------------------------------------------------------------------
# get_next_url     |          -          |                     |    +
# ------------------------------------------------------------------------
# get_next_page    |                     |           -         |

