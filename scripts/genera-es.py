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
    ('El disseny gràfic és la meua passió', 'El diseño gráfico es mi pasión'),
    ('Difusió al Mercat del Divendres del Grau', 'Difusión en el Mercado de los Viernes del Grau'),
    ('Difusió al Mercat del Dilluns de Castelló', 'Difusión en el Mercado de los Lunes de Castelló'),
    ('Taller de banderes per al teu balcó', 'Taller de banderas para tu balcón'),
    ('Cicle de Cinema Popular: ', 'Ciclo de Cine Popular: '),
    ('Com organitzem una vaga?', '¿Cómo organizamos una huelga?'),
    ('Xerrada + debat amb Raúl Beltrán / Sopar', 'Charla + debate con Raúl Beltrán / Cena'),
    ('Dia de la vaga general', 'Día de la huelga general'),
    ('Activitats per concretar', 'Actividades por concretar'),
]

DIES = {'Dl': 'Lun', 'Dm': 'Mar', 'Dc': 'Mié', 'Dj': 'Jue', 'Dv': 'Vie', 'Ds': 'Sáb', 'Dg': 'Dom'}

# Textos de la pàgina, en l'ordre en què s'apliquen (els llargs abans dels curts que contenen)
TEXTOS = [
    # Capçalera del document
    ('<html lang="ca">', '<html lang="es">'),
    ("<title>Vaga General 11N per l'habitatge · Castelló de la Plana</title>",
     '<title>Huelga General 11N por la vivienda · Castelló de la Plana</title>'),
    ("Vaga general per l'habitatge l'11 de novembre a Castelló. Reivindicacions, calendari d'activitats i com sumar-te. Vaga per la vivienda 11N.",
     "Huelga general por la vivienda el 11 de noviembre en Castelló. Reivindicaciones, calendario de actividades y cómo sumarte. Vaga per l'habitatge 11N."),
    ('''<script>
// Qui ha triat el castellà va directament a /es/
try { if (localStorage.getItem('vaga11-llengua') === 'es') location.replace('/es/' + location.hash); } catch (e) {}
</script>
''', ''),
    ('<link rel="canonical" href="https://vaga11ncs.vercel.app/">', '<link rel="canonical" href="https://vaga11ncs.vercel.app/es/">'),
    ('<meta property="og:url" content="https://vaga11ncs.vercel.app/">', '<meta property="og:url" content="https://vaga11ncs.vercel.app/es/">'),
    ('<meta property="og:locale" content="ca_ES">\n<meta property="og:locale:alternate" content="es_ES">',
     '<meta property="og:locale" content="es_ES">\n<meta property="og:locale:alternate" content="ca_ES">'),
    ("11N: Vaga general per l'habitatge · Castelló", '11N: Huelga general por la vivienda · Castelló'),
    ("Calendari d'activitats i reivindicacions. Apunta't i fes córrer la veu.",
     'Calendario de actividades y reivindicaciones. Apúntate y corre la voz.'),
    ("Vaga General 11.11 · Pel dret a l'habitatge · Comitè de Vaga de Castelló",
     'Huelga General 11.11 · Por el derecho a la vivienda · Comité de Huelga de Castelló'),

    # Dades d'esdeveniments
    ('"url": "https://vaga11ncs.vercel.app/",', '"url": "https://vaga11ncs.vercel.app/es/",'),
    ("Vaga general per l'habitatge l'11 de novembre. Per una vaga general de classe i combativa!",
     'Huelga general por la vivienda el 11 de noviembre. ¡Por una huelga general de clase y combativa!'),
    ("Vaga general per l'habitatge 11N", 'Huelga general por la vivienda 11N'),
    ('"inLanguage": "ca"', '"inLanguage": "es"'),

    # Estils
    ('content:"Ja s’ha fet"', 'content:"Ya realizada"'),

    # Menú
    ('>Vaga General · 11.11<', '>Huelga General · 11.11<'),
    ('<a href="#calendari">Calendari</a>', '<a href="#calendari">Calendario</a>'),
    ('<a href="#materials">Materials</a>', '<a href="#materials">Materiales</a>'),
    ('<a class="llengua" href="/es/" hreflang="es" lang="es" data-llengua="es" title="Versión en castellano">ES</a>',
     '<a class="llengua" href="/" hreflang="ca" lang="ca" data-llengua="ca" title="Versió en valencià">VAL</a>'),
    ('Canvia a tema fosc', 'Cambiar a tema oscuro'),
    ('Canvia a tema clar', 'Cambiar a tema claro'),
    ('Tema clar / fosc', 'Tema claro / oscuro'),

    # Portada i compte enrere
    ('<h1 class="display">Vaga<br>general</h1>', '<h1 class="display">Huelga<br>general</h1>'),
    ('El compliment del dret a l’habitatge és incompatible amb el seu negoci.',
     'El cumplimiento del derecho a la vivienda es incompatible con su negocio.'),
    ('<p class="compte-titol">Falten</p>', '<p class="compte-titol">Faltan</p>'),
    ('Compte enrere fins a la vaga general de l’11 de novembre', 'Cuenta atrás hasta la huelga general del 11 de noviembre'),
    ('<small>dies</small>', '<small>días</small>'),
    ('<small>hores</small>', '<small>horas</small>'),
    ('<small>minuts</small>', '<small>minutos</small>'),
    ('<small>segons</small>', '<small>segundos</small>'),
    ('Avui és la vaga!', '¡Hoy es la huelga!'),
    ("'La lluita continua!'", "'¡La lucha continúa!'"),

    # Reivindicacions
    ('Principals reivindicacions', 'Principales reivindicaciones'),
    ('<li>Aturar els desnonaments</li>', '<li>Parar los desahucios</li>'),
    ('<li>Abaixar els lloguers i contractes indefinits</li>', '<li>Bajar los alquileres y contratos indefinidos</li>'),
    ('<li>Expropiar els pisos buits i especulatius</li>', '<li>Expropiar los pisos vacíos y especulativos</li>'),
    ('<li>Prohibir la compra especulativa d’habitatge</li>', '<li>Prohibir la compra especulativa de vivienda</li>'),
    ('<li>Il·legalitzar les empreses de desocupació</li>', '<li>Ilegalizar las empresas de desokupación</li>'),
    ('<li>Pujada de salaris i pensions</li>', '<li>Subida de salarios y pensiones</li>'),
    ('<li>Jornada de 30 hores sense reducció salarial</li>', '<li>Jornada de 30 horas sin reducción salarial</li>'),
    ('<li>Reforç dels serveis públics i subministraments bàsics</li>', '<li>Refuerzo de los servicios públicos y suministros básicos</li>'),

    # Calendari
    ('<h2 class="display">Calendari</h2>', '<h2 class="display">Calendario</h2>'),
    ('Activitats del Comitè de Vaga de Castelló cap a l’11 de novembre. Apunta’t i vine.',
     'Actividades del Comité de Huelga de Castelló hacia el 11 de noviembre. Apúntate y ven.'),
    ('>Pròximes <span', '>Próximas <span'),
    ('>Passades <span', '>Pasadas <span'),
    ('<th>Dia</th><th>Hora</th><th>Activitat</th><th>Lloc</th><th>Inscripció</th>',
     '<th>Día</th><th>Hora</th><th>Actividad</th><th>Lugar</th><th>Inscripción</th>'),
    ('<td class="hora">Tot el dia</td>', '<td class="hora">Todo el día</td>'),
    ('>M’apunte</a>', '>Me apunto</a>'),
    ('>Més info</a>', '>Más info</a>'),
    ('No hi ha més activitats previstes. Segueix el canal de Telegram per a les novetats.',
     'No hay más actividades previstas. Sigue el canal de Telegram para enterarte de las novedades.'),
    ('Encara no s’ha fet cap activitat.', 'Todavía no se ha hecho ninguna actividad.'),

    ('Av. Ferrandis Salvador, 10 (Grau) - Dins del Pinar, al costat del camp de futbol',
     'Av. Ferrandis Salvador, 10 (Grau) - Dentro del Pinar, junto al campo de fútbol'),

    # Compartir una activitat
    ("boto: 'Comparteix'", "boto: 'Compartir'"),
    ("'Comparteix l’activitat: '", "'Comparte la actividad: '"),
    ("'Apunta’t: '", "'Apúntate: '"),
    ("info: 'Més info: '", "info: 'Más info: '"),
    ("'Tot el calendari: '", "'Todo el calendario: '"),
    ("'Copia el text'", "'Copiar el texto'"),
    ("'Copiat!'", "'¡Copiado!'"),
    ("'Guarda al calendari: '", "'Guardar en el calendario: '"),

    # Canal de Telegram
    ('Que no se’t passe res', 'Que no se te escape nada'),
    ('Avisos, canvis d’última hora, noves activitats i tot el que passe l’11 de novembre. Uneix-te al canal del Comitè de Vaga.',
     'Avisos, cambios de última hora, nuevas actividades y todo lo que pase el 11 de noviembre. Únete al canal del Comité de Huelga.'),
    ('Uneix-te al canal</a>', 'Únete al canal</a>'),

    # Materials
    ('<h2 class="display">Materials</h2>', '<h2 class="display">Materiales</h2>'),
    ('Cartells, imatges i vídeo per imprimir i difondre. Descarrega’ls i fes-los córrer.',
     'Carteles, imágenes y vídeo (en valenciano) para imprimir y difundir. Descárgalos y hazlos correr.'),
    ('<h3>Octavetes i cartells en paper</h3>', '<h3>Octavillas y carteles en papel</h3>'),
    ('Si en vols per repartir o penjar, passa a recollir-ne per <strong>La Verduleria</strong> (C/&nbsp;Cronista Muntaner,&nbsp;4) mentre hi haja activitats. Consulta el calendari per saber quan està oberta.',
     'Si quieres para repartir o colgar, pasa a recogerlos por <strong>La Verduleria</strong> (C/&nbsp;Cronista Muntaner,&nbsp;4) mientras haya actividades. Consulta el calendario para saber cuándo está abierta.'),
    ('Com arribar</a>', 'Cómo llegar</a>'),
    ('Mira el calendari</a>', 'Mira el calendario</a>'),
    ('Cartell amb les 8 reivindicacions de la vaga i codi QR', 'Cartel con las 8 reivindicaciones de la huelga y código QR'),
    ('<h3>Cartell de reivindicacions</h3>', '<h3>Cartel de reivindicaciones</h3>'),
    ('A4 amb les 8 reivindicacions i QR al canal de Telegram. Per imprimir i penjar.',
     'A4 con las 8 reivindicaciones y QR al canal de Telegram. Para imprimir y colgar.'),
    ("Cartell Vaga General 11.11 pel dret a l'habitatge", 'Cartel Huelga General 11.11 por el derecho a la vivienda'),
    ('<h3>Cartell Vaga General</h3>', '<h3>Cartel Huelga General</h3>'),
    ("«Pel dret a l'habitatge». En A4 i A3, per imprimir.", "«Pel dret a l'habitatge». En A4 y A3, para imprimir."),
    ('Diapositiva 16:9 de la vaga general amb QR al Telegram', 'Diapositiva 16:9 de la huelga general con QR al Telegram'),
    ('<h3>Projecció 16:9</h3>', '<h3>Proyección 16:9</h3>'),
    ('Per a pantalles, assemblees i presentacions. Amb QR al Telegram.', 'Para pantallas, asambleas y presentaciones. Con QR al Telegram.'),
    ("Història d'Instagram de la vaga general", 'Historia de Instagram de la huelga general'),
    ("<h3>Història d'Instagram</h3>", '<h3>Historia de Instagram</h3>'),
    ('Format vertical 1080×1920 per a stories i estats de WhatsApp.', 'Formato vertical 1080×1920 para stories y estados de WhatsApp.'),
    ("Post d'Instagram de la vaga general", 'Post de Instagram de la huelga general'),
    ("<h3>Post d'Instagram</h3>", '<h3>Post de Instagram</h3>'),
    ('Format 1080×1350 per a publicacions a xarxes.', 'Formato 1080×1350 para publicaciones en redes.'),
    ('Reel de la vaga general', 'Reel de la huelga general'),
    ('Vídeo vertical per a reels, TikTok i estats.', 'Vídeo vertical para reels, TikTok y estados.'),

    # Compartir
    ('<h2 class="display">Comparteix</h2>', '<h2 class="display">Comparte</h2>'),
    ('Fes córrer la veu: envia aquesta pàgina als teus grups.', 'Corre la voz: envía esta página a tus grupos.'),
    ('>Correu</a>', '>Correo</a>'),
    ('Vaga%20general%2011.11', 'Huelga%20general%2011.11'),
    ('https%3A%2F%2Fvaga11ncs.vercel.app%2F', 'https%3A%2F%2Fvaga11ncs.vercel.app%2Fes%2F'),
    ("'Vaga general 11.11 · Per una vaga general de classe i combativa!'",
     "'Huelga general 11.11 · ¡Por una huelga general de clase y combativa!'"),
    ("encodeURIComponent('Vaga general 11.11')", "encodeURIComponent('Huelga general 11.11')"),

    # Peu
    ('Per una vaga general de classe i combativa!</p>', '¡Por una huelga general de clase y combativa!</p>'),

    # Avís per afegir a la pantalla d'inici
    ('Afegeix la web a la pantalla d’inici', 'Añade la web a la pantalla de inicio'),
    ('Tin el calendari sempre a mà', 'Ten el calendario siempre a mano'),
    ('aria-label="Tanca"', 'aria-label="Cerrar"'),
    ('>Afegeix</button>', '>Añadir</button>'),
    ('>Ara no</button>', '>Ahora no</button>'),
    (' i després <b>«Afegeix a la pantalla d’inici»</b>.', ' y después <b>«Añadir a pantalla de inicio»</b>.'),
    ('Afig la web a la pantalla d’inici del mòbil i obri-la com una app.',
     'Añade la web a la pantalla de inicio del móvil y ábrela como una app.'),

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
