from statikus import Statikus, render_page, raw_page
import json

db = {'people': [{'name': 'Jack Jackson'}, {'name': 'Peter Peterson'}]}

app = Statikus(db=db, some_parameter='...')


# @app.requires('scripts', ['foo.js', 'baa'])
@app.requires_asset('scripts', 'scripts/foo.js')
@app.requires_asset('scripts', 'scripts/baa.js')
@app.route('people/')
def people_index(db, some_parameter):
    return {'people': [person['name'] for person in db['people']]}
    # implicit = render_page(dict{})


@app.route('people/<name>')
def people_list(db):
    for person in db['people']:
        yield render_page({'person': person}, name=person['name'].replace(' ', '_'))


@app.route('api/people/<name>.json')
def people_raw_data(db):
    for person in db['people']:
        yield raw_page(json.dumps({'person': person, }), name=person['name'].replace(' ', '_'))


# TODO:url_for method - see http://flask.pocoo.org/docs/0.10/quickstart/
# TODO: return redirect(url_for('login'))
# Return render_page(url='specific', {attrs})
# Return render_page(name='x', vorname='y', {render_opts:...})
if __name__ == '__main__':
    app.run()
