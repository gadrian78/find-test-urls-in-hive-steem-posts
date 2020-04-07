import os, sys
from beem import Steem
from beem.account import Account
import json, re
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from functions import add_to_output, test_url, set_author
import functions

# script parameters
# =================

# Steem/Hive node
NODE = 'https://anyx.io' #'https://api.steemit.com'
add_to_output('Node used: ' + NODE)
# change this based on the node used
interface_to_open_posts = 'https://peakd.com' #'https://steempeak.com' # don't include ending "/"
print('Interface to open posts: ' + interface_to_open_posts)

s = Steem(node=NODE, keys=[os.getenv('keys')])

# author
author_name = 'gadrian'
set_author(author_name)
add_to_output('Author username: ' + author_name)

acc = Account(author_name, steem_instance=s)

# import only one settings file at a time
#

# full means matching all URLs (including images) and testing for broken links
from script_params_sample_full import * # a sample of 20 posts, but it takes longer to process every matching url

# set customized settins as you wish - currently it's full, filtered by datetime post-hardfork 23
#from script_params_customized import *

# exclude images from search
#from script_params_full_no_images import * # takes longer to process every matching url

# do the opposite and only match image links
#from script_params_full_only_images import *

#from script_params_full import * # takes longer to process every matching url

# only lists posts which contain URL matches including 'steemit' in them (but can be changed obviously), without matching images or testing for broken links
#from script_params_minimal_settings import *

# same as above, outputs to text file, possibly usable by a script
#from script_params_minimal_text_file_output import *

# =====================
# end script parameters
#

# clear color legend for the html results file
if human_readable_output and test_broken_links:
    functions.script_params_html += '<h3>Color Legend:</h3>\n'
    add_to_output('<span style="font-size:12px;color:green">&#9632</span> OK status', print_also=False)
    add_to_output('<span style="font-size:12px;color:red">&#9632</span> NOK status, possibly broken links (error code and reason are also shown); sometimes errors are temporary or only returned to this type of link checking, not to regular browsing', print_also=False)
    add_to_output('<span style="font-size:12px;color:darkorange">&#9632</span> also possibly broken links, caught by different exceptions which only show reason, not status and reason', print_also=False)
    add_to_output('<span style="font-size:12px;color:darkgray">&#9632</span> already tested or not tested. If already tested, previous tested reason is displayed. For not tested, reason for not testing should be provided.', print_also=False)
    if find_images_too and not find_images_only:
        add_to_output('<a href="#">link</a> regular link', print_also=False)
        add_to_output('<span class="image_link_mixed"><a href="#">link</a></span> link of image', print_also=False)

#create results directory (as a subdirectory or sub-path of the current directory)
try:
    os.makedirs(results_dir)
    print('Directory ' + results_dir + ' created in current directory ' + os.curdir)
except FileExistsError:
    print('Directory ' + results_dir + ' already exists in current directory ' + os.curdir)
except OSError:
    print('Directory ' + results_dir + ' couldn\'t be created in current directory ' + os.curdir)

# create results file (overwrite if exists)
try:
    f = open(results_dir + '/' + results_filename, 'w+')
    if human_readable_output:
        f.writelines(['<html>\n', '<head><link rel="stylesheet" href="../main.css"></head>', '<body>\n', functions.script_params_html,'<h3>List of matches:</h3>\n'])
    else:
        f.writelines([url_to_find + '\n'])
    f.close()
    f = open(results_dir + '/' + results_filename, 'a')
except OSError:
    print('Something went wrong while attempting to write file ' + results_dir + '/' + results_filename)
    raise OSError

total_matches_found = 0
# used to count posts where matches are found,
# and to have a line match between the html and txt outputs,
# in case someone wants to manually go through the results
# and sync them before feeding the text file to a script
line_number = 1

