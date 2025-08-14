Manual de Uso – Script water.py 

Descripción: 
water.py es una herramienta en Python 3 para aplicar marcas de agua visibles y personalizadas sobre documentos PDF e imágenes (JPG, PNG, WEBP, TIFF, BMP). Está pensada para proteger copias de DNI, pasaportes u otros documentos sensibles, añadiendo datos como destinatario, propósito, fecha, hash SHA-256 del original y texto de advertencia. 

 

Instalación: 

Requiere Python 3.8+ y las librerías: 

pip install pymupdf pillow 

Uso: 

python3 water2.py -i dni_ficticio.png -o dni_marcado.png 

<img width="824" height="261" alt="imagen" src="https://github.com/user-attachments/assets/8c37f25a-aaf4-4f8d-8429-7193d99439f9" />

 

Consejos de seguridad: 

- Marca tanto anverso como reverso en documentos de identidad. 
- Incluye siempre propósito y destinatario. 
- El hash SHA-256 insertado permite trazar la procedencia. 

Ejemplos visuales: 

 

Antes 
<img width="944" height="599" alt="imagen" src="https://github.com/user-attachments/assets/616846e3-ff87-4ff2-b72a-98a0edad2086" />

 

 

Despues 

 <img width="967" height="641" alt="imagen" src="https://github.com/user-attachments/assets/75412669-6fc5-4473-999f-f9d13ea24a77" />


 
