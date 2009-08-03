#--
# $Id: http_email_address_grabber.py 48117 2007-08-03 20:32:37Z riq $
#
# Description:
#       This module searches the web for email addresses
#

from webcrawler import webcrawler
import re                               # regular expressions


class email_grabber:
    
    def initialize(self, inputs, grab_type='domain2name&email', crawl_depth='0', tuple_proxy=('192.168.254.254', 80)):
        # TODO: perhaps inputs could be a list of regexps instead...
        # read parameters
        inputs_string   = inputs #self.getParameters().get('DOMAINS')
        depth            = int(crawl_depth)

        # convert urls and inputs to list removing spaces.
        if grab_type == 'name2email&domain':
            aux_inputs        = inputs_string.split(',')
            inputs = []
            for i in aux_inputs:
                # first.last
                inputs.append( i.strip().lower().replace(' ', '.') )
                # firstlast
                inputs.append( i.strip().lower().replace(' ', '') )
                first = i.strip().lower().split(' ')[0]
                last  = i.strip().lower().split(' ')[1]
                # first_firstletterlast
                inputs.append( first[0] + last )
            grab_type = 'email2name&email'
        else:
            inputs_string = inputs_string.replace(' ', '')
            inputs        = inputs_string.split(',')

        proxy = tuple_proxy
        
        self.init_vars(inputs, depth, proxy, grab_type)

    # --------------------------------------------------------------------------
    def isConcurrent(self):
        return 1    # allow more than one instance running at the same time

    # --------------------------------------------------------------------------
    def select_urls(self):
        raise Exception("Method not implemented")

    # --------------------------------------------------------------------------
    def init_vars(self, inputs, depth = 1, proxy = None, grab_type = 'domain2name&email'):

        # inputs is a list containing the end of the email addresses to search
        # i.e. name@domain
        self.inputs           = inputs
        self.depth            = depth
        self.proxy            = proxy
        self.emails           = {}            # contains the result set
        #self.names            = []            # contains the result set names
        self.grab_type        = grab_type

        nonvc = r'[^/=!\"#$%(),:;<>@[\\\]\'|\s\t\n\r\f\v]+'  # non-valid address characters
        # matches: (case doesn't matter)
        #           name@example.com
        #           name@example.com.ar
        #           name@ar.example.com
        #           name at example.com
        #           name at example dot com
        #           name&#64example.com
        #           name@<b>example.com</b>
        #           name at <b>example.com</b>
        #           name&#64<b>example dot com</b>
        self._regexps = []
        for _input in inputs:
            # types are 'domain2name&email' 'email2name&name'
            if grab_type == 'domain2name&email':
                # the following urls should NOT contain groups
                self._regexps += [
                                    # first_name last_name bla@example.com
                                    nonvc + r' ' + nonvc + r' ' + nonvc + r' at ' + _input,
                                    nonvc + r' ' + nonvc + r' ' + nonvc + r' at ' + _input.replace('.',' dot '),
                                    nonvc + r' ' + nonvc + r' ' + nonvc + r'&#64;' + _input,
                                    nonvc + r' ' + nonvc + r' ' + nonvc + r'@(?:\w+[_\-\.]{1})*' + _input + r'(?:[_\-\.]{1}\w+)*',
                                    # same as above but with _input between <b> and </b>
                                    # (yahoo puts search pattern between them)
                                    nonvc + r' ' + nonvc + r' ' + nonvc + r' at <b>' + _input + r'</b>',
                                    nonvc + r' ' + nonvc + r' ' + nonvc + r'&#64;<b>' + _input + r'</b>',
                                    nonvc + r' ' + nonvc + r' ' + nonvc + r'@(?:\w+[_\-\.]{1})*<b>' + _input + r'</b>(?:[_\-\.]{1}\w+)*',

                                    # bla@example.com
                                    nonvc + r' at ' + _input,
                                    nonvc + r' at ' + _input.replace('.',' dot '),
                                    nonvc + r'&#64;' + _input,
                                    nonvc + r'@(?:\w+[_\-\.]{1})*' + _input + r'(?:[_\-\.]{1}\w+)*',
                                    # same as above but with _input between <b> and </b>
                                    # (yahoo puts search pattern between them)
                                    nonvc + r' at <b>' + _input + r'</b>',
                                    nonvc + r'&#64;<b>' + _input + r'</b>',
                                    nonvc + r'@(?:\w+[_\-\.]{1})*<b>' + _input + r'</b>(?:[_\-\.]{1}\w+)*'
                                 ]
            elif grab_type == 'email2name&email':
                # the following urls should NOT contain groups
                self._regexps += [
                                    # first_name last_name bla@example.com
                                    nonvc + r' ' + nonvc + r' ' + _input + r' at ' + nonvc,
                                    nonvc + r' ' + nonvc + r' ' + _input + r' at ' + nonvc + r' dot ' + nonvc + r' ',
                                    nonvc + r' ' + nonvc + r' ' + _input + r'&#64;' + nonvc,
                                    nonvc + r' ' + nonvc + r' ' + _input + r'@(?:\w+[_\-\.]{1})*' + nonvc + r'(?:[_\-\.]{1}\w+)*',
                                    # same as above but with _input between <b> and </b>
                                    # (yahoo puts search pattern between them)
                                    nonvc + r' ' + nonvc + r' ' + _input + r' at <b>' + nonvc + r'</b>',
                                    nonvc + r' ' + nonvc + r' ' + _input + r'&#64;<b>' + nonvc + r' dot ' + nonvc + r'</b>',
                                    nonvc + r' ' + nonvc + r' ' + _input + r'@(?:\w+[_\-\.]{1})*<b>' + nonvc + r'</b>(?:[_\-\.]{1}\w+)*',

                                    # bla@example.com
                                    _input + r' at ' + nonvc,
                                    _input + r' at ' + nonvc + r' dot ' + nonvc + r' ',
                                    _input + r'&#64;' + nonvc,
                                    _input + r'@(?:\w+[_\-\.]{1})*' + nonvc + r'(?:[_\-\.]{1}\w+)*',
                                    # same as above but with _input between <b> and </b>
                                    # (yahoo puts search pattern between them)
                                    _input + r' at <b>' + nonvc + r'</b>',
                                    _input + r'&#64;<b>' + nonvc + r' dot ' + nonvc + r'</b>',
                                    _input + r'@(?:\w+[_\-\.]{1})*<b>' + nonvc + r'</b>(?:[_\-\.]{1}\w+)*'
                                 ]
            else:
                raise Exception("ERROR: bad grab_type")
