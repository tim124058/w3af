'''
digit_sum.py

Copyright 2006 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''

import re

from itertools import izip, repeat

from core.controllers.basePlugin.baseCrawlPlugin import baseCrawlPlugin
from core.controllers.misc.levenshtein import relative_distance_lt
from core.controllers.coreHelpers.fingerprint_404 import is_404

from core.data.bloomfilter.bloomfilter import scalable_bloomfilter
from core.data.options.option import option
from core.data.options.optionList import optionList


class digit_sum(baseCrawlPlugin):
    '''
    Take an URL with a number (index2.asp) and try to find related files (index1.asp, index3.asp).
    @author: Andres Riancho ( andres.riancho@gmail.com )  
    '''

    def __init__(self):
        baseCrawlPlugin.__init__(self)
        self._already_visited = scalable_bloomfilter()
        
        # User options
        self._fuzz_images = False
        self._max_digit_sections = 4
        
    def crawl(self, fuzzable_request ):
        '''
        Searches for new Url's by adding and substracting numbers to the url
        and the parameters.
        
        @parameter fuzzable_request: A fuzzableRequest instance that contains
                                     (among other things) the URL to test.
        '''
        self._fuzzable_requests = []
            
        url = fuzzable_request.getURL()
        headers = {'Referer': url.url_string }
                
        original_response = self._uri_opener.GET( fuzzable_request.getURI(),
                                                  cache=True, headers=headers )
        
        if original_response.is_text_or_html() or self._fuzz_images:
            
            fr_generator = self._mangle_digits( fuzzable_request )
            response_repeater = repeat(original_response)
            header_repeater = repeat(headers)
            
            args = izip(fr_generator, response_repeater, header_repeater)
            
            self._tm.threadpool.map_multi_args(self._do_request, args)
            
            # I add myself so the next call to this plugin wont find me ...
            # Example: index1.html ---> index2.html --!!--> index1.html
            self._already_visited.add( fuzzable_request.getURI() )

        return self._fuzzable_requests

    def _do_request(self, fuzzable_request, original_resp, headers):
        '''
        Send the request.
        
        @param fuzzable_request: The modified fuzzable request
        @param original_resp: The response for the original request that was
                              sent.
        '''
        
        response = self._uri_opener.GET(fuzzable_request.getURI(),
                                        cache=True,
                                        headers=headers)

        add = False

        if not is_404( response ):
            # We have different cases:
            #    - If the URLs are different, then there is nothing to think
            #      about, we simply found something new!
            if response.getURL() != original_resp.getURL():
                add = True
            
            #    - If the content type changed, then there is no doubt that
            #      we've found something new!
            elif response.doc_type != original_resp.doc_type:
                add = True
            
            #    - If we changed the query string parameters, we have to check 
            #      the content
            elif relative_distance_lt(response.getClearTextBody(), 
                                      original_resp.getClearTextBody(), 
                                      0.8):
                # In this case what might happen is that the number we changed
                # is "out of range" and when requesting that it will trigger an
                # error in the web application, or show us a non-interesting
                # response that holds no content.
                #
                # We choose to return these to the core because they might help
                # with the code coverage efforts. Think about something like:
                #     foo.aspx?id=OUT_OF_RANGE&foo=inject_here
                # vs.
                #     foo.aspx?id=IN_RANGE&foo=inject_here
                #
                # This relates to the EXPECTED_URLS in test_digit_sum.py
                add = True
                
        if add:
            self._fuzzable_requests.extend( self._create_fuzzable_requests( response ) )
    
    def _mangle_digits(self, fuzzable_request):
        '''
        Mangle the digits (if any) in the fr URL.
        
        @param fuzzableRequest: The original fuzzableRequest
        @return: A generator which returns mangled fuzzable requests 
        '''
        # First i'll mangle the digits in the URL file
        filename = fuzzable_request.getURL().getFileName()
        domain_path = fuzzable_request.getURL().getDomainPath()
        for fname in self._do_combinations( filename ):
            fr_copy = fuzzable_request.copy()
            fr_copy.setURL( domain_path.urlJoin(fname) )
            
            if fr_copy.getURI() not in self._already_visited:
                self._already_visited.add( fr_copy.getURI() )
                
                yield fr_copy
        
        # Now i'll mangle the query string variables
        if fuzzable_request.getMethod() == 'GET':
            for parameter in fuzzable_request.getDc():
                
                # to support repeater parameter names...
                for element_index in xrange(len(fuzzable_request.getDc()[parameter])):
                    
                    combinations = self._do_combinations( fuzzable_request.getDc()
                                                          [ parameter ][element_index] )
                    for modified_value in combinations:

                        fr_copy = fuzzable_request.copy()
                        new_dc = fr_copy.getDc()
                        new_dc[ parameter ][ element_index ] = modified_value
                        fr_copy.setDc( new_dc )
                        
                        if fr_copy.getURI() not in self._already_visited:
                            self._already_visited.add( fr_copy.getURI() )
                            yield fr_copy
        
    def _do_combinations( self, a_string ):
        '''
        >>> ds = digit_sum()
        >>> ds._do_combinations( 'abc123' )
        ['abc124', 'abc122']

        >>> ds._do_combinations( 'abc123def56' )
        ['abc124def56', 'abc122def56', 'abc123def57', 'abc123def55']
       
        '''
        res = []
        splitted = self._find_digits( a_string )
        if len( splitted ) <= 2 * self._max_digit_sections:
            for i in xrange( len( splitted ) ):
                if splitted[ i ].isdigit():
                    splitted[ i ] = str( int(splitted[ i ]) + 1 )
                    res.append( ''.join(splitted) )
                    splitted[ i ] = str( int(splitted[ i ]) - 2 )
                    res.append( ''.join(splitted) )
                    
                    # restore the initial value for next loop
                    splitted[ i ] = str( int(splitted[ i ]) + 1 )
                    
        return res
                
    def _find_digits( self, a_string ):
        '''
        Finds digits in a string and returns a list with string sections.
        
        >>> ds = digit_sum()
        >>> ds._find_digits('foo45')
        ['foo', '45']
        
        >>> ds._find_digits('f001bar112')
        ['f', '001', 'bar', '112']
                
        @return: A list of strings.
        '''
        # regexes are soooooooooooooo cool !
        return [ x for x in re.split( r'(\d+)', a_string ) if x != '' ]
        
    def get_options( self ):
        '''
        @return: A list of option objects for this plugin.
        '''
        ol = optionList()
        
        d = 'Apply URL fuzzing to all URLs, including images, videos, zip, etc.'
        h = 'It\'s safe to leave this option as the default.'
        o = option('fuzzImages', self._fuzz_images, d, 'boolean', help=h)
        ol.add(o)
        
        d = 'Set the top number of sections to fuzz'
        h = 'It\'s safe to leave this option as the default. For example, with maxDigitSections'
        h += ' = 1, this string wont be fuzzed: abc123def234 ; but this one will abc23ldd.'
        o = option('maxDigitSections', self._max_digit_sections, d, 'integer', help=h)
        ol.add(o)
                
        return ol
        
    def set_options( self, optionList ):
        '''
        This method sets all the options that are configured using the user interface 
        generated by the framework using the result of get_options().
        
        @parameter OptionList: A dictionary with the options for the plugin.
        @return: No value is returned.
        ''' 
        self._fuzz_images = optionList['fuzzImages'].getValue()
        self._max_digit_sections = optionList['maxDigitSections'].getValue()
    
    def getLongDesc( self ):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This plugin tries to find new URL's by changing the numbers that are
        present on it.
        
        Two configurable parameters exist:
            - fuzzImages
            - maxDigitSections
        
        An example will clarify what this plugin does, let's suppose that the
        input for this plugin is:
            - http://host.tld/index1.asp
            
        This plugin will request:
            - http://host.tld/index0.asp
            - http://host.tld/index2.asp
            
        If the response for the newly generated URL's is not an 404 error, then
        the new URL is a valid one that can contain more information and 
        injection points.      
        '''