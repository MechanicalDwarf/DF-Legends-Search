
def get_histfig_summary(cur, hfid):
    query_txt = 'select name, caste, race, death_year, is_deity, is_force, is_ghost from historical_figures where id = ?'
    cur.execute(query_txt, (hfid,))
    vals = cur.fetchone()
    name = vals[0].title()
    caste = vals[1].lower()
    race = vals[2].lower()
    is_dead = vals[3] > -1
    is_deity = vals[4] == 1
    is_force = vals[5] == 1
    is_ghost = vals[6] == 1
    summary = f"{name if len(name) > 0 else 'unnamed'}, {caste} {race}"
    if is_deity:
        summary += ' (deity)'
    elif is_force:
        summary += ' (force)'
    elif is_dead:
        summary += ' (dead)'
    elif is_ghost:
        summary += ' (ghost)'
    return summary

def get_site_summary(cur, site_id):
    query_txt = 'select name, type from sites where id = ?'
    cur.execute(query_txt, (site_id,))
    vals = cur.fetchone()
    name = vals[0].title()
    s_type = vals[1].lower()
    summary = f"{name if len(name) > 0 else 'unnamed'} ({s_type})"
    return summary

def get_entity_summary(cur, entity_id):
    query_txt = 'select name from entities where id = ?'
    cur.execute(query_txt, (entity_id,))
    vals = cur.fetchone()
    name = vals[0].title()
    summary = f"{name if len(name) > 0 else 'unnamed'}"
    return summary