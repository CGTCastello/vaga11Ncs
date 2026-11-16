#!/usr/bin/env python3
"""Genera la versió en castellà (es/index.html) a partir de la valenciana (index.html).

La pàgina valenciana és l'única que s'edita a mà. Després de cada canvi:

    python3 scripts/genera-es.py

Si algun text de la llista ja no apareix (perquè s'ha canviat en valencià),
o si hi ha una activitat del calendari sense traducció, el script falla i avisa.
"""
import os
import re
import sys

ARREL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEN = os.path.join(ARREL, 'index.html')
DESTI = os.path.join(ARREL, 'es', 'index.html')

# Activitats del calendari (també surten a les dades d'esdeveniments per a Google).
# Quan s'afig una activitat nova amb un nom nou, cal posar-ne ací la traducció.
ACTIVITATS = [
]

DIES = {'Dl': 'Lun', 'Dm': 'Mar', 'Dc': 'Mié', 'Dj': 'Jue', 'Dv': 'Vie', 'Ds': 'Sáb', 'Dg': 'Dom'}

# Textos de la pàgina, en l'ordre en què s'apliquen (els llargs abans dels curts que contenen)
TEXTOS = [
    # Capçalera del document
    ('<html lang="ca">', '<html lang="es">'),
    ('''<script>
// Qui ha triat el castellà va directament a /es/
try { if (localStorage.getItem('vaga11-llengua') === 'es') location.replace('/es/' + location.hash); } catch (e) {}
</script>
''', ''),
    ('<link rel="canonical" href="https://vaga11ncs.vercel.app/">', '<link rel="canonical" href="https://vaga11ncs.vercel.app/es/">'),
    ('<meta property="og:url" content="https://vaga11ncs.vercel.app/">', '<meta property="og:url" content="https://vaga11ncs.vercel.app/es/">'),
    ('<meta property="og:locale" content="ca_ES">\n<meta property="og:locale:alternate" content="es_ES">',
     '<meta property="og:locale" content="es_ES">\n<meta property="og:locale:alternate" content="ca_ES">'),
    ("Vaga General 11.11 · Pel dret a l'habitatge · Comitè de Vaga de Castelló",
     'Huelga General 11.11 · Por el derecho a la vivienda · Comité de Huelga de Castelló'),

    ('<title>Llibertat empresonades 11/11 · Comitè de Vaga de Castelló</title>',
     '<title>Llibertat empresonades 11/11 · Comité de Huelga de Castelló</title>'),
    ('Dies que porten a la presó les persones detingudes a la vaga general de l’11 de novembre a Castelló i comunicat del Comitè de Vaga de Castelló i Comarques.',
     'Días que llevan en prisión las personas detenidas en la huelga general del 11 de noviembre en Castelló y comunicado del Comité de Huelga de Castelló y Comarcas.'),
    ('Porten dies a la presó per exercir el dret a vaga. Si toquen a una, ens toquen a totis!',
     'Llevan días en prisión por ejercer el derecho a huelga. ¡Si tocan a una, nos tocan a todes!'),

    # Dades d'esdeveniments

    # Estils

    # Menú
    ('>Vaga General · 11.11<', '>Huelga General · 11.11<'),
    ('<a class="llengua" href="/es/" hreflang="es" lang="es" data-llengua="es" title="Versión en castellano">ES</a>',
     '<a class="llengua" href="/" hreflang="ca" lang="ca" data-llengua="ca" title="Versió en valencià">VAL</a>'),
    ('Canvia a tema fosc', 'Cambiar a tema oscuro'),
    ('Canvia a tema clar', 'Cambiar a tema claro'),
    ('Tema clar / fosc', 'Tema claro / oscuro'),

    # Portada i compte enrere
    ('<small>dies</small>', '<small>días</small>'),

    # Reivindicacions

    # Calendari



    # Compartir una activitat

    # Llibertat empresonades i comunicat
    ('<a href="#comunicat">Comunicat</a>',
     '<a href="#comunicat">Comunicado</a>'),
    ('Format de la imatge', 'Formato de la imagen'),
    ('<p class="compte-titol">Porten a la presó</p>',
     '<p class="compte-titol">Llevan en prisión</p>'),
    ('Temps que porten a la presó les persones detingudes l’11 de novembre',
     'Tiempo que llevan en prisión las personas detenidas el 11 de noviembre'),
    ('Comparteix la imatge</button>',
     'Compartir la imagen</button>'),
    ('>Descarrega la imatge</button>',
     '>Descargar la imagen</button>'),
    ('>Envia per WhatsApp</a>',
     '>Enviar por WhatsApp</a>'),
    ('Imatge per compartir: Llibertat empresonades 11/11, amb els dies que porten a la presó',
     'Imagen para compartir: Llibertat empresonades 11/11, con los días que llevan en prisión'),
    ("text: 'Porten {n} a la presó. Llibertat empresonades 11/11! Si toquen a una, ens toquen a totis! ✊'",
     "text: 'Llevan {n} en prisión. ¡Libertad para las encarceladas del 11/11! ¡Si tocan a una, nos tocan a todes! ✊'"),
    ("dia: 'dia',",
     "dia: 'día',"),
    ("dies: 'dies',",
     "dies: 'días',"),
    ("'Imatge descarregada. Ara pots pujar-la a Instagram, WhatsApp o on vulgues.'",
     "'Imagen descargada. Ya puedes subirla a Instagram, WhatsApp o donde quieras.'"),
    ('<h2 class="display">Comunicat</h2>',
     '<h2 class="display">Comunicado</h2>'),
    ('<p class="comunicat-autor">Comitè de Vaga de Castelló i Comarques</p>',
     '<p class="comunicat-autor">Comité de Huelga de Castelló y Comarcas</p>'),
    ('A la vista de les últimes notícies i l’ocorregut el darrer dia 11 de novembre amb motiu de la convocatòria de Vaga General, no només arreu de l’Estat Espanyol sinó, especialment a la ciutat de Castelló, des del Comité de Vaga de Castelló i Comarques expressem la més ferma condemna enfront de la intolerable repressió per part de les forces i cossos de seguretat de l’Estat. Concretament, l’actuació de les forces de seguretat cap a la població, violència, detencions i empresonaments que s’han dut a terme dins d’una clara estratègia repressiva contra els drets a vaga i manifestació de la classe treballadora.',
     'A la vista de las últimas noticias y de lo ocurrido el pasado 11 de noviembre con motivo de la convocatoria de Huelga General, no solo en todo el Estado español sino, especialmente, en la ciudad de Castelló, desde el Comité de Huelga de Castelló y Comarcas expresamos la más firme condena ante la intolerable represión por parte de las fuerzas y cuerpos de seguridad del Estado. En concreto, la actuación de las fuerzas de seguridad contra la población: la violencia, las detenciones y los encarcelamientos que se han llevado a cabo dentro de una clara estrategia represiva contra los derechos de huelga y de manifestación de la clase trabajadora.'),
    ('Tal com va ocórrer els dies anteriors a la vaga amb la pressió intimidatòria cap a companyes i sindicalistes, el dimecres 11 la policia va assetjar i provocar contínuament als piquets informatius, impedint la seua tasca i els drets de les treballadores a ser informades, amb actitud hostil i provocativa que va generar tensió, enfrontaments i la identificació de companyes vaguistes i estudiants sense cap motiu ni excusa als piquets de tota la nostra ciutat. Condemnem amb absoluta rotunditat la desmesurada utilització de la força per part dels agents contra les persones que exercien el seu dret i les detencions que es van dur a terme amb acarnissament i violència, especialment la d’un menor d’edat, la companya assetjada al centre de treball i el company empresonat.',
     'Tal como ocurrió los días previos a la huelga con la presión intimidatoria hacia compañeras y sindicalistas, el miércoles 11 la policía acosó y provocó continuamente a los piquetes informativos, impidiendo su tarea y el derecho de las trabajadoras a ser informadas, con una actitud hostil y provocadora que generó tensión, enfrentamientos y la identificación de compañeras huelguistas y estudiantes sin ningún motivo ni excusa en los piquetes de toda nuestra ciudad. Condenamos con absoluta rotundidad el desmesurado uso de la fuerza por parte de los agentes contra las personas que ejercían su derecho y las detenciones que se llevaron a cabo con ensañamiento y violencia, especialmente la de un menor de edad, la de la compañera acosada en su centro de trabajo y la del compañero encarcelado.'),
    ('És per tot això que, exigim la posada en llibertat immediata de totes les persones empresonades, la presa de mesures i responsabilitats contra els càrrecs policials i els agents encarregats dels dispositius implicats, des de dalt fins a baix, i unes explicacions que ja arriben tard per part de la Subdelegació del Govern a Castelló sobre els greus fets que vaguistes, sindicalistes i població en general vàrem patir el passat 11 de novembre a la nostra ciutat.',
     'Por todo ello, exigimos la puesta en libertad inmediata de todas las personas encarceladas, la toma de medidas y la depuración de responsabilidades de los mandos policiales y de los agentes a cargo de los dispositivos implicados, de arriba abajo, y unas explicaciones, que ya llegan tarde, por parte de la Subdelegación del Gobierno en Castelló sobre los graves hechos que huelguistas, sindicalistas y población en general sufrimos el pasado 11 de noviembre en nuestra ciudad.'),
    ('<p class="display comunicat-lema">Si toquen a una, ens toquen a totis!</p>',
     '<p class="display comunicat-lema">¡Si tocan a una, nos tocan a todes!</p>'),

    # Canal de Telegram

    # Materials

    # Compartir

    # Peu
    ('Per una vaga general de classe i combativa!</p>', '¡Por una huelga general de clase y combativa!</p>'),

    # Avís per afegir a la pantalla d'inici

    # Nom del comitè (al final, perquè ja s'han traduït les frases que el contenen)
    ('Comitè de Vaga de Castelló', 'Comité de Huelga de Castelló'),
]


