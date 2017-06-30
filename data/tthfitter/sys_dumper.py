import aidapy.meta

for s in aidapy.meta._systematic_ud_prefixes:
    up = '__1up"'
    down = '__1down"'
    if 'MET_' in s:
        up = 'Up"'
        down = 'Down"'
    print('Systematic: "'+s+'"')
    print('  Title: "'+s+'"')
    print('  Type: HISTO')
    print('  Samples: ttbar,Wt,WW,Ztautau,Diboson,Fakes,RareSM')
    print('  HistoNameSufUp: "_'+s+up)
    print('  HistoNameSufDown: "_'+s+down)
    print('  Regions: met_1pj,met_0j')
    print('')
