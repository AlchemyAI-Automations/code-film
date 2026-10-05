# Flujo Geométrico · estilo para code-films

> Geometría precisa (nodos, carriles, retículas) con acentos biomórficos (células que respiran, conductos curvos con
> partículas). Superficie clara, un color de señal. Explica procesos mostrando cómo fluyen.
> Fuente de la marca: `Marketing/brand-personal/visual-language.md`.

## 1. Esencia y lo que no es

- Diagramas de nodo y conexión sobre blanco, con conductos curvos por los que viajan partículas (la firma).
- Células biomórficas que agrupan y "encapsulan" lo que ya existe.
- Pantallas (terminal, código) oscuras o en mono, como prueba concreta dentro del diagrama.
- No es keynote oscuro con glow, no es infografía isométrica de agencia, no es tipografía cinética que rebota.

## 2. Materiales y render

- Canvas 2D. Mundo por niveles con zoom de escala (K = 6): cada nivel vive en sus coordenadas y se dibuja con su escala.
- Grosores en px de pantalla (`px()`), no del mundo. Etiquetas del mundo se desvanecen si quedan gigantes.
- Retícula de puntos tenue que acompaña el zoom. Sin grano, sin sombras, sin gradientes decorativos.
- Paneles blancos difusos (`veil`) detrás del HUD y del texto inferior: el mundo pasa por debajo sin chocar.

## 3. Color (taxonomía, no decoración)

| Color | Significa |
|---|---|
| `#FFFFFF` fondo, `#0E1A18`/`#1E2C29` texto | lienzo y lectura |
| `#0aad98` primario | lo que dura, el resultado, los conductos, la regla propia |
| `#3DD4BE` teal claro | activo, en curso (partículas, pulsos) |
| `#FF6B4A` coral | tensión, lo que se descarta. Máximo una vez por pantalla |
| `#96a1a0` gris | legado, ruido, estado "roto" (todo el mundo se apaga hacia este gris) |
| `#EAF2EF`, `#DCE6E2`, `#D3DDD9` | superficies, puntos, líneas guía |

## 4. Tipografía

- Claims: Clash Display 600 (tracking -1 px, word-spacing 3 px). 84 a 96 px en ganchos, 58 px en texto inferior.
- UI y píldoras: Satoshi 500, 22 px. Código, kickers y etiquetas: JetBrains Mono 15 a 22 px.
- Texto alineado a la izquierda, entra por clip desde la línea base y sale hacia arriba. Nunca fade, nunca rebote.
- Licencias: Clash y Satoshi (ITF Free Font License, Fontshare), JetBrains Mono (OFL). Las fuentes viajan en `fonts/`.

## 5. Movimiento (4 verbos)

- **Dibujar**: un conducto se traza (0.6 s, ease out). **Fluir**: partículas lo recorren (velocidad integrada, se pueden frenar).
- **Morfear**: células que respiran; inestables en estado roto. **Escalonar**: apariciones con 60 a 120 ms entre sí.
- Curvas: ease out en entradas, ease in en salidas, ease in out (eio) en cámara. Sin overshoot salvo el corte (back).

## 6. Cámara

| Movimiento | Expresa | Sirve para |
|---|---|---|
| Alejamiento por niveles | ganar palanca, ver el sistema | escalas, abstracción, "subir" |
| Push-in hasta un detalle | volver a lo concreto | eco final, "bajar", la prueba |
| Fijo con pausa | leer, entender | después de cada aterrizaje |
| Punch-in + temblor corto | ruptura | el giro |
| Deriva lenta hacia afuera | perder control | estado roto |

## 7. Sonido

Pulso grave + hats suaves en el ascenso, bajo que sube un grado por nivel, pad menor que pasa a mayor en la
resolución, silencio en el corte, dron inestable en el estado roto. Foley seco: teclas, ticks, pops afinados, whoosh.

## 8. Movimientos nativos

- **Encapsular**: una célula se cierra alrededor de lo que existe y lo vuelve un nodo del nivel siguiente.
  *Sirve para*: abstracción, módulos, "esto ahora es una pieza de algo mayor".
- **Corte de entendimiento**: un cuchillo coral corta el conducto que une niveles; el mundo se apaga y deja de fluir.
  *Sirve para*: riesgo, deuda técnica, dependencia rota.
- **Reconexión**: el conducto se redibuja en verde y una partícula lo recorre de punta a punta.
  *Sirve para*: la regla propia, la solución.
- **El agente reescribe**: la misma línea del inicio, ahora escrita por un cursor verde etiquetado "agente".
  *Sirve para*: cierres sobre delegación y cambio de rol.
- **Escalera HUD**: mapa de niveles a la izquierda con marcador "tú" que sigue a la cámara; medidores a la derecha.

## 9. Fallas del medio (y su arreglo)

Ver `technique.md` → "Problemas ya resueltos". Las más comunes: elementos que entran gigantes y chocan con el HUD,
relleno de una célula cubriendo la pantalla cuando la cámara está "adentro", etiquetas enormes en los zooms.

## 10. Motor

`template/kit.js`: `conduit`, `blob`, `wrap`, `pop`, `label`, `stext`, `grid`, `veil`, `col` (con estado gris),
`loadTimeline` y `at`. Película de referencia: `nivel-operativo-v2/film.js` (niveles L0 a L5 y HUD).

## 11. Espacio de variación

Se decide por película: qué representan los niveles o nodos, la estructura, el gancho, el eco, qué se rompe.
Estructuras: zoom de escala (subir/bajar), proceso que se construye pieza por pieza, antes/después dividido.
Ganchos: una línea de código, una cifra, una frase atribuida. Ecos: la misma imagen transformada, el mapa completo,
una sola palabra.
