
# coding: utf-8

# # Cinergi Jupyter Notebook Dispatcher based on metadata content
# 
# ### Execute the cells below to get parameters from Cinergi and select a notebook for processing ###
# 

# First cell executes some Javascript.
# 
# the execute command defines the variables documentID, user, and full_notebook_url used later in python
# 
# The Javascript function getQueryString takes 'key' argument that is a string parameter name. The calling URL that opens the notebook will return the value assigned to that URL parameter if the parameter is present. 
# example URL: http://suave-jupyterhub.com/user/zeppelin-v/notebooks/CinergiDispatch-UseMetadata.ipynb?documentId=f8617294d50d494dae64d8286fb2efaa
# 
# http://{jupypter hub host}/user/{user registered with the hub}/notebooks/{name of this notebook}?{parameter1}={value1}

# In[1]:

# get_ipython().run_cell_magic(u'javascript', u'', u'function getQueryStringValue (key)\n{  \n    return unescape(window.location.search.replace(new RegExp("^(?:.*[&\\\\?]" + escape(key).replace(/[\\.\\+\\*]/g, "\\\\$&") + "(?:\\\\=([^&]*))?)?.*$", "i"), "$1"));\n}\nIPython.notebook.kernel.execute("documentID=\'".concat(getQueryStringValue("documentId")).concat("\'"));\nIPython.notebook.kernel.execute("user=\'".concat(getQueryStringValue("user")).concat("\'"));\nIPython.notebook.kernel.execute("full_notebook_url=\'" + window.location + "\'"); \n')


# ## Parameters passed to workbench: ##

# In[2]:

# Check if the parameters are correct
import ntpath
#from __future__ import print_function
#from ipywidgets import interact, interactive, fixed, interact_manual
#import ipywidgets as widgets
import webbrowser
#url_partitioned = full_notebook_url.partition('/CinergiDispatch')
#base_url = url_partitioned[0];

# echo variables for clarity
#print("User: ",user)
#print("DocumentID: ", documentID)
#print("full notebook url partition", url_partitioned)
#print("full notebook url", full_notebook_url)


# #ToDo: 
# 1. get the metadata record for the URL; probably have to call ESRI JSON because of uncertainty about what dialect the XML will use
# 2. extract distribution and format information to use for filtering the action options
# 3. offer user choice of workbench actions
# 4. execute action; this will likely be a system command or opening another URL that might be another notebook or some other web application
# 

# In[3]:

import json

import requests
from lxml import etree  #supposed to be better than xml.etree
import sys
#import xml.etree.ElementTree as ET
from io import StringIO,BytesIO
from owslib.wfs import WebFeatureService
from shapely.geometry import Polygon, mapping, asShape, shape

catalogURL = "http://cinergi.sdsc.edu/geoportal/"
#documentID="e3619c5df2644204b67f51f48525a0b1"
documentID="4db8156abb6d4119aa5c35aa39514b42"

metadataURL=catalogURL + 'rest/metadata/item/' + documentID

print ("metadata URL: ", metadataURL)

the_page = requests.get(metadataURL)

thejson=json.loads(the_page.text)

for resource in thejson["_source"]["resources_nst"]:
    #print (resource["url_type_s"])
    if resource["url_type_s"] == 'WFS':
        #print("WFS link: ",resource["url_s"])
        resourceurl=resource["url_s"]
        
        url_partitioned = resourceurl.partition('?')
        base_url = url_partitioned[0];
        print("base URL: ",base_url)
        wfs = WebFeatureService(base_url, version='1.1.0')
        
        break
        
if not (wfs):
    print ("no wfs found")
    sys.exit()

print (list(wfs.contents))


# In[ ]:

a = wfs.contents['sb:footprint']
b = a.boundingBoxWGS84
shp = wfs.contents.keys()
print(shp)
shp = filter(lambda a: a != 'sb:footprint', shp)
featurelist=list(shp)
print(featurelist)


#         
#         if ("etcapabilities" in resourceurl.lower()) and ("service=wfs" in resourceurl.lower()):
#             #check that are requesting v1.1.0
#             if ("version=1.1.0" in resourceurl):
#                 resourceurl=resourceurl
#             elif ("version=1.0.0" in resourceurl):
#                 resourceurl=resourceurl.replace("version=1.0.0","version=1.1.0")
#             elif ("version=2.0.0" in resourceurl):
#                 resourceurl=resourceurl.replace("version=2.0.0","version=1.1.0")
#             elif not ("version=" in resourceurl):
#                 resourceurl=resourceurl +  "version=1.1.0"    
#             print("Resource URL: ",resourceurl)
#             thecap=requests.get(resourceurl)
#             print(requests.head(resourceurl))
#             #print("WFS capabilities: ",thecap.text)
#             
# #thecap=requests.get('https://www.sciencebase.gov/catalogMaps/mapping/ows/5032ab9de4b0d64661a77224?version=1.1.0&service=wfs&request=GetCapabilities')
# 
# 
#     
# #print(thejson["_source"]["resources_nst"][1]["url_type_s"])

# In[ ]:

#namespaces = {'ows':'http://www.opengis.net/ows'} # add more as needed

#root.findall('owl:Class', namespaces)
# StringIO(thecap.text)
""" if thecap:
    tree = etree.parse(BytesIO(thecap.text))
    root = tree.getroot()  
    namespaces=root.nsmap
    print(namespaces)
    #print(tree.find(".//ows:Operation[@name='GetFeature']/ows:Parameter[@name='outputFormat']",namespaces))
    formatparameters=tree.find(".//ows:Operation[@name='GetFeature']/ows:Parameter[@name='outputFormat']",namespaces)
    formats=formatparameters.findall(".//ows:Value",namespaces)
    #print(formats)
    for aformat in formats:
        if 'json' in aformat.text: 
            print(aformat.text)

 """
# ## Select a notebook and open its URL##

# In[ ]:

nb_menu = {
    '1. ndbc-explore': 'cinergi/ndbc-explore.ipynb',
    '2. ndbc-explore_v3': 'cinergi/ndbc-explore_v3.ipynb',
    '3. ndbc-explore_v2': 'cinergi/ndbc-explore_v2.ipynb',
    '4. NWIS-explore': 'cinergi/NWIS-explore.ipynb',
}
def f(notebooks_menu):
    return notebooks_menu
# out = interact(f, notebooks_menu=nb_menu);
out = interact(f, notebooks_menu=nb_menu.keys());

print("interact out: ", out)


# In[ ]:

chosen_nb_name = nb_menu[out.widget.result]
url1 = ('{base_url}/operations/{nb_name}?'+'docID='+documentID+'&'+'user='+user).format(base_url=base_url, nb_name=chosen_nb_name)

#webbrowser.open(url1)
webbrowser.open_new(url1)
print(url1)

#  CLICK TO OPEN THE URL BELOW


# In[ ]:



