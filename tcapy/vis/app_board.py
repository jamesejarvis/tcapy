"""This provides the entry point for the GUI web application, which uses the Dash library on top lightweight server
web application (eg. Flask). This version allows users to upload a CSV file with their trades.

It queries TCAEngine, which returns appropriate TCA output (via TCACaller). Uses LayoutDash
class to render the layout and SessionManager to keep track of each user session.

"""
from __future__ import division, print_function

__author__ = 'saeedamen' # Saeed Amen / saeed@cuemacro.com

#
# Copyright 2019 Cuemacro Ltd. - http//www.cuemacro.com / @cuemacro
#
# See the License for the specific language governing permissions and limitations under the License.
#

from tcapy.vis.app_imports import *

# Create Flask object and create Dash instance on top of it
server = Flask(__name__)

debug_start_flask_server_directly = constants.debug_start_flask_server_directly

# Add a static image/css route that serves images from desktop
# be *very* careful here - you don't want to serve arbitrary files
# from your computer or server
if debug_start_flask_server_directly:
    url_prefix = ''
else:
    url_prefix = 'tcapyboard' # eg. if hosted on "http://localhost/tcapyboard" (can also be empty)
    # url_prefix = constants.url_prefix # eg. if hosted on "http://localhost/tcapy" (can also be empty)

stylesheets = ['tcapy.css']

if url_prefix == '':
    static_css_route = '/static/'
else:
    static_css_route = '/' + url_prefix + '/static/'

stylesheets_path = []

for css in stylesheets:
    # app.css.append_css({"external_url": static_css_route + css})
    stylesheets_path.append(static_css_route + css)

app = dash.Dash(name='tcapyboard', server=server, suppress_callback_exceptions=True, serve_locally=True, external_stylesheets=stylesheets_path)
app.title = 'tcapyboard'
app.server.secret_key = constants.secret_key

# allow tcapy to be hosted on a different url eg. not on root
if debug_start_flask_server_directly:

    app.config.update({
        'routes_pathname_prefix': '/',
        'requests_pathname_prefix': '/',
    })

else:
    app.config.update({
        'routes_pathname_prefix': '/tcapyboard/',
        'requests_pathname_prefix': '/tcapyboard/'
    })

callback_dict = {}
callback_dict['aggregated'] = ['csv-uploadbox', 'market-data-val', 'calculation-button']

# this loads up a user specific version of the layout and TCA application
if constants.tcapy_version == 'user':
    try:
        # user customised version (not currently available so disable)
        from tcapyuser.layoutboarduser import *;

        layout = LayoutImplBoardUser(app=app, constants=constants, url_prefix=url_prefix)
        from tcapyuser.tcacallerboarduser import TCACallerImplBoardUser as TCACaller
    except:
        from tcapygen.layoutboardgen import *;

        layout = LayoutDashImplBoardGen(app=app, constants=constants, url_prefix=url_prefix)
        from tcapygen.tcacallerboardgen import TCACallerImplBoardGen as TCACaller

# this loads up a generic version of the layout and TCA application
elif constants.tcapy_version == 'test_tcapy' or constants.tcapy_version == 'gen':
    from tcapygen.layoutboardgen import *;

    layout = LayoutDashImplBoardGen(app=app, url_prefix=url_prefix, constants=constants)
    from tcapygen.tcacallerboardgen import TCACallerImplBoardGen as TCACaller

# you can add your own additional layout versions here
# app.config['SESSION_TYPE'] = 'memcached'

########################################################################################################################

logger.info("Root path = " + app.server.root_path)

#app.config.supress_callback_exceptions = True
#app.css.config.serve_locally = True
app.scripts.config.serve_locally = True # had issues fetching JS scripts remotely

logger.info("Connected to volatile cache/Redis server_host")

# Add a static image/css route that serves images from desktop
# be *very* careful here - you don't want to serve arbitrary files
# from your computer or server
cur_directory = app.server.root_path
stylesheets = ['tcapy.css']

# if url_prefix == '':
#     static_css_route = '/static/'
# else:
#     static_css_route = '/' + url_prefix + '/static/'
#
# for css in stylesheets:
#     app.css.append_css({"external_url": static_css_route + css})

# create the HTML layout for the pages (note: this is in a separate file layoutdash.py)
app.layout = layout.page_content

plain_css = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tcapy.css'), 'r').read()

# create objects for caching data for clients sessions (and also internally for the server)
glob_volatile_cache = Mediator.get_volatile_cache()

########################################################################################################################

@app.server.route('/static/<path>')
def static_file(path):
    return flask.send_from_directory(cur_directory, path)

# control the interaction between pages
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    # delete any session id based keys (ie. refresh cache for the user)
    glob_volatile_cache.clear_key_match(session_manager.get_session_id() + "*")

    if pathname is not None:

        if url_prefix == '':
            pathname = pathname.replace('/', '')
        else:
            pathname = pathname.replace('/' + url_prefix + '/', '')

        if pathname in util_func.dict_key_list(layout.pages.keys()):
            return layout.pages[pathname]

    # by default, return the detailed page
    return layout.pages['aggregated']

@app.server.route('/urlToDownload')
def serve_csv():

    dataFrame = flask.request.args.get('dataFrame')

    strIO = display_listeners.create_df_as_csv_string(dataFrame)

    return flask.send_file(strIO,
                     mimetype='text/csv',
                     attachment_filename=dataFrame.replace('-', '_') + '.csv',
                     as_attachment=True)

@app.server.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(app.server.root_path, 'favicon.ico')

########################################################################################################################

from tcapy.vis.displaylisteners import DisplayListeners

# converts GUI output into TCARequest objects and this then calls TCAEngine (adds listeners for the processing buttons)
tca_caller = TCACaller(app, session_manager, callback_manager, glob_volatile_cache, layout, callback_dict=callback_dict)

# adds listeners/code for each GUI display components which show the dataframes generated by TCACaller/TCAEngine
display_listeners = DisplayListeners(app, layout, session_manager, callback_manager, tca_caller, plain_css, url_prefix)

if __name__ == '__main__':
    # need this for WINDOWS machines, to ensure multiprocessing stuff works properly
    from tcapy.util.swim import Swim; Swim()

    app.run_server(threaded=True) # debug=True
