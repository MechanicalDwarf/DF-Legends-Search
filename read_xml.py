import xml.etree.ElementTree as ET
import sqlite3
import os

import settings


def read_xml(fpath):
    tree = ET.parse(fpath)
    return tree


# any field named 'id' is considered the primary key
def new_table(con, name, fields, types):
    if len(fields) != len(types):
        raise Exception('fields parameter has length {flen}, but types parameter has length {tlen}.'
                        .format(flen=len(fields), tlen=len(types)))
    elif len(fields) == 0:
        raise Exception('Table must have at least one field.')
    query_str = 'create table {name} (\n'.format(name=name)
    for i in range(len(fields)):
        query_str += '{field} {type}'.format(field=fields[i], type=types[i])
        if fields[i].lower() == 'id':
            query_str += ' PRIMARY KEY'
        if i < len(fields) - 1:
            query_str += ',\n'
        else:
            query_str += '\n'
    query_str += ')'
    cur = con.cursor()
    cur.execute(query_str)
    con.commit()


def create_db(dbname):
    dbpath = dbname.lower().strip() + '.db'
    if os.path.exists(dbpath):
        #raise Exception('Database already exists: {dbpath}'.format(dbpath=dbpath))
        os.remove(dbpath)
    con = sqlite3.connect(dbpath)
    new_table(con, 'regions',
            ['id', 'name', 'type'],
            ['integer', 'text', 'text']
    )
    new_table(con, 'sites',
            ['id', 'name', 'type', 'coords', 'rectangle'],
            ['integer', 'text', 'text', 'text', 'text']
    )
    new_table(con, 'artifacts',
            ['id', 'name', 'item', 'site_id', 'holder_hfid'],
            ['integer', 'text', 'text', 'integer', 'integer']
    )
    new_table(con, 'historical_figures',
            ['id', 'name', 'race', 'caste', 'appeared', 'birth_year', 'death_year'],
            ['integer', 'text', 'text', 'text', 'integer', 'integer', 'integer']
    )
    new_table(con, 'hf_to_hf_links',
            ['hfid', 'link_type', 'target_hfid'],
            ['integer', 'text', 'integer']
    )
    new_table(con, 'hf_to_site_links',
            ['hfid', 'link_type', 'site_id'],
            ['integer', 'text', 'integer']
    )
    new_table(con, 'hf_to_entity_links',
            ['hfid', 'link_type', 'entity_id'],
            ['integer', 'text', 'integer']
    )
    new_table(con, 'hf_skills',
            ['hfid', 'skill', 'total_ip'],
            ['integer', 'text', 'integer']
    )
    new_table(con, 'entity_populations',
            ['id'],
            ['integer']
    )
    new_table(con, 'entities',
            ['id', 'name'],
            ['integer', 'text']
    )
    new_table(con, 'historical_events',
            ['id', 'year', 'seconds72', 'type', 'hfid', 'state', 'site_id', 'coords', 'knowledge', 'artifact_id', 'civ_id', 'entity_id', 'attacker_civ_id', 'defender_civ_id', 'attacker_general_hfid', 'defender_general_hfid', 'slayer_hfid'],
            ['integer', 'integer', 'integer', 'text', 'integer', 'text', 'integer', 'text', 'text', 'integer', 'integer', 'integer', 'integer', 'integer', 'integer', 'integer', 'integer']
    )
    new_table(con, 'historical_event_collections',
            ['id', 'start_year', 'start_seconds72', 'end_year', 'end_seconds72', 'type', 'site_id'],
            ['integer', 'integer', 'integer', 'integer', 'integer', 'text', 'integer']
    )
    new_table(con, 'historical_eras',
            ['name', 'start_year'],
            ['text', 'integer']
    )
    new_table(con, 'written_contents',
            ['id', 'title', 'author_hfid', 'author_roll', 'form', 'form_id'],
            ['integer', 'text', 'integer', 'integer', 'text', 'integer']
    )
    new_table(con, 'poetic_forms',
            ['id', 'description'],
            ['integer', 'text']
    )
    new_table(con, 'musical_forms',
            ['id', 'description'],
            ['integer', 'text']
    )
    new_table(con, 'dance_forms',
            ['id', 'description'],
            ['integer', 'text']
    )
    return con

def do_insert(con, table_name, fields, values):
    if len(fields) != len(values):
        raise Exception('fields parameter has length {flen}, but values parameter has length {vlen}'
                        .format(flen=len(fields), vlen=len(values)))
    elif len(fields) == 0:
        raise Exception('Must have at least one field.')
    query_txt = f'insert into {table_name} ('
    for field in fields:
        query_txt += field + ','
    query_txt = query_txt[:-1] + ')\nvalues ('
    for value in values:
        query_txt += f'"{value}",'
    query_txt = query_txt[:-1] + ')'
    cur = con.cursor()
    cur.execute(query_txt)
    #con.commit()

