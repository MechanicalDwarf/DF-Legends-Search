
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