##            elif grab_type == 'name2email&domain':
##                # the following urls should NOT contain groups
##                first = _input.split('+')[0]
##                last = _input.split('+')[1]
##                self._regexps += [
##                                    # first_name last_name bla@example.com
##                                    first + r' ' + last + r' ' + nonvc + r' at ' + nonvc,
##                                    first + r' ' + last + r' ' + nonvc + r' at ' + nonvc + r' dot ' + nonvc + r' ',
##                                    first + r' ' + last + r' ' + nonvc + r'&#64;' + nonvc,
##                                    first + r' ' + last + r' ' + nonvc + r'@(?:\w+[_\-\.]{1})*' + nonvc + r'(?:[_\-\.]{1}\w+)*',
##                                    # same as above but with _input between <b> and </b>
##                                    # (yahoo puts search pattern between them)
##                                    first + r' ' + last + r' ' + nonvc + r' at <b>' + nonvc + r'</b>',
##                                    first + r' ' + last + r' ' + nonvc + r'&#64;<b>' + nonvc + r' dot ' + nonvc + r'</b>',
##                                    first + r' ' + last + r' ' + nonvc + r'@(?:\w+[_\-\.]{1})*<b>' + nonvc + r'</b>(?:[_\-\.]{1}\w+)*',
##
##                                    # bla@example.com
##                                    nonvc + r' at ' + nonvc,
##                                    nonvc + r' at ' + nonvc + r' dot ' + nonvc + r' ',
##                                    nonvc + r'&#64;' + nonvc,
##                                    nonvc + r'@(?:\w+[_\-\.]{1})*' + nonvc + r'(?:[_\-\.]{1}\w+)*',
##                                    # same as above but with _input between <b> and </b>
##                                    # (yahoo puts search pattern between them)
##                                    nonvc + r' at <b>' + nonvc + r'</b>',
##                                    nonvc + r'&#64;<b>' + nonvc + r' dot ' + nonvc + r'</b>',
##                                    nonvc + r'@(?:\w+[_\-\.]{1})*<b>' + nonvc + r'</b>(?:[_\-\.]{1}\w+)*',
##                                 ]


    # --------------------------------------------------------------------------
    def search_emails(self):

        # use try/finally to show results in case a cancel occurs
        try:
            urls = self.select_urls()
            wc = webcrawler(urls, self._regexps, True, self.depth, self.proxy)
            wc.crawl()

        finally:
            # forbiden string in 'first_name last_name'
            forbiden_subtrings = ['escribi', 'resumes', 'write', 'email', 'cv ', 'comments', 'e-mail', 'contact', 'support', 'him ', 'please', ' from']
            forbiden_suffixes = [' to', ' list', ' lists', ' as', ' a']
            # normalize found addresses
            for email in wc.matches:
                # convert result to lowercase, since the DB is case insensitive
                email = email.lower()

                # replace ' at ' with '@' and ' dot ' with '.'
                email = email.replace(' at ', '@').replace(' dot ', '.')
                # remove <b> and </b> tags
                email = email.replace('<b>', '').replace('</b>', '')
                # replace '&#64;' with '@'
                email = email.replace('&#64;', '@')
                
                if len(re.findall('@', email)) > 1:
                    continue
                s = email.split(' ')
                if len(s) > 1: # has first_name last_name
                    names = s[:2]
                    email = ' '.join(s[2:])
                    for forb in forbiden_subtrings:
                        if forb in ' '.join(names):
                            names = []
                    for forb in forbiden_suffixes:
                        if ' '.join(names).endswith(forb):
                            names = []
                    # no numbers
                    if re.search('[0-9]+', ' '.join(names)):
                        names = []
                else:
                    names = []
                    email = ' '.join(s)

                if email.endswith('.'):
                    email = email[:-1]
                email = email.replace('&gt','')

                if not '...' in email:
                    if not email in self.emails or self.emails[email] == '':
                        self.emails[email] = ' '.join(names)
                elif self.canFixEmail(email, names):
                    email = self.fixEmail(email, names)
                    if not email in self.emails or self.emails[email] == '':
                        self.emails[email] = ' '.join(names)
                        
            # remove duplicates (convert to set and then to list again)
            #self.emails = list(set(self.emails))

    def canFixEmail(self, email, names):
        ret = len(names)>0 and (len(email.split('@')[0]) == len('.'.join(names)) or len(email.split('@')[0]) == len(names[1]) or len(email.split('@')[0]) == len(names[0]) or len(email.split('@')[0]) == len(names[1])+1)
        return len(names)>0 and (len(email.split('@')[0]) == len('.'.join(names)) or len(email.split('@')[0]) == len(names[1]) or len(email.split('@')[0]) == len(names[0]) or len(email.split('@')[0]) == len(names[1])+1)

    def fixEmail(self, email, names):
        if len(email.split('@')[0]) == len('.'.join(names)):
            # fix with first_name.last_name@example.com
            ret = '.'.join(names).lower() + '@' + email.split('@')[1]
            return '.'.join(names).lower() + '@' + email.split('@')[1]
        elif len(email.split('@')[0]) == len(names[1])+1:
            # fix with only first_name_one_letterlast_name@example.com
            ret = names[0].lower()[0:1] + names[1].lower() + '@' + email.split('@')[1]
            return names[0].lower()[0:1] + names[1].lower() + '@' + email.split('@')[1]
        elif len(email.split('@')[0]) == len(names[0]):
            # fix with only first_name@example.com
            ret = names[0].lower() + '@' + email.split('@')[1]
            return names[0].lower() + '@' + email.split('@')[1]
        else:
            # fix with only last_name@example.com
            ret = names[1].lower() + '@' + email.split('@')[1]
            return names[1].lower() + '@' + email.split('@')[1]

    # --------------------------------------------------------------------------
    def targetRun(self):
        print('Searching, please wait...\nThis operation may take some minutes.\n')

        # do the search
        self.search_emails()

    # --------------------------------------------------------------------------
    def finalize(self):
        return_emails = []
        # show results
        title = 'Found %d email addresses:' % len(self.emails)
        if len(self.emails.keys()) == 1:
            print('-------------------------\nFound 1 match:')
            title = 'Found 1 email address:'
        else:
            print('-------------------------\nFound %d matches:' % len(self.emails))

        #self.emails.sort()      # sort emails

        table = []
        for row, name in self.emails.iteritems():      # hack to show table
            try:
                # now we have tuples (name,email)s
                row = (row,name)
                print(str(row))
                # TODO: fix this ugly unicode workaround!
                table.append((str(row).decode('latin-1', 'ignore'), ''))
                return_emails.append(row)

            except Exception, e:
                self.logHi('Ignoring email address. Contains invalid characters: %s' % row.decode('latin-1','ignore') )

