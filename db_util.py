import sqlite3
import os
import settings
from summary_util import get_histfig_summary


def get_con():
    dbpath = settings.get_setting('db_name') + '.db'
    if not os.path.exists(dbpath):
        raise Exception('Database does not exist: {dbpath}'.format(dbpath=dbpath))
    con = sqlite3.connect(dbpath)
    return con

def search_sites(search_text, site_type=None, page_num=1, page_size=50):
    con = get_con()
    cur = con.cursor()
    if site_type is None:
        query_txt = 'select id, name, type from sites where name like ? order by id limit ? offset ?'
        cur.execute(query_txt, ('%'+search_text+'%', page_size, page_size * (page_num - 1)))
    else:
        query_txt = 'select id, name, type from sites where name like ? and type like ? order by id limit ? offset ?'
        cur.execute(query_txt, ('%'+search_text+'%', '%'+site_type+'%', page_size, page_size * (page_num - 1)))
    matches = []
    for result in cur.fetchall():
        matches.append({
            'id': result[0],
            'name': result[1] if len(result[1]) > 0 else 'unnamed',
            'type': result[2]
        })
    if site_type is None:
        count_txt = 'select count(*) from sites where name like ?'
        cur.execute(count_txt, ('%'+search_text+'%',))
    else:
        count_txt = 'select count(*) from sites where name like ? and type like ?'
        cur.execute(count_txt, ('%'+search_text+'%', '%'+site_type+'%'))
    total_count = cur.fetchone()[0]
    con.close()
    return matches, total_count

def search_histfigs(search_text, page_num=1, page_size=50):
    con = get_con()
    cur = con.cursor()
    query_txt = 'select id from historical_figures where name like ? order by id limit ? offset ?'
    cur.execute(query_txt, ('%'+search_text+'%', page_size, page_size * (page_num - 1)))
    matches = []
    for result in cur.fetchall():
        matches.append({
            'id': result[0],
            'name': get_histfig_summary(cur, result[0])
        })
    count_txt = 'select count(*) from historical_figures where name like ?'
    cur.execute(count_txt, ('%'+search_text+'%',))
    total_count = cur.fetchone()[0]
    con.close()
    return matches, total_count

def search_artifacts(search_text, page_num=1, page_size=50):
    con = get_con()
    cur = con.cursor()
    query_txt = 'select id, name from artifacts where name like ? order by id limit ? offset ?'
    cur.execute(query_txt, ('%'+search_text+'%', page_size, page_size * (page_num - 1)))
    matches = []
    for result in cur.fetchall():
        matches.append({
            'id': result[0],
            'name': result[1] if len(result[1]) > 0 else 'unnamed',
        })
    count_txt = 'select count(*) from artifacts where name like ?'
    cur.execute(count_txt, ('%'+search_text+'%',))
    total_count = cur.fetchone()[0]
    con.close()
    return matches, total_count

def get_site_details(site_id):
    con = get_con()
    cur = con.cursor()
    query_txt = 'select id, name, type, coords, rectangle from sites where id = ?'
    cur.execute(query_txt, (site_id,))
    vals = cur.fetchone()
    site = {
        'id': vals[0],
        'name': vals[1] if len(vals[1]) > 0 else 'unnamed',
        'type': vals[2],
        'coords': vals[3],
        'rectangle': vals[4],
    }
    query_txt = 'select hf.id, hfl.link_type from historical_figures hf inner join hf_to_site_links hfl on hf.id=hfl.hfid where hfl.site_id = ? order by hfl.link_type asc'
    cur.execute(query_txt, (site_id,))
    histfigs = []
    for match in cur.fetchall():
        histfigs.append({
            'id': match[0],
            'name': get_histfig_summary(cur, match[1]),
            'link_type': match[1]
        })
    site['histfigs'] = histfigs
    query_txt = 'select id, name from artifacts where site_id = ?'
    cur.execute(query_txt, (site_id,))
    artifacts = []
    for match in cur.fetchall():
        artifacts.append({
            'id': match[0],
            'name': match[1] if len(match[1]) > 0 else 'unnamed'
        })
    site['artifacts'] = artifacts
    query_txt = 'select id, year, type from historical_events where site_id = ?'
    cur.execute(query_txt, (site_id,))
    historical_events = []
    for match in cur.fetchall():
        historical_events.append({
            'id': match[0],
            'year': match[1],
            'type': match[2],
        })
    site['historical_events'] = historical_events
    return site

