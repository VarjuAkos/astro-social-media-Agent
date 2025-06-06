Tesztfeladat – AI Social Media Agent
A lenti tesztfeladat kapcsán írd meg, hogy valósítanád meg, mire figyelnél és mi lenne a
végeredménye. Egy doksiban küldd el a végeredményt. Ha van olyan rész amit ténylegesen meg
építesz és megosztod, azt küldd el a kísérő levélben.

Cél
Tervezz és valósíts meg egy mini‐agentet, amely egyetlen marketingüzenet alapján
automatikusan több platformra (Facebook, Instagram, LinkedIn, X) optimalizált posztokat
generál.

Bemenet
● kampányüzenet (1‐2 mondat)
● célközönség (rövid leírás, pl. „25‐35 éves hobbigamerek”)
● hangnem (pl. „baráti”, „szakmai”, „humoros”)
● opcionálisan emojik használata (igen/nem)

Kimenet
json
CopyEdit
{
"facebook": "<szöveg + ajánlott hashtagek>",
"instagram": "<szöveg + hashtagek + 2 javasolt képötlet>",
"linkedin": "<szöveg>",
"x": "<szöveg + hashtagek>"
}

Kötelező funkcionalitás
1. Platform‐specifikus hossz‐ és stíluskorlátok betartása.

2. Variálás: legalább két kreatív átfogalmazás egy platformon belül.
3. Nyelvi korrektség magyarul (angol szavakat csak indokolt esetben).
4. Egyszerű API‐hívás (CLI vagy REST) a teszteléshez.
5. Rövid README: futtatás, paraméterek, bővíthetőség.

Értékelési szempontok

Szempont Súly
Kreativitás, UX‐relevancia 30 %
Kód tisztasága, dokumentáltság 25 %
Skálázhatósági terv (pl. prompt‐pipeline,
cache)

20 %

Hibakezelés, tesztlefedettség 15 %
Futási/telepítési egyszerűség 10 %

Leadási forma
● Git‐repo vagy zip (kód + README).
● 1 példa bemenet → JSON kimenet.
● Határidő: [dátum] 23:59 (CET).

Extra pont (opcionális)
● A generált posztokhoz automatikus A/B címke a későbbi teszteléshez.
● Ütemezett posztolási javaslat (optimális időpont napi idősáv alapján).