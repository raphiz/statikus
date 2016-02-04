from statikus import Statikus

db = {'people': [{'name': 'Jack Jackson'}, {'name': 'Peter Peterson'}]}

app = Statikus(db=db, some_parameter='...')


# @app.requires('scripts', ['foo.js', 'baa'])
@app.requires_asset('scripts', 'scripts/foo.js')
@app.requires_asset('scripts', 'scripts/baa.js')
@app.route('people/')
def people_list(db, some_parameter):
    print(some_parameter)
    return {'people': [person['name'] for person in db['people']]}
    # implicit = render_page(dict{})


@app.route('people/<name>')
def people_list(db):
    for person in db['people']:
        yield render_page(name=person['name'], {'person': person})


@app.route('api/people/<name>.json')
def people_raw_data(db):
    for person in db['people']:
        yield raw_page(name=person['name'], json.dumps({'person': person}))


# TODO:url_for method - see http://flask.pocoo.org/docs/0.10/quickstart/
# TODO: return redirect(url_for('login'))
# Return render_page(url='specific', {attrs})
# Return render_page(name='x', vorname='y', {render_opts:...})
if __name__ == '__main__':
    app.run()