##        self.getOutput().addTable(title, table)
##        self.getOutput().output()
        return return_emails


################################################################################

class http_email_address_grabber(email_grabber):

    def select_urls(self):
        urls_string  = self.getParameters().get('URLS')
        urls         = urls_string.replace(' ', '').split(',')

        if len(urls) == 1 and urls[0] == '':
            urls = []
            for _input in self.inputs:
                # try in the inputs main page (may not exist)
                urls.append(r'http://www.' + input)

        return urls


################################################################################

class search_email_address_grabber(email_grabber):

    def select_urls(self):
        urls = []
        for _input in self.inputs:

            # add pgp.mit.edu
            urls.append(r'http://pgp.mit.edu:11371/pks/lookup?search=' + _input + r'&op=index')

            # add google, show 100 results per page (max value)
            urls.append(r'http://www.google.com/search?as_epq=' + _input + r'&num=100&start=0')
            urls.append(r'http://www.google.com/search?as_epq=' + _input + r'&num=100&start=100')
##            urls.append(r'http://www.google.com/search?as_epq=' + _input + r'&num=100&start=200')
##            urls.append(r'http://www.google.com/search?as_epq=' + _input + r'&num=100&start=300')
##            urls.append(r'http://www.google.com/search?as_epq=' + _input + r'&num=100&start=400')

            # add google groups
            urls.append(r'http://groups.google.com/groups?lnk=hpsg&q=' + _input + r'&num=100&start=0')
            urls.append(r'http://groups.google.com/groups?lnk=hpsg&q=' + _input + r'&num=100&start=100')