def get_histfig_details(hfid):
    con = get_con()
    cur = con.cursor()
    # basic info
    query_txt = 'select id, name, race, caste, appeared, birth_year, death_year, is_deity, is_force, is_ghost, current_identity_id from historical_figures where id = ?'
    cur.execute(query_txt, (hfid,))
    vals = cur.fetchone()
    histfig = {
        'id': vals[0],
        'name': vals[1].title() if len(vals[1]) > 0 else 'unnamed',
        'race': vals[2].lower().replace('_', ' '),
        'caste': vals[3].lower(),
        'appeared': vals[4],
        'birth_year': vals[5],
        'death_year': vals[6],
        'not_dead': vals[6] == -1,
        'is_deity': vals[7] == 1,
        'is_force': vals[8] == 1,
        'is_ghost': vals[9] == 1,
        'current_identity': '',
    }
    current_identity_id = vals[10]
    if current_identity_id > -1:
        histfig['current_identity'] = {
            'id': current_identity_id,
            'name': get_histfig_summary(cur, current_identity_id),
        }
    # related sites
    query_txt = 'select s.id, s.name, sl.link_type from sites s inner join hf_to_site_links sl on s.id=sl.site_id where sl.hfid = ? order by sl.link_type asc'
    cur.execute(query_txt, (hfid,))
    sites = []
    for match in cur.fetchall():
        sites.append({
            'id': match[0],
            'name': match[1] if len(match[1]) > 0 else 'unnamed',
            'link_type': match[2]
        })
    histfig['sites'] = sites
    # related historical figures
    query_txt = 'select hf.id, hfl.link_type from historical_figures hf inner join hf_to_hf_links hfl on hf.id=hfl.target_hfid where hfl.hfid = ? order by hfl.link_type asc'
    cur.execute(query_txt, (hfid,))
    rel_histfigs = []
    for match in cur.fetchall():
        rel_histfigs.append({
            'id': match[0],
            'name': get_histfig_summary(cur, match[0]),
            'link_type': match[1]
        })
    histfig['histfigs'] = rel_histfigs
    # related entities
    query_txt = 'select e.id, e.name, el.link_type from entities e inner join hf_to_entity_links el on e.id=el.entity_id where el.hfid = ? order by el.link_type asc'
    cur.execute(query_txt, (hfid,))
    entities = []
    for match in cur.fetchall():
        entities.append({
            'id': match[0],
            'name': match[1] if len(match[1]) > 0 else 'unnamed',
            'link_type': match[2]
        })
    histfig['entities'] = entities
    # skills
    query_txt = 'select skill, total_ip from hf_skills where hfid = ? order by total_ip desc'
    cur.execute(query_txt, (hfid,))
    skills = []
    for match in cur.fetchall():
        skills.append({
            'skill': match[0],
            'total_ip': match[1],
        })
    histfig['skills'] = skills
    # artifacts
    query_txt = 'select id, name from artifacts where holder_hfid = ?'
    cur.execute(query_txt, (hfid,))
    artifacts = []
    for match in cur.fetchall():
        artifacts.append({
            'id': match[0],
            'name': match[1] if len(match[1]) > 0 else 'unnamed'
        })
    histfig['artifacts'] = artifacts
    # historical events
    query_txt = 'select id, year, type from historical_events where hfid = ?'
    cur.execute(query_txt, (hfid,))
    historical_events = []
    for match in cur.fetchall():
        historical_events.append({
            'id': match[0],
            'year': match[1],
            'type': match[2],
        })
    # goals
    query_txt = 'select goal from hf_goals where hfid = ?'
    cur.execute(query_txt, (hfid,))
    goals = []
    for match in cur.fetchall():
        goals.append({
            'goal': match[0],
        })
    histfig['goals'] = goals
    # honor entities
    query_txt = 'select entity_id, battles, kills, honor_id from hf_honor_entities where hfid = ?'
    cur.execute(query_txt, (hfid,))
    honor_entities = []
    for match in cur.fetchall():
        honor_entities.append({
            'entity_id': match[0],
            'battles': match[1],
            'kills': match[2],
            'honor_id': match[3],
        })
    histfig['skills'] = skills
    return histfig

def get_artifact_details(art_id):
    con = get_con()
    cur = con.cursor()
    query_txt = 'select id, name, site_id, holder_hfid from artifacts where id = ?'
    cur.execute(query_txt, (art_id,))
    vals = cur.fetchone()
    artifact = {
        'id': vals[0],
        'name': vals[1] if len(vals[1]) > 0 else 'unnamed',
        'site': '',
        'holder': ''
    }
    site_id = vals[2]
    holder_id = vals[3]
    if site_id > -1:
        query_txt = 'select id, name from sites where id = ?'
        cur.execute(query_txt, (site_id,))
        vals = cur.fetchone()
        artifact['site'] = {
            'id': vals[0],
            'name': vals[1] if len(vals[1]) > 0 else 'unnamed',
        }
    if holder_id > -1:
        artifact['holder'] = {
            'id': holder_id,
            'name': get_histfig_summary(cur, holder_id),
        }
    query_txt = 'select id, year, type from historical_events where artifact_id = ?'
    cur.execute(query_txt, (art_id,))
    historical_events = []
    for match in cur.fetchall():
        historical_events.append({
            'id': match[0],
            'year': match[1],
            'type': match[2],
        })
    artifact['historical_events'] = historical_events
    return artifact

