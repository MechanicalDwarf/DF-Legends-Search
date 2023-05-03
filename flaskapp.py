import os.path

from flask import Flask, render_template, request, redirect
import math

import settings
from db_util import search_sites, get_site_details, get_histfig_details, search_histfigs, search_artifacts, \
    get_artifact_details, get_event_details
from read_xml import load_all

app = Flask(__name__)

@app.route('/')
def index():
    xml_path = settings.get_setting('xml_path')
    xml_exists = False
    db_exists = False
    if xml_path != '':
        xml_exists = os.path.exists(xml_path)
        db_exists = os.path.exists(settings.get_setting('db_name') + '.db')
    return render_template('index.html', xml_path=xml_path, xml_exists=xml_exists, db_exists=db_exists)


@app.route('/set_xml_path', methods=['POST'])
def set_xml_path():
    xml_path = request.form.get('xml_path')
    settings.set_setting('xml_path', xml_path)
    db_name = os.path.basename(xml_path).split('.')[0]
    settings.set_setting('db_name', db_name)
    return redirect('/')


@app.route('/read_xml', methods=['POST'])
def read_xml():
    xml_path = settings.get_setting('xml_path')
    db_name = settings.get_setting('db_name')
    load_all(xml_path, dbname=db_name)
    return redirect('/')


@app.route('/search_sites')
def results_sites():
    search_text = request.args.get('search_text').lower().strip()
    site_type = request.args.get('site_type').lower().strip()
    if len(site_type) == 0 or site_type == 'none':
        site_type = None
    page_num = request.args.get('page')
    if not str(page_num).isdigit():
        page_num = 1
    else:
        page_num = int(page_num)
    matches, total_count = search_sites(search_text, site_type=site_type, page_num=page_num)
    first_count = 50 * (page_num-1) + 1
    if len(matches) == 0:
        first_count = 0
    page_range = (first_count, first_count + len(matches) - 1)
    page_count = int(math.ceil(total_count / 50.))
    return render_template('search_result_sites.html', search_text=search_text, site_type=site_type, results=matches, page_num=page_num, total_result_count=total_count, page_range=page_range, page_count=page_count)

@app.route('/search_histfigs')
def results_histfigs():
    search_text = request.args.get('search_text').lower().strip()
    page_num = request.args.get('page')
    if not str(page_num).isdigit():
        page_num = 1
    else:
        page_num = int(page_num)
    matches, total_count = search_histfigs(search_text, page_num=page_num)
    first_count = 50 * (page_num-1) + 1
    if len(matches) == 0:
        first_count = 0
    page_range = (first_count, first_count + len(matches) - 1)
    page_count = int(math.ceil(total_count / 50.))
    return render_template('search_result_histfigs.html', search_text=search_text, results=matches, page_num=page_num, total_result_count=total_count, page_range=page_range, page_count=page_count)

@app.route('/search_artifacts')
def results_artifacts():
    search_text = request.args.get('search_text').lower().strip()
    page_num = request.args.get('page')
    if not str(page_num).isdigit():
        page_num = 1
    else:
        page_num = int(page_num)
    matches, total_count = search_artifacts(search_text, page_num=page_num)
    first_count = 50 * (page_num-1) + 1
    if len(matches) == 0:
        first_count = 0
    page_range = (first_count, first_count + len(matches) - 1)
    page_count = int(math.ceil(total_count / 50.))
    return render_template('search_result_artifacts.html', search_text=search_text, results=matches, page_num=page_num, total_result_count=total_count, page_range=page_range, page_count=page_count)

@app.route('/site')
def site_details():
    site_id = request.args.get('id')
    site = get_site_details(site_id)
    return render_template('site.html', site=site)

@app.route('/histfig')
def histfig_details():
    histfig_id = request.args.get('id')
    histfig = get_histfig_details(histfig_id)
    return render_template('histfig.html', histfig=histfig)

@app.route('/artifact')
def artifact_details():
    artifact_id = request.args.get('id')
    artifact = get_artifact_details(artifact_id)
    return render_template('artifact.html', artifact=artifact)

@app.route('/event')
def event_details():
    event_id = request.args.get('id')
    event = get_event_details(event_id)
    return render_template('event.html', event=event)


app.run(port=5000, debug=True)
