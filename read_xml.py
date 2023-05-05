import xml.etree.ElementTree as ET
import sqlite3
import os

import settings


def read_xml(fpath):
    tree = ET.parse(fpath)
    return tree

def add_unmatched_tags(new_tags):
    old_tags = []
    if os.path.exists('unmatched_tags.txt'):
        fh = open('unmatched_tags.txt')
        old_tags = fh.read().strip().split('\n')
        fh.close()
    new_tags = list(set(new_tags))
    tags = old_tags + list(filter(lambda x: not x in old_tags, new_tags))
    fh = open('unmatched_tags.txt', 'w')
    fh.write('\n'.join(tags))
    fh.close()

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
    new_table(con, 'site_structures',
            ['site_id', 'local_id', 'type', 'name'],
            ['integer', 'integer', 'text', 'text']
    )
    new_table(con, 'site_properties',
            ['site_id', 'local_id', 'type', 'owner_hfid'],
            ['integer', 'integer', 'text', 'integer']
    )
    new_table(con, 'artifacts',
            ['id', 'name', 'site_id', 'holder_hfid', 'written_content_id'],
            ['integer', 'text', 'integer', 'integer', 'integer']
    )
    new_table(con, 'historical_figures',
            ['id', 'name', 'race', 'caste', 'appeared', 'birth_year', 'death_year', 'current_identity_id', 'animated_string', 'death_seconds72', 'active_interaction', 'is_animated', 'is_force', 'ent_pop_id', 'associated_type', 'is_deity', 'birth_seconds72', 'is_ghost'],
            ['integer', 'text', 'text', 'text', 'integer', 'integer', 'integer', 'integer', 'text', 'integer', 'text', 'integer', 'integer', 'integer', 'text', 'integer', 'integer', 'integer']
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
    new_table(con, 'hf_goals',
            ['hfid', 'goal'],
            ['integer', 'text']
    )
    new_table(con, 'hf_honor_entities',
            ['hfid', 'entity_id', 'battles', 'kills', 'honor_id'],
            ['integer', 'integer', 'integer', 'integer', 'integer']
    )
    new_table(con, 'hf_interaction_knowledge',
            ['hfid', 'interaction_knowledge'],
            ['integer', 'text']
    )
    new_table(con, 'hf_used_identity_ids',
            ['hfid', 'identity_id'],
            ['integer', 'integer']
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
            ['id', 'year', 'seconds72', 'type', 'hfid', 'state', 'site_id', 'coords', 'knowledge', 'artifact_id', 'civ_id', 'entity_id', 'attacker_civ_id', 'defender_civ_id', 'attacker_general_hfid', 'defender_general_hfid', 'slayer_hfid', 'cause', 'source_site_id', 'group_1_hfid', 'group_2_hfid', 'a_leader_hfid', 'd_leader_hfid', 'reason', 'entity_id_1', 'entity_id_2', 'leader_hfid', 'site_id_1', 'site_id_2', 'link', 'corruptor_hfid', 'corruptor_identity', 'result', 'circumstance', 'topic', 'trickster_hfid', 'identity_id', 'dest_site_id', ],
            ['integer', 'integer', 'integer', 'text', 'integer', 'text', 'integer', 'text', 'text', 'integer', 'integer', 'integer', 'integer', 'integer', 'integer', 'integer', 'integer', 'text', 'integer', 'integer', 'integer', 'integer', 'integer', 'text', 'integer', 'integer', 'integer', 'integer', 'integer', 'text', 'integer', 'integer', 'integer', 'text', 'text', 'integer', 'integer', 'integer',]
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
    unmatched_tags = []
    for site_elem in sites_elem:
        site_id = None
        site_name = ''
        site_type = ''
        site_coords = ''
        rectangle = ''
        structures = []
        properties = []
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
            elif detail.tag == 'structures':
                local_id = '-1'
                struct_type = ''
                struct_name = ''
                for subdetail in detail:
                    if subdetail.tag == 'local_id':
                        local_id = subdetail.text
                    elif subdetail.tag == 'type':
                        struct_type = subdetail.text
                    elif subdetail.tag == 'name':
                        struct_name = subdetail.text
                structures.append({
                    'local_id': local_id,
                    'type': struct_type,
                    'name': struct_name
                })
            elif detail.tag == 'properties':
                local_id = '-1'
                prop_type = ''
                owner_hfid = '-1'
                for subdetail in detail:
                    if subdetail.tag == 'id':
                        local_id = subdetail.text
                    elif subdetail.tag == 'type':
                        prop_type = subdetail.text
                    elif subdetail.tag == 'owner_hfid':
                        owner_hfid = subdetail.text
                structures.append({
                    'local_id': local_id,
                    'type': prop_type,
                    'owner_hfid': owner_hfid
                })
            else:
                unmatched_tags.append('site - '+detail.tag)
        do_insert(con, 'sites',
            ['id', 'name', 'type', 'coords', 'rectangle'],
            [site_id, site_name, site_type, site_coords, rectangle]
        )
        for structure in structures:
            do_insert(con, 'site_structures',
                ['site_id', 'local_id', 'type', 'name'],
                [site_id, structure['local_id'], structure['type'], structure['name']]
            )
        for prop in properties:
            do_insert(con, 'site_properties',
                ['site_id', 'local_id', 'type', 'owner_hfid'],
                [site_id, prop['local_id'], prop['type'], prop['owner_hfid']]
            )
    add_unmatched_tags(unmatched_tags)

def load_histfigs(tree, con):
    root = tree.getroot()
    histfigs_elem = None
    for child in root:
        if child.tag == 'historical_figures':
            histfigs_elem = child
            break
    if histfigs_elem is None:
        raise Exception('<historical_figures> element not found.')
    unmatched_tags = []
    for histfig_elem in histfigs_elem:
        hfid = None
        name = ''
        race = ''
        caste = ''
        appeared = '-1'
        birth_year = '-1'
        death_year = '-1'
        current_identity_id = '-1'
        animated_string = ''
        death_seconds72 = '-1'
        active_interaction = ''
        is_animated = '0'
        is_force = '0'
        ent_pop_id = '-1'
        associated_type = ''
        is_deity = '0'
        birth_seconds72 = '-1'
        is_ghost = '0'
        hf_links = []
        site_links = []
        entity_links = []
        skills = []
        goals = []
        honor_entities = []
        interaction_knowledge = []
        used_identity_ids = []
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
            elif detail.tag == 'current_identity_id':
                current_identity_id = detail.text
            elif detail.tag == 'animated_string':
                animated_string = detail.text
            elif detail.tag == 'death_seconds72':
                death_seconds72 = detail.text
            elif detail.tag == 'active_interaction':
                active_interaction = detail.text
            elif detail.tag == 'animated':
                is_animated = '1'
            elif detail.tag == 'force':
                is_force = '1'
            elif detail.tag == 'ent_pop_id':
                ent_pop_id = detail.text
            elif detail.tag == 'associated_type':
                associated_type = detail.text
            elif detail.tag == 'deity':
                is_deity = '1'
            elif detail.tag == 'birth_seconds72':
                birth_seconds72 = detail.text
            elif detail.tag == 'ghost':
                is_ghost = '1'
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
            elif detail.tag == 'goal':
                goals.append(detail.text)
            elif detail.tag == 'honor_entity':
                entity_id = '-1'
                battles = '0'
                kills = '0'
                honor_id = '-1'
                for subdetail in detail:
                    if subdetail.tag == 'entity':
                        entity = subdetail.text
                    elif subdetail.tag == 'battles':
                        battles = subdetail.text
                    elif subdetail.tag == 'kills':
                        kills = subdetail.text
                    elif subdetail.tag == 'honor_id':
                        honor_id = subdetail.text
                honor_entities.append({
                    'entity_id': entity_id,
                    'battles': battles,
                    'kills': kills,
                    'honor_id': honor_id,
                })
            elif detail.tag == 'interaction_knowledge':
                interaction_knowledge.append(
                    detail.text
                )
            elif detail.tag == 'used_identity_id':
                used_identity_ids.append(
                    detail.text
                )
            else:
                unmatched_tags.append('histfig - '+detail.tag)
        do_insert(con, 'historical_figures',
            ['id', 'name', 'race', 'caste', 'appeared', 'birth_year', 'death_year', 'current_identity_id', 'animated_string', 'death_seconds72', 'active_interaction', 'is_animated', 'is_force', 'ent_pop_id', 'associated_type', 'is_deity', 'birth_seconds72', 'is_ghost'],
            [hfid, name, race, caste, appeared, birth_year, death_year, current_identity_id, animated_string, death_seconds72, active_interaction, is_animated, is_force, ent_pop_id, associated_type, is_deity, birth_seconds72, is_ghost]
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
        for goal in goals:
            do_insert(con, 'hf_goals',
                ['hfid', 'goal'],
                [hfid, goal]
            )
        for honor_entity in honor_entities:
            do_insert(con, 'hf_honor_entities',
                ['hfid', 'entity_id', 'battles', 'kills', 'honor_id'],
                [hfid, honor_entity['entity_id'], honor_entity['battles'], honor_entity['kills'], honor_entity['honor_id']]
            )
        for knowledge in interaction_knowledge:
            do_insert(con, 'hf_interaction_knowledge',
                ['hfid', 'interaction_knowledge'],
                [hfid, knowledge]
            )
        for identity_id in used_identity_ids:
            do_insert(con, 'hf_used_identity_ids',
                ['hfid', 'identity_id'],
                [hfid, identity_id]
            )
    add_unmatched_tags(unmatched_tags)

def load_artifacts(tree, con):
    root = tree.getroot()
    artifacts_elem = None
    for child in root:
        if child.tag == 'artifacts':
            artifacts_elem = child
            break
    if artifacts_elem is None:
        raise Exception('<artifacts> element not found.')
    unmatched_tags = []
    for artifact_elem in artifacts_elem:
        art_id = None
        name = ''
        site_id = '-1'
        holder_hfid = '-1'
        written_content_id = '-1'
        for detail in artifact_elem:
            if detail.tag == 'id':
                art_id = detail.text
            elif detail.tag == 'name':
                name = detail.text
            elif detail.tag == 'site_id':
                site_id = detail.text
            elif detail.tag == 'holder_hfid':
                holder_hfid = detail.text
            elif detail.tag == 'item':
                for subdetail in detail:
                    if subdetail.tag == 'page_written_content_id':
                        written_content_id = subdetail.text
                    else:
                        unmatched_tags.append('artifact - item - '+subdetail.tag)
            else:
                unmatched_tags.append('artifact - '+detail.tag)
        do_insert(con, 'artifacts',
            ['id', 'name', 'site_id', 'holder_hfid', 'written_content_id'],
            [art_id, name, site_id, holder_hfid, written_content_id]
        )
    add_unmatched_tags(unmatched_tags)

def load_written_contents(tree, con):
    root = tree.getroot()
    written_contents_elem = None
    for child in root:
        if child.tag == 'written_contents':
            written_contents_elem = child
            break
    if written_contents_elem is None:
        raise Exception('<written_contents> element not found.')
    unmatched_tags = []
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
            else:
                unmatched_tags.append('written_content - '+detail.tag)
        do_insert(con, 'written_contents',
            ['id', 'title', 'author_hfid', 'author_roll', 'form', 'form_id'],
            [writ_id, title, author_hfid, author_roll, form, form_id]
        )
    add_unmatched_tags(unmatched_tags)

def load_entities(tree, con):
    root = tree.getroot()
    entities_elem = None
    for child in root:
        if child.tag == 'entities':
            entities_elem = child
            break
    if entities_elem is None:
        raise Exception('<entities> element not found.')
    unmatched_tags = []
    for entity_elem in entities_elem:
        ent_id = None
        name = ''
        for detail in entity_elem:
            if detail.tag == 'id':
                ent_id = detail.text
            elif detail.tag == 'name':
                name = detail.text
            else:
                unmatched_tags.append('entity - '+detail.tag)
        do_insert(con, 'entities',
            ['id', 'name'],
            [ent_id, name]
        )
    add_unmatched_tags(unmatched_tags)

def load_historical_events(tree, con):
    root = tree.getroot()
    historical_events_elem = None
    for child in root:
        if child.tag == 'historical_events':
            historical_events_elem = child
            break
    if historical_events_elem is None:
        raise Exception('<historical_events> element not found.')
    unmatched_tags = []
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
        cause = ''
        source_site_id = '-1'
        group_1_hfid = '-1'
        group_2_hfid = '-1'
        a_leader_hfid = '-1'
        d_leader_hfid = '-1'
        reason = ''
        entity_id_1 = '-1'
        entity_id_2 = '-1'
        leader_hfid = '-1'
        site_id_1 = '-1'
        site_id_2 = '-1'
        link = ''
        corruptor_hfid = '-1'
        corruptor_identity = '-1'
        result = ''
        circumstance = ''
        topic = ''
        trickster_hfid = '-1'
        identity_id = '-1'
        dest_site_id = '-1'
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
            elif detail.tag == 'cause':
                cause = detail.text
            elif detail.tag == 'source_site_id':
                source_site_id = detail.text
            elif detail.tag == 'group_1_hfid':
                group_1_hfid = detail.text
            elif detail.tag == 'group_2_hfid':
                group_2_hfid = detail.text
            elif detail.tag == 'a_leader_hfid':
                a_leader_hfid = detail.text
            elif detail.tag == 'd_leader_hfid':
                d_leader_hfid = detail.text
            elif detail.tag == 'reason':
                reason = detail.text
            elif detail.tag == 'entity_id_1':
                entity_id_1 = detail.text
            elif detail.tag == 'entity_id_2':
                entity_id_2 = detail.text
            elif detail.tag == 'leader_hfid':
                leader_hfid = detail.text
            elif detail.tag == 'site_id_1':
                site_id_1 = detail.text
            elif detail.tag == 'site_id_2':
                site_id_2 = detail.text
            elif detail.tag == 'link':
                link = detail.text
            elif detail.tag == 'corruptor_hfid':
                corruptor_hfid = detail.text
            elif detail.tag == 'corruptor_identity':
                corruptor_identity = detail.text
            elif detail.tag == 'result':
                result = detail.text
            elif detail.tag == 'circumstance':
                circumstance = detail.text
            elif detail.tag == 'topic':
                topic = detail.text
            elif detail.tag == 'trickster_hfid':
                trickster_hfid = detail.text
            elif detail.tag == 'identity_id':
                identity_id = detail.text
            elif detail.tag == 'dest_site_id':
                dest_site_id = detail.text
            else:
                unmatched_tags.append('historical_event - '+detail.tag)
        do_insert(con, 'historical_events',
            ['id', 'year', 'seconds72', 'type', 'hfid', 'state', 'site_id', 'coords', 'knowledge', 'artifact_id', 'civ_id', 'entity_id', 'attacker_civ_id', 'defender_civ_id', 'attacker_general_hfid', 'defender_general_hfid', 'slayer_hfid', 'cause', 'source_site_id', 'group_1_hfid', 'group_2_hfid', 'a_leader_hfid', 'd_leader_hfid', 'reason', 'entity_id_1', 'entity_id_2', 'leader_hfid', 'site_id_1', 'site_id_2', 'link', 'corruptor_hfid', 'corruptor_identity', 'result', 'circumstance', 'topic', 'trickster_hfid', 'identity_id', 'dest_site_id', ],
            [evt_id, year, seconds72, evt_type, hfid, state, site_id, coords, knowledge, artifact_id, civ_id, entity_id, attacker_civ_id, defender_civ_id, attacker_general_hfid, defender_general_hfid, slayer_hfid, cause, source_site_id, group_1_hfid, group_2_hfid, a_leader_hfid, d_leader_hfid, reason, entity_id_1, entity_id_2, leader_hfid, site_id_1, site_id_2, link, corruptor_hfid, corruptor_identity, result, circumstance, topic, trickster_hfid, identity_id, dest_site_id, ]
        )
    add_unmatched_tags(unmatched_tags)

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