##            urls.append(r'http://groups.google.com/groups?lnk=hpsg&q=' + _input + r'&num=100&start=200')
##            urls.append(r'http://groups.google.com/groups?lnk=hpsg&q=' + _input + r'&num=100&start=300')
##            urls.append(r'http://groups.google.com/groups?lnk=hpsg&q=' + _input + r'&num=100&start=400')

            # add yahoo
            urls.append(r'http://search.yahoo.com/search?p=' + _input)

            # add altavista. kgs=0 is for worldwide search
##            urls.append(r'http://www.altavista.com/web/results?q=' + _input + r'&kgs=0')

            # add msn
            urls.append(r'http://search.msn.com/results.aspx?FORM=MSNH&srch_type=0&q=' + _input )

            # add ask
##            urls.append(r'http://www.ask.com/web?q=' + _input + r'&qsrc=1&o=0')

            # add search
##            urls.append(r'http://search.about.com/fullsearch.htm?terms=' + _input + r'&qsrc=1&o=0')

            # add metacrawler
##            urls.append(r'http://www.metacrawler.com/info.metac/search/web/' + _input)

        return urls

######emails = search_email_address_grabber()
#######an email is "egutesman", "jorlicki", "ivan.arce", "info", etc.
#######a name is "ivan arce" or "esther goris"
####### types are 'domain2name&email' 'email2name&email' 'name2email&domain'
########emails.initialize('coresecurity.com', 'domain2name&email')
######
####### probar con jkohen, ivan.arce, juliano
######
######emails.initialize('Gerardo Richarte', 'name2email&domain')
######emails.targetRun()
######email_list = emails.finalize()
######print '--------------------------------------------------------------------------------'
######for e in email_list:
######    print str(e)

#emails = search_email_address_grabber()
#emails.initialize('javier kohen', 'name2email&domain')
#emails.targetRun()
#email_list = emails.finalize()
