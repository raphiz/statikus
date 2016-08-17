from statikus import Statikus, render_page, raw_page
import json
import os

# Temporary workaround..
os.chdir('example/')


db = {'people': [{'name': 'Jack Jackson'}, {'name': 'Peter Peterson'}]}
app = Statikus(db=db, some_parameter='...')
# app.add_asset_handler('scripts', js_minify)
app.add_asset('scripts', ['script1.foo', 'script2.foo'])
app.add_asset('scripts', 'scripts/*.js')
# TODO: This should not add static!
app.add_asset('static', ['static/**'])
app.add_asset('stylesheets', 'styles/*.css')

# @app.requires('scripts', ['foo.js', 'baa'])
@app.requires_asset('scripts', 'scripts/foo.js')
@app.requires_asset('scripts', 'scripts/baa.js')
@app.route('people/')
def people_index(db, some_parameter):
    return {'people': [person['name'] for person in db['people']]}
    # implicit = render_page(dict{})


@app.route('/')
def index():
    return render_page({})


@app.route('people/<name>')
def people_list(db):
    for person in db['people']:
        yield render_page({'person': person}, name=person['name'].replace(' ', '_'))


@app.route('api/people/<name>.json')
def people_raw_data(db):
    for person in db['people']:
        yield raw_page(json.dumps({'person': person, }), name=person['name'].replace(' ', '_'))


if __name__ == '__main__':
    app.run(serve=True)
