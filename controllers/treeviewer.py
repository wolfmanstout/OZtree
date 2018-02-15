### NOTE that the views in views/treeviewer are mostly accessed from default.py, not here
### This allows URLs like onezoom.org/life/ rather than onezoom.org/treeviewer/life/
### but still allows us to place all the tree viewer code in a single directory

def UI_layer():
    """
    We require any UI to provide the main html code for the UI in a separate page, viewer_UI,
    so the whole skin can be reloaded using a different language, e.g. if we switch to french
    """
    response.view = "treeviewer" + "/" + request.function + "." + request.extension
    tabs=[{'id':'wiki',   'name':T('Wikipedia'),            'icon':URL('static','images/W.svg')},
      {'id':'eol',    'name':T('Encyclopedia of Life'), 'icon':URL('static','images/EoL.png')},
      {'id':'iucn',   'name':T('Conservation'),         'icon':URL('static','images/IUCN_Red_List.svg')},
      {'id':'ncbi',   'name':T('Genetics'),             'icon':URL('static','images/DNA_icon.svg')},
      #{'id':'powo',   'name':T('Kew')},
      {'id':'ozspons','name':T('Sponsor'), 'icon':URL('static','images/sponsor.png')}]
    if 'tabs' in request.vars:
        #if tabs specified, then whittle down to the specified tags
        if not isinstance(request.vars.tabs, list):
            requested_tabs=set([request.vars.tabs])
        else:
            requested_tabs=set(request.vars.tabs)
        tabs = [t for t in tabs if (t['id'] in requested_tabs) or ('all' in requested_tabs)]

    return dict(browser_language=language((request.env.http_accept_language or 'en').split(',')[0].split("-")[0]), tabs=tabs)


def treetours():
    """
    The page that summarises tours.
    If the tours are stored in another app, we can access this
    using `exec_environment` (http://web2py.com/books/default/chapter/29/04/the-core#Execution-environment) 
    """
    response.view = "treeviewer" + "/" + request.function + "." + request.extension
    if len(request.args):
        # Redirect e.g. /tours/LinnSoc1 to /life/tours/LinnSoc1
        #  so that we use the default view for the tour
        if request.args[0] in ['LinnSoc1']:
            default_viewer = "life"
            default_start_loc = None
            redirect(URL(default_viewer,args=['tour',request.args[0]] + ([default_start_loc] if default_start_loc else []),
                vars=request.vars, url_encode=False))
    else:
        return dict() #should probably return a list of tours

def treetour():
    """
    A demo version: should probably be a function in the default controller of a different app
    """
    return dict()
 
def tourstop():
    """
    A single stop on the tour
    Demo only, for the moment
    Should be called with vars: tour_name and tour_stop_index, from which we can reconstruct
    the next stop on this tour as well as the next stops on other tours
    
    
    commas and double-quotes should be disallowed in tourname_abbreviations
    
    This should probably be a function in the controller of a different TreeTours app, in which
    case we would not have access to db.ordered_leaves and db.ordered_nodes, and would need to
    map otts using an API call (e.g. otts2id) instead
    """
    tourname = request.vars.tourname or ""
    stopnum = int(request.vars.stopnum or 0)
    tourstop = db((db.tourorders.identifier == tourname) & (db.tourorders.stop_number == stopnum)).select(db.tourstops.ALL, join=db.tourstops.on(db.tourorders.stop_id==db.tourstops.id)).first()
    
    if not tourstop:
        return dict(error="No tour")
    print(tourstop.id)
    #find other tours which cover this point - might want to order here by rating or alphabetical name
    tourstops = db(db.tourorders.stop_id == tourstop.id).select(db.tourorders.ALL, db.tours.ALL, join=db.tours.on(db.tourorders.identifier==db.tours.identifier))
    #find maximum number of stops for each tour, so we know if there is a next
    max = db.tourorders.stop_number.max()
    tourlengths = {r.tourorders.identifier:r[max] for r in db(db.tourorders.identifier.belongs([t.tours.identifier for t in tourstops])).select(db.tourorders.identifier, max, groupby=db.tourorders.identifier)}
    next_array = []
    for s in tourstops:
        if s.tourorders.stop_number < tourlengths[s.tourorders.identifier]:
            next_num = s.tourorders.stop_number+1
            next_array.append({
                'tourabbrev':s.tours.identifier, 
                'tourname':s.tours.name,
                'index': next_num,
                'ott':db((db.tourorders.identifier==s.tours.identifier) & (db.tourorders.stop_number==next_num)).select(db.tourstops.ott, join=db.tourstops.on(db.tourorders.stop_id == db.tourstops.id)).first(),
                'transition':db.tourorders.transition})
    back = {''}
    for n in next_array:
        #lookup what the next OTTs refer to in OneZoom IDs
        if n['ott']:
            row = db(db.ordered_leaves.ott == n['ott'].ott).select(db.ordered_leaves.id).first()
            if row:
                n['id']=-row.id
            else:
                row = db(db.ordered_nodes.ott == n['ott'].ott).select(db.ordered_nodes.id).first()
                if row:
                    n['id']=row.id


    #lookup the single previous OTT, and then what it refers to (as a OneZoom ID)
    prev_id = None
    if stopnum>0:
        prev = db((db.tourorders.identifier==s.tours.identifier) & (db.tourorders.stop_number==(stopnum-1))).select(db.tourstops.ott, join=db.tourstops.on(db.tourorders.stop_id==db.tourstops.id)).first()
        if prev:
            row = db(db.ordered_leaves.ott == prev.ott).select(db.ordered_leaves.id).first()
            if row:
                prev_id=-row.id
            else:
                row = db(db.ordered_nodes.ott == prev.ott).select(db.ordered_nodes.id).first()
                if row:
                    prev_id=row.id
    else:
        prev_id=None

            
    return dict(
        stopnum = stopnum,
        tourname = tourname,
        tour_text = tourstop.description,
        tour_vid = tourstop.video,
        next = next_array,
        prev_id = prev_id,
    )