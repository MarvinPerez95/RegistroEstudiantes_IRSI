# data.py

LATAM_PAISES_CIUDADES = {
    'Argentina': ['Buenos Aires', 'Córdoba', 'Rosario', 'Mendoza', 'La Plata', 'Tucumán', 'Mar del Plata', 'Salta', 'Santa Fe', 'San Juan', 'Resistencia', 'Neuquén', 'Santiago del Estero', 'Corrientes', 'Posadas', 'Bahía Blanca', 'Paraná', 'Formosa', 'San Luis', 'La Rioja', 'Catamarca', 'Jujuy', 'Río Gallegos', 'Ushuaia', 'San Salvador de Jujuy'],
    'Bolivia': ['La Paz', 'Santa Cruz de la Sierra', 'Cochabamba', 'Sucre', 'Oruro', 'Potosí', 'Tarija', 'Trinidad', 'Cobija', 'Montero', 'El Alto', 'Quillacollo', 'Sacaba', 'Camiri', 'Riberalta', 'Guayaramerín', 'Villazón', 'Yacuiba', 'Warnes', 'La Guardia'],
    'Brasil': ['São Paulo', 'Río de Janeiro', 'Brasilia', 'Salvador', 'Fortaleza', 'Belo Horizonte', 'Manaus', 'Curitiba', 'Recife', 'Goiânia', 'Belém', 'Porto Alegre', 'Guarulhos', 'Campinas', 'São Luís', 'São Gonçalo', 'Maceió', 'Duque de Caxias', 'Nova Iguaçu', 'Teresina', 'Natal', 'Campo Grande', 'São Bernardo do Campo', 'João Pessoa', 'Santo André', 'Osasco'],
    'Chile': ['Santiago', 'Valparaíso', 'Concepción', 'La Serena', 'Antofagasta', 'Temuco', 'Rancagua', 'Talca', 'Arica', 'Chillán', 'Iquique', 'Los Ángeles', 'Puerto Montt', 'Valdivia', 'Osorno', 'Quillota', 'Ovalle', 'Curicó', 'Punta Arenas', 'Calama', 'Copiapó', 'Linares', 'San Antonio', 'Melipilla', 'Villarrica'],
    'Colombia': ['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Cartagena', 'Cúcuta', 'Bucaramanga', 'Pereira', 'Santa Marta', 'Ibagué', 'Pasto', 'Manizales', 'Neiva', 'Villavicencio', 'Armenia', 'Valledupar', 'Montería', 'Sincelejo', 'Popayán', 'Buenaventura', 'Tunja', 'Florencia', 'Yopal', 'Quibdó', 'Riohacha', 'Mitú', 'Puerto Carreño', 'San José del Guaviare', 'Leticia', 'Mocoa', 'Inírida', 'San Andrés'],
    'Costa Rica': ['San José', 'Alajuela', 'Cartago', 'Puntarenas', 'Heredia', 'Limón', 'Liberia', 'Pococí', 'San Carlos', 'Pérez Zeledón', 'Desamparados', 'Escazú', 'Santa Ana', 'Curridabat', 'San Ramón', 'Palmares', 'Grecia', 'Atenas', 'Naranjo', 'Puriscal'],
    'Cuba': ['La Habana', 'Santiago de Cuba', 'Camagüey', 'Holguín', 'Guantánamo', 'Santa Clara', 'Las Tunas', 'Bayamo', 'Cienfuegos', 'Pinar del Río', 'Matanzas', 'Ciego de Ávila', 'Sancti Spíritus', 'Manzanillo', 'Cardenas', 'Palma Soriano', 'Artemisa', 'Mayabeque', 'Contramaestre', 'Florida'],
    'Ecuador': ['Quito', 'Guayaquil', 'Cuenca', 'Santo Domingo', 'Machala', 'Durán', 'Manta', 'Portoviejo', 'Ambato', 'Riobamba', 'Loja', 'Esmeraldas', 'Ibarra', 'Milagro', 'Quevedo', 'Latacunga', 'Tulcán', 'Babahoyo', 'Tena', 'Puyo', 'Macas', 'Nueva Loja', 'Puerto Francisco de Orellana'],
    'El Salvador': ['San Salvador', 'Santa Ana', 'San Miguel', 'Mejicanos', 'Soyapango', 'Apopa', 'Delgado', 'Ilopango', 'Nueva San Salvador', 'Cojutepeque', 'Ahuachapán', 'Usulután', 'Zacatecoluca', 'Chalatenango', 'Sensuntepeque', 'La Unión', 'Metapán', 'San Vicente', 'Chalchuapa', 'Quezaltepeque'],
    'Guatemala': ['Alta Verapaz', 'Baja Verapaz', 'Chimaltenango', 'Chiquimula', 'El Progreso', 'Escuintla', 'Guatemala', 'Huehuetenango', 'Izabal', 'Jalapa', 'Jutiapa', 'Petén', 'Quetzaltenango', 'Quiché', 'Retalhuleu', 'Sacatepéquez', 'San Marcos', 'Santa Rosa', 'Sololá', 'Suchitepéquez', 'Totonicapán', 'Zacapa'],
    'Honduras': ['Tegucigalpa', 'San Pedro Sula', 'Choloma', 'La Ceiba', 'El Progreso', 'Choluteca', 'Comayagua', 'Puerto Cortés', 'La Lima', 'Danlí', 'Siguatepeque', 'Juticalpa', 'Catacamas', 'Tocoa', 'Tela', 'Olanchito', 'Santa Rosa de Copán', 'Villanueva', 'La Paz', 'Yoro', 'El Paraíso', 'Ocotepeque', 'Gracias', 'Santa Bárbara'],
    'México': ['Ciudad de México', 'Guadalajara', 'Monterrey', 'Puebla', 'Tijuana', 'León', 'Juárez', 'Torreón', 'Querétaro', 'San Luis Potosí', 'Mérida', 'Mexicali', 'Aguascalientes', 'Cuernavaca', 'Acapulco', 'Chihuahua', 'Veracruz', 'Villahermosa', 'Cancún', 'Tampico', 'Morelia', 'Reynosa', 'Tlalnepantla', 'Chimalhuacán', 'Naucalpan', 'Saltillo', 'Xalapa', 'Toluca', 'Pachuca', 'Culiacán', 'Hermosillo', 'Oaxaca', 'Tuxtla Gutiérrez', 'Mazatlán', 'Durango', 'Colima', 'Zacatecas', 'Campeche', 'La Paz', 'Chetumal'],
    'Nicaragua': ['Managua', 'León', 'Granada', 'Masaya', 'Chinandega', 'Matagalpa', 'Estelí', 'Tipitapa', 'Jinotepe', 'Diriamba', 'Juigalpa', 'Boaco', 'Rivas', 'Nueva Guinea', 'Bluefields', 'Puerto Cabezas', 'Jinotega', 'Ocotal', 'Somoto', 'San Carlos'],
    'Panamá': ['Ciudad de Panamá', 'Colón', 'David', 'La Chorrera', 'Santiago', 'Chitré', 'Tocumen', 'Arraiján', 'Penonome', 'Las Tablas', 'Vista Alegre', 'Boquete', 'Aguadulce', 'Balboa', 'El Dorado', 'Pacora', 'San Miguelito', 'Río Abajo', 'Juan Díaz', 'Parque Lefevre'],
    'Paraguay': ['Asunción', 'Ciudad del Este', 'San Lorenzo', 'Luque', 'Capiatá', 'Lambaré', 'Fernando de la Mora', 'Limpio', 'Ñemby', 'Encarnación', 'Pedro Juan Caballero', 'Mariano Roque Alonso', 'Villa Elisa', 'San Antonio', 'Itauguá', 'Coronel Oviedo', 'Concepción', 'Villarrica', 'Caaguazú', 'Paraguarí'],
    'Perú': ['Lima', 'Arequipa', 'Trujillo', 'Chiclayo', 'Huancayo', 'Piura', 'Iquitos', 'Cusco', 'Chimbote', 'Tacna', 'Juliaca', 'Ica', 'Sullana', 'Ayacucho', 'Cajamarca', 'Pucallpa', 'Huánuco', 'Tarapoto', 'Chincha Alta', 'Callao', 'Tumbes', 'Talara', 'Huaraz', 'Puno', 'Abancay', 'Cerro de Pasco', 'Moyobamba', 'Chachapoyas', 'Huancavelica', 'Moquegua', 'Puerto Maldonado'],
    'República Dominicana': ['Santo Domingo', 'Santiago de los Caballeros', 'Santo Domingo Este', 'Santo Domingo Norte', 'San Cristóbal', 'Puerto Plata', 'La Romana', 'San Pedro de Macorís', 'San Francisco de Macorís', 'Higüey', 'Bella Vista', 'La Vega', 'Moca', 'Boca Chica', 'Bonao', 'San Juan de la Maguana', 'Baní', 'Azua', 'Mao', 'Cotuí', 'Barahona', 'Monte Cristi', 'Nagua', 'Esperanza'],
    'Uruguay': ['Montevideo', 'Salto', 'Paysandú', 'Las Piedras', 'Rivera', 'Maldonado', 'Tacuarembó', 'Melo', 'Mercedes', 'Artigas', 'Minas', 'San José de Mayo', 'Durazno', 'Florida', 'Barros Blancos', 'Ciudad de la Costa', 'Canelones', 'Fray Bentos', 'Rocha', 'San Carlos', 'Trinidad', 'Carmelo', 'Nueva Helvecia', 'Colonia del Sacramento'],
    'Venezuela': ['Caracas', 'Maracaibo', 'Valencia', 'Barquisimeto', 'Maracay', 'Ciudad Guayana', 'San Cristóbal', 'Maturín', 'Ciudad Bolívar', 'Cumana', 'Mérida', 'Barcelona', 'Turmero', 'Cabimas', 'Santa Teresa del Tuy', 'Barinas', 'Trujillo', 'Puerto La Cruz', 'Los Teques', 'Guarenas', 'Acarigua', 'Valera', 'Catia La Mar', 'El Tigre', 'Carúpano', 'Coro', 'Guanare', 'San Fernando de Apure', 'Puerto Ayacucho', 'La Asunción']
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