def load_sites(tree, con):
    root = tree.getroot()
    sites_elem = None
    for child in root:
        if child.tag == 'sites':
            sites_elem = child
            break
    if sites_elem is None:
        raise Exception('<sites> element not found.')
    for site_elem in sites_elem:
        site_id = None
        site_name = ''
        site_type = ''
        site_coords = ''
        rectangle = ''
        for detail in site_elem:
            if detail.tag == 'id':
                site_id = detail.text
            elif detail.tag == 'name':
                site_name = detail.text
            elif detail.tag == 'type':
                site_type = detail.text
            elif detail.tag == 'coords':
                site_coords = detail.text
            elif detail.tag == 'rectangle':
                rectangle = detail.text
        do_insert(con, 'sites',
            ['id', 'name', 'type', 'coords', 'rectangle'],
            [site_id, site_name, site_type, site_coords, rectangle]
        )

def load_histfigs(tree, con):
    root = tree.getroot()
    histfigs_elem = None
    for child in root:
        if child.tag == 'historical_figures':
            histfigs_elem = child
            break
    if histfigs_elem is None:
        raise Exception('<historical_figures> element not found.')
    for histfig_elem in histfigs_elem:
        hfid = None
        name = ''
        race = ''
        caste = ''
        appeared = '-1'
        birth_year = '-1'
        death_year = '-1'
        hf_links = []
        site_links = []
        entity_links = []
        skills = []
        for detail in histfig_elem:
            if detail.tag == 'id':
                hfid = detail.text
            elif detail.tag == 'name':
                name = detail.text
            elif detail.tag == 'race':
                race = detail.text
            elif detail.tag == 'caste':
                caste = detail.text
            elif detail.tag == 'appeared':
                appeared = detail.text
            elif detail.tag == 'birth_year':
                birth_year = detail.text
            elif detail.tag == 'death_year':
                death_year = detail.text
            elif detail.tag == 'hf_link':
                link_type = ''
                target_hfid = ''
                for subdetail in detail:
                    if subdetail.tag == 'link_type':
                        link_type = subdetail.text
                    elif subdetail.tag == 'hfid':
                        target_hfid = subdetail.text
                hf_links.append({
                    'link_type': link_type,
                    'target_hfid': target_hfid
                })
            elif detail.tag == 'site_link':
                link_type = ''
                site_id = ''
                for subdetail in detail:
                    if subdetail.tag == 'link_type':
                        link_type = subdetail.text
                    elif subdetail.tag == 'site_id':
                        site_id = subdetail.text
                site_links.append({
                    'link_type': link_type,
                    'site_id': site_id
                })
            elif detail.tag == 'entity_link':
                link_type = ''
                entity_id = ''
                for subdetail in detail:
                    if subdetail.tag == 'link_type':
                        link_type = subdetail.text
                    elif subdetail.tag == 'entity_id':
                        entity_id = subdetail.text
                entity_links.append({
                    'link_type': link_type,
                    'entity_id': entity_id
                })
            elif detail.tag == 'hf_skill':
                skill = ''
                total_ip = '-1'
                for subdetail in detail:
                    if subdetail.tag == 'skill':
                        skill = subdetail.text
                    elif subdetail.tag == 'total_ip':
                        total_ip = subdetail.text
                skills.append({
                    'skill': skill,
                    'total_ip': total_ip
                })
        do_insert(con, 'historical_figures',
            ['id', 'name', 'race', 'caste', 'appeared', 'birth_year', 'death_year'],
            [hfid, name, race, caste, appeared, birth_year, death_year]
        )
        for hf_link in hf_links:
            do_insert(con, 'hf_to_hf_links',
                ['hfid', 'link_type', 'target_hfid'],
                [hfid, hf_link['link_type'], hf_link['target_hfid']]
            )
        for site_link in site_links:
            do_insert(con, 'hf_to_site_links',
                ['hfid', 'link_type', 'site_id'],
                [hfid, site_link['link_type'], site_link['site_id']]
            )
        for entity_link in entity_links:
            do_insert(con, 'hf_to_entity_links',
                ['hfid', 'link_type', 'entity_id'],
                [hfid, entity_link['link_type'], entity_link['entity_id']]
            )
        for skill in skills:
            do_insert(con, 'hf_skills',
                ['hfid', 'skill', 'total_ip'],
                [hfid, skill['skill'], skill['total_ip']]
            )

def load_artifacts(tree, con):
    root = tree.getroot()
    artifacts_elem = None
    for child in root:
        if child.tag == 'artifacts':
            artifacts_elem = child
            break
    if artifacts_elem is None:
        raise Exception('<artifacts> element not found.')
    for artifact_elem in artifacts_elem:
        art_id = None
        name = ''
        item = ''
        site_id = '-1'
        holder_hfid = '-1'
        for detail in artifact_elem:
            if detail.tag == 'id':
                art_id = detail.text
            elif detail.tag == 'name':
                name = detail.text
            elif detail.tag == 'item':
                item = detail.text
            elif detail.tag == 'site_id':
                site_id = detail.text
            elif detail.tag == 'holder_hfid':
                holder_hfid = detail.text
        do_insert(con, 'artifacts',
            ['id', 'name', 'item', 'site_id', 'holder_hfid'],
            [art_id, name, item, site_id, holder_hfid]
        )

