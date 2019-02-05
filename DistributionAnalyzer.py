
# coding: utf-8

# # Extract Distribution information from ISO 19139 metadata
# 
# S.M. Richard 2018-08-03
# 
# This notebook is opened with a documentID used to pull an ISO XML record from the CINERGI catalog;
# The record is parsed to extract distribution information and generate a dispatchList object
# 
# The plan is for the dispatch list object to get passed to a dispatcher (and maybe stored with the metadata record for use by other dispatchers. The dispatcher would accesses a mapping resource that associates endpoint applications and application profiles in the dispatchList.
# 
# Currently the dispatch list is a JSON array of objects. e.g. : ``` {"profile":"nwis_rdb", "url":theURL, "label":thename } ```
# 
# ###  profile
# 
# (ideally) should be a registered URI that characterizes the protocol and interchange formats that are used to access a service.  Current demo vocabulary includes:
# * nwis_rdb -- service implements http access that serves NWIS text documents following the rdb format; TBD: think about differentiating various NWIS services. 
#   * uv -- current data 
#   * gwlevels -- groundwater levels
#   * peak -- peak stream flow at gage
#   * inventory -- site information. No time series information, but useful for location information
#   * measurements -- streamflow data for site; https://help.waterdata.usgs.gov/output-formats#streamflow_measurement_data. data files do not include the variable names in header
# * wfsclient -- service that implements OGC WFS simple feature profile on http. should work with any version of WFS (1.0.0, 1.1.0, 2.0). TBD: specializations based on feature types offered; handle complex features
# * webbrowser -- service implements http and can display html documents. TBD -- extend to include any kind of document that standard web browser can display (.tif, .jpg,....)
# 
# ### url
# The URL that is expected under the profile for a client to access a specific resource
# 
# ### label
# A text string to display in user interfaces to label links to access the application with the selected data.

# In[71]:
# package dependency imports

import requests
from lxml import etree  #supposed to be better than xml.etree
#from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
from tqdm import tqdm
from IPython.display import clear_output

#import xmltodict
#import json
#from io import StringIO,BytesIO


# In[72]:
# get_ipython().run_cell_magic(u'javascript', u'', u'function getQueryStringValue (key)\n{  \n    return unescape(window.location.search.replace(new RegExp("^(?:.*[&\\\\?]" + escape(key).replace(/[\\.\\+\\*]/g, "\\\\$&") + "(?:\\\\=([^&]*))?)?.*$", "i"), "$1"));\n}\nIPython.notebook.kernel.execute("documentID=\'".concat(getQueryStringValue("documentId")).concat("\'"));\nIPython.notebook.kernel.execute("user=\'".concat(getQueryStringValue("user")).concat("\'"));\nIPython.notebook.kernel.execute("full_notebook_url=\'" + window.location + "\'"); ')


# In[73]:
def testurl(theurl):
    #try HEAD first in case the response document is big

    try:
        r = requests.head(theurl)
        if (r.status_code != requests.codes.ok):
            #check GET in case is an incomplete http implementation
            r = requests.get(theurl)
            if (r.status_code == requests.codes.ok):
                return True
            else:
                return False
        else:
            return True
    except:
        return False


# In[74]:

documentID = ""
# use hardwired values for testing
catalogURL = "http://cinergi.sdsc.edu/geoportal/"
if (len(documentID)==0):
    #documentID="e3619c5df2644204b67f51f48525a0b1"
    documentID="4db8156abb6d4119aa5c35aa39514b42"


# In[75]:
""" 
url_partitioned = full_notebook_url.partition('ISOmetadataDispatcher.ipynb')
base_url = url_partitioned[0];

print("User: ",user)
print("DocumentID: ", documentID)
print("full notebook url partition", url_partitioned)
print("full notebook url", full_notebook_url)

 """
# In[76]:
#get the url to retrieve xml record from catalog
metadataURLx=catalogURL + 'rest/metadata/item/' + documentID + '/xml'

print ("metadata URL: ", metadataURLx)

#get the xml record
the_page = requests.get(metadataURLx)



# In[78]:
#set up namespace map for ISO metadata
NSMAP = {"gmi":"http://www.isotc211.org/2005/gmi" ,
    "gco":"http://www.isotc211.org/2005/gco" ,
    "gmd":"http://www.isotc211.org/2005/gmd" ,
    "gml":"http://www.opengis.net/gml" ,
    "gmx":"http://www.isotc211.org/2005/gmx" ,
    "gts":"http://www.isotc211.org/2005/gts" ,
    "srv":"http://www.isotc211.org/2005/srv" ,
    "xlink":"http://www.w3.org/1999/xlink"}


# In[79]:
#root = etree.fromstring(the_page.text)
#tree is an element tree
tree = etree.parse(metadataURLx)
#root = etree.tostring(tree.getroot())
root = tree.getroot()
docinfo = tree.docinfo
print(docinfo.xml_version)
#print(tree.findall("//gmd:MD_DigitalTransferOptions",namespaces=NSMAP))



