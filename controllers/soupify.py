# Our Data Structures
our_data=[]
# Our constants, rather than reload them each call
from BeautifulSoup import BeautifulSoup

def index():
    rows=db(db.recipe)
    sort_by=None
    inverse=False
    search_string=""

    if sort_by:
        if inverse==False:
            orderby=db.recipe[sort_by]
        else:
            orderby=~db.recipe[sort_by]
    else:
        orderby='<random>'

    form=FORM('Search',
            INPUT(_name='search_for'),INPUT(_type='submit')
            )
    if form.process().accepted:
        search_string=form.vars.search_for
        response.flash="Searching for {}".format(search_string)
    elif request.vars.has_key('search_string'):
        search_string=request.vars.search_string
    if len(search_string)>0:
        rows=rows(db.recipe.recipe_title.contains(search_string))

    # Final select
    rows=rows.select( orderby=orderby, limitby=(0,100))
    return dict(form=form,rows=rows, search_params=search_string)




def redo_db():
    response.view='generic.html'
    form=SQLFORM.factory(
            Field('confirm', 'boolean'),
            )
    msg=H1("This will remove all the records from the database. ARE YOU SURE???")
    if form.process().accepted:
        if form.vars.confirm==True:
            db.recipe.truncate()
            db.commit()
            session.flash="DB Truncated!"
            redirect('index.html')
        else:
            msg="You chickened out! Good for you!"
    return dict(form=form, msg=msg)

def parse():
    response.view='generic.html'
    import os,sys
    # Step 1:
    # walk the system to find all the recipes
    from os.path import join, getsize
    # Step 2:
    # parse index.html and extract all useful info
    # start here.
    for root, dirs, files in os.walk(join(request.folder,'www.bbc.co.uk','food','recipes')):
        for name in files:
            if name.split('.')[-1]=='html':
                #print("Parsing {}".format(join(root.split()[-1],name)))
                data=parse_html(join(root,name))
                if len(data['method_list'])>0:
                    try:
                        db.recipe.insert(
                            recipe_title=data['recipe_title'],
                            recipe_description=data['recipe_description'],
                            recipe_author=data['recipe_author'],
                            recipe_ingredients=data['recipe_ingredients'],
                            method_list=data['method_list'],
                            cooking_time=data['cooking_time'],
                            recipe_serves=data['recipe_serves'],
                        )
                    except:
                        print "Couldn't insert:",data
        db.commit()
    rows=db(db.recipe).select(limitby=(0,1), orderby=~db.recipe.id)
    return dict( rows=rows)


    #print sum(getsize(join(root, name)) for name in files),
    #print "bytes in", len(files), "non-directory files"
    #if 'CVS' in dirs:
    #    dirs.remove('CVS')  # don't visit CVS directories
def parse_html(inFile):
    description={
            'recipe_serves':      ['p','recipe-metadata__serving'],
            'recipe_description':  ['p','recipe-description__text'],
            'recipe_ingredients':  ['li','recipe-ingredients__list-item'],
            'method_list':       ['p','recipe-method__list-item-text'],
            'cooking_time': ['p','recipe-metadata__cook-time'],
            'recipe_author':       ['p','recipe-is-from-widget__programme-series-title'],
            'recipe_title':        ['h1','content-title__text'],
            }
    retval={}
    soup=BeautifulSoup(open(inFile))
    for k,v in description.items():
        spy=soup.findAll(v[0],v[1])
        parrot=getContents(spy)
        retval[k]=parrot
    return retval

def getContents(inL):
    output=[]
    for a in inL:
        st=""
        for b in a.contents:
            if str(type(b))=="<class 'BeautifulSoup.Tag'>":
                st=u"{} {}".format(st, unicode(b.text))
            else:
                st=u"{} {}".format(st, unicode(b))
        output.append(st)
    return output


# Step 3:
# ???
# Step 4:
# profit

