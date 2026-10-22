# Examen de medio curso — Arquitectura de Software

**Universidad Nacional Agraria de la Selva — Facultad de Ingeniería en Informática y Sistemas**  
**Grupo A | Fecha indicada: 19 de octubre de 2026 | Duración: 2 horas**

> **Nota de transcripción:** este archivo transcribe el enunciado compartido durante la conversación. Se ha organizado en Markdown para facilitar su lectura por el agente. No incluye soluciones ni decisiones de diseño. Si existiera alguna discrepancia con el examen original, prevalece el documento del docente.

## 1. Descripción del caso

Ha sido contratado por ABC Software Corp, una empresa mediana que comercializa abarrotes y mercadería al por mayor y menor. Tienen un software operativo básico que cumple con lo justo y necesario para registrar el día a día del almacén (controlan fichas sencillas con campos como fecha, ingreso, salida, producto y un número de documento interno bastante informal).

El problema grave es que la SUNAT, mediante la **RS N° 097-2012, RS N° 234-2006** y las normativas modernas de masificación de comprobantes electrónicos, les exige llevar registros formales y **emitir** comprobantes legales estructurados bajo el estándar internacional **UBL (Universal Business Language)**, puede estudiar el estándar en la web de OASIS. El sistema actual es vacío por todos lados: no valida RUCs, no calcula correctamente los impuestos (IGV, ISC, ICBPER, etc), no genera XMLs firmados digitalmente y menos se comunica con un Operador de Servicios Electrónicos (OSE) o directamente con la SUNAT.

Tu misión como líder del equipo de desarrollo es no ponerte a codificar a lo que salga, sino mediante la metodología **Spec-First** primero definir las reglas, contratos de datos, validaciones y contratos de interfaz antes de escribir una sola línea de lógica de negocio, estudiando el archivo **UBL-Invoice-2.1.xsd**, pero deberás estudiar todas las reglas antes, apoyándote de AI.

## 2. Alcance Técnico y Restricciones Arquitectónicas

La gerencia ha puesto sobre la mesa las siguientes condiciones técnicas inevitables:

- **Legado y Migración de Datos:** Toda la información histórica del software básico de mercadería (fecha, ingreso, salida, producto, nro_documento) debe acoplarse y mapearse limpiamente hacia las nuevas entidades del sistema sin perder trazabilidad por lo que el sistema debe manejar migración de datos.
- **Normativa Tributaria Peruana:** Se deberá dar estricto cumplimiento de los requerimientos de la SUNAT (catálogos de tipos de documentos, afectación al IGV, códigos de moneda, series, correlativos y validaciones de emisión), un punto clave aquí es el catálogo 8 de SUNAT.
- **Arquitectura Base y Futura:** El software debe construirse inicialmente bajo una arquitectura monolítica limpia utilizando el patrón MVC (Modelo-Vista-Controlador). Sin embargo, el diseño debe desacoplarse de tal forma que permita una fácil migración a futuro hacia una Arquitectura Hexagonal o Clean Architecture, preparándose para escalar a microservicios cuando la empresa crezca, este detalle debe verse claramente en los specs.
- **Distribución y Multiplataforma:** Por ahora, la aplicación debe ser capaz de correr de manera nativa en los entornos Windows como en dispositivos Android, y debe empaquetarse obligatoriamente en un formato de instalación amigable (instalador MSI para entornos de escritorio o un APK para distribuciones Android).

## 3. Descubriendo los Casos de Uso

La gerencia desea que detalle los casos posibles, revisando opiniones de usuarios de facturación electrónica, por lo que puede revisar otros softwares en línea como es el caso de Nubefact, donde podría crearse un usuario DEMO.

## 4. Entregable Esperado

Como entregable de la primera fase (**Spec-First**), **esqueleto de especificaciones técnicas**, el cual debe contener:

- El Modelo de Dominio y Contratos (DTOs / Schemas).
- Diagramas de Arquitectura MVC con visión a Hexagonal.
- Especificación de Endpoints / Servicios (Contratos API).
- Matriz de Trazabilidad Normativa con cruces entre datos SUNAT y datos UBL.