# In[93]:
#iterate through digital transfer options and set up dispatch object
# dispatch list is a list of 'options' consisting of 
# {an application profile (string, from EC resource registry) that the disptcher will use to identify target notebooks, 
#   the URL for the information resource input to the target for that profile}
# e.g. dispatchlist = [{"profile":"profile1","url":"url1"}, {"profile":"profile2","url":"url2"}]

dispatchlist = []

for  elt in tree.getiterator("{http://www.isotc211.org/2005/gmd}MD_DigitalTransferOptions"):
    # only want OnlineResources that are in distribution//MD_DigitalTransferOptions
    #  TBD-- figure out what to do with CI_OnlineResource inside SV_OperationMetadata
    #print elt.text
#iterate through CI_OnlineResource elements
    for onlineres in elt.getiterator("{http://www.isotc211.org/2005/gmd}CI_OnlineResource"):
        if (onlineres.find("gmd:linkage/gmd:URL",namespaces=NSMAP) is not None):
            theURL=onlineres.find("gmd:linkage/gmd:URL",namespaces=NSMAP).text
        else:
            continue #don't bother if there's no URL!
        
        if (onlineres.find("gmd:name/gco:CharacterString",namespaces=NSMAP) is not None):
            thename=onlineres.find("gmd:name/gco:CharacterString",namespaces=NSMAP).text
        else:
            thename=''
        
        if (onlineres.find("gmd:description/gco:CharacterString",namespaces=NSMAP) is not None):
            thedescription=onlineres.find("gmd:description/gco:CharacterString",namespaces=NSMAP).text
        else:
            thedescription=''
            
        if (onlineres.find("gmd:protocol/gco:CharacterString",namespaces=NSMAP) is not None):
            theprotocol=onlineres.find("gmd:protocol/gco:CharacterString",namespaces=NSMAP).text
        else:
            theprotocol=''
        
        if (onlineres.find("gmd:applicationProfile/gco:CharacterString",namespaces=NSMAP) is not None):
            theappprofile=onlineres.find("gmd:applicationProfile/gco:CharacterString",namespaces=NSMAP).text
        else:
            theappprofile=''
            
        if (onlineres.find("gmd:function/gmd:CI_OnLineFunctionCode",namespaces=NSMAP) is not None):
            thefunctioncode=onlineres.find("gmd:function/gmd:CI_OnLineFunctionCode",namespaces=NSMAP).get("codeListValue")
        else:
            thefunctioncode=''
            
        if (onlineres.find("gmd:function/gmd:CI_OnLineFunctionCode",namespaces=NSMAP) is not None):    
            thefunctiontext=onlineres.find("gmd:function/gmd:CI_OnLineFunctionCode",namespaces=NSMAP).text
        else:
            thefunctiontext=''
            
        print('\n Distribution: name-%s;\n  url- %s; \n  description--%s; \n   protocol-%s, app profile- %s; function- %s; %s' %
              (thename,theURL,thedescription,theprotocol,theappprofile,thefunctioncode,thefunctiontext))
        
        #print('wfs test: %s' % (theURL.lower().find('service=wfs')>-1))
        #print('base url %s'% (theURL.split('?')[0]))
        
        # series of tests to determine what application profiles are applicable for this online resource
        #check for OGC WFS Web feature service
        if (theprotocol.lower().find('wfs')>-1 or
           theURL.lower().find('service=wfs')>-1):       
            # append to dispatchlist
            # wfs disptacher gets the base URL for the service
            #check if service is responding
            tryurl=theURL.split('?')[0] + '?service=wfs&request=getCapabilities'
            if testurl(tryurl):
                dispatchlist.append({"profile":"wfsclient","url":theURL.split('?')[0],
                                    "label":thename})
            
        #check for OGC WMS; open in QGIS, ArcGIS, or OpenLayers web client
        if (theprotocol.lower().find('wms')>-1 or
           (theURL.lower().find('service=wms')>-1 and theURL.lower().find('request=kml')==-1) ):
            #kml test is because of GeoServer handling of kml response for wms
            # append to dispatchlist
            # wms disptacher gets the base URL for the service
            tryurl=theURL.split('?')[0] + '?service=wms&request=getCapabilities'
            if testurl(tryurl):
                dispatchlist.append({"profile":"wmsclient","url":theURL.split('?')[0],
                                    "label":thename})
            
        # KML client-- open in GoogleEarth or ?OpenLayers? kml client
        if (thedescription.lower().find('kml download')>-1 or
           (theURL.lower().find('request=kml')>-1 and theURL.lower().find('mode=download')>-1) or
           theURL.lower().find('.kml')>-1 or theURL.lower().find('.kmz')>-1):
            #kml test for GeoServer handling of kml response for wms
            # append to dispatchlist
            # wfs disptacher gets the base URL for the service
            if testurl(theURL):
                dispatchlist.append({"profile":"kmlclient","url":theURL,
                                    "label":thename})
            
        # other http URL-- check if the URL works
        if ((theURL.lower().find('.html')>-1 ) 
            or (theURL.lower().find('.pdf')>-1 )
            or (theURL.lower().find('.htm')>-1 )
            or  (theprotocol.lower().find('http')>-1)):
            #kml test for GeoServer handling of kml response for wms
            # append to dispatchlist
            # wfs disptacher gets the base URL for the service
            if testurl(theURL):
                r = requests.get(theURL)
                print('content type %s' % r.headers['Content-Type'])
                if ((r.headers['Content-Type'].find('html')>-1) 
                    or (r.headers['Content-Type'].find('application/pdf')>-1)):
                    dispatchlist.append({"profile":"webbrowser","url":theURL,
                                       "label":thename })
                    
        # nwis rdb data
        if ((theURL.lower().find('/nwis/qwdata')>-1 )
            or (theURL.lower().find('/nwis/gwlevels')>-1 )
            or (theURL.lower().find('/nwis/uv')>-1 )
            or (theURL.lower().find('/nwis/peak')>-1 )
            or (theURL.lower().find('/nwis/measurements')>-1)):
            # NWIS time series in rdb text file format
            if testurl(theURL):
                dispatchlist.append({"profile":"nwis_rdb","url":theURL,
                                       "label":thename })
                
        # national bouy center ncbc rdb data
        if (theURL.lower().find('www.ndbc.noaa.gov/view_text_file.php')>-1 ):
            #
            if testurl(theURL):
                dispatchlist.append({"profile":"ncbc_txt","url":theURL,
                                       "label":thename })
            
