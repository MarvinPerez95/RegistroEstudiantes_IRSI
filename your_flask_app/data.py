# data.py

LATAM_PAISES_CIUDADES = {
    'Argentina': ['Buenos Aires', 'Córdoba', 'Rosario'],
    'Bolivia': ['La Paz', 'Santa Cruz', 'Cochabamba'],
    'Brasil': ['São Paulo', 'Río de Janeiro', 'Brasilia'],
    'Chile': ['Santiago', 'Valparaíso', 'Concepción'],
    'Colombia': ['Bogotá', 'Medellín', 'Cali'],
    'Costa Rica': ['San José', 'Alajuela', 'Cartago'],
    'Cuba': ['La Habana', 'Santiago de Cuba', 'Camagüey'],
    'Ecuador': ['Quito', 'Guayaquil', 'Cuenca'],
    'El Salvador': ['San Salvador', 'Santa Ana', 'San Miguel'],
    'Guatemala': ['Ciudad de Guatemala', 'Quetzaltenango', 'Escuintla'],
    'Honduras': ['Tegucigalpa', 'San Pedro Sula', 'La Ceiba'],
    'México': ['Ciudad de México', 'Guadalajara', 'Monterrey'],
    'Nicaragua': ['Managua', 'León', 'Masaya'],
    'Panamá': ['Ciudad de Panamá', 'Colón', 'David'],
    'Paraguay': ['Asunción', 'Ciudad del Este', 'Encarnación'],
    'Perú': ['Lima', 'Cusco', 'Arequipa'],
    'República Dominicana': ['Santo Domingo', 'Santiago de los Caballeros', 'La Romana'],
    'Uruguay': ['Montevideo', 'Salto', 'Paysandú'],
    'Venezuela': ['Caracas', 'Maracaibo', 'Valencia']
}

# Mapeo de país a nombre de documento de identidad
NOMBRE_DOCUMENTO_POR_PAIS = {
    'Argentina': 'DNI (Documento Nacional de Identidad)',
    'Bolivia': 'C.I. (Cédula de Identidad)',
    'Brasil': 'RG (Registro Geral)',
    'Chile': 'RUT (Rol Único Tributario)',
    'Colombia': 'C.C. (Cédula de Ciudadanía)',
    'Costa Rica': 'Cédula de Identidad (DNI)', # Agrego DNI entre paréntesis para tu ejemplo
    'Cuba': 'Carnet de Identidad',
    'Ecuador': 'Cédula de Identidad',
    'El Salvador': 'DUI (Documento Único de Identidad)',
    'Guatemala': 'DPI (Documento Personal de Identificación)', # Tu ejemplo
    'Honduras': 'DNI (Documento Nacional de Identificación)',
    'México': 'INE (Credencial para Votar - INE)', # Tu ejemplo
    'Nicaragua': 'Cédula de Identidad Ciudadana',
    'Panamá': 'Cédula de Identidad Personal',
    'Paraguay': 'C.I. (Cédula de Identidad)',
    'Perú': 'DNI (Documento Nacional de Identidad)',
    'República Dominicana': 'Cédula de Identidad y Electoral',
    'Uruguay': 'Cédula de Identidad',
    'Venezuela': 'C.I. (Cédula de Identidad)'
}