def load_written_contents(tree, con):
    root = tree.getroot()
    written_contents_elem = None
    for child in root:
        if child.tag == 'written_contents':
            written_contents_elem = child
            break
    if written_contents_elem is None:
        raise Exception('<written_contents> element not found.')
    for written_content_elem in written_contents_elem:
        writ_id = None
        title = ''
        author_hfid = '-1'
        author_roll = '-1'
        form = ''
        form_id = '-1'
        for detail in written_content_elem:
            if detail.tag == 'id':
                writ_id = detail.text
            elif detail.tag == 'title':
                title = detail.text
            elif detail.tag == 'author_hfid':
                author_hfid = detail.text
            elif detail.tag == 'author_roll':
                author_roll = detail.text
            elif detail.tag == 'form':
                form = detail.text
            elif detail.tag == 'form_id':
                form_id = detail.text
        do_insert(con, 'written_contents',
            ['id', 'title', 'author_hfid', 'author_roll', 'form', 'form_id'],
            [writ_id, title, author_hfid, author_roll, form, form_id]
        )

def load_entities(tree, con):
    root = tree.getroot()
    entities_elem = None
    for child in root:
        if child.tag == 'entities':
            entities_elem = child
            break
    if entities_elem is None:
        raise Exception('<entities> element not found.')
    for entity_elem in entities_elem:
        ent_id = None
        name = ''
        for detail in entity_elem:
            if detail.tag == 'id':
                ent_id = detail.text
            elif detail.tag == 'name':
                name = detail.text
        do_insert(con, 'entities',
            ['id', 'name'],
            [ent_id, name]
        )

def load_historical_events(tree, con):
    root = tree.getroot()
    historical_events_elem = None
    for child in root:
        if child.tag == 'historical_events':
            historical_events_elem = child
            break
    if historical_events_elem is None:
        raise Exception('<historical_events> element not found.')
    for historical_event_elem in historical_events_elem:
        evt_id = None
        year = '-1'
        seconds72 = '-1'
        evt_type = ''
        hfid = '-1'
        state = ''
        site_id = '-1'
        coords = ''
        knowledge = ''
        artifact_id = '-1'
        civ_id = '-1'
        entity_id = '-1'
        attacker_civ_id = '-1'
        defender_civ_id = '-1'
        attacker_general_hfid = '-1'
        defender_general_hfid = '-1'
        slayer_hfid = '-1'
        for detail in historical_event_elem:
            if detail.tag == 'id':
                evt_id = detail.text
            elif detail.tag == 'year':
                year = detail.text
            elif detail.tag == 'seconds72':
                seconds72 = detail.text
            elif detail.tag == 'type':
                evt_type = detail.text
            elif detail.tag == 'hfid':
                hfid = detail.text
            elif detail.tag == 'state':
                state = detail.text
            elif detail.tag == 'site_id':
                site_id = detail.text
            elif detail.tag == 'coords':
                coords = detail.text
            elif detail.tag == 'knowledge':
                knowledge = detail.text
            elif detail.tag == 'artifact_id':
                artifact_id = detail.text
            elif detail.tag == 'civ_id':
                civ_id = detail.text
            elif detail.tag == 'entity_id':
                entity_id = detail.text
            elif detail.tag == 'attacker_civ_id':
                attacker_civ_id = detail.text
            elif detail.tag == 'defender_civ_id':
                defender_civ_id = detail.text
            elif detail.tag == 'attacker_general_hfid':
                attacker_general_hfid = detail.text
            elif detail.tag == 'defender_general_hfid':
                defender_general_hfid = detail.text
            elif detail.tag == 'slayer_hfid':
                slayer_hfid = detail.text
        do_insert(con, 'historical_events',
            ['id', 'year', 'seconds72', 'type', 'hfid', 'state', 'site_id', 'coords', 'knowledge', 'artifact_id', 'civ_id', 'entity_id', 'attacker_civ_id', 'defender_civ_id', 'attacker_general_hfid', 'defender_general_hfid', 'slayer_hfid'],
            [evt_id, year, seconds72, evt_type, hfid, state, site_id, coords, knowledge, artifact_id, civ_id, entity_id, attacker_civ_id, defender_civ_id, attacker_general_hfid, defender_general_hfid, slayer_hfid]
        )

def load_all(fpath, dbname=None):
    if dbname is None:
        dbname = os.path.basename(fpath).split('.')[0]
    tree = read_xml(fpath)
    print('Read XML file.')
    con = create_db(dbname)
    load_sites(tree, con)
    print('Sites loaded.')
    load_histfigs(tree, con)
    print('Historical figures loaded.')
    load_artifacts(tree, con)
    print('Artifacts loaded.')
    load_written_contents(tree, con)
    print('Written contents loaded.')
    load_entities(tree, con)
    print('Entities loaded.')
    load_historical_events(tree, con)
    print('Historical events loaded.')

    con.commit()
    print('Done.')

#load_all(settings.get_setting('xml_path'), settings.get_setting('db_name'))