# loops through all the posts of the given author
i = FIRST_POST_NUMBER_TO_SEARCH
while True:

    if i > LAST_POST_NUMBER_TO_SEARCH: break

    if i % 50 == 0: print("Searched through " + str(i) + " posts...")    
    
    #retrieve current blog post info    
    try:
        blogs = acc.get_blog(i, 1, raw_data=True)
    except Exception:
        print('Couldn\'t get blog #' + str(i) + '. Trying again. Ctrl+C to interrupt.')
        continue
    # is it empty? then we reached the end and we should break out of the loop
    if blogs == []: break

    # filter posts by date
    if post_created_before_datetime or post_created_after_datetime:
        post_creation_datetime_str = blogs[0]['comment']['created']
        post_creation_datetime = datetime.strptime(post_creation_datetime_str, '%Y-%m-%dT%H:%M:%S')
        if post_created_before_datetime and post_creation_datetime > post_created_before_datetime:
            i += 1
            continue
        if post_created_after_datetime and post_creation_datetime < post_created_after_datetime:
            i += 1
            continue

    # is it the author's post or a resteem?
    # if it's a resteem continue from the next iteration
    if blogs[0]['comment']['author'] != author_name:        
        i += 1
        continue

    #deserialize json_metadata
    json_metadata_str = blogs[0]['comment']['json_metadata']
    json_metadata_dict = json.loads(json_metadata_str)

    try:
        format = json_metadata_dict['format']        
    except KeyError:
        # json not properly formatted; defaulting format to 'markdown+html'
        format = 'markdown+html'
    # get the name of the app used to create the post
    try:
        app = json_metadata_dict['app']
    except KeyError:
        # json not properly formatted; defaulting app name to 'steemit'
        app = 'steemit'

    # filtering by app?
    if use_post_created_by_app_list:
        app_match_include = False
        for x in post_created_by_list:
            if str(app).lower().find(x) != -1:
                app_match_include = True
                break
        if not app_match_include:
            i += 1
            continue
    if use_post_not_created_by_app_list:
        app_match_exclude = False
        for x in post_not_created_by_list:
            if str(app).lower().find(x) != -1:
                app_match_exclude = True
                break
        if app_match_exclude:
            i += 1
            continue

    # get the permlink
    permlink = blogs[0]['comment']['permlink']

    # get post body
    body = blogs[0]['comment']['body']

    # is the post in markdown or markdown+html format?
    if format == 'markdown+html' or format == 'markdown':                    

        # get post main category
        post_category = blogs[0]['comment']['category']
        
        # define the find images filter regex, based on script parameters
        if find_images_too:
            if find_images_only:
                find_images_regex = r"(\!)"
            else:
                find_images_regex = r"(\!?)"
        else:
            find_images_regex = r"([^\!]{1})"

        # define the regex to use to find all URLs matching search criteria
        if exact_URL_match:
            if not url_to_find:
                print('You can\'t search for an exact match for an empty string!\nPlease fix the script params:\neither set exact_URL_match to False or provide a url_to_find).')
                exit()
            else:
                regex = find_images_regex + r'\[([\w\s\d!@#$%^&*()_\-+:;\'"|<>,.?/]+)\]\((' + re.escape(url_to_find) + r')\)'
        elif exact_URL_beginning:
            if not url_to_find:
                regex = find_images_regex + r'\[([\w\s\d!@#$%^&*()_\-+:;\'"|<>,.?/]+)\]\(((?:\/|https?:\/\/|)[\w\d./@?=\-#]+)\)'
            else:
                regex = find_images_regex + r'\[([\w\s\d!@#$%^&*()_\-+:;\'"|<>,.?/]+)\]\((' + re.escape(url_to_find) + r'[\w\d./@?=\-#]*)\)'
        else:
            if not url_to_find:
                regex = find_images_regex + r'\[([\w\s\d!@#$%^&*()_\-+:;\'"|<>,.?/]+)\]\(((?:\/|https?:\/\/|)[\w\d./@?=\-#]+)\)'
            else:
                regex = find_images_regex + r'\[([\w\s\d!@#$%^&*()_\-+:;\'"|<>,.?/]+)\]\(((?:\/|https?:\/\/|)' + re.escape(url_to_find) + r'[\w\d./@?=\-#]*)\)'
        # find all matches of regex defined above in the post body
        results = re.findall(regex, body)
        cnt = len(results)
        if cnt > 0:
            if human_readable_output:                
                # append match to results file
                try:
                    # write in results file a link to the post with the number of matches found
                    link = interface_to_open_posts + '/' + post_category + '/@' + author_name + '/' + permlink
                    if cnt == 1:
                        f.writelines(['<p class="posts">' + str(line_number) + '#: ' + str(cnt) +' match found in post <a href="'+link+'" target="_blank">'+link+'</a></p>\n'])
                    else:
                        f.writelines(['<p class="posts">' + str(line_number) + '#: ' + str(cnt) +' matches found in post <a href="'+link+'" target="_blank">'+link+'</a></p>\n'])
                    # if you test for broken links, go through each URL, test it and add result to html
                    if test_broken_links:
                        for match in results:
                            test_broken_links_html = ''                        
                            # exclude URL from testing based on domain filtering?
                            do_not_test_url = False
                            if exclude_urls_by_domain:
                                for x in domain_exclusion_list:
                                    if match[2].find(x['domain']) != -1:
                                        do_not_test_url = True
                                        resp_dict['via'] = 'not_tested'
                                        resp_dict['reason'] = x['reason']
                                        resp_dict['status'] = -1
                                        break
                            if not do_not_test_url:
                                # already tested url?
                                already_tested = False
                                for x in tested_urls:
                                    if x['url'] == match[2]:                                    
                                        resp_dict['via'] = 'already_tested'
                                        resp_dict['status'] = x['status']
                                        resp_dict['reason'] = x['reason']
                                        already_tested = True
                                        break

                                if not already_tested:
                                    resp_dict = test_url(match[2])
                                    if resp_dict:                                
                                        # potentially image that cannot be accessed directly
                                        if match[0] == '!' and \
                                        ((resp_dict['via'] == 'except_OSError' and resp_dict['reason'] == 'NONE') or \
                                            (resp_dict['via'] == 'except_URLError' and resp_dict['reason'] == '[ERRNO 111] CONNECTION REFUSED') or \
                                            (resp_dict['via'] == 'except_HTTPError' and str(resp_dict['reason']).upper() == 'BAD GATEWAY')):

                                            resp_dict.clear()
                                            resp_dict = test_url(images_base_url + match[2])
                                            if resp_dict:
                                                if resp_dict['status'] != 200:
                                                    resp_dict['via'] = 'OSError'
                                                    resp_dict['reason'] = 'NONE'

                                        # potentially needs protocol or default interface to open posts url added at the beginning
                                        if resp_dict['via'] == 'except_ValueError' and str(resp_dict['reason']).find('UNKNOWN URL TYPE') != -1:
                                            resp_dict_backup = resp_dict.copy()
                                            resp_dict.clear()
                                            resp_dict = test_url('https://' + match[2])
                                            if resp_dict:
                                                if resp_dict['status'] != 200:
                                                    resp_dict.clear()
                                                    resp_dict = test_url('http://' + match[2])                                            
                                                    if resp_dict:
                                                        if resp_dict['status'] != 200:
                                                            resp_dict.clear()
                                                            resp_dict = test_url(interface_to_open_posts + '/' + match[2])
                                                            if resp_dict:
                                                                if resp_dict['status'] != 200:                                                            
                                                                    resp_dict.clear()
                                                                    resp_dict = resp_dict_backup.copy()
                                            resp_dict_backup.clear()
                            # build test status text for URL
                            if resp_dict['via'] == 'try':
                                if resp_dict['status'] == 200:
                                    test_broken_links_html = ' <b>Status:</b> <span class="status_ok">OK</span>'
                                else:
                                    test_broken_links_html = ' <b>Status:</b> <span class="status_broken">NOK</span> ('+ str(resp_dict['status']) + ' ' + resp_dict['reason'] + ')'
                            elif resp_dict['via'] == 'except_HTTPError':
                                test_broken_links_html = ' <b>Status:</b> <span class="status_broken">NOK</span> ('+ str(resp_dict['status']) + ' ' + resp_dict['reason'] + ')'
                            elif resp_dict['via'] == 'except_URLError':
                                test_broken_links_html = ' <b>Status:</b> <span class="status_py_error"> '+ str(resp_dict['reason']).upper() + '</span>'
                            elif resp_dict['via'] == 'except_ValueError':
                                test_broken_links_html = ' <b>Status:</b> <span class="status_py_error"> '+ str(resp_dict['reason']).upper() + '</span>'
                            elif resp_dict['via'] == 'except_OSError':
                                test_broken_links_html = ' <b>Status:</b> <span class="status_py_error"> '+ str(resp_dict['reason']).upper() + '</span>'
                            elif resp_dict['via'] == 'already_tested':
                                test_broken_links_html = ' <b>Status:</b> <span class="status_already_tested"> '+ str(resp_dict['reason']).upper() + '</span>'
                            elif resp_dict['via'] == 'not_tested':
                                test_broken_links_html = ' <b>Status:</b> <span class="status_not_tested">NOT TESTED</span> <span class="status_not_tested_reason">('+ resp_dict['reason'] + ')</span>'
                            else:
                                test_broken_links_html = ' <b>Status:</b> <span class="status_py_error">Unexpected Error!</span>'
                            # build up a list with URLs already tested; they won't be tested again if found again
                            if not already_tested:
                                    tested_urls.append({'url':match[2], 'status':resp_dict['status'], 'reason':resp_dict['reason']})                            
                            resp_dict.clear()

                            if match[0] == '!' and not find_images_only:
                                f.writelines(['<p class="match"><a title="'+match[1]+'" href="'+match[2]+'" target="_blank" class="image_link_mixed">'+match[2]+'</a>'+test_broken_links_html+'</p>\n'])
                            else:
                                f.writelines(['<p class="match"><a title="'+match[1]+'" href="'+match[2]+'" target="_blank">'+match[2]+'</a>'+test_broken_links_html+'</p>\n'])
                except OSError:
                    print('Something went wrong while attempting to write file ' + results_filename)
                    raise OSError
            else: # script output
                # append match to results file
                try:
                    link = permlink
                    f.writelines([str(line_number) + '#: ' + link + '\n'])
                except OSError:
                    print('Something went wrong while attempting to write file ' + results_filename)
                    raise OSError
            # show each post with matches on screen too
            if cnt == 1:
                print(str(line_number) + '#: ' + str(cnt) + ' match in post ' + permlink)
            else:
                print(str(line_number) + '#: ' + str(cnt) + ' matches in post ' + permlink)

            line_number += 1
            total_matches_found += cnt

    #or is the post raw html?
    else:        
        print('Raw html posts not supported yet at #' + str(i) + ': ' + permlink)
            
    i+=1

print('No (more) posts.')

if test_broken_links:
    tested_urls.clear()

if not url_to_find:
    print('Total URLs found in posts of user ' + author_name + ', based on current filters: ' + str(total_matches_found))
else:
    print('Total matches found for URL\n' + url_to_find + '\nin posts of user ' + author_name + ', based on current filters: ' + str(total_matches_found))

# Closing tags to the html results file (if html, i.e. human_readable_output)
try:
    if human_readable_output:        
        f.writelines(['<h3>Total matches found:'+ str(total_matches_found) +'</h3>\n','</body>\n','</html>'])
    f.close()    
except OSError:
    print('Something went wrong while attempting to write file ' + results_filename)
    raise OSError