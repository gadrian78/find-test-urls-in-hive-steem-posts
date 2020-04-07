import urllib.request, urllib.error

script_params_html = ''
# prints message and adds it to html script params, if output is human readable
def add_to_output(message, print_also=True):
    global script_params_html
    if print_also:
        print(message)
    script_params_html += '<p class="params">' + message + '</p>\n'
# end add_to output function

author_name = ''
# functions to help make available author_name from main module to script_params_* modules without importing each other
def set_author(author):
    global author_name
    author_name = author
def get_author():
    global author_name
    return author_name

TEST_BROKEN_LINKS_TIMEOUT = 10 # seconds
# test a url to see if it's broken or not
def test_url(url_str):
    resp_dict = {}
    try:
        # setting user agent to Mozilla, otherwise urllib is blocked by sites like steemit.com
        req=urllib.request.Request(url=url_str, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=TEST_BROKEN_LINKS_TIMEOUT)
        
        if not response:
            resp_dict = None
            return resp_dict
        
        resp_dict['status'] = response.status
        resp_dict['reason'] = response.reason
        resp_dict['via'] = 'try'

    except urllib.error.HTTPError as e:
        resp_dict['status'] = e.getcode()
        resp_dict['reason'] = e.reason
        resp_dict['via'] = 'except_HTTPError'
        pass
    except urllib.error.URLError as e:                                    
        resp_dict['status'] = -1
        resp_dict['reason'] = str(e.reason).upper()
        resp_dict['via'] = 'except_URLError'
        pass                            
    except ValueError as e:
        resp_dict['status'] = -1
        resp_dict['reason'] = str(e).upper()
        resp_dict['via'] = 'except_ValueError'
        pass
    except OSError as e:                                
        resp_dict['status'] = -1
        resp_dict['reason'] = str(e.strerror).upper()
        resp_dict['via'] = 'except_OSError'
        pass

    return resp_dict
# end test_url function