def main():
    s = open(ORIGEN, encoding='utf-8').read()
    errors = []

    # Activitats sense traducció: es comproven les cel·les .act del calendari
    for act in re.findall(r'<td class="act">(.*?)</td>', s):
        net = re.sub(r'<span class="nota">.*?</span>', '', act)
        net = re.sub(r'<[^>]+>', '', net)
        if not any(net.startswith(ca) for ca, _ in ACTIVITATS):
            errors.append('Activitat sense traducció a ACTIVITATS: ' + net)

    for ca, es in TEXTOS[:-1] + ACTIVITATS + TEXTOS[-1:]:
        if ca not in s:
            errors.append('No es troba el text: ' + ca[:80])
            continue
        s = s.replace(ca, es)

    s = re.sub(r'<td class="dia">(D[lmcjvsg]) ', lambda m: '<td class="dia">' + DIES[m.group(1)] + ' ', s)

    # Rutes relatives: la pàgina viu un nivell més avall (/es/)
    s = re.sub(r'\b(src|href|poster)="(?!https?:|#|/|mailto:|data:)([^"]+)"', r'\1="../\2"', s)

    if errors:
        sys.exit('\n'.join(errors))

    capcalera = '<!-- Fitxer generat per scripts/genera-es.py a partir de index.html. No l’edites a mà. -->\n'
    s = s.replace('<!doctype html>\n', '<!doctype html>\n' + capcalera, 1)
    os.makedirs(os.path.dirname(DESTI), exist_ok=True)
    open(DESTI, 'w', encoding='utf-8').write(s)
    print('Generat', os.path.relpath(DESTI, ARREL))


if __name__ == '__main__':
    main()