print('Dispatch List: %s' % dispatchlist)


# Call the dispatcher with the dispatchlist
# The dispatcher will need to access registry with mapping from application profile values to endpoints that will 'open' the url associated with that profile in the dispatch option.
# 
# In the long run, the dispatcher should be a separate component accessed via URL; start with it hard wired here.
# 
# 

# In[81]:
#Simple dispatcher with drop down picker
#Create dropdown Buttons and generate table 
data_dropdown_options = {} 

for option in dispatchlist:
    if (option['profile']=='wfsclient'):
        #offer links for apps that consume generic WFS
        #print('got wfs')
        wfsurl=base_url+ 'WFSprocessor.ipynb?endpoint='+option['url']
        label='Inspect dataset via OGC Web Feature Service' 
        data_dropdown_options[label]=wfsurl
    if (option['profile']=='webbrowser'):
        #offer links for apps that consume generic WFS
        label = 'Display ' + option['label'] + ' in browser'
        data_dropdown_options[label] = option['url']
    if (option['profile']=='nwis_rdb'):
        #offer links for apps that consume generic WFS
        nwisgdburl=base_url+ 'NWIS-explore2.ipynb?dataurl=' + option['url']
        label = 'Inspect NWIS time series ' + option['label']
        data_dropdown_options[label] = nwisgdburl
    if (option['profile']=='ncbc_txt'):
        #offer links for apps that consume generic WFS
        label = 'Inspect Bouy data time series ' + option['label']
        data_dropdown_options[label] = base_url + 'ndbc-explore_stmet.ipynb?dataurl=' + option['url']



# In[82]:


# one way to display pick list drop box
#print (data_dropdown_options)

#Create widget with dropdown options from list created above 
#def f(notebooks_menu): return notebooks_menu

#out = interact(f, notebooks_menu=nb_menu); 
#out = interact(f, notebooks_menu=data_dropdown_options.keys())

#chosen_url = data_dropdown_options[out.widget.result]


# In[83]:
def on_buttoncomment_clicked(b):
    pass #this will allow user to comment on what they found by following link

style = {'description_width': 'initial'}

buttoncomment = widgets.Button(description="Feedback")
buttoncomment.on_click(on_buttoncomment_clicked)


# In[84]:
#Describe what happens when the button changes its value
def on_change_url(change):
    global xaxisfield
    if change['type'] == 'change' and change['name'] == 'value':
        #print('change: ' + str(change['new']))
        result=change['new']
        
        chosen_url = data_dropdown_options[result]
        clear_output()
        display(pickurl)
        display(buttoncomment)
        print('To ' + result)
        print('Please click this URL: %s' % chosen_url)
    return


# In[85]:


#print(data_dropdown_options.keys())

#experimenting with widget formatting....

form_item_layout = widgets.Layout(
    display='flex',
    flex_flow='row',
    flex_grow=2,
    justify_content='space-between'
)

init_val='select action'  #this will be displayed in picklist when it opens
picklist=[init_val]
for item in data_dropdown_options.keys():
    picklist.append(item)  #append the keys from the endpoint options

pickurl = widgets.Dropdown(
    options=picklist,
    description='Pick endpoint to explore data:',
    disabled=False,
    style = style,
    layout=form_item_layout,
    value=init_val
)


if (len(picklist)==1):
    print('There are no recognized application profiles for this resource.')
else: 
    pickurl.observe(on_change_url)
    display(pickurl)

