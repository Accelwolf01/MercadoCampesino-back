import re

f = open('init.sql', 'rb')
raw = f.read()
f.close()

replacements = {
    b'inicializaci\xef\xbf\xbdn': b'inicializaci\xc3\xb3n',
    b'Inicializaci\xef\xbf\xbdn': b'Inicializaci\xc3\xb3n',
    b'relaci\xef\xbf\xbdn': b'relaci\xc3\xb3n',
    b'cad\xef\xbf\xbddigo': b'c\xc3\xa9dula',
    b'c\xef\xbf\xbddula': b'c\xc3\xa9dula',
    b'C\xef\xbf\xbddula': b'C\xc3\xa9dula',
    b'Tub\xef\xbf\xbdrculos': b'Tub\xc3\xa9rculos',
    b'ra\xef\xbf\xbdces': b'ra\xc3\xadces',
    b'L\xef\xbf\xbdcteos': b'L\xc3\xa1cteos',
    b'arom\xef\xbf\xbdticas': b'arom\xc3\xa1ticas',
    b'Mart\xef\xbf\xbdnez': b'Mart\xc3\xadnez',
    b'Garc\xef\xbf\xbda': b'Garc\xc3\xada',
    b'Fr\xef\xbf\xbdjol': b'Fr\xc3\xadjol',
    b'Bogot\xef\xbf\xbd': b'Bogot\xc3\xa1',
    b'categor\xef\xbf\xbdas': b'categor\xc3\xadas',
    b'descripci\xef\xbf\xbdn': b'descripci\xc3\xb3n',
    b'Descripci\xef\xbf\xbdn': b'Descripci\xc3\xb3n',
    b'rese\xef\xbf\xbda': b'rese\xc3\xb1a',
    b'rese\xef\xbf\xbdas': b'rese\xc3\xb1as',
    b'Rese\xef\xbf\xbdas': b'Rese\xc3\xb1as',
    b'Se\xef\xbf\xbdalar': b'Se\xc3\xb1alar',
    b'se\xef\xbf\xbdalar': b'se\xc3\xb1alar',
    b'ubicaci\xef\xbf\xbdn': b'ubicaci\xc3\xb3n',
    b'Ubicaci\xef\xbf\xbdn': b'Ubicaci\xc3\xb3n',
    b'pre\xef\xbf\xbdrdenes': b'pre\xc3\xb3rdenes',
    b'Pre\xef\xbf\xbdrdenes': b'Pre\xc3\xb3rdenes',
    b'pre\xef\xbf\xbdrden': b'pre\xc3\xb3rden',
    b'Pre\xef\xbf\xbdrden': b'Pre\xc3\xb3rden',
    b'historial_ventas': b'historial_ventas',
    b'historial_compras': b'historial_compras',
    b'puntuaci\xef\xbf\xbdn': b'puntuaci\xc3\xb3n',
    b'comentario': b'comentario',
    b'reportada': b'reportada',
    b'reportadas': b'reportadas',
    b'respuesta': b'respuesta',
    b'reportes': b'reportes',
    b'Rpublicar': b'Publicar',
    b'ra publicaci': b'publicaci',
    b'publicaci\xef\xbf\xbdn': b'publicaci\xc3\xb3n',
    b'Publicaci\xef\xbf\xbdn': b'Publicaci\xc3\xb3n',
}

for old, new in replacements.items():
    raw = raw.replace(old, new)

remaining = raw.count(b'\xef\xbf\xbd')
print(f'Remaining: {remaining}')

if remaining > 0:
    text = raw.decode('latin-1')
    text = text.replace('ï¿½', '')
    raw = text.encode('latin-1')
    remaining = raw.count(b'\xef\xbf\xbd')
    print(f'After cleanup: {remaining}')

f = open('init.sql', 'wb')
f.write(raw)
f.close()
print('Done')
