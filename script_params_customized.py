from datetime import datetime

from functions import add_to_output, test_url, get_author
import functions

# URL to find
url_to_find = ''
if not url_to_find:
    add_to_output('URL to find: matches any URL')
else:
    add_to_output('URL to find: ' + url_to_find)
# allow partial matches for URL?
exact_URL_match = False
exact_URL_beginning = False
add_to_output('Exact URL matching? ' + str(exact_URL_match))
add_to_output('Exact URL beginning? ' + str(exact_URL_beginning))

# when testing for broken links the requested response of the
# matched URL pages can considerably slow down the search;
# make sure you set stricter search filters and
# don't abuse it, target websites may not like it, even if we don't scrape anything
test_broken_links = True
add_to_output('Test for broken links? ' + str(test_broken_links))
# set tineout in seconds before the test_url function def (in functions.py)
if test_broken_links:
    tested_urls = []
    add_to_output('Test broken links timeout: ' + str(functions.TEST_BROKEN_LINKS_TIMEOUT))

# FILTERS

# filter posts by number
FIRST_POST_NUMBER_TO_SEARCH = 1
LAST_POST_NUMBER_TO_SEARCH = 100000
add_to_output('Search posts from #'+ str(FIRST_POST_NUMBER_TO_SEARCH) +' to max #'+ str(LAST_POST_NUMBER_TO_SEARCH))

# image-related filters
find_images_too = True
find_images_only = False # works only if find_images_too is True
if find_images_too and find_images_only:
    add_to_output('Find images only? '+ str(find_images_only))
else:
    add_to_output('Find images too? '+ str(find_images_too))
# what base path to use for images, when an error is thrown for the direct link?
images_base_url = 'https://images.hive.blog/0x0/'
if find_images_too:
    add_to_output('Base path for images, when error on direct link: '+ images_base_url)

# filters by creation date
# Use None if you don't want to filter the results by that option

post_created_before_datetime = None
post_created_after_datetime = datetime.fromisoformat('2020-03-20T14:00:00')

if post_created_after_datetime != None and post_created_before_datetime != None:
    add_to_output('Only posts between ' + str(post_created_before_datetime))
    add_to_output('  and ' + str(post_created_after_datetime) + ' are included in the search.')
elif post_created_after_datetime != None:
    add_to_output('Only posts more recent than ' + str(post_created_after_datetime) + ' are included in the search.')
elif post_created_before_datetime != None:
    add_to_output('Only posts older than ' + str(post_created_before_datetime) + ' are included in the search.')
else:
    add_to_output('Posts not filtered by date.')


# Include/exclude posts created by certain apps.
# It works like partial matches, meaning if the app field
# 'contains' the listed string, it is considered a match

use_post_created_by_app_list = False
post_created_by_list = ['steemit', 'steempeak', 'busy', 'peakd'] # use lowercase
if use_post_created_by_app_list:
    add_to_output('Include posts created by ' + str(post_created_by_list))
use_post_not_created_by_app_list = False
post_not_created_by_list = ['steepshot'] # use lowercase
if use_post_not_created_by_app_list:
    add_to_output('Exclude posts created by ' + str(post_not_created_by_list))

# Exclude URLs based on domain (subdomain+domain) match.
# Status will be 'NOT TESTED" + a reason for not testing.

exclude_urls_by_domain = True
domain_exclusion_list = [{'domain':'pixabay.com', 'reason':'Returns 403 Forbidden errors, but OK via normal browsing'},
                         {'domain':'support.binance.com', 'reason':'Returns 403 Forbidden errors, but OK via normal browsing'},
                         {'domain':'steepshot.org', 'reason':'Always times out'}]
if exclude_urls_by_domain:
    add_to_output('Refrain from testing URls with these domains for the following reasons: ' + str(domain_exclusion_list))

# OUTPUT

# the results file name (no extension)

# add datetime to filename to create different result files every time,
# based on potentially different script params
add_datetime_to_filename = True
print('Add datetime to filename? '+ str(add_datetime_to_filename))
time_str = ''
if add_datetime_to_filename:
    now = datetime.now()
    time_str = now.strftime('-%y-%m-%d_%H-%M')
results_dir = 'results-finding-urls-in-posts'
results_filename = get_author() + time_str
# prepare human-readable output or ready for script
human_readable_output = True
if human_readable_output:
    results_filename += ".html"
else: results_filename += ".txt"
print('Results file name: ' + results_filename)
print('Human readable output? ' + str(human_readable_output))