def get_event_details(evt_id):
    con = get_con()
    cur = con.cursor()
    query_txt = 'select id, year, type, state, coords, knowledge, hfid, site_id, artifact_id, entity_id, civ_id, attacker_civ_id, defender_civ_id, attacker_general_hfid, defender_general_hfid, slayer_hfid from historical_events where id = ?'
    cur.execute(query_txt, (evt_id,))
    vals = cur.fetchone()
    event = {
        'id': vals[0],
        'year': vals[1],
        'type': vals[2],
        'state': vals[3],
        'coords': vals[4],
        'knowledge': vals[5],
        'histfig': '',
        'site': '',
        'artifact': '',
        'entity': '',
        'civ': '',
        'attacker_civ': '',
        'defender_civ': '',
        'attacker_general': '',
        'defender_general': '',
        'slayer': '',
    }
    hfid = vals[6]
    site_id = vals[7]
    art_id = vals[8]
    ent_id = vals[9]
    civ_id = vals[10]
    attacker_civ_id = vals[11]
    defender_civ_id = vals[12]
    attacker_general_hfid = vals[13]
    defender_general_hfid = vals[14]
    slayer_hfid = vals[15]
    if hfid > -1:
        event['histfig'] = {
            'id': hfid,
            'name': get_histfig_summary(cur, hfid),
        }
    if site_id > -1:
        query_txt = 'select id, name from sites where id = ?'
        cur.execute(query_txt, (site_id,))
        vals = cur.fetchone()
        event['site'] = {
            'id': vals[0],
            'name': vals[1] if len(vals[1]) > 0 else 'unnamed',
        }
    if art_id > -1:
        query_txt = 'select id, name from artifacts where id = ?'
        cur.execute(query_txt, (art_id,))
        vals = cur.fetchone()
        event['artifact'] = {
            'id': vals[0],
            'name': vals[1] if len(vals[1]) > 0 else 'unnamed',
        }
    if ent_id > -1:
        query_txt = 'select id, name from entities where id = ?'
        cur.execute(query_txt, (ent_id,))
        vals = cur.fetchone()
        event['entity'] = {
            'id': vals[0],
            'name': vals[1] if len(vals[1]) > 0 else 'unnamed',
        }
    if civ_id > -1:
        query_txt = 'select id, name from entities where id = ?'
        cur.execute(query_txt, (civ_id,))
        vals = cur.fetchone()
        event['civ'] = {
            'id': vals[0],
            'name': vals[1] if len(vals[1]) > 0 else 'unnamed',
        }
    if attacker_civ_id > -1:
        query_txt = 'select id, name from entities where id = ?'
        cur.execute(query_txt, (attacker_civ_id,))
        vals = cur.fetchone()
        event['attacker_civ'] = {
            'id': vals[0],
            'name': vals[1] if len(vals[1]) > 0 else 'unnamed',
        }
    if defender_civ_id > -1:
        query_txt = 'select id, name from entities where id = ?'
        cur.execute(query_txt, (defender_civ_id,))
        vals = cur.fetchone()
        event['defender_civ'] = {
            'id': vals[0],
            'name': vals[1] if len(vals[1]) > 0 else 'unnamed',
        }
    if attacker_general_hfid > -1:
        event['attacker_general'] = {
            'id': attacker_general_hfid,
            'name': get_histfig_summary(cur, attacker_general_hfid),
        }
    if defender_general_hfid > -1:
        event['defender_general'] = {
            'id': defender_general_hfid,
            'name': get_histfig_summary(cur, defender_general_hfid),
        }
    if slayer_hfid > -1:
        event['slayer'] = {
            'id': slayer_hfid,
            'name': get_histfig_summary(cur, slayer_hfid),
        }
    return event

def get_entity_details(ent_id):
    con = get_con()
    cur = con.cursor()
    query_txt = 'select id, name from entities where id = ?'
    cur.execute(query_txt, (ent_id,))
    vals = cur.fetchone()
    entity = {
        'id': vals[0],
        'name': vals[1] if len(vals[1]) > 0 else 'unnamed',
    }
    return entity
