#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Usage: ./iedata2nexus.py

Note that the raw data is included in a fold below
"""
# TODO make some unit tests to check the parsing
from __future__ import print_function
import sys

# TODO: 
# - don't conflate "doubtful" codings, since each "doubtful" subset is not
# doubtful within itself
# - but put a comment in the cognate set object saying that this set may be
# cognate with another set
# - add a view notes field and an alias field to /cognate/\d+ view

def parse():
    """
    Returns a dictionary of dictionaries keyed on [language name][meaning] with
    values a tuple of ('source_form', 'cognate_class', 'reliability')
    """
    data = {}
    confident, doubtful = make_equivalence_dicts()
    for line in raw_data:
        if line.startswith("a"):
            # header line with a meaning
            meaning_id = line[2:6].strip()
            meaning = line[6:30].strip()
        elif line.startswith("b"):
            # Cognate Class Number (for the following forms)
            cognate_class = "%s-%s" % (meaning_id, line.split()[1])
        elif line.startswith("c"):
            # Equivalence cognate classes
            cognate_class1 = "%s-%s" % (meaning_id, line.split()[1])
            kind = int(line.split()[2])
            cognate_class2 = "%s-%s" % (meaning_id, line.split()[3])
            # if kind == 2, then class2 is equivalent to class1; if kind == 3
            # the equivalence is "doubtful"
            # assert cognate_class1 > 99 and cognate_class2 > 99 
            if kind == 2:
                # a series of equivalences:
                # c     200  2  201
                # c     201  2  202
                # c     201  2  207
                # should map on to:
                # {207:200, 202:200, 201:200)
                confident[cognate_class2] = cognate_class1
        elif line.startswith(" "):
            # language data
            # A form line has a blank in column 1
            # the meaning number in columns 3-5,
            # the language number in columns 7-8,
            # the language name in columns 10-24,
            # and the form or forms in columns 26-78.
            if cognate_class.endswith("-0"):
                # uncertain
                cognate_class = ""
                reliability = "C"
            elif cognate_class.endswith("-1"):
                # uninformative, certain
                cognate_class = ""
                reliability = "A"
            else:
                # informative, certain
                reliability = "A"
                try:
                    cognate_class = confident[cognate_class]
                except KeyError:
                    pass
                assert line[:6].strip() == meaning_id
            language = line[9:24].strip().replace(" ", "_")
            source_form = line[25:].strip()
            if source_form:
                data.setdefault(language, {})
                data[language][meaning] = (source_form, cognate_class,
                        reliability)
        else:
            raise ValueError("Don't know what to do with line: "+line)
    return data

def make_equivalence_dicts():
    doubtful = []
    equivalent = {}
    for line in raw_data:
        if line.startswith("a"):
            # header line with a meaning
            meaning_id = line[2:6].strip()
        elif line.startswith("c"):
            # Equivalence cognate classes
            cognate_class1 = "%s-%s" % (meaning_id, line.split()[1])
            kind = int(line.split()[2])
            cognate_class2 = "%s-%s" % (meaning_id, line.split()[3])
            if kind == 2:
                if cognate_class1 in equivalent:
                    cognate_class1 = equivalent[cognate_class1]
                equivalent[cognate_class2] = cognate_class1
            if kind == 3:
                if cognate_class1 in equivalent:
                    cognate_class1 =  equivalent[cognate_class1]
                # if cognate_class2 in equivalent:
                #     cognate_class2 =  equivalent[cognate_class2]
                doubtful.append((cognate_class1, cognate_class2))
    return (equivalent, doubtful)

def write_doubtful():
    confident, doubtful = make_equivalence_dicts()
    output = file("dyen_data/doubtful_identity.txt", "w")
    for line in doubtful:
        print(*line, file=output)
    return

def write_csv():
    HEADER = ["ID", "source_form", "phon_form", "notes",
                "source", "cognate_class", "reliability"]
    data = parse()
    for language in data:
        output = file("dyen_data/"+language+".csv", "w")
        print(*HEADER, sep="\t", file=output)
        for meaning in sorted(data[language]):
            source_form, cognate_class, reliability= data[language][meaning]
            print(meaning2id[meaning], source_form, "", "", "DyenDB",
                    cognate_class, reliability, sep="\t", file=output)
    return


# RAW DATA {{{ 
raw_data = """\
a 001 ALL
b                      001
  001 73 Ossetic         IUYL, IUYLDAER
  001 74 Afghan          TOL
  001 59 Gujarati        BEDHA
  001 58 Marathi         SERVE
  001 79 Wakhi           KUXT, CU, CUST
b                      002
  001 40 Lithuanian ST   VISAS
  001 39 Lithuanian O    VISAS, VISI (PL)
  001 41 Latvian         VISS
  001 92 SERBOCROATIAN P VAS
  001 54 Serbocroatian   SAV
  001 46 Slovak          VSETKO
  001 89 SLOVAK P        VSETOK
  001 42 Slovenian       CELO, VSE
  001 91 SLOVENIAN P     VES
  001 86 UKRAINIAN P     VES
  001 85 RUSSIAN P       VES
  001 51 Russian         VSE
  001 88 POLISH P        WSZYSTEK
  001 50 Polish          WSZYSCY
  001 94 BULGARIAN P     VSEKI
  001 47 Czech E         FSECKI
  001 93 MACEDONIAN P    SIOT
  001 53 Bulgarian       BSICKO
  001 45 Czech           VSE
  001 90 CZECH P         VSECHEN
  001 43 Lusatian L      WSEN
  001 44 Lusatian U      WSON
  001 87 BYELORUSSIAN P  UVES
  001 52 Macedonian      SA, SIOV-N-T
  001 48 Ukrainian       UVES'
  001 49 Byelorussian    WSE, WSE
b                      003
  001 17 Sardinian N     TOTTU
  001 09 Vlach           TUTI
  001 18 Sardinian L     TOTU
  001 15 French Creole C TUT
  001 13 French          TOUT
  001 16 French Creole D TUT
  001 14 Walloon         TOT
  001 12 Provencal       TOUT, TOUTO
  001 20 Spanish         TODO
  001 23 Catalan         TOT, TOTS
  001 10 Italian         TUTTO
  001 19 Sardinian C     TOTTU
  001 11 Ladin           TUOT
  001 08 Rumanian List   TOTI (M. PL.), TOATE (N. PL.)
  001 83 Albanian K      TUTI
  001 21 Portuguese ST   TODO
  001 22 Brazilian       TODO(TO)
b                      004
  001 38 Takitaki        ALA
  001 30 Swedish Up      ALL
  001 31 Swedish VL      AL  AL
  001 24 German ST       ALLE
  001 35 Icelandic ST    ALLIR
  001 34 Riksmal         ALLE
  001 32 Swedish List    ALL, ALLT, ALLA
  001 33 Danish          AL
  001 36 Faroese         ALLIR
  001 29 Frisian         ALLE, ALLES, ALLEGEARRE
  001 28 Flemish         ALLE, ALLES
  001 25 Penn. Dutch     OLL
  001 26 Dutch List      ALLES
  001 27 Afrikaans       AL, ALLE
  001 37 English ST      ALL
b                      005
  001 04 Welsh C         PAWB
  001 03 Welsh N         POB, CYFAN
b                      006
  001 68 Greek Mod       OLOS
  001 66 Greek ML        HOLOS
  001 70 Greek K         HOLOI
  001 67 Greek MD        HOLOI
  001 69 Greek D         HOLOI
  001 01 Irish A         UILE, GO LEIR, AR FAD
  001 02 Irish B         UILE
  001 07 Breton ST       HOLL
  001 06 Breton SE       OL
  001 05 Breton List     AN HOLL
b                      007
  001 71 Armenian Mod    BOLOR
  001 72 Armenian List   BOLOR
b                      008
  001 95 ALBANIAN        GJITH
  001 82 Albanian G      GJITH
  001 84 Albanian C      GITH
  001 80 Albanian T      GJITHE
  001 81 Albanian Top    GITHE
b                      200
c                         200  3  201
  001 76 Persian List    HAME
  001 77 Tadzik          XAMA, TAMOM
  001 75 Waziri          GHWUT, HAMAGI
b                      201
c                         200  3  201
  001 56 Singhalese      OKKAMA
b                      202
c                         202  2  203
c                         202  3  400
  001 63 Bengali         SOB
  001 65 Khaskura        SABAI
  001 64 Nepali List     SAB, SABAI, SARBA
b                      203
c                         202  2  203
c                         203  3  400
  001 61 Lahnda          SEBU, SARE
  001 62 Hindi           SEB, SARA
  001 60 Panjabi ST      SEB, SARA
b                      400
c                         202  3  400
c                         203  3  400
  001 55 Gypsy Gk        SAVORA
  001 57 Kashmiri        SORI
  001 78 Baluchi         KULL, DRUH, THEGH, THEWAGH, SARO
a 002 AND
b                      001
  002 55 Gypsy Gk        DA
  002 41 Latvian         UN
  002 56 Singhalese      SAHA
  002 08 Rumanian List   IAR
  002 79 Wakhi           ET, SE, WOZ
  002 09 Vlach           SE
  002 73 Ossetic         AEMAE
  002 31 Swedish VL      A
b                      002
  002 36 Faroese         OG
  002 33 Danish          OG
  002 32 Swedish List    OCH
  002 34 Riksmal         OG
  002 30 Swedish Up      OCH
  002 35 Icelandic ST    OG
b                      003
  002 60 Panjabi ST      TE
  002 57 Kashmiri        TA
  002 61 Lahnda          TE
b                      004
  002 62 Hindi           OR
  002 63 Bengali         AR, EBON
  002 65 Khaskura        ARU, RA
  002 64 Nepali List     AU, RA
  002 74 Afghan          AU
  002 75 Waziri          AU
b                      005
  002 76 Persian List    VA
  002 77 Tadzik          VA
  002 78 Baluchi         GUDA, DI, WA, O
b                      006
  002 04 Welsh C         A
  002 03 Welsh N         A
  002 07 Breton ST       HA, HAG
  002 06 Breton SE       HA, HAG
  002 05 Breton List     HA, HAG
  002 01 Irish A         AGUS
  002 02 Irish B         AGUS
b                      007
  002 81 Albanian Top    DHE
  002 83 Albanian K      EDHE
  002 80 Albanian T      EDHE
  002 95 ALBANIAN        ENE, NE, E
  002 82 Albanian G      ENE, NE, E
  002 84 Albanian C      E
b                      008
  002 66 Greek ML        KAI
  002 70 Greek K         KAI
  002 67 Greek MD        KAI, ME
  002 69 Greek D         KAI
  002 68 Greek Mod       KE, K, KY
b                      009
  002 24 German ST       UND
  002 37 English ST      AND
  002 38 Takitaki        NANGA, EN
  002 27 Afrikaans       EN
  002 26 Dutch List      EN
  002 28 Flemish         EN
  002 29 Frisian         EN
  002 25 Penn. Dutch     UUN
b                      010
  002 58 Marathi         ANI
  002 59 Gujarati        ANE (TATHA)
b                      011
  002 71 Armenian Mod    EW
  002 72 Armenian List   YEV
b                      012
  002 40 Lithuanian ST   IR
  002 39 Lithuanian O    IR
b                      200
c                         200  2  201
c                         200  3  202
  002 52 Macedonian      I, PA
  002 94 BULGARIAN P     I
  002 87 BYELORUSSIAN P  I
  002 90 CZECH P         I
  002 43 Lusatian L      I
  002 44 Lusatian U      I
  002 93 MACEDONIAN P    I
  002 50 Polish          I
  002 88 POLISH P        I
  002 51 Russian         I
  002 85 RUSSIAN P       I
  002 54 Serbocroatian   I
  002 92 SERBOCROATIAN P I
  002 89 SLOVAK P        I
  002 91 SLOVENIAN P     I
  002 86 UKRAINIAN P     I
  002 53 Bulgarian       I
  002 48 Ukrainian       I, J, TA
  002 49 Byelorussian    I
b                      201
c                         200  2  201
c                         201  3  202
c                         201  2  203
  002 46 Slovak          A, I
b                      202
c                         200  3  202
c                         201  3  202
  002 42 Slovenian       IN
b                      203
c                         201  2  203
  002 45 Czech           A
  002 47 Czech E         AY
b                      204
c                         204  2  205
  002 17 Sardinian N     E
  002 18 Sardinian L     E  E
  002 22 Brazilian       E
  002 21 Portuguese ST   E
  002 13 French          ET
  002 14 Walloon         ET
  002 12 Provencal       E, EME, EMAI
  002 10 Italian         E, ED
  002 19 Sardinian C     E
  002 11 Ladin           E, ED
  002 20 Spanish         Y
  002 23 Catalan         E, Y
b                      205
c                         204  2  205
c                         205  2  206
  002 15 French Creole C EPI, E
b                      206
c                         205  2  206
  002 16 French Creole D EPI
a 003 ANIMAL
b                      000
  003 09 Vlach
  003 55 Gypsy Gk
  003 79 Wakhi
  003 16 French Creole D
  003 38 Takitaki
b                      001
  003 37 English ST      ANIMAL
  003 74 Afghan          HAJVAN
  003 73 Ossetic         CAERAEGOJ, XAJUAN
  003 71 Armenian Mod    KENDANI
  003 72 Armenian List   ANASOON
  003 56 Singhalese      SATA
  003 48 Ukrainian       TVARYNA
  003 29 Frisian         BISTEGUD
  003 84 Albanian C      ANIMAX
b                      002
  003 95 ALBANIAN        SHTASA
  003 82 Albanian G      BAKTIA, SHTASA
b                      003
  003 81 Albanian Top    KAFSE
  003 83 Albanian K      KAFSE
  003 80 Albanian T      KAFSHE
b                      004
  003 05 Breton List     ANEVAL, LOEN
  003 07 Breton ST       LOEN, ANEVAL
  003 06 Breton SE       LON, ENEVAL
b                      005
  003 30 Swedish Up      DJUR
  003 31 Swedish VL      JUR
  003 27 Afrikaans       DIER
  003 26 Dutch List      DIER
  003 25 Penn. Dutch     GEDIER
  003 36 Faroese         DYRUR
  003 33 Danish          DYR
  003 32 Swedish List    DJUR
  003 34 Riksmal         DYR
  003 35 Icelandic ST    DYR
  003 24 German ST       TIER
  003 28 Flemish         DIER, BEEST
b                      006
  003 77 Tadzik          XAJVON, CONDOR
  003 76 Persian List    HEYVAN
b                      200
c                         200  2  201
  003 91 SLOVENIAN P     ZVER
  003 86 UKRAINIAN P     ZVIR
  003 94 BULGARIAN P     ZV AR
  003 87 BYELORUSSIAN P  ZVER
  003 46 Slovak          ZVER
  003 89 SLOVAK P        ZVER
  003 47 Czech E         ZVIRE
  003 92 SERBOCROATIAN P ZVER
  003 85 RUSSIAN P       ZVER
  003 43 Lusatian L      ZWERISCO
  003 44 Lusatian U      ZWERJO
  003 93 MACEDONIAN P    DZVER
  003 90 CZECH P         ZVER
  003 50 Polish          ZWIERZE
  003 88 POLISH P        ZWIERZ
  003 45 Czech           ZVIRE
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  207
  003 40 Lithuanian ST   GYVULYS, ZVERIS (WILD)
b                      202
c                         201  2  202
c                         202  2  207
  003 53 Bulgarian       ZIVOTNO
  003 42 Slovenian       ZIVALI
  003 51 Russian         ZIVOTNOE
  003 54 Serbocroatian   ZIVOTINJA
  003 68 Greek Mod       ZOO
  003 66 Greek ML        DZOON
  003 70 Greek K         DZOON
  003 67 Greek MD        DZOO
  003 69 Greek D         TO DZOO
  003 39 Lithuanian O    GYVULYS
  003 41 Latvian         DZIVNIEKS, KUSTONIS
  003 52 Macedonian      ZIVOTINA, -INKA
  003 49 Byelorussian    ZYVELA
b                      203
c                         203  2  204
  003 65 Khaskura        JANTU, PASHU
b                      204
c                         203  2  204
c                         204  3  400
  003 63 Bengali         JANOAR, JONTU
b                      400
c                         204  3  400
  003 61 Lahnda          JANWER
  003 64 Nepali List     PASU, JANAWAR
  003 57 Kashmiri        JANAWAR
  003 78 Baluchi         JANWAR, ZANWAR, SHANWAR
  003 59 Gujarati        JANWER (PRANI) JENAWER
  003 58 Marathi         PRANI (CREATURE), JENAVER (NON-HUMAN ANIMAL)
  003 62 Hindi           JANVER
  003 60 Panjabi ST      JANVER
  003 75 Waziri          DZANAWAR
b                      205
c                         205  2  206
  003 14 Walloon         BIESSE
b                      206
c                         205  2  206
c                         206  3  401
  003 15 French Creole C BET, ZANIMO
b                      401
c                         206  3  401
  003 22 Brazilian       ANIMAL
  003 21 Portuguese ST   ANIMAL
  003 12 Provencal       ANIMAU
  003 20 Spanish         ANIMAL
  003 23 Catalan         ANIMAL
  003 10 Italian         ANIMALE
  003 19 Sardinian C     ANIMALI
  003 11 Ladin           ANIMAL, ARMAINT
  003 08 Rumanian List   ANIMAL
  003 13 French          ANIMAL
  003 17 Sardinian N     ANIMALE
  003 18 Sardinian L     ANIMALE
b                      207
c                         201  2  207
c                         202  2  207
c                         207  2  208
c                         207  3  209
  003 01 Irish A         AINMHE, BEITHIDHEACH
b                      208
c                         207  2  208
c                         208  3  209
  003 02 Irish B         AINMHIDH
b                      209
c                         207  3  209
c                         208  3  209
  003 04 Welsh C         ANIFAIL
  003 03 Welsh N         ANIFAIL
a 004 ASHES
b                      001
  004 55 Gypsy Gk        PRAXORA
  004 73 Ossetic         FAENYK
  004 51 Russian         ZOLA
  004 70 Greek K         TEFRA
  004 56 Singhalese      ALU
  004 74 Afghan          IRA
  004 75 Waziri          TRA
  004 65 Khaskura        KHARANI
  004 63 Bengali         CHAI
b                      002
  004 09 Vlach           CENUSE
  004 15 French Creole C SAN
  004 14 Walloon         CINDE
  004 12 Provencal       CENDRE
  004 20 Spanish         CENIZA
  004 23 Catalan         CENDRA
  004 10 Italian         CENERE
  004 19 Sardinian C     CINIZU
  004 11 Ladin           TSCHENDRA
  004 08 Rumanian List   CENUSA
  004 16 French Creole D SAN
  004 13 French          CENDRE
  004 21 Portuguese ST   CINZA
  004 22 Brazilian       CINZA
  004 17 Sardinian N     KISINAS
  004 18 Sardinian L     CHIJNA
b                      003
  004 85 RUSSIAN P       PEPEL
  004 54 Serbocroatian   PEPEO
  004 92 SERBOCROATIAN P PEPEO
  004 46 Slovak          POPOL
  004 89 SLOVAK P        POPOL
  004 42 Slovenian       PEPJU
  004 91 SLOVENIAN P     PEPEL
  004 86 UKRAINIAN P     POPIL
  004 94 BULGARIAN P     PEPEL
  004 87 BYELORUSSIAN P  POPEL
  004 45 Czech           POPEL
  004 90 CZECH P         POPEL
  004 43 Lusatian L      POPEL
  004 44 Lusatian U      POPJEL
  004 93 MACEDONIAN P    PEPEL
  004 50 Polish          POPIOL
  004 88 POLISH P        POPIOL
  004 40 Lithuanian ST   PELENAI
  004 39 Lithuanian O    PELENAI
  004 41 Latvian         PELNI
  004 52 Macedonian      PEPEL
  004 47 Czech E         POPEL
  004 49 Byelorussian    POPEL
  004 48 Ukrainian       POPIL
  004 53 Bulgarian       PEPEL
b                      004
  004 76 Persian List    KHAKESTAR
  004 77 Tadzik          XOKISTAR
  004 64 Nepali List     KHAG, CHARO
  004 57 Kashmiri        KHAKH, SUR
b                      005
  004 07 Breton ST       LUDU
  004 06 Breton SE       LUDU
  004 05 Breton List     LUDU
  004 04 Welsh C         LLUDW
  004 03 Welsh N         LLUDW
  004 01 Irish A         LUAITH
  004 02 Irish B         LUAITH
b                      006
  004 59 Gujarati        RAKH
  004 58 Marathi         RAKH
  004 62 Hindi           RAKH
b                      007
  004 30 Swedish Up      ASKA
  004 31 Swedish VL      ASKA
  004 24 German ST       ASCHE
  004 27 Afrikaans       AS
  004 26 Dutch List      ASCH
  004 25 Penn. Dutch     ESCH
  004 28 Flemish         ASCH
  004 29 Frisian         YESKE
  004 36 Faroese         OSKA
  004 33 Danish          ASKE
  004 32 Swedish List    ASKA, STOFT
  004 34 Riksmal         ASKE
  004 35 Icelandic ST    ASKA
  004 37 English ST      ASHES
  004 38 Takitaki        ASESI
b                      008
  004 61 Lahnda          SWA
  004 60 Panjabi ST      SVA
b                      009
  004 67 Greek MD        STACHTE
  004 69 Greek D         STACHTE, STACHTES
  004 68 Greek Mod       STAKHTI
  004 66 Greek ML        STACHTE
b                      010
  004 81 Albanian Top    HI
  004 84 Albanian C      XI-RI
  004 83 Albanian K      XII
  004 80 Albanian T      HI
  004 82 Albanian G      HINI
  004 95 ALBANIAN        HINI
b                      011
  004 71 Armenian Mod    MOXIR
  004 72 Armenian List   MOGHIR
b                      100
  004 78 Baluchi         PHUR
  004 79 Wakhi           PERG
a 005 AT
b                      000
  005 76 Persian List
  005 95 ALBANIAN
  005 59 Gujarati
  005 63 Bengali
b                      001
  005 82 Albanian G      ME
  005 39 Lithuanian O    ANT
  005 84 Albanian C      TE
  005 56 Singhalese      E
  005 23 Catalan         AB, DE, PER
  005 29 Frisian         OP
  005 08 Rumanian List   LA
  005 71 Armenian Mod    HET
b                      002
  005 68 Greek Mod       SE, S
  005 66 Greek ML        SE
  005 67 Greek MD        SE, STE
  005 69 Greek D         STO, STE
  005 70 Greek K         EIS TO
b                      003
  005 80 Albanian T      NE
  005 81 Albanian Top    NE
  005 83 Albanian K      NDE
b                      100
  005 78 Baluchi         A,SAR-A
  005 74 Afghan          DE...SERA, TA NEZDE
b                      101
  005 57 Kashmiri        KANI
  005 55 Gypsy Gk        KAI
b                      102
  005 72 Armenian List   MOD
  005 73 Ossetic         (MAE - AEM)
b                      200
c                         200  2  201
c                         200  2  203
c                         200  2  204
  005 33 Danish          VED
  005 34 Riksmal         VED
  005 35 Icelandic ST    VIO
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  2  204
c                         201  2  206
  005 30 Swedish Up      AT, VID
b                      202
c                         201  2  202
c                         202  2  206
  005 37 English ST      AT
  005 31 Swedish VL      DEVE, OT  OT
  005 01 Irish A         AIG
  005 02 Irish B         AG
  005 09 Vlach           A
  005 17 Sardinian N     A
  005 18 Sardinian L     A
  005 15 French Creole C A (TIME), 0 (ZERO), A (PLACE)
  005 10 Italian         A, AD
  005 19 Sardinian C     A
  005 11 Ladin           A, AD, ADA
  005 13 French          A
  005 16 French Creole D A-, A
  005 14 Walloon         A
  005 12 Provencal       A
  005 20 Spanish         A
b                      203
c                         200  2  203
c                         201  2  203
c                         203  2  204
c                         203  2  206
c                         203  2  207
c                         203  2  212
  005 32 Swedish List    VID, PA, I
b                      204
c                         200  2  204
c                         201  2  204
c                         203  2  204
c                         204  2  205
c                         204  2  206
c                         204  2  207
c                         204  2  208
c                         204  2  210
c                         204  2  212
c                         204  2  213
c                         204  2  214
c                         204  2  215
  005 36 Faroese         VID, I, A
b                      205
c                         204  2  205
c                         205  2  208
c                         205  2  210
c                         205  2  212
c                         205  2  213
c                         205  2  214
c                         205  2  215
  005 25 Penn. Dutch     ONN
  005 24 German ST       AN
  005 53 Bulgarian       NA
b                      206
c                         201  2  206
c                         202  2  206
c                         203  2  206
c                         204  2  206
c                         206  2  207
c                         206  2  212
  005 22 Brazilian       A, NO
b                      207
c                         203  2  207
c                         204  2  207
c                         206  2  207
c                         207  2  212
  005 38 Takitaki        NA, NA SEI VO
  005 07 Breton ST       E, EN
  005 21 Portuguese ST   EM, NA
  005 06 Breton SE       E, EN
  005 05 Breton List     E, EN
  005 04 Welsh C         YN
  005 03 Welsh N         YN, WRTH
b                      208
c                         204  2  208
c                         205  2  208
c                         208  2  209
c                         208  2  210
c                         208  2  212
c                         208  2  213
c                         208  2  214
c                         208  2  215
  005 28 Flemish         TE, AEN
b                      209
c                         208  2  209
  005 27 Afrikaans       TE
  005 26 Dutch List      TE
b                      210
c                         204  2  210
c                         205  2  210
c                         208  2  210
c                         210  2  211
c                         210  2  212
c                         210  2  213
c                         210  2  214
c                         210  2  215
  005 52 Macedonian      U, NA
b                      211
c                         210  2  211
c                         211  2  212
c                         211  2  213
  005 90 CZECH P         U
  005 43 Lusatian L      WU
  005 86 UKRAINIAN P     U
  005 89 SLOVAK P        U
  005 92 SERBOCROATIAN P U
  005 50 Polish          W
  005 88 POLISH P        U
  005 51 Russian         V, U
  005 85 RUSSIAN P       U
  005 94 BULGARIAN P     U
  005 87 BYELORUSSIAN P  U
b                      212
c                         203  2  212
c                         204  2  212
c                         205  2  212
c                         206  2  212
c                         207  2  212
c                         208  2  212
c                         210  2  212
c                         211  2  212
c                         212  2  213
c                         212  2  214
c                         212  2  215
c                         212  2  217
  005 48 Ukrainian       V, BILJA, NA, PRY
b                      213
c                         204  2  213
c                         205  2  213
c                         208  2  213
c                         210  2  213
c                         211  2  213
c                         212  2  213
c                         213  2  214
c                         213  2  215
c                         213  2  216
c                         213  2  217
  005 45 Czech           U, PRI, ZA, NA, PO, PODLE, KU
b                      214
c                         204  2  214
c                         205  2  214
c                         208  2  214
c                         210  2  214
c                         212  2  214
c                         213  2  214
c                         214  2  215
c                         214  2  217
  005 47 Czech E         NA, PRI
b                      215
c                         204  2  215
c                         205  2  215
c                         208  2  215
c                         210  2  215
c                         212  2  215
c                         213  2  215
c                         214  2  215
c                         215  2  216
  005 42 Slovenian       NE, K
b                      216
c                         213  2  216
c                         215  2  216
  005 54 Serbocroatian   KOD
b                      217
c                         212  2  217
c                         213  2  217
c                         214  2  217
  005 41 Latvian         UZ, PIE
  005 40 Lithuanian ST   PRIE
  005 49 Byelorussian    PRY, KALJA, LJA
  005 91 SLOVENIAN P     PRI
  005 46 Slovak          PRI
  005 44 Lusatian U      PRI
  005 93 MACEDONIAN P    PRI
b                      218
c                         218  3  219
c                         218  3  223
c                         218  3  224
  005 61 Lahnda          UTTE
b                      219
c                         218  3  219
c                         219  2  220
c                         219  3  222
c                         219  3  224
  005 58 Marathi         -T, -VER, -I
  005 60 Panjabi ST      TE, PER
b                      220
c                         219  2  220
c                         220  2  221
c                         220  3  222
  005 62 Hindi           -ME, -PER
b                      221
c                         220  2  221
  005 65 Khaskura        MA
  005 64 Nepali List     MA
b                      222
c                         219  3  222
c                         220  3  222
c                         222  3  223
  005 75 Waziri          KSHE, PA, PERI
b                      223
c                         218  3  223
c                         222  3  223
c                         223  3  224
  005 77 Tadzik          DAR, BA
b                      224
c                         218  3  224
c                         219  3  224
c                         223  3  224
  005 79 Wakhi           TER, DU
a 006 BACK
b                      000
  006 09 Vlach           PELTAYA
  006 17 Sardinian N
  006 19 Sardinian C     SKINA
  006 46 Slovak          NAZPAT, NAZAD
  006 54 Serbocroatian   POZADI
  006 90 CZECH P         ZPATKY
  006 45 Czech           ZPATKY, NAZPET, ZPET
  006 80 Albanian T
  006 53 Bulgarian       (ADV) NAZAD
b                      001
  006 49 Byelorussian    ZAD, ADVAROT
  006 73 Ossetic         C"YLDYM, FAESONTAE
  006 71 Armenian Mod    T`IKUNK`
  006 65 Khaskura        KANDO
  006 72 Armenian List   EDEV
b                      002
  006 69 Greek D         PISO
  006 70 Greek K         HOPISO
b                      003
  006 82 Albanian G      SHPINA
  006 95 ALBANIAN        SHPINA
b                      004
  006 52 Macedonian      GRB
  006 47 Czech E         HRBET
  006 89 SLOVAK P        CHRBAT
  006 42 Slovenian       HERBET
  006 91 SLOVENIAN P     HRBET
  006 92 SERBOCROATIAN P HRBAT
  006 88 POLISH P        GRZBIET
  006 43 Lusatian L      KSEBJAT
  006 44 Lusatian U      CHRIBJET
  006 93 MACEDONIAN P    GRB
  006 94 BULGARIAN P     GRUB
  006 87 BYELORUSSIAN P  CHRYBET
b                      005
  006 86 UKRAINIAN P     SPYNA
  006 85 RUSSIAN P       SPINA
  006 51 Russian         SPINA
  006 48 Ukrainian       SPYNA,(NAZAG, OMYNATY)
b                      006
  006 77 Tadzik          PUST, TAXTAPUST
  006 61 Lahnda          PICCHE
  006 64 Nepali List     PITH
  006 57 Kashmiri        PYUTHU
  006 56 Singhalese      PASSA
  006 78 Baluchi         PHUSHT
  006 59 Gujarati        PITH, WASO
  006 60 Panjabi ST      PITTH
  006 62 Hindi           PITH
  006 63 Bengali         PIT
  006 58 Marathi         PATH
  006 76 Persian List    POSHT
b                      007
  006 04 Welsh C         CEFEN
  006 03 Welsh N         CEFN (NOUN), YN OL
  006 07 Breton ST       KEIN
  006 06 Breton SE       KEIN
  006 05 Breton List     KEIN
b                      008
  006 40 Lithuanian ST   NUGARA
  006 41 Latvian         MUGURA
b                      209
  006 68 Greek Mod       PLATI
  006 66 Greek ML        PLATE
  006 67 Greek MD        PLATE, RACHE
b                      100
  006 50 Polish          PLECY
  006 39 Lithuanian O    PECAI
b                      101
  006 74 Afghan          SA
  006 75 Waziri          SHAMZAI
b                      200
c                         200  2  201
c                         200  2  203
c                         200  2  205
  006 13 French          DOS
  006 16 French Creole D DO
  006 10 Italian         DOSSO
  006 15 French Creole C DO
  006 18 Sardinian L     DORSO
  006 12 Provencal       ESQUINO, DOS
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  2  205
  006 11 Ladin           DOSS, RAIN
b                      202
c                         201  2  202
  006 14 Walloon         RIN
b                      203
c                         200  2  203
c                         201  2  203
c                         203  2  204
c                         203  2  205
  006 21 Portuguese ST   COSTAS, DORSO
b                      204
c                         203  2  204
  006 22 Brazilian       COSTAS
b                      205
c                         200  2  205
c                         201  2  205
c                         203  2  205
c                         205  2  206
  006 20 Spanish         DORSO, ESPALDA
  006 08 Rumanian List   SPATE, DOS
b                      206
c                         205  2  206
  006 23 Catalan         ESPATLLAS, ESQUENA
b                      207
c                         207  3  208
  006 01 Irish A         DROM
  006 02 Irish B         DRUIM
b                      208
c                         207  3  208
  006 79 Wakhi           DUM, URQA
  006 55 Gypsy Gk        DUMO
b                      209
c                         209  2  210
  006 29 Frisian         RUG, RECH
  006 27 Afrikaans       RUG
  006 26 Dutch List      RUG
  006 31 Swedish VL      ROG, (BAK)
  006 24 German ST       RUCKEN
  006 34 Riksmal         RYGG
  006 32 Swedish List    RYGG
  006 28 Flemish         RUG
b                      210
c                         209  2  210
c                         210  2  211
  006 30 Swedish Up      RYGG, BAK
b                      211
c                         210  2  211
  006 35 Icelandic ST    BAK
  006 33 Danish          BAG
  006 36 Faroese         BAK, (RYGGUR)
  006 25 Penn. Dutch     BUUCKEL
  006 37 English ST      BACK
  006 38 Takitaki        BAKA
b                      212
c                         212  3  213
  006 83 Albanian K      RAXOKOKALEE
b                      213
c                         212  3  213
c                         213  3  214
  006 84 Albanian C      GHARESI, KRAX-T / KARINA
b                      214
c                         213  3  214
  006 81 Albanian Top    KURIS
a 007 BAD
b                      001
  007 48 Ukrainian       POGANYJ, LYXYJ
  007 41 Latvian         SLIKTS
  007 58 Marathi         VAIT
  007 71 Armenian Mod    VAT`
  007 49 Byelorussian    BLAGI, DRINNY
  007 55 Gypsy Gk        NASUL
  007 73 Ossetic         AEVZAER
  007 51 Russian         PLOXOJ
  007 67 Greek MD        ASKEMOS
  007 56 Singhalese      NARAKA
  007 64 Nepali List     GHATIYA
  007 79 Wakhi           SUK
  007 83 Albanian K      PALHO
  007 65 Khaskura        NARAMRO
  007 72 Armenian List   GESH
  007 08 Rumanian List   RAU
  007 10 Italian         CATTIVO
  007 60 Panjabi ST      PERA
b                      002
  007 30 Swedish Up      DALIG
  007 31 Swedish VL      DALI
  007 32 Swedish List    DALIG, USEL
  007 34 Riksmal         DARLIG
b                      003
  007 39 Lithuanian O    BLOGAS, NEGERAS
  007 40 Lithuanian ST   BLOGAS, NEGERAS
b                      004
  007 04 Welsh C         DRWG
  007 03 Welsh N         DRWG
b                      005
  007 53 Bulgarian       LOSO
  007 52 Macedonian      LOS
b                      006
  007 09 Vlach           SLAB
  007 42 Slovenian       SLABU
b                      007
  007 24 German ST       SCHLECHT
  007 26 Dutch List      SLECHT
  007 25 Penn. Dutch     SCHLECHT
  007 28 Flemish         SLECHT
  007 27 Afrikaans       SLEG
  007 38 Takitaki        OGRI, SLEKTI
b                      008
  007 07 Breton ST       FALL
  007 06 Breton SE       FALL
  007 05 Breton List     FALL, GWALL-, FALS-
b                      200
c                         200  2  201
  007 61 Lahnda          BURA
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  2  204
  007 62 Hindi           KHERAB, BURA
b                      202
c                         201  2  202
c                         202  2  203
c                         202  2  204
  007 59 Gujarati        KNERAB
  007 63 Bengali         KHARAP
b                      203
c                         201  2  203
c                         202  2  203
c                         203  2  204
c                         203  2  205
  007 78 Baluchi         GANDAGH, HARAB
b                      204
c                         201  2  204
c                         202  2  204
c                         203  2  204
c                         204  2  205
c                         204  2  206
  007 75 Waziri          BAD, KHAROP
b                      205
c                         203  2  205
c                         204  2  205
c                         205  2  206
  007 77 Tadzik          BAD, GANDA
b                      206
c                         204  2  206
c                         205  2  206
  007 76 Persian List    BAD
  007 37 English ST      BAD
  007 57 Kashmiri        MADA, AROTU, BAD
  007 74 Afghan          BAD
b                      207
c                         207  2  208
  007 46 Slovak          ZLY
  007 91 SLOVENIAN P     ZEL
  007 86 UKRAINIAN P     ZLYJ
  007 85 RUSSIAN P       ZLOJ
  007 54 Serbocroatian   ZAO
  007 92 SERBOCROATIAN P ZAO
  007 89 SLOVAK P        ZLY
  007 90 CZECH P         ZLY
  007 43 Lusatian L      ZLY
  007 44 Lusatian U      ZLY
  007 93 MACEDONIAN P    ZOL
  007 50 Polish          ZLY
  007 88 POLISH P        ZLY
  007 94 BULGARIAN P     ZUL
  007 87 BYELORUSSIAN P  ZLY
b                      208
c                         207  2  208
c                         208  2  209
  007 47 Czech E         ZLE, SPATNE
b                      209
c                         208  2  209
  007 45 Czech           SPATNY
b                      210
c                         210  2  211
  007 33 Danish          OND
b                      211
c                         210  2  211
c                         211  2  212
c                         211  2  213
c                         211  3  214
  007 35 Icelandic ST    LELEGUR, VONDUR, ILLUR
b                      212
c                         211  2  212
c                         212  3  214
  007 36 Faroese         ILLUR
b                      213
c                         211  2  213
  007 29 Frisian         BAR, ERCH, LILK
b                      214
c                         211  3  214
c                         212  3  214
  007 01 Irish A         OLC
  007 02 Irish B         OLC
b                      215
c                         215  2  216
  007 84 Albanian C      LIK
  007 81 Albanian Top    ILIK
b                      216
c                         215  2  216
c                         216  2  217
c                         216  3  218
  007 95 ALBANIAN        KEKJ, LIG
b                      217
c                         216  2  217
c                         217  3  218
  007 80 Albanian T      I KEG, E KEGE
  007 82 Albanian G      KEKJ
b                      218
c                         216  3  218
c                         217  3  218
  007 68 Greek Mod       KAKOS
  007 66 Greek ML        KAKOS
  007 70 Greek K         KAKOS
  007 69 Greek D         KAKOS
b                      219
c                         219  3  220
  007 17 Sardinian N     MALU
  007 18 Sardinian L     MALU
  007 15 French Creole C MOVE
  007 19 Sardinian C     MALU
  007 11 Ladin           MEL
  007 13 French          MAUVAIS
  007 16 French Creole D MOVE
  007 14 Walloon         MAL
  007 20 Spanish         MAL
  007 23 Catalan         MAL
  007 22 Brazilian       MAU
  007 21 Portuguese ST   MAO
b                      220
c                         219  3  220
  007 12 Provencal       MARRIT, IDO
a 008 BARK (OF A TREE)
b                      000
  008 84 Albanian C
  008 67 Greek MD
b                      001
  008 09 Vlach           FLUDHE
  008 83 Albanian K      FUDHE
  008 12 Provencal       RUSCO, GRUEIO
  008 55 Gypsy Gk        KOZA
  008 73 Ossetic         BAELASY C"AR
  008 80 Albanian T      LEVEZHGE
  008 48 Ukrainian       XYNA
  008 38 Takitaki        BOEBA
  008 06 Breton SE       KLOREN
  008 78 Baluchi         GAWAZ
  008 57 Kashmiri        DEL, TSAM
  008 41 Latvian         MIZA
  008 42 Slovenian       LUPOD DRVA
  008 81 Albanian Top    CIPE
b                      002
  008 25 Penn. Dutch     RINN
  008 24 German ST       RINDE
b                      003
  008 07 Breton ST       RUSK
  008 05 Breton List     RUSK
  008 04 Welsh C         RHISGL
  008 03 Welsh N         RHISGL
b                      004
  008 40 Lithuanian ST   MEDZIO ZIEVE
  008 39 Lithuanian O    MEDZIO ZIEVE
b                      005
  008 65 Khaskura        BOKRA
  008 64 Nepali List     BOKRO
b                      006
  008 16 French Creole D LAPO
  008 15 French Creole C LAPO BWA
  008 14 Walloon         PELOTE
b                      100
  008 71 Armenian Mod    KETEW
  008 72 Armenian List   GEGHEV
b                      200
c                         200  3  201
  008 30 Swedish Up      BARK
  008 31 Swedish VL      BARK
  008 32 Swedish List    BARK, GARVARBARK
  008 34 Riksmal         BARK
  008 35 Icelandic ST    BORKUR
  008 33 Danish          BARK
  008 36 Faroese         BORKUR
b                      201
c                         200  3  201
  008 37 English ST      BARK
b                      202
c                         202  2  203
  008 29 Frisian         BAST
  008 28 Flemish         BAST
b                      203
c                         202  2  203
c                         203  2  204
c                         203  3  205
c                         203  3  206
c                         203  3  207
  008 27 Afrikaans       BAS, BOOMSKORS
b                      204
c                         203  2  204
c                         204  3  205
c                         204  3  206
c                         204  3  207
  008 26 Dutch List      SCHORS
  008 20 Spanish         CORTEZA
  008 22 Brazilian       CORTEX, CORTICA
  008 21 Portuguese ST   CORTICA, CASCA
  008 10 Italian         SCORZA, CORTECCIA
  008 11 Ladin           SCORZA
  008 13 French          ECORCE
  008 08 Rumanian List   SCOARTA
  008 18 Sardinian L     ISCORZA
  008 23 Catalan         ESCORXZ
  008 19 Sardinian C     KROZU
  008 17 Sardinian N     ISKORTHA
  008 44 Lusatian U      SKORA
  008 43 Lusatian L      SKORA
  008 49 Byelorussian    KARA
  008 53 Bulgarian       KORA
  008 47 Czech E         KURA
  008 52 Macedonian      KORA
  008 51 Russian         KORA
  008 88 POLISH P        KORA
  008 50 Polish          KORA
  008 93 MACEDONIAN P    KORA
  008 90 CZECH P         KURA
  008 87 BYELORUSSIAN P  KARA
  008 45 Czech           KURA
  008 89 SLOVAK P        KORA
  008 94 BULGARIAN P     KORA
  008 46 Slovak          KORA
  008 92 SERBOCROATIAN P KORA
  008 85 RUSSIAN P       KORA
  008 54 Serbocroatian   KORA
  008 91 SLOVENIAN P     KORA
  008 86 UKRAINIAN P     KORA
b                      205
c                         203  3  205
c                         204  3  205
c                         205  3  206
c                         205  3  207
  008 58 Marathi         SAL
  008 61 Lahnda          CHAL
  008 59 Gujarati        CHAL
  008 63 Bengali         CHAL
  008 62 Hindi           CHAL
  008 60 Panjabi ST      CHELL
b                      206
c                         203  3  206
c                         204  3  206
c                         205  3  206
c                         206  3  207
  008 01 Irish A         COIRT
  008 02 Irish B         COIRT
b                      207
c                         203  3  207
c                         204  3  207
c                         205  3  207
c                         206  3  207
  008 82 Albanian G      ZHABA, KUJA
  008 95 ALBANIAN        ZHABA, KUJA
b                      208
c                         208  3  209
  008 69 Greek D         FLOUDA
  008 66 Greek ML        FLOUDA
  008 68 Greek Mod       FLUDHA
b                      209
c                         208  3  209
  008 70 Greek K         FLOIOS
b                      210
c                         210  3  400
  008 74 Afghan          POST
  008 79 Wakhi           DERUXTE PIST
  008 77 Tadzik          PUST, TAXTAPUST
  008 76 Persian List    PUST
b                      400
c                         210  3  400
  008 75 Waziri          PATIKAI
  008 56 Singhalese      POTTA
a 009 BECAUSE
b                      000
  009 31 Swedish VL
  009 02 Irish B
  009 75 Waziri
b                      001
  009 09 Vlach           KA
  009 91 SLOVENIAN P     KER
  009 79 Wakhi           CIZER
  009 01 Irish A         MAR, TOISC
  009 78 Baluchi         PHA HAW-AN SAUAV, PHA HAW-AN KHAN, KI
  009 74 Afghan          DZEKA CE, VALI CE
  009 08 Rumanian List   FIINDCA
  009 04 Welsh C         ACHOS
  009 03 Welsh N         OHERWYDD, AM, GAN
  009 07 Breton ST       PEOGWIR
  009 76 Persian List    CHUN
  009 71 Armenian Mod    OROVHETEW
  009 72 Armenian List   KANZI
  009 50 Polish          DLATEGO ZE
  009 41 Latvian         TAPEC KA
  009 57 Kashmiri        NEMATI
  009 56 Singhalese      NISA
b                      002
  009 25 Penn. Dutch     WEIL
  009 24 German ST       WEIL
b                      003
  009 88 POLISH P        PONIEWAZ
  009 90 CZECH P         PONEVADZ
b                      004
  009 59 Gujarati        KAREN KE
  009 63 Bengali         KARON
  009 58 Marathi         KAREN
b                      005
  009 46 Slovak          BO, LEBO
  009 89 SLOVAK P        LEBO
b                      006
  009 26 Dutch List      OMDAT
  009 29 Frisian         OMDET, OMREDENEN, TROCHDET
  009 28 Flemish         WANT, OMDAT
  009 27 Afrikaans       OMDAT, DOORDAT, OOR, WANT
b                      007
  009 40 Lithuanian ST   TODEL KAD, UZ TAI KAD
  009 39 Lithuanian O    TODEL KAD, UZTAI KAD
b                      008
  009 06 Breton SE       RAK MA
  009 05 Breton List     DRE MA, RAK MA, O VEZA MA
b                      009
  009 35 Icelandic ST    AF THVI AO
  009 36 Faroese         (AV) TI (AT)
b                      010
  009 13 French          PARCE QUE
  009 14 Walloon         PACE QUI
  009 12 Provencal       PER-CO-QUE
  009 20 Spanish         PORQUE
  009 23 Catalan         PEOQUE
  009 22 Brazilian       PORQUE
  009 21 Portuguese ST   PORQUE
  009 17 Sardinian N     PROKE
  009 11 Ladin           CAUSA CHA, PERVI CHA
  009 10 Italian         PERCHE
  009 16 French Creole D PAS, PIS
  009 15 French Creole C PIS, A KOZ, BIKOZ
b                      011
  009 38 Takitaki        BIKASI, BIKA
  009 37 English ST      BECAUSE
b                      012
  009 48 Ukrainian       CEREZ TE, TOMU SCO
  009 49 Byelorussian    TAMU, DZELJA, TAGO STO
  009 87 BYELORUSSIAN P  TAMU STO
  009 51 Russian         POTOMU CTO
  009 85 RUSSIAN P       POTOMU CTO
  009 86 UKRAINIAN P     TOMU STO
b                      013
  009 18 Sardinian L     PROITE
  009 19 Sardinian C     POITA
b                      100
  009 77 Tadzik          BAROI..., BAROI XAMIN, BINOBAR IN, AZ IN SABAB
  009 73 Ossetic         UMAEN AEMAE
b                      200
c                         200  2  201
  009 55 Gypsy Gk        EPIDHI
  009 66 Greek ML        EPEIDE
  009 70 Greek K         EPEIDE, DIOTI
b                      201
c                         200  2  201
c                         201  2  202
  009 69 Greek D         EPEIDE, GIATI
b                      202
c                         201  2  202
  009 67 Greek MD        GIATI
  009 68 Greek Mod       YATI, PU
b                      203
c                         203  2  204
  009 95 ALBANIAN        SEPSE
  009 82 Albanian G      SEPSE
  009 83 Albanian K      PSE
b                      204
c                         203  2  204
c                         204  2  205
  009 80 Albanian T      SE, SEPSE
b                      205
c                         204  2  205
  009 84 Albanian C      SE
  009 81 Albanian Top    SE
b                      206
c                         206  3  207
  009 47 Czech E         PROTO
  009 45 Czech           PROTOZE
b                      207
c                         206  3  207
  009 43 Lusatian L      PSETO
  009 44 Lusatian U      PRETOZ
b                      208
c                         208  3  209
  009 52 Macedonian      ZASTO
  009 93 MACEDONIAN P    ZASTO
  009 53 Bulgarian       ZASCOTO
  009 94 BULGARIAN P     ZASTOTO
  009 92 SERBOCROATIAN P ZATO STO
b                      209
c                         208  3  209
  009 54 Serbocroatian   ZATO
  009 42 Slovenian       ZATO
b                      210
c                         210  2  211
  009 30 Swedish Up      EMEDAN
b                      211
c                         210  2  211
c                         211  3  212
  009 32 Swedish List    EMEDAN, DARFOR ATT
b                      212
c                         211  3  212
  009 33 Danish          FORDI
  009 34 Riksmal         FORDI
b                      213
c                         213  3  214
  009 60 Panjabi ST      KYOKE
  009 62 Hindi           KYOKE
  009 61 Lahnda          KYUKE
b                      214
c                         213  3  214
  009 65 Khaskura        KINAKI
  009 64 Nepali List     KASOGARI BHANE, KINAKI
a 010 BELLY
b                      000
  010 71 Armenian Mod
b                      001
  010 86 UKRAINIAN P     CEREVO
  010 55 Gypsy Gk        GII
  010 73 Ossetic         GUYBYN
  010 53 Bulgarian       KOREM
  010 78 Baluchi         LAF
  010 57 Kashmiri        MYADA, PHORU, YED
  010 72 Armenian List   POR
b                      002
  010 07 Breton ST       KOF
  010 06 Breton SE       KOV
  010 05 Breton List     KOF
b                      003
  010 68 Greek Mod       KILYA
  010 66 Greek ML        KOILIA
  010 70 Greek K         KOILIA
  010 67 Greek MD        KOILIA
  010 69 Greek D         KOILIA
b                      004
  010 42 Slovenian       TREBUH
  010 91 SLOVENIAN P     TREBUCH
  010 94 BULGARIAN P     TURBUCH
  010 54 Serbocroatian   TRBUH
  010 92 SERBOCROATIAN P TRBUCH
b                      005
  010 81 Albanian Top    BARK
  010 84 Albanian C      BARK
  010 83 Albanian K      BARK
  010 80 Albanian T      BARK
  010 82 Albanian G      BARKU, MULLA
  010 95 ALBANIAN        BARKU, MULLA
b                      006
  010 93 MACEDONIAN P    MEV
  010 52 Macedonian      MEV, SKEMBE
b                      007
  010 40 Lithuanian ST   PILVAS
  010 39 Lithuanian O    PILVAS
b                      008
  010 77 Tadzik          SIKAM, SIKAMBA
  010 76 Persian List    SHEKAM
b                      100
  010 75 Waziri          GADOLYAI
  010 74 Afghan          NAS, GEDA, XETA
b                      101
  010 56 Singhalese      BADA
  010 79 Wakhi           DOR, WANJ, WERD
b                      200
c                         200  2  201
  010 16 French Creole D BUDE
b                      201
c                         200  2  201
c                         201  2  202
  010 15 French Creole C BUDE, VAT
  010 13 French          VENTRE
  010 22 Brazilian       VENTRE
  010 21 Portuguese ST   VENTRE
  010 14 Walloon         VINTE
  010 20 Spanish         VIENTRE
  010 23 Catalan         VENTRE
  010 10 Italian         VENTRE
  010 19 Sardinian C     BRENTI
  010 11 Ladin           VAINTER
  010 17 Sardinian N     ENTRE
  010 18 Sardinian L     BENTRE
  010 41 Latvian         VEDERS
b                      202
c                         201  2  202
c                         202  2  203
  010 12 Provencal       VENTRE, PANSO
b                      203
c                         202  2  203
  010 08 Rumanian List   PINTEC(E)
  010 09 Vlach           PENDIKE
b                      204
c                         204  2  205
  010 37 English ST      BELLY
  010 38 Takitaki        BELE
  010 04 Welsh C         BOLA
  010 03 Welsh N         BOL, BOLA
  010 01 Irish A         BOLG
  010 02 Irish B         BOLG
b                      205
c                         204  2  205
c                         205  2  206
  010 30 Swedish Up      BALG, MAGE
b                      206
c                         205  2  206
c                         206  2  207
  010 31 Swedish VL      MAGA  MAGA
  010 35 Icelandic ST    MAGI
  010 34 Riksmal         MAVE
b                      207
c                         206  2  207
c                         207  2  208
  010 32 Swedish List    BUK, MAGE
b                      208
c                         207  2  208
  010 26 Dutch List      BUIK
  010 25 Penn. Dutch     BAUCH
  010 28 Flemish         BUIK
  010 29 Frisian         BAST, BUK
  010 36 Faroese         BUKUR
  010 33 Danish          BUG
  010 24 German ST       BAUCH
  010 27 Afrikaans       BUIK, PENS
b                      209
c                         209  2  210
  010 51 Russian         ZIVOT
  010 85 RUSSIAN P       ZYVOT
  010 87 BYELORUSSIAN P  ZYVOT
  010 48 Ukrainian       SLUNOK, ZYVIT
b                      210
c                         209  2  210
c                         210  2  211
  010 49 Byelorussian    BRUXA, ZYVOT
b                      211
c                         210  2  211
  010 47 Czech E         BRUX
  010 45 Czech           BRICHO
  010 90 CZECH P         BRICHO
  010 43 Lusatian L      BRUCH
  010 44 Lusatian U      BRJUCH
  010 50 Polish          BRZUCH
  010 88 POLISH P        BRZUCH
  010 46 Slovak          BRUCHO
  010 89 SLOVAK P        BRUCHO
b                      212
c                         212  2  213
  010 61 Lahnda          PET
  010 59 Gujarati        PET
  010 60 Panjabi ST      PET
  010 62 Hindi           PET
  010 63 Bengali         PET
  010 58 Marathi         POT
b                      213
c                         212  2  213
c                         213  2  214
  010 64 Nepali List     PET, BHURI
b                      214
c                         213  2  214
  010 65 Khaskura        BHUNRI
a 011 BIG
b                      001
  011 51 Russian         BOL SOJ
  011 32 Swedish List    GROV
  011 41 Latvian         LIELS
  011 74 Afghan          LOJ
  011 56 Singhalese      LOKU
  011 79 Wakhi           LUP
b                      002
  011 60 Panjabi ST      VEDDA
  011 61 Lahnda          WEDDA
b                      003
  011 53 Bulgarian       GOLJAMO
  011 52 Macedonian      GOLEM
  011 94 BULGARIAN P     GOL AM
b                      004
  011 77 Tadzik          KALON, BUZURG
  011 76 Persian List    BOZORG
b                      005
  011 40 Lithuanian ST   DIDELIS
  011 39 Lithuanian O    DIDELIS
b                      006
  011 85 RUSSIAN P       VELIKIJ
  011 54 Serbocroatian   VELIK
  011 92 SERBOCROATIAN P VELIK
  011 46 Slovak          VEL KY
  011 89 SLOVAK P        VEL KY
  011 42 Slovenian       VELIKA
  011 91 SLOVENIAN P     VELIK
  011 86 UKRAINIAN P     VELIKYJ
  011 87 BYELORUSSIAN P  V ALIKI
  011 45 Czech           VELKY
  011 90 CZECH P         VELKY
  011 43 Lusatian L      WELIKI
  011 44 Lusatian U      WULKI
  011 93 MACEDONIAN P    VELIK
  011 50 Polish          WIELKI
  011 88 POLISH P        WIELKI
  011 48 Ukrainian       VELYKYJ, SLJAXETNYJ
  011 49 Byelorussian    VJALIKI
  011 47 Czech E         VELIKE, HRUBE
b                      007
  011 58 Marathi         MOTHA
  011 59 Gujarati        MOTU
b                      008
  011 04 Welsh C         MAWR
  011 03 Welsh N         MAWR
  011 01 Irish A         MOR
  011 02 Irish B         MOR
b                      009
  011 24 German ST       GROSS
  011 27 Afrikaans       GROOT
  011 26 Dutch List      GROOT
  011 25 Penn. Dutch     GROESZ
  011 28 Flemish         GROOT
  011 29 Frisian         GREAT
b                      010
  011 08 Rumanian List   MARE
  011 09 Vlach           MARE
b                      011
  011 38 Takitaki        BIGI, LANGA, GROFOE, GRAN, GRANDI
  011 37 English ST      BIG
b                      200
c                         200  2  201
  011 78 Baluchi         MAZAAN, MAZ EN
  011 17 Sardinian N     MANNU
  011 18 Sardinian L     MANNU
  011 19 Sardinian C     MANNU
  011 68 Greek Mod       MEGHALOS
  011 66 Greek ML        MEGALOS
  011 70 Greek K         MEGALOS
  011 67 Greek MD        MEGALOS
  011 69 Greek D         MEGALOS
  011 71 Armenian Mod    MEC
  011 72 Armenian List   MEDZ
  011 82 Albanian G      MADH
  011 84 Albanian C      I-MATH
  011 83 Albanian K      I MATH
  011 80 Albanian T      I MATH, E MADHE
  011 81 Albanian Top    I-MATH
  011 95 ALBANIAN        I MADH
b                      201
c                         200  2  201
c                         201  2  202
c                         201  3  203
  011 36 Faroese         STORUR, MIKILL
b                      202
c                         201  2  202
c                         202  3  203
  011 30 Swedish Up      STOR
  011 31 Swedish VL      STOR
  011 34 Riksmal         STOR
  011 35 Icelandic ST    STOR
  011 33 Danish          STOR
b                      203
c                         201  3  203
c                         202  3  203
  011 75 Waziri          STER
  011 73 Ossetic         YSTYR
b                      204
c                         204  2  205
  011 62 Hindi           BERA
  011 63 Bengali         BORO
  011 55 Gypsy Gk        BARO
  011 57 Kashmiri        BODU
b                      205
c                         204  2  205
c                         205  2  206
  011 64 Nepali List     THULO, BIRAT
b                      206
c                         205  2  206
  011 65 Khaskura        THULO
b                      207
c                         207  2  208
  011 12 Provencal       GROS, LARG
  011 07 Breton ST       BRAS
  011 06 Breton SE       BRAS
  011 05 Breton List     BRAS
b                      208
c                         207  2  208
c                         208  2  209
  011 16 French Creole D GWO, GWA
  011 15 French Creole C GHWA, GHO
b                      209
c                         208  2  209
  011 11 Ladin           GRAND
  011 20 Spanish         GRANDE
  011 23 Catalan         GRAN
  011 10 Italian         GRANDE
  011 13 French          GRAND
  011 14 Walloon         GRAND
  011 22 Brazilian       GRANDE
  011 21 Portuguese ST   GRANDE
a 012 BIRD
b                      001
  012 37 English ST      BIRD
  012 79 Wakhi           UNGUS
  012 56 Singhalese      KURULLA
b                      002
  012 73 Ossetic         MARG"
  012 78 Baluchi         MURGH
  012 74 Afghan          MURGE
  012 76 Persian List    MORGH
  012 75 Waziri          MARGHAI
b                      003
  012 67 Greek MD        POULI
  012 69 Greek D         POULI
  012 68 Greek Mod       PULI
  012 66 Greek ML        POULI
b                      004
  012 81 Albanian Top    ZOK
  012 80 Albanian T      ZOG
  012 83 Albanian K      ZOK
  012 84 Albanian C      ZOG
  012 82 Albanian G      SHPENDI, SHPEZA, ZOGU
  012 95 ALBANIAN        SHPENDI, ZOGU
b                      005
  012 77 Tadzik          PARRANDA
  012 61 Lahnda          PERINDA
b                      006
  012 70 Greek K         PTENON
  012 05 Breton List     EVN, LABOUS
  012 07 Breton ST       LABOUS, EVN (NE)
  012 06 Breton SE       EN
  012 04 Welsh C         ADERYN
  012 03 Welsh N         ADERYN, EDN
  012 01 Irish A         EAN
  012 02 Irish B         EAN
b                      007
  012 71 Armenian Mod    T`RC`UN
  012 72 Armenian List   TURCHUN
b                      200
c                         200  2  201
  012 16 French Creole D ZWEZO
  012 15 French Creole C ZIBYE (BIG), ZWEZO (SMALL)
  012 11 Ladin           UTSCHE
  012 10 Italian         UCCELLO
  012 12 Provencal       AUCEU
  012 23 Catalan         AUCELL, MOIXO
  012 13 French          OISEAU
  012 14 Walloon         OUHE
  012 21 Portuguese ST   AVE
  012 22 Brazilian       AVE
b                      201
c                         200  2  201
c                         201  2  202
  012 20 Spanish         AVE, PAJARO
b                      202
c                         201  2  202
  012 08 Rumanian List   PASARE
b                      203
c                         203  2  204
  012 57 Kashmiri        JANAWAR, PANKHI
  012 59 Gujarati        PENKHI, PEKSI
  012 60 Panjabi ST      PENCHI
  012 58 Marathi         PEKSI
  012 63 Bengali         PAKHI
  012 62 Hindi           PEKSI
b                      204
c                         203  2  204
c                         204  2  205
  012 65 Khaskura        CHARA, PANCHHI
b                      205
c                         204  2  205
  012 64 Nepali List     CARO
  012 55 Gypsy Gk        CIRIKLI
b                      206
c                         206  3  207
  012 38 Takitaki        FOUWLOE
  012 30 Swedish Up      FAGEL
  012 31 Swedish VL      FOGAL
  012 36 Faroese         FUGLUR
  012 33 Danish          FUGL
  012 32 Swedish List    FAGEL
  012 34 Riksmal         FUGL
  012 35 Icelandic ST    FUGL
  012 24 German ST       VOGEL
  012 26 Dutch List      VOGEL
  012 25 Penn. Dutch     FUGGEL
  012 28 Flemish         VOGEL
  012 29 Frisian         FUGEL
  012 27 Afrikaans       VOEL
b                      207
c                         206  3  207
  012 09 Vlach           PULU
  012 19 Sardinian C     PILLONI
  012 18 Sardinian L     PUZZONE
  012 17 Sardinian N     PUTHTHONE
  012 51 Russian         PTICA
  012 42 Slovenian       TICK
  012 91 SLOVENIAN P     PTICA
  012 86 UKRAINIAN P     PTACH
  012 89 SLOVAK P        VTAK
  012 46 Slovak          VTAK
  012 44 Lusatian U      PTAK
  012 93 MACEDONIAN P    PTICA
  012 50 Polish          PTAK
  012 88 POLISH P        PTAK
  012 85 RUSSIAN P       PTICA
  012 54 Serbocroatian   PTICA
  012 92 SERBOCROATIAN P PTICA
  012 94 BULGARIAN P     PTICA
  012 87 BYELORUSSIAN P  PTACH
  012 45 Czech           PTAK
  012 90 CZECH P         PTAK
  012 43 Lusatian L      PTAK
  012 52 Macedonian      PTICA
  012 53 Bulgarian       PTICA
  012 48 Ukrainian       PTAX
  012 49 Byelorussian    PTUSKA
  012 47 Czech E         FTAK
  012 40 Lithuanian ST   PAUKSTIS
  012 39 Lithuanian O    PAUKSTIS
  012 41 Latvian         PUTNS
a 013 TO BITE
b                      001
  013 03 Welsh N         BRATHU
  013 01 Irish A         GREIM DO BHAINT AS
  013 14 Walloon         HAGNI
  013 56 Singhalese      HAPANAWA
  013 57 Kashmiri        TSAPUN
  013 60 Panjabi ST      VEDDENA
  013 78 Baluchi         WARAGH, WARTHA
b                      002
  013 33 Danish          BIDE
  013 30 Swedish Up      BITA
  013 31 Swedish VL      BIT
  013 27 Afrikaans       BYT
  013 26 Dutch List      BIJTEN
  013 25 Penn. Dutch     BEISZ
  013 28 Flemish         BYTEN
  013 29 Frisian         BITE
  013 36 Faroese         BITA
  013 32 Swedish List    BITA, BITA I
  013 34 Riksmal         BITE
  013 35 Icelandic ST    BITA
  013 24 German ST       BEISSEN
  013 37 English ST      TO BITE
  013 38 Takitaki        BETI, NJAM
b                      003
  013 16 French Creole D MODE
  013 15 French Creole C MODE
  013 10 Italian         MORDERE
  013 11 Ladin           MORDER
  013 12 Provencal       MORDRE
  013 20 Spanish         MORDER
  013 13 French          MORDRE
  013 22 Brazilian       MORDER
  013 21 Portuguese ST   MORDER
b                      004
  013 82 Albanian G      KAPSHOJ
  013 81 Albanian Top    KAFSON, AOR. KAFSOVA
  013 80 Albanian T      ME KAFSHUAR
  013 95 ALBANIAN        KAPSHOJ
b                      005
  013 64 Nepali List     TOKNU
  013 65 Khaskura        TOKNU
b                      006
  013 42 Slovenian       GRIZT
  013 91 SLOVENIAN P     GRISTI
  013 50 Polish          GRYZC
  013 54 Serbocroatian   UGRISTI
  013 92 SERBOCROATIAN P GRISTI
b                      007
  013 18 Sardinian L     MOSSIGARE
  013 17 Sardinian N     MOSSIKRARE
  013 23 Catalan         MOSSEGAR, PICAR
  013 19 Sardinian C     MUSSIAI
  013 08 Rumanian List   A MUSCA
  013 09 Vlach           MYSKU
b                      008
  013 66 Greek ML        DAGKANO
  013 68 Greek Mod       DHANGO
  013 70 Greek K         DAGEANO
  013 67 Greek MD        DAGKANO
  013 69 Greek D         DAGKONO
b                      009
  013 83 Albanian K      ZEE AAJ
  013 84 Albanian C      ZE NE AC
b                      010
  013 53 Bulgarian       DA XAPE
  013 94 BULGARIAN P     CHAP A
b                      011
  013 52 Macedonian      KASA/KASNE
  013 46 Slovak          KUSNUT
  013 89 SLOVAK P        KUSAT
  013 88 POLISH P        KASAC
  013 51 Russian         KUSAT
  013 85 RUSSIAN P       KUSAT
  013 87 BYELORUSSIAN P  KUSAC
  013 45 Czech           KOUSATI
  013 90 CZECH P         KOUSATI
  013 43 Lusatian L      KUSAS
  013 44 Lusatian U      KUSAC
  013 93 MACEDONIAN P    KASAM
  013 40 Lithuanian ST   KASTI
  013 39 Lithuanian O    KASTI
  013 41 Latvian         KOST
  013 48 Ukrainian       KUSATY
  013 49 Byelorussian    KUSAC'
  013 47 Czech E         KUSAT
  013 86 UKRAINIAN P     KUSATY
b                      100
  013 62 Hindi           KHANA
  013 73 Ossetic         XAECYN
b                      101
  013 61 Lahnda          KETTEN
  013 59 Gujarati        KERERWU
b                      102
  013 63 Bengali         CIBONO
  013 58 Marathi         CAVNE
b                      103
  013 04 Welsh C         CNOI
  013 02 Irish B         COGNAIM
b                      200
c                         200  3  400
  013 75 Waziri          CHICHEL
  013 74 Afghan          CICEL
b                      400
c                         200  3  400
  013 72 Armenian List   KHATZNEL
  013 71 Armenian Mod    KCEL
b                      201
c                         201  2  202
  013 05 Breton List     KREGI (EN)
b                      202
c                         201  2  202
c                         202  2  203
c                         202  3  204
c                         202  3  401
  013 07 Breton ST       KREGIN, DANTAN
b                      203
c                         202  2  203
c                         203  3  204
c                         203  3  401
  013 06 Breton SE       DANTEIN
b                      204
c                         202  3  204
c                         203  3  204
c                         204  3  205
c                         204  3  401
  013 76 Persian List    DANDAN GEREFTAN
b                      205
c                         204  3  205
  013 77 Tadzik          GAZIDAN, GAZIDA GIRIFTAN
b                      401
c                         202  3  401
c                         203  3  401
c                         204  3  401
  013 55 Gypsy Gk        DANDALAV
  013 79 Wakhi           DENDUK DI-, GUP DI-
a 014 BLACK
b                      000
  014 29 Frisian
  014 73 Ossetic
b                      001
  014 09 Vlach           LAI
b                      002
  014 55 Gypsy Gk        KALO
  014 61 Lahnda          KALA
  014 64 Nepali List     KALO
  014 57 Kashmiri        KALA, KREHONU
  014 56 Singhalese      KALU
  014 59 Gujarati        KALU
  014 65 Khaskura        KALO
  014 60 Panjabi ST      KALA
  014 62 Hindi           KALA
  014 63 Bengali         KALO
  014 58 Marathi         KALA
b                      003
  014 34 Riksmal         SORT
  014 33 Danish          SORT
  014 30 Swedish Up      SVART
  014 31 Swedish VL      SVART
  014 36 Faroese         SVARTUR
  014 32 Swedish List    SVART
  014 35 Icelandic ST    SVARTR
  014 24 German ST       SCHWARZ
  014 27 Afrikaans       SWART
  014 26 Dutch List      ZWART
  014 25 Penn. Dutch     SCHWOTZ
  014 28 Flemish         ZWART
b                      004
  014 86 UKRAINIAN P     CORNYJ
  014 92 SERBOCROATIAN P CRN
  014 46 Slovak          CIERNY
  014 89 SLOVAK P        CIERNY
  014 42 Slovenian       CRNU
  014 91 SLOVENIAN P     CRN
  014 94 BULGARIAN P     CEREN
  014 87 BYELORUSSIAN P  CORNY
  014 45 Czech           CERNY
  014 90 CZECH P         CERNY
  014 43 Lusatian L      CARNY
  014 44 Lusatian U      CORNY
  014 93 MACEDONIAN P    CRN
  014 50 Polish          CZARNY
  014 88 POLISH P        CZARNY
  014 51 Russian         CERNYJ
  014 85 RUSSIAN P       C ORNYJ
  014 54 Serbocroatian   CRN
  014 52 Macedonian      CRN
  014 53 Bulgarian       CERNO
  014 48 Ukrainian       CORNYJ, TEMNYJ
  014 49 Byelorussian    CORNY
  014 47 Czech E         CERNE
b                      005
  014 08 Rumanian List   NEGRU
  014 19 Sardinian C     NIEDDU
  014 13 French          NOIR
  014 16 French Creole D NWE
  014 14 Walloon         NEUR
  014 12 Provencal       NEGRE, EGRO
  014 20 Spanish         NEGRO
  014 23 Catalan         NEGRE
  014 10 Italian         NERO
  014 22 Brazilian       NEGRO, PRETO
  014 21 Portuguese ST   NEGRO, PRETO
  014 17 Sardinian N     NIEDDU
  014 18 Sardinian L     NIEDDU
  014 15 French Creole C NWE
  014 11 Ladin           MOR, NAIR
b                      006
  014 07 Breton ST       DU
  014 06 Breton SE       DU
  014 05 Breton List     DU
  014 04 Welsh C         DU
  014 03 Welsh N         DU
  014 01 Irish A         DUBH
  014 02 Irish B         DUBH
b                      007
  014 71 Armenian Mod    SEW
  014 72 Armenian List   SEV
  014 79 Wakhi           SU, SIO
  014 77 Tadzik          SIEX
  014 78 Baluchi         SIYAH
  014 76 Persian List    SIAH
b                      008
  014 74 Afghan          TOR
  014 75 Waziri          TOR
b                      009
  014 40 Lithuanian ST   JUODAS
  014 39 Lithuanian O    JUODAS
b                      010
  014 70 Greek K         MELAS
  014 41 Latvian         MELNS
b                      011
  014 95 ALBANIAN        IZI
  014 82 Albanian G      ZI
  014 84 Albanian C      I-ZI
  014 83 Albanian K      I ZII
  014 80 Albanian T      I ZI, E ZEZE
  014 81 Albanian Top    I-ZI
b                      012
  014 37 English ST      BLACK
  014 38 Takitaki        BLAKA
b                      013
  014 67 Greek MD        MAUROS
  014 69 Greek D         MAUROS
  014 68 Greek Mod       MAVROS
  014 66 Greek ML        MAUROS
a 015 BLOOD
b                      001
  015 73 Ossetic         TUG
b                      002
  015 07 Breton ST       GWAD
  015 06 Breton SE       GOED
  015 05 Breton List     GWAD
  015 04 Welsh C         GWAED
  015 03 Welsh N         GWAED
b                      003
  015 22 Brazilian       SANGUE
  015 21 Portuguese ST   SANGUE
  015 08 Rumanian List   SINGE
  015 09 Vlach           SYNZE
  015 15 French Creole C SA
  015 13 French          SANG
  015 16 French Creole D SA
  015 14 Walloon         SONG'
  015 12 Provencal       SANG
  015 20 Spanish         SANGRE
  015 23 Catalan         SANCH
  015 10 Italian         SANGUE
  015 19 Sardinian C     SANGUINI
  015 11 Ladin           SAUNG
  015 17 Sardinian N     SAMBEBE
  015 18 Sardinian L     SAMBENE
b                      004
  015 30 Swedish Up      BLOD
  015 31 Swedish VL      BLO
  015 27 Afrikaans       BLOED
  015 26 Dutch List      BLOED
  015 25 Penn. Dutch     BLUUT
  015 28 Flemish         BLOED
  015 29 Frisian         BLOED
  015 36 Faroese         BLOD
  015 33 Danish          BLOD
  015 32 Swedish List    BLOD
  015 34 Riksmal         BLOD
  015 35 Icelandic ST    BLOO
  015 24 German ST       BLUT
  015 37 English ST      BLOOD
  015 38 Takitaki        BROEDOE
b                      005
  015 43 Lusatian L      KSEJ
  015 44 Lusatian U      KREJ
  015 93 MACEDONIAN P    KRV
  015 50 Polish          KREW
  015 88 POLISH P        KREW
  015 51 Russian         KROV
  015 85 RUSSIAN P       KROV
  015 54 Serbocroatian   KRV
  015 92 SERBOCROATIAN P KRV
  015 46 Slovak          KRV
  015 89 SLOVAK P        KRV
  015 42 Slovenian       KRI
  015 91 SLOVENIAN P     KRV
  015 86 UKRAINIAN P     KROU
  015 94 BULGARIAN P     KRUV
  015 87 BYELORUSSIAN P  KROU
  015 45 Czech           KREV
  015 90 CZECH P         KREV
  015 40 Lithuanian ST   KRAUJAS
  015 39 Lithuanian O    KRAUJAS
  015 52 Macedonian      KRV
  015 53 Bulgarian       KREV
  015 48 Ukrainian       KROV, SIMJA
  015 49 Byelorussian    KROW
  015 47 Czech E         KREF
b                      006
  015 41 Latvian         ASINIS
  015 71 Armenian Mod    ARYUN
  015 72 Armenian List   AROON
b                      007
  015 82 Albanian G      GJAKU
  015 84 Albanian C      GAK
  015 83 Albanian K      GAK
  015 80 Albanian T      GJAK
  015 95 ALBANIAN        GJAKU
  015 81 Albanian Top    GAK
b                      008
  015 60 Panjabi ST      LEU
  015 56 Singhalese      LE
  015 59 Gujarati        LOHI
b                      009
  015 66 Greek ML        HAIMA
  015 70 Greek K         HAIMA
  015 67 Greek MD        HAIMA
  015 69 Greek D         HAIMA
  015 68 Greek Mod       EMA
b                      010
  015 01 Irish A         FUIL
  015 02 Irish B         PUIL
b                      011
  015 78 Baluchi         HON
  015 79 Wakhi           WUSEN, XUN
  015 77 Tadzik          XUN
  015 76 Persian List    KHUN
b                      012
  015 61 Lahnda          XUN
  015 64 Nepali List     KHUN
b                      013
  015 74 Afghan          VINA
  015 75 Waziri          WINA
b                      014
  015 55 Gypsy Gk        RAT
  015 57 Kashmiri        RATH
b                      200
c                         200  3  201
  015 58 Marathi         REKTE
  015 62 Hindi           REKT
  015 63 Bengali         ROKTO
b                      201
c                         200  3  201
  015 65 Khaskura        RAGAT
a 016 TO BLOW (WIND)
b                      000
  016 82 Albanian G
b                      001
  016 09 Vlach           ASKUKU
  016 63 Bengali         BOOA
  016 56 Singhalese      HAMANAVA
  016 78 Baluchi         KASHAGH, KHASHTA
  016 79 Wakhi           KULUMUT, MEST
  016 74 Afghan          LEGEDEL
  016 55 Gypsy Gk        PHURDAV
  016 42 Slovenian       PIHA SAPA
  016 70 Greek K         PNEEI
  016 02 Irish B         REIDIM
  016 16 French Creole D VATE
b                      002
  016 04 Welsh C         CHWYTHU
  016 03 Welsh N         GHWYTHU
  016 01 Irish A         SEIDEADH
  016 07 Breton ST       C'HWEZHAN
  016 06 Breton SE       HUEHEIN
  016 05 Breton List     C'HOUEZA
b                      003
  016 87 BYELORUSSIAN P  DZ MUC
  016 49 Byelorussian    DZ'MUC'
b                      004
  016 95 ALBANIAN        FRYJ
  016 81 Albanian Top    FRYN, AOR. FRYVA
  016 84 Albanian C      FRIN (3 SG.)
  016 83 Albanian K      FRIIN
  016 80 Albanian T      ME FRYRE
b                      005
  016 45 Czech           FOUKATI
  016 47 Czech E         FUKAT
b                      006
  016 40 Lithuanian ST   PUSTI
  016 39 Lithuanian O    PUSTI
  016 41 Latvian         PUST
  016 68 Greek Mod       FISA(I)
  016 66 Greek ML        FUSO
  016 69 Greek D         FUSAEI
  016 67 Greek MD        FUSO
  016 72 Armenian List   PUCHEL (HOV)
  016 71 Armenian Mod    P`C`EL
  016 59 Gujarati        FUKWU, FUKAWU (INTR.)
  016 65 Khaskura        PHUKNU
  016 57 Kashmiri        PHOKUN
b                      100
  016 75 Waziri          CHALEDEL
  016 61 Lahnda          CELLEN
b                      200
c                         200  3  201
  016 58 Marathi         VAHNE
  016 64 Nepali List     BAHANU
  016 62 Hindi           BEHNA
b                      201
c                         200  3  201
c                         201  3  202
  016 77 Tadzik          VAZIDAN
  016 76 Persian List    VAZIDAN
b                      202
c                         201  3  202
  016 60 Panjabi ST      VEGNA
b                      203
c                         203  2  204
c                         203  2  206
  016 24 German ST       WEHEN
  016 28 Flemish         WAEIJEN
  016 29 Frisian         WAEIJE
  016 27 Afrikaans       WAAI
b                      204
c                         203  2  204
c                         204  2  205
c                         204  2  206
c                         204  2  208
c                         204  2  209
  016 26 Dutch List      BLAZEN, WAAIEN
b                      205
c                         204  2  205
c                         205  2  208
c                         205  2  209
  016 37 English ST      TO BLOW
  016 25 Penn. Dutch     BLOESZ
  016 38 Takitaki        BLO
  016 36 Faroese         BLASA
  016 33 Danish          BLAESE
  016 32 Swedish List    BLASA
  016 34 Riksmal         BLASE
  016 35 Icelandic ST    BLASA
  016 30 Swedish Up      BLASA
  016 31 Swedish VL      BLAS
b                      206
c                         203  2  206
c                         204  2  206
c                         206  2  207
c                         206  3  400
  016 48 Ukrainian       VIJATY, DUTY
b                      207
c                         206  2  207
c                         207  3  400
  016 91 SLOVENIAN P     DUTI
  016 86 UKRAINIAN P     DUTY
  016 90 CZECH P         DOUTI
  016 43 Lusatian L      DUS
  016 44 Lusatian U      DUC
  016 93 MACEDONIAN P    DUJAM
  016 50 Polish          DAC
  016 88 POLISH P        DAC
  016 51 Russian         DUT
  016 85 RUSSIAN P       DUT
  016 46 Slovak          DUT
  016 89 SLOVAK P        DUT
  016 92 SERBOCROATIAN P DUTI
  016 94 BULGARIAN P     DUJA
  016 52 Macedonian      DUVA
  016 54 Serbocroatian   DUVATI
b                      400
c                         206  3  400
c                         207  3  400
  016 53 Bulgarian       DA DUXA
  016 73 Ossetic         DYMYN
b                      208
c                         204  2  208
c                         205  2  208
c                         208  2  209
  016 20 Spanish         SOPLAR
  016 08 Rumanian List   A SUFLA
  016 10 Italian         SOFFIARE
  016 19 Sardinian C     SULAI
  016 14 Walloon         SOFLER, TCHESSI, HUZER, -ELER
  016 13 French          SOUFFLER (DU VENT)
  016 22 Brazilian       SOPRAR
  016 21 Portuguese ST   ASSOPRAR
  016 17 Sardinian N     SURVARE
  016 18 Sardinian L     SULARE
  016 15 French Creole C SUFLE
b                      209
c                         204  2  209
c                         205  2  209
c                         208  2  209
c                         209  2  210
  016 11 Ladin           BOFFER, SBOFFER, SOFFLER
b                      210
c                         209  2  210
  016 12 Provencal       BOUFA
  016 23 Catalan         BUFAR
a 017 BONE
b                      001
  017 55 Gypsy Gk        KOKALO
  017 83 Albanian K      KOKAU
  017 56 Singhalese      KATUWA
b                      002
  017 01 Irish A         CNAMH
  017 02 Irish B         CHAIMH
b                      003
  017 41 Latvian         KAULS
  017 40 Lithuanian ST   KAULAS
  017 39 Lithuanian O    KAULAS
b                      004
  017 67 Greek MD        KOKKALO
  017 69 Greek D         KOKKALO
  017 68 Greek Mod       KOKALO
  017 66 Greek ML        KOKKALO
b                      005
  017 24 German ST       KNOCHEN
  017 25 Penn. Dutch     GNUCHE
b                      006
  017 37 English ST      BONE
  017 38 Takitaki        BOON
  017 30 Swedish Up      BEN
  017 31 Swedish VL      BEN
  017 28 Flemish         BEEN
  017 29 Frisian         BIEN
  017 36 Faroese         BEIN
  017 33 Danish          BEN
  017 32 Swedish List    BEN
  017 34 Riksmal         BEN
  017 35 Icelandic ST    BEIN
  017 27 Afrikaans       BEEN
  017 26 Dutch List      BEEN, BOT (GRAAT)
b                      007
  017 80 Albanian T      KOSKE
  017 81 Albanian Top    KOCKE
b                      200
c                         200  3  201
c                         200  3  202
  017 84 Albanian C      AST
  017 09 Vlach           OS
  017 17 Sardinian N     OSSU
  017 18 Sardinian L     OSSU
  017 15 French Creole C ZO
  017 70 Greek K         OSTOUN
  017 13 French          OS
  017 16 French Creole D ZOS
  017 14 Walloon         OHE
  017 12 Provencal       OS, OUSSAIO
  017 20 Spanish         HUESO
  017 23 Catalan         OS
  017 10 Italian         OSSO
  017 19 Sardinian C     OSSU
  017 11 Ladin           OSS
  017 08 Rumanian List   OS
  017 71 Armenian Mod    OSKOR
  017 72 Armenian List   VOSGOR
  017 22 Brazilian       OSSO
  017 21 Portuguese ST   OSSO
  017 07 Breton ST       ASKORN
  017 06 Breton SE       ASKORN
  017 05 Breton List     ASKOURN
  017 04 Welsh C         ASGWRN
  017 03 Welsh N         ASGWRN
  017 76 Persian List    OSTOKHAN
  017 77 Tadzik          USTUXON
  017 73 Ossetic         YSTAEG
  017 79 Wakhi           YUSC, USTUXON
b                      201
c                         200  3  201
c                         201  3  202
  017 94 BULGARIAN P     KOST
  017 87 BYELORUSSIAN P  KOSC
  017 45 Czech           KOST
  017 90 CZECH P         KOST
  017 43 Lusatian L      KOSC
  017 44 Lusatian U      KOSC
  017 93 MACEDONIAN P    KOSKA
  017 50 Polish          KOSC
  017 88 POLISH P        KOSC
  017 51 Russian         KOST
  017 85 RUSSIAN P       KOST
  017 54 Serbocroatian   KOST
  017 92 SERBOCROATIAN P KOST
  017 46 Slovak          KOST
  017 89 SLOVAK P        KOST
  017 42 Slovenian       KUST
  017 91 SLOVENIAN P     KOST
  017 86 UKRAINIAN P     KISTKA
  017 52 Macedonian      KOSKA
  017 53 Bulgarian       KOST
  017 48 Ukrainian       KIST'
  017 49 Byelorussian    KOSTKA
  017 47 Czech E         KOSTY
b                      202
c                         200  3  202
c                         201  3  202
  017 82 Albanian G      RRASHTI
  017 95 ALBANIAN        RRASHTI
b                      203
c                         203  2  204
c                         203  3  206
  017 78 Baluchi         HAD
  017 59 Gujarati        HARKU
  017 65 Khaskura        HAR
  017 60 Panjabi ST      HEDDI
  017 62 Hindi           HEDDI
  017 63 Bengali         HAR
  017 58 Marathi         HAD
  017 64 Nepali List     HAR
  017 61 Lahnda          HEDDI
b                      204
c                         203  2  204
c                         204  2  205
c                         204  3  206
  017 74 Afghan          HED, HADUKAJ
b                      205
c                         204  2  205
c                         205  3  206
  017 75 Waziri          HADIKAI
b                      206
c                         203  3  206
c                         204  3  206
c                         205  3  206
  017 57 Kashmiri        ADIJU
a 018 TO BREATHE
b                      000
  018 09 Vlach
  018 55 Gypsy Gk
  018 79 Wakhi
  018 65 Khaskura
b                      001
  018 66 Greek ML        ANASAINO
  018 37 English ST      TO BREATHE
  018 38 Takitaki        BRO
  018 84 Albanian C      CATAR
  018 56 Singhalese      HUSMA/GANAWA
  018 34 Riksmal         PUSTE
  018 74 Afghan          TANAFFUS KAVEL
b                      002
  018 94 BULGARIAN P     DISAM
  018 87 BYELORUSSIAN P  DYCHAC
  018 45 Czech           DYCHATI
  018 90 CZECH P         DYCHATI
  018 43 Lusatian L      DYCHAS
  018 44 Lusatian U      DYCHAC
  018 93 MACEDONIAN P    DISAM
  018 50 Polish          ODDYCHAC
  018 88 POLISH P        DYSZEC
  018 51 Russian         DYSAT
  018 85 RUSSIAN P       DYSAT
  018 54 Serbocroatian   DISATI
  018 92 SERBOCROATIAN P DIHATI
  018 46 Slovak          DYCHAT
  018 89 SLOVAK P        DYCHAT
  018 42 Slovenian       DIHAT, DIHAS
  018 91 SLOVENIAN P     DIHATI
  018 86 UKRAINIAN P     DYCHATY
  018 52 Macedonian      DISI
  018 47 Czech E         DIXAT
  018 49 Byelorussian    DYXAC'
  018 48 Ukrainian       VIDDYXATY
  018 53 Bulgarian       DA DISA
b                      003
  018 77 Tadzik          NAFAS KASIDAN
  018 76 Persian List    NAFAS KASHIDAN
b                      004
  018 82 Albanian G      MARR FRYM
  018 95 ALBANIAN        MARR FRYM
  018 83 Albanian K      MAR FRIIME
  018 80 Albanian T      ME MANE FRYME
  018 81 Albanian Top    MAR FRYME, MORA FRYME KAM
b                      005
  018 24 German ST       ATMEN
  018 27 Afrikaans       ASEMHAAL
  018 26 Dutch List      ADEMEN
  018 25 Penn. Dutch     ODOM
  018 28 Flemish         ADEMEN
  018 29 Frisian         AMJE, AZEMJE
b                      006
  018 68 Greek Mod       ANAPNEO
  018 70 Greek K         ANAPNEO
  018 67 Greek MD        ANAPNEO
  018 69 Greek D         ANAPNEO
b                      007
  018 40 Lithuanian ST   KVEPUOTI, ALSUOTI
  018 39 Lithuanian O    KVEPUOTI
b                      008
  018 64 Nepali List     SAS PHERNU
  018 61 Lahnda          SA GHINNEN
  018 57 Kashmiri        SHAH HYONU
  018 78 Baluchi         SAH ZIRAGH
  018 59 Gujarati        SWASLEWO
  018 62 Hindi           SAS+LENA
  018 63 Bengali         SAS+PHELA
  018 58 Marathi         SVAS+GHENE
  018 60 Panjabi ST      SA+LENA
  018 75 Waziri          SAYA (BREATH)
  018 71 Armenian Mod    SNJEL
  018 72 Armenian List   SHUNCHEL
b                      100
  018 73 Ossetic         ULAEFYN
  018 41 Latvian         ELPOT
b                      200
c                         200  2  201
c                         200  2  203
  018 35 Icelandic ST    ANDA
  018 30 Swedish Up      ANDAS
  018 31 Swedish VL      AN
  018 36 Faroese         ANDA
  018 33 Danish          AANDE
  018 32 Swedish List    ANDAS, LEVA
  018 04 Welsh C         ANADLU
  018 03 Welsh N         ANADLU
  018 01 Irish A         ANAL DO THARRAINMGT
  018 02 Irish B         ANALAIM
  018 05 Breton List     ALANAT, C'HOUEZA-DIC' HOUEZA
  018 07 Breton ST       ANALAT
  018 06 Breton SE       HANALEIN
  018 23 Catalan         ALENAR
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  2  204
  018 12 Provencal       RESPIRA, ALENA
b                      202
c                         201  2  202
c                         202  2  203
c                         202  2  204
  018 18 Sardinian L     RESPIRARE
  018 10 Italian         RESPIRARE
  018 19 Sardinian C     RESPIRAI
  018 11 Ladin           RESPIRER
  018 20 Spanish         RESPIRAR
  018 13 French          RESPIRER
  018 16 French Creole D WESPIRE
  018 14 Walloon         RESPIRER
  018 22 Brazilian       RESPIRAR
  018 21 Portuguese ST   RESPIRAR
  018 17 Sardinian N     SUSPIRARE
b                      203
c                         200  2  203
c                         201  2  203
c                         202  2  203
c                         203  2  204
  018 15 French Creole C HWESPIHWE, PWA HALEN, PWA SUF
b                      204
c                         201  2  204
c                         202  2  204
c                         203  2  204
  018 08 Rumanian List   A RESPIRA, A RASUFLA
a 019 TO BURN (INTRANSITIVE)
b                      000
  019 80 Albanian T
b                      001
  019 61 Lahnda          BHA LAWEN
  019 23 Catalan         CREMAR
  019 55 Gypsy Gk        PABIAV
  019 56 Singhalese      PICCENAWA
  019 22 Brazilian       QUEIMAR
  019 79 Wakhi           THAU-
b                      002
  019 68 Greek Mod       KEO
  019 66 Greek ML        KAIGETAI (3 SG.)
  019 70 Greek K         KAIOMAI, FLEGOMAI
  019 67 Greek MD        KAIETAI (3 SG.)
  019 69 Greek D         KAIOMAI
b                      003
  019 34 Riksmal         BRENNE
  019 30 Swedish Up      BRINNA, BRANNA (TR.)
  019 31 Swedish VL      BRIN
  019 27 Afrikaans       AANBRAND
  019 26 Dutch List      BRANDEN (GLOEIEN)
  019 25 Penn. Dutch     BRENN
  019 28 Flemish         VERBRANDEN
  019 29 Frisian         BARNE, BRANNE
  019 36 Faroese         BRENNA
  019 33 Danish          BRAENDE
  019 32 Swedish List    BRANNA, FORBRANNE
  019 35 Icelandic ST    BRENNA
  019 24 German ST       BRENNEN
  019 37 English ST      TO BURN
  019 38 Takitaki        BRON
b                      004
  019 05 Breton List     LESKI, LISKI
  019 06 Breton SE       LOSKEIN
  019 04 Welsh C         LLOSGI
  019 03 Welsh N         LLOSGI
b                      100
  019 72 Armenian List   VAREL
  019 71 Armenian Mod    AYREL
b                      200
c                         200  2  201
c                         200  2  203
  019 51 Russian         GORET
  019 45 Czech           HORETI
  019 47 Czech E         HORIT
  019 53 Bulgarian       DA GORI
  019 48 Ukrainian       GORITY
  019 42 Slovenian       ZGORET
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
  019 46 Slovak          ZHORET, PALIT
b                      202
c                         201  2  202
c                         202  2  203
  019 49 Byelorussian    PALIC'
  019 86 UKRAINIAN P     PALATY
  019 89 SLOVAK P        PALIT
  019 54 Serbocroatian   PALITI
  019 50 Polish          PALIC SIE
  019 88 POLISH P        PALIC
  019 90 CZECH P         PALITI
  019 43 Lusatian L      PALIS
  019 87 BYELORUSSIAN P  PALIC
b                      203
c                         200  2  203
c                         201  2  203
c                         202  2  203
c                         203  2  204
c                         203  3  205
  019 52 Macedonian      GORI, ZEGA, PALI
b                      204
c                         203  2  204
c                         204  3  205
  019 91 SLOVENIAN P     ZGATI
  019 92 SERBOCROATIAN P ZECI
  019 85 RUSSIAN P       ZEC
  019 94 BULGARIAN P     ZEZA
  019 44 Lusatian U      ZEC
  019 93 MACEDONIAN P    ZEZAM
  019 40 Lithuanian ST   DEGTI
  019 39 Lithuanian O    DEGINTI
  019 41 Latvian         DEDZINAT
  019 95 ALBANIAN        DJEG
  019 82 Albanian G      DIGJEM (DJEG)
  019 84 Albanian C      DJEK
  019 83 Albanian K      DIGEM
  019 81 Albanian Top    DIGEM, AOR. UDOGA
  019 01 Irish A         DOGHADH
  019 02 Irish B         DOIGHIM
  019 57 Kashmiri        DAZUN
b                      205
c                         203  3  205
c                         204  3  205
  019 07 Breton ST       DEVIN
b                      206
c                         206  2  207
  019 73 Ossetic         SUDZYN
  019 74 Afghan          SVADZEDEL, SVADZEL
b                      207
c                         206  2  207
c                         207  2  208
  019 77 Tadzik          SUXTAN, SUZONDAN
b                      208
c                         207  2  208
  019 76 Persian List    SUKHTAN
b                      209
c                         209  2  210
  019 60 Panjabi ST      JELNA
  019 62 Hindi           JELNA
  019 63 Bengali         PORA, JOLA
  019 58 Marathi         JELNE
b                      210
c                         209  2  210
c                         210  2  211
c                         210  3  400
  019 65 Khaskura        BALNU, JALNU
  019 64 Nepali List     JALNU, BALNU
b                      211
c                         210  2  211
c                         211  3  400
  019 59 Gujarati        BELWU
b                      400
c                         210  3  400
c                         211  3  400
  019 75 Waziri          SWEL, BALEDEL
  019 78 Baluchi         BALAGH
b                      212
c                         212  2  213
  019 20 Spanish         ARDER
  019 09 Vlach           ARTU
  019 21 Portuguese ST   ARDER
  019 08 Rumanian List   A ARDE
b                      213
c                         212  2  213
c                         213  2  214
  019 10 Italian         ARDERE, BRUCIARE
  019 11 Ladin           ARDER, BRUSCHER
b                      214
c                         213  2  214
  019 17 Sardinian N     BRUJARE
  019 18 Sardinian L     BRUJARE
  019 15 French Creole C BURLE
  019 13 French          BRULER
  019 16 French Creole D BWILE
  019 14 Walloon         BROULER
  019 12 Provencal       BRULA
  019 19 Sardinian C     ABRUZAI
a 020 CHILD (YOUNG)
b                      001
  020 57 Kashmiri        BOKUTU, SHURU
  020 37 English ST      CHILD
  020 08 Rumanian List   COPIL
  020 83 Albanian K      DJALE
  020 09 Vlach           FICOR, FEATA (FEM.)
  020 56 Singhalese      LAMAYA, DARUVA
  020 02 Irish B         LEANBH
  020 58 Marathi         MUL
  020 01 Irish A         PAISTE
  020 38 Takitaki        PIKIEN
  020 19 Sardinian C     PIPPIU
  020 74 Afghan          TIFL
  020 75 Waziri          WORKAI
b                      002
  020 31 Swedish VL      BAN
  020 30 Swedish Up      BARN
  020 41 Latvian         BERNS
  020 36 Faroese         BARN
  020 33 Danish          BARN
  020 32 Swedish List    BARN
  020 34 Riksmal         BARN
  020 35 Icelandic ST    BARN
b                      003
  020 24 German ST       KIND
  020 27 Afrikaans       KIND
  020 26 Dutch List      KIND
  020 25 Penn. Dutch     KINNDT
  020 28 Flemish         KIND
  020 29 Frisian         KYN
b                      004
  020 86 UKRAINIAN P     DYTYNA
  020 85 RUSSIAN P       DIT A
  020 54 Serbocroatian   DETE
  020 92 SERBOCROATIAN P DETE
  020 46 Slovak          DIETA
  020 89 SLOVAK P        DIET A
  020 52 Macedonian      DETE, ROZBA
  020 53 Bulgarian       DETE
  020 48 Ukrainian       DYTYNA, DYTJA
  020 49 Byelorussian    DZICE
  020 47 Czech E         DYITYE
  020 43 Lusatian L      ZESE
  020 44 Lusatian U      DZECO
  020 93 MACEDONIAN P    DETE
  020 50 Polish          DZIECKO
  020 88 POLISH P        DZIECIE
  020 94 BULGARIAN P     DETE
  020 87 BYELORUSSIAN P  DZIC A
  020 45 Czech           DITE
  020 90 CZECH P         DITE
  020 51 Russian         REBENOK
b                      005
  020 61 Lahnda          BECCA
  020 60 Panjabi ST      BECCA
  020 62 Hindi           BECCA
  020 63 Bengali         BACCA
b                      006
  020 64 Nepali List     BALAKHA
  020 65 Khaskura        BALAKHA, KETA
b                      007
  020 04 Welsh C         PLENTYN
  020 03 Welsh N         PLENTYN
b                      008
  020 91 SLOVENIAN P     OTROK
  020 42 Slovenian       MLAT OTROK
b                      009
  020 95 ALBANIAN        FEMIJ
  020 82 Albanian G      FEMIJA
  020 84 Albanian C      FEMIJ
b                      010
  020 72 Armenian List   MANOOG
  020 71 Armenian Mod    MANUK, EREXA
b                      011
  020 68 Greek Mod       PEDHI
  020 66 Greek ML        PAIDI
  020 70 Greek K         PAIDION
  020 67 Greek MD        PAIDI, PAIDAKI
  020 69 Greek D         PAIDI
b                      012
  020 07 Breton ST       BUGEL
  020 06 Breton SE       KROEDUR (PL. BUGALE)
  020 05 Breton List     BUGEL
b                      013
  020 40 Lithuanian ST   KUDIKIS, VAIKAS
  020 39 Lithuanian O    VAIKAS
b                      014
  020 13 French          ENFANT
  020 16 French Creole D ZAFA
  020 14 Walloon         EFANT
  020 12 Provencal       ENFANT
  020 15 French Creole C ZAFA, TI MAMAY
  020 11 Ladin           INFAUNT
  020 10 Italian         FANCIULLO, BAMBINO
b                      015
  020 81 Albanian Top    FOSNE
  020 80 Albanian T      FOSHNJE
b                      016
  020 18 Sardinian L     PIZZINNU
  020 17 Sardinian N     PITHTHINNEDDU
b                      100
  020 59 Gujarati        CHOKRO
  020 78 Baluchi         CHUKH
b                      101
  020 55 Gypsy Gk        CHAVO
  020 73 Ossetic         SYVAELLON, SABI
b                      200
c                         200  2  201
  020 76 Persian List    BACHCHE
b                      201
c                         200  2  201
c                         201  2  202
  020 77 Tadzik          BACA, KUDAK, FARZAND
b                      202
c                         201  2  202
  020 79 Wakhi           ZA, ZUMAN, KUDUK
b                      203
c                         203  2  204
  020 22 Brazilian       CRIANCA
b                      204
c                         203  2  204
c                         204  3  205
  020 21 Portuguese ST   MENINO, CRIANCA
b                      205
c                         204  3  205
  020 20 Spanish         NINO
  020 23 Catalan         CRIATURA, NEN, NOY, NIN
a 021 CLOUD
b                      001
  021 55 Gypsy Gk        BULUTO
  021 38 Takitaki        BLAKA VO TAPOE, WOLKOE
  021 37 English ST      CLOUD
  021 58 Marathi         DHEG
  021 78 Baluchi         JH UR
  021 06 Breton SE       KOGUSEN
  021 41 Latvian         MAKONIS
  021 84 Albanian C      MJEGUGHA
  021 51 Russian         TUCA
  021 56 Singhalese      VALAKULA
b                      002
  021 82 Albanian G      REJA
  021 95 ALBANIAN        REJA
  021 81 Albanian Top    RE
  021 83 Albanian K      REE
  021 80 Albanian T      RE
b                      003
  021 24 German ST       WOLKE
  021 27 Afrikaans       WOLK
  021 26 Dutch List      WOLK
  021 25 Penn. Dutch     WULLG
  021 28 Flemish         WOLK
  021 29 Frisian         WOLK, WOLKE
b                      004
  021 64 Nepali List     BADAL
  021 61 Lahnda          BEDDEL
  021 59 Gujarati        WADEL
  021 65 Khaskura        BADAL, DHUNRI
  021 60 Panjabi ST      BEDDEL
  021 62 Hindi           BADEL
b                      005
  021 43 Lusatian L      KURAWA
  021 44 Lusatian U      KURJAWA
b                      006
  021 01 Irish A         NEAL, SGAMALL
  021 02 Irish B         NEALL
b                      007
  021 07 Breton ST       KOUMOULENN
  021 05 Breton List     KOUMOUL, KOC'HENN
  021 04 Welsh C         CWMWL
  021 03 Welsh N         CWMWL
b                      008
  021 20 Spanish         NUBE
  021 13 French          NUAGE
  021 16 French Creole D NWAZ
  021 14 Walloon         NULEYE
  021 23 Catalan         NUVOL
  021 10 Italian         NUVOLA, NUBE
  021 19 Sardinian C     NUI
  021 11 Ladin           NUVLA
  021 08 Rumanian List   NOR
  021 22 Brazilian       NUVEM
  021 21 Portuguese ST   NUVEM
  021 17 Sardinian N     NUGE
  021 18 Sardinian L     NUE
  021 09 Vlach           NIORI
  021 15 French Creole C NIAZ
  021 12 Provencal       NIVO, NIEU
b                      200
c                         200  3  201
  021 49 Byelorussian    XMARA
  021 86 UKRAINIAN P     CHMARA
  021 48 Ukrainian       XMARA
b                      201
c                         200  3  201
  021 50 Polish          CHMURA
b                      202
c                         202  2  203
  021 35 Icelandic ST    SKY
  021 36 Faroese         SKYGGJ
  021 33 Danish          SKY
  021 34 Riksmal         SKY
b                      203
c                         202  2  203
c                         203  2  204
  021 32 Swedish List    MOLN, SKY
b                      204
c                         203  2  204
  021 30 Swedish Up      MOLN
  021 31 Swedish VL      MARN  MARN
b                      205
c                         205  3  206
  021 85 RUSSIAN P       OBLAKO
b                      206
c                         205  3  206
  021 54 Serbocroatian   OBLAK
  021 92 SERBOCROATIAN P OBLAK
  021 46 Slovak          OBLAK
  021 89 SLOVAK P        OBLAK
  021 42 Slovenian       OBLAK
  021 91 SLOVENIAN P     OBLAK
  021 88 POLISH P        OBLOK
  021 93 MACEDONIAN P    OBLAK
  021 94 BULGARIAN P     OBLAK
  021 87 BYELORUSSIAN P  VOBLAKA
  021 45 Czech           OBLAK, MRAK
  021 90 CZECH P         OBLAK
  021 52 Macedonian      OBLAK
  021 53 Bulgarian       OBLAK
  021 47 Czech E         MRACNO, OBLOHA
b                      207
c                         207  3  208
c                         207  3  209
  021 70 Greek K         NEFOS
  021 67 Greek MD        SUNNEFO
  021 69 Greek D         SUNNEFO
  021 68 Greek Mod       SIGHNEFO
  021 66 Greek ML        SUNNEFO
  021 40 Lithuanian ST   DEBESIS
  021 39 Lithuanian O    DEBESIS
  021 77 Tadzik          ABR
  021 76 Persian List    ABR
  021 72 Armenian List   AMB
  021 71 Armenian Mod    AMP
b                      208
c                         207  3  208
c                         208  3  209
  021 74 Afghan          TORA URIADZ, XERA URIADZ
  021 75 Waziri          WERYEZ
b                      209
c                         207  3  209
c                         208  3  209
  021 57 Kashmiri        OBUR
b                      210
c                         210  3  211
  021 63 Bengali         MEG
  021 73 Ossetic         MIG"
b                      211
c                         210  3  211
  021 79 Wakhi           MOR, WETIS
a 022 COLD (WEATHER)
b                      001
  022 09 Vlach           ARKWARE
  022 72 Armenian List   BAKH
  022 71 Armenian Mod    C`URT
  022 65 Khaskura        JARO, CHISO
  022 42 Slovenian       MRAZ (MRZLO UREME)
  022 84 Albanian C      TITIM
  022 70 Greek K         PSUCHROS
  022 08 Rumanian List   RECE
  022 55 Gypsy Gk        SUDRO
  022 73 Ossetic         UAZAL
b                      002
  022 30 Swedish Up      KALL
  022 31 Swedish VL      KAL
  022 38 Takitaki        KOUROE
  022 37 English ST      COLD
  022 27 Afrikaans       KOUD
  022 26 Dutch List      KOUD
  022 25 Penn. Dutch     KELT
  022 28 Flemish         KOUD
  022 29 Frisian         KALD
  022 36 Faroese         KALDUR
  022 33 Danish          KOLD
  022 32 Swedish List    KALL
  022 34 Riksmal         KALD
  022 35 Icelandic ST    KALDR
  022 24 German ST       KALT
b                      003
  022 18 Sardinian L     FRITTU
  022 17 Sardinian N     FRITTU
  022 16 French Creole D FWET
  022 15 French Creole C FWET
  022 12 Provencal       FRE, EJO
  022 20 Spanish         FRIO
  022 23 Catalan         FRET
  022 10 Italian         FREDDO
  022 19 Sardinian C     FRIRU
  022 11 Ladin           FRAID
  022 13 French          FROID
  022 14 Walloon         FREUD
  022 22 Brazilian       FRIO
  022 21 Portuguese ST   FRIO
b                      004
  022 61 Lahnda          THEND
  022 64 Nepali List     THANDA
  022 59 Gujarati        THENDI
  022 60 Panjabi ST      THEND
  022 62 Hindi           THENDA
  022 63 Bengali         THANDA
  022 58 Marathi         THEND
b                      005
  022 40 Lithuanian ST   SALTAS
  022 39 Lithuanian O    SALTAS
  022 74 Afghan          SOR
  022 78 Baluchi         SARTH, GWAHAR
  022 79 Wakhi           SUR, SOZ
  022 77 Tadzik          XUNUK, SARD
  022 76 Persian List    SARD
  022 75 Waziri          SOR
b                      006
  022 57 Kashmiri        SHITAL, TURU
  022 56 Singhalese      SI TALA
b                      007
  022 07 Breton ST       YEN
  022 06 Breton SE       IEIN
  022 05 Breton List     YEN
b                      008
  022 81 Albanian Top    FTOTE
  022 83 Albanian K      FTOXETE
  022 80 Albanian T      I, E FTOHTE
  022 82 Albanian G      FTOFT
  022 95 ALBANIAN        FTOFT, FTOFET
b                      009
  022 67 Greek MD        KRUOS
  022 68 Greek Mod       KRIOS
  022 66 Greek ML        KRUO
  022 69 Greek D         KRUO
b                      200
c                         200  2  201
  022 49 Byelorussian    S'CJUDZENA
  022 53 Bulgarian       STUDENO
  022 46 Slovak          STUDENY
  022 94 BULGARIAN P     STUDEN
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
  022 45 Czech           CHLADNY, STUDENY
b                      202
c                         201  2  202
c                         202  2  203
  022 90 CZECH P         CHLADNY
  022 52 Macedonian      LADEN, STRUD
  022 43 Lusatian L      CHLODNY
  022 44 Lusatian U      KHLODNY
  022 93 MACEDONIAN P    CHLADEN
  022 87 BYELORUSSIAN P  CHALODNY
  022 91 SLOVENIAN P     HLADEN
  022 86 UKRAINIAN P     CHOLODNYJ
  022 89 SLOVAK P        CHLADNY
  022 88 POLISH P        CHLODNY
  022 51 Russian         XOLODNYJ
  022 85 RUSSIAN P       CHOLODNYJ
  022 54 Serbocroatian   HLADNO
  022 92 SERBOCROATIAN P HLADAN
b                      203
c                         201  2  203
c                         202  2  203
c                         203  2  204
  022 48 Ukrainian       ZYMNO, XOLODNO
b                      204
c                         203  2  204
  022 50 Polish          ZIMNY
  022 47 Czech E         ZIMA
b                      205
c                         205  3  206
  022 01 Irish A         FUAR
  022 04 Welsh C         OER
  022 03 Welsh N         OER
  022 02 Irish B         PUAR
b                      206
c                         205  3  206
  022 41 Latvian         AUKSTS
a 023 TO COME
b                      001
  023 78 Baluchi         AGH, AKHTA, ATKA
  023 63 Bengali         ASA
  023 41 Latvian         NAKT, BRAUKT
  023 73 Ossetic         CAEUYN
  023 79 Wakhi           WEZI-
b                      002
  023 71 Armenian Mod    GAL
  023 72 Armenian List   KAL
b                      003
  023 76 Persian List    AMADAN
  023 77 Tadzik          OMADAN, OMADA RASIDAN
b                      004
  023 04 Welsh C         DYFOD
  023 07 Breton ST       DONT
  023 06 Breton SE       DONET
  023 05 Breton List     DONET, DONT
  023 03 Welsh N         DOD
b                      100
  023 02 Irish B         TAR
  023 01 Irish A         TEACHT
b                      200
c                         200  3  201
  023 64 Nepali List     AUNU
  023 60 Panjabi ST      ONA
  023 65 Khaskura        ANU
  023 62 Hindi           ANA
  023 56 Singhalese      ANAWA
  023 59 Gujarati        AWEWU
  023 55 Gypsy Gk        AVAV
  023 61 Lahnda          AWEN
b                      201
c                         200  3  201
c                         201  3  202
  023 57 Kashmiri        YUNU
b                      202
c                         201  3  202
  023 58 Marathi         YENE
b                      203
c                         203  2  204
c                         203  3  205
  023 52 Macedonian      DOJDE, PRIJDE
  023 91 SLOVENIAN P     PRITI
  023 42 Slovenian       PRTDI
  023 54 Serbocroatian   DOCI
  023 92 SERBOCROATIAN P DOCI
  023 46 Slovak          PRIST
  023 43 Lusatian L      PSIS
  023 44 Lusatian U      PRINC
  023 93 MACEDONIAN P    IDAM
  023 45 Czech           PRIJITI
  023 94 BULGARIAN P     IDVAM
  023 40 Lithuanian ST   ATEITI
  023 39 Lithuanian O    ATEITI
  023 47 Czech E         PRIYIT
  023 53 Bulgarian       DA IDVA
b                      204
c                         203  2  204
c                         204  2  205
  023 48 Ukrainian       PRYXODYTY, PRYJTY
b                      205
c                         203  3  205
c                         204  2  205
  023 86 UKRAINIAN P     PRYCHODYTY
  023 85 RUSSIAN P       PRICHODIT
  023 51 Russian         PRIXODIT
  023 90 CZECH P         PRICHAZETI
  023 89 SLOVAK P        PRICHODIT
  023 50 Polish          PRZYCHODZIC
  023 88 POLISH P        PRZYCHODZIC
  023 87 BYELORUSSIAN P  PRYCHODZIC
  023 49 Byelorussian    PRYXODZIC'
b                      206
c                         206  3  207
  023 34 Riksmal         KOMME
  023 30 Swedish Up      KOMMA
  023 31 Swedish VL      KOMA  KOMA
  023 27 Afrikaans       KOM
  023 26 Dutch List      KOMEN
  023 25 Penn. Dutch     KUUM
  023 28 Flemish         KOMEN
  023 29 Frisian         KOMME
  023 36 Faroese         KOMA
  023 33 Danish          KOMME
  023 32 Swedish List    KOMMA
  023 35 Icelandic ST    KOMA
  023 24 German ST       KOMMEN
  023 37 English ST      TO COME
  023 38 Takitaki        KOM
  023 17 Sardinian N     BENNERE
  023 18 Sardinian L     BENNERE
  023 15 French Creole C VINI
  023 13 French          VENIR
  023 16 French Creole D VINI
  023 14 Walloon         V(I)NI
  023 12 Provencal       VENI
  023 20 Spanish         VENIR
  023 23 Catalan         VENIR
  023 10 Italian         VENIRE
  023 19 Sardinian C     BENNI
  023 11 Ladin           GNIR
  023 08 Rumanian List   A VENI
  023 22 Brazilian       VIR
  023 21 Portuguese ST   VIR
b                      207
c                         206  3  207
  023 09 Vlach           YINU
b                      208
c                         208  3  209
c                         208  3  210
  023 81 Albanian Top    VIN, AOR. ERDHA
  023 95 ALBANIAN        VIJ, (ERDHA=AOR.) (ARDH= INF.)
  023 82 Albanian G      VIJ ( ARDH = INF.)
  023 84 Albanian C      VIN (PRET. ARTH  3 SG. )
  023 83 Albanian K      VIN (AOR. ERDHA, PPLE. ARDHURE, IMPV. EA)
  023 80 Albanian T      ME ARDHUR
b                      209
c                         208  3  209
c                         209  3  210
  023 68 Greek Mod       ERKHOME
  023 66 Greek ML        ERCHOMAI
  023 70 Greek K         ERCHOMAI
  023 67 Greek MD        ERCHOMAI
  023 69 Greek D         ERCHOMAI
b                      210
c                         208  3  210
c                         209  3  210
  023 75 Waziri          ROTLEL
  023 74 Afghan          RATLEL
a 024 TO COUNT
b                      000
  024 55 Gypsy Gk
b                      001
  024 37 English ST      TO COUNT
  024 72 Armenian List   HASHFEL
  024 71 Armenian Mod    HAMREL, T`VEL
  024 83 Albanian K      MENDERON
  024 09 Vlach           MISUTU
  024 58 Marathi         MOJNE
  024 73 Ossetic         NYMAJYN
  024 54 Serbocroatian   RACUNATI
  024 86 UKRAINIAN P     RACHUVATY
  024 39 Lithuanian O    ROKUOTI
  024 74 Afghan          SMEREL
b                      002
  024 64 Nepali List     GANNU
  024 61 Lahnda          GINNEN
  024 57 Kashmiri        GANZARUN
  024 56 Singhalese      GANAN/KARANAWA
  024 78 Baluchi         GANNAGH, GANNITHA
  024 75 Waziri          GANREL
  024 59 Gujarati        GENEWU
  024 65 Khaskura        GANNU
  024 60 Panjabi ST      GINENA
  024 62 Hindi           GINNA
  024 63 Bengali         GONA
b                      003
  024 68 Greek Mod       METRO
  024 66 Greek ML        METRO
  024 70 Greek K         METRO
  024 67 Greek MD        METRO
  024 69 Greek D         METRAO
b                      004
  024 40 Lithuanian ST   SKAICIUOTI
  024 41 Latvian         SKAITIT
b                      005
  024 92 SERBOCROATIAN P BROJATI
  024 93 MACEDONIAN P    BROJAM
  024 53 Bulgarian       DA BROI
  024 52 Macedonian      BROI, NABROI
b                      006
  024 49 Byelorussian    LIZYC'
  024 43 Lusatian L      LICYS
  024 44 Lusatian U      LICIC
  024 87 BYELORUSSIAN P  LICYC
  024 50 Polish          LICZYC
  024 88 POLISH P        LICZYC
b                      007
  024 07 Breton ST       KONTAN
  024 06 Breton SE       KONTEIN
  024 05 Breton List     KONTA, NIVERI, JEDI
b                      008
  024 84 Albanian C      DHEMBRON
  024 95 ALBANIAN        NUMEROJ
  024 80 Albanian T      ME NEMERUAR
  024 81 Albanian Top    NEMERON, AOR. NEMEROVA
  024 82 Albanian G      NUMEROJ
b                      009
  024 47 Czech E         CITAT
  024 94 BULGARIAN P     RAZCITAM
  024 51 Russian         SCITAT
  024 85 RUSSIAN P       SCEST
  024 45 Czech           POCITATI
  024 90 CZECH P         POCITATI
  024 42 Slovenian       STET
  024 91 SLOVENIAN P     STETI
  024 46 Slovak          POCITAT
  024 89 SLOVAK P        CITAT
  024 48 Ukrainian       RAXUBATY, CYSLYTY
b                      200
c                         200  2  201
  024 24 German ST       ZAHLEN
  024 25 Penn. Dutch     ZAYL
  024 28 Flemish         TELLEN
  024 38 Takitaki        TELI
  024 29 Frisian         TELLE
  024 36 Faroese         TELJA
  024 33 Danish          TAELLE
  024 34 Riksmal         TELLE
  024 35 Icelandic ST    TELJA
b                      201
c                         200  2  201
c                         201  2  202
  024 27 Afrikaans       TEL, REKEN, AG
b                      202
c                         201  2  202
  024 30 Swedish Up      RAKNA
  024 31 Swedish VL      RAKAN
  024 32 Swedish List    RAKNA
  024 26 Dutch List      REKENEN
b                      203
c                         203  2  204
  024 08 Rumanian List   A NUMARA
  024 11 Ladin           DOMBRER, IN(N)UMBRER
b                      204
c                         203  2  204
c                         204  2  205
  024 21 Portuguese ST   CONTAR, NUMERAR
b                      205
c                         204  2  205
  024 17 Sardinian N     KONTARE
  024 18 Sardinian L     CONTARE
  024 15 French Creole C KOTE
  024 23 Catalan         CONTAR
  024 10 Italian         CONTARE
  024 19 Sardinian C     KONTAI
  024 13 French          COMPTER
  024 16 French Creole D KOTE
  024 14 Walloon         COMPTER, CONTER
  024 12 Provencal       COUMTA
  024 20 Spanish         CONTAR
  024 22 Brazilian       CONTAR
b                      206
c                         206  2  207
  024 76 Persian List    SHOMORDAN
b                      207
c                         206  2  207
c                         207  2  208
  024 77 Tadzik          XISOB, KARDAN, SUMURDAN
b                      208
c                         207  2  208
  024 79 Wakhi           ISOB TSER-
b                      209
c                         209  3  210
  024 01 Irish A         COMHAIREAMH
  024 02 Irish B         AIREA MHAIM
b                      210
c                         209  3  210
  024 04 Welsh C         RHIFO, CYFRIF
  024 03 Welsh N         CYFRIF
a 025 TO CUT
b                      001
  025 50 Polish          CIAC
  025 55 Gypsy Gk        CINAV
  025 41 Latvian         GRIEZT
  025 73 Ossetic         LYG KAENYN KAERGYN
  025 40 Lithuanian ST   PIAUTI, RIEKTI (BREAD)
  025 78 Baluchi         CHAKAGH, CHAKITHA
  025 79 Wakhi           RESED-
b                      002
  025 76 Persian List    BORIDAN
  025 77 Tadzik          BURIDAN
b                      003
  025 07 Breton ST       TROC'HAN
  025 06 Breton SE       TROHEIN
  025 05 Breton List     TROUC'HA, SKEJA
b                      004
  025 24 German ST       SCHNEIDEN
  025 27 Afrikaans       SNY, SNOEI
  025 26 Dutch List      SNIJDEN
  025 25 Penn. Dutch     SCHNEIDT
  025 28 Flemish         SNYDEN
  025 29 Frisian         SNIJE
b                      005
  025 81 Albanian Top    PRES, AOR. PREVA
  025 82 Albanian G      PRES (PRE = INF.)
  025 84 Albanian C      PRES
  025 83 Albanian K      SKLHIEN, PRES
  025 80 Albanian T      ME PRERE
  025 95 ALBANIAN        PRES
b                      006
  025 01 Irish A         GEARRADH
  025 02 Irish B         GEARRU
b                      007
  025 04 Welsh C         TORRI
  025 03 Welsh N         TORRI
b                      008
  025 72 Armenian List   GUDREL
  025 71 Armenian Mod    KTREL
b                      009
  025 70 Greek K         KOPTO
  025 68 Greek Mod       KOVO
  025 66 Greek ML        KOBO
  025 67 Greek MD        KOBO
  025 69 Greek D         KOBO
b                      010
  025 58 Marathi         KAPNE
  025 56 Singhalese      KAPANAWA
  025 59 Gujarati        KAPWU
b                      100
  025 75 Waziri          PREKREL
  025 74 Afghan          PREKAVEL
b                      200
c                         200  2  201
  025 37 English ST      TO CUT
  025 38 Takitaki        KOTI
b                      201
c                         200  2  201
c                         201  2  202
c                         201  3  203
  025 30 Swedish Up      KOTTA, SKARA
b                      202
c                         201  2  202
c                         202  3  203
  025 36 Faroese         SKERA
  025 31 Swedish VL      SARA
  025 33 Danish          SKAERE
  025 32 Swedish List    SKARA
  025 34 Riksmal         SKJAERE
  025 35 Icelandic ST    SKERA
  025 39 Lithuanian O    KIRSTI
  025 65 Khaskura        KATNU
  025 57 Kashmiri        TSATUN, KATUN
  025 61 Lahnda          KETTEN
  025 64 Nepali List     KATNU, PHARNU
  025 62 Hindi           KATNA
  025 63 Bengali         KATA
  025 20 Spanish         CORTAR
  025 22 Brazilian       CORTAR
  025 21 Portuguese ST   CORTAR
b                      203
c                         201  3  203
c                         202  3  203
  025 60 Panjabi ST      KHETTENA
b                      204
c                         204  2  205
  025 13 French          COUPER
  025 16 French Creole D KUPE
  025 12 Provencal       COUPA
  025 15 French Creole C KUPE
b                      205
c                         204  2  205
c                         205  2  206
  025 14 Walloon         COPER, TEYI
b                      206
c                         205  2  206
  025 11 Ladin           TAGLIER
  025 08 Rumanian List   A TAIA
  025 23 Catalan         TALLAR
  025 10 Italian         TAGLIARE
  025 09 Vlach           TALU
b                      207
c                         207  2  208
  025 53 Bulgarian       DA REZE
  025 48 Ukrainian       RIZATY
  025 49 Byelorussian    REZAC'
  025 47 Czech E         REZAT
  025 86 UKRAINIAN P     RIZATY
  025 94 BULGARIAN P     REZA
  025 87 BYELORUSSIAN P  REZAC
  025 45 Czech           REZATI
  025 90 CZECH P         REZATI
  025 43 Lusatian L      REZAS
  025 44 Lusatian U      REZAC
  025 93 MACEDONIAN P    REZAM
  025 92 SERBOCROATIAN P REZATI
  025 46 Slovak          REZAT
  025 89 SLOVAK P        REZAT
  025 42 Slovenian       REZAT
  025 88 POLISH P        RZEZAC
  025 51 Russian         REZAT
  025 85 RUSSIAN P       REZAT
b                      208
c                         207  2  208
c                         208  2  209
  025 52 Macedonian      PO REZE, REZE, SECE
b                      209
c                         208  2  209
  025 19 Sardinian C     SEGAI
  025 91 SLOVENIAN P     SEKATI
  025 54 Serbocroatian   SECI
  025 17 Sardinian N     SEKARE
  025 18 Sardinian L     SEGARE
a 026 DAY (NOT NIGHT)
b                      001
  026 73 Ossetic         BON
  026 55 Gypsy Gk        GYES
  026 79 Wakhi           ROR, REWOR
b                      002
  026 68 Greek Mod       MERA
  026 66 Greek ML        MERA
  026 70 Greek K         HEMERA
  026 67 Greek MD        MERA, HEMERA
  026 69 Greek D         MERA, HEMERA
b                      003
  026 60 Panjabi ST      DIN
  026 62 Hindi           DIN
  026 63 Bengali         DIN
  026 53 Bulgarian       DEN
  026 48 Ukrainian       DEN'
  026 49 Byelorussian    DZEN'
  026 47 Czech E         DENY
  026 52 Macedonian      DEN
  026 45 Czech           DEN
  026 90 CZECH P         DEN
  026 43 Lusatian L      ZEN
  026 44 Lusatian U      DZEN
  026 93 MACEDONIAN P    DEN
  026 50 Polish          DZIEN
  026 88 POLISH P        DZIEN
  026 51 Russian         DEN
  026 85 RUSSIAN P       DEN
  026 54 Serbocroatian   DAN
  026 92 SERBOCROATIAN P DAN
  026 46 Slovak          DEN
  026 89 SLOVAK P        DEN
  026 42 Slovenian       DAN
  026 91 SLOVENIAN P     DEN
  026 86 UKRAINIAN P     DEN
  026 40 Lithuanian ST   DIENA
  026 39 Lithuanian O    DIENA
  026 41 Latvian         DIENA
  026 94 BULGARIAN P     DEN
  026 87 BYELORUSSIAN P  DZEN
  026 61 Lahnda          DI
  026 64 Nepali List     DIN
  026 57 Kashmiri        DEN, DOH
  026 56 Singhalese      DAVAL
  026 59 Gujarati        DIWES
  026 58 Marathi         DIVES
  026 65 Khaskura        DIUSO
  026 07 Breton ST       DEIZ
  026 06 Breton SE       DE
  026 05 Breton List     DEIZ, DE(Z)
  026 04 Welsh C         DYDD
  026 03 Welsh N         DYDD
  026 20 Spanish         DIA
  026 23 Catalan         DIA
  026 17 Sardinian N     DIE
  026 18 Sardinian L     DIE
  026 95 ALBANIAN        DITA
  026 82 Albanian G      DITA
  026 84 Albanian C      DIT
  026 83 Albanian K      DITE
  026 80 Albanian T      DITE
  026 81 Albanian Top    DITE
  026 19 Sardinian C     DI
  026 11 Ladin           DI
  026 22 Brazilian       DIA
  026 21 Portuguese ST   DIA
  026 08 Rumanian List   ZI
  026 09 Vlach           ZUE
  026 15 French Creole C ZU
  026 13 French          JOUR
  026 16 French Creole D ZU
  026 14 Walloon         DJOU
  026 12 Provencal       JOUR
  026 10 Italian         GIORNO
b                      004
  026 33 Danish          DAG
  026 36 Faroese         DAGUR
  026 32 Swedish List    DAG
  026 34 Riksmal         DAG
  026 35 Icelandic ST    DAGR
  026 24 German ST       TAG
  026 27 Afrikaans       DAG
  026 26 Dutch List      DAG
  026 25 Penn. Dutch     DAWG
  026 28 Flemish         DAG
  026 30 Swedish Up      DAG
  026 31 Swedish VL      DAG
  026 29 Frisian         DEI
  026 37 English ST      DAY
  026 38 Takitaki        DEI
b                      005
  026 01 Irish A         LA
  026 02 Irish B         LA
b                      006
  026 71 Armenian Mod    OR
  026 72 Armenian List   ORR
b                      200
c                         200  3  201
  026 78 Baluchi         ROSH
  026 77 Tadzik          RUZ
  026 76 Persian List    RUZ
b                      201
c                         200  3  201
  026 74 Afghan          VRADZ
  026 75 Waziri          VREZ, WREZ
a 027 TO DIE
b                      001
  027 01 Irish A         BAS D'FHAGHAIL
  027 02 Irish B         DOLUIDH
b                      002
  027 68 Greek Mod       PETHENO
  027 66 Greek ML        PETHAINO
  027 70 Greek K         APOTHNESKO
  027 67 Greek MD        PETHAINO, PSOFO
  027 69 Greek D         PETHAINO
b                      003
  027 65 Khaskura        MARNU, BITNU
  027 47 Czech E         UMRIT, SKAPAT
  027 09 Vlach           MURI ("HE DIED")
  027 55 Gypsy Gk        MERAV
  027 40 Lithuanian ST   MIRTI (PEOPLE), DVESTI (ANIMALS)
  027 39 Lithuanian O    MIRTI
  027 41 Latvian         MIRST
  027 94 BULGARIAN P     MRAM
  027 87 BYELORUSSIAN P  MERCI
  027 45 Czech           ZEMRITI
  027 90 CZECH P         MRITI
  027 43 Lusatian L      MRES
  027 44 Lusatian U      MREC
  027 93 MACEDONIAN P    UMRAM
  027 50 Polish          UMIERAC
  027 88 POLISH P        UMRZEC
  027 51 Russian         UMIRAT
  027 85 RUSSIAN P       MERET
  027 54 Serbocroatian   UMRETI
  027 92 SERBOCROATIAN P MRETI
  027 46 Slovak          UMIERAT
  027 89 SLOVAK P        MRET
  027 42 Slovenian       UMRT
  027 91 SLOVENIAN P     MRETI
  027 86 UKRAINIAN P     MERTY
  027 15 French Creole C MO
  027 16 French Creole D MO
  027 18 Sardinian L     MORRERE
  027 13 French          MOURIR
  027 14 Walloon         MORI
  027 12 Provencal       MOURI, DEBANA
  027 20 Spanish         MORIR
  027 23 Catalan         MORIRSE
  027 10 Italian         MORIRE
  027 19 Sardinian C     MORRI
  027 17 Sardinian N     MORRERE
  027 11 Ladin           MORIR, SMURIR
  027 08 Rumanian List   A MURI
  027 74 Afghan          MREL
  027 78 Baluchi         MIRAGH, MURTHA
  027 79 Wakhi           MERI-
  027 73 Ossetic         MAELYN, UD ISYN
  027 61 Lahnda          MEREN
  027 64 Nepali List     MARNU
  027 57 Kashmiri        MARUN
  027 56 Singhalese      MARENAWA
  027 07 Breton ST       MERVEL
  027 06 Breton SE       MARUEIN
  027 05 Breton List     MERVEL
  027 04 Welsh C         MARW
  027 03 Welsh N         MARW
  027 59 Gujarati        MERWU
  027 52 Macedonian      UMRE
  027 77 Tadzik          MURDAN
  027 60 Panjabi ST      MERNA
  027 62 Hindi           MERNA
  027 63 Bengali         MORA
  027 58 Marathi         MERNE.
  027 76 Persian List    MORDAN
  027 71 Armenian Mod    MERNEL
  027 53 Bulgarian       DA UMRE
  027 48 Ukrainian       UMYRATY
  027 49 Byelorussian    PAMIRAC'
  027 21 Portuguese ST   MORRER
  027 22 Brazilian       MORRER
  027 72 Armenian List   MARNIL
  027 75 Waziri          MREL
b                      004
  027 81 Albanian Top    VDES, AOR. VDIKA
  027 82 Albanian G      VDES (VDEK = INF.)
  027 84 Albanian C      VDES
  027 83 Albanian K      VDES, (AOR. VDIKA)
  027 80 Albanian T      ME VDEKUR
  027 95 ALBANIAN        VDES, (VDIKJA = AOR.) (VDEK = INF.)
b                      200
c                         200  2  201
  027 37 English ST      TO DIE
  027 30 Swedish Up      DO
  027 31 Swedish VL      DO
  027 36 Faroese         DOYGGJA, ANDAST
  027 33 Danish          DO
  027 32 Swedish List    DO
  027 34 Riksmal         DO
  027 35 Icelandic ST    DEYJA
  027 38 Takitaki        DEDE
b                      201
c                         200  2  201
c                         201  2  202
  027 27 Afrikaans       STERF, STERWE, DOODGAAN
  027 29 Frisian         DEAGEAN, FORSTJERRE
b                      202
c                         201  2  202
  027 26 Dutch List      STERVEN
  027 25 Penn. Dutch     SCHTAAREVE
  027 28 Flemish         STERVEN
  027 24 German ST       STERBEN
a 028 TO DIG
b                      001
  028 13 French          CREUSER
  028 76 Persian List    BILZADAN
  028 56 Singhalese      HARANAWA
  028 78 Baluchi         JANAGH, PHATAGH, KATAGH
  028 73 Ossetic         KWAXYN
  028 84 Albanian C      KAVAR
  028 81 Albanian Top    MIN, AOR. MIVA
  028 79 Wakhi           PUS-
  028 41 Latvian         RAKT
  028 55 Gypsy Gk        SKAVO
  028 14 Walloon         TCHABOTER
b                      002
  028 16 French Creole D FWIYE
  028 15 French Creole C FUYE  FWIYE
b                      003
  028 20 Spanish         CAVAR
  028 23 Catalan         CAVAR, PENETRAR
  028 10 Italian         VANGARE, SCAVARE
  028 19 Sardinian C     SKAVAI
  028 11 Ladin           CHAVER
  028 12 Provencal       CAVA, FURA
  028 22 Brazilian       CAVAR
  028 21 Portuguese ST   CAVAR
  028 17 Sardinian N     ISKAVARE
  028 18 Sardinian L     ISCAVARE
b                      004
  028 37 English ST      TO DIG
  028 38 Takitaki        DIKI
b                      005
  028 40 Lithuanian ST   KASTI
  028 39 Lithuanian O    KASTI
b                      006
  028 08 Rumanian List   A SAPA
  028 09 Vlach           SAPU
b                      007
  028 72 Armenian List   PORELL
  028 71 Armenian Mod    P`OREL
b                      008
  028 01 Irish A         ROMHAR
  028 02 Irish B         ROMHARAIM
  028 51 Russian         RYT
b                      009
  028 63 Bengali         KHODAI+KORA
  028 62 Hindi           KHODNA
  028 60 Panjabi ST      KHODNA
  028 59 Gujarati        KHODWU
  028 61 Lahnda          KHODEN
b                      200
c                         200  2  201
  028 06 Breton SE       KLAUEIN
  028 05 Breton List     TOULLA, KLEUZA, KLEUZIA, KAVA
  028 07 Breton ST       TOULLAN, KLEUZIAN
b                      201
c                         200  2  201
c                         201  2  202
  028 03 Welsh N         PALU (DIG A GARDEN) CLODDIO (DIG FOR GOLD)
b                      202
c                         201  2  202
  028 04 Welsh C         PALU
b                      203
c                         203  2  204
c                         203  3  208
  028 68 Greek Mod       SKAVO
  028 66 Greek ML        SKABO
  028 70 Greek K         SKAPTO
  028 67 Greek MD        SKABO
  028 69 Greek D         SKABO
  028 85 RUSSIAN P       KOPAT
  028 54 Serbocroatian   KOPATI
  028 92 SERBOCROATIAN P KOPATI
  028 46 Slovak          KOPAT
  028 89 SLOVAK P        KOPAT
  028 42 Slovenian       KOPAT
  028 91 SLOVENIAN P     KOPATI
  028 86 UKRAINIAN P     KOPATY
  028 94 BULGARIAN P     KOPAJA
  028 87 BYELORUSSIAN P  KAPAC
  028 45 Czech           KOPATI
  028 90 CZECH P         KOPATI
  028 43 Lusatian L      KOPAS
  028 44 Lusatian U      KOPAC
  028 93 MACEDONIAN P    KOPAM
  028 50 Polish          KOPAC
  028 88 POLISH P        KOPAC
  028 53 Bulgarian       DA KOPAE
  028 48 Ukrainian       KOPATY
  028 49 Byelorussian    KAPAC'
  028 47 Czech E         KOPAT
b                      204
c                         203  2  204
c                         204  2  205
c                         204  2  206
c                         204  3  208
  028 52 Macedonian      GREBE, KOPA
b                      205
c                         204  2  205
c                         205  2  206
  028 30 Swedish Up      GRAVA
  028 31 Swedish VL      GRAVA  GRAVA
  028 36 Faroese         GRAVA
  028 33 Danish          GRAVE
  028 32 Swedish List    GRAVA
  028 34 Riksmal         GRAVE
  028 35 Icelandic ST    GRAFA
  028 24 German ST       GRABEN
  028 25 Penn. Dutch     GRAWB
  028 27 Afrikaans       GRAAF, GRAWE
b                      206
c                         204  2  206
c                         205  2  206
c                         206  2  207
  028 28 Flemish         GRAVEN, DELVEN
  028 29 Frisian         DOLLE, GRAVE
b                      207
c                         206  2  207
  028 26 Dutch List      DELVEN
b                      208
c                         203  3  208
c                         204  3  208
c                         208  2  209
  028 77 Tadzik          KOFTAN, KANDAN
b                      209
c                         208  2  209
  028 75 Waziri          KANDEL
  028 74 Afghan          KINEL, KINDEL
  028 64 Nepali List     KHANNU
  028 57 Kashmiri        KHANUN
  028 65 Khaskura        KHANNU
  028 58 Marathi         KHENNE.
b                      210
c                         210  3  211
  028 82 Albanian G      GERMOJ
  028 95 ALBANIAN        GERMOJ
b                      211
c                         210  3  211
  028 83 Albanian K      REMON
  028 80 Albanian T      ME REMIRE
a 029 DIRTY
b                      000
  029 52 Macedonian
b                      001
  029 57 Kashmiri        ACHOLU, ASORSHU, MALABORUTU
  029 72 Armenian List   AGHDOD
  029 70 Greek K         AKATHARTOS
  029 11 Ladin           ASCHER
  029 77 Tadzik          CIRKIN, IFLOS
  029 25 Penn. Dutch     DRECKICH
  029 31 Swedish VL      DYNGI
  029 81 Albanian Top    FELIKUR
  029 84 Albanian C      GHORDU
  029 71 Armenian Mod    KELTOT
  029 56 Singhalese      KILUTU
  029 14 Walloon         MASSI
  029 08 Rumanian List   MURDAR
  029 09 Vlach           (NE)LATE  ("UNWASHED")
  029 41 Latvian         NETIRS
  029 83 Albanian K      I PERGUAM
  029 55 Gypsy Gk        PISI
  029 79 Wakhi           RIM
  029 86 UKRAINIAN P     SKVERNYJ
b                      002
  029 49 Byelorussian    BRUDNY
  029 48 Ukrainian       BRUDNYJ, POGANYJ, PASKUDNYJ
  029 46 Slovak          BRUDNY
  029 50 Polish          BRUDNY
  029 88 POLISH P        BRUDNY
b                      003
  029 45 Czech           SPINAVY
  029 90 CZECH P         SPINAVY
  029 89 SLOVAK P        SPINAVY
  029 47 Czech E         SPINAVE
b                      004
  029 35 Icelandic ST    SKITUGUR
  029 34 Riksmal         SKIDDEN
  029 36 Faroese         SKITIN
  029 33 Danish          BESKIDT
b                      005
  029 04 Welsh C         BRWNT
  029 03 Welsh N         BUDR, BRWNT
b                      006
  029 43 Lusatian L      MAZANY
  029 44 Lusatian U      MAZANY
  029 42 Slovenian       UMAZANU
  029 91 SLOVENIAN P     UMAZAN
b                      007
  029 94 BULGARIAN P     MRUSEN
  029 53 Bulgarian       MRESNO
b                      008
  029 40 Lithuanian ST   NESVARUS, PURVINAS
  029 39 Lithuanian O    PURVINAS
b                      009
  029 54 Serbocroatian   PRLJAV
  029 92 SERBOCROATIAN P PRLJAV
  029 93 MACEDONIAN P    PRLAV
b                      010
  029 24 German ST       SCHMUTZIG
  029 30 Swedish Up      LORTIG, SMUTSIG
  029 32 Swedish List    SMUTSIG, OREN
b                      011
  029 38 Takitaki        DOTI, MORSOE, MOTOMOTO
  029 37 English ST      DIRTY
b                      012
  029 07 Breton ST       LOUS
  029 06 Breton SE       LOUS
  029 05 Breton List     LOUS, LOUAN, LOUDOUR, FANK, LASTEZ-, LOUI-DIK.
b                      013
  029 74 Afghan          CATAL, XIREN
  029 75 Waziri          KHACHEN, KHIRAN
b                      014
  029 51 Russian         GRJAZNYJ
  029 85 RUSSIAN P       GR AZNYJ
  029 87 BYELORUSSIAN P  HRAZKI
b                      015
  029 01 Irish A         SALACH
  029 02 Irish B         SALACH
b                      016
  029 15 French Creole C SAL
  029 13 French          SALE
  029 16 French Creole D SAL
  029 12 Provencal       SALE, ALO
b                      100
  029 76 Persian List    KASIF
  029 73 Ossetic         C"IZI, C"YF
b                      200
c                         200  2  201
  029 80 Albanian T      I, E NDOHTUR
b                      201
c                         200  2  201
c                         201  2  202
  029 95 ALBANIAN        ZHGRYM, NDYT
b                      202
c                         201  2  202
  029 82 Albanian G      TROK, ZHGRYM
b                      203
c                         203  2  204
  029 19 Sardinian C     BRUTTU
  029 17 Sardinian N     BRUTTU
  029 18 Sardinian L     BRUTTU
b                      204
c                         203  2  204
c                         204  2  205
c                         204  2  206
  029 23 Catalan         BRUT, PORCH
b                      205
c                         204  2  205
c                         205  2  206
  029 10 Italian         SPORCO
b                      206
c                         204  2  206
c                         205  2  206
c                         206  2  207
  029 21 Portuguese ST   SUJO, PORCO
b                      207
c                         206  2  207
  029 20 Spanish         SUCIO
  029 22 Brazilian       SUJO
b                      208
c                         208  2  209
  029 29 Frisian         FIIS
b                      209
c                         208  2  209
c                         209  2  210
  029 28 Flemish         VIES, VUIL
b                      210
c                         209  2  210
  029 26 Dutch List      VUIL
  029 27 Afrikaans       VUIL, SMERIG
b                      211
c                         211  2  212
  029 59 Gujarati        GENDU
  029 58 Marathi         GHAN, GHANERDA
b                      212
c                         211  2  212
c                         212  2  213
  029 62 Hindi           GENDA, MELA
b                      213
c                         212  2  213
  029 60 Panjabi ST      MELLA
  029 61 Lahnda          MAELA
  029 64 Nepali List     GUHE, MAILO
  029 78 Baluchi         MELAR
  029 65 Khaskura        PHORI, MAILO
  029 63 Bengali         MOELA
b                      214
c                         214  2  215
  029 66 Greek ML        LEROS
b                      215
c                         214  2  215
c                         215  2  216
  029 67 Greek MD        BROMIKOS, LEROMENOS
b                      216
c                         215  2  216
  029 69 Greek D         BROMIKOS
  029 68 Greek Mod       VROMIKOS
a 030 DOG
b                      001
  030 56 Singhalese      BALLA
  030 73 Ossetic         KUYDZ
  030 20 Spanish         PERRO
b                      002
  030 77 Tadzik          SAG
  030 76 Persian List    SAG
b                      003
  030 30 Swedish Up      HUND
  030 31 Swedish VL      HUN
  030 17 Sardinian N     KANE
  030 18 Sardinian L     CANE
  030 15 French Creole C SIE
  030 40 Lithuanian ST   SUO
  030 39 Lithuanian O    SUO
  030 41 Latvian         SUNS
  030 70 Greek K         KUON
  030 10 Italian         CANE
  030 19 Sardinian C     KANI
  030 11 Ladin           CHAUN
  030 08 Rumanian List   CIINE
  030 13 French          CHIEN
  030 16 French Creole D SYE
  030 14 Walloon         TCHIN
  030 12 Provencal       CHIN, INO, CAN
  030 07 Breton ST       KI
  030 06 Breton SE       KI
  030 05 Breton List     KI
  030 04 Welsh C         CI
  030 03 Welsh N         CI
  030 24 German ST       HUND
  030 27 Afrikaans       HOND
  030 57 Kashmiri        HUNU
  030 26 Dutch List      HOND
  030 25 Penn. Dutch     HUUNDT
  030 28 Flemish         HOND
  030 29 Frisian         HOUN
  030 36 Faroese         HUNDUR
  030 33 Danish          HUND
  030 32 Swedish List    HUND
  030 34 Riksmal         HUND
  030 35 Icelandic ST    HUNDR
  030 71 Armenian Mod    SUN
  030 72 Armenian List   SHUN
  030 22 Brazilian       CAO
  030 21 Portuguese ST   CAO
  030 23 Catalan         CA, GOS
  030 75 Waziri          SPAI
  030 74 Afghan          SPAJ
  030 09 Vlach           KYNE
b                      004
  030 63 Bengali         KUKUR
  030 65 Khaskura        KUKUR
  030 64 Nepali List     KUKUR
b                      005
  030 58 Marathi         KUTRA
  030 62 Hindi           KUTTA
  030 60 Panjabi ST      KUTTA
  030 59 Gujarati        KUTERO
  030 61 Lahnda          KUTTA
b                      006
  030 37 English ST      DOG
  030 38 Takitaki        DAGOE
b                      007
  030 02 Irish B         MADA
  030 01 Irish A         MADADH, GADHAR
b                      008
  030 67 Greek MD        SKULI
  030 69 Greek D         SKULOS, SKOLI
  030 68 Greek Mod       SKILI
  030 66 Greek ML        SKULOS
b                      009
  030 95 ALBANIAN        KJENI
  030 82 Albanian G      KJENI
  030 80 Albanian T      GEN
  030 84 Albanian C      KEN
  030 83 Albanian K      KEN
  030 81 Albanian Top    KEN, BUSTER
b                      100
  030 78 Baluchi         BING, KSHIK
  030 79 Wakhi           SUC
  030 55 Gypsy Gk        JUKEL
b                      200
c                         200  2  201
c                         200  2  203
  030 54 Serbocroatian   PAS
  030 92 SERBOCROATIAN P PAS
  030 46 Slovak          PES
  030 89 SLOVAK P        PES
  030 42 Slovenian       PAS
  030 91 SLOVENIAN P     PES
  030 86 UKRAINIAN P     PES
  030 87 BYELORUSSIAN P  P OS
  030 45 Czech           PES
  030 90 CZECH P         PES
  030 43 Lusatian L      PJAS
  030 44 Lusatian U      POS
  030 93 MACEDONIAN P    PES
  030 50 Polish          PIES
  030 88 POLISH P        PIES
  030 94 BULGARIAN P     PES
  030 47 Czech E         PES
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
  030 48 Ukrainian       SOBAKA, PES
b                      202
c                         201  2  202
  030 51 Russian         SOBAKA
  030 85 RUSSIAN P       SOBAKA
  030 49 Byelorussian    SABAKA
b                      203
c                         200  2  203
c                         201  2  203
c                         203  2  204
  030 52 Macedonian      PCISTE, KUCE/PES
b                      204
c                         203  2  204
  030 53 Bulgarian       KUCE
a 031 TO DRINK
b                      001
  031 56 Singhalese      BONAWA
  031 57 Kashmiri        CYONU
  031 29 Frisian         NINNE
  031 78 Baluchi         WARAGH, WARTHA
b                      002
  031 65 Khaskura        KHANU
  031 63 Bengali         KHAOA
b                      003
  031 26 Dutch List      DRINKEN
  031 25 Penn. Dutch     NEMM EN DRINK
  031 28 Flemish         DRINKEN
  031 37 English ST      TO DRINK
  031 38 Takitaki        DRINGI
  031 30 Swedish Up      DRICKA
  031 31 Swedish VL      DREK
  031 36 Faroese         DREKKA
  031 33 Danish          DRIKKE
  031 32 Swedish List    DRICKA
  031 34 Riksmal         DRIKKE
  031 35 Icelandic ST    DREKKA
  031 24 German ST       TRINKEN
  031 27 Afrikaans       DRINK
b                      004
  031 58 Marathi         PINE.
  031 01 Irish A         OL
  031 02 Irish B         OLAIM
  031 55 Gypsy Gk        PEAV
  031 81 Albanian Top    PI, AOR. PIVA
  031 94 BULGARIAN P     PIJA
  031 87 BYELORUSSIAN P  PIC
  031 45 Czech           PITI
  031 90 CZECH P         PITI
  031 43 Lusatian L      PIS
  031 44 Lusatian U      PIC
  031 93 MACEDONIAN P    PIJAM
  031 50 Polish          PIC
  031 88 POLISH P        PIC
  031 51 Russian         PIT
  031 85 RUSSIAN P       PIT
  031 54 Serbocroatian   PITI
  031 92 SERBOCROATIAN P PITI
  031 46 Slovak          PIT
  031 89 SLOVAK P        PIT
  031 42 Slovenian       PIT
  031 91 SLOVENIAN P     PITI
  031 86 UKRAINIAN P     PYTY
  031 68 Greek Mod       PINO
  031 66 Greek ML        PINO
  031 70 Greek K         PINO
  031 67 Greek MD        PINO
  031 69 Greek D         PINO
  031 79 Wakhi           PEV-, PU(W)-
  031 61 Lahnda          PIWEN
  031 64 Nepali List     PANI KHANU, PIUNU
  031 82 Albanian G      PI
  031 84 Albanian C      PI
  031 83 Albanian K      PII
  031 80 Albanian T      ME PIRE
  031 95 ALBANIAN        PI, PIVA
  031 59 Gujarati        PIWU
  031 52 Macedonian      PIE
  031 60 Panjabi ST      PINA
  031 62 Hindi           PINA
  031 48 Ukrainian       PYTY
  031 49 Byelorussian    PIC'
  031 47 Czech E         PIT
  031 53 Bulgarian       DA PIE
  031 09 Vlach           BEAU
  031 17 Sardinian N     BIERE
  031 18 Sardinian L     BIERE
  031 15 French Creole C BWE
  031 13 French          BOIRE
  031 16 French Creole D BWE
  031 14 Walloon         BEURE
  031 12 Provencal       BEURE, CHOURLA
  031 20 Spanish         BEBER
  031 23 Catalan         BEURER
  031 10 Italian         BERE, BEVERE
  031 19 Sardinian C     BUFFAI
  031 11 Ladin           BAIVER
  031 08 Rumanian List   A BEA
  031 22 Brazilian       BEBER
  031 21 Portuguese ST   BEBER
  031 07 Breton ST       EVAN
  031 06 Breton SE       IVET
  031 05 Breton List     EVA
  031 04 Welsh C         YFED
  031 03 Welsh N         YFED
b                      005
  031 41 Latvian         DZERT
  031 40 Lithuanian ST   GERTI
  031 39 Lithuanian O    GERTI
b                      006
  031 74 Afghan          CSEL
  031 75 Waziri          TSHEL
b                      007
  031 71 Armenian Mod    EMPEL, XMEL
  031 72 Armenian List   KHIMEL
b                      008
  031 77 Tadzik          NUSIDAN, OSOMIDAN
  031 76 Persian List    NUSHIDAN
  031 73 Ossetic         NUAZYN, CYMYN
a 032 DRY (SUBSTANCE)
b                      001
  032 02 Irish B         DIOSC
  032 67 Greek MD        STEGNOS
  032 56 Singhalese      VELICCA, VIYALI
b                      002
  032 07 Breton ST       SEC'H
  032 06 Breton SE       SEH
  032 05 Breton List     SEC'H
  032 04 Welsh C         SYCH
  032 03 Welsh N         SYCH
b                      003
  032 81 Albanian Top    I-THAT
  032 80 Albanian T      I, E THATI
  032 83 Albanian K      THAATE
  032 82 Albanian G      THAT
  032 95 ALBANIAN        THAT
b                      004
  032 26 Dutch List      DROOG
  032 25 Penn. Dutch     DRUUCKE
  032 28 Flemish         DROOG
  032 29 Frisian         DROECH
  032 24 German ST       TROCKEN
  032 27 Afrikaans       DROOG, DROR
  032 37 English ST      DRY
  032 38 Takitaki        DRE
b                      005
  032 01 Irish A         TIRIM
  032 84 Albanian C      I-TERM
  032 30 Swedish Up      TORR
  032 31 Swedish VL      TOR
  032 36 Faroese         TURRUR
  032 33 Danish          TOR
  032 32 Swedish List    TORR
  032 34 Riksmal         TORR
  032 35 Icelandic ST    THURR
b                      200
c                         200  3  201
  032 69 Greek D         KSEROS
  032 68 Greek Mod       KSEROS
  032 66 Greek ML        KSEROS
  032 70 Greek K         KSEROS
b                      201
c                         200  3  201
  032 72 Armenian List   CHOR
  032 71 Armenian Mod    C`OR
b                      202
c                         202  2  203
  032 21 Portuguese ST   SECCO
  032 20 Spanish         SECO, ARIDO
  032 17 Sardinian N     SIKKU
  032 18 Sardinian L     SICCU
  032 15 French Creole C SES
  032 19 Sardinian C     SIKKU
  032 13 French          SEC
  032 16 French Creole D SES
  032 14 Walloon         SETCH
  032 12 Provencal       SE, SECO
  032 22 Brazilian       SECO
b                      203
c                         202  2  203
c                         203  2  204
  032 11 Ladin           SECH, SUT
  032 23 Catalan         SECH, AIXUT
b                      204
c                         203  2  204
  032 10 Italian         ASCIUTTO
  032 08 Rumanian List   USCAT
  032 09 Vlach           USKATE
b                      205
c                         205  2  206
  032 85 RUSSIAN P       SUCHOJ
  032 55 Gypsy Gk        SUKO
  032 54 Serbocroatian   SUV
  032 92 SERBOCROATIAN P SUV
  032 46 Slovak          SUCHY
  032 89 SLOVAK P        SUCHY
  032 42 Slovenian       SUHO
  032 91 SLOVENIAN P     SUV
  032 86 UKRAINIAN P     SUCHYJ
  032 44 Lusatian U      SUCHI
  032 93 MACEDONIAN P    SUV
  032 50 Polish          SUCHY
  032 88 POLISH P        SUCHY
  032 51 Russian         SUXOJ
  032 40 Lithuanian ST   SAUSAS
  032 39 Lithuanian O    SAUSAS
  032 41 Latvian         SAUSS
  032 94 BULGARIAN P     SUCH
  032 87 BYELORUSSIAN P  SUCHI
  032 45 Czech           SUCHY
  032 90 CZECH P         SUCHY
  032 43 Lusatian L      SUCHY
  032 61 Lahnda          SUKKA
  032 64 Nepali List     SUKO, BUKO
  032 59 Gujarati        SUKU
  032 52 Macedonian      SUV
  032 65 Khaskura        SUKYAKO
  032 60 Panjabi ST      SUKKA
  032 62 Hindi           SUKHA
  032 63 Bengali         SUKNO
  032 58 Marathi         SUKA
  032 53 Bulgarian       SUXO
  032 48 Ukrainian       SUXYJ, - A - E
  032 49 Byelorussian    SUXI
  032 47 Czech E         SUXE
  032 73 Ossetic         XUS
  032 57 Kashmiri        HOKHU, KHOSHK
  032 78 Baluchi         HUSHK
  032 77 Tadzik          XUSK, KOK
  032 76 Persian List    KHOSHK
b                      206
c                         205  2  206
c                         206  3  207
  032 79 Wakhi           WESK, XUSK
b                      207
c                         206  3  207
  032 75 Waziri          SIR, WUCH
  032 74 Afghan          VUC
a 033 DULL (KNIFE)
b                      000
  033 09 Vlach
  033 55 Gypsy Gk
  033 66 Greek ML
  033 78 Baluchi
  033 79 Wakhi
  033 10 Italian
  033 32 Swedish List
  033 28 Flemish
  033 84 Albanian C
  033 65 Khaskura
  033 75 Waziri
  033 72 Armenian List
b                      001
  033 18 Sardinian L     (BULTEDDU) CHI NON SEGA
  033 35 Icelandic ST    BITLAUS
  033 71 Armenian Mod    BUT`
  033 02 Irish B         DUR
  033 83 Albanian K      I PAA ECURE
  033 17 Sardinian N     ISPUNTATU
  033 73 Ossetic         K"UYMYX
  033 01 Irish A         MAOL
  033 70 Greek K         ME AICHMERON
  033 57 Kashmiri        MONDU
  033 56 Singhalese      MOTTA
  033 62 Hindi           MUTHRA
  033 74 Afghan          PEC
  033 19 Sardinian C     SGURDU
  033 42 Slovenian       SKRHAN
  033 67 Greek MD        STOMOMENOS
  033 08 Rumanian List   TOCIT
  033 14 Walloon         TOT R'DOHI
b                      002
  033 94 BULGARIAN P     TUP
  033 91 SLOVENIAN P     TOP
  033 86 UKRAINIAN P     TUPYJ
  033 87 BYELORUSSIAN P  TUPY
  033 45 Czech           TUPY
  033 90 CZECH P         TUPY
  033 43 Lusatian L      TUPY
  033 44 Lusatian U      TUPY
  033 93 MACEDONIAN P    TAP
  033 50 Polish          TEPY
  033 88 POLISH P        TEPY
  033 51 Russian         TUPOJ
  033 85 RUSSIAN P       TUPOJ
  033 54 Serbocroatian   TUP
  033 92 SERBOCROATIAN P TUP
  033 46 Slovak          TUPY
  033 89 SLOVAK P        TUPY
  033 52 Macedonian      TAP
  033 53 Bulgarian       TEP
  033 48 Ukrainian       TUPYJ
  033 49 Byelorussian    TUPY
  033 47 Czech E         TUPE
b                      003
  033 68 Greek Mod       DHEN-GOVI (DOES NOT CUT)
  033 69 Greek D         DIOLOU MUTERO, DEV KOBEI
b                      004
  033 13 French          EMOUSSE
  033 12 Provencal       MOUTU, UDO
  033 11 Ladin           MUOT
  033 23 Catalan         ROM, AMUSSADO
b                      005
  033 24 German ST       STUMPF
  033 29 Frisian         STOMP
  033 27 Afrikaans       STOMP
  033 26 Dutch List      STOMP
  033 25 Penn. Dutch     SCHTUUMP
  033 38 Takitaki        DEDE, STOMPOE, TOMPOE
b                      006
  033 37 English ST      DULL
  033 05 Breton List     (TO LOSE SHARPNESS) DALLA, KIZA, TALTOUZA,
  033 07 Breton ST       DALL, TOUGN
  033 06 Breton SE       DALL, TOUGN
b                      007
  033 61 Lahnda          KHUNDA
  033 77 Tadzik          KYND
  033 60 Panjabi ST      KHUNDA
  033 76 Persian List    KOND
b                      008
  033 20 Spanish         EMBOTADO
  033 22 Brazilian       EMBOTADOR
  033 21 Portuguese ST   EMBOTADO
b                      009
  033 82 Albanian G      NUK PREFET
  033 95 ALBANIAN        NUK PREFET
b                      010
  033 16 French Creole D PA FILE
  033 15 French Creole C PA FILE
b                      011
  033 40 Lithuanian ST   BUKAS, NEASTRUS, ATSIPES
  033 39 Lithuanian O    ATBUKES, NE ASTRUS
  033 41 Latvian         NEASS (TRULS)
b                      012
  033 81 Albanian Top    E-PAPREHUR
  033 80 Albanian T      I, E PAPREHUR
b                      013
  033 04 Welsh C         DIFIN
  033 03 Welsh N         DI-FIN, DI-AWCH (DI= NEGATIVE PARTICLE)
b                      200
c                         200  2  201
  033 33 Danish          SLOV
  033 34 Riksmal         SLOV
  033 31 Swedish VL      SLOG  SLOG
b                      201
c                         200  2  201
c                         201  2  202
  033 30 Swedish Up      OVASS, SLO
b                      202
c                         201  2  202
  033 36 Faroese         OHVASSUR, BAKKI ( )
b                      203
c                         203  3  400
  033 63 Bengali         BHOTA
  033 64 Nepali List     BHUTTE
b                      400
c                         203  3  400
  033 58 Marathi         BOTHET
  033 59 Gujarati        BUTTNU
a 034 DUST
b                      000
  034 08 Rumanian List   PRAF
b                      001
  034 78 Baluchi         DATO, DATO, DANZ
  034 06 Breton SE       HUAN
  034 76 Persian List    KHAK
  034 70 Greek K         KONIORTOS
  034 09 Vlach           KURNAXTO
  034 50 Polish          KURZ
  034 61 Lahnda          MITTI
  034 35 Icelandic ST    RYK
  034 83 Albanian K      SKON
  034 55 Gypsy Gk        SKONI
b                      002
  034 95 ALBANIAN        PLUHUNI
  034 80 Albanian T      PLUHUR
  034 82 Albanian G      PLUHUNI
  034 84 Albanian C      PLUXURAC
  034 81 Albanian Top    PLUHUR
b                      003
  034 72 Armenian List   POSHEE
  034 71 Armenian Mod    POSI
b                      004
  034 20 Spanish         POLVO
  034 23 Catalan         POLS
  034 10 Italian         POLVERE
  034 19 Sardinian C     PRUINI
  034 11 Ladin           PUOLVRA
  034 22 Brazilian       PO, POEIRA
  034 21 Portuguese ST   PO, POEIRA
  034 17 Sardinian N     PRUERE
  034 18 Sardinian L     PIUERE
  034 15 French Creole C PUSYE
  034 13 French          POUSSIERE
  034 16 French Creole D PUSYE
  034 14 Walloon         POUSSIRE
  034 12 Provencal       POUSSO
b                      005
  034 67 Greek MD        SKONE
  034 69 Greek D         SKONE
  034 68 Greek Mod       SKONI
  034 66 Greek ML        SKONE
b                      006
  034 04 Welsh C         LLWCH
  034 03 Welsh N         LLWCH
b                      007
  034 05 Breton List     POULTR
  034 07 Breton ST       POULTRENN
b                      008
  034 30 Swedish Up      DAMM
  034 31 Swedish VL      DAM
b                      009
  034 01 Irish A         DUSTA, CEO
  034 02 Irish B         CEO
b                      010
  034 77 Tadzik          CAND, GARD
  034 79 Wakhi           GERD, XSUREM
  034 74 Afghan          GARZ
b                      100
  034 75 Waziri          KHAIRPAL
  034 73 Ossetic         CYREN, TAERK, TAEVD
b                      200
c                         200  2  201
  034 49 Byelorussian    PYL
  034 87 BYELORUSSIAN P  PYL
  034 51 Russian         PYL
  034 85 RUSSIAN P       PYL
  034 41 Latvian         PUTEKLI
b                      201
c                         200  2  201
c                         201  2  202
  034 48 Ukrainian       POROX, NYL
b                      202
c                         201  2  202
  034 47 Czech E         PRAX
  034 52 Macedonian      PRAV
  034 53 Bulgarian       PRAX
  034 54 Serbocroatian   PRASINA
  034 92 SERBOCROATIAN P PRAH
  034 46 Slovak          PRACH
  034 89 SLOVAK P        PRACH
  034 42 Slovenian       PRAH
  034 91 SLOVENIAN P     PRAH
  034 86 UKRAINIAN P     POROCH
  034 45 Czech           PRACH
  034 90 CZECH P         PRACH
  034 43 Lusatian L      PROCH
  034 44 Lusatian U      PROCH
  034 93 MACEDONIAN P    PRAV
  034 94 BULGARIAN P     PRACH
  034 88 POLISH P        PROCH
b                      203
c                         203  2  204
  034 24 German ST       STAUB
  034 33 Danish          STOV
  034 32 Swedish List    STOFT
  034 34 Riksmal         STOV
  034 38 Takitaki        STOF
  034 27 Afrikaans       STOF
  034 26 Dutch List      STOF
  034 25 Penn. Dutch     SCHTAWB
  034 28 Flemish         STOF
  034 29 Frisian         STOF
b                      204
c                         203  2  204
c                         204  3  205
  034 36 Faroese         DUST, STOV
b                      205
c                         204  3  205
  034 37 English ST      DUST
b                      206
c                         206  2  207
c                         206  3  209
  034 40 Lithuanian ST   DULKES
  034 39 Lithuanian O    DULKES
  034 56 Singhalese      DUWILI
  034 59 Gujarati        DHUL
  034 65 Khaskura        DHULO
  034 62 Hindi           DHUL
  034 63 Bengali         DHULA
  034 58 Marathi         DHUL
b                      207
c                         206  2  207
c                         207  2  208
c                         207  3  209
  034 64 Nepali List     KHAG, DHULO
b                      208
c                         207  2  208
  034 57 Kashmiri        KHAKH, LATSH, PHEKH
b                      209
c                         206  3  209
c                         207  3  209
  034 60 Panjabi ST      TUR
a 035 EAR
b                      002
  035 76 Persian List    GUSH
  035 75 Waziri          GHOZH
  035 73 Ossetic         X"US
  035 79 Wakhi           YIS
  035 74 Afghan          GVAZ
  035 78 Baluchi         GOSH
  035 77 Tadzik          GUS
  035 81 Albanian Top    VES
  035 82 Albanian G      VESHI
  035 84 Albanian C      VES
  035 83 Albanian K      VES
  035 80 Albanian T      VESH
  035 95 ALBANIAN        VESHI
b                      003
  035 55 Gypsy Gk        KAN
  035 61 Lahnda          KEN
  035 64 Nepali List     KAN
  035 57 Kashmiri        KAN
  035 56 Singhalese      KANA
  035 59 Gujarati        KAN
  035 65 Khaskura        KAN
  035 60 Panjabi ST      KENN
  035 62 Hindi           KAN
  035 63 Bengali         KAN
  035 58 Marathi         KAN
b                      004
  035 07 Breton ST       SKOUARN
  035 06 Breton SE       SKOUARN
  035 05 Breton List     SKOUARN
b                      200
c                         200  2  201
  035 70 Greek K         HOUS
  035 94 BULGARIAN P     UCHO
  035 87 BYELORUSSIAN P  VUCHI
  035 45 Czech           UCHO
  035 90 CZECH P         UCHO
  035 43 Lusatian L      HUCHO
  035 44 Lusatian U      WUCHO
  035 93 MACEDONIAN P    UVO
  035 50 Polish          UCHO
  035 88 POLISH P        UCHO
  035 51 Russian         UXO
  035 85 RUSSIAN P       UCHO
  035 54 Serbocroatian   UVO
  035 92 SERBOCROATIAN P UVO
  035 46 Slovak          UCHO
  035 89 SLOVAK P        UCHO
  035 42 Slovenian       USESU
  035 91 SLOVENIAN P     UHO
  035 86 UKRAINIAN P     VUCHO
  035 52 Macedonian      UVO, USI
  035 49 Byelorussian    VUXA
  035 47 Czech E         UXO
  035 53 Bulgarian       UXO
  035 30 Swedish Up      ORA
  035 31 Swedish VL      ORA
  035 27 Afrikaans       OOR
  035 26 Dutch List      OOR
  035 25 Penn. Dutch     ORR
  035 28 Flemish         OOR
  035 29 Frisian         EAR
  035 36 Faroese         OYRA
  035 33 Danish          ORE
  035 32 Swedish List    ORA
  035 34 Riksmal         ORE
  035 35 Icelandic ST    EYRA
  035 24 German ST       OHR
  035 38 Takitaki        JESI
  035 37 English ST      EAR
  035 68 Greek Mod       AFTI
  035 66 Greek ML        AUTI
  035 67 Greek MD        AUTI
  035 69 Greek D         AUTI
  035 40 Lithuanian ST   AUSIS
  035 39 Lithuanian O    AUSIS
  035 41 Latvian         AUSS
  035 09 Vlach           UREAKLI
  035 17 Sardinian N     URIKRA
  035 18 Sardinian L     ORICA
  035 11 Ladin           URAGLIA
  035 08 Rumanian List   URECHE
  035 13 French          OREILLE
  035 16 French Creole D ZOREJ
  035 15 French Creole C ZOHWEY
  035 14 Walloon         OREYE
  035 12 Provencal       AURIHO
  035 20 Spanish         OREJA
  035 23 Catalan         AURELLA, ORELLA, OIDO
  035 10 Italian         ORECCHIO
  035 19 Sardinian C     URIGA
  035 22 Brazilian       ORELHA
  035 21 Portuguese ST   ORELHA
  035 71 Armenian Mod    AKANJ
  035 72 Armenian List   AGUNCH
b                      201
c                         200  2  201
c                         201  2  202
  035 48 Ukrainian       VUXO, SLUX, KOLOS
b                      202
c                         201  2  202
  035 01 Irish A         CLUAS
  035 02 Irish B         CLUAS
  035 04 Welsh C         CLUST
  035 03 Welsh N         CLUST
a 036 EARTH (SOIL)
b                      001
  036 01 Irish A         CRE, ITHIR
  036 38 Takitaki        GRON
  036 49 Byelorussian    HLEBA
  036 71 Armenian Mod    HOL
  036 75 Waziri          KHOVRA, WATAN
  036 53 Bulgarian       PREST
  036 73 Ossetic         SYDZYT
  036 02 Irish B         TALAMH
  036 72 Armenian List   YERGIR, KEDIN
  036 68 Greek Mod       YI
b                      002
  036 35 Icelandic ST    MOLD
  036 36 Faroese         MOLD, (JORO)
b                      003
  036 84 Albanian C      BOT
  036 83 Albanian K      BOTE
b                      004
  036 34 Riksmal         JORD
  036 30 Swedish Up      JORD, MARK
  036 31 Swedish VL      JOL
  036 24 German ST       ERDE
  036 37 English ST      EARTH
  036 27 Afrikaans       AARDE
  036 26 Dutch List      AARDE
  036 25 Penn. Dutch     AIIRD
  036 28 Flemish         AERDE
  036 29 Frisian         IERDE
  036 33 Danish          JORD
  036 32 Swedish List    JORD
b                      100
  036 56 Singhalese      PASA
  036 55 Gypsy Gk        POSU
b                      200
c                         200  2  201
c                         200  3  203
c                         200  3  204
  036 51 Russian         ZEMLJA
  036 85 RUSSIAN P       ZEML A
  036 89 SLOVAK P        ZEM
  036 42 Slovenian       ZEMLA
  036 91 SLOVENIAN P     ZEMLJA
  036 86 UKRAINIAN P     ZEML A
  036 90 CZECH P         ZEME
  036 43 Lusatian L      ZEMJA
  036 44 Lusatian U      ZEMJA
  036 93 MACEDONIAN P    ZEM A
  036 50 Polish          ZIEMIA
  036 88 POLISH P        ZIEMIA
  036 54 Serbocroatian   ZEMLJA
  036 92 SERBOCROATIAN P ZEMLJA
  036 40 Lithuanian ST   ZEME
  036 39 Lithuanian O    ZEME
  036 41 Latvian         ZEME
  036 94 BULGARIAN P     ZEM A
  036 87 BYELORUSSIAN P  Z AML A
  036 48 Ukrainian       ZEMLJA, GRUNT
  036 52 Macedonian      ZEMJA
  036 77 Tadzik          ZAMIN
  036 47 Czech E         ZEM, HLINA
  036 81 Albanian Top    DHE
  036 80 Albanian T      TOKE, DHE
  036 82 Albanian G      DHEU
  036 95 ALBANIAN        DHEU
  036 76 Persian List    ZAMIN
b                      201
c                         200  2  201
c                         201  2  202
c                         201  3  203
c                         201  3  204
  036 46 Slovak          ZEM, PODA
b                      202
c                         201  2  202
  036 45 Czech           PUDA
b                      203
c                         200  3  203
c                         201  3  203
c                         203  3  204
  036 61 Lahnda          ZEMIN
b                      204
c                         200  3  204
c                         201  3  204
c                         203  3  204
  036 66 Greek ML        CHOMA
  036 70 Greek K         CHOMA
  036 67 Greek MD        CHOMA
  036 69 Greek D         CHOMA
b                      205
c                         205  2  206
  036 17 Sardinian N     TERRA
  036 18 Sardinian L     TERRINU
  036 15 French Creole C TE
  036 13 French          TERRE
  036 16 French Creole D TE
  036 14 Walloon         TERE, TERE
  036 12 Provencal       TERRO
  036 20 Spanish         TIERRA
  036 23 Catalan         TERRA
  036 10 Italian         TERRA
  036 19 Sardinian C     TERRA
  036 11 Ladin           TERRA
  036 09 Vlach           CARE
b                      206
c                         205  2  206
c                         206  2  207
  036 21 Portuguese ST   TERRA, CHAO, SOLO
b                      207
c                         206  2  207
  036 22 Brazilian       SOLO
  036 08 Rumanian List   SOL, PAMINT
b                      208
c                         208  2  209
  036 07 Breton ST       DOUAR
  036 06 Breton SE       DOUAR
  036 05 Breton List     DOUAR
b                      209
c                         208  2  209
c                         209  2  210
  036 03 Welsh N         PRIDD, DAEAR
b                      210
c                         209  2  210
  036 04 Welsh C         PRIDD
b                      211
c                         211  3  212
  036 57 Kashmiri        METSU, ZAMIN
  036 64 Nepali List     MATO
  036 78 Baluchi         MITTI
  036 59 Gujarati        MATI
  036 65 Khaskura        MATO
  036 63 Bengali         MATI
  036 58 Marathi         MATI
  036 60 Panjabi ST      MITTI
  036 62 Hindi           MITTI
b                      212
c                         211  3  212
c                         212  2  213
  036 74 Afghan          MDZEKA, XAK
b                      213
c                         212  2  213
  036 79 Wakhi           SET, XOK
a 037 TO EAT
b                      001
  037 38 Takitaki        NJANJAM
  037 19 Sardinian C     PAPPAI
  037 79 Wakhi           YAU-
b                      002
  037 33 Danish          SPISE
  037 34 Riksmal         SPISE
b                      003
  037 20 Spanish         COMER
  037 22 Brazilian       COMER
  037 21 Portuguese ST   COMER
b                      004
  037 11 Ladin           MANGER
  037 08 Rumanian List   A MINCA
  037 23 Catalan         MENJAR
  037 10 Italian         MANGIARE
  037 13 French          MANGER
  037 16 French Creole D MAZE
  037 14 Walloon         MAGNI
  037 12 Provencal       MANJA
  037 09 Vlach           MYKU
  037 17 Sardinian N     MANNIKARE
  037 18 Sardinian L     MANDIGARE
  037 15 French Creole C MAZE
b                      005
  037 67 Greek MD        TROGO
  037 69 Greek D         TROO
  037 68 Greek Mod       TROO
  037 66 Greek ML        TROGO
  037 70 Greek K         TROGO
b                      006
  037 41 Latvian         EST
  037 94 BULGARIAN P     JAM
  037 87 BYELORUSSIAN P  JESCI
  037 45 Czech           JISTI
  037 90 CZECH P         JISTI
  037 43 Lusatian L      JESC
  037 44 Lusatian U      JESC
  037 93 MACEDONIAN P    JADAM
  037 50 Polish          JESC
  037 88 POLISH P        JESC
  037 51 Russian         EST
  037 85 RUSSIAN P       JEST
  037 54 Serbocroatian   JESTI
  037 92 SERBOCROATIAN P JESTI
  037 46 Slovak          JEST
  037 89 SLOVAK P        JEST
  037 42 Slovenian       JEST
  037 91 SLOVENIAN P     JESTI
  037 86 UKRAINIAN P     JISTY
  037 52 Macedonian      JADE
  037 49 Byelorussian    ES'CI
  037 47 Czech E         YEST
  037 53 Bulgarian       DA JADE
  037 48 Ukrainian       JISTY, XARCUVATYS'
  037 30 Swedish Up      ATA
  037 31 Swedish VL      ATA  ETA
  037 35 Icelandic ST    ETA, BOROA
  037 24 German ST       ESSEN
  037 32 Swedish List    ATA
  037 27 Afrikaans       EET
  037 26 Dutch List      ETEN
  037 25 Penn. Dutch     ESS
  037 28 Flemish         ETEN
  037 29 Frisian         ITE
  037 36 Faroese         ETA
  037 37 English ST      TO EAT
  037 72 Armenian List   UDELL
  037 71 Armenian Mod    UTEL
b                      007
  037 77 Tadzik          XURDAN
  037 76 Persian List    KHORDAN
  037 75 Waziri          KHWAREL
  037 74 Afghan          XVAREL
  037 73 Ossetic         XAERYN
  037 78 Baluchi         WARAGH, WARTHA
b                      008
  037 04 Welsh C         BWYTA
  037 03 Welsh N         BWYTA
b                      009
  037 07 Breton ST       DEBRIN
  037 06 Breton SE       DEBREIN
  037 05 Breton List     DIBRI
b                      010
  037 40 Lithuanian ST   VALGYTI
  037 39 Lithuanian O    VALGYTI
b                      011
  037 01 Irish A         ITHE
  037 02 Irish B         ITHIM
b                      200
c                         200  3  201
  037 65 Khaskura        KHANU
  037 61 Lahnda          KHAWEN
  037 64 Nepali List     KHANU
  037 56 Singhalese      KANAWA
  037 59 Gujarati        KHAWU
  037 60 Panjabi ST      KHANA
  037 62 Hindi           KHANA
  037 63 Bengali         KHAOA
  037 58 Marathi         KHANE.
  037 55 Gypsy Gk        XAV
  037 81 Albanian Top    HA, AOR. HENGERA
  037 83 Albanian K      XAA (AOR. XENGERA, PPLE. GRENE)
  037 80 Albanian T      ME NGRENE
  037 82 Albanian G      HA (HANGER = INF.)
  037 84 Albanian C      XA
  037 95 ALBANIAN        HA, (HANGRA = AOR.) (HANGER = INF.)
b                      201
c                         200  3  201
  037 57 Kashmiri        KHYONU
a 038 EGG
b                      000
  038 73 Ossetic
b                      001
  038 70 Greek K         HOON
  038 55 Gypsy Gk        ARNO
  038 56 Singhalese      BITTARA
  038 37 English ST      EGG
  038 72 Armenian List   HAVGIT
  038 41 Latvian         OLA
  038 57 Kashmiri        THUL
b                      002
  038 59 Gujarati        INDU
  038 61 Lahnda          ENDA
  038 60 Panjabi ST      ANDA
  038 62 Hindi           ENDA
  038 63 Bengali         ANDA
  038 58 Marathi         ENDE.
b                      003
  038 79 Wakhi           TUXM MURGH
  038 77 Tadzik          TUXM
  038 76 Persian List    TOKHM
b                      004
  038 40 Lithuanian ST   KIAUSINIS
  038 39 Lithuanian O    KIAUSINIS
b                      005
  038 64 Nepali List     PHUL
  038 65 Khaskura        PHUL
b                      006
  038 81 Albanian Top    KOKOVE
  038 95 ALBANIAN        VEJA
  038 82 Albanian G      VEJA
  038 84 Albanian C      VE
  038 83 Albanian K      VEE
  038 80 Albanian T      VE, VEZE
b                      007
  038 44 Lusatian U      JEJO
  038 93 MACEDONIAN P    JAJCE
  038 50 Polish          JAJKO
  038 88 POLISH P        JAJE
  038 51 Russian         JAJCO
  038 85 RUSSIAN P       JAJCO
  038 54 Serbocroatian   JAJE
  038 92 SERBOCROATIAN P JAJE
  038 46 Slovak          VAJCE
  038 89 SLOVAK P        VAJCE
  038 42 Slovenian       JAJCE
  038 91 SLOVENIAN P     JAJCE
  038 86 UKRAINIAN P     JAJCE
  038 94 BULGARIAN P     JAJCE
  038 87 BYELORUSSIAN P  JAJCO
  038 45 Czech           VEJCE
  038 90 CZECH P         VEJCE
  038 43 Lusatian L      JAJO
  038 07 Breton ST       VI, UI
  038 06 Breton SE       UI
  038 05 Breton List     VI
  038 04 Welsh C         WY
  038 03 Welsh N         WY
  038 52 Macedonian      JAJCE
  038 48 Ukrainian       JAJCE
  038 49 Byelorussian    JAJKO
  038 47 Czech E         VAYCO
  038 53 Bulgarian       JAJCE
  038 09 Vlach           OU
  038 17 Sardinian N     OVU
  038 18 Sardinian L     OU
  038 01 Irish A         UBH
  038 02 Irish B         UBH
  038 13 French          OEUF
  038 16 French Creole D ZE
  038 15 French Creole C ZE
  038 14 Walloon         OU
  038 12 Provencal       IOU
  038 20 Spanish         HUEVO
  038 23 Catalan         OU
  038 10 Italian         UOVO
  038 19 Sardinian C     OU
  038 11 Ladin           OV
  038 08 Rumanian List   OU
  038 22 Brazilian       OVO
  038 21 Portuguese ST   OVO
  038 30 Swedish Up      AGG
  038 31 Swedish VL      AG
  038 27 Afrikaans       EIER
  038 26 Dutch List      EI
  038 25 Penn. Dutch     OI
  038 28 Flemish         EI
  038 29 Frisian         EIKE
  038 36 Faroese         EGG
  038 33 Danish          AEG
  038 32 Swedish List    AGG
  038 34 Riksmal         EGG
  038 35 Icelandic ST    EGG
  038 24 German ST       EI
  038 38 Takitaki        EKSI
  038 71 Armenian Mod    JU
  038 78 Baluchi         HAIKH, ANU
  038 74 Afghan          HAGEJ
  038 68 Greek Mod       AVGHO
  038 66 Greek ML        AUGO
  038 67 Greek MD        AUGO
  038 69 Greek D         AUGO
  038 75 Waziri          YOWYA, YIYA
a 039 EYE
b                      001
  039 58 Marathi         DOLA
b                      002
  039 37 English ST      EYE
  039 70 Greek K         OFTHALMOS
  039 30 Swedish Up      OGA
  039 31 Swedish VL      YGA  OGA
  039 27 Afrikaans       OOG
  039 26 Dutch List      OOG
  039 25 Penn. Dutch     AWK
  039 28 Flemish         OOG
  039 29 Frisian         EACH
  039 36 Faroese         EYGA
  039 33 Danish          OJE
  039 32 Swedish List    OGA
  039 34 Riksmal         OYE
  039 35 Icelandic ST    AUGA
  039 24 German ST       AUGE
  039 38 Takitaki        HAI
  039 54 Serbocroatian   OKO
  039 92 SERBOCROATIAN P OKO
  039 46 Slovak          OKO
  039 89 SLOVAK P        OKO
  039 42 Slovenian       OKO
  039 91 SLOVENIAN P     OKO
  039 86 UKRAINIAN P     OKO
  039 40 Lithuanian ST   AKIS
  039 39 Lithuanian O    AKIS
  039 41 Latvian         ACS
  039 94 BULGARIAN P     OKO
  039 87 BYELORUSSIAN P  VOKA
  039 45 Czech           OKO
  039 90 CZECH P         OKO
  039 43 Lusatian L      WOKO
  039 44 Lusatian U      WOKO
  039 93 MACEDONIAN P    OKO
  039 50 Polish          OKO
  039 88 POLISH P        OKO
  039 52 Macedonian      OKO, OCI
  039 53 Bulgarian       OKO
  039 48 Ukrainian       OKO, VUSKO
  039 49 Byelorussian    VOKA
  039 47 Czech E         OKO
  039 55 Gypsy Gk        YAK
  039 61 Lahnda          EKH
  039 64 Nepali List     AKHO
  039 57 Kashmiri        ACHI, NITHAR
  039 56 Singhalese      ASA
  039 59 Gujarati        AKH
  039 71 Armenian Mod    AC`K`
  039 72 Armenian List   ASHK
  039 65 Khaskura        ANKHA
  039 60 Panjabi ST      EKKH
  039 62 Hindi           AKH
  039 10 Italian         OCCHIO
  039 19 Sardinian C     OGU
  039 11 Ladin           OGL
  039 08 Rumanian List   OCHI
  039 09 Vlach           OKLI
  039 17 Sardinian N     OKRU
  039 18 Sardinian L     OJU
  039 15 French Creole C ZYE
  039 13 French          OEIL
  039 16 French Creole D ZJE
  039 14 Walloon         OUY
  039 12 Provencal       UEI
  039 20 Spanish         OJO
  039 23 Catalan         ULL
  039 22 Brazilian       OLHO
  039 21 Portuguese ST   OLHO
  039 68 Greek Mod       MATI
  039 66 Greek ML        MATI
  039 67 Greek MD        MATI
  039 69 Greek D         MATI
b                      003
  039 76 Persian List    CHASHM
  039 63 Bengali         COK
  039 73 Ossetic         CAEST
  039 78 Baluchi         CHHAM
  039 79 Wakhi           CEZM
  039 77 Tadzik          CASM, DIDA
b                      004
  039 03 Welsh N         LLYGAD
  039 07 Breton ST       LAGAD
  039 06 Breton SE       LAGAD
  039 05 Breton List     LAGAD
  039 04 Welsh C         LLYGAD
b                      005
  039 01 Irish A         SUIL
  039 02 Irish B         SUIL
b                      006
  039 74 Afghan          STERGA
  039 75 Waziri          STERGA
b                      007
  039 81 Albanian Top    SY
  039 95 ALBANIAN        SYNI
  039 82 Albanian G      SYNI
  039 84 Albanian C      SI
  039 83 Albanian K      SII
  039 80 Albanian T      SY
b                      008
  039 51 Russian         GLAZ
  039 85 RUSSIAN P       GLAZ
a 040 TO FALL (DROP)
b                      001
  040 61 Lahnda          DHAWEN
  040 60 Panjabi ST      DIGGENA
  040 65 Khaskura        LOTNU
  040 56 Singhalese      VITENAWA
b                      002
  040 77 Tadzik          AFTIDAN
  040 76 Persian List    OFTADAN
b                      003
  040 21 Portuguese ST   CAHIR
  040 09 Vlach           KADU
  040 11 Ladin           CRUDER
  040 08 Rumanian List   A CADEA
  040 20 Spanish         CAER
  040 23 Catalan         CAURER
  040 10 Italian         CADERE
  040 22 Brazilian       CAIR
b                      004
  040 13 French          TOMBER
  040 16 French Creole D TOBE
  040 14 Walloon         TOUMER
  040 12 Provencal       TOUMBA
  040 15 French Creole C TOBE
b                      005
  040 17 Sardinian N     RUGERE
  040 19 Sardinian C     ARRUI
  040 18 Sardinian L     RUERE
b                      006
  040 68 Greek Mod       PEFTO
  040 66 Greek ML        PEFTO
  040 70 Greek K         PIPTO
  040 67 Greek MD        PEFTO
  040 69 Greek D         PEFTO
b                      007
  040 04 Welsh C         CWYMPO
  040 03 Welsh N         GOLLWNG, CWYMPO
b                      008
  040 05 Breton List     KOUEZA
  040 07 Breton ST       KOUEZHAN
  040 06 Breton SE       KOEHEIN
b                      009
  040 01 Irish A         TUITIM
  040 02 Irish B         TUITIM
b                      010
  040 74 Afghan          LVEDEL
  040 75 Waziri          PREWATEL, WALWEDEL
b                      011
  040 81 Albanian Top    BIE, AOR. RAS
  040 82 Albanian G      BI (RA, RAN = INF.)
  040 84 Albanian C      BIE, (PRET. RA)
  040 83 Albanian K      BIE (AOR. RAASE)
  040 80 Albanian T      ME RENE
  040 95 ALBANIAN        BI
b                      100
  040 73 Ossetic         XAUYN
  040 78 Baluchi         KHAFAGH, KHAPTA
b                      101
  040 71 Armenian Mod    ENKNEL
  040 72 Armenian List   HANAL
b                      200
c                         200  2  201
  040 30 Swedish Up      FALLA
  040 31 Swedish VL      FAL
  040 27 Afrikaans       VAL
  040 26 Dutch List      VALLEN
  040 25 Penn. Dutch     FOLL
  040 28 Flemish         VALLEN
  040 29 Frisian         FALLE
  040 36 Faroese         FALLA, (DETTA)
  040 33 Danish          FALDE
  040 32 Swedish List    FALLA
  040 34 Riksmal         FALLE
  040 35 Icelandic ST    FALLA
  040 24 German ST       FALLEN
  040 37 English ST      TO FALL
  040 38 Takitaki        FADOM
  040 39 Lithuanian O    PULTI
b                      201
c                         200  2  201
c                         201  2  202
  040 40 Lithuanian ST   (NU)KRISTI, NUPULTI
b                      202
c                         201  2  202
  040 41 Latvian         KRIST
b                      203
c                         203  2  204
c                         203  3  206
  040 63 Bengali         PORA
  040 55 Gypsy Gk        PERAV
  040 59 Gujarati        PERWU
  040 58 Marathi         PEDNE.
  040 57 Kashmiri        PYONU
b                      204
c                         203  2  204
c                         204  2  205
c                         204  3  206
  040 64 Nepali List     GIRNU, PARNU
b                      205
c                         204  2  205
  040 62 Hindi           GIRNA
b                      206
c                         203  3  206
c                         204  3  206
  040 79 Wakhi           PULUN-, WUZ-, PERVE-
b                      207
c                         207  3  208
  040 48 Ukrainian       PADATY
  040 94 BULGARIAN P     PADAM
  040 87 BYELORUSSIAN P  UPASCI
  040 45 Czech           UPADNOUTI
  040 90 CZECH P         PADATI
  040 43 Lusatian L      PADAS
  040 44 Lusatian U      PADAC
  040 93 MACEDONIAN P    PADNAM
  040 50 Polish          PADAC
  040 88 POLISH P        PASC
  040 51 Russian         PADAT
  040 85 RUSSIAN P       PAST
  040 54 Serbocroatian   PASTI
  040 92 SERBOCROATIAN P PASTI
  040 46 Slovak          PADAT
  040 89 SLOVAK P        PADAT
  040 42 Slovenian       PADE
  040 91 SLOVENIAN P     PASTI
  040 86 UKRAINIAN P     UPASTY
  040 53 Bulgarian       DA PADA
  040 49 Byelorussian    PADAC'
  040 47 Czech E         PADNUT
b                      208
c                         207  3  208
  040 52 Macedonian      PAGA, PAGNE
a 041 FAR
b                      001
  041 19 Sardinian C     ATTESU
  041 73 Ossetic         DARD
  041 01 Irish A         FADA, I BHFAD
  041 17 Sardinian N     ILLARGU
  041 20 Spanish         LEJOS
  041 21 Portuguese ST   REMOTO, DISTANTE, LONGE (ADV)
  041 02 Irish B         SIA
  041 11 Ladin           VIA
b                      002
  041 68 Greek Mod       MAKRIA
  041 66 Greek ML        MAKRUA
  041 70 Greek K         MAKRAN
  041 67 Greek MD        MAKRUA
  041 69 Greek D         MAKRIA
b                      003
  041 09 Vlach           DEPARTE
  041 08 Rumanian List   DEPARTE
b                      004
  041 07 Breton ST       PELL
  041 06 Breton SE       PELL
  041 05 Breton List     PELL, DIABELL, LARK
  041 04 Welsh C         PELL
  041 03 Welsh N         PELL
b                      005
  041 82 Albanian G      GJAT, LARG
  041 95 ALBANIAN        LARG, GJAN
  041 81 Albanian Top    LARK
  041 80 Albanian T      LURG
  041 84 Albanian C      GHARGHU
b                      006
  041 24 German ST       WEIT
  041 25 Penn. Dutch     WEIT
b                      007
  041 55 Gypsy Gk        DUR
  041 61 Lahnda          DUR
  041 64 Nepali List     DUR
  041 57 Kashmiri        DUR, DURU
  041 56 Singhalese      DURA
  041 77 Tadzik          DUR
  041 59 Gujarati        DUR
  041 62 Hindi           DUR
  041 63 Bengali         DUR
  041 58 Marathi         DUR
  041 76 Persian List    DUR
b                      200
c                         200  2  201
  041 37 English ST      FAR
  041 33 Danish          FJERN
  041 32 Swedish List    FJARRAN
  041 28 Flemish         VER
  041 29 Frisian         FIER
  041 27 Afrikaans       VER
  041 26 Dutch List      VER
  041 38 Takitaki        FARAWEI, FARA
  041 71 Armenian Mod    HERU
  041 72 Armenian List   HERU
  041 60 Panjabi ST      PERE
  041 83 Albanian K      PARE
b                      201
c                         200  2  201
c                         201  2  202
  041 30 Swedish Up      LANGT BORD, FJARRAN
b                      202
c                         201  2  202
  041 31 Swedish VL      LANGT
  041 36 Faroese         LANGT BURTUR
  041 34 Riksmal         LANGT BORTE
  041 35 Icelandic ST    LANGT (I) BURTU
  041 18 Sardinian L     LONTANU
  041 10 Italian         LONTANO
  041 15 French Creole C LWE
  041 23 Catalan         LLUNY
  041 13 French          LOIN
  041 16 French Creole D LWE
  041 14 Walloon         LON
  041 12 Provencal       LUEN, LIUEN
  041 22 Brazilian       LONGE
b                      203
c                         203  3  204
  041 40 Lithuanian ST   TOLIMAS
  041 39 Lithuanian O    TOLUS
  041 41 Latvian         TALS
b                      204
c                         203  3  204
  041 65 Khaskura        TARA
b                      205
c                         205  3  206
  041 42 Slovenian       DALEC
  041 94 BULGARIAN P     DALEK
  041 87 BYELORUSSIAN P  DAL OKI
  041 45 Czech           DALEKO
  041 90 CZECH P         DALEKY
  041 43 Lusatian L      DALOKI
  041 44 Lusatian U      DALOKI
  041 93 MACEDONIAN P    DALEK
  041 50 Polish          DALEKO
  041 88 POLISH P        DALEKI
  041 51 Russian         DALEKO
  041 85 RUSSIAN P       DAL OKIJ
  041 54 Serbocroatian   DALEK
  041 92 SERBOCROATIAN P DALEK
  041 46 Slovak          D ALEKY
  041 89 SLOVAK P        D ALEKY
  041 91 SLOVENIAN P     DALJEN
  041 86 UKRAINIAN P     DALEKYJ
  041 52 Macedonian      DALEKU
  041 53 Bulgarian       DALEC
  041 48 Ukrainian       DALEKO
  041 49 Byelorussian    DALEKI, DALEKA
  041 47 Czech E         DALEKO
  041 78 Baluchi         DIR
  041 79 Wakhi           DIR
b                      206
c                         205  3  206
  041 74 Afghan          LIRI
  041 75 Waziri          LIRE, WURIYA
a 042 FAT (SUBSTANCE)
b                      000
  042 84 Albanian C
  042 45 Czech
  042 79 Wakhi
b                      001
  042 05 Breton List     LARD
  042 83 Albanian K      LHIPOS
  042 71 Armenian Mod    CARP
  042 76 Persian List    CHARBI
  042 02 Irish B         MEATHAS
  042 61 Lahnda          MOTA
  042 68 Greek Mod       PAKHOS
  042 78 Baluchi         PHIGH
  042 77 Tadzik          RAVWAN
  042 73 Ossetic         SOJ, SOJAG
  042 11 Ladin           SUNDSCHA
  042 75 Waziri          WOZDA
b                      002
  042 22 Brazilian       GORDURA, GORDO
  042 21 Portuguese ST   GORDURA
b                      003
  042 66 Greek ML        LIPOS
  042 70 Greek K         LIPOS
  042 67 Greek MD        LIPOS
  042 69 Greek D         LIPOS, KSUGGI
b                      004
  042 07 Breton ST       DRUZONI
  042 06 Breton SE       DRU, DRUONI
b                      005
  042 89 SLOVAK P        TUK
  042 90 CZECH P         TUK
  042 43 Lusatian L      TUK
  042 44 Lusatian U      TUK
  042 49 Byelorussian    TUK
  042 40 Lithuanian ST   TAUKAI
  042 39 Lithuanian O    TAUKAI
  042 41 Latvian         TAUKS, TREKNS
b                      006
  042 37 English ST      FAT
  042 38 Takitaki        FATOE
  042 30 Swedish Up      FETT
  042 31 Swedish VL      FET
  042 27 Afrikaans       VET
  042 26 Dutch List      VET
  042 25 Penn. Dutch     FETT
  042 28 Flemish         VET
  042 29 Frisian         VET
  042 36 Faroese         FITI, (FEITT)
  042 33 Danish          FEDT
  042 32 Swedish List    FET
  042 34 Riksmal         FETT
  042 35 Icelandic ST    FITA
  042 24 German ST       FETT
b                      007
  042 59 Gujarati        CERBI
  042 60 Panjabi ST      CERBI
  042 62 Hindi           CERBI
  042 63 Bengali         CORBI
  042 58 Marathi         CERBI
  042 57 Kashmiri        BIKH, CARBI
b                      008
  042 64 Nepali List     BOSO
  042 65 Khaskura        BOSO
b                      009
  042 17 Sardinian N     GRASSU
  042 09 Vlach           SEU, GRASEAME
  042 18 Sardinian L     RASSU
  042 15 French Creole C GHWES
  042 08 Rumanian List   GRASIME
  042 13 French          GRAISSE
  042 16 French Creole D GWES
  042 14 Walloon         CRAHE
  042 12 Provencal       GRAISSO
  042 20 Spanish         GRASA
  042 23 Catalan         GRAS, GREIX
  042 10 Italian         GRASSO
  042 19 Sardinian C     GRASSU
b                      100
  042 55 Gypsy Gk        KHOI, THULO
  042 56 Singhalese      TELA
b                      200
c                         200  2  201
  042 04 Welsh C         BRASTER
b                      201
c                         200  2  201
c                         201  2  202
  042 03 Welsh N         BRASTER, BLONEG
b                      202
c                         201  2  202
c                         202  3  203
c                         202  3  400
  042 01 Irish A         BLONAG, GEIR
b                      203
c                         202  3  203
c                         203  3  400
  042 86 UKRAINIAN P     ZYR
  042 51 Russian         ZIR
  042 85 RUSSIAN P       ZYR
b                      400
c                         202  3  400
c                         203  3  400
  042 72 Armenian List   GER
  042 74 Afghan          GVARI
b                      204
c                         204  2  205
  042 46 Slovak          TLSTY
  042 50 Polish          TLUSZCZ
  042 88 POLISH P        TLUSZCZ
  042 87 BYELORUSSIAN P  TLUSC
  042 47 Czech E         TLUSTI
  042 53 Bulgarian       TLESTO
b                      205
c                         204  2  205
c                         205  2  206
  042 48 Ukrainian       TOVSC, SALO
b                      206
c                         205  2  206
c                         206  2  207
  042 52 Macedonian      MAST/LOJ/SALO
b                      207
c                         206  2  207
  042 42 Slovenian       MAST
  042 91 SLOVENIAN P     MAST
  042 54 Serbocroatian   MAST
  042 92 SERBOCROATIAN P MAST
  042 94 BULGARIAN P     MAZ
  042 93 MACEDONIAN P    MAZ
b                      208
c                         208  2  209
  042 81 Albanian Top    DHJAME
  042 80 Albanian T      I, E DHJAMTE
b                      209
c                         208  2  209
c                         209  2  210
  042 82 Albanian G      DHJAMI, LYRA, YNDYRA
b                      210
c                         209  2  210
  042 95 ALBANIAN        LYRA, YNDYRA
a 043 FATHER
b                      001
  043 55 Gypsy Gk        DADE
  043 53 Bulgarian       DASCA
  043 43 Lusatian L      NAN
b                      002
  043 49 Byelorussian    BAC'KA
  043 94 BULGARIAN P     BASTA
  043 87 BYELORUSSIAN P  BAC KA
  043 48 Ukrainian       BAT'KO
b                      200
c                         200  2  201
c                         200  2  202
c                         200  2  206
  043 51 Russian         OTEC
  043 85 RUSSIAN P       OTEC
  043 88 POLISH P        OJCIEC
  043 54 Serbocroatian   OTAC
  043 92 SERBOCROATIAN P OTAC
  043 46 Slovak          OTEC
  043 89 SLOVAK P        OTEC
  043 42 Slovenian       OCE (ATEK)
  043 91 SLOVENIAN P     OCE
  043 86 UKRAINIAN P     OTEC
  043 50 Polish          OJCIEC
  043 44 Lusatian U      WOTC
  043 90 CZECH P         OTEC
  043 45 Czech           OTEC
  043 82 Albanian G      ATI
  043 95 ALBANIAN        ATI
b                      201
c                         200  2  201
c                         201  3  202
c                         201  3  203
c                         201  3  204
c                         201  3  205
c                         201  3  206
c                         201  3  207
c                         201  3  208
c                         201  3  209
c                         201  3  400
  043 47 Czech E         TATA, OTEC
b                      202
c                         200  2  202
c                         201  3  202
c                         202  2  203
c                         202  3  204
c                         202  3  205
c                         202  3  206
c                         202  3  207
c                         202  3  208
c                         202  3  209
c                         202  3  400
  043 84 Albanian C      TATA, JATI
b                      203
c                         201  3  203
c                         202  2  203
c                         203  3  204
c                         203  3  205
c                         203  3  206
c                         203  3  207
c                         203  3  208
c                         203  3  209
c                         203  3  400
  043 83 Albanian K      TATE
b                      204
c                         201  3  204
c                         202  3  204
c                         203  3  204
c                         204  3  205
c                         204  3  206
c                         204  3  207
c                         204  3  208
c                         204  3  209
c                         204  3  400
  043 40 Lithuanian ST   TEVAS
  043 39 Lithuanian O    TEVAS
  043 41 Latvian         TEVS
b                      205
c                         201  3  205
c                         202  3  205
c                         203  3  205
c                         204  3  205
c                         205  3  206
c                         205  3  207
c                         205  3  208
c                         205  3  209
c                         205  3  400
  043 07 Breton ST       TAD
  043 06 Breton SE       TAD
  043 05 Breton List     TAD
  043 04 Welsh C         TAD
  043 03 Welsh N         TAD
b                      206
c                         200  2  206
c                         201  3  206
c                         202  3  206
c                         203  3  206
c                         204  3  206
c                         205  3  206
c                         206  2  207
c                         206  3  208
c                         206  3  209
c                         206  3  400
  043 52 Macedonian      TATKO/OTEC
b                      207
c                         201  3  207
c                         202  3  207
c                         203  3  207
c                         204  3  207
c                         205  3  207
c                         206  2  207
c                         207  3  208
c                         207  3  209
c                         207  3  400
  043 93 MACEDONIAN P    TATKO
b                      208
c                         201  3  208
c                         202  3  208
c                         203  3  208
c                         204  3  208
c                         205  3  208
c                         206  3  208
c                         207  3  208
c                         208  3  209
c                         208  3  400
  043 09 Vlach           TATE, NENI, AFENT, BABA
  043 08 Rumanian List   TATA
b                      209
c                         201  3  209
c                         202  3  209
c                         203  3  209
c                         204  3  209
c                         205  3  209
c                         206  3  209
c                         207  3  209
c                         208  3  209
c                         209  3  400
c                         209  2  210
c                         209  2  211
c                         209  2  213
c                         209  2  216
  043 56 Singhalese      PIYA, TATTA
b                      400
c                         201  3  400
c                         202  3  400
c                         203  3  400
c                         204  3  400
c                         205  3  400
c                         206  3  400
c                         207  3  400
c                         208  3  400
c                         209  3  400
  043 38 Takitaki        TATA, POCPA
  043 79 Wakhi           TUT
b                      210
c                         209  2  210
c                         210  2  211
c                         210  2  213
c                         210  2  216
  043 74 Afghan          PLAR
  043 61 Lahnda          PYU
  043 78 Baluchi         PHITH, PITH
  043 70 Greek K         PATER
  043 67 Greek MD        PATERAS
  043 30 Swedish Up      FAR, FADER
  043 31 Swedish VL      FAR
  043 73 Ossetic         FYD
  043 68 Greek Mod       PATERAS
  043 66 Greek ML        PATERAS
  043 14 Walloon         PERE
  043 12 Provencal       PAIRE, PAI
  043 20 Spanish         PADRE
  043 23 Catalan         PARE
  043 10 Italian         PADRE
  043 13 French          PERE
  043 29 Frisian         FAER
  043 36 Faroese         FADIR
  043 33 Danish          FADER
  043 32 Swedish List    FADER
  043 34 Riksmal         FAR
  043 35 Icelandic ST    FAOIR
  043 24 German ST       VATER
  043 26 Dutch List      VADER
  043 25 Penn. Dutch     FOTTER
  043 77 Tadzik          PADAR
  043 76 Persian List    PEDAR
  043 71 Armenian Mod    HAYR
  043 22 Brazilian       PAI
  043 21 Portuguese ST   PAI
  043 72 Armenian List   HIRE
  043 37 English ST      FATHER
  043 01 Irish A         ATHAIR
  043 02 Irish B         ATHAIR
b                      211
c                         209  2  211
c                         210  2  211
c                         211  3  212
c                         211  2  213
c                         211  3  214
c                         211  3  215
c                         211  2  216
  043 69 Greek D         PATERAS, MPAMPAS
  043 75 Waziri          BABA, PLOR
b                      212
c                         211  3  212
c                         212  3  213
c                         212  3  214
c                         212  3  215
  043 19 Sardinian C     BABBU
  043 17 Sardinian N     BABBU
  043 18 Sardinian L     BABBU
b                      213
c                         209  2  213
c                         210  2  213
c                         211  2  213
c                         212  3  213
c                         213  3  214
c                         213  3  215
c                         213  2  216
  043 60 Panjabi ST      BAP, PYO
b                      214
c                         211  3  214
c                         212  3  214
c                         213  3  214
c                         214  3  215
  043 62 Hindi           BAP, PITA
  043 58 Marathi         VEDIL, BAP
  043 63 Bengali         BABA, BAP
  043 59 Gujarati        BAP, BAPA, BAPU, (PITA)
  043 80 Albanian T      BABA
  043 81 Albanian Top    BABA
  043 11 Ladin           BAP
b                      215
c                         211  3  215
c                         212  3  215
c                         213  3  215
c                         214  3  215
  043 65 Khaskura        BABU
  043 57 Kashmiri        MOLU, BAB
  043 64 Nepali List     BABU
b                      216
c                         209  2  216
c                         210  2  216
c                         211  2  216
c                         213  2  216
c                         216  3  217
  043 28 Flemish         PAPA, VADER
  043 27 Afrikaans       VADER, PA
b                      217
c                         216  3  217
  043 15 French Creole C PAPA
  043 16 French Creole D PAPA
a 044 TO FEAR
b                      000
  044 02 Irish B
  044 25 Penn. Dutch
  044 71 Armenian Mod
b                      001
  044 14 Walloon         AVEUR SOGNE
  044 29 Frisian         EANGJE
  044 80 Albanian T      ME PASUR FRIKE
  044 01 Irish A         TA EAGLA AIR ("THERE IS FEAR ON HIM")
  044 72 Armenian List   VAKHNAL
  044 79 Wakhi           WESI-
b                      002
  044 04 Welsh C         OFNI
  044 03 Welsh N         OFNI
b                      003
  044 34 Riksmal         VAERE REDD
  044 30 Swedish Up      VARA RADD FOR
  044 36 Faroese         RAEDAST, VERA RADDUR
  044 35 Icelandic ST    HRAEOASK, VERA HRAEDDR
b                      004
  044 24 German ST       FURCHTEN
  044 31 Swedish VL      FRUKT
  044 33 Danish          FRYGTE
  044 32 Swedish List    FARHAGA
b                      005
  044 68 Greek Mod       FOVUME
  044 66 Greek ML        FOBAMAI
  044 70 Greek K         FOBOUMAI
  044 67 Greek MD        FOBAMAI
  044 69 Greek D         FOBAMAI
b                      006
  044 07 Breton ST       DOUJAN, KAOUT AON RAK
  044 06 Breton SE       DOUJEIN, EN DEVOUT EUN RAK
  044 05 Breton List     KAOUT AON, DOUJA
b                      007
  044 82 Albanian G      DRUJ, DRUHEM
  044 95 ALBANIAN        DRUJ, DRUHEM
b                      008
  044 81 Albanian Top    TREMBEM, AOR. UTREMBA
  044 84 Albanian C      TREMBEM
  044 83 Albanian K      TREMBEM
b                      009
  044 74 Afghan          BEREDEL
  044 75 Waziri          DAREDEL, WYEREDEL
b                      010
  044 42 Slovenian       STRAH
  044 53 Bulgarian       DA SE STRAXUVA
b                      011
  044 28 Flemish         VREZEN
  044 27 Afrikaans       VREES, BANG WEES
  044 26 Dutch List      VREEZEN
  044 37 English ST      TO FEAR
  044 38 Takitaki        FREDE
b                      200
c                         200  2  201
  044 76 Persian List    TARSIDAN
  044 77 Tadzik          TARSIDAN, VAXMIDAN
  044 73 Ossetic         TAERSYN
  044 78 Baluchi         THURSAGH
  044 55 Gypsy Gk        TRASAV
b                      201
c                         200  2  201
c                         201  2  202
  044 57 Kashmiri        DARUN, TARSUN, KHOTSUN
b                      202
c                         201  2  202
c                         202  2  203
  044 65 Khaskura        DARNU
  044 60 Panjabi ST      DERNA
  044 62 Hindi           DERNA
  044 61 Lahnda          DEREN
  044 64 Nepali List     DARNU
b                      203
c                         202  2  203
c                         203  2  204
  044 59 Gujarati        DERWU, BIHWU
b                      204
c                         203  2  204
  044 40 Lithuanian ST   BIJOTI
  044 39 Lithuanian O    BIJOTI
  044 41 Latvian         BAIDITIES
  044 63 Bengali         BHOE+PAOA
  044 58 Marathi         BHINE.
  044 91 SLOVENIAN P     BOJATI SE
  044 86 UKRAINIAN P     BOJATYS A
  044 46 Slovak          BAT SA
  044 89 SLOVAK P        BAT SA
  044 94 BULGARIAN P     BOJA SE
  044 87 BYELORUSSIAN P  BAJACCA
  044 45 Czech           BATI SE
  044 90 CZECH P         BATI SE
  044 43 Lusatian L      BOJAS SE
  044 44 Lusatian U      BOJEC SO
  044 93 MACEDONIAN P    BOJAM SE
  044 50 Polish          BAC SIE
  044 88 POLISH P        BAC SIE
  044 51 Russian         BOJAT SJA
  044 85 RUSSIAN P       BOJAT S A
  044 54 Serbocroatian   BOJATI SE
  044 92 SERBOCROATIAN P BOJATI SE
  044 56 Singhalese      BAYA
  044 52 Macedonian      BOI SE
  044 48 Ukrainian       LJAKATYS', BOJATYS'
  044 49 Byelorussian    BAJACCA
  044 47 Czech E         BATSA
b                      205
c                         205  2  206
  044 20 Spanish         TEMER
  044 23 Catalan         TEMOREJAR, TEMER
  044 10 Italian         TEMERE
  044 19 Sardinian C     TIMMI
  044 11 Ladin           TMAIR
  044 08 Rumanian List   A SE TEME DE
  044 22 Brazilian       TEMER
  044 21 Portuguese ST   TEMER
  044 17 Sardinian N     TIMERE
  044 18 Sardinian L     TIMERE
b                      206
c                         205  2  206
c                         206  2  207
c                         206  2  208
  044 12 Provencal       CREGNE, TEME
b                      207
c                         206  2  207
c                         207  2  208
  044 13 French          CRAINDRE
b                      208
c                         206  2  208
c                         207  2  208
c                         208  2  209
  044 15 French Creole C PE, KHWEN
b                      209
c                         208  2  209
  044 16 French Creole D PE
  044 09 Vlach           MESPARU
a 045 FEATHER (LARGE)
b                      000
  045 28 Flemish
b                      001
  045 74 Afghan          BENA, BANEKA
  045 63 Bengali         PALOK
  045 67 Greek MD        POUPOULO
  045 73 Ossetic         SIS
  045 41 Latvian         SPALVA
  045 71 Armenian Mod    T`EW
  045 38 Takitaki        WIURRI, FOUWLOE-WIURRI
b                      002
  045 01 Irish A         CLEITE
  045 02 Irish B         CLEITE
b                      003
  045 75 Waziri          PAKHA
  045 55 Gypsy Gk        PHAK
  045 57 Kashmiri        PAKHACH, TIR
  045 64 Nepali List     PWAKH
  045 65 Khaskura        PWANKH
b                      004
  045 81 Albanian Top    PENDE
  045 95 ALBANIAN        PENDA
  045 82 Albanian G      PENDA
  045 84 Albanian C      PEND
  045 83 Albanian K      PENDE
  045 80 Albanian T      PENDE
b                      005
  045 07 Breton ST       PLUENN
  045 06 Breton SE       PLUENN
  045 05 Breton List     PLUN, PLU
  045 04 Welsh C         PLUFYN
  045 03 Welsh N         PLUEN
b                      100
  045 58 Marathi         PIS
  045 56 Singhalese      PIHATTA
  045 59 Gujarati        PICU
b                      200
c                         200  2  201
c                         200  3  203
c                         200  3  204
c                         200  3  205
  045 53 Bulgarian       PERO
  045 48 Ukrainian       LJAK, STRAX, PERO
  045 49 Byelorussian    PERA
  045 47 Czech E         PERO
  045 94 BULGARIAN P     PERO
  045 87 BYELORUSSIAN P  P ARO
  045 45 Czech           PERO
  045 90 CZECH P         PERO
  045 43 Lusatian L      PERO
  045 44 Lusatian U      PJERO
  045 93 MACEDONIAN P    PERO
  045 50 Polish          PIORO
  045 88 POLISH P        PIORO
  045 51 Russian         PERO
  045 85 RUSSIAN P       PERO
  045 54 Serbocroatian   PERO
  045 92 SERBOCROATIAN P PERO
  045 46 Slovak          PERO
  045 89 SLOVAK P        PERO
  045 42 Slovenian       PERU
  045 91 SLOVENIAN P     PERO
  045 86 UKRAINIAN P     PERO
  045 52 Macedonian      PERO, PERJE, PERJA
  045 77 Tadzik          PAR
  045 62 Hindi           PER
  045 76 Persian List    PAR
  045 79 Wakhi           PUR
  045 61 Lahnda          PER
b                      201
c                         200  2  201
c                         201  2  202
c                         201  3  203
c                         201  3  204
c                         201  3  205
  045 78 Baluchi         PHAR, KHAMB
b                      202
c                         201  2  202
  045 60 Panjabi ST      KHEMB
b                      203
c                         200  3  203
c                         201  3  203
c                         203  3  204
c                         203  2  205
  045 37 English ST      FEATHER
  045 29 Frisian         FEAR
  045 36 Faroese         FJODUR
  045 33 Danish          FJER
  045 32 Swedish List    FJADER
  045 34 Riksmal         FJAER
  045 35 Icelandic ST    FJOOUR
  045 24 German ST       FEDER
  045 26 Dutch List      VEDER
  045 25 Penn. Dutch     FEDDER
  045 30 Swedish Up      FJADER
  045 31 Swedish VL      FJAR  FJER
  045 68 Greek Mod       FTERO
  045 66 Greek ML        FTERO
  045 70 Greek K         PTERUKS
  045 69 Greek D         FTEROUGA
  045 27 Afrikaans       VEER, PLUIM
  045 19 Sardinian C     PINNA
  045 11 Ladin           PENNA
  045 09 Vlach           PEANE
  045 17 Sardinian N     PIA
  045 08 Rumanian List   PANA
b                      204
c                         200  3  204
c                         201  3  204
c                         203  3  204
c                         204  3  205
  045 72 Armenian List   PEDUR
b                      205
c                         200  3  205
c                         201  3  205
c                         203  2  205
c                         204  3  205
c                         205  2  206
  045 21 Portuguese ST   PENNA, PLUMA
b                      206
c                         205  2  206
  045 22 Brazilian       PLUMA
  045 13 French          PLUME (D'OISEAU)
  045 15 French Creole C PLIM
  045 16 French Creole D PLIM
  045 14 Walloon         PLOME
  045 12 Provencal       PLUMO
  045 20 Spanish         PLUMA
  045 23 Catalan         PLOMA
  045 10 Italian         PIUMA
  045 18 Sardinian L     PIUMAGGIU
  045 40 Lithuanian ST   PLUNKSNA
  045 39 Lithuanian O    PLUNKENA
a 046 FEW
b                      000
  046 88 POLISH P
  046 90 CZECH P
  046 43 Lusatian L
  046 44 Lusatian U
  046 93 MACEDONIAN P
  046 94 BULGARIAN P
  046 87 BYELORUSSIAN P
  046 85 RUSSIAN P
  046 92 SERBOCROATIAN P
  046 89 SLOVAK P
  046 86 UKRAINIAN P
  046 91 SLOVENIAN P
  046 09 Vlach
b                      001
  046 83 Albanian K      CA
  046 72 Armenian List   KANI
  046 49 Byelorussian    KRYXU, TROXI
  046 57 Kashmiri        MAINAY
  046 41 Latvian         MAZLIET, DRUSKU, DAZI
  046 40 Lithuanian ST   NEDAUG
  046 42 Slovenian       (MOLO) NEKAJ
  046 63 Bengali         OLPO
  046 47 Czech E         PAR
  046 08 Rumanian List   PUTINI, PUTINE
  046 29 Frisian         RUSKE
  046 56 Singhalese      TIKA
  046 55 Gypsy Gk        XARNWK
b                      002
  046 37 English ST      FEW
  046 30 Swedish Up      FA, NAGRA
  046 31 Swedish VL      FA
  046 36 Faroese         FAIR
  046 33 Danish          FAA
  046 32 Swedish List    FA
  046 34 Riksmal         FA
  046 35 Icelandic ST    FAIR
  046 17 Sardinian N     PAKOS
  046 18 Sardinian L     PAGOS
  046 15 French Creole C PE
  046 13 French          PEU
  046 16 French Creole D PE
  046 14 Walloon         PO
  046 12 Provencal       PAU, GAIRE
  046 20 Spanish         POCO
  046 23 Catalan         POCH, MICA
  046 10 Italian         POCHI, POCHE
  046 19 Sardinian C     PAGUS
  046 11 Ladin           POCHA
  046 22 Brazilian       POUCOS
  046 21 Portuguese ST   POUCOS
b                      003
  046 01 Irish A         BEAGAN
  046 02 Irish B         BEAGAN
b                      004
  046 04 Welsh C         YCHYDIG
  046 03 Welsh N         YCHYDIG
b                      005
  046 05 Breton List     NEBEUT
  046 07 Breton ST       NEBEUT A
  046 06 Breton SE       NEBET A
b                      006
  046 81 Albanian Top    PAK
  046 80 Albanian T      PAK, DISA
  046 95 ALBANIAN        PAK
  046 82 Albanian G      PAK
  046 84 Albanian C      PAK
b                      007
  046 68 Greek Mod       LIYI
  046 66 Greek ML        LIGOI (M. PL. NOM.)
  046 70 Greek K         OLIGOI
  046 67 Greek MD        MERIKOI, LIGOI
  046 69 Greek D         LIGOI
b                      008
  046 74 Afghan          LEZ
  046 75 Waziri          LEZH, LEZHKI
b                      100
  046 48 Ukrainian       KIL'KA
  046 39 Lithuanian O    KELI
b                      101
  046 71 Armenian Mod    K`IC`
  046 73 Ossetic         CYSYL
b                      200
c                         200  3  201
c                         200  2  202
  046 53 Bulgarian       MALKO
  046 50 Polish          MALO
  046 45 Czech           MALO
  046 51 Russian         MALO
b                      201
c                         200  3  201
c                         201  2  202
c                         201  2  203
  046 52 Macedonian      NEKOLKU/MALOBROEN
b                      202
c                         200  2  202
c                         201  2  202
c                         202  2  203
  046 46 Slovak          NIEKOLKO, MALO
b                      203
c                         201  2  203
c                         202  2  203
  046 54 Serbocroatian   NEKOLIKO
b                      204
c                         204  3  205
  046 76 Persian List    KAM
  046 78 Baluchi         KHARDE, KHAM
  046 79 Wakhi           KUM
  046 77 Tadzik          KAM, NOKIFOJA
b                      205
c                         204  3  205
c                         205  2  206
  046 65 Khaskura        KAMTI, THORAI
b                      206
c                         205  2  206
  046 59 Gujarati        THORU
  046 58 Marathi         THODA
  046 60 Panjabi ST      THORA
  046 62 Hindi           THORA
  046 61 Lahnda          THORE
  046 64 Nepali List     THOR
b                      207
c                         207  2  208
  046 24 German ST       WENIG
  046 28 Flemish         WEINIG
  046 26 Dutch List      WEINIG
  046 38 Takitaki        WEINIKI, PIKIN, NO FOELOE
b                      208
c                         207  2  208
c                         208  2  209
  046 27 Afrikaans        N PAAR, WEINIG
b                      209
c                         208  2  209
  046 25 Penn. Dutch     PAWR
a 047 TO FIGHT
b                      000
  047 09 Vlach
  047 55 Gypsy Gk
  047 05 Breton List
  047 35 Icelandic ST
b                      001
  047 19 Sardinian C     CERTAI
  047 29 Frisian         DEILJE
  047 51 Russian         DRAT SJA
  047 17 Sardinian N     GERRARE
  047 72 Armenian List   GURVIL
  047 83 Albanian K      LEKSEM
  047 78 Baluchi         MIRAGH, MIRATHA
  047 39 Lithuanian O    MUSTIS
  047 71 Armenian Mod    PAYK`AR, KRIW
  047 56 Singhalese      SANDU/KARANWA
  047 52 Macedonian      STEPA
  047 42 Slovenian       TJEPES
  047 73 Ossetic         XYL KAENYN, TOX KAENYN
  047 84 Albanian C      ZEXEM
b                      002
  047 65 Khaskura        LARNU
  047 64 Nepali List     JUJHNU, LARNU
  047 57 Kashmiri        LADUN
  047 61 Lahnda          LEREN
  047 59 Gujarati        LEREWU
  047 60 Panjabi ST      LERNA
  047 62 Hindi           LERNA
  047 63 Bengali         LORA
  047 58 Marathi         LEDHNE.
b                      003
  047 41 Latvian         KAUTIES, SISTIES, CINITIES
  047 40 Lithuanian ST   KOVOTI
b                      004
  047 33 Danish          KAEMPE
  047 24 German ST       KAMPFEN
b                      005
  047 68 Greek Mod       POLEMO
  047 66 Greek ML        POLEMO
  047 70 Greek K         POLEMO
  047 67 Greek MD        PALEUO, POLEMO
  047 69 Greek D         POLEMAO
b                      006
  047 76 Persian List    JANGIDAN (DA'VA KARDAN)
  047 79 Wakhi           JUNG TSER-
  047 74 Afghan          DZANGEDEL
  047 77 Tadzik          CANG KARDAN, MUBORIZA KARDAN
  047 75 Waziri          JANG, JAGGARRA BALWA (FIGHTING)
b                      007
  047 81 Albanian Top    LEFTON, AOR. LEFTOVA/ ZIEM, AOR. UZUZE  UZURA
  047 80 Albanian T      ME LEFTUAR
  047 95 ALBANIAN        LUFTOJ
  047 82 Albanian G      LUFTOJ
b                      008
  047 93 MACEDONIAN P    BORAM SE
  047 94 BULGARIAN P     BOR A SE
  047 89 SLOVAK P        BORIT SA
  047 91 SLOVENIAN P     BORITI SE
  047 86 UKRAINIAN P     BOROTYS A
  047 85 RUSSIAN P       BOROT S A
  047 54 Serbocroatian   BORITI SE
  047 92 SERBOCROATIAN P BORITI SE
b                      009
  047 04 Welsh C         YMLADD
  047 03 Welsh N         YMLADD
b                      010
  047 07 Breton ST       EN EM GANNAN
  047 06 Breton SE       EMGANNEIN
b                      011
  047 90 CZECH P         BOJOVATI
  047 43 Lusatian L      WOJOWAS
  047 44 Lusatian U      WOJOWAC
  047 45 Czech           BOJOVATI, ZAPASITI
  047 88 POLISH P        WOJOWAC
  047 87 BYELORUSSIAN P  VAJAVAC
  047 46 Slovak          BIT SA, BOJOVAT , ZAPASIT
  047 47 Czech E         BITSA
  047 50 Polish          BIC SIE
  047 53 Bulgarian       DA SE BIE
  047 48 Ukrainian       BYTYS'
  047 49 Byelorussian    BICCA
b                      200
c                         200  2  201
  047 34 Riksmal         SLASS
  047 36 Faroese         BERJAST, SLAAST
  047 31 Swedish VL      SLAS  SLOS
b                      201
c                         200  2  201
c                         201  2  202
  047 30 Swedish Up      SLASS, FAKTA
b                      202
c                         201  2  202
  047 25 Penn. Dutch     FECHT
  047 28 Flemish         VECHTEN
  047 27 Afrikaans       VEG
  047 26 Dutch List      VECHTEN
  047 37 English ST      TO FIGHT
  047 38 Takitaki        FETI
b                      203
c                         203  3  204
  047 01 Irish A         TROID
  047 02 Irish B         CATHUIGH IM, TROIDIM, IOMBUAILIM
b                      204
c                         203  3  204
  047 32 Swedish List    STRIDA
b                      205
c                         205  3  206
  047 18 Sardinian L     CUMBATTERE
  047 11 Ladin           CUMBATTER
  047 14 Walloon         SI BATE, SI K'BATE, SI PINGHI
  047 12 Provencal       SE BATRE, CO
  047 20 Spanish         BATALLAR, COMBATIR
  047 10 Italian         COMBATTERE
  047 13 French          SE BATTRE
  047 22 Brazilian       COMBATER
  047 21 Portuguese ST   PELEJAR, COMBATER
  047 08 Rumanian List   A (SE) BATE, A (SE) LUPTA
  047 23 Catalan         LLUYTAR, BATALLAR, BREGAR, COMBATRER
b                      206
c                         205  3  206
  047 16 French Creole D GUME
  047 15 French Creole C GUME
a 048 FIRE
b                      001
  048 61 Lahnda          BHA
  048 56 Singhalese      GINDARA
  048 72 Armenian List   GURAG
  048 57 Kashmiri        NAR
  048 79 Wakhi           RUXUNIGH
  048 54 Serbocroatian   VATRA
b                      002
  048 14 Walloon         FEU
  048 09 Vlach           FOKU
  048 17 Sardinian N     OKU
  048 18 Sardinian L     FOGU
  048 15 French Creole C DIFE
  048 16 French Creole D DIFE
  048 12 Provencal       FIO
  048 20 Spanish         FUEGO
  048 23 Catalan         FOCH
  048 10 Italian         FUOCO
  048 19 Sardinian C     FOGU
  048 11 Ladin           FO
  048 08 Rumanian List   FOC
  048 13 French          FEU
  048 22 Brazilian       FOGO
  048 21 Portuguese ST   FOGO, LUME
b                      003
  048 37 English ST      FIRE
  048 38 Takitaki        FAJA
  048 24 German ST       FEUER
  048 27 Afrikaans       VUUR
  048 26 Dutch List      VUUR
  048 25 Penn. Dutch     FEIER
  048 28 Flemish         VUER, BRAND
  048 29 Frisian         BRAN, FJUR
  048 71 Armenian Mod    KRAK, HUR
  048 70 Greek K         PUR
b                      004
  048 59 Gujarati        AG
  048 65 Khaskura        AGO
  048 60 Panjabi ST      EGG
  048 62 Hindi           AG
  048 63 Bengali         AGUN
  048 58 Marathi         AG
  048 64 Nepali List     AGO
  048 52 Macedonian      OGAN/OGNI
  048 55 Gypsy Gk        YAK
  048 92 SERBOCROATIAN P OGANJ
  048 46 Slovak          OHEN
  048 89 SLOVAK P        OHEN
  048 42 Slovenian       OGEN
  048 91 SLOVENIAN P     OGENJ
  048 86 UKRAINIAN P     VOHON
  048 40 Lithuanian ST   UGNIS
  048 39 Lithuanian O    UGNIS
  048 41 Latvian         UGUNS
  048 94 BULGARIAN P     OGUN
  048 87 BYELORUSSIAN P  AHON
  048 45 Czech           OHEN
  048 90 CZECH P         OHEN
  048 43 Lusatian L      HOGEN
  048 44 Lusatian U      WOHEN
  048 93 MACEDONIAN P    OGON
  048 50 Polish          OGIEN
  048 88 POLISH P        OGIEN
  048 51 Russian         OGON
  048 85 RUSSIAN P       OGON
  048 53 Bulgarian       OGEN
  048 48 Ukrainian       VOGON'
  048 49 Byelorussian    VAGON'
  048 47 Czech E         OHENY
b                      005
  048 33 Danish          ILD
  048 35 Icelandic ST    ELDR
  048 36 Faroese         ELDUR
  048 32 Swedish List    ELD  EN
  048 30 Swedish Up      ELD
  048 31 Swedish VL      AL
b                      006
  048 07 Breton ST       TAN
  048 06 Breton SE       TAN
  048 05 Breton List     TAN
  048 04 Welsh C         TAN
  048 03 Welsh N         TAN
  048 01 Irish A         TEINE
  048 02 Irish B         TEINE
b                      007
  048 67 Greek MD        FOTIA
  048 69 Greek D         FOTIA
  048 68 Greek Mod       FOTYA
  048 66 Greek ML        FOTIA
b                      008
  048 81 Albanian Top    ZJAR
  048 82 Albanian G      ZJARRI
  048 84 Albanian C      ZJAR
  048 83 Albanian K      ZJARM
  048 80 Albanian T      ZJARR
  048 95 ALBANIAN        ZJARRI
  048 34 Riksmal         VARME
b                      009
  048 75 Waziri          YOR
  048 74 Afghan          OR
b                      200
c                         200  3  201
  048 77 Tadzik          OTAS, ALOV
  048 76 Persian List    ATASH
  048 73 Ossetic         ZYNG, ART, CAEXAER
b                      201
c                         200  3  201
  048 78 Baluchi         AS
a 049 FISH
b                      000
  049 75 Waziri
b                      001
  049 57 Kashmiri        GAD
  049 73 Ossetic         KAESAG
b                      002
  049 60 Panjabi ST      MECCHI
  049 62 Hindi           MECHLI
  049 63 Bengali         MAC
  049 58 Marathi         MASA
  049 76 Persian List    MAHI
  049 55 Gypsy Gk        MACHO
  049 56 Singhalese      MALU
  049 61 Lahnda          MECHLI
  049 64 Nepali List     MACHO
  049 78 Baluchi         MAHI
  049 77 Tadzik          MOXI
  049 59 Gujarati        MACHELI
  049 65 Khaskura        MACHHA
b                      003
  049 87 BYELORUSSIAN P  RYBA
  049 94 BULGARIAN P     RIBA
  049 45 Czech           RYBA
  049 90 CZECH P         RYBA
  049 43 Lusatian L      RYBA
  049 44 Lusatian U      RYBA
  049 93 MACEDONIAN P    RIBA
  049 50 Polish          RYBA
  049 88 POLISH P        RYBA
  049 51 Russian         RYBA
  049 85 RUSSIAN P       RYBA
  049 54 Serbocroatian   RIBA
  049 92 SERBOCROATIAN P RIBA
  049 46 Slovak          RYBA
  049 89 SLOVAK P        RYBA
  049 42 Slovenian       RIBA
  049 91 SLOVENIAN P     RIBA
  049 86 UKRAINIAN P     RYBA
  049 52 Macedonian      RIBA
  049 53 Bulgarian       RIBA
  049 48 Ukrainian       RYBA
  049 49 Byelorussian    RYBA
  049 47 Czech E         RIBA
b                      004
  049 70 Greek K         ICHTHUS
  049 40 Lithuanian ST   ZUVIS
  049 39 Lithuanian O    ZUVIS
  049 41 Latvian         ZIVS
  049 71 Armenian Mod    JUK
  049 72 Armenian List   ZOOK
b                      005
  049 68 Greek Mod       PSARI
  049 66 Greek ML        PSARI
  049 67 Greek MD        PSARI
  049 69 Greek D         PSARI
b                      006
  049 79 Wakhi           KUP
  049 74 Afghan          KAB
b                      007
  049 04 Welsh C         PISGODYN
  049 03 Welsh N         PYSGODYN
  049 07 Breton ST       PESK
  049 06 Breton SE       PESK
  049 05 Breton List     PESK
b                      008
  049 82 Albanian G      PESHKU
  049 84 Albanian C      PISK
  049 83 Albanian K      PISK
  049 80 Albanian T      PESHK
  049 95 ALBANIAN        PESHKU
  049 81 Albanian Top    PESK
b                      009
  049 30 Swedish Up      FISK
  049 31 Swedish VL      FISK
  049 27 Afrikaans       VIS
  049 26 Dutch List      VISCH
  049 25 Penn. Dutch     FISCH
  049 28 Flemish         VISCH
  049 29 Frisian         FISK
  049 36 Faroese         FISKUR
  049 33 Danish          FISK
  049 32 Swedish List    FISK
  049 34 Riksmal         FISK
  049 35 Icelandic ST    FISKR
  049 24 German ST       FISCHE
  049 37 English ST      FISH
  049 38 Takitaki        FISI
  049 12 Provencal       PEIS, PEISSOUN
  049 15 French Creole C PWESO
  049 13 French          POISSON
  049 16 French Creole D PWESO
  049 14 Walloon         PEHON
  049 01 Irish A         IASC
  049 02 Irish B         IASC
  049 17 Sardinian N     PISKE
  049 18 Sardinian L     PISCHE
  049 22 Brazilian       PEIXE
  049 21 Portuguese ST   PEIXE
  049 09 Vlach           PEASTE
  049 20 Spanish         PEZ
  049 23 Catalan         PEIX
  049 10 Italian         PESCE
  049 19 Sardinian C     PISSI
  049 11 Ladin           PESCH
  049 08 Rumanian List   PESTE
a 050 FIVE
b                      002
  050 37 English ST      FIVE
  050 30 Swedish Up      FEM
  050 31 Swedish VL      FAM
  050 24 German ST       FUNF
  050 27 Afrikaans       VYF
  050 26 Dutch List      VIJF
  050 25 Penn. Dutch     FINFE
  050 28 Flemish         VYF
  050 29 Frisian         FIIF
  050 36 Faroese         FIMM
  050 33 Danish          FEM
  050 32 Swedish List    FEM
  050 34 Riksmal         FEM
  050 35 Icelandic ST    FIMM
  050 38 Takitaki        FEIFI
  050 55 Gypsy Gk        PANCH
  050 73 Ossetic         FONDZ
  050 74 Afghan          PINDZE
  050 78 Baluchi         PHANCH
  050 79 Wakhi           PANZ
  050 61 Lahnda          PENJ
  050 64 Nepali List     PAC
  050 57 Kashmiri        PANTS
  050 56 Singhalese      PAHA
  050 77 Tadzik          PANC
  050 59 Gujarati        PAE
  050 65 Khaskura        PANCH
  050 60 Panjabi ST      PENJ
  050 62 Hindi           PAC
  050 63 Bengali         PAC
  050 58 Marathi         PAC
  050 76 Persian List    PANJ
  050 75 Waziri          PINZE
  050 07 Breton ST       PEMP
  050 06 Breton SE       PEMP
  050 05 Breton List     PEMP
  050 04 Welsh C         PUMP
  050 03 Welsh N         PUMP
  050 68 Greek Mod       PENDE
  050 66 Greek ML        PENTE
  050 70 Greek K         PENTE
  050 67 Greek MD        PENTE
  050 69 Greek D         PENTE
  050 40 Lithuanian ST   PENKI
  050 39 Lithuanian O    PENKI
  050 81 Albanian Top    PESE
  050 82 Albanian G      PES
  050 84 Albanian C      PES
  050 83 Albanian K      PESE
  050 80 Albanian T      PESE
  050 95 ALBANIAN        PES
  050 17 Sardinian N     KIMBE
  050 18 Sardinian L     CHIMBE
  050 09 Vlach           CINJE
  050 15 French Creole C SEK
  050 13 French          CINQ
  050 16 French Creole D SEK
  050 14 Walloon         CINQ'
  050 12 Provencal       CINQ
  050 20 Spanish         CINCO
  050 23 Catalan         CINCH
  050 10 Italian         CINQUE
  050 19 Sardinian C     CINKU
  050 11 Ladin           TSCHINCH
  050 08 Rumanian List   CINCI
  050 22 Brazilian       CINCO
  050 21 Portuguese ST   CINCO
  050 71 Armenian Mod    HING
  050 72 Armenian List   HING
  050 01 Irish A         CUIG
  050 94 BULGARIAN P     PET
  050 87 BYELORUSSIAN P  P AC
  050 45 Czech           PET
  050 90 CZECH P         PET
  050 43 Lusatian L      PES
  050 44 Lusatian U      PJEC
  050 93 MACEDONIAN P    PET
  050 50 Polish          PIEC
  050 88 POLISH P        PIEC
  050 51 Russian         PJAT
  050 85 RUSSIAN P       P AT
  050 54 Serbocroatian   PET
  050 92 SERBOCROATIAN P PET
  050 46 Slovak          PAT
  050 89 SLOVAK P        PAT
  050 42 Slovenian       PJT
  050 91 SLOVENIAN P     PET
  050 86 UKRAINIAN P     P AT
  050 52 Macedonian      PET
  050 53 Bulgarian       PET
  050 48 Ukrainian       P'JAT'
  050 49 Byelorussian    PJAC'
  050 47 Czech E         PYET
  050 41 Latvian         PIECI
  050 02 Irish B         CUIGEAR
a 051 TO FLOAT
b                      000
  051 09 Vlach
  051 55 Gypsy Gk
  051 91 SLOVENIAN P
  051 86 UKRAINIAN P
  051 89 SLOVAK P
  051 92 SERBOCROATIAN P
  051 85 RUSSIAN P
  051 88 POLISH P
  051 90 CZECH P
  051 43 Lusatian L
  051 44 Lusatian U
  051 93 MACEDONIAN P
  051 94 BULGARIAN P
  051 87 BYELORUSSIAN P
  051 79 Wakhi
  051 11 Ladin
  051 02 Irish B
  051 24 German ST
  051 25 Penn. Dutch
  051 82 Albanian G
  051 84 Albanian C
  051 76 Persian List
b                      001
  051 95 ALBANIAN        BAJ NOT
  051 63 Bengali         BHASA
  051 72 Armenian List   DADANIL
  051 53 Bulgarian       DA SE NOSI
  051 29 Frisian         DOBBERJE
  051 20 Spanish         FLOTAR
  051 74 Afghan          GERZEDEL, CALEDEL
  051 81 Albanian Top    JAM MBI VALET
  051 73 Ossetic         LENK KAENYN
  051 78 Baluchi         LURAGH, LURITHA
  051 71 Armenian Mod    LUAL
  051 80 Albanian T      ME LUNDRUAR
  051 08 Rumanian List   A PLUTI
  051 77 Tadzik          SINO KARDAN, SINOVARI KARDAN
  051 23 Catalan         SURAR, FREGAR
  051 38 Takitaki        SWEM
  051 83 Albanian K      VETE MBII DEET
  051 57 Kashmiri        YIRUN
b                      002
  051 59 Gujarati        TEREWU
  051 60 Panjabi ST      TERNA
  051 58 Marathi         TERNE.
  051 61 Lahnda          TAEREN
  051 62 Hindi           UTERANA
b                      003
  051 13 French          FLOTTER
  051 16 French Creole D FLOTE
  051 14 Walloon         FLOTER
  051 12 Provencal       FLOUTA, FLOUQUEJA
  051 15 French Creole C FLOTE
b                      004
  051 04 Welsh C         NOFIO
  051 03 Welsh N         NOFIO
  051 07 Breton ST       NEUIN, NEUNVIAL
  051 06 Breton SE       NEANNEIN
  051 05 Breton List     NEUI, BEZA WAR NEUN, WAR VORDO
  051 01 Irish A         SNAMH
b                      005
  051 37 English ST      TO FLOAT
  051 30 Swedish Up      FLYTA
  051 31 Swedish VL      FLYT
  051 36 Faroese         FLOTA
  051 33 Danish          FLYDE
  051 32 Swedish List    FLYTA
  051 34 Riksmal         FLYTE
  051 35 Icelandic ST    FLJOTA
  051 42 Slovenian       PLAVAT
  051 46 Slovak          PLAVAT
  051 54 Serbocroatian   PLOVITI
  051 51 Russian         PLAVAT
  051 50 Polish          PLYNAC
  051 68 Greek Mod       PLEO
  051 66 Greek ML        PLEBO
  051 70 Greek K         PLEO
  051 67 Greek MD        PLEO
  051 69 Greek D         PLEO
  051 40 Lithuanian ST   PLAUKTI
  051 39 Lithuanian O    PLAUKYTI
  051 41 Latvian         PELDET
  051 52 Macedonian      PLIVA, PLOVI
  051 49 Byelorussian    PLAVAC'
  051 48 Ukrainian       PLAVATY
b                      006
  051 28 Flemish         DRYVEN
  051 27 Afrikaans       DRYF, DRYWE
  051 26 Dutch List      DRIJVEN
b                      007
  051 22 Brazilian       ABOIAR
  051 21 Portuguese ST   ABOIAR
b                      008
  051 17 Sardinian N     GALLEJJARE
  051 18 Sardinian L     GALLIZZARE
  051 10 Italian         GALLEGGIARE
  051 19 Sardinian C     GALLEGAI
b                      100
  051 65 Khaskura        BAHNU, BAGNU
  051 75 Waziri          BAIYEDEL
b                      101
  051 47 Czech E         STAT NA VODE
  051 45 Czech           VZNASETI SE, DRZETI SE NA VODE
b                      102
  051 64 Nepali List     PAURANU
  051 56 Singhalese      PAVENAWA
a 052 TO FLOW
b                      000
  052 09 Vlach
  052 55 Gypsy Gk
  052 84 Albanian C
b                      001
  052 56 Singhalese      GALANAWA
  052 02 Irish B         GUISIM
  052 25 Penn. Dutch     LAWF
  052 79 Wakhi           REC-, CAU
b                      002
  052 72 Armenian List   HOSIL
  052 71 Armenian Mod    HOSEL
b                      003
  052 04 Welsh C         LLIFO
  052 03 Welsh N         LLIFO
b                      004
  052 91 SLOVENIAN P     TECI
  052 86 UKRAINIAN P     TEKTY
  052 89 SLOVAK P        TIECT
  052 94 BULGARIAN P     TEKA
  052 87 BYELORUSSIAN P  C ACY
  052 45 Czech           TECI
  052 90 CZECH P         TECI
  052 43 Lusatian L      SAC
  052 44 Lusatian U      CEC
  052 93 MACEDONIAN P    TECAM
  052 50 Polish          CIEC
  052 88 POLISH P        CIEC
  052 51 Russian         TEC
  052 85 RUSSIAN P       TEC
  052 54 Serbocroatian   TECI
  052 92 SERBOCROATIAN P TECI
  052 39 Lithuanian O    TEKETI, BEGTI
  052 40 Lithuanian ST   TEKETI
  052 52 Macedonian      TECE
  052 47 Czech E         TECIT
  052 53 Bulgarian       DA TECE
  052 48 Ukrainian       TEKTY
b                      005
  052 07 Breton ST       REDEK, BERAN
  052 01 Irish A         RITH
  052 06 Breton SE       RIDEK, BEREIN
  052 05 Breton List     BERA, DIVERA, REDEK
b                      006
  052 82 Albanian G      RRJEDH
  052 81 Albanian Top    RIETH, AOR. RODHA
  052 83 Albanian K      RETH
  052 80 Albanian T      ME RJEDHUR
  052 95 ALBANIAN        RJEDH, (RODHA = AOR.)
b                      100
  052 77 Tadzik          CORI SUD
  052 76 Persian List    JARI SHODAN
b                      200
c                         200  2  201
c                         200  2  203
c                         200  2  204
  052 37 English ST      TO FLOW
  052 33 Danish          FLYDE
  052 24 German ST       FLIESSEN
  052 42 Slovenian       PLAVATI
  052 46 Slovak          PLYNUT
  052 49 Byelorussian    PLYC'
  052 41 Latvian         PLUST
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  2  204
  052 30 Swedish Up      RINNA, FLYTA
  052 31 Swedish VL      RIN, FLYT
b                      202
c                         201  2  202
c                         202  2  203
  052 34 Riksmal         RENNE
  052 35 Icelandic ST    RENNA
  052 38 Takitaki        RON
  052 36 Faroese         RENNA
b                      203
c                         200  2  203
c                         201  2  203
c                         202  2  203
c                         203  2  204
c                         203  2  205
  052 32 Swedish List    FLYTA, RINNA, STROMMA
b                      204
c                         200  2  204
c                         201  2  204
c                         203  2  204
c                         204  2  205
  052 27 Afrikaans       VLOEI, STROOM
  052 26 Dutch List      STROOMEN, VLOEIEN
b                      205
c                         203  2  205
c                         204  2  205
  052 28 Flemish         STROMEN
  052 29 Frisian         STROME
b                      206
c                         206  2  207
  052 68 Greek Mod       REO
  052 70 Greek K         REO
b                      207
c                         206  2  207
c                         207  2  208
  052 67 Greek MD        REO, TRECHO
b                      208
c                         207  2  208
  052 69 Greek D         TRECHO
  052 66 Greek ML        TRECHEI (3 SG.)
b                      209
c                         209  2  210
c                         209  2  213
  052 14 Walloon         COLER
  052 13 French          COULER
  052 16 French Creole D KULE
  052 15 French Creole C KULE
b                      210
c                         209  2  210
c                         210  2  211
c                         210  2  213
  052 12 Provencal       COULA, RAJA
b                      211
c                         210  2  211
c                         211  2  212
c                         211  2  213
  052 23 Catalan         CORRER, RAJAR
b                      212
c                         211  2  212
c                         212  2  213
  052 21 Portuguese ST   CORRER
  052 17 Sardinian N     ISKURRERE
  052 18 Sardinian L     ISCURRERE
  052 22 Brazilian       ESCORRER
  052 08 Rumanian List   A CURGE
  052 19 Sardinian C     KURRI
b                      213
c                         209  2  213
c                         210  2  213
c                         211  2  213
c                         212  2  213
c                         213  2  214
  052 10 Italian         SCORRERE, COLARE, FLUIRE
b                      214
c                         213  2  214
  052 11 Ladin           FLUIR
  052 20 Spanish         FLUIR
b                      215
c                         215  2  216
c                         215  3  218
c                         215  3  219
  052 58 Marathi         VAHNE.
  052 62 Hindi           BEHNA
  052 74 Afghan          BAHEDEL, TOJEDEL
  052 78 Baluchi         BAHAGH, BAHITHA
  052 57 Kashmiri        WAHUN
  052 59 Gujarati        WEHEWU
  052 61 Lahnda          WAWEN
b                      216
c                         215  2  216
c                         216  2  217
c                         216  3  218
c                         216  3  219
  052 65 Khaskura        BAHANU, BAGNU
  052 64 Nepali List     BAGNU, BAHANU
b                      217
c                         216  2  217
  052 60 Panjabi ST      VEGNA
b                      218
c                         215  3  218
c                         216  3  218
c                         218  3  219
  052 73 Ossetic         CAEUYN, UAJYN, KAELYN
  052 75 Waziri          BAIYEDEL
b                      219
c                         215  3  219
c                         216  3  219
c                         218  3  219
  052 63 Bengali         BOOA
a 053 FLOWER
b                      001
  053 70 Greek K         ANTHOS
  053 73 Ossetic         DIDINAEG
  053 37 English ST      FLOWER
  053 09 Vlach           LILICE
  053 55 Gypsy Gk        LULUGI
  053 56 Singhalese      MALA
  053 57 Kashmiri        POSH, GUL
  053 41 Latvian         PUKE
  053 72 Armenian List   ZAGHEG
b                      002
  053 26 Dutch List      BLOEM
  053 25 Penn. Dutch     BLUUM
  053 30 Swedish Up      BLOMMA
  053 31 Swedish VL      BLOMA
  053 27 Afrikaans       BLOM
  053 28 Flemish         BLOEM
  053 29 Frisian         BLOM
  053 36 Faroese         BLOMA
  053 33 Danish          BLOMST
  053 32 Swedish List    BLOMMA
  053 34 Riksmal         BLOMST
  053 35 Icelandic ST    BLOM
  053 24 German ST       BLUME
  053 38 Takitaki        BLOMIKI, BLOMETJE
  053 17 Sardinian N     FRORE
  053 18 Sardinian L     FIORE
  053 15 French Creole C FLE
  053 13 French          FLEUR
  053 16 French Creole D FLE
  053 14 Walloon         FLEUR
  053 12 Provencal       FLOUR, FLOUS
  053 20 Spanish         FLOR
  053 23 Catalan         FLORS
  053 10 Italian         FIORE
  053 19 Sardinian C     FRORI
  053 11 Ladin           FLUR
  053 08 Rumanian List   FLOARE
  053 22 Brazilian       FLORA
  053 21 Portuguese ST   FLOR
  053 07 Breton ST       BLEUNIENN
  053 06 Breton SE       BLEUENN
  053 05 Breton List     BLEUN, BLEUNV
  053 04 Welsh C         BLODYN
  053 03 Welsh N         BLODEUYN
  053 01 Irish A         BLATH
  053 02 Irish B         BLATH
b                      003
  053 79 Wakhi           SPREGH, GUL
  053 74 Afghan          GUL
  053 77 Tadzik          GUL, SUKUFA
  053 76 Persian List    GOL
  053 75 Waziri          GUL
b                      004
  053 61 Lahnda          PHUL
  053 64 Nepali List     PHUL
  053 78 Baluchi         PHUL
  053 59 Gujarati        FUL
  053 65 Khaskura        PHUL
  053 60 Panjabi ST      PHULL
  053 62 Hindi           PHUL
  053 63 Bengali         PHUL
  053 58 Marathi         PHUL
b                      005
  053 82 Albanian G      LULE
  053 84 Albanian C      LULE
  053 83 Albanian K      LULE
  053 80 Albanian T      LULE
  053 95 ALBANIAN        LULE
  053 81 Albanian Top    LULE
b                      006
  053 68 Greek Mod       LULUDHI
  053 66 Greek ML        LOULOUDI
  053 67 Greek MD        LOULOUDI
  053 69 Greek D         LOULOUDI
b                      100
  053 40 Lithuanian ST   GELE
  053 71 Armenian Mod    CATIK
b                      200
c                         200  3  201
  053 94 BULGARIAN P     CVETE
  053 87 BYELORUSSIAN P  KVETKA
  053 45 Czech           KVETINA
  053 90 CZECH P         KVET
  053 43 Lusatian L      KWET
  053 44 Lusatian U      KWET
  053 93 MACEDONIAN P    CVET
  053 50 Polish          KWIAT
  053 88 POLISH P        KWIAT
  053 51 Russian         CVET
  053 85 RUSSIAN P       CVETOK
  053 54 Serbocroatian   CVET
  053 92 SERBOCROATIAN P CVET
  053 46 Slovak          KVET
  053 89 SLOVAK P        KVET
  053 42 Slovenian       CVET, RAZE
  053 91 SLOVENIAN P     CVET
  053 86 UKRAINIAN P     KUITKA
  053 52 Macedonian      CVET
  053 53 Bulgarian       CVETE
  053 48 Ukrainian       KVITKA, CICKA
  053 49 Byelorussian    KVETKA
  053 47 Czech E         KVITKO
b                      201
c                         200  3  201
  053 39 Lithuanian O    KVIETKA
a 054 TO FLY
b                      000
  054 79 Wakhi
b                      001
  054 74 Afghan          ALVOTEL
  054 23 Catalan         AIXECAR, ALSAR
  054 78 Baluchi         BAL GIRAGH, BAL GIPTA
  054 41 Latvian         LIDOT
  054 56 Singhalese      PIHA/BINAWA
  054 09 Vlach           PITEKSESKU
  054 73 Ossetic         TAEXYN
  054 55 Gypsy Gk        UCAV
  054 29 Frisian         WJUKJE
b                      002
  054 03 Welsh N         HEDEG, HEDFAN
  054 04 Welsh C         HEDFAN
  054 68 Greek Mod       PETO
  054 66 Greek ML        PETO
  054 70 Greek K         HIPTAMAI
  054 67 Greek MD        PETO
  054 69 Greek D         PETAO
b                      003
  054 76 Persian List    PARVAZ KARDAN
  054 77 Tadzik          PARVOZ KARDAN, PARIDAN
b                      004
  054 72 Armenian List   TURCHIL
  054 71 Armenian Mod    T`RC`EL
b                      005
  054 22 Brazilian       VOAR
  054 21 Portuguese ST   VOAR
  054 08 Rumanian List   A ZBURA
  054 17 Sardinian N     VOLARE
  054 18 Sardinian L     BOLARE
  054 15 French Creole C VOLE
  054 10 Italian         VOLARE
  054 19 Sardinian C     BOLAI
  054 11 Ladin           SVOLER
  054 13 French          VOLER (OISEAU)
  054 16 French Creole D VOLE
  054 14 Walloon         VOLER
  054 12 Provencal       VOULA, RAUBA
  054 20 Spanish         VOLAR
b                      006
  054 37 English ST      TO FLY
  054 38 Takitaki        FLEI
  054 30 Swedish Up      FLYGA
  054 31 Swedish VL      FLYG
  054 27 Afrikaans       VLIE, VLIEG
  054 26 Dutch List      VLIEGEN
  054 25 Penn. Dutch     FLIEK
  054 28 Flemish         VLIEGEN
  054 36 Faroese         FLUGVA
  054 33 Danish          FLYVE
  054 32 Swedish List    FLYGA
  054 34 Riksmal         FLY
  054 35 Icelandic ST    FLJUGA
  054 24 German ST       FLIEGEN
b                      007
  054 82 Albanian G      FLUTEROJ
  054 84 Albanian C      FLUTURON
  054 81 Albanian Top    FLUTURON, AOR. FLUTUROVA
  054 83 Albanian K      FURTULON
  054 80 Albanian T      ME FLYTURUAR
  054 95 ALBANIAN        FLUTEROJ
b                      008
  054 01 Irish A         EITILT
  054 02 Irish B         EITLIM, EITILLIGHIM, EITIM
b                      009
  054 07 Breton ST       NIJAL
  054 06 Breton SE       NEIJAL
  054 05 Breton List     NIJAL
b                      200
c                         200  3  201
  054 65 Khaskura        URNU
  054 60 Panjabi ST      UDDENA
  054 62 Hindi           URNA
  054 63 Bengali         ORA
  054 58 Marathi         UDNE.
  054 61 Lahnda          UDDEN
  054 64 Nepali List     URNU
  054 57 Kashmiri        WUPHUN, WUDUN
  054 59 Gujarati        URWU
b                      201
c                         200  3  201
  054 75 Waziri          WRATEL (FLY AWAY)
b                      202
c                         202  2  203
  054 39 Lithuanian O    SKRISTI
b                      203
c                         202  2  203
c                         203  2  204
  054 40 Lithuanian ST   SKRISTI, LEKTI
b                      204
c                         203  2  204
  054 94 BULGARIAN P     LET A
  054 87 BYELORUSSIAN P  L OTAC
  054 45 Czech           LETATI
  054 90 CZECH P         LETETI
  054 43 Lusatian L      LESES
  054 44 Lusatian U      LECEC
  054 93 MACEDONIAN P    LETNAM
  054 50 Polish          LECIEC
  054 88 POLISH P        LECIEC
  054 51 Russian         LETET
  054 85 RUSSIAN P       LETET
  054 54 Serbocroatian   LETETI
  054 92 SERBOCROATIAN P LETETI
  054 46 Slovak          LETET
  054 89 SLOVAK P        LETET
  054 42 Slovenian       LETETI
  054 91 SLOVENIAN P     LETETI
  054 86 UKRAINIAN P     LETITY
  054 52 Macedonian      LETNE, ZAREE
  054 53 Bulgarian       DALETI
  054 48 Ukrainian       LITATY
  054 49 Byelorussian    LETAC'
  054 47 Czech E         LETAT
a 055 FOG
b                      000
  055 79 Wakhi
  055 16 French Creole D
b                      001
  055 75 Waziri          BADAL, LERA
  055 23 Catalan         BOYRA, BAIXA, BROMA
  055 78 Baluchi         DITHLO
  055 29 Frisian         DIZE
  055 37 English ST      FOG
  055 84 Albanian C      GHURFI
  055 68 Greek Mod       KATAKHNYA
  055 55 Gypsy Gk        KATAXNYA
  055 63 Bengali         KUASA
  055 56 Singhalese      MIOUMA
  055 83 Albanian K      MNENK
  055 71 Armenian Mod    MSUS
  055 38 Takitaki        SMOKO, SMOKO VO GRON, DAMPOE
  055 11 Ladin           TSCHIERA
  055 77 Tadzik          TUMAN, WAFS
  055 39 Lithuanian O    UKAS
  055 57 Kashmiri        WUNAL
b                      002
  055 01 Irish A         CEO
  055 02 Irish B         CEO
b                      003
  055 65 Khaskura        KUHIRO
  055 64 Nepali List     KUIRO, RUD
  055 62 Hindi           KOHRA
b                      004
  055 81 Albanian Top    MJERGUL
  055 95 ALBANIAN        MJEGULLA
  055 80 Albanian T      MJEGULL
  055 82 Albanian G      MJEGULLA
b                      005
  055 04 Welsh C         NIWL
  055 03 Welsh N         NIWL
b                      006
  055 13 French          BROUILLARD
  055 14 Walloon         BROULIARD
b                      007
  055 61 Lahnda          DHUNDH
  055 60 Panjabi ST      TUND
  055 59 Gujarati        DHUMMES
  055 58 Marathi         DHUKE.
b                      200
c                         200  2  201
c                         200  2  203
c                         200  2  205
  055 52 Macedonian      MAGLA
  055 73 Ossetic         MIG", C"AEXMIG"
  055 85 RUSSIAN P       MGLA
  055 54 Serbocroatian   MAGLA
  055 92 SERBOCROATIAN P MAGLA
  055 46 Slovak          HMLA
  055 89 SLOVAK P        HMLA
  055 42 Slovenian       MEGLA
  055 91 SLOVENIAN P     MEGLA
  055 41 Latvian         MIGLA
  055 94 BULGARIAN P     MUGLA
  055 87 BYELORUSSIAN P  IMHLA
  055 45 Czech           MLHA
  055 90 CZECH P         MHLA
  055 43 Lusatian L      MLA
  055 44 Lusatian U      MHLA
  055 93 MACEDONIAN P    MAGLA
  055 50 Polish          MGLA
  055 88 POLISH P        MGLA
  055 47 Czech E         MHLA
  055 40 Lithuanian ST   MIGLA
  055 74 Afghan          MIH
  055 76 Persian List    MEH
  055 53 Bulgarian       MEGLA
  055 72 Armenian List   MEK
  055 70 Greek K         OMICHLE
  055 69 Greek D         OMICHLE
  055 28 Flemish         MIST
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  2  205
  055 67 Greek MD        POUSI, OMICHLE
b                      202
c                         201  2  202
  055 66 Greek ML        POUSI
b                      203
c                         200  2  203
c                         201  2  203
c                         203  2  204
c                         203  2  205
  055 49 Byelorussian    IMHLA, TUMAN
b                      204
c                         203  2  204
  055 51 Russian         TUMAN
  055 86 UKRAINIAN P     TUMAN
  055 48 Ukrainian       MRJAKA, TUMAN
b                      205
c                         200  2  205
c                         201  2  205
c                         203  2  205
c                         205  2  206
  055 27 Afrikaans       MIS, NEWEL
  055 26 Dutch List      NEVEL, MIST
b                      206
c                         205  2  206
  055 25 Penn. Dutch     NEVEL
  055 24 German ST       NEBEL
  055 08 Rumanian List   CEATA, NEGURA
  055 09 Vlach           NEGURE
  055 22 Brazilian       NEVOA
  055 21 Portuguese ST   NEVOEIRO
  055 17 Sardinian N     NEULA
  055 18 Sardinian L     NEULA
  055 15 French Creole C (VAPE, NIAZ)
  055 10 Italian         NEBBIA
  055 19 Sardinian C     NEBBIA
  055 12 Provencal       NEBLO, SAGARES
  055 20 Spanish         NIEBLA
b                      207
c                         207  2  208
  055 31 Swedish VL      DIMA
b                      208
c                         207  2  208
c                         208  2  209
  055 32 Swedish List    TJOKA, DIMMA
  055 30 Swedish Up      DIMMA, TJOCKA
b                      209
c                         208  2  209
  055 36 Faroese         TOKA
  055 33 Danish          TAAGE
  055 34 Riksmal         TAKE
  055 35 Icelandic ST    THOKA
b                      210
c                         210  2  211
  055 06 Breton SE       BRUMEN
b                      211
c                         210  2  211
c                         211  2  212
  055 07 Breton ST       LATAR, BRUMENN
b                      212
c                         211  2  212
  055 05 Breton List     LATAR, LUGENN, LUSENN, MORENN, MOGIDELL, BRUMENN
a 056 FOOT
b                      001
  056 34 Riksmal         BEN
  056 55 Gypsy Gk        CANK
  056 59 Gujarati        PEG
b                      002
  056 40 Lithuanian ST   KOJA
  056 39 Lithuanian O    KOJA
  056 41 Latvian         KAJA
b                      003
  056 91 SLOVENIAN P     NOGA
  056 86 UKRAINIAN P     NOHA
  056 88 POLISH P        NOGA
  056 51 Russian         NOGA
  056 85 RUSSIAN P       NOGA
  056 54 Serbocroatian   NOGA
  056 92 SERBOCROATIAN P NOGA
  056 46 Slovak          NOHA
  056 89 SLOVAK P        NOHA
  056 87 BYELORUSSIAN P  NAHA
  056 45 Czech           NOHA
  056 90 CZECH P         NOHA
  056 43 Lusatian L      NOGA
  056 44 Lusatian U      NOHA
  056 93 MACEDONIAN P    NOGA
  056 52 Macedonian      NOGA
  056 47 Czech E         NOHA
  056 48 Ukrainian       NOGA, OSNOVA
b                      004
  056 49 Byelorussian    STAPA
  056 42 Slovenian       STAPOLU
  056 50 Polish          STOPA
b                      005
  056 94 BULGARIAN P     KRAK
  056 53 Bulgarian       KRAK
b                      006
  056 81 Albanian Top    KEMBE
  056 84 Albanian C      KEMB
  056 83 Albanian K      KEMBE
  056 80 Albanian T      KEMBE
  056 95 ALBANIAN        KAMA
  056 82 Albanian G      KAMA, PUTER
b                      200
c                         200  2  201
c                         200  3  202
  056 73 Ossetic         K"AX, FAD
  056 56 Singhalese      KAKULA, PAYA
  056 57 Kashmiri        KHOR, PAR, PAD, PURU
  056 61 Lahnda          PAER
  056 78 Baluchi         PHADH
  056 79 Wakhi           PUED
  056 77 Tadzik          PO, POJ
  056 60 Panjabi ST      PER
  056 62 Hindi           PER
  056 63 Bengali         PA
  056 58 Marathi         PAUL, PAY
  056 76 Persian List    PA
  056 71 Armenian Mod    OT
  056 72 Armenian List   VODK
  056 08 Rumanian List   PICIOR
  056 09 Vlach           CORU
  056 11 Ladin           PE
  056 13 French          PIED
  056 16 French Creole D PYE
  056 14 Walloon         PI
  056 12 Provencal       PED
  056 20 Spanish         PIE
  056 23 Catalan         PEU
  056 10 Italian         PIE, PIEDE
  056 19 Sardinian C     PEI
  056 22 Brazilian       PE
  056 21 Portuguese ST   PE
  056 30 Swedish Up      FOT
  056 31 Swedish VL      FOT
  056 17 Sardinian N     PEDE
  056 18 Sardinian L     PE
  056 15 French Creole C PYE
  056 68 Greek Mod       PODHI
  056 66 Greek ML        PODI
  056 70 Greek K         POUS
  056 67 Greek MD        PODI
  056 69 Greek D         PODI
  056 35 Icelandic ST    FOTR
  056 24 German ST       FUSS
  056 27 Afrikaans       VOET
  056 26 Dutch List      VOET
  056 25 Penn. Dutch     FUUSZ
  056 28 Flemish         VOET
  056 29 Frisian         FOET
  056 36 Faroese         FOTUR
  056 33 Danish          FOD
  056 32 Swedish List    FOT
  056 37 English ST      FOOT
  056 38 Takitaki        FOETOE
b                      201
c                         200  2  201
c                         201  3  202
c                         201  2  203
  056 64 Nepali List     KHUTTO, GORO, PAU
b                      202
c                         200  3  202
c                         201  3  202
  056 74 Afghan          PSA
  056 75 Waziri          PSHA
b                      203
c                         201  2  203
  056 65 Khaskura        KHUTTA
b                      204
c                         204  2  205
  056 07 Breton ST       TROAD
  056 06 Breton SE       TROED
  056 05 Breton List     TROAD
  056 04 Welsh C         TROED
  056 03 Welsh N         TROED
b                      205
c                         204  2  205
c                         205  2  206
  056 01 Irish A         COS, TROIGH
b                      206
c                         205  2  206
  056 02 Irish B         COS
a 057 FOUR
b                      000
  057 73 Ossetic
b                      002
  057 37 English ST      FOUR
  057 38 Takitaki        FO
  057 40 Lithuanian ST   KETURI
  057 39 Lithuanian O    KETURI
  057 41 Latvian         CETRI
  057 74 Afghan          CALOR
  057 78 Baluchi         CHIAR
  057 79 Wakhi           TSEBUR, SUBUR
  057 75 Waziri          TSALOR, TSALWOR, TSALWER
  057 94 BULGARIAN P     CETIRI
  057 87 BYELORUSSIAN P  CATYRY
  057 45 Czech           CTYRI
  057 90 CZECH P         CTYRI
  057 43 Lusatian L      STYRI
  057 44 Lusatian U      STYRI
  057 93 MACEDONIAN P    CETIRI
  057 50 Polish          CZTERY
  057 88 POLISH P        CZTERY
  057 51 Russian         CETYRE
  057 85 RUSSIAN P       CETYRE
  057 54 Serbocroatian   CETIRI
  057 92 SERBOCROATIAN P CETIRI
  057 46 Slovak          STYRI
  057 89 SLOVAK P        STYRI
  057 42 Slovenian       STJRI
  057 91 SLOVENIAN P     STIRJE
  057 86 UKRAINIAN P     COTYRY
  057 53 Bulgarian       CETIRI
  057 48 Ukrainian       COTYRY
  057 49 Byelorussian    CATYRY
  057 47 Czech E         STIRI
  057 55 Gypsy Gk        ISTAR
  057 61 Lahnda          CAR
  057 64 Nepali List     CAR
  057 57 Kashmiri        TSOR
  057 56 Singhalese      HATARA
  057 59 Gujarati        CAR
  057 52 Macedonian      CETIRI
  057 77 Tadzik          COR
  057 65 Khaskura        CHAR
  057 60 Panjabi ST      CAR
  057 62 Hindi           CAR
  057 63 Bengali         CAR
  057 58 Marathi         CAR
  057 76 Persian List    CHAHAR (CHAR)
  057 71 Armenian Mod    C`ORS
  057 72 Armenian List   CHORSE
  057 01 Irish A         CEATHAIR
  057 02 Irish B         CESTHAIR
  057 68 Greek Mod       TESERIS
  057 66 Greek ML        TESSERA
  057 70 Greek K         TESSARA
  057 67 Greek MD        TESSERA
  057 69 Greek D         TESSERA
  057 17 Sardinian N     BATTORO
  057 18 Sardinian L     BATTORO
  057 09 Vlach           PATRU
  057 81 Albanian Top    KATER
  057 15 French Creole C KAT
  057 13 French          QUATRE
  057 16 French Creole D KAT
  057 14 Walloon         CWATE, QWATE
  057 12 Provencal       QUATRE
  057 20 Spanish         CUATRO
  057 23 Catalan         QUATRE
  057 10 Italian         QUATTRO
  057 19 Sardinian C     KWATTRU
  057 11 Ladin           QUATTER
  057 08 Rumanian List   PATRU
  057 82 Albanian G      KATER
  057 84 Albanian C      KATR
  057 83 Albanian K      KATRE
  057 80 Albanian T      KATER
  057 95 ALBANIAN        KATER
  057 22 Brazilian       QUATRO
  057 21 Portuguese ST   QUATRO
  057 30 Swedish Up      FYRA
  057 31 Swedish VL      FYRA
  057 27 Afrikaans       VIER
  057 26 Dutch List      VIER
  057 25 Penn. Dutch     FIERE
  057 28 Flemish         VIER
  057 29 Frisian         FJOUWER
  057 36 Faroese         FYRA
  057 33 Danish          FIRE
  057 32 Swedish List    FYRA
  057 34 Riksmal         FIRE
  057 35 Icelandic ST    FJORIR
  057 24 German ST       VIER
  057 07 Breton ST       PEVAR (M.), PEDER (F.)
  057 06 Breton SE       PEAR (M.), PEDER (F.)
  057 05 Breton List     PEVAR (M), PEDER (F)
  057 04 Welsh C         PEDWAR
  057 03 Welsh N         PEDWAR
a 058 TO FREEZE
b                      000
  058 25 Penn. Dutch
  058 84 Albanian C
  058 65 Khaskura
  058 38 Takitaki
b                      001
  058 17 Sardinian N     ASTRAGARE
  058 55 Gypsy Gk        BUZLANDU
  058 83 Albanian K      FTOXEM
  058 58 Marathi         GOTHNE.
  058 57 Kashmiri        HANDARUN
  058 75 Waziri          KARANG (FROZEN)
  058 78 Baluchi         MADHAGH, MASTAGH
  058 70 Greek K         PSUGOMAI
  058 56 Singhalese      SITA/KARANAWA
  058 54 Serbocroatian   SLEDITI SE
b                      002
  058 66 Greek ML        PAGONO
  058 67 Greek MD        PAGONO
  058 69 Greek D         PAGONO
  058 68 Greek Mod       INE PAGHONYA
b                      003
  058 80 Albanian T      ME NGRIRE
  058 81 Albanian Top    GRIN, AOR. GRIVA
b                      004
  058 62 Hindi           JEMNA
  058 61 Lahnda          JEMMEN
  058 64 Nepali List     JAMNU
  058 59 Gujarati        THERWU, JHAMEWU, JHAMI JEWU
  058 60 Panjabi ST      JEMMENA
  058 63 Bengali         JOMAT+BADHANO
b                      005
  058 82 Albanian G      MERDHIF
  058 95 ALBANIAN        MERDHIF
  058 92 SERBOCROATIAN P MRZNUTI
  058 46 Slovak          MRZNUT
  058 89 SLOVAK P        MRAZIT SA
  058 42 Slovenian       ZMRZNE
  058 91 SLOVENIAN P     MRZETI
  058 86 UKRAINIAN P     MOROZYTY
  058 94 BULGARIAN P     MRUZNA
  058 87 BYELORUSSIAN P  MAROZIC
  058 45 Czech           MRZNOUTI
  058 90 CZECH P         MRAZITI
  058 43 Lusatian L      MARZNUS
  058 44 Lusatian U      MJERZNYC
  058 93 MACEDONIAN P    MRZNAM
  058 50 Polish          ZAMARZAC
  058 88 POLISH P        MROZIC
  058 51 Russian         ZAMERZAT
  058 85 RUSSIAN P       MOROZIT
  058 52 Macedonian      MRAZI/MRZNE
  058 53 Bulgarian       DA ZAMREZVA
  058 48 Ukrainian       MERZNUTY
  058 49 Byelorussian    ZJAMARATYVAC'
  058 47 Czech E         ZMRZNUT
b                      200
c                         200  2  201
  058 77 Tadzik          JAX KARDAN, JAX BASTAN
  058 79 Wakhi           YIS WOTS-, YIS TSER-
  058 74 Afghan          JAX KEDEL
  058 76 Persian List    YAKH BASTAN
b                      201
c                         200  2  201
c                         201  3  202
c                         201  3  203
  058 73 Ossetic         SAELYN, IX KAENYN
b                      202
c                         201  3  202
c                         202  3  203
  058 72 Armenian List   SARIL
  058 71 Armenian Mod    SAREL, SARECNEL
b                      203
c                         201  3  203
c                         202  3  203
  058 40 Lithuanian ST   SALDYTI
  058 39 Lithuanian O    SALDYTI
  058 41 Latvian         SALT
b                      204
c                         204  2  205
  058 13 French          GELER
  058 18 Sardinian L     GHELARE
  058 15 French Creole C ZELE (CONFEAL)
  058 16 French Creole D ZELE
  058 14 Walloon         DJALER
  058 12 Provencal       GELA, JALA
  058 20 Spanish         HELAR
  058 10 Italian         GELARE
  058 19 Sardinian C     GELAI
  058 11 Ladin           DSCHLER
  058 22 Brazilian       GELAR
  058 21 Portuguese ST   GELAR
b                      205
c                         204  2  205
c                         205  2  206
  058 23 Catalan         GELAR, FLASSAR
b                      206
c                         205  2  206
  058 08 Rumanian List   A INGHETA
  058 09 Vlach           EGLICE
b                      207
c                         207  3  208
  058 37 English ST      TO FREEZE
  058 30 Swedish Up      FRYSA
  058 31 Swedish VL      FRYS
  058 28 Flemish         BEVRIEZEN
  058 29 Frisian         FRIEZE
  058 36 Faroese         FRYSTA
  058 33 Danish          FRYSE
  058 32 Swedish List    FRYSA
  058 34 Riksmal         FRYSE
  058 35 Icelandic ST    FRJOSA
  058 24 German ST       FRIEREN
  058 27 Afrikaans       VRIES
  058 26 Dutch List      VRIEZEN
b                      208
c                         207  3  208
  058 07 Breton ST       REVIN
  058 06 Breton SE       REUEIN
  058 05 Breton List     REVI, RIVA
  058 04 Welsh C         RHEWI
  058 03 Welsh N         RHEWI
  058 01 Irish A         REODHADH
  058 02 Irish B         DO RHIOCADH, DO REOILEACADH
a 059 FRUIT
b                      000
  059 84 Albanian C
  059 71 Armenian Mod
  059 91 SLOVENIAN P
  059 86 UKRAINIAN P
  059 92 SERBOCROATIAN P
  059 89 SLOVAK P
  059 85 RUSSIAN P
  059 88 POLISH P
  059 90 CZECH P
  059 43 Lusatian L
  059 44 Lusatian U
  059 93 MACEDONIAN P
  059 94 BULGARIAN P
  059 87 BYELORUSSIAN P
  059 34 Riksmal
  059 35 Icelandic ST
  059 36 Faroese
b                      001
  059 41 Latvian         AUGLIS
  059 72 Armenian List   BUDUGH
  059 73 Ossetic         DYRG"
  059 55 Gypsy Gk        EMISA
  059 37 English ST      FRUIT
  059 25 Penn. Dutch     OEPS
  059 70 Greek K         OPORAI, KARPOI
  059 09 Vlach           POMU
  059 42 Slovenian       SADJE
b                      002
  059 61 Lahnda          PHEL
  059 64 Nepali List     PHAL
  059 57 Kashmiri        PHAL
  059 56 Singhalese      PALATURU, PHALA
  059 65 Khaskura        PHALPHUL
  059 60 Panjabi ST      PHEL
  059 62 Hindi           PHEL
  059 63 Bengali         PHOL
  059 59 Gujarati        FEL
  059 58 Marathi         PHEL
b                      003
  059 22 Brazilian       FRUTA
  059 21 Portuguese ST   FRUCTO
  059 13 French          FRUIT
  059 16 French Creole D FWI
  059 14 Walloon         FRUT, FRUT'
  059 12 Provencal       FRU, FRUCHO
  059 20 Spanish         FRUTO
  059 23 Catalan         FRUYT
  059 10 Italian         FRUTTO
  059 19 Sardinian C     FRUTTA
  059 11 Ladin           FRUT
  059 08 Rumanian List   FRUCT
  059 15 French Creole C FWITAZ (CULTIV.), GHWEN BWA (WILD)
  059 17 Sardinian N     FRUTTORA
  059 18 Sardinian L     FRUTTU
b                      004
  059 74 Afghan          MEVA
  059 78 Baluchi         MEWA, BAR
  059 79 Wakhi           MIWA
  059 77 Tadzik          MEVA
  059 76 Persian List    MIVE
  059 75 Waziri          MEWA
b                      005
  059 80 Albanian T      PEME
  059 82 Albanian G      PEMA
  059 95 ALBANIAN        PEMA
b                      006
  059 38 Takitaki        NJANJAM, VROEKTOE
  059 24 German ST       FRUCHT
  059 33 Danish          FRUGT
  059 32 Swedish List    FRUKT
  059 28 Flemish         VRUCHT
  059 29 Frisian         FRUCHT
  059 27 Afrikaans       VRUG
  059 26 Dutch List      VRUCHT
  059 30 Swedish Up      FRUKT
  059 31 Swedish VL      FRUKT
b                      007
  059 68 Greek Mod       FRUTO
  059 66 Greek ML        FROUTO
  059 67 Greek MD        FROUTO
  059 69 Greek D         FROUTO
b                      008
  059 83 Albanian K      FRUTO
  059 81 Albanian Top    FRUTA (PL.)
b                      009
  059 07 Breton ST       FROUEZH
  059 06 Breton SE       FREH
  059 05 Breton List     FROUEZ
  059 04 Welsh C         FFRWYTH
  059 03 Welsh N         FFRWYTH
b                      010
  059 40 Lithuanian ST   VAISIUS
  059 39 Lithuanian O    VAISIUS
b                      011
  059 01 Irish A         TORADH
  059 02 Irish B         TORADH, TORAIDH, TORTHA
b                      200
c                         200  2  201
  059 46 Slovak          OVOCIE
  059 54 Serbocroatian   VOCE
  059 50 Polish          OWOC
  059 45 Czech           OVOCE
  059 47 Czech E         OVOCE
b                      201
c                         200  2  201
c                         201  2  202
  059 48 Ukrainian       OVOC, PLID
b                      202
c                         201  2  202
  059 53 Bulgarian       PLOD
  059 49 Byelorussian    PLOD
  059 51 Russian         PLOD
  059 52 Macedonian      PLOD, EMIS
a 060 TO GIVE
b                      000
  060 79 Wakhi
  060 29 Frisian
b                      001
  060 59 Gujarati        APWU
  060 74 Afghan          VERKAVEL
b                      002
  060 37 English ST      TO GIVE
  060 38 Takitaki        GI
  060 30 Swedish Up      GE, GIVA
  060 31 Swedish VL      JE
  060 36 Faroese         GEVA
  060 33 Danish          GIVE
  060 32 Swedish List    GIVA
  060 34 Riksmal         GI
  060 35 Icelandic ST    GEFA
  060 24 German ST       GEBEN
  060 27 Afrikaans       GEE
  060 26 Dutch List      GEVEN
  060 25 Penn. Dutch     GEP
  060 28 Flemish         GEVEN
b                      003
  060 01 Irish A         TABHAIRT
  060 02 Irish B         TABHARIM
b                      200
c                         200  2  201
c                         200  3  203
  060 55 Gypsy Gk        DAV
  060 09 Vlach           DAU
  060 73 Ossetic         DAETTYN
  060 17 Sardinian N     DARE
  060 18 Sardinian L     DARE
  060 68 Greek Mod       DHINO
  060 66 Greek ML        DINO
  060 70 Greek K         DIDO
  060 67 Greek MD        DINO
  060 69 Greek D         DINO
  060 40 Lithuanian ST   DUOTI
  060 39 Lithuanian O    DUOTI
  060 41 Latvian         DOT
  060 94 BULGARIAN P     DAM
  060 87 BYELORUSSIAN P  DAC
  060 45 Czech           DAVATI
  060 90 CZECH P         DATI
  060 43 Lusatian L      DAS
  060 44 Lusatian U      DAC
  060 93 MACEDONIAN P    DAM
  060 50 Polish          DAWAC
  060 88 POLISH P        DAC
  060 51 Russian         DAVAT
  060 85 RUSSIAN P       DAT
  060 54 Serbocroatian   DATI
  060 92 SERBOCROATIAN P DATI
  060 46 Slovak          DAT
  060 89 SLOVAK P        DAT
  060 42 Slovenian       DATI, DAJ
  060 91 SLOVENIAN P     DATI
  060 86 UKRAINIAN P     DATY
  060 78 Baluchi         DEAGH, DATHA
  060 20 Spanish         DAR
  060 23 Catalan         DONAR
  060 10 Italian         DARE
  060 19 Sardinian C     DONAI
  060 11 Ladin           DER
  060 08 Rumanian List   A DA
  060 14 Walloon         DINER (D'NER, N'NER)
  060 13 French          DONNER
  060 52 Macedonian      DAVA
  060 77 Tadzik          DODAN
  060 71 Armenian Mod    TAL
  060 72 Armenian List   DAL
  060 49 Byelorussian    DAVAC'
  060 47 Czech E         DAT
  060 22 Brazilian       DAR
  060 21 Portuguese ST   DAR
  060 53 Bulgarian       DA DAVA
  060 48 Ukrainian       DAVATY, VRUCATY
  060 75 Waziri          DERKREL
  060 61 Lahnda          DEWEN
  060 64 Nepali List     DINU
  060 57 Kashmiri        DYUNU
  060 56 Singhalese      DENAWA
  060 65 Khaskura        DINU
  060 60 Panjabi ST      DENA
  060 62 Hindi           DENA
  060 63 Bengali         DEOA
  060 58 Marathi         DENE.
  060 76 Persian List    DADAN
  060 81 Albanian Top    JAP, AOR. DHASE
  060 82 Albanian G      AP (DHAN, DHAN = INF.)
  060 84 Albanian C      JAP
  060 83 Albanian K      JAP (AOR. DHASE, PPLE. DHENE)
  060 80 Albanian T      ME DHENE
  060 95 ALBANIAN        AP, (DHASH = AOR.) (DHAN = INF.)
b                      201
c                         200  2  201
c                         201  3  202
c                         201  3  203
  060 12 Provencal       DOUNA, BAIA
b                      202
c                         201  3  202
  060 15 French Creole C BAY  BA
  060 16 French Creole D BAY
b                      203
c                         200  3  203
c                         201  3  203
  060 03 Welsh N         RHODDI
  060 07 Breton ST       REIN
  060 06 Breton SE       REIN
  060 05 Breton List     REI, AOTREN
  060 04 Welsh C         RHOI
a 061 GOOD
b                      001
  061 38 Takitaki        BOEN
  061 72 Armenian List   BARI (PERSON)
  061 56 Singhalese      HONDA
  061 55 Gypsy Gk        LACHO
  061 78 Baluchi         PHUTUR
  061 59 Gujarati        SARU
  061 51 Russian         XOROSIJ
  061 29 Frisian         WOL
b                      002
  061 13 French          BON
  061 16 French Creole D BO
  061 14 Walloon         BON, BONE
  061 12 Provencal       BON, ONO
  061 20 Spanish         BUENO
  061 23 Catalan         BO
  061 10 Italian         BUONO
  061 19 Sardinian C     BONU
  061 11 Ladin           BUNA
  061 08 Rumanian List   BUN
  061 22 Brazilian       BOM
  061 21 Portuguese ST   BOM
  061 09 Vlach           BUNE
  061 17 Sardinian N     BONU
  061 18 Sardinian L     BONU
  061 15 French Creole C BO
b                      003
  061 37 English ST      GOOD
  061 30 Swedish Up      GOD
  061 31 Swedish VL      GO
  061 36 Faroese         GODUR
  061 33 Danish          GOD
  061 32 Swedish List    GOD
  061 34 Riksmal         GOD
  061 35 Icelandic ST    GOOR
  061 24 German ST       GUT
  061 27 Afrikaans       GOED
  061 26 Dutch List      GOED
  061 25 Penn. Dutch     GUUT
  061 28 Flemish         GOED
b                      004
  061 42 Slovenian       DOBRO
  061 91 SLOVENIAN P     DOBER
  061 86 UKRAINIAN P     DOBRYJ
  061 52 Macedonian      AREN, DOBAR, DOBRO
  061 48 Ukrainian       DOBRYJ, HARNIJ
  061 53 Bulgarian       DOBRO
  061 49 Byelorussian    DOBRY, DOBRA
  061 47 Czech E         DOBRE
  061 94 BULGARIAN P     DOBUR
  061 87 BYELORUSSIAN P  DOBRY
  061 45 Czech           DOBRY
  061 90 CZECH P         DOBRY
  061 43 Lusatian L      DOBRY
  061 44 Lusatian U      DOBRY
  061 93 MACEDONIAN P    DOBAR
  061 50 Polish          DOBRY
  061 88 POLISH P        DOBRY
  061 85 RUSSIAN P       DOBRYJ
  061 54 Serbocroatian   DOBAR
  061 92 SERBOCROATIAN P DOBAR
  061 46 Slovak          DOBRY
  061 89 SLOVAK P        DOBRY
b                      005
  061 75 Waziri          SHE
  061 74 Afghan          SA
b                      006
  061 07 Breton ST       MAT
  061 06 Breton SE       MAT
  061 05 Breton List     MAT
  061 01 Irish A         MAITH
  061 02 Irish B         MAITH
b                      007
  061 04 Welsh C         DA
  061 03 Welsh N         DA
b                      008
  061 60 Panjabi ST      CENGA
  061 61 Lahnda          CENGA
  061 58 Marathi         CANGLA
b                      009
  061 68 Greek Mod       KALOS
  061 66 Greek ML        KALOS
  061 70 Greek K         KALOS
  061 67 Greek MD        KALOS
  061 69 Greek D         KALOS
b                      010
  061 95 ALBANIAN        MIR
  061 82 Albanian G      MIR
  061 84 Albanian C      I-MIR
  061 83 Albanian K      MIRE
  061 80 Albanian T      I, E MIRE
  061 81 Albanian Top    I-MIRE
b                      011
  061 40 Lithuanian ST   GERAS
  061 39 Lithuanian O    GERAS
b                      100
  061 71 Armenian Mod    LAV
  061 41 Latvian         LABS
b                      200
c                         200  2  201
  061 62 Hindi           ECCHA
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  3  204
  061 64 Nepali List     BHALO, JATI, ACCHA
b                      202
c                         201  2  202
c                         202  3  204
  061 65 Khaskura        RAMRO, JATI
b                      203
c                         201  2  203
  061 63 Bengali         BHALO
b                      204
c                         201  3  204
c                         202  3  204
  061 57 Kashmiri        KHARA, JAN
b                      205
c                         205  2  206
  061 76 Persian List    KHUB
  061 79 Wakhi           BUF, XUB
b                      206
c                         205  2  206
c                         206  3  207
  061 77 Tadzik          XUB, HAWZ
b                      207
c                         206  3  207
  061 73 Ossetic         XORZ, DZAEBAEX
a 062 GRASS
b                      001
  062 58 Marathi         GEVET (GRASS), GHAS (FODDER)
  062 55 Gypsy Gk        CAR
  062 60 Panjabi ST      KA
  062 73 Ossetic         KAERDAEG
  062 05 Breton List     LETON
  062 04 Welsh C         PORFA
  062 78 Baluchi         RENV, REM
  062 56 Singhalese      TANAKOLA
b                      002
  062 23 Catalan         HERBA
  062 10 Italian         ERBA
  062 19 Sardinian C     ERBA
  062 11 Ladin           ERVA
  062 08 Rumanian List   IARBA
  062 22 Brazilian       ERVA
  062 21 Portuguese ST   HERVA, RELVA
  062 09 Vlach           YERBE
  062 17 Sardinian N     ERVA
  062 18 Sardinian L     ERBA
  062 15 French Creole C ZEB
  062 13 French          HERBE
  062 16 French Creole D ZEB
  062 14 Walloon         JEBE
  062 12 Provencal       ERBO, GERME
  062 20 Spanish         HIERBA
b                      003
  062 41 Latvian         ZALE
  062 40 Lithuanian ST   ZOLE
  062 39 Lithuanian O    ZOLE
  062 70 Greek K         CHLOE
b                      004
  062 76 Persian List    ALAF
  062 77 Tadzik          ALAF
b                      005
  062 07 Breton ST       GEOT
  062 06 Breton SE       GEAUT
  062 03 Welsh N         GWELLT, GLASWELLT, GWAIR
b                      006
  062 94 BULGARIAN P     TREVA
  062 87 BYELORUSSIAN P  TRAVA
  062 45 Czech           TRAVA
  062 90 CZECH P         TRAVA
  062 43 Lusatian L      TSAWA
  062 44 Lusatian U      TRAWA
  062 93 MACEDONIAN P    TREVKA
  062 50 Polish          TRAWA
  062 88 POLISH P        TRAWA
  062 51 Russian         TRAVA
  062 85 RUSSIAN P       TRAVA
  062 54 Serbocroatian   TRAVA
  062 92 SERBOCROATIAN P TRAVA
  062 46 Slovak          TRAVA
  062 89 SLOVAK P        TRAVA
  062 42 Slovenian       TRAVA
  062 91 SLOVENIAN P     TRAVA
  062 86 UKRAINIAN P     TRAVA
  062 52 Macedonian      TREVA
  062 53 Bulgarian       TREVA
  062 48 Ukrainian       TRAVA, MURAVA
  062 49 Byelorussian    TRAVA
  062 47 Czech E         TRAVA
b                      007
  062 37 English ST      GRASS
  062 38 Takitaki        GRASI
  062 30 Swedish Up      GRAS
  062 31 Swedish VL      GRAS  GRAS
  062 27 Afrikaans       GRAS
  062 26 Dutch List      GRAS
  062 25 Penn. Dutch     GRAWSZ
  062 28 Flemish         GRAS
  062 29 Frisian         GJERS
  062 36 Faroese         GRASS
  062 33 Danish          GRAES
  062 32 Swedish List    GRAS
  062 34 Riksmal         GRESS
  062 35 Icelandic ST    GRAS
  062 24 German ST       GRAS
b                      008
  062 64 Nepali List     GHAS
  062 61 Lahnda          GHA
  062 57 Kashmiri        GASA
  062 59 Gujarati        GHAS
  062 65 Khaskura        GHAS, JHAR
  062 62 Hindi           GHAS
  062 63 Bengali         GHAS
b                      009
  062 01 Irish A         FEAR
  062 02 Irish B         FEAR, FEIR
b                      010
  062 72 Armenian List   KHOD
  062 71 Armenian Mod    XOT
b                      011
  062 68 Greek Mod       KHORTARI
  062 66 Greek ML        CHORTARI
  062 67 Greek MD        CHORTARI, GRASIDI, CHORTO
  062 69 Greek D         CHORTO, CHORTARI
b                      012
  062 79 Wakhi           WUS
  062 74 Afghan          VASE
  062 75 Waziri          WOSHE
b                      013
  062 81 Albanian Top    BAR
  062 95 ALBANIAN        BARI
  062 82 Albanian G      BAR
  062 84 Albanian C      BAR
  062 83 Albanian K      BAAR
  062 80 Albanian T      BAR
a 063 GREEN
b                      001
  063 83 Albanian K      BIME (PLANTS), I-RIMTE (OBJECTS)
  063 73 Ossetic         C"AEX
  063 55 Gypsy Gk        ESILI
  063 56 Singhalese      KOLA
  063 59 Gujarati        LILU
  063 46 Slovak          TRAVNIK
  063 84 Albanian C      VIRDHI
b                      002
  063 76 Persian List    SABZ
  063 57 Kashmiri        NYULU, SABAZ
  063 79 Wakhi           SUVZ
  063 78 Baluchi         SAVZ, MAUNSHAR
  063 77 Tadzik          SABZ, KABUD
  063 63 Bengali         SOBUJ
b                      003
  063 24 German ST       GRUN
  063 37 English ST      GREEN
  063 38 Takitaki        GROEN
  063 30 Swedish Up      GRON
  063 31 Swedish VL      GRON
  063 27 Afrikaans       GROEN
  063 26 Dutch List      GROEN
  063 25 Penn. Dutch     GRIE
  063 28 Flemish         GROEN
  063 29 Frisian         GRIEM
  063 36 Faroese         GRONUR
  063 33 Danish          GRON
  063 32 Swedish List    GRON
  063 34 Riksmal         GRONN
  063 35 Icelandic ST    GRAENN
b                      004
  063 68 Greek Mod       PRASINOS
  063 66 Greek ML        PRASINOS
  063 70 Greek K         PRASINOS
  063 67 Greek MD        PRASINOS
  063 69 Greek D         PRASINOS
b                      005
  063 95 ALBANIAN        JESHIL (GJELBER)
  063 82 Albanian G      JESHIL
b                      006
  063 80 Albanian T      I, E GJELBER, I, E KALTERT
  063 81 Albanian Top    GELBER
b                      007
  063 71 Armenian Mod    KANAC`
  063 72 Armenian List   GANANCH
b                      008
  063 09 Vlach           VEARDE
  063 17 Sardinian N     VIRDE
  063 18 Sardinian L     BIRDE
  063 15 French Creole C VE
  063 13 French          VERT
  063 16 French Creole D VE
  063 14 Walloon         VERT
  063 12 Provencal       VERT, ERDO
  063 20 Spanish         VERDE
  063 23 Catalan         VERT
  063 10 Italian         VERDE
  063 19 Sardinian C     BIRDI
  063 11 Ladin           VERD, VIERD
  063 08 Rumanian List   VERDE
  063 22 Brazilian       VERDE (VER)
  063 21 Portuguese ST   VERDE
b                      200
c                         200  2  201
c                         200  2  203
c                         200  3  205
c                         200  3  206
  063 86 UKRAINIAN P     ZELENYJ
  063 54 Serbocroatian   ZELEN
  063 92 SERBOCROATIAN P ZELEN
  063 89 SLOVAK P        ZELENY
  063 42 Slovenian       ZELENO
  063 91 SLOVENIAN P     ZELEN
  063 94 BULGARIAN P     ZELEN
  063 87 BYELORUSSIAN P  Z AL ONY
  063 45 Czech           ZELENY
  063 90 CZECH P         ZELENY
  063 43 Lusatian L      ZELENY
  063 44 Lusatian U      ZELENY
  063 93 MACEDONIAN P    ZELEN
  063 50 Polish          ZIELONY
  063 88 POLISH P        ZIELONY
  063 51 Russian         ZELENYJ
  063 85 RUSSIAN P       ZEL ONYJ
  063 52 Macedonian      ZELEN
  063 53 Bulgarian       ZELENO
  063 48 Ukrainian       ZELENYJ, NEDOSPILYJ
  063 49 Byelorussian    ZJALENY
  063 47 Czech E         ZELENE
  063 40 Lithuanian ST   ZALIAS
  063 39 Lithuanian O    ZALIAS
  063 41 Latvian         ZALS
  063 01 Irish A         GLAS, UAINE
  063 02 Irish B         GLAS, UAITHNE
  063 65 Khaskura        HARIO
  063 64 Nepali List     HARIYO
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  3  205
c                         201  3  206
  063 07 Breton ST       GLAS, GWER
  063 06 Breton SE       GLAS, GUERH
  063 05 Breton List     GWER, GLAS (ALSO BLUE AND GREY)
b                      202
c                         201  2  202
  063 04 Welsh C         GWYRDD
  063 03 Welsh N         GWYRDD
b                      203
c                         200  2  203
c                         201  2  203
c                         203  2  204
c                         203  3  205
c                         203  3  206
  063 75 Waziri          SHIN, ZARGHIN
b                      204
c                         203  2  204
  063 74 Afghan          SIN
b                      205
c                         200  3  205
c                         201  3  205
c                         203  3  205
c                         205  3  206
  063 61 Lahnda          HERA
  063 60 Panjabi ST      HERA
  063 62 Hindi           HERA
b                      206
c                         200  3  206
c                         201  3  206
c                         203  3  206
c                         205  3  206
  063 58 Marathi         HIRVA
a 064 GUTS
b                      000
  064 39 Lithuanian O
  064 67 Greek MD
  064 29 Frisian
  064 25 Penn. Dutch
  064 65 Khaskura
b                      001
  064 38 Takitaki        BELE, TRIPA
  064 56 Singhalese      BADAVEL(A)
  064 52 Macedonian      DROBOVI
  064 70 Greek K         EUTOSTHIA
  064 37 English ST      GUTS
  064 61 Lahnda          HIMMET
  064 01 Irish A         HUTOGA
  064 02 Irish B         INNREACHTAN, AIN
  064 88 POLISH P        JELITO
  064 08 Rumanian List   MARUNTAIE
  064 63 Bengali         NARIBHURI
  064 04 Welsh C         PERFEDD
  064 55 Gypsy Gk        PORA
  064 78 Baluchi         ROTH, RODH
  064 79 Wakhi           SINGER
  064 69 Greek D         SKOTIA, SPLACHNA
  064 73 Ossetic         T"ANG
  064 57 Kashmiri        TSAPH
  064 03 Welsh N         YMYSGAROEDD
b                      002
  064 51 Russian         KISKI
  064 85 RUSSIAN P       KISKA
  064 48 Ukrainian       KISKI
  064 49 Byelorussian    KISKI
  064 50 Polish          KISZKI
  064 87 BYELORUSSIAN P  KISKA
  064 86 UKRAINIAN P     KYSKA
b                      003
  064 89 SLOVAK P        CREVO
  064 42 Slovenian       CEJVA
  064 91 SLOVENIAN P     CREVO
  064 43 Lusatian L      CROWO
  064 44 Lusatian U      CRJEWO
  064 93 MACEDONIAN P    CREVO
  064 94 BULGARIAN P     CERVO
  064 53 Bulgarian       CERVA
  064 92 SERBOCROATIAN P CREVO
  064 90 CZECH P         STREVO
  064 47 Czech E         STREVA
b                      004
  064 46 Slovak          VNUTORNOSTI
  064 45 Czech           VNITRNOSTI
b                      005
  064 07 Breton ST       BOUZELLOU
  064 06 Breton SE       BOELLEU
  064 05 Breton List     BOUZELLOU
b                      006
  064 81 Albanian Top    ZORE
  064 95 ALBANIAN        ZORRET
  064 82 Albanian G      ZORRET
  064 84 Albanian C      ZOR
  064 83 Albanian K      ZORE
  064 80 Albanian T      ZORE
b                      007
  064 76 Persian List    RUDE
  064 77 Tadzik          RUDA, SLANG
b                      008
  064 75 Waziri          KULMA, LARMIN
  064 74 Afghan          KULMA
b                      009
  064 13 French          BOYAU
  064 14 Walloon         BOYE
  064 12 Provencal       BUDEU, BOUIEU
  064 23 Catalan         BUDELL
  064 16 French Creole D BUDE
  064 11 Ladin           BOGL
b                      010
  064 66 Greek ML        ANTERA
  064 68 Greek Mod       ANDERA
b                      100
  064 09 Vlach           MACE
  064 19 Sardinian C     MAZZAMINI
b                      101
  064 71 Armenian Mod    ALI
  064 72 Armenian List   AKHIK
b                      200
c                         200  2  201
c                         200  2  203
  064 64 Nepali List     ANRA
  064 59 Gujarati        ANTERLA
  064 60 Panjabi ST      ANDER
  064 62 Hindi           AT
  064 58 Marathi         ATEDE.
  064 17 Sardinian N     ENTRE
  064 54 Serbocroatian   UTROBA
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
  064 22 Brazilian       ENTRANHA, INTESTINO
b                      202
c                         201  2  202
  064 10 Italian         INTESTINO
  064 18 Sardinian L     INTESTINOS (M. PL.)
  064 20 Spanish         INTESTINO
b                      203
c                         200  2  203
c                         201  2  203
c                         203  2  204
  064 21 Portuguese ST   TRIPAS, ENTRANHAS
b                      204
c                         203  2  204
  064 15 French Creole C THWIP
b                      205
c                         205  2  206
  064 33 Danish          TARM
  064 32 Swedish List    TARM
  064 34 Riksmal         TARMER
  064 35 Icelandic ST    THARMAR
  064 28 Flemish         DARMEN
  064 26 Dutch List      DARM
  064 27 Afrikaans       INGEWAND, DERM
  064 24 German ST       EINGEWEIDE, GEDARM
  064 30 Swedish Up      TARMAR
  064 31 Swedish VL      TORMA
b                      206
c                         205  2  206
c                         206  2  207
  064 36 Faroese         TARMAR, GARNAR
b                      207
c                         206  2  207
  064 41 Latvian         ZARNAS
  064 40 Lithuanian ST   VIDURIAI, ZARNOS
a 065 HAIR
b                      001
  065 70 Greek K         KOME
  065 84 Albanian C      KRIP
  065 41 Latvian         MATS
  065 65 Khaskura        RAUN
  065 73 Ossetic         SAERYX"UYN
  065 79 Wakhi           SUFS, PICA
  065 78 Baluchi         PHUT
  065 38 Takitaki        WIWIRI
b                      002
  065 40 Lithuanian ST   PLAUKAS
  065 39 Lithuanian O    PLAUKAI
b                      003
  065 76 Persian List    MU
  065 77 Tadzik          MUJ
b                      004
  065 37 English ST      HAIR
  065 31 Swedish VL      HAR
  065 30 Swedish Up      HAR
  065 27 Afrikaans       HAAR, HARE
  065 26 Dutch List      HAAR
  065 25 Penn. Dutch     HORR
  065 28 Flemish         HAIR, HAER
  065 29 Frisian         HIER
  065 36 Faroese         HAR
  065 33 Danish          HAAR
  065 32 Swedish List    HAR
  065 34 Riksmal         HAR
  065 35 Icelandic ST    HAR
  065 24 German ST       HAAR
b                      005
  065 83 Albanian K      LES
  065 81 Albanian Top    LES
  065 80 Albanian T      LESHRA
b                      006
  065 82 Albanian G      FLOKU, KJIME
  065 95 ALBANIAN        KJIME
b                      007
  065 75 Waziri          WESHTE
  065 74 Afghan          VESTE
b                      008
  065 01 Irish A         GRUAIG
  065 02 Irish B         GRUAIG, GRUAIGE
b                      009
  065 54 Serbocroatian   KOSA
  065 93 MACEDONIAN P    KOSA
  065 52 Macedonian      KOSA
  065 53 Bulgarian       KOSA
b                      010
  065 71 Armenian Mod    MAZ, HER, GES
  065 72 Armenian List   MAZ
b                      200
c                         200  2  201
  065 13 French          CHEVEU
  065 15 French Creole C SIVE
  065 11 Ladin           CHAVE
  065 16 French Creole D SIVE
  065 14 Walloon         TCHIVE, DJ'VE
  065 21 Portuguese ST   CABELLO
  065 22 Brazilian       CABELO
b                      201
c                         200  2  201
c                         201  2  202
  065 20 Spanish         CABELLO, PELO
  065 23 Catalan         PEL, CABELLO
  065 10 Italian         PELO, CAPELLO
  065 12 Provencal       PEU, CABEU
b                      202
c                         201  2  202
  065 17 Sardinian N     PILU
  065 18 Sardinian L     PILU
  065 08 Rumanian List   PAR
  065 19 Sardinian C     PILU
  065 09 Vlach           PERI
b                      203
c                         203  3  204
c                         203  3  205
  065 46 Slovak          VLAS
  065 89 SLOVAK P        VLASY
  065 86 UKRAINIAN P     VOLOS
  065 92 SERBOCROATIAN P VLAS
  065 50 Polish          WLOSY
  065 88 POLISH P        WLOS
  065 51 Russian         VOLOSY
  065 85 RUSSIAN P       VOLOS
  065 94 BULGARIAN P     VLAS
  065 87 BYELORUSSIAN P  VOLAS
  065 45 Czech           VLASY
  065 90 CZECH P         VLAS
  065 44 Lusatian U      WLOS
  065 43 Lusatian L      LOS
  065 42 Slovenian       LASJE
  065 91 SLOVENIAN P     LAS
  065 49 Byelorussian    VOLAS
  065 47 Czech E         VLASI
  065 48 Ukrainian       VOLOSSJA, VOLOS
  065 04 Welsh C         GWALLT
  065 03 Welsh N         GWALLT
b                      204
c                         203  3  204
c                         204  2  205
  065 57 Kashmiri        MAS, RUM, WAL
  065 64 Nepali List     KAPAL, BAL
  065 55 Gypsy Gk        BALA
  065 61 Lahnda          WAL
  065 59 Gujarati        WAL
  065 60 Panjabi ST      VAL
b                      205
c                         203  3  205
c                         204  2  205
c                         205  2  206
  065 62 Hindi           BAL, KES
b                      206
c                         205  2  206
  065 56 Singhalese      KES, KONDE
  065 58 Marathi         KES
  065 63 Bengali         KES
b                      207
c                         207  3  208
  065 69 Greek D         MALLIA
  065 67 Greek MD        MALLIA
  065 68 Greek Mod       MALYA
  065 66 Greek ML        MALLIA
b                      208
c                         207  3  208
  065 07 Breton ST       BLEV
  065 06 Breton SE       BLEU
  065 05 Breton List     BLEO
a 066 HAND
b                      001
  066 73 Ossetic         K"YX
  066 59 Gujarati        NATH
b                      002
  066 17 Sardinian N     MANU
  066 18 Sardinian L     MANU
  066 09 Vlach           MYNE
  066 22 Brazilian       MAO
  066 21 Portuguese ST   MAO
  066 15 French Creole C LAME
  066 13 French          MAIN
  066 16 French Creole D LAME
  066 14 Walloon         MIN
  066 12 Provencal       MAIN
  066 20 Spanish         MANO
  066 23 Catalan         MA
  066 10 Italian         MANO
  066 19 Sardinian C     MANU
  066 11 Ladin           MAUN
  066 08 Rumanian List   MINA
b                      003
  066 27 Afrikaans       HAND
  066 26 Dutch List      HAND
  066 25 Penn. Dutch     HONNDT
  066 28 Flemish         HAND
  066 29 Frisian         HAN
  066 36 Faroese         HOND
  066 33 Danish          HAAND
  066 32 Swedish List    HAND
  066 34 Riksmal         HAND
  066 35 Icelandic ST    HOND
  066 24 German ST       HAND
  066 37 English ST      HAND
  066 38 Takitaki        HAN, HANOE
  066 30 Swedish Up      HAND
  066 31 Swedish VL      HAN
b                      004
  066 04 Welsh C         LLAW
  066 03 Welsh N         LLAW
  066 01 Irish A         LAMH
  066 02 Irish B         LAMH
b                      005
  066 47 Czech E         RUKA
  066 40 Lithuanian ST   RANKA
  066 39 Lithuanian O    RANKA
  066 41 Latvian         ROKA
  066 94 BULGARIAN P     RUKA
  066 87 BYELORUSSIAN P  RUKA
  066 45 Czech           RUKA
  066 90 CZECH P         RUKA
  066 43 Lusatian L      RUKA
  066 44 Lusatian U      RUKA
  066 93 MACEDONIAN P    RAKA
  066 50 Polish          REKA
  066 88 POLISH P        REKA
  066 51 Russian         RUKA
  066 85 RUSSIAN P       RUKA
  066 54 Serbocroatian   RUKA
  066 92 SERBOCROATIAN P RUKA
  066 46 Slovak          RUKA
  066 89 SLOVAK P        RUKA
  066 42 Slovenian       RAKA
  066 91 SLOVENIAN P     ROKA
  066 86 UKRAINIAN P     RUKA
  066 52 Macedonian      RAKA
  066 53 Bulgarian       REKA
  066 48 Ukrainian       RUKA
  066 49 Byelorussian    RUKA
b                      006
  066 07 Breton ST       DORN
  066 06 Breton SE       DORN
  066 05 Breton List     DOURN
b                      200
c                         200  3  201
c                         200  3  202
c                         200  3  203
  066 78 Baluchi         DAST
  066 79 Wakhi           DUST
  066 77 Tadzik          DAST
  066 76 Persian List    DAST
  066 61 Lahnda          HETH
  066 64 Nepali List     HAT
  066 57 Kashmiri        ATHA
  066 56 Singhalese      ATA
  066 65 Khaskura        HATH
  066 60 Panjabi ST      HETTH
  066 62 Hindi           HATH
  066 63 Bengali         HAT
  066 58 Marathi         HAT
b                      201
c                         200  3  201
c                         201  3  202
c                         201  3  203
  066 55 Gypsy Gk        VAS
b                      202
c                         200  3  202
c                         201  3  202
c                         202  3  203
  066 74 Afghan          LAS
  066 75 Waziri          LOS
b                      203
c                         200  3  203
c                         201  3  203
c                         202  3  203
  066 68 Greek Mod       CHERI
  066 66 Greek ML        CHERI
  066 70 Greek K         CHEIR
  066 67 Greek MD        CHERI
  066 69 Greek D         CHERI
  066 81 Albanian Top    DORE
  066 82 Albanian G      DORA
  066 84 Albanian C      DOR
  066 83 Albanian K      DORE
  066 80 Albanian T      DORE
  066 95 ALBANIAN        DORA
  066 71 Armenian Mod    JERK`
  066 72 Armenian List   ZARK
a 067 HE
b                      000
  067 72 Armenian List
b                      001
  067 74 Afghan          DE
  067 55 Gypsy Gk        KOVA
  067 09 Vlach           NESU
b                      002
  067 13 French          IL
  067 16 French Creole D I
  067 15 French Creole C I
  067 14 Walloon         I (BEFORE CONSONANT), IL (BEFORE VOWEL)
  067 20 Spanish         EL
  067 23 Catalan         LO
  067 10 Italian         EGLI
  067 11 Ladin           EL
  067 08 Rumanian List   EL
  067 22 Brazilian       ELE
  067 21 Portuguese ST   ELLE
  067 12 Provencal       EU
b                      003
  067 68 Greek Mod       AFTOS, TOS
  067 66 Greek ML        AUTOS
  067 70 Greek K         OUTOS
  067 67 Greek MD        AUTOS, TOU
  067 69 Greek D         AUTOS
b                      200
c                         200  2  201
c                         200  3  203
c                         200  2  207
c                         200  2  208
c                         200  2  209
  067 51 Russian         ON
  067 85 RUSSIAN P       ON
  067 54 Serbocroatian   ON
  067 92 SERBOCROATIAN P ON
  067 46 Slovak          ON
  067 89 SLOVAK P        ON
  067 42 Slovenian       ON
  067 91 SLOVENIAN P     ON
  067 86 UKRAINIAN P     VIN
  067 87 BYELORUSSIAN P  JON
  067 45 Czech           ON
  067 90 CZECH P         ON
  067 43 Lusatian L      WON
  067 44 Lusatian U      WON
  067 93 MACEDONIAN P    ON
  067 50 Polish          ON
  067 88 POLISH P        ON
  067 48 Ukrainian       VIN
  067 49 Byelorussian    EN
  067 47 Czech E         ON
  067 71 Armenian Mod    NA
b                      201
c                         200  2  201
c                         201  2  202
c                         201  3  203
c                         201  2  205
c                         201  2  206
c                         201  2  207
c                         201  2  208
c                         201  2  209
c                         201  2  210
  067 52 Macedonian      ON, TOJ
b                      202
c                         201  2  202
c                         202  2  205
c                         202  2  206
c                         202  2  207
c                         202  2  210
  067 94 BULGARIAN P     TOJ
  067 53 Bulgarian       TOJ
  067 58 Marathi         TO, HA
b                      203
c                         200  3  203
c                         201  3  203
c                         203  2  204
c                         203  3  208
c                         203  3  209
  067 30 Swedish Up      HAN
  067 31 Swedish VL      HAN
  067 36 Faroese         HANN
  067 33 Danish          HAN
  067 32 Swedish List    HAN
  067 34 Riksmal         HAN
  067 35 Icelandic ST    HANN
b                      204
c                         203  2  204
c                         204  3  208
  067 28 Flemish         HY
  067 27 Afrikaans       HY
  067 26 Dutch List      HIJ
  067 38 Takitaki        A, HEM
  067 37 English ST      HE
b                      205
c                         201  2  205
c                         202  2  205
c                         205  2  206
c                         205  2  207
c                         205  2  210
  067 64 Nepali List     TYO, SO
b                      206
c                         201  2  206
c                         202  2  206
c                         205  2  206
c                         206  2  207
c                         206  2  210
  067 01 Irish A         SE
  067 63 Bengali         SE
  067 57 Kashmiri        SUH
b                      207
c                         200  2  207
c                         201  2  207
c                         202  2  207
c                         205  2  207
c                         206  2  207
c                         207  2  208
c                         207  2  209
c                         207  2  210
  067 02 Irish B         E, SEISEAN, SE
b                      208
c                         200  2  208
c                         201  2  208
c                         203  3  208
c                         204  3  208
c                         207  2  208
c                         208  2  209
  067 29 Frisian         ER, HIJKE
b                      209
c                         200  2  209
c                         201  2  209
c                         203  3  209
c                         207  2  209
c                         208  2  209
  067 24 German ST       ER
  067 25 Penn. Dutch     ER
  067 07 Breton ST       EN
  067 06 Breton SE       EAN
  067 05 Breton List     HEN
  067 04 Welsh C         EFE
  067 03 Welsh N         EF
b                      210
c                         201  2  210
c                         202  2  210
c                         205  2  210
c                         206  2  210
c                         207  2  210
c                         210  3  211
c                         210  3  212
  067 59 Gujarati        E, TE
b                      211
c                         210  3  211
c                         211  3  212
  067 40 Lithuanian ST   JIS
  067 39 Lithuanian O    JIS
  067 17 Sardinian N     ISSE
  067 18 Sardinian L     IPSE
  067 19 Sardinian C     ISSU
  067 41 Latvian         VINS
b                      212
c                         210  3  212
c                         211  3  212
  067 81 Albanian Top    AY
  067 95 ALBANIAN        AI
  067 82 Albanian G      AI
  067 84 Albanian C      AJI
  067 83 Albanian K      AJ
  067 80 Albanian T      AY
b                      213
c                         213  3  214
c                         213  3  400
  067 65 Khaskura        U
  067 60 Panjabi ST      O
  067 56 Singhalese      OHU
  067 61 Lahnda          O
  067 62 Hindi           VOH, YEH
b                      214
c                         213  3  214
c                         214  3  400
  067 76 Persian List    U
  067 77 Tadzik          VAJ, U
  067 73 Ossetic         YU
b                      400
c                         213  3  400
c                         214  3  400
  067 79 Wakhi           YA
  067 78 Baluchi         I, CHI, ANH
  067 75 Waziri          AGHA
a 068 HEAD
b                      001
  068 57 Kashmiri        KALA
  068 81 Albanian Top    KOKE
  068 56 Singhalese      OLUWA, HISA
b                      002
  068 40 Lithuanian ST   GALVA
  068 39 Lithuanian O    GALVA
  068 41 Latvian         GALVA
  068 94 BULGARIAN P     GLAVA
  068 87 BYELORUSSIAN P  HALAVA
  068 45 Czech           HLAVA
  068 90 CZECH P         HLAVA
  068 43 Lusatian L      GLOWA
  068 44 Lusatian U      HLOWA
  068 93 MACEDONIAN P    GLAVA
  068 50 Polish          GLOWA
  068 88 POLISH P        GLOWA
  068 51 Russian         GOLOVA
  068 85 RUSSIAN P       GOLOVA
  068 54 Serbocroatian   GLAVA
  068 92 SERBOCROATIAN P GLAVA
  068 46 Slovak          HLAVA
  068 89 SLOVAK P        HLAVA
  068 42 Slovenian       GLAVA
  068 91 SLOVENIAN P     GLAVA
  068 86 UKRAINIAN P     HOLOVA
  068 52 Macedonian      GLAVA
  068 53 Bulgarian       GLAVA
  068 48 Ukrainian       GOLOVA
  068 49 Byelorussian    GALAVA
  068 47 Czech E         HLAVA
b                      003
  068 82 Albanian G      KRYET
  068 84 Albanian C      KRIE
  068 83 Albanian K      KRIE
  068 80 Albanian T      KRYE
  068 95 ALBANIAN        KRYET, KREJ
b                      004
  068 07 Breton ST       PENN
  068 06 Breton SE       PENN
  068 05 Breton List     PENN
  068 04 Welsh C         PEN
  068 03 Welsh N         PEN
  068 01 Irish A         CEANN
  068 02 Irish B         CEANN
b                      005
  068 71 Armenian Mod    GLUX
  068 72 Armenian List   GALOKH
b                      006
  068 19 Sardinian C     KONKA
  068 17 Sardinian N     KONKA
b                      007
  068 68 Greek Mod       KEFALI
  068 66 Greek ML        KEFALI
  068 70 Greek K         KEFALE
  068 67 Greek MD        KEFALI
  068 69 Greek D         KEFALI
b                      200
c                         200  2  201
  068 18 Sardinian L     TESTA
  068 15 French Creole C TET
  068 11 Ladin           TESTA
  068 10 Italian         TESTA
  068 13 French          TETE
  068 16 French Creole D TET
  068 14 Walloon         TIESSE
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
  068 12 Provencal       TESTO, CABESSO, CAP
b                      202
c                         201  2  202
c                         202  2  203
  068 20 Spanish         CABEZA
  068 09 Vlach           KAPU
  068 08 Rumanian List   CAP
  068 23 Catalan         CAP
  068 22 Brazilian       CABECA
  068 21 Portuguese ST   CABECA
  068 37 English ST      HEAD
  068 38 Takitaki        HEDE
  068 30 Swedish Up      HUVUD
  068 31 Swedish VL      HUVA
  068 36 Faroese         HOVD
  068 33 Danish          HOVED
  068 32 Swedish List    HUVUD
  068 34 Riksmal         HODE
  068 35 Icelandic ST    HOFUO
  068 26 Dutch List      HOOFD
  068 28 Flemish         HOOFD
b                      203
c                         201  2  203
c                         202  2  203
c                         203  2  204
  068 29 Frisian         HAED, KOP
  068 27 Afrikaans       HOOF, KOP
b                      204
c                         203  2  204
  068 25 Penn. Dutch     KUP
  068 24 German ST       KOPF
b                      205
c                         205  2  206
  068 76 Persian List    SAR
  068 60 Panjabi ST      SIR
  068 62 Hindi           SIR
  068 75 Waziri          SAR
  068 55 Gypsy Gk        SORO
  068 73 Ossetic         SAER
  068 74 Afghan          SAR
  068 78 Baluchi         SAGHAR
  068 79 Wakhi           SER
  068 61 Lahnda          SIR
  068 77 Tadzik          SAR, KALLA
b                      206
c                         205  2  206
c                         206  2  207
c                         206  2  208
c                         206  3  209
  068 64 Nepali List     MANTO, MATH, SIR, TAUKO
b                      207
c                         206  2  207
  068 59 Gujarati        MATHU
  068 63 Bengali         MATHA
b                      208
c                         206  2  208
c                         208  3  209
  068 65 Khaskura        TAUKO, MUNTO
b                      209
c                         206  3  209
c                         208  3  209
  068 58 Marathi         DOKE.
a 069 TO HEAR
b                      001
  069 56 Singhalese      AHANAWA
  069 57 Kashmiri        BOZUN
  069 58 Marathi         EYKNE.
  069 59 Gujarati        SAMBHELEWU
b                      002
  069 40 Lithuanian ST   GIRDE TI
  069 39 Lithuanian O    GIRDETI
  069 41 Latvian         DZIRDET
b                      003
  069 37 English ST      TO HEAR
  069 38 Takitaki        JERI
  069 30 Swedish Up      HORA
  069 31 Swedish VL      HOR
  069 27 Afrikaans       HOOR
  069 26 Dutch List      HOOREN
  069 25 Penn. Dutch     HAIIR
  069 28 Flemish         HOOREN
  069 29 Frisian         HEARE
  069 36 Faroese         HOYRA
  069 33 Danish          HORE
  069 32 Swedish List    HORA
  069 34 Riksmal         HORE
  069 35 Icelandic ST    HEYRA
  069 24 German ST       HOREN
  069 68 Greek Mod       AKUO
  069 66 Greek ML        AKOUGO
  069 70 Greek K         AKOUO
  069 67 Greek MD        AKOUO
  069 69 Greek D         AKOUO
b                      004
  069 74 Afghan          ARVEDEL
  069 75 Waziri          WORWEDEL, ARWEDEL
b                      100
  069 79 Wakhi           KSUI-
  069 73 Ossetic         X"YCYN
  069 78 Baluchi         ASKHANAGH, ASKHUTHA
b                      200
c                         200  2  201
  069 18 Sardinian L     INTENDERE
  069 17 Sardinian N     INTENNERE
  069 15 French Creole C TAN
  069 19 Sardinian C     INTENDI
  069 13 French          ENTENDRE
  069 16 French Creole D TAN
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
  069 12 Provencal       ENTENDRE, AUSI
b                      202
c                         201  2  202
c                         202  2  203
  069 08 Rumanian List   A AUZI
  069 11 Ladin           UDIR
  069 09 Vlach           AVDU
  069 20 Spanish         OIR
  069 22 Brazilian       OUVIR
  069 21 Portuguese ST   OUVIR
  069 14 Walloon         ORE, OYI
c                         201  2  203
c                         202  2  203
c                         203  2  204
b                      203
  069 10 Italian         UDIRE, SENTIRE
b                      204
c                         203  2  204
  069 23 Catalan         SENTIR
b                      205
c                         205  2  206
  069 94 BULGARIAN P     SLUSAM
  069 87 BYELORUSSIAN P  SLUCHAC
  069 45 Czech           SLYSETI
  069 90 CZECH P         SLYSETI
  069 43 Lusatian L      SLYSAS
  069 44 Lusatian U      SLYSEC
  069 93 MACEDONIAN P    SLUSAM
  069 50 Polish          SLYSZEC
  069 88 POLISH P        SLYSZEC
  069 51 Russian         SLYSAT
  069 85 RUSSIAN P       SLUSAT
  069 92 SERBOCROATIAN P SLUSATI
  069 89 SLOVAK P        SLYSAT
  069 91 SLOVENIAN P     SLUSATI
  069 86 UKRAINIAN P     SLUCHATY
  069 07 Breton ST       KLEVOUT
  069 06 Breton SE       KLEUEIN
  069 05 Breton List     KLEVOUT, KLEVET
  069 04 Welsh C         CLYWED
  069 03 Welsh N         CLYWED
  069 01 Irish A         CLOS
  069 02 Irish B         AINIGHIM, CLOISIM
  069 64 Nepali List     SUNNU
  069 55 Gypsy Gk        ASUNAV
  069 61 Lahnda          SUNNEN
  069 77 Tadzik          SUNIDAN
  069 76 Persian List    SHENIDAN
  069 65 Khaskura        SUNNU
  069 60 Panjabi ST      SUNENA
  069 62 Hindi           SUNNA
  069 63 Bengali         SONA
  069 71 Armenian Mod    LSEL
  069 72 Armenian List   LUREL
b                      206
c                         205  2  206
c                         206  2  207
  069 48 Ukrainian       SLUXATY, CUTY
b                      207
c                         206  2  207
  069 42 Slovenian       CUJES
  069 46 Slovak          CUT
  069 54 Serbocroatian   CUTI
  069 52 Macedonian      DOCUE, CUE
  069 49 Byelorussian    CUC'
  069 47 Czech E         CUT
  069 53 Bulgarian       DA CUVA
b                      208
c                         208  3  209
  069 84 Albanian C      GEGEM
  069 83 Albanian K      GIGEM (AOR. GEJSE)
b                      209
c                         208  3  209
  069 80 Albanian T      ME DEGJUAR
  069 82 Albanian G      NDEGJOJ
  069 81 Albanian Top    DEGON, AOR. DEGOVA
  069 95 ALBANIAN        NDEGJOJ
a 070 HEART
b                      000
  070 59 Gujarati        (HREDEY)
b                      001
  070 63 Bengali         BUK
  070 55 Gypsy Gk        ILO
  070 79 Wakhi           PEZUV
  070 76 Persian List    QALB
b                      002
  070 81 Albanian Top    ZEMER
  070 82 Albanian G      ZEMER
  070 84 Albanian C      ZEMBER
  070 83 Albanian K      ZEMERE
  070 80 Albanian T      ZEMER
  070 95 ALBANIAN        ZEMER
b                      003
  070 15 French Creole C CE
  070 16 French Creole D CE
b                      004
  070 44 Lusatian U      WUTROBA
  070 43 Lusatian L      HUTSOBA
b                      005
  070 07 Breton ST       KALON
  070 06 Breton SE       KALON
  070 05 Breton List     KALON
  070 04 Welsh C         CALON
  070 03 Welsh N         CALON
b                      006
  070 08 Rumanian List   INIMA
  070 09 Vlach           INIMA
b                      007
  070 62 Hindi           DIL, HRIDEY
  070 61 Lahnda          DIL
  070 78 Baluchi         DIL
  070 77 Tadzik          DIL
  070 60 Panjabi ST      DIL
  070 57 Kashmiri        DIL, REDA, WOLINJ
b                      200
c                         200  2  201
  070 30 Swedish Up      HJARTA
  070 31 Swedish VL      JATA
  070 17 Sardinian N     KORO
  070 18 Sardinian L     CORO
  070 73 Ossetic         ZAERDAE
  070 93 MACEDONIAN P    SRCE
  070 50 Polish          SERCE
  070 88 POLISH P        SERCE
  070 51 Russian         SERDCE
  070 85 RUSSIAN P       SERDCE
  070 54 Serbocroatian   SRCE
  070 92 SERBOCROATIAN P SRCE
  070 46 Slovak          SRDCE
  070 89 SLOVAK P        SRDCE
  070 42 Slovenian       SRCJ
  070 91 SLOVENIAN P     SRCE
  070 86 UKRAINIAN P     SERCE
  070 68 Greek Mod       KARDHYA
  070 66 Greek ML        KARDIA
  070 70 Greek K         KARDIA
  070 67 Greek MD        KARDIA
  070 69 Greek D         KARDIA
  070 40 Lithuanian ST   SIRDIS
  070 39 Lithuanian O    SIRDIS
  070 41 Latvian         SIRDS
  070 94 BULGARIAN P     SURCE
  070 87 BYELORUSSIAN P  SERCA
  070 45 Czech           SRDCE
  070 90 CZECH P         SRDCE
  070 56 Singhalese      PAPUWA, HRADAYA
  070 74 Afghan          ZRE
  070 14 Walloon         COUR
  070 12 Provencal       COR
  070 20 Spanish         CORAZON
  070 23 Catalan         COR
  070 10 Italian         CUORE
  070 19 Sardinian C     KORI
  070 11 Ladin           COUR
  070 01 Irish A         CROIDHE
  070 02 Irish B         CROIDHE
  070 13 French          COEUR
  070 27 Afrikaans       HART
  070 26 Dutch List      HART
  070 25 Penn. Dutch     HOTZ
  070 28 Flemish         HART
  070 29 Frisian         HART
  070 36 Faroese         HJARTA
  070 33 Danish          HJERTE
  070 32 Swedish List    HJARTA
  070 34 Riksmal         HJERTE
  070 35 Icelandic ST    HJARTA
  070 24 German ST       HERZ
  070 52 Macedonian      SRCE
  070 58 Marathi         HRIDEY
  070 37 English ST      HEART
  070 38 Takitaki        HATTI
  070 75 Waziri          ZRE
  070 72 Armenian List   SIRD
  070 22 Brazilian       CORACAO
  070 21 Portuguese ST   CORACAO
  070 53 Bulgarian       SERCE
  070 48 Ukrainian       SERCE
  070 49 Byelorussian    SERCA
  070 47 Czech E         SRDCO
  070 71 Armenian Mod    SIRT
b                      201
c                         200  2  201
c                         201  2  202
  070 64 Nepali List     HIYO, MUTU
b                      202
c                         201  2  202
  070 65 Khaskura        MUTO
a 071 HEAVY
b                      000
  071 36 Faroese
b                      001
  071 57 Kashmiri        GOBU
  071 58 Marathi         JED
  071 29 Frisian         LEADICH, POUNICH
  071 41 Latvian         SMAGS
b                      002
  071 82 Albanian G      RAND
  071 84 Albanian C      I-REND
  071 83 Albanian K      IRENDE
  071 80 Albanian T      I, E RENDE
  071 95 ALBANIAN        RAND
  071 81 Albanian Top    I-RENDE
b                      003
  071 04 Welsh C         TRWM
  071 03 Welsh N         TRWM
  071 01 Irish A         TROM
  071 02 Irish B         IOMTHROM
b                      004
  071 74 Afghan          DRUND
  071 75 Waziri          DRIND, SAKHT
b                      005
  071 40 Lithuanian ST   SUNKUS
  071 39 Lithuanian O    SUNKUS
b                      006
  071 37 English ST      HEAVY
  071 38 Takitaki        HEBI
b                      007
  071 45 Czech           TEZKY
  071 90 CZECH P         TEZKY
  071 87 BYELORUSSIAN P  C AZKI
  071 94 BULGARIAN P     TEZUK
  071 43 Lusatian L      SEZKI
  071 44 Lusatian U      CEZKI
  071 93 MACEDONIAN P    TEZOK
  071 50 Polish          CIEZKI
  071 88 POLISH P        CIEZKI
  071 51 Russian         TJAZELYJ
  071 85 RUSSIAN P       T AZOLYJ
  071 54 Serbocroatian   TEZAK
  071 92 SERBOCROATIAN P TEZAK
  071 46 Slovak          TAZKY
  071 89 SLOVAK P        T AZKY
  071 42 Slovenian       TEZKO, TESKO
  071 91 SLOVENIAN P     TEZEK
  071 86 UKRAINIAN P     T AZKYJ
  071 52 Macedonian      TEZOK
  071 53 Bulgarian       TEZKO
  071 48 Ukrainian       TJAZKYJ
  071 49 Byelorussian    CJAZKI
  071 47 Czech E         TYASKE
  071 30 Swedish Up      TUNG
  071 31 Swedish VL      TONG
  071 33 Danish          TUNG
  071 34 Riksmal         TUNG
  071 35 Icelandic ST    THUNGR
b                      008
  071 24 German ST       SCHWER
  071 32 Swedish List    SVAR, STOR
  071 27 Afrikaans       SWAAR
  071 26 Dutch List      ZWAAR
  071 25 Penn. Dutch     SCHWAIIR
  071 28 Flemish         ZWAAR
b                      009
  071 71 Armenian Mod    CANR
  071 72 Armenian List   ZUNNER
b                      010
  071 05 Breton List     POUNNER
  071 07 Breton ST       PONNER
  071 06 Breton SE       PONNER
b                      200
c                         200  2  201
c                         200  2  202
c                         200  2  205
c                         200  3  400
  071 66 Greek ML        BARUS
  071 68 Greek Mod       VARIS
  071 70 Greek K         BARUS
  071 67 Greek MD        BARUS
  071 69 Greek D         BARUS
  071 09 Vlach           GREU
  071 18 Sardinian L     GRAVE
  071 19 Sardinian C     GRAI
  071 08 Rumanian List   GREU
  071 65 Khaskura        GARUNGO
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  204
c                         201  2  205
c                         201  3  400
  071 10 Italian         PESANTE, GREVE
  071 20 Spanish         GRAVE, PESADO
b                      202
c                         200  2  202
c                         201  2  202
c                         202  2  203
c                         202  2  205
c                         202  3  400
  071 12 Provencal       LOURD, GREU, EVO
b                      203
c                         202  2  203
  071 13 French          LOURD
  071 15 French Creole C LU
  071 16 French Creole D LU
  071 14 Walloon         LOUR(D)
b                      204
c                         201  2  204
  071 21 Portuguese ST   PESADO
  071 22 Brazilian       PESADO
  071 11 Ladin           PESANT
  071 23 Catalan         FEIXUCH, PESANT
  071 17 Sardinian N     PESANTE
b                      205
c                         200  2  205
c                         201  2  205
c                         202  2  205
c                         205  2  206
c                         205  3  400
  071 64 Nepali List     GARAU, BHARI
b                      206
c                         205  2  206
  071 56 Singhalese      BARA
  071 61 Lahnda          BHARI
  071 62 Hindi           BHARI
  071 63 Bengali         BHARI
  071 59 Gujarati        BHARE
  071 60 Panjabi ST      PARA
  071 55 Gypsy Gk        PHARO
b                      400
c                         200  3  400
c                         201  3  400
c                         202  3  400
c                         205  3  400
  071 78 Baluchi         GIRAN
  071 79 Wakhi           GHURUNG
b                      207
c                         207  2  208
  071 73 Ossetic         UAEZZAU
b                      208
c                         207  2  208
c                         208  2  209
  071 77 Tadzik          VAZNIN, SANGI VAZNIN
b                      209
c                         208  2  209
  071 76 Persian List    SANGIN
a 072 HERE
b                      001
  072 09 Vlach           AWA
  072 71 Armenian Mod    AYSTEL
  072 14 Walloon         CHAL
  072 77 Tadzik          DAR NI CO, NI CO
  072 38 Takitaki        DIA, DIASO
  072 72 Armenian List   HOS
  072 76 Persian List    INJA
  072 56 Singhalese      METANA
b                      002
  072 75 Waziri          DELE, DOLATA
  072 74 Afghan          DELTA, DALE
b                      003
  072 37 English ST      HERE
  072 27 Afrikaans       HIER
  072 26 Dutch List      HIER
  072 25 Penn. Dutch     HAIIR
  072 28 Flemish         HIER
  072 29 Frisian         HJIR, HJIRRE
  072 36 Faroese         HER
  072 33 Danish          HER
  072 32 Swedish List    HAR
  072 34 Riksmal         HER
  072 35 Icelandic ST    HER(NA)
  072 24 German ST       HIER
  072 30 Swedish Up      HAR
  072 31 Swedish VL      HAR, HENA  HENAN
b                      004
  072 66 Greek ML        EDO
  072 70 Greek K         EDO
  072 67 Greek MD        EDO
  072 69 Greek D         EDO
  072 68 Greek Mod       EDHO
b                      005
  072 95 ALBANIAN        KETU
  072 82 Albanian G      KETU
  072 84 Albanian C      XTU
  072 83 Albanian K      KETU
  072 80 Albanian T      KETU
  072 81 Albanian Top    KETU
b                      200
c                         200  2  201
c                         200  2  203
  072 65 Khaskura        YAHAN
  072 62 Hindi           YEHA
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
  072 64 Nepali List     YATA, YAHA
b                      202
c                         201  2  202
  072 57 Kashmiri        YOR, YUTU
b                      203
c                         200  2  203
c                         201  2  203
c                         203  3  204
c                         203  3  205
c                         203  3  206
c                         203  3  207
  072 79 Wakhi           DREM, HADREM, YEM, YAEI
b                      204
c                         203  3  204
c                         204  3  205
c                         204  3  206
c                         204  3  207
  072 73 Ossetic         AM
b                      205
c                         203  3  205
c                         204  3  205
c                         205  3  206
c                         205  3  207
  072 07 Breton ST       AMAN
  072 06 Breton SE       AMEN
  072 05 Breton List     AMAN, DU-MAN
  072 04 Welsh C         YMA
  072 03 Welsh N         YMA
b                      206
c                         203  3  206
c                         204  3  206
c                         205  3  206
c                         206  2  207
  072 01 Irish A         ANNSO
b                      207
c                         203  3  207
c                         204  3  207
c                         205  3  207
c                         206  2  207
  072 02 Irish B         AG SO
b                      208
c                         208  2  209
c                         208  3  210
  072 61 Lahnda          ITTHA
  072 60 Panjabi ST      ETTHE
b                      209
c                         208  2  209
c                         209  3  210
c                         209  3  400
  072 58 Marathi         ITHE., IKDE.
b                      210
c                         208  3  210
c                         209  3  210
  072 78 Baluchi         EDHA
b                      400
c                         209  3  400
  072 59 Gujarati        EHI
  072 63 Bengali         EKHANE
b                      211
c                         211  2  212
c                         211  2  214
c                         211  3  216
c                         211  3  217
  072 86 UKRAINIAN P     TUT
  072 92 SERBOCROATIAN P TU
  072 89 SLOVAK P        TU
  072 42 Slovenian       TUKAJ
  072 43 Lusatian L      TU
  072 44 Lusatian U      TU
  072 93 MACEDONIAN P    TUKA
  072 50 Polish          TU
  072 88 POLISH P        TU
  072 94 BULGARIAN P     TUK
  072 87 BYELORUSSIAN P  TUT
  072 53 Bulgarian       TUK
  072 48 Ukrainian       TUT, OS'TUT
  072 49 Byelorussian    TUT, TUTAKA
b                      212
c                         211  2  212
c                         212  2  213
c                         212  2  214
c                         212  3  216
c                         212  3  217
  072 52 Macedonian      HAVAKA, OVDE, OVDEKA, TUKA, TYKA
b                      213
c                         212  2  213
c                         213  3  215
  072 54 Serbocroatian   OVDE
b                      214
c                         211  2  214
c                         212  2  214
c                         214  2  215
c                         214  2  216
c                         214  3  217
  072 47 Czech E         TU, TADI, SEM
  072 46 Slovak          TU, SEM
b                      215
c                         213  3  215
c                         214  2  215
c                         215  2  216
  072 91 SLOVENIAN P     ZDE
  072 51 Russian         ZDES
  072 85 RUSSIAN P       ZDES
  072 45 Czech           ZDE
  072 90 CZECH P         ZDE
b                      216
c                         211  3  216
c                         212  3  216
c                         214  2  216
c                         215  2  216
c                         216  3  217
  072 39 Lithuanian O    CIA, SICIA
  072 40 Lithuanian ST   CIA
  072 41 Latvian         SEIT
  072 13 French          ICI
  072 15 French Creole C ESIT, ISI
  072 11 Ladin           TSCHO, ACCO / ACQUI, QUI
  072 16 French Creole D ISI
  072 12 Provencal       EICI, CAI
  072 20 Spanish         AQUI
  072 23 Catalan         AQUI, ENSA
  072 10 Italian         QUI, QUA
  072 22 Brazilian       AQUI
  072 21 Portuguese ST   AQUI
  072 08 Rumanian List   AICI, INCOACE
  072 19 Sardinian C     INNOI
  072 17 Sardinian N     INOKKE
  072 18 Sardinian L     INOGHE
b                      217
c                         211  3  217
c                         212  3  217
c                         214  3  217
c                         216  3  217
  072 55 Gypsy Gk        KATE
a 073 TO HIT
b                      001
  073 09 Vlach           AGUDESKU
  073 08 Rumanian List   A NIMERI, A LOVI
  073 14 Walloon         (SOMEONE) BOUHI, FERI, MAKER D'SSUS
  073 55 Gypsy Gk        CALAVAV
  073 21 Portuguese ST   DAR UMA PANCADA
  073 79 Wakhi           DI-
  073 84 Albanian C      FORT
  073 13 French          FRAPPER
  073 37 English ST      TO HIT
  073 41 Latvian         IESIST
  073 57 Kashmiri        LAYUN
  073 40 Lithuanian ST   MUSTI
  073 38 Takitaki        NAKI
  073 73 Ossetic         NAEMYN
  073 52 Macedonian      PERNE
  073 12 Provencal       PICA, TABASA, BACELA
  073 19 Sardinian C     PIGAI
  073 39 Lithuanian O    SUDUOTI
  073 45 Czech           UHODITI
b                      002
  073 95 ALBANIAN        RRAF
  073 82 Albanian G      RRAF, SILL
  073 83 Albanian K      I BIE (AOR. I-RAASE)
b                      003
  073 80 Albanian T      ME GODITUR
  073 81 Albanian Top    GODIT, AOR. GODITA
b                      004
  073 74 Afghan          VAHEL
  073 75 Waziri          WAHEL, TAKAWEL
b                      005
  073 07 Breton ST       SKEIN
  073 06 Breton SE       SKOEIN
  073 05 Breton List     SKEI
b                      006
  073 16 French Creole D FUTE
  073 15 French Creole C FUTE, BAY KU
b                      007
  073 18 Sardinian L     COLPIRE
  073 11 Ladin           COLPIR
  073 22 Brazilian       GOLPEAR
  073 20 Spanish         GOLPEAR
  073 17 Sardinian N     KURPIRE
  073 23 Catalan         COPEJAR, BATRER
  073 10 Italian         BATTERE, COLPIRE
b                      008
  073 71 Armenian Mod    XPEL, ZARKEL
  073 72 Armenian List   ZARNELL
b                      009
  073 01 Irish A         BUALADH
  073 02 Irish B         D'AMUS, DO BHUALADH
b                      010
  073 03 Welsh N         TARO
  073 04 Welsh C         BWRW, TARO
b                      200
c                         200  2  201
c                         200  2  202
  073 35 Icelandic ST    SLA
  073 34 Riksmal         SLA
  073 32 Swedish List    SLA
  073 25 Penn. Dutch     SCHLOCK
  073 36 Faroese         SLAA
  073 29 Frisian         SLAEN
  073 27 Afrikaans       SLAAN, RAPS
  073 31 Swedish VL      SLA  SLA
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
  073 24 German ST       SCHLAGEN, TREFFEN
b                      202
c                         200  2  202
c                         201  2  202
c                         202  2  203
c                         202  2  204
  073 28 Flemish         SLAEN, TREFFEN, RAKEN
b                      203
c                         201  2  203
c                         202  2  203
  073 30 Swedish Up      TRAFFA
  073 33 Danish          RAMME, TRAEFFE
b                      204
c                         202  2  204
  073 26 Dutch List      RAKEN, STOOTEN
b                      205
c                         205  2  206
  073 85 RUSSIAN P       UDARIT
  073 54 Serbocroatian   UDARITI
  073 92 SERBOCROATIAN P UDARITI
  073 46 Slovak          UDERIT, UDIERAT
  073 89 SLOVAK P        UDERIT
  073 42 Slovenian       UDARIT
  073 91 SLOVENIAN P     UDARITI
  073 86 UKRAINIAN P     UDARYTY
  073 88 POLISH P        UDERZAC
  073 43 Lusatian L      DERIS
  073 44 Lusatian U      DYRIC
  073 93 MACEDONIAN P    UDARAM
  073 94 BULGARIAN P     UDAR AM
  073 87 BYELORUSSIAN P  UDARAC
  073 53 Bulgarian       DA UDARI
  073 48 Ukrainian       UDARJATY
  073 49 Byelorussian    UDARAC'
b                      206
c                         205  2  206
c                         206  2  207
  073 47 Czech E         UDERIT, BIT
b                      207
c                         206  2  207
  073 51 Russian         BIT
  073 50 Polish          BIC
  073 90 CZECH P         BITI
b                      208
c                         208  3  209
  073 68 Greek Mod       KHTIPO
  073 66 Greek ML        CHTUPO
  073 70 Greek K         KTUPO
  073 67 Greek MD        CHTUPO
b                      209
c                         208  3  209
  073 69 Greek D         CHLUPAO
b                      210
c                         210  3  211
c                         210  3  212
  073 77 Tadzik          ZADAN, ZARBA ZADAN
  073 76 Persian List    ZADAN
b                      211
c                         210  3  211
c                         211  2  212
  073 65 Khaskura        HANNU, HIRKANU
  073 56 Singhalese      GAHANAWA
  073 78 Baluchi         JANAGH
b                      212
c                         210  3  212
c                         211  2  212
c                         212  2  213
  073 64 Nepali List     THOKNU, HANNU
b                      213
c                         212  2  213
c                         213  2  214
  073 60 Panjabi ST      THOKKER+MARNA
b                      214
c                         213  2  214
  073 62 Hindi           MARNA
  073 58 Marathi         APETNE., MARNE.
  073 63 Bengali         MARA
  073 61 Lahnda          MAREN
  073 59 Gujarati        MAREWU
a 074 HOLD (IN HAND)
b                      000
  074 64 Nepali List
  074 78 Baluchi
b                      001
  074 56 Singhalese      ALLAGANAWA
  074 55 Gypsy Gk        ASTARAV
  074 66 Greek ML        BASTO
  074 02 Irish B         CONGABHAIM
  074 25 Penn. Dutch     HAYB
  074 57 Kashmiri        HYONU, RATUN
  074 74 Afghan          LAREL
  074 75 Waziri          NIWEL, SOTEL
  074 17 Sardinian N     REGERE
  074 01 Irish A         RUD DO CHOINNEAIL SA LAIMH
  074 65 Khaskura        THAMNU
  074 41 Latvian         TURET
  074 71 Armenian Mod    UNEL
  074 73 Ossetic         XAECYN
  074 79 Wakhi           WUDER
b                      002
  074 68 Greek Mod       KRATO
  074 69 Greek D         KRATAO
  074 67 Greek MD        KRATO
  074 70 Greek K         KRATO
b                      003
  074 59 Gujarati        PEKERWU
  074 61 Lahnda          PEKREN
b                      004
  074 10 Italian         TENERE
  074 23 Catalan         TENIR
  074 20 Spanish         TENER
  074 12 Provencal       TENI
  074 14 Walloon         TINI, TINRE
  074 16 French Creole D CEN
  074 13 French          TENIR
  074 22 Brazilian       TER
  074 21 Portuguese ST   TER
  074 18 Sardinian L     TENNERE
  074 15 French Creole C CEN
  074 08 Rumanian List   A TINE
  074 11 Ladin           TGNAIR, TEGNER
  074 19 Sardinian C     TENNI
  074 09 Vlach           CYNU
b                      005
  074 48 Ukrainian       TRYMATY
  074 50 Polish          TRZYMAC
  074 87 BYELORUSSIAN P  TRYMAC
  074 49 Byelorussian    TPYMAC'
b                      006
  074 05 Breton List     DERC'HEL
  074 03 Welsh N         DAL
  074 06 Breton SE       DALHEIN
  074 04 Welsh C         DAL
  074 07 Breton ST       DERC'HEL
b                      007
  074 40 Lithuanian ST   LAIKYTI
  074 39 Lithuanian O    LAIKYTI
b                      008
  074 81 Albanian Top    MBAN, AOR. MBAJTA
  074 80 Albanian T      ME MBAJTUR
  074 83 Albanian K      MBAA   BAA
  074 84 Albanian C      MBAN
b                      009
  074 82 Albanian G      MARR
  074 95 ALBANIAN        MARR
b                      010
  074 52 Macedonian      DRZI
  074 47 Czech E         DRZAT
  074 53 Bulgarian       DERZI
  074 93 MACEDONIAN P    DRZAM
  074 86 UKRAINIAN P     DERZATY
  074 91 SLOVENIAN P     DRZATI
  074 42 Slovenian       DRZAT U RAKI
  074 89 SLOVAK P        DRZAT
  074 46 Slovak          DRZAT
  074 92 SERBOCROATIAN P DRZATI
  074 54 Serbocroatian   DRZATI
  074 85 RUSSIAN P       DERZAT
  074 51 Russian         DERZAT
  074 88 POLISH P        DZIERZYC
  074 44 Lusatian U      DZERZEC
  074 43 Lusatian L      ZARZAS
  074 90 CZECH P         DRZETI
  074 45 Czech           DRZETI
  074 94 BULGARIAN P     DURZA
  074 62 Hindi           DHERNA
  074 63 Bengali         DHORA
  074 58 Marathi         DHERNE.
b                      100
  074 72 Armenian List   BURNE
  074 60 Panjabi ST      PHERNA
b                      200
c                         200  2  201
  074 37 English ST      HOLD
  074 31 Swedish VL      HAL  HOL
  074 30 Swedish Up      HALLA
  074 24 German ST       HALTEN
  074 35 Icelandic ST    HALDA
  074 34 Riksmal         HOLDE
  074 32 Swedish List     FAST  HALLA
  074 33 Danish          HOLDE
  074 36 Faroese         HALDA
  074 29 Frisian         FESTHALDE, HALDE
  074 26 Dutch List      HOUDEN
  074 27 Afrikaans       HOU
  074 38 Takitaki        HOLI
b                      201
c                         200  2  201
c                         201  2  202
  074 28 Flemish         GRYPEN, VASTHOUDEN
b                      202
c                         201  2  202
  074 76 Persian List    GEREFTAN
  074 77 Tadzik          DAST GIRIFTAN
a 075 HOW
b                      000
  075 38 Takitaki
b                      002
  075 04 Welsh C         SUT
  075 03 Welsh N         SUT
b                      200
c                         200  3  201
c                         200  3  202
c                         200  3  203
c                         200  3  204
c                         200  3  205
  075 37 English ST      HOW
  075 27 Afrikaans       HOE
  075 26 Dutch List      HOE
  075 28 Flemish         HOE
  075 32 Swedish List    HUR  U
  075 30 Swedish Up      HUR
  075 35 Icelandic ST    HVERNIG, HVERSU
  075 31 Swedish VL      HORA
  075 33 Danish          HOORLEDES
  075 34 Riksmal         HVORLEDES
  075 36 Faroese         HVUSSUR
  075 29 Frisian         HO'T
  075 52 Macedonian      KAKO
  075 91 SLOVENIAN P     KAKO
  075 42 Slovenian       KAKO
  075 92 SERBOCROATIAN P KAKO
  075 54 Serbocroatian   KAKO
  075 93 MACEDONIAN P    KAKO
  075 85 RUSSIAN P       KAK
  075 51 Russian         KAK
  075 44 Lusatian U      KAK
  075 43 Lusatian L      KAK
  075 94 BULGARIAN P     KAK
  075 53 Bulgarian       KAK
  075 40 Lithuanian ST   KAIP
  075 39 Lithuanian O    KAIP
  075 41 Latvian         KA
  075 64 Nepali List     KASO
  075 58 Marathi         KESA
  075 62 Hindi           KESA
  075 60 Panjabi ST      KIS+TERA
  075 65 Khaskura        KASTO, KASTARI
  075 57 Kashmiri        KETHA
  075 61 Lahnda          KIWE
  075 56 Singhalese      KOHOMADA
  075 95 ALBANIAN        KJYSH, SI
  075 82 Albanian G      KJYSH, SI
  075 84 Albanian C      SI
  075 83 Albanian K      SI
  075 80 Albanian T      SI
  075 81 Albanian Top    SI
  075 59 Gujarati        KEM
  075 63 Bengali         KEMON
  075 69 Greek D         POS
  075 67 Greek MD        POS
  075 70 Greek K         POS
  075 66 Greek ML        POS
  075 68 Greek Mod       POS
  075 05 Breton List     PENAOS, PENOS
  075 06 Breton SE       PENAOS
  075 07 Breton ST       PENAOS
  075 73 Ossetic         KUYD
  075 11 Ladin           QUANT
  075 23 Catalan         COM, QUANT
  075 18 Sardinian L     COMENTE
  075 17 Sardinian N     KOMENTE
  075 19 Sardinian C     KOMMENTI
  075 10 Italian         COME
  075 20 Spanish         COMO
  075 21 Portuguese ST   COMO
  075 22 Brazilian       COMO
  075 13 French          COMMENT
  075 14 Walloon         KIMINT
  075 16 French Creole D KUMA
  075 12 Provencal       COUME
  075 15 French Creole C KUMA
  075 08 Rumanian List   CUM
  075 09 Vlach           KU
  075 02 Irish B         COINNUS
  075 01 Irish A         CONAS
  075 24 German ST       WIE
  075 25 Penn. Dutch     WIE
b                      201
c                         200  3  201
c                         201  3  202
c                         201  3  203
c                         201  3  204
c                         201  3  205
  075 48 Ukrainian       JAK, JAKYM ROBOM
  075 49 Byelorussian    JAK
  075 47 Czech E         YAK
  075 87 BYELORUSSIAN P  JAK
  075 45 Czech           JAK
  075 90 CZECH P         JAK
  075 50 Polish          JAK
  075 86 UKRAINIAN P     JAK
  075 88 POLISH P        JAK
  075 46 Slovak          AKO, JAKO
  075 89 SLOVAK P        AKO
b                      202
c                         200  3  202
c                         201  3  202
c                         202  3  203
c                         202  3  204
c                         202  3  205
  075 74 Afghan          CENGA
  075 78 Baluchi         CHACCHO, CHON, CHO
  075 75 Waziri          TSANGRA
  075 79 Wakhi           TSERUNG
b                      203
c                         200  3  203
c                         201  3  203
c                         202  3  203
c                         203  3  204
c                         203  3  205
  075 55 Gypsy Gk        SAR
b                      204
c                         200  3  204
c                         201  3  204
c                         202  3  204
c                         203  3  204
c                         204  3  205
  075 71 Armenian Mod    INC`PES
  075 72 Armenian List   INCHBES
b                      205
c                         200  3  205
c                         201  3  205
c                         202  3  205
c                         203  3  205
c                         204  3  205
  075 77 Tadzik          CI TAVR, CI XEL
  075 76 Persian List    CHETOWR
a 076 TO HUNT (GAME)
b                      000
  076 55 Gypsy Gk
  076 09 Vlach
  076 79 Wakhi
  076 65 Khaskura
b                      001
  076 08 Rumanian List   A VINA
  076 56 Singhalese      DADAYAM/KARANAWA
  076 06 Breton SE       JIBOESEIN
  076 73 Ossetic         CUAN KAENYN, MOJ, LAEG
  076 25 Penn. Dutch     HUUNT
  076 83 Albanian K      KINIJISIN
b                      002
  076 41 Latvian         MEDIT
  076 40 Lithuanian ST   MEDZIOTI
  076 39 Lithuanian O    MEDZIOTI
b                      003
  076 18 Sardinian L     CAZZARE
  076 17 Sardinian N     KATHTHARE
  076 15 French Creole C SASE, ALE LASAS
  076 11 Ladin           CHATSCHER
  076 19 Sardinian C     KASSAI
  076 10 Italian         ANDARE A CACCIA
  076 23 Catalan         CASSAR, PERSEQUIR LA CASSA
  076 20 Spanish         CAZAR
  076 12 Provencal       CASSA
  076 05 Breton List     KAS KUIT
  076 14 Walloon         TCHESSI
  076 07 Breton ST       CHASEAL
  076 16 French Creole D SASE
  076 13 French          CHASSER
  076 21 Portuguese ST   CACAR
  076 22 Brazilian       CACAR
b                      004
  076 57 Kashmiri        SHIKAR KARUN
  076 64 Nepali List     SIKAR KHELNU, LAGARNU
  076 61 Lahnda          SIKAR KHEDEN
  076 78 Baluchi         SHIKAR KHANAGH-A PHA (HUNTING GAME)
  076 74 Afghan          SKAR KAVEL
  076 77 Tadzik          SIKOR KARDAN, SAJD KARDAN
  076 59 Gujarati        SIKAR KERWO
  076 76 Persian List    SHEKAR KARDAN
  076 58 Marathi         SIKAR+KERNE.
  076 63 Bengali         SIKAR+KORA
  076 62 Hindi           SIKAR + KERNA
  076 60 Panjabi ST      SEKAR+KERNA
  076 75 Waziri          SHKORZAN (HUNTER)
b                      005
  076 48 Ukrainian       POLJUVATY
  076 86 UKRAINIAN P     POL UVATY
  076 88 POLISH P        POLOWAC
  076 50 Polish          POLOWAC
  076 49 Byelorussian    NALJARAC'
  076 87 BYELORUSSIAN P  PAL AVAC
  076 43 Lusatian L      LOJS
  076 44 Lusatian U      LOJIC
  076 91 SLOVENIAN P     LOVITI
  076 89 SLOVAK P        LOVIT
  076 92 SERBOCROATIAN P LOVITI
  076 54 Serbocroatian   LOVITI
  076 93 MACEDONIAN P    LOVAM
  076 90 CZECH P         LOVITI
  076 45 Czech           LOVITI
  076 94 BULGARIAN P     LOVUVAM
  076 53 Bulgarian       DA XODIS NA LOV
  076 52 Macedonian      LOV
b                      006
  076 71 Armenian Mod    ORSAL
  076 72 Armenian List   VORSAL
b                      007
  076 32 Swedish List    JAGA
  076 30 Swedish Up      JAGA
  076 31 Swedish VL      JAGA  JAGA
  076 42 Slovenian       JAGAT
  076 24 German ST       JAGEN
  076 34 Riksmal         GA PA JAKT
  076 33 Danish          JAGE
  076 29 Frisian         JEIJE
  076 28 Flemish         JAGEN
  076 26 Dutch List      JAGEN
  076 27 Afrikaans       JAG, JA (AG), JAE
b                      008
  076 51 Russian         OXOTIT SJA
  076 85 RUSSIAN P       OCHOTIT S A
b                      009
  076 35 Icelandic ST    VEIOA
  076 36 Faroese         VEIDA (VEIDA)
b                      010
  076 37 English ST      TO HUNT
  076 38 Takitaki        HONTI
b                      011
  076 46 Slovak          HONIT
  076 47 Czech E         IT NA HON, HONYIT
b                      012
  076 67 Greek MD        KUNEGO
  076 69 Greek D         KUNEGAO
  076 68 Greek Mod       KINIGHO, PAO
  076 66 Greek ML        KUNEGO
  076 70 Greek K         KUNEGO
b                      200
c                         200  2  201
  076 02 Irish B         DUL AG FLADHACH
b                      201
c                         200  2  201
c                         201  2  202
  076 01 Irish A         SEILG, FIADHACH
b                      202
c                         201  2  202
  076 04 Welsh C         HELA
  076 03 Welsh N         HELA
b                      203
c                         203  2  204
  076 80 Albanian T      ME GJUAJTUR
  076 82 Albanian G      GJUJ
  076 95 ALBANIAN        GJUJ, GJUJTE
b                      204
c                         203  2  204
c                         204  2  205
  076 81 Albanian Top    VETE PER GA, GUAN
b                      205
c                         204  2  205
  076 84 Albanian C      VETE AKACA
a 077 HUSBAND
b                      000
  077 73 Ossetic
  077 34 Riksmal
  077 29 Frisian
b                      001
  077 31 Swedish VL      GOBA
  077 61 Lahnda          GEBHRU
  077 70 Greek K         SUDZUGOS
  077 49 Byelorussian    SUZENEC
  077 32 Swedish List    HUSHALLA
  077 58 Marathi         NEVRA
  077 37 English ST      HUSBAND
  077 05 Breton List     OZAC'H, PRIED
b                      002
  077 07 Breton ST       GWAZ
  077 06 Breton SE       GOAS
b                      003
  077 67 Greek MD        ANTRAS
  077 69 Greek D         ANTRAS
  077 68 Greek Mod       ANDRAS
  077 66 Greek ML        ANTRAS
b                      004
  077 71 Armenian Mod    AMUSIN
  077 72 Armenian List   AMOUSIN
b                      005
  077 09 Vlach           BERBATU
  077 08 Rumanian List   SOT, BARBAT
b                      006
  077 74 Afghan          MERE
  077 75 Waziri          CHESHTAN, MERE
b                      007
  077 79 Wakhi           SAUHER
  077 77 Tadzik          SAVXAR, SUJ
  077 76 Persian List    SHOWHAR
b                      008
  077 45 Czech           MANZEL
  077 46 Slovak          MANZEL
b                      009
  077 56 Singhalese      PURUSAYA, SWAMIYA
  077 63 Bengali         SAMI
b                      010
  077 65 Khaskura        LOGNIA
  077 64 Nepali List     POI, LOGNE, PURUKH
b                      100
  077 55 Gypsy Gk        ROM
  077 57 Kashmiri        RUNU, BARTA
b                      200
c                         200  2  201
  077 22 Brazilian       MARIDO
  077 21 Portuguese ST   MARIDO, ESPOSO
  077 10 Italian         MARITO, SPOSO
  077 17 Sardinian N     MARITU
  077 18 Sardinian L     MARIDU
  077 19 Sardinian C     MARIRU
  077 20 Spanish         MARIDO, ESPOSO
  077 16 French Creole D MAWI
  077 15 French Creole C MAHWI
  077 13 French          MARI
  077 11 Ladin           MARID
  077 78 Baluchi         MARD
b                      201
c                         200  2  201
c                         201  2  202
  077 23 Catalan         MARIT, HOME, ESPOS
  077 12 Provencal       MARIT, OME
b                      202
c                         201  2  202
  077 14 Walloon         OME
b                      203
c                         203  2  204
  077 01 Irish A         FEAR
  077 02 Irish B         FEAN POSTA
  077 41 Latvian         VIRS
  077 39 Lithuanian O    VYRAS
  077 40 Lithuanian ST   VYRAS
  077 04 Welsh C         GWR
  077 03 Welsh N         GWR
b                      204
c                         203  2  204
c                         204  2  205
  077 59 Gujarati        PATI, WER
b                      205
c                         204  2  205
  077 60 Panjabi ST      PETI
  077 62 Hindi           PETI
b                      206
c                         206  2  207
c                         206  2  209
  077 89 SLOVAK P        MUZ
  077 91 SLOVENIAN P     MOZ
  077 86 UKRAINIAN P     MUZ
  077 54 Serbocroatian   MUZ
  077 92 SERBOCROATIAN P MUZ
  077 85 RUSSIAN P       MUZ
  077 51 Russian         MUZ
  077 44 Lusatian U      MUZ
  077 43 Lusatian L      MUZ
  077 90 CZECH P         MUZ
  077 94 BULGARIAN P     MUZ
  077 87 BYELORUSSIAN P  MUZ
  077 47 Czech E         MUZ
  077 48 Ukrainian       MUZ, COLOVIK
  077 88 POLISH P        MAZ
  077 50 Polish          MAZ
  077 93 MACEDONIAN P    MAZ
  077 42 Slovenian       MAS
  077 35 Icelandic ST    MADUR EIGINMADUR
  077 36 Faroese         MADUR
  077 25 Penn. Dutch     MAAN
  077 38 Takitaki        MAN
  077 33 Danish          MAND
  077 30 Swedish Up      (AKTA) MAN
  077 24 German ST       EHEMANN, GATTE
b                      207
c                         206  2  207
c                         207  2  208
c                         207  2  209
  077 52 Macedonian      MAZ, SUPRUG
b                      208
c                         207  2  208
  077 53 Bulgarian       SEPRUG
b                      209
c                         206  2  209
c                         207  2  209
c                         209  2  210
  077 28 Flemish         ECHTGENOOT, MAN
  077 27 Afrikaans       MAN, EGGENOOT
b                      210
c                         209  2  210
  077 26 Dutch List      ECHTGENOOT
b                      211
c                         211  2  212
  077 81 Albanian Top    BURE
  077 83 Albanian K      BURE (MAN)
b                      212
c                         211  2  212
c                         212  2  213
  077 80 Albanian T      BURRE, SHOG
b                      213
c                         212  2  213
  077 95 ALBANIAN        I SHOKJ
  077 84 Albanian C      I-SOK
  077 82 Albanian G      I SHOKJ
a 078 I
b                      000
  078 73 Ossetic
b                      200
c                         200  3  201
c                         200  3  202
  078 94 BULGARIAN P     AZ
  078 41 Latvian         ES
  078 39 Lithuanian O    AS
  078 40 Lithuanian ST   AS
  078 53 Bulgarian       AZ
  078 86 UKRAINIAN P     JA
  078 91 SLOVENIAN P     JA
  078 54 Serbocroatian   JA
  078 92 SERBOCROATIAN P JA
  078 46 Slovak          JA
  078 89 SLOVAK P        JA
  078 85 RUSSIAN P       JA
  078 51 Russian         JA
  078 88 POLISH P        JA
  078 50 Polish          JA
  078 44 Lusatian U      JA
  078 43 Lusatian L      JA
  078 90 CZECH P         JA
  078 45 Czech           JA
  078 87 BYELORUSSIAN P  JA
  078 47 Czech E         YA
  078 49 Byelorussian    JA
  078 48 Ukrainian       JA
  078 78 Baluchi         MAN
  078 77 Tadzik          MAN
  078 76 Persian List    MAN
  078 17 Sardinian N     JEO
  078 42 Slovenian       JEST
  078 93 MACEDONIAN P    JAS
  078 14 Walloon         DJI
  078 13 French          JE
  078 52 Macedonian      JAS
  078 71 Armenian Mod    ES
  078 72 Armenian List   YES
  078 56 Singhalese      MAMA
  078 63 Bengali         AMI
  078 64 Nepali List     MA
  078 61 Lahnda          MAE
  078 58 Marathi         MI
  078 62 Hindi           ME
  078 60 Panjabi ST      ME
  078 65 Khaskura        M
  078 08 Rumanian List   EU
  078 11 Ladin           EAU
  078 19 Sardinian C     DEU
  078 10 Italian         IO
  078 23 Catalan         JO
  078 20 Spanish         YO
  078 12 Provencal       IEU
  078 21 Portuguese ST   EU
  078 22 Brazilian       EU
  078 02 Irish B         ME
  078 01 Irish A         ME
  078 05 Breton List     ME
  078 06 Breton SE       ME
  078 07 Breton ST       ME
  078 38 Takitaki        MI
  078 55 Gypsy Gk        ME
  078 15 French Creole C MWE
  078 16 French Creole D MWE
  078 31 Swedish VL      JAG, JA  JAG, JA
  078 30 Swedish Up      JAG
  078 09 Vlach           EO
  078 18 Sardinian L     EGO
  078 67 Greek MD        EGO, MOU
  078 69 Greek D         EGO
  078 70 Greek K         EGO
  078 66 Greek ML        EGO
  078 68 Greek Mod       EGHO
  078 24 German ST       ICH
  078 35 Icelandic ST    EG
  078 34 Riksmal         JEG
  078 32 Swedish List    JAG
  078 33 Danish          JEG
  078 36 Faroese         EG
  078 29 Frisian         IK, IKKE
  078 28 Flemish         IK
  078 25 Penn. Dutch     ICH
  078 26 Dutch List      IK
  078 27 Afrikaans       EK, EKKE
  078 37 English ST      I
  078 74 Afghan          ZE
  078 75 Waziri          ZE
  078 59 Gujarati        HU
  078 81 Albanian Top    UNE
  078 80 Albanian T      UNE
  078 83 Albanian K      U
  078 84 Albanian C      U
  078 82 Albanian G      UN
  078 95 ALBANIAN        UN
  078 79 Wakhi           WUZ
b                      201
c                         200  3  201
c                         201  3  202
  078 03 Welsh N         I, FI
  078 04 Welsh C         FI
b                      202
c                         200  3  202
c                         201  3  202
  078 57 Kashmiri        BOH
a 079 ICE
b                      000
  079 73 Ossetic
b                      001
  079 17 Sardinian N     ASTRAGU
  079 55 Gypsy Gk        BUZO
  079 84 Albanian C      GAC
  079 81 Albanian Top    KALKAN
  079 75 Waziri          KARANG
  079 83 Albanian K      PAGHO
b                      002
  079 74 Afghan          JAX
  079 77 Tadzik          JAX
  079 76 Persian List    YAKH
b                      003
  079 03 Welsh N         RHEW, IA
  079 04 Welsh C         IA, RHEW
  079 01 Irish A         LEAC OIDHRE
  079 02 Irish B         LEAC OIDHRE
b                      004
  079 07 Breton ST       SKORN
  079 06 Breton SE       SKORN
  079 05 Breton List     SKOURN, SKORN
b                      005
  079 37 English ST      ICE
  079 30 Swedish Up      IS
  079 31 Swedish VL      IS
  079 24 German ST       EIS
  079 35 Icelandic ST    IS
  079 34 Riksmal         IS
  079 32 Swedish List    IS
  079 33 Danish          IS
  079 36 Faroese         ISUR
  079 29 Frisian         IIS
  079 28 Flemish         YS
  079 25 Penn. Dutch     ICE
  079 26 Dutch List      IJS
  079 27 Afrikaans       YS
  079 38 Takitaki        YSI
b                      006
  079 69 Greek D         PAGOS
  079 67 Greek MD        PAGOS
  079 70 Greek K         PAGOS
  079 66 Greek ML        PAGOS
  079 68 Greek Mod       PAGHOS
b                      007
  079 65 Khaskura        HIUN
  079 56 Singhalese      HIMA
  079 64 Nepali List     HIU
b                      008
  079 80 Albanian T      AKULL
  079 82 Albanian G      AKULLI
  079 95 ALBANIAN        AKULLI
b                      009
  079 71 Armenian Mod    SAROYC`
  079 72 Armenian List   SAR
b                      100
  079 79 Wakhi           YUZ
  079 57 Kashmiri        SHUH
b                      200
c                         200  3  201
  079 13 French          GLACE
  079 15 French Creole C LAGLAS
  079 14 Walloon         GLECE
  079 16 French Creole D LAGLAS
  079 10 Italian         GHIACCIO
  079 08 Rumanian List   GHEATA
  079 19 Sardinian C     GIACCU
  079 09 Vlach           GLECU
  079 11 Ladin           GLATSCH
  079 23 Catalan         GEL, GLAS
  079 12 Provencal       GLACO, GEU
  079 21 Portuguese ST   GELO
  079 22 Brazilian       GELO
  079 20 Spanish         HIELO
b                      201
c                         200  3  201
  079 18 Sardinian L     BIDDIA
b                      202
c                         202  3  203
  079 59 Gujarati        BEREF
  079 58 Marathi         BERPHE
  079 63 Bengali         BOROP
  079 62 Hindi           BERPH
  079 60 Panjabi ST      BEREPH
  079 61 Lahnda          BERF, BERREF
b                      203
c                         202  3  203
  079 78 Baluchi         BAWAR
b                      204
c                         204  2  205
  079 86 UKRAINIAN P     LID
  079 91 SLOVENIAN P     LED
  079 42 Slovenian       LETT
  079 89 SLOVAK P        L AD
  079 46 Slovak          L AD
  079 92 SERBOCROATIAN P LED
  079 54 Serbocroatian   LED
  079 85 RUSSIAN P       L OD
  079 51 Russian         LED
  079 88 POLISH P        LOD
  079 50 Polish          LOD
  079 44 Lusatian U      LOD
  079 43 Lusatian L      LOD
  079 90 CZECH P         LED
  079 45 Czech           LED
  079 87 BYELORUSSIAN P  L OD
  079 94 BULGARIAN P     LED
  079 41 Latvian         LEDUS
  079 39 Lithuanian O    LEDAS
  079 40 Lithuanian ST   LEDAS
  079 47 Czech E         LET
  079 49 Byelorussian    LED
  079 48 Ukrainian       LID
  079 53 Bulgarian       LED
b                      205
c                         204  2  205
c                         205  2  206
  079 52 Macedonian      MRAZ, LED
b                      206
c                         205  2  206
  079 93 MACEDONIAN P    MRAZ
a 080 IF
b                      000
  080 28 Flemish
  080 71 Armenian Mod
b                      001
  080 65 Khaskura        BHANEDEKHIN
  080 42 Slovenian       CEBIBLO
  080 08 Rumanian List   DACA
  080 09 Vlach           KA
  080 80 Albanian T      ME GOFTI SE
  080 72 Armenian List   YETE
b                      002
  080 89 SLOVAK P        JESTLI
  080 50 Polish          JESLI
  080 88 POLISH P        JESLI
  080 51 Russian         ESLI
  080 85 RUSSIAN P       JESLI
  080 45 Czech           JESTLI
  080 90 CZECH P         JESTLI
  080 43 Lusatian L      JOLI AZ
  080 44 Lusatian U      JELI-ZO
b                      003
  080 17 Sardinian N     SI
  080 18 Sardinian L     SI
  080 15 French Creole C SI
  080 13 French          SI
  080 16 French Creole D SI
  080 14 Walloon         SI
  080 12 Provencal       SE
  080 20 Spanish         SI
  080 23 Catalan         SI
  080 10 Italian         SE
  080 19 Sardinian C     SI
  080 11 Ladin           SCHA
  080 22 Brazilian       SE
  080 21 Portuguese ST   SE
b                      004
  080 82 Albanian G      NE
  080 84 Albanian C      NA
  080 95 ALBANIAN        NE
b                      005
  080 01 Irish A         MA
  080 02 Irish B         MA, DA
  080 07 Breton ST       MA, MAZ, MAR
  080 06 Breton SE       MAR
  080 05 Breton List     MA, MAR
b                      006
  080 68 Greek Mod       AN, AM, A
  080 66 Greek ML        AN
  080 70 Greek K         AN
  080 67 Greek MD        AN
  080 69 Greek D         AN
b                      007
  080 37 English ST      IF
  080 38 Takitaki        EFI
  080 35 Icelandic ST    EF
  080 29 Frisian         OF
b                      008
  080 24 German ST       WENN
  080 25 Penn. Dutch     WONN
b                      009
  080 81 Albanian Top    PO
  080 83 Albanian K      PO
b                      010
  080 77 Tadzik          AGAR
  080 76 Persian List    AGAR
  080 78 Baluchi         AR, AR KI
  080 79 Wakhi           UGER
b                      100
  080 56 Singhalese      TOT
  080 55 Gypsy Gk        TE
b                      200
c                         200  2  201
  080 34 Riksmal         HVIS
  080 33 Danish          HVIS
b                      201
c                         200  2  201
c                         201  2  202
  080 36 Faroese         UM, VISS
b                      202
c                         201  2  202
  080 30 Swedish Up      OM, I FALL (ATT)
  080 31 Swedish VL      OM  OM
  080 32 Swedish List    OM, IFALL, SA/VRAMT
b                      203
c                         203  2  204
c                         203  2  206
  080 91 SLOVENIAN P     AKO
  080 54 Serbocroatian   AKO
  080 92 SERBOCROATIAN P AKO
  080 93 MACEDONIAN P    AKO
  080 94 BULGARIAN P     AKO
  080 52 Macedonian      AKO
  080 53 Bulgarian       AKO
b                      204
c                         203  2  204
c                         204  2  205
c                         204  2  206
c                         204  3  207
c                         204  2  208
c                         204  3  210
  080 46 Slovak          KED , KEBY, AK
b                      205
c                         204  2  205
c                         205  3  206
c                         205  3  207
c                         205  3  208
c                         205  3  210
  080 47 Czech E         KEBI
b                      206
c                         203  2  206
c                         204  2  206
c                         205  3  206
c                         206  2  207
c                         206  3  208
c                         206  3  210
  080 48 Ukrainian       JAKSCO, KOLY, JAK, JAKBY
b                      207
c                         204  3  207
c                         205  3  207
c                         206  2  207
c                         207  3  210
  080 86 UKRAINIAN P     KOLY
  080 87 BYELORUSSIAN P  KALI
  080 49 Byelorussian    KALI
b                      208
c                         204  2  208
c                         205  3  208
c                         206  3  208
c                         208  2  209
c                         208  3  210
  080 40 Lithuanian ST   JEI, JEIGU, KAD
b                      209
c                         208  2  209
  080 63 Bengali         JODI
  080 61 Lahnda          JE
  080 64 Nepali List     JADI
  080 57 Kashmiri        YED, AY
  080 59 Gujarati        JO
  080 58 Marathi         JER
  080 60 Panjabi ST      EGER, JE
  080 62 Hindi           EGER, YEDI
  080 39 Lithuanian O    JEI, JEIGU
  080 41 Latvian         JA
b                      210
c                         204  3  210
c                         205  3  210
c                         206  3  210
c                         207  3  210
c                         208  3  210
  080 74 Afghan          KA
  080 75 Waziri          CHE, KE
  080 73 Ossetic         KAED, KUY
b                      211
c                         211  3  212
  080 04 Welsh C         OS
  080 03 Welsh N         OS
b                      212
c                         211  3  212
c                         212  2  213
  080 27 Afrikaans       AS, INDIEN
b                      213
c                         212  2  213
  080 26 Dutch List      INDIEN
a 081 IN
b                      000
  081 41 Latvian
  081 79 Wakhi
b                      001
  081 76 Persian List    DAR
  081 56 Singhalese      HI ATULA
  081 09 Vlach           NEUNDRE
  081 78 Baluchi         NIANWAN, LAFA, SARA
  081 23 Catalan         SOBRE, AB, DE
  081 84 Albanian C      TE
b                      200
c                         200  2  201
c                         200  2  203
  081 14 Walloon         DIVINS
  081 10 Italian         DENTRO
  081 28 Flemish         IN, BY, OP
  081 26 Dutch List      IN, NAAR, BIJ, VAN, OP
  081 29 Frisian         BINNEN
  081 12 Provencal       DINS, DEDINS, EN
  081 13 French          DANS
  081 24 German ST       IN
  081 36 Faroese         I
  081 33 Danish          I
  081 34 Riksmal         I
  081 35 Icelandic ST    I
  081 07 Breton ST       E, EN
  081 06 Breton SE       E, EN
  081 05 Breton List     E, EN
  081 04 Welsh C         YN
  081 03 Welsh N         YN
  081 01 Irish A         I
  081 30 Swedish Up      I
  081 31 Swedish VL      INI, I
  081 17 Sardinian N     IN
  081 18 Sardinian L     IN
  081 15 French Creole C A
  081 19 Sardinian C     IN
  081 11 Ladin           IN
  081 08 Rumanian List   IN
  081 20 Spanish         EN
  081 16 French Creole D A
  081 21 Portuguese ST   EM
  081 22 Brazilian       EM, NA
  081 38 Takitaki        NA IM
  081 27 Afrikaans       IN
  081 25 Penn. Dutch     IM, IN
  081 37 English ST      IN
  081 48 Ukrainian       V, NA, U
  081 91 SLOVENIAN P     V
  081 86 UKRAINIAN P     V
  081 94 BULGARIAN P     V
  081 87 BYELORUSSIAN P  VA
  081 45 Czech           V
  081 90 CZECH P         V
  081 43 Lusatian L      W
  081 44 Lusatian U      W
  081 93 MACEDONIAN P    V
  081 50 Polish          W
  081 88 POLISH P        W
  081 51 Russian         V
  081 85 RUSSIAN P       V
  081 54 Serbocroatian   U
  081 92 SERBOCROATIAN P U
  081 46 Slovak          V, VO
  081 89 SLOVAK P        V
  081 52 Macedonian      V, VO
  081 47 Czech E         V, VE
  081 49 Byelorussian    U
  081 53 Bulgarian       V, VEV
  081 40 Lithuanian ST   I
  081 39 Lithuanian O    I
  081 32 Swedish List    I, UTI, PA
  081 02 Irish B         I, IN, SA, ANN, SAN
  081 61 Lahnda          ENDER
  081 63 Bengali         ONDOR
  081 60 Panjabi ST      ENDER
  081 55 Gypsy Gk        ANDRE
  081 68 Greek Mod       SE, S
  081 70 Greek K         EIS
  081 42 Slovenian       NOTRI
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
  081 62 Hindi           ENDER, -ME
b                      202
c                         201  2  202
  081 64 Nepali List     MA
  081 57 Kashmiri        MANZ
  081 58 Marathi         AT, -MEDHE
  081 65 Khaskura        MA
  081 73 Ossetic         - (SUFFIX) - MAE, - AEJ
  081 59 Gujarati        MA (ENDER)
  081 71 Armenian Mod    MEJ
  081 72 Armenian List   MECHE
b                      203
c                         200  2  203
c                         201  2  203
c                         203  2  204
  081 67 Greek MD        MESA, SE
  081 69 Greek D         S , MESA
b                      204
c                         203  2  204
  081 66 Greek ML        MESA
b                      205
c                         205  3  206
  081 74 Afghan          PE...KI
  081 75 Waziri          KSHE, PA...KSHE
b                      206
c                         205  3  206
  081 77 Tadzik          BA
b                      207
c                         207  2  208
  081 95 ALBANIAN        NE, ME
  081 82 Albanian G      ME, NE
  081 83 Albanian K      NDE, MENDA
b                      208
c                         207  2  208
c                         208  2  209
  081 80 Albanian T      NE, BRENDA
b                      209
c                         208  2  209
  081 81 Albanian Top    BRENDA
a 082 TO KILL
b                      000
  082 65 Khaskura
  082 25 Penn. Dutch
b                      001
  082 70 Greek K         FONEUO
  082 02 Irish B         DO MHASBHADH
  082 55 Gypsy Gk        MUNDARAV  MUTARAV
  082 23 Catalan         NAFRAR
  082 41 Latvian         NOGALINAT, NONAVET
  082 79 Wakhi           SAEI-
  082 09 Vlach           VATEMU
b                      002
  082 05 Breton List     LAZA
  082 07 Breton ST       LAZHAN
  082 06 Breton SE       LAHEIN
  082 04 Welsh C         LLADD
  082 03 Welsh N         LLADD
b                      003
  082 71 Armenian Mod    SPANEL
  082 72 Armenian List   SBANNELL
b                      004
  082 40 Lithuanian ST   UZMUSTI
  082 39 Lithuanian O    UZMUSTI, NAIKINTI
b                      005
  082 18 Sardinian L     BOCCHIRE
  082 19 Sardinian C     BOCCIRI
b                      006
  082 74 Afghan          VAZEL
  082 75 Waziri          WEZHLEL
b                      007
  082 20 Spanish         MATAR
  082 21 Portuguese ST   MATAR
  082 22 Brazilian       MATAR
b                      008
  082 92 SERBOCROATIAN P UBITI
  082 42 Slovenian       UBIJAT
  082 91 SLOVENIAN P     UBITI
  082 86 UKRAINIAN P     UBYVATI
  082 94 BULGARIAN P     UBIVAM
  082 93 MACEDONIAN P    UBIVAM
  082 51 Russian         UBIVAT
  082 85 RUSSIAN P       UBIT
  082 54 Serbocroatian   UBITI
  082 53 Bulgarian       DA UBIVA
  082 47 Czech E         ZABIT
  082 49 Byelorussian    ZABIVAC'
  082 50 Polish          ZABIJAC
  082 88 POLISH P        ZABIC
  082 87 BYELORUSSIAN P  ZABIC
  082 45 Czech           ZABITI
  082 90 CZECH P         ZABIJETI
  082 43 Lusatian L      ZABIS
  082 44 Lusatian U      ZABIC
  082 46 Slovak          ZABIT
  082 89 SLOVAK P        ZABIT
  082 52 Macedonian      OTEPA, UBIVA
  082 48 Ukrainian       UBYVATY, RIZATY
b                      009
  082 13 French          TUER
  082 12 Provencal       TUA, PERI
  082 15 French Creole C CWE
  082 14 Walloon         TOUWER
  082 16 French Creole D CWE
b                      010
  082 81 Albanian Top    VRAS, AOR. VRAVA
  082 80 Albanian T      ME VRARE
  082 83 Albanian K      VRAS (AOR. VRAVA)
  082 84 Albanian C      VRAS
  082 82 Albanian G      VRAS ( VRA = INF.)
  082 95 ALBANIAN        VRAS
b                      011
  082 37 English ST      TO KILL
  082 38 Takitaki        KILI
b                      012
  082 76 Persian List    KOSHTAN
  082 77 Tadzik          ZADAN, KUFTAN, SAR BURIDAN
  082 78 Baluchi         KHUSHAGH, KHUSHTA
b                      200
c                         200  2  201
c                         200  2  204
  082 57 Kashmiri        MARUN
  082 56 Singhalese      MARANAWA
  082 64 Nepali List     MARNU
  082 61 Lahnda          MAREN
  082 59 Gujarati        MAREWU
  082 58 Marathi         THAR+MARNE.
  082 63 Bengali         MARA
  082 62 Hindi           MARNA
  082 60 Panjabi ST      MARNA
  082 01 Irish A         MARBHUGHADH
  082 73 Ossetic         MARYN
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  2  204
  082 08 Rumanian List   A OMORI, A UCIDE
b                      202
c                         201  2  202
c                         202  2  203
  082 17 Sardinian N     UKKIERE
b                      203
c                         201  2  203
c                         202  2  203
c                         203  2  204
  082 10 Italian         UCCIDELE, AMMAZZARE
b                      204
c                         200  2  204
c                         201  2  204
c                         203  2  204
  082 11 Ladin           MAZZER, MURENTER
b                      205
c                         205  2  206
  082 31 Swedish VL      DRAPA
  082 35 Icelandic ST    DREPA
  082 34 Riksmal         DREPE
  082 36 Faroese         DREPA
  082 33 Danish          DRAEBE
b                      206
c                         205  2  206
c                         206  2  207
c                         206  2  208
c                         206  3  210
  082 32 Swedish List    DODA, DRAPA
b                      207
c                         206  2  207
c                         207  2  208
c                         207  3  210
  082 24 German ST       TOTEN
  082 28 Flemish         DOODEN
  082 27 Afrikaans       DOODMAAK
  082 29 Frisian         DEADZJE, DEIJE
b                      208
c                         206  2  208
c                         207  2  208
c                         208  2  209
c                         208  3  210
  082 26 Dutch List      DOODEN, SLACKTEN
b                      209
c                         208  2  209
  082 30 Swedish Up      SLA IHJAL
b                      210
c                         206  3  210
c                         207  3  210
c                         208  3  210
c                         210  2  211
  082 67 Greek MD        SKOTONO, KSEKANO, THANATONO
b                      211
c                         210  2  211
  082 69 Greek D         SKOTONO
  082 68 Greek Mod       SKOTONO
  082 66 Greek ML        SKOTONO
a 083 KNOW (FACTS)
b                      001
  083 38 Takitaki        SABI
  083 75 Waziri          KHABAR, MOLIM (KNOWN)
  083 74 Afghan          POHEDEL
  083 78 Baluchi         SAHIH BIAGH
  083 23 Catalan         SENTIRSE, SEMBLARSE
b                      002
  083 20 Spanish         SABER
  083 21 Portuguese ST   SABER
  083 22 Brazilian       SABER
  083 10 Italian         SAPERE
  083 13 French          SAVOIR
  083 16 French Creole D SAV
  083 14 Walloon         SAVEUR, SAVU, SEPI
  083 12 Provencal       SABE, SAUPRE
  083 15 French Creole C SAV  SE
  083 11 Ladin           SAVAIR
b                      003
  083 17 Sardinian N     ISKIRE
  083 18 Sardinian L     ISCHIRE
  083 19 Sardinian C     SIRI
  083 08 Rumanian List   A STI
  083 09 Vlach           STIU
b                      200
c                         200  2  201
  083 24 German ST       WISSEN
  083 35 Icelandic ST    VITA
  083 34 Riksmal         VITE
  083 32 Swedish List    VETA
  083 33 Danish          VIDE
  083 36 Faroese         VITA
  083 29 Frisian         WITTEN
  083 28 Flemish         WETEN
  083 25 Penn. Dutch     WAYSS
  083 26 Dutch List      WETEN
  083 27 Afrikaans       WEET
  083 03 Welsh N         GWYBOD
  083 04 Welsh C         GWYBOD
  083 05 Breton List     GOUZOUT, GOUT
  083 06 Breton SE       GOUIEIN
  083 07 Breton ST       GOUZOUT
  083 31 Swedish VL      VETA
  083 47 Czech E         VEDET
  083 49 Byelorussian    VEDAC'
  083 71 Armenian Mod    GITENAL
  083 72 Armenian List   KIDNAL
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
  083 30 Swedish Up      VETA, KANNA (TILL)
  083 46 Slovak          VEDIET, ZNAT
  083 45 Czech           VEDETI, ZNATI
b                      202
c                         201  2  202
c                         202  2  203
  083 55 Gypsy Gk        JANAV
  083 73 Ossetic         ZONYN, FAESMAERUN
  083 56 Singhalese      KARUNU/DANNAWA
  083 57 Kashmiri        ZANUN
  083 64 Nepali List     JANNU
  083 61 Lahnda          JANEN
  083 77 Tadzik          DONISTAN, FAXMIDAN, OGOX BUDAN
  083 59 Gujarati        JANEWU
  083 76 Persian List    DANESTAN
  083 58 Marathi         JANNE.
  083 63 Bengali         JANA
  083 62 Hindi           JANNA
  083 60 Panjabi ST      JANNENA
  083 65 Khaskura        JANNU
  083 37 English ST      KNOW
  083 86 UKRAINIAN P     ZNATY
  083 91 SLOVENIAN P     ZNATI
  083 42 Slovenian       ZNAS
  083 89 SLOVAK P        ZNAT
  083 92 SERBOCROATIAN P ZNATI
  083 54 Serbocroatian   ZNATI
  083 85 RUSSIAN P       ZNAT
  083 51 Russian         ZNAT
  083 88 POLISH P        ZNAC
  083 50 Polish          ZNAC
  083 93 MACEDONIAN P    ZNAM
  083 44 Lusatian U      ZNAC
  083 43 Lusatian L      ZNAS
  083 90 CZECH P         ZNATI
  083 87 BYELORUSSIAN P  ZNAC
  083 94 BULGARIAN P     ZANJA
  083 41 Latvian         ZINAT
  083 39 Lithuanian O    ZINOTI
  083 40 Lithuanian ST   ZINOTI
  083 52 Macedonian      ZNAE
  083 48 Ukrainian       ZNATY
  083 53 Bulgarian       DA ZNAE
  083 01 Irish A         TA A FHIOS AIGE ("ITS KNOWLEDGE IS AT HIM")
  083 02 Irish B         AITHNIGHIM
  083 70 Greek K         GNORIDZO
b                      203
c                         201  2  203
c                         202  2  203
c                         203  2  204
  083 67 Greek MD        KSERO, GNORIDZO
b                      204
c                         203  2  204
  083 69 Greek D         KSERO
  083 66 Greek ML        KSERO
  083 68 Greek Mod       KSERO
b                      205
c                         205  3  206
  083 80 Albanian T      ME DITUR
  083 83 Albanian K      DII
  083 84 Albanian C      DI
  083 82 Albanian G      DI (DIT = INF.)
  083 95 ALBANIAN        DI
  083 81 Albanian Top    DI, AOR. DINE
b                      206
c                         205  3  206
  083 79 Wakhi           DIS-
a 084 LAKE
b                      000
  084 55 Gypsy Gk        LIMNI
  084 09 Vlach           LIMNI
  084 29 Frisian
  084 75 Waziri
b                      001
  084 63 Bengali         BIL
  084 73 Ossetic         CAD
  084 84 Albanian C      LAGHU
  084 37 English ST      LAKE
  084 25 Penn. Dutch     WASSER LOCH
  084 83 Albanian K      LUCE
  084 56 Singhalese      WEWA
  084 79 Wakhi           ZOI
b                      002
  084 53 Bulgarian       EZERO
  084 47 Czech E         YAZERO
  084 52 Macedonian      EZERO
  084 88 POLISH P        JEZIORO
  084 50 Polish          JEZIORO
  084 93 MACEDONIAN P    EZERO
  084 44 Lusatian U      JEZOR
  084 43 Lusatian L      JAZOR
  084 90 CZECH P         JEZERO
  084 45 Czech           JEZERO
  084 94 BULGARIAN P     EZERO
  084 41 Latvian         EZERS
  084 39 Lithuanian O    AZERAS
  084 40 Lithuanian ST   EZERAS
  084 91 SLOVENIAN P     JEZERO
  084 42 Slovenian       JEZERO
  084 89 SLOVAK P        JAZERO
  084 46 Slovak          JAZERO
  084 92 SERBOCROATIAN P JEZERO
  084 54 Serbocroatian   JEZERO
  084 48 Ukrainian       OZERO
  084 49 Byelorussian    VOZERA
  084 87 BYELORUSSIAN P  VOZERA
  084 86 UKRAINIAN P     OZERO
  084 51 Russian         OZERO
  084 85 RUSSIAN P       OZERO
b                      003
  084 35 Icelandic ST    VATN
  084 34 Riksmal         VANN
  084 36 Faroese         VATN
b                      004
  084 24 German ST       SEE
  084 32 Swedish List    SJO, INSJO
  084 38 Takitaki        ZEE
  084 33 Danish          SO
  084 30 Swedish Up      SJO
  084 31 Swedish VL      SO
b                      005
  084 28 Flemish         MEER
  084 26 Dutch List      MEER
  084 27 Afrikaans       MEER, PAN
b                      006
  084 68 Greek Mod       LIMNI
  084 66 Greek ML        LIMNE
  084 70 Greek K         LIMNE
  084 67 Greek MD        LIMNE
  084 69 Greek D         LIMNE
b                      007
  084 16 French Creole D LETA
  084 15 French Creole C LETA
b                      100
  084 57 Kashmiri        SAR, DAL
  084 59 Gujarati        SEROWER
b                      200
c                         200  2  201
c                         200  3  203
c                         200  3  204
  084 13 French          LAC
  084 23 Catalan         ESTANY, BASSA, LLACH
  084 08 Rumanian List   LAC
  084 14 Walloon         LAC
  084 02 Irish B         LOCH
  084 01 Irish A         LOCH
  084 22 Brazilian       LAGO
  084 21 Portuguese ST   LAGO
  084 12 Provencal       LAU, CLAR
  084 20 Spanish         LAGO
  084 10 Italian         LAGO
  084 19 Sardinian C     LAGU
  084 17 Sardinian N     LAGU
  084 18 Sardinian L     LAGU
  084 11 Ladin           LEJ, LEIH
b                      201
c                         200  2  201
c                         201  2  202
c                         201  3  203
c                         201  3  204
  084 05 Breton List     LENN, LOUC'H, LOC'H
b                      202
c                         201  2  202
c                         202  3  203
  084 07 Breton ST       LENN
  084 06 Breton SE       LENN
  084 04 Welsh C         LLYN
  084 03 Welsh N         LLYN
b                      203
c                         200  3  203
c                         201  3  203
c                         202  3  203
c                         203  3  204
  084 71 Armenian Mod    LIC
  084 72 Armenian List   LICH
b                      204
c                         200  3  204
c                         201  3  204
c                         203  3  204
c                         204  2  205
  084 95 ALBANIAN        GJOLLI, LIKJE NI
  084 80 Albanian T      LIGEN, GJOL
b                      205
c                         204  2  205
  084 81 Albanian Top    GOL
  084 82 Albanian G      GJOLLI
b                      206
c                         206  2  207
  084 77 Tadzik          KUL
b                      207
c                         206  2  207
c                         207  2  208
c                         207  2  209
c                         207  2  210
c                         207  2  212
  084 74 Afghan          KUL, GADIR, DZIHIL, DAND, DARJACA
b                      208
c                         207  2  208
  084 78 Baluchi         DHAND, DAND, DAND
b                      209
c                         207  2  209
c                         209  2  210
  084 61 Lahnda          JHIL
  084 62 Hindi           JHIL
  084 60 Panjabi ST      CIL
b                      210
c                         207  2  210
c                         209  2  210
c                         210  2  211
  084 64 Nepali List     JHIL, TAL, POKHARI
b                      211
c                         210  2  211
  084 58 Marathi         TELE.
  084 65 Khaskura        TALAU, TAL
b                      212
c                         207  2  212
  084 76 Persian List    DARYACHE
a 085 TO LAUGH
b                      001
  085 56 Singhalese      HINAWENAWA
  085 72 Armenian List   KHUNTAL
b                      002
  085 03 Welsh N         CHWERTHIN
  085 04 Welsh C         CHWERTHYN
  085 05 Breton List     C'HOARZIN
  085 06 Breton SE       HOARHEIN
  085 07 Breton ST       C'HOARZHIN
b                      003
  085 10 Italian         RIDERE
  085 17 Sardinian N     RIDERE
  085 18 Sardinian L     RIERE
  085 11 Ladin           RIR
  085 19 Sardinian C     ARRIRI
  085 23 Catalan         RIURER, RIURERSEN
  085 20 Spanish         REIR
  085 12 Provencal       RIRE
  085 14 Walloon         RIRE
  085 13 French          RIRE
  085 21 Portuguese ST   RIR
  085 22 Brazilian       RIR
  085 16 French Creole D WI
  085 15 French Creole C HWI
  085 08 Rumanian List   A RIDE
  085 09 Vlach           ARYTU
b                      004
  085 52 Macedonian      NASMEA
  085 41 Latvian         SMIETIES
  085 94 BULGARIAN P     SMEJA SE
  085 46 Slovak          SMIAT SA
  085 89 SLOVAK P        SMIAT SA
  085 42 Slovenian       SMEJAT
  085 91 SLOVENIAN P     SMEJATI SE
  085 86 UKRAINIAN P     SMIJATYS
  085 92 SERBOCROATIAN P SMEJATI SE
  085 54 Serbocroatian   SMIJATI SE
  085 85 RUSSIAN P       SMEJAT S A
  085 51 Russian         SMEJAT SJA
  085 88 POLISH P        SMIAC SIE
  085 50 Polish          SMIAC SIE
  085 93 MACEDONIAN P    SMEAM SE
  085 44 Lusatian U      SMJEC SO
  085 43 Lusatian L      SMJAS SE
  085 90 CZECH P         SMATI SE
  085 45 Czech           SMATI SE
  085 87 BYELORUSSIAN P  SM ACCA
  085 47 Czech E         SMITSA
  085 49 Byelorussian    C'MJAJACCA
  085 48 Ukrainian       SMIJATYC', REHOTATYC'
  085 53 Bulgarian       DA SE SMEE
b                      005
  085 02 Irish B         DO DHEANAMH GAIRE
  085 01 Irish A         GAIRIGHE
b                      006
  085 69 Greek D         GELAO
  085 67 Greek MD        GELO
  085 70 Greek K         GELO
  085 68 Greek Mod       YELO
  085 66 Greek ML        GELO
  085 71 Armenian Mod    CICAL
b                      007
  085 64 Nepali List     HASNU
  085 57 Kashmiri        ASUN
  085 61 Lahnda          HESSEN
  085 59 Gujarati        HESWU
  085 58 Marathi         HESNE.
  085 63 Bengali         HASA
  085 62 Hindi           HESNA
  085 60 Panjabi ST      HESSENA
  085 65 Khaskura        HANSNU
  085 55 Gypsy Gk        ASAV
b                      008
  085 30 Swedish Up      SKRATTA
  085 31 Swedish VL      SKRAT
  085 32 Swedish List    SKRATTA
b                      009
  085 40 Lithuanian ST   JUOKTIS
  085 39 Lithuanian O    JUOKTIS
b                      010
  085 75 Waziri          KHANDEL
  085 79 Wakhi           KUND
  085 78 Baluchi         KHANDAGH, KHANDITHA
  085 74 Afghan          XANDEL
  085 77 Tadzik          XANDIDAN
  085 76 Persian List    KHANDIDAN
  085 73 Ossetic         XUDYN
b                      200
c                         200  3  201
  085 34 Riksmal         LE
  085 33 Danish          LE
  085 28 Flemish         LACHEN
  085 25 Penn. Dutch     LAUCH
  085 26 Dutch List      LACHEN
  085 27 Afrikaans       LAG
  085 38 Takitaki        LAFOE
  085 36 Faroese         LAEA
  085 37 English ST      TO LAUGH
  085 35 Icelandic ST    HLAEJA
  085 24 German ST       LACHEN
  085 29 Frisian         GIIZJE, LAEITSJE, LAITSJE
b                      201
c                         200  3  201
  085 84 Albanian C      KES
  085 81 Albanian Top    KES, AOR. KESA
  085 83 Albanian K      KESIN
  085 82 Albanian G      KJESH
  085 95 ALBANIAN        KJESH
  085 80 Albanian T      ME GESHUR
a 086 LEAF
b                      001
  086 56 Singhalese      KOLAYA
  086 42 Slovenian       PERU
  086 79 Wakhi           PULC
  086 73 Ossetic         SYF
  086 78 Baluchi         THAKH
  086 38 Takitaki        WIWIRI
b                      002
  086 91 SLOVENIAN P     LIST
  086 86 UKRAINIAN P     LYST
  086 94 BULGARIAN P     LIST
  086 87 BYELORUSSIAN P  LIST
  086 45 Czech           LIST
  086 90 CZECH P         LIST
  086 43 Lusatian L      LIST
  086 44 Lusatian U      LIST
  086 93 MACEDONIAN P    LIST
  086 50 Polish          LISC
  086 88 POLISH P        LISC
  086 51 Russian         LIST
  086 85 RUSSIAN P       LIST
  086 54 Serbocroatian   LIST
  086 92 SERBOCROATIAN P LIST
  086 46 Slovak          LIST
  086 89 SLOVAK P        LIST
  086 52 Macedonian      LIST
  086 49 Byelorussian    LIST
  086 47 Czech E         LIST
  086 48 Ukrainian       LYST, ARKUS
  086 53 Bulgarian       LIST
b                      003
  086 77 Tadzik          BARG
  086 76 Persian List    BARG
b                      004
  086 39 Lithuanian O    LAPAS, LAKSTAS
  086 40 Lithuanian ST   LAPAS
  086 41 Latvian         LAPA
b                      005
  086 64 Nepali List     PAT
  086 65 Khaskura        PAT
  086 60 Panjabi ST      PETTA
  086 62 Hindi           PETTA
  086 63 Bengali         PATA
  086 55 Gypsy Gk        PATRIN
  086 61 Lahnda          PETTA
b                      006
  086 72 Armenian List   DEREF
  086 71 Armenian Mod    TEREW
b                      200
c                         200  2  201
c                         200  3  203
c                         200  3  204
c                         200  3  205
  086 21 Portuguese ST   FOLHA
  086 22 Brazilian       FOLHA
  086 13 French          FEUILLE
  086 16 French Creole D FEY
  086 14 Walloon         FOUYE, FOYE
  086 12 Provencal       FUEIO, RAMO
  086 18 Sardinian L     FOZZA
  086 17 Sardinian N     OTHTHA
  086 15 French Creole C FEY
  086 23 Catalan         FULLA
  086 10 Italian         FOGLIO
  086 19 Sardinian C     FOLLA
  086 11 Ladin           FOGLIA
  086 20 Spanish         HOJA
b                      201
c                         200  2  201
c                         201  2  202
c                         201  3  203
  086 08 Rumanian List   FRUNZA, FOAIE
b                      202
c                         201  2  202
  086 09 Vlach           FRYNZE
b                      203
c                         200  3  203
c                         201  3  203
  086 07 Breton ST       DELIENN
  086 06 Breton SE       DELEN
  086 05 Breton List     DEIL
  086 04 Welsh C         DALEN
  086 03 Welsh N         DEILEN
  086 01 Irish A         DUILLEOG
  086 02 Irish B         DUILLE
b                      204
c                         200  3  204
c                         204  2  205
  086 24 German ST       BLATT
  086 34 Riksmal         BLAD
  086 36 Faroese         (LEYF)BLAD
  086 30 Swedish Up      BLAD
  086 27 Afrikaans       BLAD, BLAAR
  086 26 Dutch List      BLAD
  086 25 Penn. Dutch     BLOT
  086 28 Flemish         BLAD
  086 29 Frisian         BLED
  086 68 Greek Mod       FILO
  086 66 Greek ML        FULLO
  086 70 Greek K         FULLON
  086 67 Greek MD        FULLO
  086 69 Greek D         FULLO
b                      205
c                         200  3  205
c                         204  2  205
c                         205  2  206
  086 32 Swedish List    LOV, BLAD
  086 35 Icelandic ST    LAUFBLAO
  086 31 Swedish VL      BLA, LOVBLA
b                      206
c                         205  2  206
  086 37 English ST      LEAF
  086 33 Danish          LOV
b                      207
c                         207  3  208
  086 57 Kashmiri        PAN
  086 74 Afghan          PANA
  086 58 Marathi         PAN
  086 59 Gujarati        PAN, PANDERU
b                      208
c                         207  3  208
  086 75 Waziri          PONRYE
b                      209
c                         209  2  210
  086 81 Albanian Top    FLETE
  086 84 Albanian C      FLET
  086 83 Albanian K      FLETE
  086 80 Albanian T      FLETE
b                      210
c                         209  2  210
c                         210  2  211
  086 82 Albanian G      FLETA, GJETHI
b                      211
c                         210  2  211
  086 95 ALBANIAN        GJETHI
a 087 LEFT (HAND)
b                      001
  087 84 Albanian C      E-STREMBRA
  087 73 Ossetic         GALAU
  087 18 Sardinian L     INFAUSTU
  087 41 Latvian         KREISAIS
  087 38 Takitaki        KROEKOETOE
  087 37 English ST      LEFT (HAND)
  087 55 Gypsy Gk        NASUL
  087 83 Albanian K      ZERVIST
b                      002
  087 79 Wakhi           CUP
  087 78 Baluchi         CHAP
  087 77 Tadzik          CAP
  087 76 Persian List    CHAP
b                      003
  087 75 Waziri          KINR
  087 74 Afghan          KIN
b                      004
  087 30 Swedish Up      VANSTER
  087 31 Swedish VL      VINSTAR  VANSTAR
  087 35 Icelandic ST    VINSTRI
  087 34 Riksmal         VENSTRE
  087 32 Swedish List    VANSTER
  087 36 Faroese         VINSTRI
  087 33 Danish          VENSTRE
b                      005
  087 01 Irish A         CLE
  087 02 Irish B         CLI, CLE
  087 05 Breton List     KLEIZ
  087 06 Breton SE       KLEI
  087 07 Breton ST       KLEIZ
b                      006
  087 24 German ST       LINK
  087 29 Frisian         LINKS
  087 28 Flemish         LINKSCH
  087 25 Penn. Dutch     LINGSS
  087 26 Dutch List      LINKS
  087 27 Afrikaans       LINKS, HOT
b                      007
  087 59 Gujarati        DABU
  087 58 Marathi         DAVA
  087 65 Khaskura        DEBRO
  087 64 Nepali List     DEBRE
b                      008
  087 15 French Creole C GOS
  087 13 French          GAUCHE
  087 16 French Creole D GOS
  087 14 Walloon         GOCHE
  087 12 Provencal       GAUCHE, AUCHO
b                      009
  087 53 Bulgarian       LJAVO
  087 94 BULGARIAN P     L AV
  087 89 SLOVAK P        L AVY
  087 46 Slovak          L AVY
  087 87 BYELORUSSIAN P  LEVY
  087 45 Czech           LEVY
  087 90 CZECH P         LEVY
  087 43 Lusatian L      LEWY
  087 44 Lusatian U      LEWY
  087 93 MACEDONIAN P    LEV
  087 50 Polish          LEWY
  087 88 POLISH P        LEWY
  087 52 Macedonian      LEV
  087 47 Czech E         LEVO
  087 49 Byelorussian    LEVY
  087 48 Ukrainian       LIVYJ, -A - E
  087 86 UKRAINIAN P     LIVYJ
  087 91 SLOVENIAN P     LEV
  087 42 Slovenian       LEVIC, LEVA RAKA
  087 92 SERBOCROATIAN P LEV
  087 54 Serbocroatian   LJEVICA
  087 85 RUSSIAN P       LEVYJ
  087 51 Russian         LEVYJ
b                      010
  087 08 Rumanian List   STING
  087 09 Vlach           ASTEGU
b                      011
  087 17 Sardinian N     MANKA
  087 19 Sardinian C     MANKA
b                      012
  087 81 Albanian Top    MENGER
  087 80 Albanian T      I, E MENGJER
b                      013
  087 66 Greek ML        ARISTEROS
  087 70 Greek K         ARISTERA
  087 69 Greek D         ARISTERO
  087 67 Greek MD        ARISTEROS, DZERBOS
  087 68 Greek Mod       ZERVOS, ARISTERA (TO THE LEFT)
b                      014
  087 71 Armenian Mod    JAX
  087 72 Armenian List   ZAGH (ZARK)
b                      015
  087 40 Lithuanian ST   KAIRYS
  087 39 Lithuanian O    KAIRINIS
  087 04 Welsh C         CHWITH
  087 03 Welsh N         CHWITH, ASWY
b                      016
  087 82 Albanian G      MAJT
  087 95 ALBANIAN        MAJT
b                      017
  087 60 Panjabi ST      KHEBBA
  087 61 Lahnda          KHEBBA
  087 57 Kashmiri        KHOWORU
b                      200
c                         200  2  201
  087 10 Italian         SINISTRO
  087 11 Ladin           SCHNESTER
b                      201
c                         200  2  201
c                         201  2  202
  087 23 Catalan         ESQUER, SINISTRE
b                      202
c                         201  2  202
  087 20 Spanish         IZQUIERDO
  087 21 Portuguese ST   ESQUERDO
  087 22 Brazilian       ESQUERDO
b                      203
c                         203  3  204
  087 56 Singhalese      VAMATA
b                      204
c                         203  3  204
c                         204  2  205
  087 63 Bengali         BA, BAM
b                      205
c                         204  2  205
  087 62 Hindi           BAYA
a 088 LEG
b                      001
  088 17 Sardinian N     ANKA
  088 38 Takitaki        FOETOE
  088 56 Singhalese      KAKULA
  088 80 Albanian T      KOFSHE
  088 59 Gujarati        PEG
  088 72 Armenian List   SAROONK
b                      002
  088 20 Spanish         PIERNA
  088 22 Brazilian       PERNA
  088 21 Portuguese ST   PERNA
b                      003
  088 42 Slovenian       NOGA
  088 46 Slovak          NOHA
  088 54 Serbocroatian   NOGA
  088 93 MACEDONIAN P    NOGA
  088 50 Polish          NOGA
  088 88 POLISH P        NOGA
  088 51 Russian         NOGA
  088 45 Czech           NOHA
  088 52 Macedonian      NOGA
  088 48 Ukrainian       NOGA, NIZKA
  088 49 Byelorussian    NAGA
  088 47 Czech E         NOHA
b                      004
  088 10 Italian         GAMBA
  088 18 Sardinian L     CAMBA
  088 15 French Creole C ZAM
  088 13 French          JAMBE
  088 16 French Creole D ZAM
  088 14 Walloon         DJAMBE
  088 23 Catalan         CAMA, CUIXA
  088 19 Sardinian C     KAMBA
  088 11 Ladin           CHAMMA
  088 12 Provencal       CAMBO, GARRO
b                      005
  088 41 Latvian         KAJA
  088 40 Lithuanian ST   KOJA
  088 39 Lithuanian O    KOJA
b                      006
  088 43 Lusatian L      GIZLA
  088 44 Lusatian U      HWIZDZEL
b                      007
  088 01 Irish A         COS
  088 02 Irish B         COS, COISE, -A
b                      008
  088 04 Welsh C         COES
  088 03 Welsh N         COES
b                      009
  088 61 Lahnda          TENG
  088 62 Hindi           TAG
  088 60 Panjabi ST      LETT, TENG
b                      010
  088 07 Breton ST       GAR
  088 06 Breton SE       GAR
  088 05 Breton List     GARR, GAR
b                      011
  088 57 Kashmiri        ZANG
  088 73 Ossetic         ZAENG
  088 55 Gypsy Gk        CANK
b                      012
  088 53 Bulgarian       KRAK
  088 94 BULGARIAN P     KRAK
b                      013
  088 82 Albanian G      KAMA
  088 95 ALBANIAN        KAMA
  088 84 Albanian C      KEMB
  088 83 Albanian K      KEMBE
  088 81 Albanian Top    KEMBE
b                      014
  088 65 Khaskura        KHUTTA
  088 64 Nepali List     KHUTTO
b                      015
  088 85 RUSSIAN P       GOLEN
  088 90 CZECH P         HOLEN
  088 87 BYELORUSSIAN P  HAL ONKA
  088 86 UKRAINIAN P     HOLINKA
  088 91 SLOVENIAN P     GOLEN
  088 89 SLOVAK P        HOLEN
  088 92 SERBOCROATIAN P GOLEN
b                      200
c                         200  2  201
c                         200  2  203
  088 68 Greek Mod       PODHI
  088 66 Greek ML        PODI
  088 70 Greek K         POUS
  088 67 Greek MD        PODI, SKELI
  088 69 Greek D         PODI
  088 78 Baluchi         PHADH
  088 35 Icelandic ST    FOTR
  088 77 Tadzik          PO, POJ
  088 71 Armenian Mod    OT
  088 63 Bengali         PA
  088 58 Marathi         PAY
  088 76 Persian List    PA
  088 08 Rumanian List   PICIOR
  088 09 Vlach           CORU
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  2  205
  088 26 Dutch List      BEEN, POOT
b                      202
c                         201  2  202
c                         202  2  205
  088 30 Swedish Up      BEN
  088 31 Swedish VL      BEN
  088 24 German ST       BEIN
  088 33 Danish          BEN
  088 32 Swedish List    BEN
  088 34 Riksmal         BEN
  088 25 Penn. Dutch     BAY
  088 28 Flemish         BEEN
  088 29 Frisian         BONKJE
  088 27 Afrikaans       BEEN
b                      203
c                         200  2  203
c                         201  2  203
c                         203  3  204
c                         203  3  205
c                         203  2  206
  088 79 Wakhi           LENG, PUED
b                      204
c                         203  3  204
c                         204  3  205
c                         204  3  206
  088 37 English ST      LEG
b                      205
c                         201  2  205
c                         202  2  205
c                         203  3  205
c                         204  3  205
c                         205  3  206
  088 36 Faroese         BEIN, LEGGUR
b                      206
c                         203  2  206
c                         204  3  206
c                         205  3  206
c                         206  2  207
  088 75 Waziri          LANGRA, PSHA
b                      207
c                         206  2  207
  088 74 Afghan          PSA
a 089 TO LIE (ON SIDE)
b                      000
  089 09 Vlach
  089 57 Kashmiri
  089 79 Wakhi
  089 29 Frisian
  089 82 Albanian G
  089 65 Khaskura
b                      001
  089 49 Byelorussian    ABKLADAC'
  089 56 Singhalese      ALA/WENAWA
  089 21 Portuguese ST   ESTAR POSTO
  089 17 Sardinian N     IMBOLARE
  089 18 Sardinian L     ISTERRIARE
  089 69 Greek D         KATHOMAI
  089 70 Greek K         KEIMAI
  089 75 Waziri          LMOSTEL
  089 71 Armenian Mod    PARKEL
  089 58 Marathi         PEDNE.
  089 74 Afghan          PREVATELAJ (3 SG.)
  089 95 ALBANIAN        RRI
  089 55 Gypsy Gk        UZANURUM
  089 78 Baluchi         WAFSAGH
  089 73 Ossetic         XUYCCYN, FAERSYL (UYN)
b                      002
  089 76 Persian List    KHABIDAN (DERAZ KASHIDAN)
  089 77 Tadzik          DAROZ KASIDAN, XOBIDAN
b                      003
  089 24 German ST       LIEGEN
  089 37 English ST      TO LIE
  089 38 Takitaki        LIDOM
  089 36 Faroese         LIGGJA
  089 33 Danish          LIGGE
  089 30 Swedish Up      LIGGA
  089 31 Swedish VL      LIGA
  089 32 Swedish List    LIGGA
  089 34 Riksmal         LIGGE
  089 35 Icelandic ST    LIGGJA
  089 27 Afrikaans       LE, LEG
  089 26 Dutch List      LIGGEN
  089 25 Penn. Dutch     LAYK
  089 28 Flemish         LIGGEN
  089 94 BULGARIAN P     LEZA
  089 87 BYELORUSSIAN P  L AZAC
  089 45 Czech           LEZETI
  089 90 CZECH P         LEZETI
  089 43 Lusatian L      LAZAS
  089 44 Lusatian U      LEZEC
  089 93 MACEDONIAN P    LEZAM
  089 50 Polish          LEZEC
  089 88 POLISH P        LEZAC
  089 51 Russian         LEZAT
  089 85 RUSSIAN P       LEZAT
  089 54 Serbocroatian   LEZATI
  089 92 SERBOCROATIAN P LEZATI
  089 46 Slovak          LEZAT
  089 89 SLOVAK P        LEZAT
  089 42 Slovenian       LEZI
  089 91 SLOVENIAN P     LEZATI
  089 86 UKRAINIAN P     LEZATY
  089 52 Macedonian      LEGNE, LEZI
  089 47 Czech E         LEZAT
  089 53 Bulgarian       DA LEZI
  089 48 Ukrainian       LEZATY, ZNAXODYTYS'
  089 01 Irish A         LUIGHE
  089 02 Irish B         LUIGHIM
b                      004
  089 07 Breton ST       GOURVEZ
  089 06 Breton SE       GOURVE
  089 05 Breton List     SOUCHA, GOURVEZ
  089 04 Welsh C         GORWEDD
  089 03 Welsh N         GORWEDD
b                      005
  089 66 Greek ML        KSAPLONO
  089 67 Greek MD        KSAPLONOMAI
  089 68 Greek Mod       IME-KSAPLOMENOS
b                      006
  089 41 Latvian         GULET
  089 40 Lithuanian ST   GULETI
  089 39 Lithuanian O    GULETI
b                      007
  089 81 Albanian Top    STRITEM, AOR. USTRITA
  089 80 Albanian T      ME U SHTRIRE
  089 83 Albanian K      RII   STRIXEM   JAM GLHATURE (LONG)
  089 84 Albanian C      STIXEM
b                      008
  089 60 Panjabi ST      LETNA
  089 61 Lahnda          LETEN
  089 62 Hindi           LETNA
b                      200
c                         200  2  201
  089 15 French Creole C KUSE
  089 13 French          SE COUCHER
  089 16 French Creole D KUSE
  089 14 Walloon         SI COUKI
  089 08 Rumanian List   A STA CULCAT
  089 19 Sardinian C     SI KROKKAI
b                      201
c                         200  2  201
c                         201  2  202
  089 12 Provencal       COUCHA, JAIRE
b                      202
c                         201  2  202
  089 10 Italian         GIACERE
  089 11 Ladin           GIASCHAIR
  089 20 Spanish         YACER
  089 22 Brazilian       JAZER
  089 23 Catalan         RESPOSAR, DESCANSAR, JAURER
b                      203
c                         203  3  204
  089 63 Bengali         SOA
  089 59 Gujarati        SUWU, (ARA PERWU)
  089 64 Nepali List     KOLTE SUTNU
b                      204
c                         203  3  204
  089 72 Armenian List   SUDEL
a 090 TO LIVE
b                      000
  090 55 Gypsy Gk
  090 09 Vlach
  090 79 Wakhi
  090 60 Panjabi ST      RENA (DWELL)
b                      001
  090 08 Rumanian List   A TRAI
  090 73 Ossetic         CAERYN
  090 17 Sardinian N     KAMPARE
  090 01 Irish A         MAIREACHTAINT
  090 75 Waziri          PAEDEL
b                      002
  090 37 English ST      TO LIVE
  090 24 German ST       LEBEN
  090 30 Swedish Up      LEVA
  090 31 Swedish VL      LEVA
  090 35 Icelandic ST    LIFA
  090 34 Riksmal         LEVE
  090 32 Swedish List    LEVA
  090 33 Danish          LEVE
  090 36 Faroese         LIVA
  090 29 Frisian         LEVE
  090 28 Flemish         LEVEN
  090 25 Penn. Dutch     LAYB
  090 26 Dutch List      LEVEN
  090 27 Afrikaans       LEEF, LEWE
  090 38 Takitaki        LIEBI
b                      003
  090 71 Armenian Mod    APREL
  090 72 Armenian List   ABRIL
b                      004
  090 81 Albanian Top    RON, AOR. ROJTA
  090 83 Albanian K      RON
  090 84 Albanian C      RON (PRET / ROVA)
  090 80 Albanian T      ME RROJTUR
  090 82 Albanian G      JETOJ, RROJ, ( RROJT = INF.)
  090 95 ALBANIAN        RROJ, (RROJTA = AOR.) (RROJT = INF.)
b                      005
  090 66 Greek ML        DZO
  090 70 Greek K         DZO
  090 67 Greek MD        DZO
  090 69 Greek D         DZO
  090 68 Greek Mod       ZO
  090 03 Welsh N         BYW
  090 04 Welsh C         BYW
  090 05 Breton List     BEVA
  090 06 Breton SE       BIUEIN
  090 07 Breton ST       BEVAN
  090 02 Irish B         DO BHEITH NA BHEATHIDH
  090 18 Sardinian L     VIVERE
  090 15 French Creole C VIV
  090 11 Ladin           VIVER
  090 19 Sardinian C     BIVI
  090 10 Italian         VIVERE
  090 23 Catalan         VIVRER, ESTAR
  090 20 Spanish         VIVIR
  090 12 Provencal       VIEURE
  090 14 Walloon         VIKER
  090 16 French Creole D VIV
  090 13 French          VIVRE
  090 21 Portuguese ST   VIVER
  090 22 Brazilian       VIVER
  090 56 Singhalese      JIVAT/WENAWA
  090 64 Nepali List     JIUNU
  090 61 Lahnda          JIWEN
  090 59 Gujarati        JIWEWU
  090 58 Marathi         JEGNE (BE ALIVE)
  090 63 Bengali         JIOA (BE ALIVE)
  090 62 Hindi           JINA (BE ALIVE)
  090 65 Khaskura        JIUNO
  090 86 UKRAINIAN P     ZYTY
  090 91 SLOVENIAN P     ZIVETI
  090 42 Slovenian       ZIVI
  090 89 SLOVAK P        ZIT
  090 46 Slovak          ZIT
  090 92 SERBOCROATIAN P ZIVETI
  090 54 Serbocroatian   ZIVITI
  090 85 RUSSIAN P       ZYT
  090 51 Russian         ZIT
  090 88 POLISH P        ZYC
  090 50 Polish          ZYC
  090 93 MACEDONIAN P    ZIVEAM
  090 44 Lusatian U      ZIC
  090 43 Lusatian L      ZYWIS SE
  090 90 CZECH P         ZITI
  090 45 Czech           ZITI
  090 87 BYELORUSSIAN P  ZYC
  090 94 BULGARIAN P     ZIVEJA
  090 41 Latvian         DZIVOT
  090 52 Macedonian      ZIVEE
  090 47 Czech E         ZIT
  090 49 Byelorussian    ZYC'
  090 48 Ukrainian       ZYTY, MESKATY
  090 53 Bulgarian       DA ZIBEE
  090 39 Lithuanian O    GYVENTI
  090 40 Lithuanian ST   GYVENTI
  090 57 Kashmiri        LASUN, ZUWUN
  090 74 Afghan          ZVAND KAVEL
  090 76 Persian List    ZENDEGI KARDAN
  090 78 Baluchi         ZINDAGH (LIVING)
  090 77 Tadzik          ZINDAGI KARDAN, ZISTAN
a 091 LIVER
b                      000
  091 52 Macedonian
  091 59 Gujarati
b                      001
  091 62 Hindi           DIL
  091 83 Albanian K      SPREKE
  091 84 Albanian C      U-FIGHATU
  091 56 Singhalese      PIKUDU
  091 18 Sardinian L     VIVENTE
b                      002
  091 30 Swedish Up      LEVER
  091 31 Swedish VL      LEVAR
  091 34 Riksmal         LEVER
  091 35 Icelandic ST    LIFR
  091 24 German ST       LEBER
  091 32 Swedish List    LEVER
  091 33 Danish          LEVER
  091 36 Faroese         LIVUR
  091 29 Frisian         LEVER
  091 28 Flemish         LEVER
  091 26 Dutch List      LEVER
  091 25 Penn. Dutch     LEVVER
  091 27 Afrikaans       LEWER
  091 38 Takitaki        LEVER
  091 37 English ST      LIVER
b                      003
  091 01 Irish A         AE, AENNA (PL.)
  091 02 Irish B         AE
  091 03 Welsh N         IAU, AFU
  091 04 Welsh C         AFU
  091 05 Breton List     AVU
  091 06 Breton SE       AHU
  091 07 Breton ST       AVU
b                      004
  091 13 French          FOIE
  091 21 Portuguese ST   FIGADO
  091 22 Brazilian       FIGADO
  091 09 Vlach           IDKATU
  091 17 Sardinian N     IKATU
  091 15 French Creole C FWA
  091 08 Rumanian List   FICAT
  091 11 Ladin           FIO
  091 19 Sardinian C     FIGAU
  091 10 Italian         FEGATO
  091 23 Catalan         FETGE
  091 20 Spanish         HIGADO
  091 12 Provencal       FEGE
  091 14 Walloon         FEUTE
  091 16 French Creole D FWA
b                      005
  091 51 Russian         PECEN
  091 86 UKRAINIAN P     PECINKA
  091 46 Slovak          PECEN
  091 85 RUSSIAN P       PECEN
  091 87 BYELORUSSIAN P  PECAN
  091 48 Ukrainian       PECINKA
  091 40 Lithuanian ST   KEPENOS (PL.), KEPENYS (PL.)
  091 39 Lithuanian O    KEPENYS
b                      006
  091 67 Greek MD        SEKOTI, SUKOTI
  091 69 Greek D         SEKOTI
  091 66 Greek ML        SEKOTI
  091 68 Greek Mod       SKOTI
b                      007
  091 80 Albanian T      MELCI
  091 95 ALBANIAN        MELTSI E ZEZ
  091 81 Albanian Top    MELCIA EZEZE
  091 82 Albanian G      MELTSI E ZEZ
b                      008
  091 71 Armenian Mod    LYARD
  091 72 Armenian List   LIART (JIYER)
b                      009
  091 75 Waziri          YENNA
  091 74 Afghan          INA
b                      200
c                         200  2  201
  091 63 Bengali         KOLJE
  091 65 Khaskura        KALEJO
  091 55 Gypsy Gk        KALINJO
  091 64 Nepali List     KALEJO
b                      201
c                         200  2  201
c                         201  2  202
  091 58 Marathi         KALIJ, YEKRIT
  091 57 Kashmiri        JIGAR, KALEJA
b                      202
c                         201  2  202
  091 73 Ossetic         IGAER
  091 61 Lahnda          JIGER
  091 79 Wakhi           JIGAR
  091 78 Baluchi         JAGHAR
  091 77 Tadzik          CIGAR
  091 76 Persian List    JEGAR
  091 60 Panjabi ST      JIGER
  091 41 Latvian         AKNAS
  091 70 Greek K         HEPAR
b                      203
c                         203  3  204
  091 47 Czech E         YATRA
  091 91 SLOVENIAN P     JETRA
  091 42 Slovenian       JTRA
  091 89 SLOVAK P        JATRA
  091 92 SERBOCROATIAN P JETRA
  091 54 Serbocroatian   JETRA
  091 44 Lusatian U      JATRA
  091 43 Lusatian L      JETSA
  091 90 CZECH P         JATRA
  091 45 Czech           JATRA
  091 88 POLISH P        WATROBA
  091 50 Polish          WATROBA
  091 49 Byelorussian    VANTROBA
b                      204
c                         203  3  204
  091 93 MACEDONIAN P    DROB
  091 53 Bulgarian       CERENDROB
  091 94 BULGARIAN P     CEREN DROB
a 092 LONG
b                      001
  092 41 Latvian         GARS
  092 55 Gypsy Gk        LUNGO
  092 57 Kashmiri        ZYUTHU
b                      002
  092 69 Greek D         MAKRUS
  092 67 Greek MD        MAKRUS
  092 70 Greek K         MAKROS
  092 66 Greek ML        MAKRUS
  092 68 Greek Mod       MAKRIS
b                      003
  092 64 Nepali List     LAMU
  092 61 Lahnda          LEMBA
  092 59 Gujarati        LAMBU
  092 58 Marathi         LAMB
  092 63 Bengali         LOMBA
  092 62 Hindi           LEMBA
  092 60 Panjabi ST      LEMMA
  092 65 Khaskura        LAMO
b                      004
  092 03 Welsh N         HIR
  092 04 Welsh C         HIR
  092 05 Breton List     HIR
  092 06 Breton SE       HIR
  092 07 Breton ST       HIR
b                      005
  092 20 Spanish         LARGO
  092 23 Catalan         LLARCH
b                      006
  092 02 Irish B         FADA
  092 01 Irish A         FADA
b                      007
  092 74 Afghan          UZD
  092 75 Waziri          WIZHD
b                      200
c                         200  2  201
c                         200  3  203
c                         200  3  204
  092 10 Italian         LUNGO
  092 09 Vlach           LUNGU
  092 18 Sardinian L     LONGU
  092 17 Sardinian N     LONGU
  092 15 French Creole C LON
  092 19 Sardinian C     LONGU
  092 11 Ladin           LUNGIA
  092 08 Rumanian List   LUNG
  092 16 French Creole D LON
  092 14 Walloon         LONG, LONGUE
  092 12 Provencal       LONG, LONGO
  092 13 French          LONG
  092 37 English ST      LONG
  092 30 Swedish Up      LANG
  092 31 Swedish VL      LONG
  092 25 Penn. Dutch     LUNG
  092 28 Flemish         LANG
  092 29 Frisian         LANG
  092 36 Faroese         LANGUR
  092 33 Danish          LANG
  092 32 Swedish List    LANG
  092 34 Riksmal         LANG
  092 35 Icelandic ST    LANGR
  092 24 German ST       LANG
  092 26 Dutch List      LANG
  092 27 Afrikaans       LANG
  092 38 Takitaki        LANGA
  092 40 Lithuanian ST   ILGAS
  092 39 Lithuanian O    ILGAS
  092 79 Wakhi           DEROZ, VERZ
  092 78 Baluchi         DRAZH
  092 77 Tadzik          DAROZ, DUR
  092 76 Persian List    DERAZ
  092 73 Ossetic         DARG"
  092 86 UKRAINIAN P     DOUHYJ
  092 91 SLOVENIAN P     DOLG
  092 42 Slovenian       DOVGU
  092 89 SLOVAK P        DLHY
  092 46 Slovak          DLHY
  092 92 SERBOCROATIAN P DUG
  092 54 Serbocroatian   DUG
  092 85 RUSSIAN P       DOLGIJ
  092 51 Russian         DLINNYJ (SPAT.), DOLGIJ (TEMP.)
  092 88 POLISH P        DLUGI
  092 50 Polish          DLUGI
  092 93 MACEDONIAN P    DOLG
  092 44 Lusatian U      DOLHI
  092 43 Lusatian L      DLUJKI
  092 90 CZECH P         DLOUHY
  092 45 Czech           DLOUHY
  092 87 BYELORUSSIAN P  DOUHI
  092 94 BULGARIAN P     DULUG
  092 52 Macedonian      DOLG
  092 47 Czech E         DLUHE
  092 49 Byelorussian    DAWHI, DOWHA
  092 48 Ukrainian       DOVGYJ, - A - E
  092 53 Bulgarian       DELGO
  092 56 Singhalese      DIGA
b                      201
c                         200  2  201
c                         201  2  202
c                         201  3  203
c                         201  3  204
  092 21 Portuguese ST   LONGO, COMPRIDO
b                      202
c                         201  2  202
  092 22 Brazilian       COMPRIDO
b                      203
c                         200  3  203
c                         201  3  203
c                         203  3  204
  092 80 Albanian T      I, E GJATHE
  092 83 Albanian K      I GLHATE
  092 84 Albanian C      I-GLAT
  092 82 Albanian G      GJAT
  092 95 ALBANIAN        GJAT
  092 81 Albanian Top    I-GATE
b                      204
c                         200  3  204
c                         201  3  204
c                         203  3  204
  092 71 Armenian Mod    ERKAR
  092 72 Armenian List   YERGAR
a 093 LOUSE
b                      000
  093 67 Greek MD
  093 61 Lahnda
  093 77 Tadzik
  093 59 Gujarati
b                      001
  093 78 Baluchi         BOT
  093 56 Singhalese      TADIYA
b                      002
  093 75 Waziri          SPAZHA
  093 74 Afghan          SPEZA, SPEZA
  093 76 Persian List    SHEPESH
b                      003
  093 13 French          POU
  093 16 French Creole D PU
  093 09 Vlach           BIDUKLU
  093 18 Sardinian L     PIOGU
  093 17 Sardinian N     PRIUKKU
  093 15 French Creole C PU
  093 08 Rumanian List   PADUCHE
  093 11 Ladin           PLUOGL
  093 19 Sardinian C     PRIOGU
  093 10 Italian         PIDOCCHIO
  093 23 Catalan         POLL
  093 20 Spanish         PIOJO
  093 12 Provencal       PESOU
  093 21 Portuguese ST   PIOLHO
  093 22 Brazilian       PIOLHO
  093 14 Walloon         PIOU
b                      004
  093 81 Albanian Top    MOR
  093 80 Albanian T      MOZ
  093 83 Albanian K      MOR
  093 84 Albanian C      MOR
  093 82 Albanian G      MORRA
  093 95 ALBANIAN        MORR
b                      005
  093 69 Greek D         PSULLOS
  093 70 Greek K         PSULLOS
b                      006
  093 66 Greek ML        PSEIRA
  093 68 Greek Mod       PSIRA
b                      007
  093 01 Irish A         MIOL
  093 02 Irish B         MIOL
b                      008
  093 58 Marathi         U
  093 63 Bengali         UKUN
b                      009
  093 71 Armenian Mod    OJIL
  093 72 Armenian List   OCHIL
b                      010
  093 73 Ossetic         SYST
  093 79 Wakhi           SIS
b                      200
c                         200  3  201
c                         200  3  202
c                         200  3  203
c                         200  3  204
  093 25 Penn. Dutch     LOUSE
  093 35 Icelandic ST    LUS
  093 34 Riksmal         LUS
  093 32 Swedish List    LUS
  093 33 Danish          LUS
  093 36 Faroese         LUS
  093 28 Flemish         LUIS
  093 27 Afrikaans       LUIS
  093 38 Takitaki        LOSO
  093 37 English ST      LOUSE
  093 30 Swedish Up      LUS
  093 31 Swedish VL      LUS
  093 24 German ST       LAUS
  093 26 Dutch List      VLOO, LUIS
  093 29 Frisian         FLIE, LUS, LUS
b                      201
c                         200  3  201
c                         201  3  202
c                         201  3  203
c                         201  3  204
  093 03 Welsh N         LLO
  093 04 Welsh C         LLEUEN
  093 05 Breton List     LAOU
  093 06 Breton SE       LEUEN
  093 07 Breton ST       LAOUENN
b                      202
c                         200  3  202
c                         201  3  202
c                         202  3  203
c                         202  3  204
  093 40 Lithuanian ST   UTELE
  093 39 Lithuanian O    UTELE
  093 41 Latvian         UTS
b                      203
c                         200  3  203
c                         201  3  203
c                         202  3  203
c                         203  3  204
  093 92 SERBOCROATIAN P VAS
  093 87 BYELORUSSIAN P  VOS
  093 94 BULGARIAN P     VUSKA
  093 52 Macedonian      VOSKA
  093 47 Czech E         VES
  093 49 Byelorussian    VOS
  093 48 Ukrainian       VOSA, VOS
  093 53 Bulgarian       VESKA
  093 46 Slovak          VOS
  093 89 SLOVAK P        VOS
  093 42 Slovenian       USI
  093 91 SLOVENIAN P     US
  093 86 UKRAINIAN P     VOSA
  093 45 Czech           VES
  093 90 CZECH P         VES
  093 43 Lusatian L      WES
  093 44 Lusatian U      WOS
  093 93 MACEDONIAN P    VOSKA
  093 50 Polish          WESZ
  093 88 POLISH P        WESZ
  093 51 Russian         VOS
  093 85 RUSSIAN P       VOS
  093 54 Serbocroatian   US
b                      204
c                         200  3  204
c                         201  3  204
c                         202  3  204
c                         203  3  204
  093 64 Nepali List     JUMRO
  093 62 Hindi           JU
  093 60 Panjabi ST      JU
  093 65 Khaskura        JUMRA
  093 55 Gypsy Gk        JUV
  093 57 Kashmiri        ZOV
a 094 MAN (MALE)
b                      001
  094 76 Persian List    ADAM
  094 61 Lahnda          ADMI
  094 62 Hindi           ADMI
  094 60 Panjabi ST      ADMI
  094 38 Takitaki        SOEMA
b                      002
  094 06 Breton SE       GOAS
  094 07 Breton ST       GWAZ
b                      003
  094 08 Rumanian List   BARBAT
  094 09 Vlach           BERBATU
b                      200
c                         200  2  201
  094 22 Brazilian       HOMEM
  094 13 French          HOMME
  094 16 French Creole D NOM
  094 14 Walloon         OME
  094 12 Provencal       OME
  094 20 Spanish         HOMBRE
  094 23 Catalan         HOME
  094 21 Portuguese ST   HOMEM, VARAO
  094 19 Sardinian C     OMINI
  094 10 Italian         UOMO
  094 11 Ladin           HOMENS, CRASTIAUN
  094 15 French Creole C NOM
  094 18 Sardinian L     OMINE
  094 17 Sardinian N     OMINE
  094 02 Irish B         DUINE
  094 04 Welsh C         DYN
  094 05 Breton List     DEN
b                      201
c                         200  2  201
c                         201  2  202
  094 03 Welsh N         DYN, GWR
b                      202
c                         201  2  202
  094 39 Lithuanian O    VYRAS
  094 41 Latvian         VIRIETIS
  094 40 Lithuanian ST   VYRAS
  094 01 Irish A         FEAR
b                      203
c                         203  2  204
  094 52 Macedonian      COVEK
  094 94 BULGARIAN P     COVEK
  094 87 BYELORUSSIAN P  CALAVEK
  094 90 CZECH P         CLOVEK
  094 43 Lusatian L      CLOWEK
  094 44 Lusatian U      CLOWJEK
  094 93 MACEDONIAN P    COVEK
  094 88 POLISH P        CZLOWIEK
  094 85 RUSSIAN P       CELOVEK
  094 54 Serbocroatian   COVEK
  094 92 SERBOCROATIAN P COVEK
  094 89 SLOVAK P        CLOVEK
  094 86 UKRAINIAN P     COLOVIK
  094 91 SLOVENIAN P     CLOVEK
  094 48 Ukrainian       LJUDYNA
b                      204
c                         203  2  204
c                         204  2  205
c                         204  2  206
  094 49 Byelorussian    MUZCYNA, CALAVEK
b                      205
c                         204  2  205
c                         205  2  206
  094 42 Slovenian       MOZ, MASKI
  094 46 Slovak          CHLAP, MUZ
  094 51 Russian         MUZCINA
  094 50 Polish          MEZCZYZNA
  094 45 Czech           MUZ
  094 53 Bulgarian       MEZ
  094 47 Czech E         XLAP, MUSKI
  094 37 English ST      MAN
  094 27 Afrikaans       MAN
  094 26 Dutch List      MAN
  094 24 German ST       MANN
  094 34 Riksmal         MANN
  094 33 Danish          MAND
  094 25 Penn. Dutch     MAAN
  094 28 Flemish         MAN
  094 29 Frisian         MAN
  094 32 Swedish List    MAN, KARL
  094 30 Swedish Up      KARL, MAN
  094 36 Faroese         MADUR, KALLMADUR
  094 31 Swedish VL      KAR, MAN
  094 35 Icelandic ST    KARL / KARLMADR / MADR
  094 59 Gujarati        MANES
  094 65 Khaskura        MANCHHA, JANA, MANIS
  094 56 Singhalese      MINIHA
b                      206
c                         204  2  206
c                         205  2  206
c                         206  2  207
c                         206  2  208
  094 64 Nepali List     MANCHE, LOGNE, PURUKH
b                      207
c                         206  2  207
c                         207  2  208
c                         207  2  209
c                         207  2  210
c                         207  2  212
c                         207  2  214
c                         207  2  216
  094 57 Kashmiri        MARD, PORUSH, NAR, ZONU
b                      208
c                         206  2  208
c                         207  2  208
  094 63 Bengali         PURUS
  094 58 Marathi         PURUS
  094 55 Gypsy Gk        MRUS
b                      209
c                         207  2  209
c                         209  2  210
  094 78 Baluchi         MARD, MAR
  094 77 Tadzik          MARD
  094 71 Armenian Mod    MARD
  094 72 Armenian List   MART
b                      210
c                         207  2  210
c                         209  2  210
c                         210  3  211
  094 79 Wakhi           MERDINA, DAEI, XULG
b                      211
c                         210  3  211
  094 73 Ossetic         LAEG, NAELGOJMAG
b                      212
c                         207  2  212
c                         212  2  213
c                         212  2  214
c                         212  2  216
  094 95 ALBANIAN        BURRI, NJERIU
b                      213
c                         212  2  213
  094 81 Albanian Top    BURE
  094 80 Albanian T      BURRE
  094 83 Albanian K      BURE
  094 84 Albanian C      BUR
  094 82 Albanian G      BURRI
b                      214
c                         207  2  214
c                         212  2  214
c                         214  2  215
c                         214  2  216
  094 75 Waziri          NAR, NER, SARAI
b                      215
c                         214  2  215
  094 74 Afghan          SARAJ
b                      216
c                         207  2  216
c                         212  2  216
c                         214  2  216
  094 69 Greek D         ANTRAS
  094 67 Greek MD        ANTRAS
  094 70 Greek K         ANER
  094 66 Greek ML        ANTRAS
  094 68 Greek Mod       ANDRAS
a 095 MANY
b                      001
  095 11 Ladin           BAINQUAUNTS, BGER
  095 73 Ossetic         BIRAE
  095 29 Frisian         BOT, RJUE
  095 38 Takitaki        FOELOE
  095 79 Wakhi           GHUFC
  095 47 Czech E         HODNE
  095 61 Lahnda          KEI
  095 12 Provencal       MANT, ANTO
  095 35 Icelandic ST    MARGIR
  095 58 Marathi         PUSKEL, PHAR, KHUP
  095 49 Byelorussian    SMAT
  095 57 Kashmiri        SETHAH
b                      002
  095 09 Vlach           MULTI
  095 08 Rumanian List   MULTI, MULTE
  095 10 Italian         MOLTI
  095 23 Catalan         MOLT, FORSA
  095 20 Spanish         MUCHOS
  095 21 Portuguese ST   MUITOS
  095 22 Brazilian       MUITOS
b                      003
  095 76 Persian List    ZIAD, CHANDIN
  095 77 Tadzik          BIS ER, XELE, ZIED
b                      004
  095 40 Lithuanian ST   DAUG
  095 39 Lithuanian O    DAUG
  095 41 Latvian         DAUDZ
  095 42 Slovenian       DOSTI
  095 50 Polish          DUZO
b                      005
  095 81 Albanian Top    SUME
  095 80 Albanian T      SHUME
  095 83 Albanian K      SUME
  095 84 Albanian C      SUM
  095 82 Albanian G      SHUM
  095 95 ALBANIAN        SHUM
b                      006
  095 14 Walloon         BECOP
  095 13 French          BEAUCOUP
b                      007
  095 18 Sardinian L     MEDAS
  095 19 Sardinian C     MERAS
  095 17 Sardinian N     METAS
b                      008
  095 16 French Creole D OTA
  095 15 French Creole C STA, A PIL
b                      009
  095 62 Hindi           BOHT
  095 60 Panjabi ST      BOT
  095 55 Gypsy Gk        BUT
  095 78 Baluchi         BA Z
b                      010
  095 48 Ukrainian       BAHATO
  095 86 UKRAINIAN P     BAHATO
b                      011
  095 71 Armenian Mod    BAZUM, SAT
  095 72 Armenian List   SHAD
b                      100
  095 63 Bengali         ONEK
  095 56 Singhalese      HUNGAK
b                      200
c                         200  2  201
  095 37 English ST      MANY
  095 30 Swedish Up      MANGA
  095 31 Swedish VL      MANG  MONG
  095 34 Riksmal         MANGE
  095 32 Swedish List    MANGA
  095 33 Danish          MANGE
  095 36 Faroese         MANGUR
  095 91 SLOVENIAN P     MNOG
  095 89 SLOVAK P        MNOHY
  095 51 Russian         MNOGO
  095 85 RUSSIAN P       MNOGO
  095 54 Serbocroatian   MNOGI
  095 92 SERBOCROATIAN P MNOGO
  095 44 Lusatian U      MNOHO
  095 93 MACEDONIAN P    MNOGU
  095 94 BULGARIAN P     MNOGO
  095 87 BYELORUSSIAN P  MNOHA
  095 45 Czech           MNOHO, MNOHY
  095 90 CZECH P         MNOHY
  095 43 Lusatian L      MLOGI
  095 52 Macedonian      KALABALAK/MNOGU
  095 53 Bulgarian       MNOGO
b                      201
c                         200  2  201
c                         201  2  202
  095 46 Slovak          MNOHY, NEJEDEN, VEL A
b                      202
c                         201  2  202
  095 88 POLISH P        WIELE
b                      203
c                         203  2  204
  095 67 Greek MD        POLLOI
  095 69 Greek D         POLLOI
  095 70 Greek K         POLLOI
  095 66 Greek ML        POLLOI
  095 68 Greek Mod       POLI
  095 24 German ST       VIELE
  095 28 Flemish         VEEL, VELE
  095 25 Penn. Dutch     FIEL
  095 27 Afrikaans       BAIE, VEEL
  095 26 Dutch List      VEEL
b                      204
c                         203  2  204
c                         204  2  205
  095 05 Breton List     KALZ, E-LEIZ, MEURBET
b                      205
c                         204  2  205
  095 06 Breton SE       KALZ
  095 07 Breton ST       KALZ
b                      206
c                         206  2  207
  095 65 Khaskura        DHERI, SASTI
  095 74 Afghan          DER
  095 75 Waziri          DER
b                      207
c                         206  2  207
c                         207  3  208
  095 64 Nepali List     DHER, GHANERO
b                      208
c                         207  3  208
  095 59 Gujarati        GHERU (BEHU)
b                      209
c                         209  2  210
  095 03 Welsh N         LLAWER
  095 04 Welsh C         LLAWER
b                      210
c                         209  2  210
c                         210  2  211
  095 01 Irish A         GO LEOR, MORAN
b                      211
c                         210  2  211
  095 02 Irish B         MORAN, IOMAD, IOMDHA, LIACHT, FOIRLION
a 096 MEAT (FLESH)
b                      001
  096 73 Ossetic         FYD, FYDYZG"AED
  096 41 Latvian         GALA
b                      002
  096 02 Irish B         FEOIL
  096 01 Irish A         FEOIL
b                      003
  096 03 Welsh N         CIG, CNAWD
  096 04 Welsh C         CIG
  096 05 Breton List     KIG
  096 06 Breton SE       KIG
  096 07 Breton ST       KIG
b                      004
  096 79 Wakhi           GOST
  096 78 Baluchi         GOZHD
  096 74 Afghan          GVASA
  096 77 Tadzik          GUST
  096 76 Persian List    GUSHT
  096 75 Waziri          GHOSHA, GHESHA
b                      005
  096 36 Faroese         HOLD
  096 35 Icelandic ST    HOLD
b                      006
  096 24 German ST       FLEISCH
  096 29 Frisian         FLEIS, FLESK, FLESK
  096 28 Flemish         VLEESCH
  096 25 Penn. Dutch     FLAYSCH
  096 26 Dutch List      VLEESCH
  096 27 Afrikaans       VLEES, VLEIS
b                      007
  096 55 Gypsy Gk        MAS
  096 81 Albanian Top    MIS
  096 86 UKRAINIAN P     M ASO
  096 91 SLOVENIAN P     MESO
  096 42 Slovenian       MESO
  096 89 SLOVAK P        MASO
  096 46 Slovak          MASO
  096 92 SERBOCROATIAN P MESO
  096 54 Serbocroatian   MESO
  096 85 RUSSIAN P       M ASO
  096 51 Russian         MJASO
  096 88 POLISH P        MIESO
  096 50 Polish          MIESO
  096 93 MACEDONIAN P    MESO
  096 44 Lusatian U      MJASO
  096 43 Lusatian L      MESO
  096 90 CZECH P         MASO
  096 45 Czech           MASO
  096 87 BYELORUSSIAN P  M ASA
  096 94 BULGARIAN P     MESO
  096 39 Lithuanian O    MESA
  096 40 Lithuanian ST   MESA
  096 56 Singhalese      MAS
  096 57 Kashmiri        MAZ
  096 64 Nepali List     MASU
  096 61 Lahnda          MAS
  096 80 Albanian T      MISH
  096 83 Albanian K      MIS
  096 84 Albanian C      MIS
  096 82 Albanian G      MISHT
  096 52 Macedonian      MESO
  096 59 Gujarati        MAS
  096 95 ALBANIAN        MISHT
  096 58 Marathi         MAS, MAVS
  096 63 Bengali         MANSO
  096 62 Hindi           MAS
  096 60 Panjabi ST      MAS
  096 65 Khaskura        SHIKAR, MASU
  096 71 Armenian Mod    MIS
  096 47 Czech E         MASO
  096 49 Byelorussian    MJASA
  096 48 Ukrainian       M'JASO, M'JASYVO
  096 53 Bulgarian       MESO
  096 72 Armenian List   MIS
b                      008
  096 19 Sardinian C     PECCA
  096 18 Sardinian L     PETTA
  096 17 Sardinian N     PETHTHA
b                      009
  096 69 Greek D         KREAS
  096 67 Greek MD        KREAS
  096 70 Greek K         KREAS
  096 66 Greek ML        KREAS
  096 68 Greek Mod       KREAS
b                      200
c                         200  2  201
  096 30 Swedish Up      KOTT
  096 31 Swedish VL      TZOT
  096 34 Riksmal         KJOTT
  096 33 Danish          KOD
b                      201
c                         200  2  201
c                         201  3  202
  096 32 Swedish List    MAT, KOTT
b                      202
c                         201  3  202
  096 37 English ST      MEAT
  096 38 Takitaki        METI
b                      203
c                         203  2  204
  096 08 Rumanian List   CARNE
  096 11 Ladin           CHARN
  096 10 Italian         CARNE
  096 23 Catalan         CARN
  096 20 Spanish         CARNE
  096 14 Walloon         TCHAR
  096 21 Portuguese ST   CARNE
  096 22 Brazilian       CARNE
  096 09 Vlach           KARNE
  096 16 French Creole D LASE
b                      204
c                         203  2  204
c                         204  2  205
  096 12 Provencal       VIANDO, CAR
b                      205
c                         204  2  205
  096 15 French Creole C VYAN, LASE (FLESH)
  096 13 French          VIANDE
a 097 MOTHER
b                      001
  097 58 Marathi         AI
  097 55 Gypsy Gk        DALE
  097 09 Vlach           MAIKA
  097 79 Wakhi           NUN
b                      200
c                         200  2  201
c                         200  2  202
c                         200  2  203
c                         200  3  204
  097 37 English ST      MOTHER
  097 30 Swedish Up      MOR, MODER
  097 31 Swedish VL      MOR
  097 73 Ossetic         MAD
  097 86 UKRAINIAN P     MATY
  097 91 SLOVENIAN P     MATI
  097 42 Slovenian       MATI
  097 89 SLOVAK P        MAT
  097 46 Slovak          MATKA
  097 92 SERBOCROATIAN P MATI
  097 85 RUSSIAN P       MAT
  097 51 Russian         MAT
  097 88 POLISH P        MATKA
  097 50 Polish          MATKA
  097 44 Lusatian U      MAC
  097 43 Lusatian L      MAS
  097 90 CZECH P         MATI
  097 45 Czech           MATKA
  097 87 BYELORUSSIAN P  MACI
  097 41 Latvian         MATE
  097 39 Lithuanian O    MOTINA
  097 40 Lithuanian ST   MOTINA
  097 67 Greek MD        METERA
  097 70 Greek K         METER
  097 66 Greek ML        METERA
  097 68 Greek Mod       MITERA
  097 78 Baluchi         MATH
  097 74 Afghan          MOR
  097 10 Italian         MADRE
  097 23 Catalan         MARE
  097 20 Spanish         MADRE
  097 12 Provencal       MAIRE
  097 14 Walloon         MERE
  097 13 French          MERE
  097 02 Irish B         MATHAIR
  097 01 Irish A         MATHAIR
  097 24 German ST       MUTTER
  097 35 Icelandic ST    MOOIR
  097 34 Riksmal         MOR
  097 32 Swedish List    MODER
  097 33 Danish          MODER
  097 36 Faroese         MODIR
  097 26 Dutch List      MOEDER
  097 77 Tadzik          MODAR
  097 76 Persian List    MADAR
  097 71 Armenian Mod    MAYR
  097 49 Byelorussian    MACI
  097 22 Brazilian       MAE
  097 72 Armenian List   MIRE
  097 75 Waziri          MOR, MER
  097 21 Portuguese ST   MAI
  097 61 Lahnda          MA
  097 63 Bengali         MA
  097 62 Hindi           MA
  097 60 Panjabi ST      MA
  097 59 Gujarati        MA, BA, MATA
  097 57 Kashmiri        MOJU
  097 48 Ukrainian       MATY, NEN'KA
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  3  204
c                         201  3  206
c                         201  3  207
c                         201  3  208
c                         201  3  209
c                         201  3  210
c                         201  3  212
  097 69 Greek D         MANA, MAMA, METERA
b                      202
c                         200  2  202
c                         201  2  202
c                         202  3  203
c                         202  3  206
c                         202  3  207
c                         202  2  208
c                         202  3  209
c                         202  3  210
c                         202  3  212
  097 27 Afrikaans       MOEDER, MA
  097 28 Flemish         MOEDER, MAMA
  097 25 Penn. Dutch     MEM, MOM, MUUTER, MOMMI
b                      203
c                         200  2  203
c                         201  2  203
c                         202  3  203
c                         203  3  204
c                         203  3  206
c                         203  3  207
c                         203  3  208
c                         203  3  209
c                         203  3  210
c                         203  3  212
  097 47 Czech E         MAMA, MATKA
b                      204
c                         200  3  204
c                         201  3  204
c                         203  3  204
c                         204  2  205
  097 56 Singhalese      MAVA, AMMA
b                      205
c                         204  2  205
  097 65 Khaskura        AMA
  097 64 Nepali List     AMA
b                      206
c                         201  3  206
c                         202  3  206
c                         203  3  206
c                         206  3  207
c                         206  3  208
c                         206  3  209
c                         206  3  210
c                         206  3  212
  097 18 Sardinian L     MAMMA
  097 17 Sardinian N     MAMA
  097 15 French Creole C MAMA
  097 08 Rumanian List   MAMA
  097 11 Ladin           MAMA
  097 19 Sardinian C     MAMMA
  097 16 French Creole D MAMA
b                      207
c                         201  3  207
c                         202  3  207
c                         203  3  207
c                         206  3  207
c                         207  3  208
c                         207  3  209
c                         207  3  210
c                         207  3  212
  097 03 Welsh N         MAM
  097 04 Welsh C         MAM
  097 05 Breton List     MAMM
  097 06 Breton SE       MAMM
  097 07 Breton ST       MAMM
b                      208
c                         201  3  208
c                         202  2  208
c                         203  3  208
c                         206  3  208
c                         207  3  208
c                         208  3  209
c                         208  3  210
c                         208  3  212
  097 38 Takitaki        MAMA
  097 29 Frisian         MEM
b                      209
c                         201  3  209
c                         202  3  209
c                         203  3  209
c                         206  3  209
c                         207  3  209
c                         208  3  209
c                         209  2  210
c                         209  3  212
  097 83 Albanian K      MEME
  097 84 Albanian C      MEM
b                      210
c                         201  3  210
c                         202  3  210
c                         203  3  210
c                         206  3  210
c                         207  3  210
c                         208  3  210
c                         209  2  210
c                         210  2  211
c                         210  3  212
  097 82 Albanian G      AMA, MOMA, NANA
  097 95 ALBANIAN        MOMA, AMA, NANA
b                      211
c                         210  2  211
  097 81 Albanian Top    NENE
  097 80 Albanian T      NENE
b                      212
c                         201  3  212
c                         202  3  212
c                         203  3  212
c                         206  3  212
c                         207  3  212
c                         208  3  212
c                         209  3  212
c                         210  3  212
  097 54 Serbocroatian   MAJKA
  097 93 MACEDONIAN P    MAJKA
  097 94 BULGARIAN P     MAJKA
  097 52 Macedonian      MAJKA
  097 53 Bulgarian       MAJKA
a 098 MOUNTAIN
b                      001
  098 58 Marathi         DONGER
  098 56 Singhalese      KANDA
  098 37 English ST      MOUNTAIN
  098 25 Penn. Dutch     MOUNTAIN
  098 55 Gypsy Gk        VOS
b                      002
  098 17 Sardinian N     MONTE
  098 18 Sardinian L     MUNTAGNA
  098 09 Vlach           MUNDE
  098 15 French Creole C MON, MOTAY
  098 08 Rumanian List   MUNTE
  098 11 Ladin           MUNT, MUNTAGNA
  098 19 Sardinian C     MONTI
  098 10 Italian         MONTAGNA, MONTE
  098 23 Catalan         MONT, MONTANYA
  098 20 Spanish         MONTANA
  098 12 Provencal       MOUNTAGNO
  098 14 Walloon         MONTAGNE
  098 16 French Creole D MON
  098 13 French          MONTAGNE
  098 21 Portuguese ST   MONTE, MONTANHA
  098 22 Brazilian       MONTANHA
  098 03 Welsh N         MYNYDD
  098 04 Welsh C         MYNYDD
  098 05 Breton List     MENEZ
  098 06 Breton SE       MANNE
  098 07 Breton ST       MENEZ
b                      003
  098 73 Ossetic         XOX
  098 79 Wakhi           KU(H)
  098 77 Tadzik          KUX
  098 76 Persian List    KUH
b                      004
  098 40 Lithuanian ST   KALNAS
  098 39 Lithuanian O    KALNAS
  098 41 Latvian         KALNS
b                      005
  098 02 Irish B         SLAIBH
  098 01 Irish A         SLIABH
b                      006
  098 72 Armenian List   LEV
  098 71 Armenian Mod    SAR, LER
b                      007
  098 81 Albanian Top    MAL
  098 80 Albanian T      MAL
  098 83 Albanian K      MAL
  098 84 Albanian C      MAL
  098 82 Albanian G      MALI
  098 95 ALBANIAN        MALI
b                      200
c                         200  2  201
  098 30 Swedish Up      BERG
  098 24 German ST       BERG
  098 32 Swedish List    BERG
  098 33 Danish          BJERG
  098 29 Frisian         BERCH
  098 28 Flemish         BERG
  098 26 Dutch List      BERG
  098 27 Afrikaans       BERG
  098 38 Takitaki        BERGI
b                      201
c                         200  2  201
c                         201  2  202
  098 31 Swedish VL      FJEL  FJAL, BARJ
b                      202
c                         201  2  202
  098 35 Icelandic ST    FJALL
  098 34 Riksmal         FJELL
  098 36 Faroese         FJALL
b                      203
c                         203  2  204
  098 53 Bulgarian       PLANINA
  098 94 BULGARIAN P     PLANINA
  098 93 MACEDONIAN P    PLANINA
b                      204
c                         203  2  204
c                         204  2  205
  098 52 Macedonian      PLANINA/BRDO/GORA
b                      205
c                         204  2  205
  098 50 Polish          GORA
  098 88 POLISH P        GORA
  098 51 Russian         GORA
  098 85 RUSSIAN P       GORA
  098 54 Serbocroatian   GORA
  098 92 SERBOCROATIAN P GORA
  098 46 Slovak          HORA
  098 89 SLOVAK P        HORA
  098 42 Slovenian       GORE
  098 91 SLOVENIAN P     GORA
  098 86 UKRAINIAN P     HORA
  098 45 Czech           HORA
  098 90 CZECH P         HORA
  098 43 Lusatian L      GORA
  098 44 Lusatian U      HORA
  098 87 BYELORUSSIAN P  HARA
  098 47 Czech E         HORA
  098 49 Byelorussian    HARA
  098 48 Ukrainian       HORA
  098 75 Waziri          GHAR
  098 74 Afghan          GAR
b                      206
c                         206  2  207
  098 57 Kashmiri        BAL, PARBATH
  098 64 Nepali List     PARBAT
  098 65 Khaskura        PARBAT, LEKH
  098 63 Bengali         PORBOT
  098 78 Baluchi         PHAWAD
b                      207
c                         206  2  207
c                         207  2  208
  098 59 Gujarati        PERWET, PEHAR
b                      208
c                         207  2  208
  098 61 Lahnda          PEHAR
  098 62 Hindi           PEHAR
  098 60 Panjabi ST      PAR
b                      209
c                         209  2  210
  098 70 Greek K         OROS
b                      210
c                         209  2  210
c                         210  2  211
  098 67 Greek MD        BOUNO, OROS
b                      211
c                         210  2  211
  098 69 Greek D         BOUNO
  098 68 Greek Mod       VUNO
  098 66 Greek ML        BOUNO
a 099 MOUTH
b                      001
  099 79 Wakhi           GHUS
  099 47 Czech E         HUBA
  099 56 Singhalese      KATA
  099 58 Marathi         TOND
b                      002
  099 86 UKRAINIAN P     ROT
  099 85 RUSSIAN P       ROT
  099 51 Russian         ROT
  099 87 BYELORUSSIAN P  ROT
  099 48 Ukrainian       ROT
  099 49 Byelorussian    ROT
b                      003
  099 09 Vlach           GURE
  099 08 Rumanian List   GURA
b                      004
  099 81 Albanian Top    GOJE
  099 80 Albanian T      GOJE
  099 83 Albanian K      GOLHE
  099 84 Albanian C      GOJ
  099 82 Albanian G      GOJA
  099 95 ALBANIAN        GOJA
b                      005
  099 40 Lithuanian ST   BURNA
  099 39 Lithuanian O    BURNA
  099 71 Armenian Mod    BERAN
  099 72 Armenian List   BERAN
b                      006
  099 18 Sardinian L     BUCCA
  099 17 Sardinian N     BUKKA
  099 15 French Creole C BUS
  099 11 Ladin           BUOCHA
  099 19 Sardinian C     BUKKA
  099 10 Italian         BOCCA
  099 23 Catalan         BOCA
  099 13 French          BOUCHE
  099 16 French Creole D BUS
  099 14 Walloon         BOKE
  099 12 Provencal       BOUCO, AIS
  099 20 Spanish         BOCA
  099 21 Portuguese ST   BOCCA
  099 22 Brazilian       BOCA
b                      007
  099 30 Swedish Up      MUN
  099 31 Swedish VL      MON
  099 32 Swedish List    MUN
  099 34 Riksmal         MUNN
  099 35 Icelandic ST    MUNNR
  099 24 German ST       MUND
  099 33 Danish          MUND
  099 36 Faroese         MUNNUR
  099 28 Flemish         MOND
  099 26 Dutch List      MOND
  099 27 Afrikaans       MOND
  099 37 English ST      MOUTH
  099 38 Takitaki        MOFO
b                      008
  099 68 Greek Mod       STOMA
  099 66 Greek ML        STOMA
  099 70 Greek K         STOMA
  099 67 Greek MD        STOMA
  099 69 Greek D         STOMA
b                      009
  099 01 Irish A         BEAL
  099 02 Irish B         BEAL, -EIL
b                      100
  099 74 Afghan          XLA
  099 75 Waziri          KHWULA
b                      200
c                         200  2  201
  099 91 SLOVENIAN P     USTA
  099 42 Slovenian       VUJSTA
  099 89 SLOVAK P        USTA
  099 46 Slovak          USTA
  099 92 SERBOCROATIAN P USTA
  099 54 Serbocroatian   USTA
  099 88 POLISH P        USTA
  099 50 Polish          USTA
  099 93 MACEDONIAN P    USTA
  099 44 Lusatian U      WUSTA
  099 43 Lusatian L      HUSTA
  099 90 CZECH P         USTA
  099 45 Czech           USTA
  099 94 BULGARIAN P     USTA
  099 52 Macedonian      USTA
  099 53 Bulgarian       USTA
b                      201
c                         200  2  201
c                         201  2  202
  099 57 Kashmiri        MOKH, OS
b                      202
c                         201  2  202
  099 64 Nepali List     MUKH
  099 59 Gujarati        MOH, MOHRU
  099 63 Bengali         MUK
  099 62 Hindi           MUKH
  099 65 Khaskura        MUKH
  099 55 Gypsy Gk        MUI
  099 61 Lahnda          MU
  099 60 Panjabi ST      MU
  099 41 Latvian         MUTE
  099 25 Penn. Dutch     MAUL
  099 29 Frisian         HAPPERT, MULWIRK, SNAPPERT
b                      203
c                         203  3  400
  099 77 Tadzik          DAXAN
  099 76 Persian List    DAHAN
b                      400
c                         203  3  400
  099 78 Baluchi         DAF
  099 73 Ossetic         DZYX, KOM
b                      204
c                         204  2  205
  099 07 Breton ST       GENOU
b                      205
c                         204  2  205
c                         205  3  206
  099 05 Breton List     GENOU, BEG
  099 06 Breton SE       GENEU, BEG
b                      206
c                         205  3  206
  099 03 Welsh N         CEG
  099 04 Welsh C         CEG
a 100 NAME
b                      001
  100 55 Gypsy Gk        ALAV
  100 76 Persian List    ESM
b                      002
  100 41 Latvian         VARDS
  100 39 Lithuanian O    VARDAS
  100 40 Lithuanian ST   VARDAS
b                      003
  100 30 Swedish Up      NAMN
  100 31 Swedish VL      NAMN
  100 46 Slovak          MENO
  100 89 SLOVAK P        MENO
  100 42 Slovenian       IMJ
  100 91 SLOVENIAN P     IME
  100 86 UKRAINIAN P     IM A
  100 15 French Creole C NO
  100 73 Ossetic         NOM
  100 17 Sardinian N     NUMENE
  100 18 Sardinian L     NOMENE
  100 09 Vlach           NUME
  100 92 SERBOCROATIAN P IME
  100 54 Serbocroatian   IME
  100 85 RUSSIAN P       IM A
  100 51 Russian         IMJA
  100 88 POLISH P        IMIE
  100 50 Polish          IMIE
  100 93 MACEDONIAN P    IME
  100 44 Lusatian U      MJENO
  100 43 Lusatian L      ME
  100 90 CZECH P         JMENO
  100 45 Czech           JMENO
  100 87 BYELORUSSIAN P  IM A
  100 94 BULGARIAN P     IME
  100 69 Greek D         ONOMA
  100 67 Greek MD        ONOMA
  100 70 Greek K         ONOMA
  100 66 Greek ML        ONOMA
  100 68 Greek Mod       ONOMA
  100 56 Singhalese      NAMA
  100 57 Kashmiri        NAV
  100 64 Nepali List     NAU
  100 61 Lahnda          NA
  100 79 Wakhi           NONG
  100 78 Baluchi         NAM
  100 74 Afghan          NUM
  100 08 Rumanian List   NUME
  100 11 Ladin           NOM
  100 19 Sardinian C     NOMINI
  100 10 Italian         NOME
  100 23 Catalan         NOM
  100 20 Spanish         NOMBRE
  100 12 Provencal       NOUM
  100 14 Walloon         NOM, NON
  100 16 French Creole D NO
  100 13 French          NOM
  100 02 Irish B         AINM
  100 01 Irish A         AINM
  100 03 Welsh N         ENW
  100 04 Welsh C         ENW
  100 05 Breton List     HANO, HANV
  100 06 Breton SE       HANU
  100 07 Breton ST       ANV
  100 24 German ST       NAME
  100 35 Icelandic ST    NAFN
  100 34 Riksmal         NAVN
  100 32 Swedish List    NAMN
  100 33 Danish          NAVN
  100 36 Faroese         NAVN
  100 29 Frisian         NAMME
  100 28 Flemish         NAEM
  100 25 Penn. Dutch     NAWME
  100 26 Dutch List      NAAM
  100 27 Afrikaans       NAAM
  100 80 Albanian T      EMER
  100 83 Albanian K      EMER
  100 81 Albanian Top    EMER
  100 84 Albanian C      EMBER
  100 82 Albanian G      EMEN
  100 52 Macedonian      IME
  100 59 Gujarati        NAM
  100 95 ALBANIAN        EMEN
  100 58 Marathi         NAV
  100 63 Bengali         NAM
  100 62 Hindi           NAM
  100 60 Panjabi ST      NA
  100 65 Khaskura        NAM, NAUN
  100 71 Armenian Mod    ANUN
  100 47 Czech E         MENO
  100 49 Byelorussian    IMJA, PROZ'VIMCA
  100 48 Ukrainian       IM'JA
  100 53 Bulgarian       IME
  100 21 Portuguese ST   NOME
  100 22 Brazilian       NOME
  100 72 Armenian List   ANOON
  100 75 Waziri          NUM
  100 38 Takitaki        NEM
  100 37 English ST      NAME
  100 77 Tadzik          NOM, ISM
a 101 NARROW
b                      000
  101 72 Armenian List
b                      001
  101 56 Singhalese      PATU
  101 58 Marathi         ERUNDE
  101 71 Armenian Mod    NEL
  101 37 English ST      NARROW
b                      002
  101 04 Welsh C         CUL
  101 03 Welsh N         CUL
  101 01 Irish A         CAOL
b                      003
  101 81 Albanian Top    NGUSTE
  101 95 ALBANIAN        NGUSHT
  101 82 Albanian G      NGUSHT
  101 84 Albanian C      I-NGUST
  101 83 Albanian K      I NGUSTE
  101 80 Albanian T      I, E NGUSHTE
b                      004
  101 68 Greek Mod       STENOS
  101 66 Greek ML        STENOS
  101 70 Greek K         STENOS
  101 67 Greek MD        STENOS
  101 69 Greek D         STENOS
b                      200
c                         200  2  201
  101 13 French          ETROIT
  101 16 French Creole D ETWET
  101 14 Walloon         STREUT
  101 12 Provencal       ESTRE, ECHO
  101 23 Catalan         ESTRET
  101 10 Italian         STRETTO
  101 19 Sardinian C     STRINTU
  101 11 Ladin           STRET
  101 22 Brazilian       ESTREITO
  101 21 Portuguese ST   APERTADO, ESTREITO
  101 15 French Creole C ETHWET
  101 09 Vlach           STRIMTU
  101 17 Sardinian N     ASTRINTU
  101 18 Sardinian L     ISTRINTU
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  2  205
c                         201  2  207
c                         201  2  209
c                         201  3  211
  101 20 Spanish         ANGOSTO, ESTRECHO
  101 08 Rumanian List   INGUST, STRIMT
b                      202
c                         201  2  202
c                         202  2  203
c                         202  2  205
c                         202  2  207
c                         202  2  209
c                         202  3  211
  101 54 Serbocroatian   UZAK
  101 92 SERBOCROATIAN P UZAK
  101 46 Slovak          UZKY
  101 89 SLOVAK P        UZKY
  101 87 BYELORUSSIAN P  VUZKI
  101 45 Czech           UZKY
  101 90 CZECH P         UZKY
  101 43 Lusatian L      HUZKI
  101 44 Lusatian U      WUZKY
  101 48 Ukrainian       VUZ'KYJ
  101 49 Byelorussian    VUZKI, VUZKA
  101 47 Czech E         USKO
  101 91 SLOVENIAN P     OZEK
  101 86 UKRAINIAN P     VUZ KYJ
  101 50 Polish          WAZKI
  101 88 POLISH P        WASKI
  101 51 Russian         UZKIJ
  101 85 RUSSIAN P       UZKIJ
  101 02 Irish B         CUMHANG
  101 24 German ST       ENG
  101 25 Penn. Dutch     ENG
b                      203
c                         201  2  203
c                         202  2  203
c                         203  2  204
c                         203  2  205
c                         203  2  207
c                         203  2  209
c                         203  3  211
  101 42 Slovenian       TESEN, VASKO
b                      204
c                         203  2  204
  101 93 MACEDONIAN P    TESEN
  101 94 BULGARIAN P     TESEN
  101 53 Bulgarian       TESNO
  101 52 Macedonian      TESEN
b                      205
c                         201  2  205
c                         202  2  205
c                         203  2  205
c                         205  2  206
c                         205  2  207
c                         205  2  209
c                         205  3  211
  101 05 Breton List     ENK, STRIZ, MOAN
b                      206
c                         205  2  206
  101 07 Breton ST       STRIZH
  101 06 Breton SE       STREH
b                      207
c                         201  2  207
c                         202  2  207
c                         203  2  207
c                         205  2  207
c                         207  2  208
c                         207  2  209
c                         207  3  211
  101 27 Afrikaans       NOU, ENG
  101 26 Dutch List      NAUW, ENG
b                      208
c                         207  2  208
  101 28 Flemish         NAAUW
  101 29 Frisian         NAU
b                      209
c                         201  2  209
c                         202  2  209
c                         203  2  209
c                         205  2  209
c                         207  2  209
c                         209  2  210
c                         209  3  211
  101 40 Lithuanian ST   SIAURAS, ANKSTAS
b                      210
c                         209  2  210
  101 39 Lithuanian O    SIAURAS
  101 41 Latvian         SAURS
b                      211
c                         201  3  211
c                         202  3  211
c                         203  3  211
c                         205  3  211
c                         207  3  211
c                         209  3  211
  101 73 Ossetic         UYNGAEG
b                      212
c                         212  3  213
c                         212  2  214
c                         212  3  216
  101 75 Waziri          TANG
  101 55 Gypsy Gk        TANK
  101 74 Afghan          TANG
  101 78 Baluchi         TANKH
b                      213
c                         212  3  213
c                         213  3  214
c                         213  2  216
  101 61 Lahnda          TEG
  101 57 Kashmiri        TANG
  101 60 Panjabi ST      PIRA, TENG
b                      214
c                         212  2  214
c                         213  3  214
c                         214  2  215
c                         214  3  216
  101 79 Wakhi           TUNG, BIRIK
  101 77 Tadzik          TANG, BORIK, KAMBAR
b                      215
c                         214  2  215
  101 76 Persian List    BARIK
b                      216
c                         212  3  216
c                         213  2  216
c                         214  3  216
c                         216  2  217
  101 62 Hindi           SEKRA, TENG
b                      217
c                         216  2  217
  101 59 Gujarati        SAKRU
  101 63 Bengali         SORU
  101 64 Nepali List     SAGURO
  101 65 Khaskura        SANGURO
b                      218
c                         218  2  219
  101 34 Riksmal         SMAL
  101 33 Danish          SMAL
  101 38 Takitaki        SMALA, PIKIN
b                      219
c                         218  2  219
c                         219  2  220
  101 30 Swedish Up      TRANG, SMAL
  101 31 Swedish VL      TRANG  TRONG, SMAL  SMAL
  101 32 Swedish List    TRANG, SMAL
b                      220
c                         219  2  220
  101 36 Faroese         TRONGUR
  101 35 Icelandic ST    THRONGUR, MJOR
a 102 NEAR
b                      001
  102 19 Sardinian C     AKKANTA
  102 17 Sardinian N     AKKURTHU
  102 11 Ladin           ARDAINT, STRUSCH
  102 18 Sardinian L     BIGHINU
  102 20 Spanish         CERCA, JUNTO
  102 21 Portuguese ST   CHEGADO
  102 70 Greek K         EGGUS
  102 58 Marathi         JEVEL
  102 63 Bengali         KACE
  102 38 Takitaki        KLOSIBEI
  102 61 Lahnda          KOL
  102 56 Singhalese      LANGA
  102 22 Brazilian       PERTO
  102 41 Latvian         TUVU
  102 10 Italian         VICINO
  102 73 Ossetic         XAESTAEG
b                      002
  102 92 SERBOCROATIAN P BLIZAK
  102 46 Slovak          BLIZKY
  102 89 SLOVAK P        BLIZKY
  102 42 Slovenian       BLIZII
  102 91 SLOVENIAN P     BLIZEK
  102 86 UKRAINIAN P     BLYZ KYJ
  102 93 MACEDONIAN P    BLIZOK
  102 50 Polish          BLIZKO
  102 88 POLISH P        BLISKI
  102 51 Russian         BLIZKO
  102 85 RUSSIAN P       BLIZKIJ
  102 54 Serbocroatian   BLIZU
  102 45 Czech           BLIZKY
  102 90 CZECH P         BLIZKY
  102 43 Lusatian L      BLIZKI
  102 44 Lusatian U      BLIZKI
  102 94 BULGARIAN P     BLIZUK
  102 87 BYELORUSSIAN P  BLIZKI
  102 52 Macedonian      BLIZOK/NABLIZU
  102 47 Czech E         BLISKO
  102 49 Byelorussian    BLIZKI, BLIZKA
  102 48 Ukrainian       BILJA, KOLO, BLYZ'KO
  102 53 Bulgarian       BLIZKO
b                      003
  102 04 Welsh C         AGOS
  102 03 Welsh N         AGOS, YMYL
b                      004
  102 13 French          PRES
  102 14 Walloon         PRES
  102 16 French Creole D PWE
  102 15 French Creole C PWE
b                      005
  102 12 Provencal       PROCHE
  102 08 Rumanian List   APROPIAT
  102 09 Vlach           APREEPE
  102 23 Catalan         TANCA, A PROP
b                      006
  102 55 Gypsy Gk        PASE
  102 59 Gujarati        PASE
  102 62 Hindi           PAS
b                      007
  102 71 Armenian Mod    MOTIK
  102 72 Armenian List   MOD
b                      008
  102 01 Irish A         COMHGARACH, GAR
  102 02 Irish B         GAR
b                      009
  102 40 Lithuanian ST   ARTI
  102 39 Lithuanian O    ARTI, NETOLI
b                      010
  102 07 Breton ST       TOST
  102 06 Breton SE       TOST
  102 05 Breton List     TOST, NES, E-KICHEN
b                      011
  102 81 Albanian Top    AFER
  102 80 Albanian T      AFER
  102 82 Albanian G      AFER
  102 95 ALBANIAN        AFER, AFEREM
b                      012
  102 83 Albanian K      NDANE
  102 84 Albanian C      DANZ
b                      013
  102 69 Greek D         KONTA
  102 67 Greek MD        KONTA, SIMA
  102 68 Greek Mod       KONDA
  102 66 Greek ML        KONTA
b                      200
c                         200  2  201
c                         200  3  400
  102 37 English ST      NEAR
  102 30 Swedish Up      NARA
  102 31 Swedish VL      NAR
  102 24 German ST       NAHE
  102 35 Icelandic ST    NALAEGT
  102 34 Riksmal         NAER
  102 32 Swedish List    NARA
  102 33 Danish          NAER
  102 36 Faroese         NAR
  102 26 Dutch List      NABIJ
b                      201
c                         200  2  201
c                         201  2  202
c                         201  3  400
  102 27 Afrikaans       NABY, DIGBY
b                      202
c                         201  2  202
  102 28 Flemish         DICHT BY
b                      400
c                         200  3  400
c                         201  3  400
  102 25 Penn. Dutch     NAYKSCHT
  102 29 Frisian         NJONKE(N)
b                      203
c                         203  3  204
c                         203  3  206
  102 74 Afghan          NEZDE
  102 78 Baluchi         NAZI, NAZIKH
  102 79 Wakhi           QERIB, SIS, NEZD
  102 77 Tadzik          NAZDIK, KARIB
  102 76 Persian List    NAZDIK
  102 75 Waziri          NEZDE, TSARMA
b                      204
c                         203  3  204
c                         204  2  205
c                         204  3  206
  102 65 Khaskura        NIR, NAJIK
b                      205
c                         204  2  205
c                         205  3  206
  102 64 Nepali List     NIRA
  102 60 Panjabi ST      NERE
b                      206
c                         203  3  206
c                         204  3  206
c                         205  3  206
  102 57 Kashmiri        NISH
a 103 NECK
b                      000
  103 73 Ossetic
b                      001
  103 18 Sardinian L     ATTILE
  103 65 Khaskura        GHANTI
  103 60 Panjabi ST      GICCI
  103 84 Albanian C      KOC
  103 17 Sardinian N     THUKRU
  103 72 Armenian List   VIZ
  103 83 Albanian K      ZHERK (NAPE), GRIKE (THROAT)
b                      002
  103 22 Brazilian       PESCOCO
  103 21 Portuguese ST   PESCOCO
b                      003
  103 58 Marathi         MAN
  103 64 Nepali List     MANTO
  103 01 Irish A         MUINEAL
  103 02 Irish B         MUINEAL, -NIL
b                      004
  103 07 Breton ST       GOUZOUG
  103 06 Breton SE       GOUG
  103 05 Breton List     GOUZOUG, GOUG
  103 04 Welsh C         GWDDF
  103 03 Welsh N         GWDDF
b                      005
  103 68 Greek Mod       LEMOS
  103 66 Greek ML        LAIMOS
  103 70 Greek K         LAIMOS
  103 67 Greek MD        LAIMOS
  103 69 Greek D         LAIMOS
b                      006
  103 42 Slovenian       VRAT
  103 54 Serbocroatian   VRAT
  103 93 MACEDONIAN P    VRAT
  103 52 Macedonian      VRAT
  103 53 Bulgarian       BRAT
  103 79 Wakhi           GERDON, MAEYUK
  103 61 Lahnda          GERDEN
  103 77 Tadzik          GARDAN
  103 59 Gujarati        GELU, GERDEN
  103 76 Persian List    GARDAN
  103 75 Waziri          GHWORA, MAGHZAI, MA KANDAI
  103 74 Afghan          GARA
  103 78 Baluchi         GWAR
b                      100
  103 09 Vlach           GUSE
  103 08 Rumanian List   GIT
  103 19 Sardinian C     ZUGU
b                      200
c                         200  2  201
  103 50 Polish          SZYJA
  103 88 POLISH P        SZYJA
  103 51 Russian         SEJA
  103 85 RUSSIAN P       SEJA
  103 92 SERBOCROATIAN P SIJA
  103 89 SLOVAK P        SIJA
  103 91 SLOVENIAN P     SIJA
  103 86 UKRAINIAN P     SYJA
  103 90 CZECH P         SIJE
  103 43 Lusatian L      SYJA
  103 44 Lusatian U      SIJA
  103 94 BULGARIAN P     SIJA
  103 87 BYELORUSSIAN P  SYJA
  103 48 Ukrainian       SYJA
b                      201
c                         200  2  201
c                         201  2  202
c                         201  3  203
  103 45 Czech           KRK, SIJE
b                      202
c                         201  2  202
c                         202  3  203
  103 46 Slovak          KRK
  103 49 Byelorussian    KARAK
  103 47 Czech E         KRK
b                      203
c                         201  3  203
c                         202  3  203
  103 71 Armenian Mod    COCRAK
b                      204
c                         204  2  205
  103 37 English ST      NECK
  103 38 Takitaki        NEKI
b                      205
c                         204  2  205
c                         205  2  206
c                         205  3  207
c                         205  3  208
  103 24 German ST       HALS, NACKEN
  103 29 Frisian         HALS, NEKKE
  103 26 Dutch List      HALS, NEK
  103 27 Afrikaans       HALS, NEK
b                      206
c                         205  2  206
c                         206  3  207
c                         206  3  208
  103 30 Swedish Up      HALS
  103 31 Swedish VL      HAS  HALS
  103 25 Penn. Dutch     HOLSZ
  103 28 Flemish         HALS
  103 36 Faroese         HALSUR
  103 33 Danish          HALS
  103 32 Swedish List    HALS
  103 34 Riksmal         HALS
  103 35 Icelandic ST    HALS
  103 15 French Creole C KU
  103 13 French          COU
  103 16 French Creole D KU
  103 14 Walloon         CO
  103 12 Provencal       COU, COUI
  103 20 Spanish         CUELLO
  103 23 Catalan         COLL, CAMA, CUA
  103 10 Italian         COLLO
  103 11 Ladin           CULOZ
b                      207
c                         205  3  207
c                         206  3  207
c                         207  3  208
  103 40 Lithuanian ST   KAKLAS
  103 39 Lithuanian O    KAKLAS
  103 41 Latvian         KAKLS
b                      208
c                         205  3  208
c                         206  3  208
c                         207  3  208
  103 82 Albanian G      KJAFA
  103 95 ALBANIAN        KJAFA
  103 80 Albanian T      GAFE
  103 81 Albanian Top    KAFE
b                      209
c                         209  3  210
  103 55 Gypsy Gk        KHOR
  103 57 Kashmiri        KORU
  103 56 Singhalese      KARA
b                      210
c                         209  3  210
c                         210  2  211
  103 63 Bengali         GHAR, GORDAN
b                      211
c                         210  2  211
  103 62 Hindi           GERDEN
a 104 NEW
b                      001
  104 41 Latvian         JAUNS
b                      002
  104 67 Greek MD        KAINOURGIOS
  104 69 Greek D         KAINOURGIOS
  104 68 Greek Mod       KENURYOS
  104 66 Greek ML        KAINOURGIOS
b                      003
  104 82 Albanian G      RI
  104 95 ALBANIAN        IRI
  104 81 Albanian Top    I-IRI (PL. TERIN)
  104 80 Albanian T      I, E RI
  104 83 Albanian K      I RII
  104 84 Albanian C      I-RI
b                      200
c                         200  2  201
  104 70 Greek K         NEOS
  104 09 Vlach           NAWE
  104 55 Gypsy Gk        NEVO
  104 30 Swedish Up      NY
  104 31 Swedish VL      NY
  104 40 Lithuanian ST   NAUJAS
  104 39 Lithuanian O    NAUJAS
  104 94 BULGARIAN P     NOV
  104 87 BYELORUSSIAN P  NOVY
  104 45 Czech           NOVY
  104 90 CZECH P         NOVY
  104 43 Lusatian L      NOWY
  104 44 Lusatian U      NOWY
  104 93 MACEDONIAN P    NOV
  104 50 Polish          NOWY
  104 88 POLISH P        NOWY
  104 51 Russian         NOVYJ
  104 85 RUSSIAN P       NOVYJ
  104 54 Serbocroatian   NOV
  104 92 SERBOCROATIAN P NOV
  104 46 Slovak          NOVY
  104 89 SLOVAK P        NOVY
  104 42 Slovenian       NOVA
  104 91 SLOVENIAN P     NOV
  104 86 UKRAINIAN P     NOVYJ
  104 15 French Creole C NUVO
  104 73 Ossetic         NAEUAEG
  104 17 Sardinian N     NOVU
  104 18 Sardinian L     NOU
  104 57 Kashmiri        NOWU
  104 61 Lahnda          NEWA
  104 27 Afrikaans       NUWE
  104 26 Dutch List      NIEUW
  104 25 Penn. Dutch     NEI
  104 28 Flemish         NIEUW
  104 29 Frisian         NIJ
  104 36 Faroese         NYGGJUR
  104 33 Danish          NY
  104 32 Swedish List    NY
  104 34 Riksmal         NY
  104 35 Icelandic ST    NYR
  104 24 German ST       NEU
  104 07 Breton ST       NEVEZ
  104 06 Breton SE       NEUE
  104 05 Breton List     NEVEZ
  104 04 Welsh C         NEWYDD
  104 03 Welsh N         NEWYDD
  104 01 Irish A         NUA
  104 02 Irish B         NUADH
  104 13 French          NOUVEAU
  104 16 French Creole D NUVO
  104 14 Walloon         NOVE
  104 12 Provencal       NOUVEU
  104 20 Spanish         NUEVO
  104 23 Catalan         NOU
  104 10 Italian         NUOVO
  104 19 Sardinian C     NOU
  104 11 Ladin           NOUV, NOV
  104 08 Rumanian List   NOU
  104 74 Afghan          NEVAJ
  104 52 Macedonian      NOB
  104 59 Gujarati        NEWU
  104 58 Marathi         NEVIN
  104 60 Panjabi ST      NEVA
  104 37 English ST      NEW
  104 38 Takitaki        NJOE
  104 75 Waziri          NEWAI
  104 72 Armenian List   NOR
  104 22 Brazilian       NOVO
  104 21 Portuguese ST   NOVO
  104 53 Bulgarian       NOVO
  104 48 Ukrainian       NOVYJ - A - E
  104 49 Byelorussian    NOVY, NOVA
  104 47 Czech E         NOVE
  104 71 Armenian Mod    NOR
  104 78 Baluchi         NOKH
  104 63 Bengali         NOTUN, NOEA
  104 56 Singhalese      NAVA, ALUT
  104 64 Nepali List     NAULO, NAYA
  104 62 Hindi           NEYA
  104 65 Khaskura        NAYA, NAULA
b                      201
c                         200  2  201
c                         201  2  202
  104 77 Tadzik          NAV, TOZA, NAVBAROMAD
b                      202
c                         201  2  202
  104 76 Persian List    TAZE
  104 79 Wakhi           SEGHD, TOZA
a 105 NIGHT
b                      002
  105 74 Afghan          SPA
  105 77 Tadzik          SAB
  105 76 Persian List    SHAB
  105 75 Waziri          SHPA
  105 73 Ossetic         AEXCAEV
  105 78 Baluchi         SHAF
b                      003
  105 65 Khaskura        RAT
  105 60 Panjabi ST      RAT, RAT
  105 62 Hindi           RAT
  105 63 Bengali         RAT
  105 58 Marathi         RATRE
  105 55 Gypsy Gk        RAKI  RAT
  105 61 Lahnda          RAT
  105 64 Nepali List     RAT
  105 57 Kashmiri        RATH
  105 56 Singhalese      RA
  105 59 Gujarati        RAT, RATU
b                      004
  105 68 Greek Mod       NIKHTA
  105 66 Greek ML        NUCHTA
  105 70 Greek K         NUKS
  105 67 Greek MD        NUCHTA
  105 69 Greek D         NUCHTA
  105 40 Lithuanian ST   NAKTIS
  105 39 Lithuanian O    NAKTIS
  105 41 Latvian         NAKTS
  105 94 BULGARIAN P     NOST
  105 87 BYELORUSSIAN P  NOC
  105 45 Czech           NOC
  105 90 CZECH P         NOC
  105 43 Lusatian L      NOC
  105 44 Lusatian U      NOC
  105 93 MACEDONIAN P    NOK
  105 50 Polish          NOC
  105 88 POLISH P        NOC
  105 51 Russian         NOC
  105 85 RUSSIAN P       NOC
  105 54 Serbocroatian   NOC
  105 92 SERBOCROATIAN P NOC
  105 46 Slovak          NOC
  105 89 SLOVAK P        NOC
  105 42 Slovenian       NOC
  105 91 SLOVENIAN P     NOC
  105 86 UKRAINIAN P     NIC
  105 15 French Creole C LANWIT
  105 17 Sardinian N     NOTTE
  105 18 Sardinian L     NOTTE
  105 81 Albanian Top    NATE
  105 09 Vlach           NWAPTE
  105 30 Swedish Up      NATT
  105 31 Swedish VL      NAT
  105 79 Wakhi           NUGHD
  105 82 Albanian G      NATA
  105 84 Albanian C      NAT
  105 83 Albanian K      NATE
  105 80 Albanian T      NATE
  105 27 Afrikaans       NAG, AAND
  105 26 Dutch List      NACHT
  105 25 Penn. Dutch     NAACHT
  105 28 Flemish         NACHT
  105 29 Frisian         JOUN, NACHT
  105 36 Faroese         NATT
  105 33 Danish          NAT
  105 32 Swedish List    NATT
  105 34 Riksmal         NATT
  105 35 Icelandic ST    NOTT
  105 24 German ST       NACHT
  105 07 Breton ST       NOZ
  105 06 Breton SE       NOZ
  105 05 Breton List     NOZ
  105 04 Welsh C         NOS
  105 03 Welsh N         NOS
  105 13 French          NUIT
  105 16 French Creole D LENWIT
  105 14 Walloon         NUT'
  105 12 Provencal       NUE, NIUE
  105 20 Spanish         NOCHE
  105 23 Catalan         NIT
  105 10 Italian         NOTTE
  105 19 Sardinian C     NOTTI
  105 11 Ladin           NOT, NOAT
  105 08 Rumanian List   NOAPTE
  105 52 Macedonian      NOK
  105 95 ALBANIAN        NATA
  105 22 Brazilian       NOITE
  105 21 Portuguese ST   NOITE
  105 53 Bulgarian       NOSC
  105 48 Ukrainian       NIC
  105 49 Byelorussian    NOC
  105 47 Czech E         NOC
  105 38 Takitaki        NETI
  105 37 English ST      NIGHT
b                      005
  105 71 Armenian Mod    GISER
  105 72 Armenian List   KISHER
b                      006
  105 01 Irish A         OIDHCHE
  105 02 Irish B         OIDHEHE
a 106 NOSE
b                      001
  106 41 Latvian         DEGUNS
  106 79 Wakhi           MIS
  106 35 Icelandic ST    NEF
  106 70 Greek K         REN
b                      002
  106 04 Welsh C         TRWYN
  106 03 Welsh N         TRWYN
b                      003
  106 72 Armenian List   KIT
  106 71 Armenian Mod    K`IT`
b                      004
  106 76 Persian List    DAMAGH
  106 77 Tadzik          BINI, FUK, TUMSUK, DIMOW, NUL
b                      005
  106 30 Swedish Up      NASA
  106 31 Swedish VL      NASA
  106 94 BULGARIAN P     NOS
  106 87 BYELORUSSIAN P  NOS
  106 45 Czech           NOS
  106 90 CZECH P         NOS
  106 43 Lusatian L      NOS
  106 44 Lusatian U      NOS
  106 93 MACEDONIAN P    NOS
  106 50 Polish          NOS
  106 88 POLISH P        NOS
  106 51 Russian         NOS
  106 85 RUSSIAN P       NOS
  106 54 Serbocroatian   NOS
  106 92 SERBOCROATIAN P NOS
  106 46 Slovak          NOS
  106 89 SLOVAK P        NOS
  106 42 Slovenian       NUS
  106 91 SLOVENIAN P     NOS
  106 86 UKRAINIAN P     NIS
  106 40 Lithuanian ST   NOSIS
  106 39 Lithuanian O    NOSIS
  106 24 German ST       NASE
  106 27 Afrikaans       NEUS
  106 26 Dutch List      NEUS
  106 25 Penn. Dutch     NAWSZ
  106 28 Flemish         NEUS
  106 29 Frisian         NOAS
  106 36 Faroese         NOS
  106 33 Danish          NAESE
  106 32 Swedish List    NASA, NOS
  106 34 Riksmal         NESE
  106 52 Macedonian      NOS
  106 53 Bulgarian       NOS
  106 48 Ukrainian       NIS
  106 49 Byelorussian    NOS
  106 47 Czech E         NOS
  106 37 English ST      NOSE
  106 38 Takitaki        NOSO
  106 09 Vlach           NARE
  106 17 Sardinian N     NARE
  106 20 Spanish         NARIZ
  106 22 Brazilian       NARIZ
  106 21 Portuguese ST   NARIZ
  106 18 Sardinian L     NASU
  106 15 French Creole C NE
  106 23 Catalan         NAS
  106 10 Italian         NASO
  106 19 Sardinian C     NASU
  106 11 Ladin           NES
  106 08 Rumanian List   NAS
  106 13 French          NEZ
  106 16 French Creole D NE
  106 14 Walloon         NE, NEZ
  106 12 Provencal       NAS
  106 57 Kashmiri        NAST
  106 62 Hindi           NAK
  106 63 Bengali         NAK
  106 58 Marathi         NAK
  106 60 Panjabi ST      NEKK
  106 65 Khaskura        NAK
  106 59 Gujarati        NAK
  106 56 Singhalese      NAHAYA
  106 55 Gypsy Gk        NAK
  106 61 Lahnda          NEK
  106 64 Nepali List     NAK
b                      006
  106 67 Greek MD        MUTE
  106 69 Greek D         MUTI
  106 68 Greek Mod       MITI
  106 66 Greek ML        MUTE
b                      007
  106 78 Baluchi         PHONZ
  106 73 Ossetic         FYNDZ
b                      008
  106 80 Albanian T      HUNDE
  106 81 Albanian Top    UNDE
  106 95 ALBANIAN        HUNDA
  106 82 Albanian G      HUNDA
  106 84 Albanian C      XUND
  106 83 Albanian K      XUNDE
b                      009
  106 74 Afghan          PAZA
  106 75 Waziri          PEZA, WARBIZ, WARSAK
b                      010
  106 07 Breton ST       FRI
  106 06 Breton SE       FRI
  106 05 Breton List     FRI
  106 01 Irish A         SRON
  106 02 Irish B         SRON
a 107 NOT
b                      000
  107 03 Welsh N
  107 65 Khaskura
b                      001
  107 05 Breton List     NAMM, NAREN
b                      002
  107 15 French Creole C PA
  107 16 French Creole D PE
b                      003
  107 66 Greek ML        DEN
  107 70 Greek K         ME, DEN
  107 67 Greek MD        DE, OCHI
  107 69 Greek D         ME, DEN
  107 68 Greek Mod       MIN, DHEN, OCHI
b                      004
  107 71 Armenian Mod    OC`
  107 72 Armenian List   VOCH
b                      005
  107 53 Bulgarian       NE
  107 48 Ukrainian       NE
  107 49 Byelorussian    NE
  107 47 Czech E         NE
  107 52 Macedonian      NE
  107 40 Lithuanian ST   NE- (PREFIX)
  107 39 Lithuanian O    NE
  107 41 Latvian         NE
  107 94 BULGARIAN P     NE
  107 87 BYELORUSSIAN P  NE
  107 45 Czech           NE
  107 90 CZECH P         NE
  107 43 Lusatian L      NE
  107 44 Lusatian U      NE
  107 93 MACEDONIAN P    NE
  107 50 Polish          NIE
  107 88 POLISH P        NIE
  107 51 Russian         NE
  107 85 RUSSIAN P       NE
  107 54 Serbocroatian   NE
  107 92 SERBOCROATIAN P NE
  107 46 Slovak          NIE
  107 89 SLOVAK P        NIE
  107 42 Slovenian       NJE
  107 91 SLOVENIAN P     NE
  107 86 UKRAINIAN P     NE
  107 55 Gypsy Gk        IN, NI
  107 61 Lahnda          NE, NI
  107 64 Nepali List     NA
  107 57 Kashmiri        NA
  107 56 Singhalese      NAHA
  107 59 Gujarati        NEHI
  107 60 Panjabi ST      NEI, NA
  107 62 Hindi           NA, NEHI
  107 63 Bengali         NA
  107 58 Marathi         NE, NAHI
  107 76 Persian List    NA
  107 77 Tadzik          NA, NE
  107 74 Afghan          NA
  107 78 Baluchi         NA, N
  107 79 Wakhi           NE
  107 73 Ossetic         NAE
  107 75 Waziri          NA
  107 07 Breton ST       NE...KET
  107 06 Breton SE       NE...KET
  107 01 Irish A         NI
  107 02 Irish B         NI
  107 04 Welsh C         NID
  107 29 Frisian         NE
  107 27 Afrikaans       NIE
  107 25 Penn. Dutch     NET
  107 28 Flemish         NIET
  107 26 Dutch List      NIET
  107 24 German ST       NICHT
  107 37 English ST      NOT
  107 13 French          NON
  107 14 Walloon         NENI
  107 12 Provencal       NOUN, NANI
  107 20 Spanish         NO
  107 23 Catalan         NO
  107 10 Italian         NO, NON
  107 19 Sardinian C     NO
  107 11 Ladin           NA, NOAT, NUN
  107 08 Rumanian List   NU
  107 22 Brazilian       NAO
  107 21 Portuguese ST   NAO, NEM
  107 18 Sardinian L     NON
  107 09 Vlach           NU
  107 17 Sardinian N     NO
  107 38 Takitaki        NO
  107 81 Albanian Top    JO, NUK, MOS
  107 82 Albanian G      NUK
  107 84 Albanian C      NG
  107 83 Albanian K      JOO (PRED. NEG.), NUKU  S(+VERB), MOS (MODAL), PAA'UN
  107 95 ALBANIAN        NUK
  107 80 Albanian T      NUK
b                      200
c                         200  2  201
  107 36 Faroese         IKKI
  107 33 Danish          IKKE
  107 34 Riksmal         IKKE
  107 35 Icelandic ST    EKKI
b                      201
c                         200  2  201
c                         201  2  202
  107 32 Swedish List    ICKE, EJ, INTE
b                      202
c                         201  2  202
  107 30 Swedish Up      INTE
  107 31 Swedish VL      INTA, INT, IT
a 108 OLD
b                      001
  108 79 Wakhi           KONA, XAEIYAR
  108 58 Marathi         MHATARA (ANIMATE), JUNA (INANIMATE)
  108 56 Singhalese      NAKI
b                      002
  108 92 SERBOCROATIAN P STAR
  108 46 Slovak          STARY
  108 89 SLOVAK P        STARY
  108 42 Slovenian       STAR, STARA, STARII
  108 91 SLOVENIAN P     STAR
  108 86 UKRAINIAN P     STARYJ
  108 50 Polish          STARY
  108 88 POLISH P        STARY
  108 51 Russian         STARYJ
  108 85 RUSSIAN P       STARYJ
  108 54 Serbocroatian   STAR
  108 87 BYELORUSSIAN P  STARY
  108 45 Czech           STARY
  108 90 CZECH P         STARY
  108 43 Lusatian L      STARY
  108 44 Lusatian U      STARY
  108 93 MACEDONIAN P    STAR
  108 94 BULGARIAN P     STAR
  108 52 Macedonian      VETOV, STAR
  108 49 Byelorussian    STARY
  108 47 Czech E         STARE
  108 48 Ukrainian       STARYJ
  108 53 Bulgarian       STARO
b                      003
  108 55 Gypsy Gk        PHURO
  108 78 Baluchi         PHIR
  108 77 Tadzik          PIR, KUXANSOL
  108 76 Persian List    PIR
b                      004
  108 30 Swedish Up      GAMMAL
  108 31 Swedish VL      GAMAL
  108 35 Icelandic ST    GAMALL
  108 34 Riksmal         GAMMEL
  108 32 Swedish List    GAMMAL
  108 33 Danish          GAMMEL
  108 36 Faroese         GAMAL(UR)
b                      005
  108 73 Ossetic         ZAEROND
  108 74 Afghan          ZOR
  108 75 Waziri          ZOR
b                      006
  108 24 German ST       ALT
  108 29 Frisian         ALD
  108 28 Flemish         OUD
  108 25 Penn. Dutch     ALT
  108 26 Dutch List      OUD
  108 27 Afrikaans       OUD, OU
  108 38 Takitaki        OUROE
  108 37 English ST      OLD
b                      007
  108 05 Breton List     KOZ, HIR-HOALET
  108 06 Breton SE       KOH
  108 07 Breton ST       KOZH
b                      008
  108 04 Welsh C         HEN
  108 03 Welsh N         HEN
  108 39 Lithuanian O    SENAS
  108 40 Lithuanian ST   SENAS
  108 71 Armenian Mod    HIN
  108 72 Armenian List   HIN
  108 02 Irish B         SEAN, AOSTA, ARSA(CH), DIBHEALL
  108 01 Irish A         SEAN, AOSTA
b                      009
  108 81 Albanian Top    VJETER
  108 83 Albanian K      I-VJETERE
  108 84 Albanian C      I-VJETR
  108 82 Albanian G      VJETER
  108 95 ALBANIAN        VJETER
  108 80 Albanian T      I, E YETER, PLAK
b                      010
  108 09 Vlach           VYEKLU
  108 18 Sardinian L     BEZZU
  108 17 Sardinian N     VETHTHU
  108 15 French Creole C VYE
  108 41 Latvian         VECS
  108 08 Rumanian List   BATRIN, VECHI
  108 11 Ladin           VEGL
  108 19 Sardinian C     BECCU
  108 10 Italian         VECCHIO
  108 16 French Creole D VYE
  108 14 Walloon         VI
  108 12 Provencal       VIEI, VIEIO
  108 20 Spanish         VIEJO
  108 23 Catalan         VELL, ANCIA, JAYO
  108 13 French          VIEUX
  108 21 Portuguese ST   VELHO
  108 22 Brazilian       VELHO
b                      200
c                         200  2  201
  108 60 Panjabi ST      PERANA
b                      201
c                         200  2  201
c                         201  2  202
  108 62 Hindi           BURHA (ANIMATE), PURANA (INANIMATE)
  108 63 Bengali         BURO (ANIMATE), PURONO (INANIMATE)
b                      202
c                         201  2  202
  108 65 Khaskura        BURO
  108 57 Kashmiri        BUDA
  108 64 Nepali List     BURO
  108 61 Lahnda          BUDDHA
  108 59 Gujarati        BUDDHU, GHERERU, JUNU
b                      203
c                         203  2  204
  108 67 Greek MD        GEROS
b                      204
c                         203  2  204
c                         204  2  205
  108 68 Greek Mod       PALYOS, YEROS
b                      205
c                         204  2  205
  108 69 Greek D         PALEOS
  108 70 Greek K         PALAIOS
  108 66 Greek ML        PALEOS
a 109 ONE
b                      000
  109 29 Frisian
b                      002
  109 71 Armenian Mod    MEK, MI
  109 72 Armenian List   MEG
  109 68 Greek Mod       ENAS
  109 66 Greek ML        HENA
  109 70 Greek K         HEIS, MIA, HEN
  109 67 Greek MD        HENA
  109 69 Greek D         HENAS, MIA, HENA
b                      200
c                         200  3  201
c                         200  3  202
  109 09 Vlach           UNE
  109 30 Swedish Up      EN
  109 31 Swedish VL      EN
  109 18 Sardinian L     UNU
  109 17 Sardinian N     UNU
  109 15 French Creole C YO
  109 41 Latvian         VIENS
  109 39 Lithuanian O    VIENAS
  109 40 Lithuanian ST   NIENAS, VIENERI (COLL.)
  109 08 Rumanian List   UN
  109 11 Ladin           UN
  109 19 Sardinian C     UNU
  109 10 Italian         UNO
  109 23 Catalan         UN, HU
  109 20 Spanish         UN
  109 12 Provencal       UN, UNO
  109 14 Walloon         ON (BEFORE CONSONANT), IN (BEFORE VOWEL)
  109 16 French Creole D YO
  109 13 French          UN
  109 02 Irish B         AON
  109 01 Irish A         AON, CEANN
  109 03 Welsh N         UN
  109 04 Welsh C         UN
  109 05 Breton List     UNAN, EUN, EUR, EUL
  109 06 Breton SE       UNAN
  109 07 Breton ST       UNAN
  109 24 German ST       EIN
  109 35 Icelandic ST    EINN
  109 34 Riksmal         EN
  109 32 Swedish List    EN
  109 33 Danish          EN
  109 36 Faroese         EIN
  109 28 Flemish         EEN
  109 25 Penn. Dutch     AYNS, AYNER
  109 26 Dutch List      EEN
  109 27 Afrikaans       EEN
  109 21 Portuguese ST   UM, UNO
  109 22 Brazilian       UM
  109 38 Takitaki        WAN
  109 37 English ST      ONE
  109 86 UKRAINIAN P     ODYN
  109 91 SLOVENIAN P     EDEN
  109 42 Slovenian       ADEN
  109 89 SLOVAK P        JEDEN
  109 46 Slovak          JEDEN
  109 92 SERBOCROATIAN P JEDAN
  109 54 Serbocroatian   JEDAN
  109 85 RUSSIAN P       ODIN
  109 51 Russian         ODIN
  109 88 POLISH P        JEDEN
  109 50 Polish          JEDEN
  109 93 MACEDONIAN P    EDEN
  109 44 Lusatian U      JEDYN
  109 43 Lusatian L      JADEN
  109 90 CZECH P         JEDEN
  109 45 Czech           JEDEN
  109 87 BYELORUSSIAN P  ADZIN
  109 94 BULGARIAN P     EDIN
  109 52 Macedonian      EDEN
  109 47 Czech E         YEDEN
  109 49 Byelorussian    ADZIN
  109 48 Ukrainian       ODYN
  109 53 Bulgarian       EDNO
  109 55 Gypsy Gk        YEK
  109 56 Singhalese      EKA
  109 64 Nepali List     EK
  109 57 Kashmiri        OKU, AKH
  109 61 Lahnda          HIK
  109 78 Baluchi         YAK, YA
  109 74 Afghan          JAV
  109 77 Tadzik          JAK
  109 59 Gujarati        EK
  109 76 Persian List    YEK
  109 58 Marathi         EK
  109 63 Bengali         EK
  109 62 Hindi           EK
  109 60 Panjabi ST      IKK
  109 79 Wakhi           YI, I, YIU
  109 73 Ossetic         IU, IUNAEG
  109 75 Waziri          YO
b                      201
c                         200  3  201
c                         201  3  202
  109 65 Khaskura        YOTA
b                      202
c                         200  3  202
c                         201  3  202
  109 81 Albanian Top    NE
  109 80 Albanian T      NJE
  109 83 Albanian K      NE
  109 84 Albanian C      NE
  109 82 Albanian G      NJI
  109 95 ALBANIAN        NJI
a 110 OTHER
b                      000
  110 60 Panjabi ST
b                      001
  110 38 Takitaki        TRA
  110 55 Gypsy Gk        AVER
  110 78 Baluchi         DOHMI, DUHMI
b                      002
  110 79 Wakhi           DIGAR
  110 77 Tadzik          DIGAR
  110 76 Persian List    DIGAR
b                      003
  110 61 Lahnda          BIYA
  110 57 Kashmiri        BYAKH, PAR
  110 59 Gujarati        BIJU ("SECOND")
b                      004
  110 75 Waziri          BEL, NOR
  110 74 Afghan          BEL
b                      005
  110 81 Albanian Top    TJATRE
  110 82 Albanian G      TJETER
  110 84 Albanian C      JETR
  110 83 Albanian K      NETRE
  110 80 Albanian T      TJETER
  110 95 ALBANIAN        TJETER
b                      006
  110 40 Lithuanian ST   KITAS
  110 39 Lithuanian O    KITAS
  110 41 Latvian         CITS
b                      007
  110 58 Marathi         DUSRA, ITER
  110 62 Hindi           DUSRA
b                      008
  110 56 Singhalese      ARA, ANEK
  110 64 Nepali List     ARU, ARKO
  110 65 Khaskura        ARKO
b                      009
  110 20 Spanish         OTRO
  110 09 Vlach           ALTU
  110 17 Sardinian N     ATERU
  110 18 Sardinian L     ATERE
  110 15 French Creole C LOT
  110 13 French          AUTRE
  110 16 French Creole D LOT
  110 14 Walloon         OTE
  110 12 Provencal       AUTRE
  110 23 Catalan         ALTRA
  110 10 Italian         ALTRO
  110 19 Sardinian C     ATRU
  110 11 Ladin           OTER
  110 21 Portuguese ST   OUTRO
  110 22 Brazilian       OUTRO
  110 08 Rumanian List   ALT
b                      200
c                         200  2  201
  110 89 SLOVAK P        DRUHY
  110 42 Slovenian       DRUGI
  110 91 SLOVENIAN P     DRUG
  110 86 UKRAINIAN P     DRUHYJ
  110 88 POLISH P        DRUGI
  110 51 Russian         DRUGOJ
  110 85 RUSSIAN P       DRUGOJ
  110 54 Serbocroatian   DRUGI
  110 92 SERBOCROATIAN P DRUG
  110 90 CZECH P         DRUHY
  110 43 Lusatian L      DRUGI
  110 44 Lusatian U      DRUHI
  110 93 MACEDONIAN P    DRUG
  110 94 BULGARIAN P     DRUG
  110 87 BYELORUSSIAN P  DRUHI
  110 52 Macedonian      DRUG
  110 47 Czech E         DRUHE
  110 53 Bulgarian       DRUGO
b                      201
c                         200  2  201
c                         201  2  202
  110 45 Czech           JINY, DRUHY
b                      202
c                         201  2  202
c                         202  3  203
c                         202  3  204
  110 46 Slovak          INY
  110 50 Polish          INNY
b                      203
c                         202  3  203
c                         203  3  204
  110 73 Ossetic         INNAE
b                      204
c                         202  3  204
c                         203  3  204
  110 48 Ukrainian       INSYJ
  110 49 Byelorussian    INSY
b                      205
c                         205  3  206
  110 24 German ST       ANDER
  110 36 Faroese         ANNAR
  110 30 Swedish Up      ANNAN, ANNAT
  110 31 Swedish VL      AN, ANA
  110 33 Danish          ANDEN
  110 32 Swedish List    ANDRA, ANNAN, ANNAT
  110 34 Riksmal         ANNEN
  110 35 Icelandic ST    ANNAR
  110 27 Afrikaans       ANDER
  110 26 Dutch List      ANDER, NOG EEN
  110 25 Penn. Dutch     ONNER
  110 28 Flemish         ANDERE
  110 37 English ST      OTHER
  110 29 Frisian         OAR
b                      206
c                         205  3  206
  110 63 Bengali         ONNO
b                      207
c                         207  2  208
  110 68 Greek Mod       ALOS
  110 66 Greek ML        ALLOS
  110 70 Greek K         ALLOS
  110 67 Greek MD        ALLOS
  110 69 Greek D         ALLOS
  110 07 Breton ST       ALL
  110 05 Breton List     ALL
  110 04 Welsh C         ARALL
  110 06 Breton SE       ARALL
  110 03 Welsh N         LLALL
  110 01 Irish A         EILE
  110 02 Irish B         EILE
b                      208
c                         207  2  208
c                         208  2  209
  110 71 Armenian Mod    URIS, AYL
b                      209
c                         208  2  209
  110 72 Armenian List   URISH
a 111 PERSON
b                      000
  111 73 Ossetic
  111 79 Wakhi
  111 23 Catalan
  111 65 Khaskura
  111 47 Czech E
b                      001
  111 40 Lithuanian ST   ASMUO
  111 84 Albanian C      GINDE, ISTER
  111 37 English ST      PERSON
  111 02 Irish B         PEARSA, -ANN, -ANNA
  111 41 Latvian         PERSONA
  111 38 Takitaki        SOEMA
  111 39 Lithuanian O    ZMOGUS
b                      002
  111 86 UKRAINIAN P     OSOBA
  111 48 Ukrainian       OSOBA
  111 49 Byelorussian    ASOBA
  111 42 Slovenian       OSJBA
  111 89 SLOVAK P        OSOBA
  111 46 Slovak          OSOBA
  111 54 Serbocroatian   OSOBA
  111 88 POLISH P        OSOBA
  111 87 BYELORUSSIAN P  ASOBA
  111 45 Czech           OSOBA
  111 90 CZECH P         OSOBA
  111 43 Lusatian L      WOSOBA
  111 44 Lusatian U      WOSOBA
b                      003
  111 81 Albanian Top    NERI
  111 80 Albanian T      NJERI
  111 83 Albanian K      NERII
  111 82 Albanian G      NJERIU
  111 95 ALBANIAN        NJERIU
b                      004
  111 07 Breton ST       DEN
  111 06 Breton SE       DEN
  111 05 Breton List     DEN
  111 01 Irish A         DUINE
b                      005
  111 16 French Creole D MUA
  111 15 French Creole C MUN
b                      006
  111 04 Welsh C         PERSON
  111 03 Welsh N         PERSON
b                      007
  111 60 Panjabi ST      JENA
  111 57 Kashmiri        ZAN, MURTH
b                      008
  111 71 Armenian Mod    ANJ
  111 72 Armenian List   ANTZ
b                      200
c                         200  2  201
  111 53 Bulgarian       LICE
  111 93 MACEDONIAN P    LICE
  111 94 BULGARIAN P     LICE
  111 91 SLOVENIAN P     LICE
  111 92 SERBOCROATIAN P LICE
  111 85 RUSSIAN P       LICO
b                      201
c                         200  2  201
c                         201  2  202
  111 52 Macedonian      LICE, COVEK
b                      202
c                         201  2  202
  111 51 Russian         CELOVEK
  111 50 Polish          CZLOWIEK
b                      203
c                         203  2  204
  111 69 Greek D         PROSOPO
  111 66 Greek ML        PROSOPO
  111 70 Greek K         PROSOPON
b                      204
c                         203  2  204
c                         204  2  205
  111 67 Greek MD        PROSOPO, ANTHROPOS, KURIOS, ATOMO
b                      205
c                         204  2  205
  111 68 Greek Mod       ANTHROPOS, KANENAS
b                      206
c                         206  2  207
  111 17 Sardinian N     PESSONE
  111 18 Sardinian L     PERSONA
  111 22 Brazilian       PESSOA
  111 21 Portuguese ST   PESSOA
  111 08 Rumanian List   PERSOANA
  111 10 Italian         PERSONA
  111 19 Sardinian C     PERSONA
  111 12 Provencal       PERSOUNO, GENT
  111 20 Spanish         PERSONA
  111 14 Walloon         PERSONE
  111 13 French          PERSONNE
b                      207
c                         206  2  207
c                         207  2  208
  111 11 Ladin           CRASTIAUN, HOMENS,PERSUNA
b                      208
c                         207  2  208
  111 09 Vlach           OM
b                      209
c                         209  2  210
c                         209  3  221
  111 76 Persian List    SHAKHS
b                      210
c                         209  2  210
c                         210  2  211
c                         210  2  212
c                         210  2  213
c                         210  3  221
  111 77 Tadzik          ODAM, INSON, KAS, SAXA
b                      211
c                         210  2  211
c                         211  2  212
  111 78 Baluchi         KHAS
b                      212
c                         210  2  212
c                         211  2  212
  111 75 Waziri          KAS, TAN
  111 74 Afghan          TAN, KAS
b                      213
c                         210  2  213
c                         213  2  214
c                         213  2  215
  111 62 Hindi           LOG, INSAN
b                      214
c                         213  2  214
c                         214  2  215
  111 63 Bengali         LOK
b                      215
c                         213  2  215
c                         214  2  215
c                         215  2  216
c                         215  2  217
c                         215  2  219
  111 58 Marathi         MANUS, LOK
b                      216
c                         215  2  216
c                         216  2  217
c                         216  2  219
  111 59 Gujarati        RYEKTI, MANES
  111 64 Nepali List     MANIS, MANCHE
  111 56 Singhalese      MINIHA
  111 55 Gypsy Gk        MANUS
  111 35 Icelandic ST    MAOR
  111 36 Faroese         MADUR
  111 26 Dutch List      MENSCH
  111 25 Penn. Dutch     MENSCH
  111 29 Frisian         MINSKE
  111 34 Riksmal         MENNESKE
  111 24 German ST       MENSCH
b                      217
c                         215  2  217
c                         216  2  217
c                         217  2  218
c                         217  2  219
  111 31 Swedish VL      PASON, MANIS
b                      218
c                         217  2  218
  111 30 Swedish Up      PERSON
  111 33 Danish          PERSON
  111 32 Swedish List    PERSON
b                      219
c                         215  2  219
c                         216  2  219
c                         217  2  219
c                         219  2  220
  111 28 Flemish         PERSOON, MENSCH
b                      220
c                         219  2  220
  111 27 Afrikaans       PERSOON
b                      221
c                         209  3  221
c                         210  3  221
  111 61 Lahnda          SEXS
a 112 TO PLAY
b                      000
  112 09 Vlach
  112 79 Wakhi
b                      001
  112 57 Kashmiri        GINDUN
  112 78 Baluchi         LEV KHANAGH
  112 75 Waziri          MAZSHILEDEL
  112 59 Gujarati        REMOWU
  112 23 Catalan         RIURERSE D'ALGU
  112 56 Singhalese      SELLAM/KARANAWA
  112 41 Latvian         SPELET
b                      002
  112 76 Persian List    BAZI KARDAN
  112 74 Afghan          BAZI KAVEL
  112 77 Tadzik          BOZI KARDAN
b                      003
  112 17 Sardinian N     JOKARE
  112 18 Sardinian L     GIOGARE
  112 15 French Creole C ZWE
  112 10 Italian         GIUOCARE
  112 19 Sardinian C     GOGAI
  112 11 Ladin           GIOVER
  112 08 Rumanian List   A (SE) JUCA
  112 13 French          JOUER
  112 16 French Creole D ZWE
  112 14 Walloon         DJOUWER
  112 12 Provencal       JOUGA
  112 20 Spanish         JUGAR
  112 21 Portuguese ST   JOGAR
  112 22 Brazilian       JOGAR
b                      004
  112 04 Welsh C         CHWARAE
  112 03 Welsh N         CHWARAE
  112 05 Breton List     C'HOARI, EBATA
  112 06 Breton SE       HOARI
  112 07 Breton ST       C'HOARI
b                      005
  112 01 Irish A         IMIRT
  112 02 Irish B         IMRIM
b                      006
  112 37 English ST      TO PLAY
  112 38 Takitaki        PRE
b                      007
  112 81 Albanian Top    LHOS, AOR. LHOJTA
  112 83 Albanian K      LUAN
  112 80 Albanian T      ME LOJTUR
  112 84 Albanian C      LOS
  112 82 Albanian G      LUJ
  112 95 ALBANIAN        LUJ, LUJTA
b                      008
  112 68 Greek Mod       PEZO
  112 66 Greek ML        PAIDZO
  112 70 Greek K         PAIDZO
  112 67 Greek MD        PAIDZO
  112 69 Greek D         PAIDZO
b                      009
  112 87 BYELORUSSIAN P  HUL AC
  112 49 Byelorussian    HULJAC', ZABAWLJACCA
b                      010
  112 71 Armenian Mod    XALAL
  112 72 Armenian List   GHAGHAL
b                      011
  112 65 Khaskura        KHELNU
  112 55 Gypsy Gk        KHELAV
  112 64 Nepali List     KHELNU
  112 62 Hindi           KHELNA
  112 63 Bengali         KHELA
  112 58 Marathi         KHELNE.
  112 61 Lahnda          KHEDEN
  112 60 Panjabi ST      KHEDDENA
b                      100
  112 73 Ossetic         X"AZYN
  112 40 Lithuanian ST   ZAISTI, ZAISTI
b                      200
c                         200  2  201
  112 89 SLOVAK P        HRAT
  112 42 Slovenian       SE JGRAT
  112 91 SLOVENIAN P     IGRATI
  112 86 UKRAINIAN P     HRATY
  112 54 Serbocroatian   IGRATI SE
  112 92 SERBOCROATIAN P IGRATI
  112 90 CZECH P         HRATI
  112 43 Lusatian L      GRAS
  112 44 Lusatian U      HRAC
  112 93 MACEDONIAN P    IGRAM
  112 50 Polish          GRAC
  112 88 POLISH P        GRAC
  112 51 Russian         IGRAT
  112 85 RUSSIAN P       IGRAT
  112 45 Czech           HRATI
  112 94 BULGARIAN P     IGRAJA
  112 52 Macedonian      IGRA
  112 47 Czech E         HRAT
  112 48 Ukrainian       HRATY
  112 53 Bulgarian       DA IGRAE
b                      201
c                         200  2  201
c                         201  3  202
  112 46 Slovak          HRAT , BAVIT  SA
b                      202
c                         201  3  202
  112 39 Lithuanian O    BOVYTIS
b                      203
c                         203  2  204
  112 30 Swedish Up      LEKA
  112 35 Icelandic ST    LEIKA SER
  112 34 Riksmal         LEKE
  112 33 Danish          LEGE
  112 36 Faroese         LEIKA
b                      204
c                         203  2  204
c                         204  2  205
  112 31 Swedish VL      LEK, SPELA
  112 32 Swedish List    SPELA, LEKA
b                      205
c                         204  2  205
  112 24 German ST       SPIELEN
  112 29 Frisian         BOARTSJE, SPYLJE
  112 26 Dutch List      SPELEN
  112 25 Penn. Dutch     SCHPIEL
  112 28 Flemish         SPELEN
  112 27 Afrikaans       SPEEL
a 113 TO PULL
b                      001
  113 38 Takitaki        HALI
  113 53 Bulgarian       DA DERPA
  113 73 Ossetic         IVAZYN, LASYN
  113 57 Kashmiri        LAMUN
  113 42 Slovenian       NATZRAT
  113 37 English ST      TO PULL
  113 84 Albanian C      RNAR
  113 14 Walloon         SETCHI
  113 55 Gypsy Gk        SWRDAV
b                      002
  113 70 Greek K         TRABO
  113 68 Greek Mod       TRAVO, SERNO
  113 66 Greek ML        TRABO
  113 67 Greek MD        TRABO
  113 69 Greek D         TRABAO
b                      003
  113 01 Irish A         TARRAINGT
  113 02 Irish B         TARRAINGIM, STRACAIM, STATHAIM
b                      004
  113 28 Flemish         TREKKEN
  113 27 Afrikaans       TREK
  113 26 Dutch List      TREKKEN
  113 29 Frisian         LUKE, TREKKE
  113 33 Danish          TRAEKKE
  113 34 Riksmal         TREKKE
b                      005
  113 76 Persian List    KASHIDAN
  113 77 Tadzik          KASIDAN, KASOLA KARDAN
  113 74 Afghan          KSEL, ISTEL
  113 75 Waziri          WUKSHEL, KSHEL
  113 79 Wakhi           XUS-
b                      006
  113 22 Brazilian       PUXAR
  113 21 Portuguese ST   PUXAR
b                      007
  113 40 Lithuanian ST   TRAUKTI
  113 39 Lithuanian O    TRAUKTI
b                      008
  113 71 Armenian Mod    K`ASEL
  113 72 Armenian List   KASHEL
b                      009
  113 82 Albanian G      HEK
  113 95 ALBANIAN        HEK
  113 81 Albanian Top    EK, AOR. OKA
  113 80 Albanian T      ME HEGUR
  113 83 Albanian K      XELHKIN
b                      010
  113 05 Breton List     TENNA
  113 04 Welsh C         TYNNU
  113 03 Welsh N         TYNNU
b                      100
  113 07 Breton ST       SACHAN
  113 06 Breton SE       CHACHEIN
b                      101
  113 58 Marathi         ODHNE.
  113 56 Singhalese      ADINAWA
b                      200
c                         200  3  201
c                         200  2  202
  113 10 Italian         TIRARE
  113 20 Spanish         TIRAR
  113 19 Sardinian C     TIRAI
  113 13 French          TIRER
  113 16 French Creole D TIWE
  113 18 Sardinian L     TIRARE
  113 15 French Creole C TIHWE, HALE
b                      201
c                         200  3  201
c                         201  3  202
  113 17 Sardinian N     ISTRITHTHIRE
b                      202
c                         200  2  202
c                         201  3  202
c                         202  2  203
c                         202  3  204
  113 23 Catalan         TRAURER, TIRAR
  113 12 Provencal       TIRA, TRAIRE
b                      203
c                         202  2  203
c                         203  3  204
  113 09 Vlach           TRAGU
  113 08 Rumanian List   A TRAGE
  113 11 Ladin           TRER
  113 32 Swedish List    DRAGA(I), RYCKA(I)
  113 35 Icelandic ST    DRAGA
  113 30 Swedish Up      DRA(GA), SLITA
  113 31 Swedish VL      DRA, SLIT
b                      204
c                         202  3  204
c                         203  3  204
c                         204  2  205
  113 36 Faroese         DRAGA, TOGA
b                      205
c                         204  2  205
  113 24 German ST       ZIEHEN
  113 25 Penn. Dutch     ZIEK
b                      206
c                         206  2  207
c                         206  3  209
c                         206  3  210
  113 51 Russian         TJANUT
  113 85 RUSSIAN P       T AGAT
  113 46 Slovak          T AHAT
  113 45 Czech           TAHATI
  113 87 BYELORUSSIAN P  C AHNYC
  113 49 Byelorussian    CJAHNUC'
  113 47 Czech E         TAHNUT
  113 86 UKRAINIAN P     T AHATY
  113 44 Lusatian U      CAHAC
  113 50 Polish          CIAGNAC
  113 88 POLISH P        CIAGNAC
b                      207
c                         206  2  207
c                         207  2  208
c                         207  3  209
c                         207  3  210
  113 48 Ukrainian       TJAHNUTY, VOLOCYTY
b                      208
c                         207  2  208
  113 93 MACEDONIAN P    VLECAM
  113 91 SLOVENIAN P     VLECI
  113 52 Macedonian      VLECE, PROVIRA, TRGA
  113 89 SLOVAK P        VLIECT
  113 43 Lusatian L      LAC
  113 41 Latvian         VILKT
  113 94 BULGARIAN P     VLACA
  113 90 CZECH P         VLECI
  113 54 Serbocroatian   VUCI
  113 92 SERBOCROATIAN P VUCI
b                      209
c                         206  3  209
c                         207  3  209
c                         209  2  210
  113 63 Bengali         TANA
  113 65 Khaskura        TANNU
b                      210
c                         206  3  210
c                         207  3  210
c                         209  2  210
c                         210  2  211
c                         210  3  212
  113 64 Nepali List     KHAICNU, TANNU
b                      211
c                         210  2  211
c                         211  3  212
  113 61 Lahnda          KHICCEN
  113 59 Gujarati        KHECWU
  113 60 Panjabi ST      KHICCENA
  113 62 Hindi           KHICNA
b                      212
c                         210  3  212
c                         211  3  212
  113 78 Baluchi         CHIKAGH, CHIKITHA
a 114 TO PUSH
b                      000
  114 82 Albanian G
  114 38 Takitaki
b                      001
  114 62 Hindi           DEBANA
  114 41 Latvian         GRUST
  114 76 Persian List    HOL DADAN
  114 61 Lahnda          KHICCEN
  114 70 Greek K         OTHO
  114 42 Slovenian       PORIVAT
  114 37 English ST      TO PUSH
  114 55 Gypsy Gk        SPILDAV
  114 11 Ladin           SBUERLER, STUMPLER
  114 86 UKRAINIAN P     STOUCHATY
  114 79 Wakhi           SUKE DI-, TECUV-
  114 93 MACEDONIAN P    TURKAM
  114 35 Icelandic ST    YTA
  114 73 Ossetic         YCXOJYN
  114 57 Kashmiri        ZIRU DINU
b                      002
  114 13 French          POUSSER
  114 15 French Creole C PUSE, VOYE
  114 16 French Creole D PUSE
  114 20 Spanish         EMPUJAR
b                      003
  114 10 Italian         SPINGERE
  114 19 Sardinian C     SPINGI
  114 18 Sardinian L     ISPINGHERE
  114 17 Sardinian N     ISPINGERE
  114 08 Rumanian List   A IMPINGE, A IMBRINCI
  114 09 Vlach           PINKU
b                      004
  114 53 Bulgarian       DA BUTA
  114 52 Macedonian      BUTNE/KOSKA
b                      005
  114 48 Ukrainian       PXATY, STOVXATY, DOSCYT'
  114 49 Byelorussian    PXAC'
  114 87 BYELORUSSIAN P  PCHAC
  114 50 Polish          PCHAC
  114 88 POLISH P        PCHAC
  114 91 SLOVENIAN P     PEHATI
b                      006
  114 43 Lusatian L      TLUC
  114 44 Lusatian U      TOLC
  114 94 BULGARIAN P     TLASKAM
  114 51 Russian         TOLKAT
  114 85 RUSSIAN P       TOLKAT
  114 47 Czech E         TLACIT
b                      007
  114 54 Serbocroatian   GURATI
  114 92 SERBOCROATIAN P GURATI
b                      008
  114 07 Breton ST       BOUNTAN
  114 06 Breton SE       BOUTEIN
  114 05 Breton List     LUSKA, BOUNTA
b                      009
  114 04 Welsh C         GWTHIO, HWPO
  114 03 Welsh N         GWTHIO
b                      010
  114 45 Czech           STRKATI
  114 90 CZECH P         STRKATI
  114 89 SLOVAK P        STRKNUT
  114 46 Slovak          STRKAT
b                      011
  114 22 Brazilian       EMPURRAR
  114 21 Portuguese ST   EMPURRAR
b                      012
  114 29 Frisian         DOMPE, TRIUWE
  114 27 Afrikaans       VOORT-DRYF, VOORT-DRYWE
b                      013
  114 01 Irish A         BRUGHADH, SATHADH
  114 02 Irish B         DRIGIM, BRUIDHIM, RAITHIM
b                      014
  114 72 Armenian List   HUREL
  114 71 Armenian Mod    HREL
b                      015
  114 74 Afghan          PORI VAHEL
  114 75 Waziri          PORI WAHEL
b                      200
c                         200  2  201
  114 33 Danish          STODE
  114 24 German ST       STOSSEN
  114 31 Swedish VL      STYR, FLOJ
  114 40 Lithuanian ST   STUMTI
  114 39 Lithuanian O    STUMDYTI
  114 84 Albanian C      STIN
  114 83 Albanian K      STIIN (AOR. STIIJTA)
  114 80 Albanian T      ME SHTYRE
  114 95 ALBANIAN        SHTYP
  114 81 Albanian Top    STYN, AOR. STYVA
b                      201
c                         200  2  201
c                         201  2  202
  114 32 Swedish List    SKJUTA  PA , STOTA
b                      202
c                         201  2  202
  114 30 Swedish Up      SKJUTA PA, KNUFFA TILL
b                      203
c                         203  2  204
c                         203  3  206
  114 34 Riksmal         SKYVE
  114 25 Penn. Dutch     SCHIEP
b                      204
c                         203  2  204
c                         204  2  205
c                         204  3  206
  114 26 Dutch List      SCHUIVEN, VOORTDUWEN
b                      205
c                         204  2  205
  114 28 Flemish         DUWEN
b                      206
c                         203  3  206
c                         204  3  206
  114 36 Faroese         SKUMPA
b                      207
c                         207  2  208
  114 14 Walloon         BOUTER
b                      208
c                         207  2  208
c                         208  2  209
  114 12 Provencal       BUTA, EMPEGNE
b                      209
c                         208  2  209
  114 23 Catalan         EMPENYER
b                      210
c                         210  2  211
  114 59 Gujarati        DHEKKELWU
  114 63 Bengali         DHAKKA+DEOA
  114 58 Marathi         DHEKELNE.
  114 60 Panjabi ST      TIKKENA
b                      211
c                         210  2  211
c                         211  2  212
  114 64 Nepali List     GHACETNU, THELNU, DHAKELNU
b                      212
c                         211  2  212
  114 65 Khaskura        GHACHYA DINU
b                      213
c                         213  2  214
  114 68 Greek Mod       SPROKHNO
  114 69 Greek D         SPROCHNO
b                      214
c                         213  2  214
c                         214  2  215
  114 67 Greek MD        SPROCHNO, SKOUNTO
b                      215
c                         214  2  215
  114 66 Greek ML        SKOUNTO
b                      216
c                         216  3  217
  114 77 Tadzik          TELA DODAN, FUSURDAN
  114 78 Baluchi         TELAN (SB.)
b                      217
c                         216  3  217
  114 56 Singhalese      TALLU/KARANAWA
a 115 TO RAIN
b                      000
  115 09 Vlach
  115 79 Wakhi
  115 49 Byelorussian
b                      001
  115 53 Bulgarian       DA VALI
  115 63 Bengali         JOL+PORA
  115 54 Serbocroatian   KISITI
  115 58 Marathi         PAUS+PEDNE.
  115 56 Singhalese      VAHINAWA
  115 52 Macedonian      VRNE
b                      002
  115 30 Swedish Up      REGNA
  115 31 Swedish VL      RANGN
  115 24 German ST       REGNEN
  115 35 Icelandic ST    RIGNA
  115 34 Riksmal         REGNE
  115 32 Swedish List    REGNA
  115 33 Danish          REGN
  115 36 Faroese         REGNA
  115 29 Frisian         REINE
  115 28 Flemish         REGENEN
  115 25 Penn. Dutch     REGGE
  115 26 Dutch List      REGENEN
  115 27 Afrikaans       REEN, REGENT
  115 38 Takitaki        AREEN
  115 37 English ST      TO RAIN
b                      003
  115 86 UKRAINIAN P     DOSC
  115 91 SLOVENIAN P     DEZ
  115 42 Slovenian       DEZ, DES PADA
  115 89 SLOVAK P        DAZD
  115 92 SERBOCROATIAN P DAZD
  115 85 RUSSIAN P       DOZD
  115 51 Russian         DOZD  IDET (IT RAINS)
  115 88 POLISH P        DESZCZ
  115 50 Polish          DESZCZ PADA (IT IS RAINING)
  115 93 MACEDONIAN P    DOZD
  115 44 Lusatian U      DESC
  115 43 Lusatian L      DESC
  115 90 CZECH P         DEST
  115 87 BYELORUSSIAN P  DOZDZ
  115 94 BULGARIAN P     DUZD
  115 48 Ukrainian       PADE DOSC
b                      004
  115 18 Sardinian L     PIOERE
  115 17 Sardinian N     PROERE
  115 08 Rumanian List   A PLOUA
  115 11 Ladin           PLOUVER, PLOVER
  115 19 Sardinian C     PROI
  115 10 Italian         PIOVERE
  115 23 Catalan         PLOURER, CAURER
  115 12 Provencal       PLOURE
  115 14 Walloon         PLOURE
  115 13 French          PLEUVOIR
  115 20 Spanish         LLOVER
  115 21 Portuguese ST   CHOVER
  115 22 Brazilian       CHOVER
  115 16 French Creole D TOBE (LAPLI)
  115 15 French Creole C LAPLI (SB.)
b                      005
  115 41 Latvian         LIT (LIETUS)
  115 39 Lithuanian O    LYTI
  115 40 Lithuanian ST   LYTI
b                      006
  115 07 Breton ST       GLAV A ZO ("THERE IS RAIN")
  115 06 Breton SE       GLAU E ZOU ("THERE IS RAIN")
  115 05 Breton List     GLAOIA, FLAVA, OBER GLAO
  115 04 Welsh C         BWRW GLAW
  115 03 Welsh N         BWRWGLAW, GLAWIO
b                      007
  115 01 Irish A         FEARTHAINN DO CHUR (BAISTEACH DO DHEANAMH C.)
  115 02 Irish B         DO DHEANAMH   FEARTHAINNE
b                      008
  115 71 Armenian Mod    ANJREW, ANJREWEL
  115 72 Armenian List   ANZREV
b                      009
  115 69 Greek D         BRECHEI
  115 68 Greek Mod       VRECHI
  115 70 Greek K         BRECHEI
  115 66 Greek ML        BRECHEI (3 SG.)
  115 67 Greek MD        BRECHEI
b                      010
  115 73 Ossetic         UARYN, K"AEVDA
  115 74 Afghan          BARAN UREZI
  115 77 Tadzik          BORON BORIDA ISTODAAST
  115 76 Persian List    BARIDAN
  115 57 Kashmiri        RUD PYONU, WASHUN
  115 60 Panjabi ST      VESSENA
  115 75 Waziri          WAREDEL
  115 78 Baluchi         GWARAGH, GWARTA
b                      011
  115 46 Slovak          PRSAT
  115 45 Czech           PRSETI
  115 47 Czech E         PRSAT
b                      012
  115 80 Albanian T      ME RENE SHI
  115 83 Albanian K      BIE SII
  115 84 Albanian C      SI (NOUN)
  115 82 Albanian G      BI SHI (IT RAINS)
  115 95 ALBANIAN        BISHI (IT RAINS)
  115 81 Albanian Top    BIE SI, RA SI, KA RENE SI
b                      013
  115 61 Lahnda          BARES THIWEN
  115 64 Nepali List     BARSANU
  115 55 Gypsy Gk        BRWSUNT
  115 62 Hindi           BERESNA, BARIS+HONA
  115 65 Khaskura        BARSANU
  115 59 Gujarati        WERSAD PERE CUE
a 116 RED
b                      001
  116 57 Kashmiri        WOZOLU
b                      002
  116 55 Gypsy Gk        LOLO
  116 61 Lahnda          LAL
  116 59 Gujarati        LAL
  116 58 Marathi         TAMBDA, LAL
  116 63 Bengali         LAL
  116 62 Hindi           LAL
  116 60 Panjabi ST      LAL
b                      003
  116 30 Swedish Up      ROD
  116 31 Swedish VL      RO
  116 18 Sardinian L     RUJU
  116 17 Sardinian N     RUJU
  116 15 French Creole C HWUZ
  116 42 Slovenian       RUDJCE
  116 39 Lithuanian O    RAUDONAS
  116 40 Lithuanian ST   RAUDONAS
  116 70 Greek K         ERUTHROUS
  116 19 Sardinian C     ARRUBIU
  116 24 German ST       ROT
  116 35 Icelandic ST    RAUOR
  116 34 Riksmal         ROD
  116 32 Swedish List    ROD
  116 33 Danish          ROD
  116 36 Faroese         REYDUR
  116 29 Frisian         READ, REA
  116 28 Flemish         ROOD
  116 25 Penn. Dutch     ROEDT
  116 26 Dutch List      ROOD
  116 27 Afrikaans       ROOI
  116 38 Takitaki        REDI
  116 37 English ST      RED
  116 10 Italian         ROSSO
  116 23 Catalan         ROIG
  116 20 Spanish         ROJO
  116 12 Provencal       ROUGE, JO
  116 14 Walloon         RODJE
  116 16 French Creole D WUZ
  116 13 French          ROUGE
  116 06 Breton SE       RU
  116 07 Breton ST       RUZ
  116 05 Breton List     RUZ
b                      004
  116 65 Khaskura        RATO
  116 56 Singhalese      RATA, RATU
  116 64 Nepali List     RATO
b                      005
  116 86 UKRAINIAN P     CERVONYJ
  116 91 SLOVENIAN P     CRLJEN
  116 89 SLOVAK P        CERVENY
  116 46 Slovak          CERVENY
  116 54 Serbocroatian   CRVEN
  116 92 SERBOCROATIAN P CRVEN
  116 88 POLISH P        CZERWONY
  116 50 Polish          CZERWONY
  116 93 MACEDONIAN P    CRVEN
  116 44 Lusatian U      CERWJENY
  116 43 Lusatian L      CERWENY
  116 90 CZECH P         CERVENY
  116 45 Czech           CERVENY
  116 87 BYELORUSSIAN P  CYRVONY
  116 94 BULGARIAN P     CERVEN
  116 52 Macedonian      ALOV, CRVEN
  116 47 Czech E         CERVENE
  116 49 Byelorussian    CYRVONY
  116 48 Ukrainian       CERVONYJ, BAHRJANYJ
  116 53 Bulgarian       CERVENO
b                      006
  116 69 Greek D         KOKKINO
  116 67 Greek MD        KOKKINOS
  116 66 Greek ML        KOKKINOS
  116 68 Greek Mod       KOKINOS
b                      007
  116 02 Irish B         DEARG, -EIRGE
  116 01 Irish A         DEARG
b                      008
  116 08 Rumanian List   ROSU
  116 09 Vlach           AROSE
b                      009
  116 21 Portuguese ST   VERMELHO
  116 22 Brazilian       VERMELHO (ME)
b                      010
  116 11 Ladin           COTSCHEN
  116 03 Welsh N         COCH, RHUDD
  116 04 Welsh C         COCH
b                      011
  116 80 Albanian T      I, E KUG
  116 83 Albanian K      I KUK
  116 84 Albanian C      I-KUK
  116 82 Albanian G      KUKJ
  116 95 ALBANIAN        KUKJ
  116 81 Albanian Top    I-KUK
b                      200
c                         200  3  201
  116 76 Persian List    SORKH
  116 73 Ossetic         CYRX
  116 79 Wakhi           SEKR
  116 78 Baluchi         SUHR
  116 74 Afghan          SUR
  116 77 Tadzik          SURX
  116 75 Waziri          SIR
b                      201
c                         200  3  201
  116 41 Latvian         SARKANS
b                      202
c                         202  3  203
  116 71 Armenian Mod    KARMIR
  116 72 Armenian List   GARMIR
b                      203
c                         202  3  203
  116 51 Russian         KRASNYJ
  116 85 RUSSIAN P       KRASNYJ
a 117 RIGHT (CORRECT)
b                      000
  117 57 Kashmiri
  117 16 French Creole D
  117 29 Frisian
b                      001
  117 47 Czech E         AKORAT
  117 15 French Creole C BO, KOREK
  117 01 Irish A         CEART
  117 28 Flemish         GOED
  117 56 Singhalese      HARI
  117 84 Albanian C      LIK ("TRUE", NOT "EXACT", "JUST")
  117 77 Tadzik          ODILONA, BOINSOFONA
  117 70 Greek K         ORTHOS
  117 41 Latvian         PAREIZS
  117 72 Armenian List   SHIDAG
  117 50 Polish          SLUSZNY
  117 55 Gypsy Gk        TAMAMI
  117 71 Armenian Mod    ULI'L
  117 53 Bulgarian       VJARNO
b                      002
  117 92 SERBOCROATIAN P PRAV
  117 46 Slovak          SPRAVNY
  117 89 SLOVAK P        PRAVY
  117 42 Slovenian       PROV
  117 91 SLOVENIAN P     PRAV
  117 86 UKRAINIAN P     SPAVEDLYVYI
  117 94 BULGARIAN P     PRAV
  117 87 BYELORUSSIAN P  PRAVNY
  117 45 Czech           SPRAVNY
  117 90 CZECH P         SPRAVNY
  117 43 Lusatian L      PSAWY
  117 44 Lusatian U      PRAWY
  117 93 MACEDONIAN P    PRAV
  117 52 Macedonian      PRAVILEN
  117 48 Ukrainian       PRJAMYJ, SPRAVEDLYVYJ
  117 49 Byelorussian    PRAVIDLOVY, -A
  117 88 POLISH P        POPRAWNY
  117 51 Russian         PRAVIL NYJ
  117 85 RUSSIAN P       PRAVYJ
  117 54 Serbocroatian   ISPRAVNO
b                      003
  117 09 Vlach           SOSTO
  117 67 Greek MD        SOSTOS
  117 69 Greek D         SOSTO
  117 68 Greek Mod       DHIKYO, SOSTOS
  117 66 Greek ML        SOSTOS
b                      004
  117 39 Lithuanian O    TEISINGAS
  117 40 Lithuanian ST   TAISYKLINGAS
b                      005
  117 81 Albanian Top    DREK, IDREJTE
  117 80 Albanian T      I, E DREJTE
  117 83 Albanian K      DREK
  117 82 Albanian G      DREJT
  117 95 ALBANIAN        DREJT
b                      006
  117 05 Breton List     EEUN, REIZ, REIZEK, GWIRION
  117 02 Irish B         COIR
  117 04 Welsh C         CYWIR, IAWN
  117 03 Welsh N         CYWIR
b                      007
  117 61 Lahnda          THIK
  117 64 Nepali List     THIK
  117 65 Khaskura        THIK
  117 60 Panjabi ST      THIK
  117 62 Hindi           THIK
  117 63 Bengali         THIK
  117 58 Marathi         THIK, BEROBER
b                      100
  117 59 Gujarati        SACU, KHERU
  117 74 Afghan          SAM
  117 75 Waziri          SAHI
b                      200
c                         200  2  201
  117 79 Wakhi           WERTS, DURUST, BUF, BEROBER
  117 73 Ossetic         RAST, RAESTON
  117 78 Baluchi         RAST
  117 76 Persian List    DOROST
  117 30 Swedish Up      RATT
  117 31 Swedish VL      RAT
  117 33 Danish          RET
  117 32 Swedish List    RATT
  117 34 Riksmal         RIKTIG
  117 35 Icelandic ST    RETTR
  117 24 German ST       RECHT
  117 36 Faroese         RAETTUR
  117 25 Penn. Dutch     RECHT
  117 26 Dutch List      RICHTIG, RECHT, WAAR, ECHT
  117 27 Afrikaans       REG
  117 37 English ST      RIGHT
  117 38 Takitaki        RETI
  117 07 Breton ST       REIZH
  117 06 Breton SE       REIH
  117 20 Spanish         DERECHO
  117 22 Brazilian       DIREITO
  117 21 Portuguese ST   DIREITO
  117 08 Rumanian List   CORECT, DREPT
  117 11 Ladin           DRET
b                      201
c                         200  2  201
c                         201  2  202
  117 23 Catalan         RECTE, DRET, JUST
b                      202
c                         201  2  202
  117 18 Sardinian L     JUSTU
  117 17 Sardinian N     JUSTU
  117 10 Italian         GIUSTO
  117 19 Sardinian C     GUSTU
  117 13 French          JUSTE
  117 14 Walloon         DJUSSE
  117 12 Provencal       JUST, USTO
a 118 RIGHT (HAND)
b                      000
  118 91 SLOVENIAN P
  118 86 UKRAINIAN P
  118 89 SLOVAK P
  118 92 SERBOCROATIAN P
  118 85 RUSSIAN P
  118 88 POLISH P
  118 90 CZECH P
  118 43 Lusatian L
  118 44 Lusatian U
  118 93 MACEDONIAN P
  118 94 BULGARIAN P
  118 87 BYELORUSSIAN P
  118 29 Frisian
  118 72 Armenian List
b                      001
  118 71 Armenian Mod    AJ
  118 77 Tadzik          BEGUNOX, BEAJB
  118 55 Gypsy Gk        CACO
  118 02 Irish B         CORA
  118 59 Gujarati        JEMELU
  118 41 Latvian         LABAIS
  118 39 Lithuanian O    TEISA
  118 58 Marathi         UJVA
b                      002
  118 68 Greek Mod       DHEKSIS
  118 66 Greek ML        DEKSIOS
  118 70 Greek K         DEKSEIA
  118 67 Greek MD        DEKSIOS, DEKSES
  118 69 Greek D         DEKSI
  118 40 Lithuanian ST   DESINYS
  118 52 Macedonian      DESEN
  118 65 Khaskura        DAHINA
  118 53 Bulgarian       DJASNO
  118 81 Albanian Top    DJATHE
  118 83 Albanian K      DJATHETIST
  118 80 Albanian T      I, E DJATHTE
  118 82 Albanian G      DJATHT
  118 10 Italian         DESTRO
  118 18 Sardinian L     DESTRU
  118 07 Breton ST       DEHOU
  118 06 Breton SE       DEHEU
  118 05 Breton List     DEHOU
  118 04 Welsh C         DE
  118 03 Welsh N         DE, DEHEU
  118 01 Irish A         DEAS
  118 42 Slovenian       DESNA RAKA
  118 54 Serbocroatian   DESNICA
  118 57 Kashmiri        DACHYUNU
  118 56 Singhalese      DAKUNATA
b                      003
  118 46 Slovak          PRAVY
  118 51 Russian         PRAVYJ
  118 50 Polish          PRAWY
  118 45 Czech           PRAVY
  118 48 Ukrainian       PRAVORUC, PRAVYJ
  118 49 Byelorussian    PRAVY
  118 47 Czech E         PRAVO
b                      004
  118 30 Swedish Up      HOGER
  118 31 Swedish VL      HOGAR
  118 36 Faroese         HOGRI
  118 33 Danish          HOJRE
  118 32 Swedish List    HOGER
  118 34 Riksmal         HOYRE
  118 35 Icelandic ST    HAEGRI
b                      005
  118 84 Albanian C      E-DREJTA
  118 95 ALBANIAN        DREJT
b                      200
c                         200  3  400
  118 24 German ST       RECHT
  118 27 Afrikaans       REG
  118 26 Dutch List      RECHTS, RECHTER
  118 25 Penn. Dutch     REHTSS HONNDT
  118 28 Flemish         REGTSCH
  118 37 English ST      RIGHT (HAND)
  118 38 Takitaki        RETI
  118 17 Sardinian N     DERETTU
  118 15 French Creole C DWET
  118 20 Spanish         DERECHO
  118 23 Catalan         DRETA
  118 19 Sardinian C     DERETTU
  118 11 Ladin           DRET
  118 09 Vlach           ANDEARTU
  118 08 Rumanian List   (PE PARTA) DREAPTA (ON THE RIGHT SIDE)
  118 13 French          DROIT
  118 16 French Creole D DWET
  118 14 Walloon         DREUT
  118 12 Provencal       DRE, ECHO
  118 22 Brazilian       DIREITO
  118 21 Portuguese ST   DIREITO
  118 78 Baluchi         RAST
  118 76 Persian List    RAST
b                      400
c                         200  3  400
  118 73 Ossetic         RAXIZ
  118 79 Wakhi           WURZGE
b                      201
c                         201  3  202
  118 64 Nepali List     DAINU
  118 62 Hindi           DAYA
b                      202
c                         201  3  202
  118 63 Bengali         DAN
b                      203
c                         203  3  204
  118 60 Panjabi ST      SEJJA
  118 61 Lahnda          SEJJA
b                      204
c                         203  3  204
  118 75 Waziri          SHAI
  118 74 Afghan          SAJ
a 119 RIVER
b                      001
  119 55 Gypsy Gk        POTAMI
  119 73 Ossetic         DON, CAEUGAEDON
  119 57 Kashmiri        KOL
  119 42 Slovenian       POTOK
  119 76 Persian List    SUDKHANE
  119 47 Czech E         XVOYNYICA
b                      002
  119 04 Welsh C         AFON
  119 03 Welsh N         AFON
  119 01 Irish A         ABHAINN
  119 02 Irish B         ABHA
  119 40 Lithuanian ST   UPE
  119 39 Lithuanian O    UPE
  119 41 Latvian         UPE
b                      003
  119 91 SLOVENIAN P     REKA
  119 86 UKRAINIAN P     RIKA
  119 50 Polish          RZEKA
  119 88 POLISH P        RZEKA
  119 51 Russian         REKA
  119 85 RUSSIAN P       REKA
  119 54 Serbocroatian   REKA
  119 92 SERBOCROATIAN P REKA
  119 46 Slovak          RIEKA
  119 89 SLOVAK P        RIEKA
  119 93 MACEDONIAN P    REKA
  119 44 Lusatian U      REKA
  119 43 Lusatian L      REKA
  119 90 CZECH P         REKA
  119 45 Czech           REKA
  119 87 BYELORUSSIAN P  RAKA
  119 94 BULGARIAN P     REKA
  119 52 Macedonian      REKA
  119 49 Byelorussian    RAKA
  119 48 Ukrainian       RICKA, RIKA
  119 53 Bulgarian       REKA
b                      004
  119 27 Afrikaans       RIVIER
  119 25 Penn. Dutch     REVVER
  119 26 Dutch List      RIVIER
b                      005
  119 37 English ST      RIVER
  119 38 Takitaki        RIBA, LIBA
b                      006
  119 30 Swedish Up      ALV
  119 34 Riksmal         ELV
b                      007
  119 35 Icelandic ST    A
  119 36 Faroese         A
  119 31 Swedish VL      A
b                      008
  119 65 Khaskura        GANGA
  119 56 Singhalese      GANGA
b                      009
  119 81 Albanian Top    LHUME
  119 80 Albanian T      LUME
  119 83 Albanian K      LUME
  119 84 Albanian C      LUM
  119 82 Albanian G      LUMI
  119 95 ALBANIAN        LUMI
b                      010
  119 68 Greek Mod       POTAMI
  119 66 Greek ML        POTAMOS
  119 70 Greek K         POTAMOS
  119 67 Greek MD        POTAMI
  119 69 Greek D         POTAMOS, POTAMI
b                      011
  119 71 Armenian Mod    GET
  119 72 Armenian List   GED
b                      012
  119 05 Breton List     STEIR, STER
  119 06 Breton SE       STER
  119 07 Breton ST       STER
b                      200
c                         200  2  201
  119 09 Vlach           ARUW
  119 17 Sardinian N     RIVU
  119 15 French Creole C LAYVYE
  119 16 French Creole D LAYVYE
  119 23 Catalan         RIU
  119 20 Spanish         RIO
  119 12 Provencal       RIBIERO
  119 14 Walloon         RIVIRE
  119 13 French          RIVIERE
  119 29 Frisian         REVIER, RIVIER
  119 28 Flemish         RIVIER
  119 21 Portuguese ST   RIO
  119 22 Brazilian       RIO
b                      201
c                         200  2  201
c                         201  2  202
  119 08 Rumanian List   RIU, FLUVIU
b                      202
c                         201  2  202
  119 18 Sardinian L     FLUMEN
  119 10 Italian         FIUME
  119 19 Sardinian C     FLUMINI
  119 11 Ladin           FLUM
  119 24 German ST       FLUSS
  119 32 Swedish List    FLOD
  119 33 Danish          FLOD
b                      203
c                         203  2  204
  119 59 Gujarati        NEDI
  119 58 Marathi         NEDI
  119 63 Bengali         NODI
  119 62 Hindi           NEDI
b                      204
c                         203  2  204
c                         204  2  205
  119 64 Nepali List     DARIYA, NAD
  119 60 Panjabi ST      NEDI, DERYA
b                      205
c                         204  2  205
  119 61 Lahnda          DERYA
b                      206
c                         206  2  207
  119 75 Waziri          DARYOB, TOI
  119 78 Baluchi         DIRA
  119 79 Wakhi           DERIO
b                      207
c                         206  2  207
c                         207  2  208
  119 77 Tadzik          DAR E, RUD
b                      208
c                         207  2  208
  119 74 Afghan          RUD, SIND
a 120 ROAD
b                      001
  120 55 Gypsy Gk        DROM
  120 70 Greek K         HODOS
  120 53 Bulgarian       NET
  120 56 Singhalese      PARA
  120 77 Tadzik          POX
  120 76 Persian List    RAH
  120 37 English ST      ROAD
  120 12 Provencal       ROUTO
b                      002
  120 41 Latvian         CELS
  120 39 Lithuanian O    KELIAS
  120 40 Lithuanian ST   KELIAS
b                      003
  120 57 Kashmiri        WATH
  120 64 Nepali List     BATO
  120 65 Khaskura        BATO
b                      004
  120 91 SLOVENIAN P     POT
  120 86 UKRAINIAN P     PUT
  120 89 SLOVAK P        PUT
  120 92 SERBOCROATIAN P PUT
  120 54 Serbocroatian   PUT
  120 85 RUSSIAN P       PUT
  120 43 Lusatian L      PUS
  120 44 Lusatian U      PUC
  120 93 MACEDONIAN P    PAT
  120 94 BULGARIAN P     PUT
  120 52 Macedonian      PAT/CADE
b                      005
  120 47 Czech E         CESTA
  120 42 Slovenian       CESTA
  120 46 Slovak          CESTA
  120 45 Czech           CESTA
b                      006
  120 20 Spanish         CAMINO
  120 15 French Creole C SIME
  120 13 French          CHEMIN
  120 16 French Creole D SIME
  120 22 Brazilian       CAMINHO
  120 23 Catalan         CAMI, SENDER
b                      007
  120 71 Armenian Mod    CAMPA, CANAPARH, ULI
  120 72 Armenian List   JANBA
b                      008
  120 14 Walloon         VOYE
  120 17 Sardinian N     VIA
  120 18 Sardinian L     VIA
  120 11 Ladin           VIA
b                      009
  120 84 Albanian C      DHROM
  120 83 Albanian K      DHROM
b                      010
  120 75 Waziri          LYAR
  120 74 Afghan          LAR
b                      011
  120 78 Baluchi         DAG
  120 73 Ossetic         FAENDAG
  120 79 Wakhi           VEDEK
b                      012
  120 01 Irish A         BOTHAR
  120 02 Irish B         BOTHAR, -AIR
b                      013
  120 10 Italian         STRADA
  120 21 Portuguese ST   ESTRADA
b                      014
  120 05 Breton List     HENT
  120 04 Welsh C         HEOL
  120 03 Welsh N         FFORDD, HEOL
  120 06 Breton SE       HENT
  120 07 Breton ST       HENT
b                      015
  120 67 Greek MD        DROMOS
  120 69 Greek D         DROMOS
  120 66 Greek ML        DROMOS
  120 68 Greek Mod       DHROMOS
b                      016
  120 38 Takitaki        PASI
  120 29 Frisian         PAED
b                      017
  120 08 Rumanian List   DRUM, CALE
  120 09 Vlach           KALE
b                      200
c                         200  2  201
  120 58 Marathi         RESTA
  120 59 Gujarati        RESTO
b                      201
c                         200  2  201
c                         201  2  202
  120 62 Hindi           RASTA, SEREK
  120 63 Bengali         SOROK, RASTA
b                      202
c                         201  2  202
  120 60 Panjabi ST      SEREK
  120 61 Lahnda          SEREK
b                      203
c                         203  2  204
  120 51 Russian         DOROGA
  120 88 POLISH P        DROGA
  120 50 Polish          DROGA
  120 87 BYELORUSSIAN P  DAROHA
  120 90 CZECH P         DRAHA
b                      204
c                         203  2  204
c                         204  2  205
  120 48 Ukrainian       DOROHA, SLJAX
b                      205
c                         204  2  205
  120 49 Byelorussian    SLJAX
b                      206
c                         206  2  207
  120 19 Sardinian C     ARRUGA
b                      207
c                         206  2  207
c                         207  2  208
c                         207  3  209
  120 82 Albanian G      RRUGA, UDHA
  120 95 ALBANIAN        UDHA, RRUGA
b                      208
c                         207  2  208
c                         208  3  209
  120 81 Albanian Top    UDHE
  120 80 Albanian T      UDHE
b                      209
c                         207  3  209
c                         208  3  209
  120 35 Icelandic ST    VEGR
  120 24 German ST       WEG, LANDSTRASSE
  120 34 Riksmal         VEI
  120 32 Swedish List    VAG
  120 33 Danish          VEJ
  120 36 Faroese         VEGUR
  120 28 Flemish         WEG
  120 25 Penn. Dutch     WAYK
  120 26 Dutch List      WEG
  120 27 Afrikaans       WEG
  120 30 Swedish Up      VAG
  120 31 Swedish VL      VAG
a 121 ROOT
b                      000
  121 52 Macedonian
b                      001
  121 78 Baluchi         PAR
  121 55 Gypsy Gk        RIZA
  121 63 Bengali         SEKOR
  121 73 Ossetic         UIDAG, BYN
b                      002
  121 41 Latvian         SAKNE
  121 39 Lithuanian O    SAKNIS
  121 40 Lithuanian ST   SAKNIS
b                      003
  121 07 Breton ST       GWRIZIENN
  121 06 Breton SE       GROUIEN
  121 05 Breton List     GWRIZIENN
  121 04 Welsh C         GWREIDDYN
  121 03 Welsh N         GWREIDDYN
  121 01 Irish A         PREAMH
  121 02 Irish B         PREAMH, -A
  121 09 Vlach           ARIDICINA
  121 18 Sardinian L     RAIGHINA
  121 17 Sardinian N     RAIKINA
  121 15 French Creole C HWASIN
  121 08 Rumanian List   RADACINA
  121 23 Catalan         ARREL, REL
  121 19 Sardinian C     ARREZINA
  121 10 Italian         RADICE
  121 20 Spanish         RAIZ
  121 12 Provencal       RACINO
  121 14 Walloon         RECENE
  121 16 French Creole D WASIN
  121 13 French          RACINE
  121 82 Albanian G      RRAJA
  121 95 ALBANIAN        RRAJA
  121 21 Portuguese ST   RAIZ
  121 22 Brazilian       RAIZ
  121 81 Albanian Top    RENE
  121 80 Albanian T      RENJE
  121 83 Albanian K      RENE
  121 84 Albanian C      REN
  121 24 German ST       WURZEL
  121 29 Frisian         WOARTEL
  121 28 Flemish         WORTEL
  121 25 Penn. Dutch     WOTZEL
  121 26 Dutch List      WORTEL
  121 27 Afrikaans       WORTEL
  121 31 Swedish VL      ROT
  121 30 Swedish Up      ROT
  121 35 Icelandic ST    ROT
  121 34 Riksmal         ROT
  121 32 Swedish List    ROT
  121 33 Danish          ROD
  121 36 Faroese         ROT
  121 37 English ST      ROOT
  121 38 Takitaki        LOETOE
  121 68 Greek Mod       RIZA
  121 66 Greek ML        HRIDZA
  121 70 Greek K         RIDZA
  121 67 Greek MD        RIDZA
  121 69 Greek D         RIDZA
b                      004
  121 88 POLISH P        KORZEN
  121 51 Russian         KOREN
  121 85 RUSSIAN P       KOREN
  121 54 Serbocroatian   KOREN
  121 92 SERBOCROATIAN P KOREN
  121 46 Slovak          KOREN
  121 89 SLOVAK P        KOREN
  121 42 Slovenian       KORERUKA
  121 91 SLOVENIAN P     KOREN
  121 86 UKRAINIAN P     KORIN
  121 50 Polish          KORZEN
  121 93 MACEDONIAN P    KOREN
  121 44 Lusatian U      KORJEN
  121 43 Lusatian L      KOREN
  121 90 CZECH P         KOREN
  121 45 Czech           KOREN
  121 87 BYELORUSSIAN P  KORAN
  121 94 BULGARIAN P     KOREN
  121 49 Byelorussian    KARIN'
  121 47 Czech E         KORENY
  121 48 Ukrainian       KORIN', KORINNJA
  121 53 Bulgarian       KOREN
b                      005
  121 71 Armenian Mod    ARMAT
  121 72 Armenian List   ARMAD
b                      200
c                         200  2  201
  121 64 Nepali List     JARO
  121 61 Lahnda          JER
  121 60 Panjabi ST      JER
b                      201
c                         200  2  201
c                         201  2  202
  121 65 Khaskura        JARA, MULA
b                      202
c                         201  2  202
  121 62 Hindi           MUL
  121 58 Marathi         MUL
  121 59 Gujarati        MUL
  121 56 Singhalese      MULA
  121 57 Kashmiri        MUL
b                      203
c                         203  2  204
  121 79 Wakhi           WIUX
  121 75 Waziri          WEKH, BEKH
b                      204
c                         203  2  204
c                         204  2  205
  121 74 Afghan          BEX, RISA
b                      205
c                         204  2  205
  121 11 Ladin           RISCH
  121 76 Persian List    RISHE
  121 77 Tadzik          RESA, ASL, ASOS, WAFS
a 122 ROPE
b                      001
  122 77 Tadzik          ARWAMCINI
  122 73 Ossetic         BAENDAEN
  122 72 Armenian List   CHUVAN
  122 08 Rumanian List   FRINGHIE, ODGON
  122 93 MACEDONIAN P    JAZE
  122 17 Sardinian N     KANNAU
  122 54 Serbocroatian   KONOPAC
  122 56 Singhalese      LANUWA
  122 52 Macedonian      ORTOMA
  122 71 Armenian Mod    PARAN, T`OK
  122 25 Penn. Dutch     SCHTRICK
  122 24 German ST       SEIL
  122 55 Gypsy Gk        SKINI
  122 42 Slovenian       SPAH
  122 83 Albanian K      TELH
  122 38 Takitaki        TETEI
  122 53 Bulgarian       VEZE
b                      002
  122 07 Breton ST       KORDENN
  122 05 Breton List     KORDENN
  122 06 Breton SE       KORDENN
b                      003
  122 64 Nepali List     DORI
  122 59 Gujarati        DORERU
  122 58 Marathi         DOR, DORI
  122 63 Bengali         DORI
  122 65 Khaskura        JIURI, DORI, SUTARI
b                      004
  122 01 Irish A         TEAD, ROPA
  122 02 Irish B         TEAD
b                      005
  122 86 UKRAINIAN P     VIRJOUKA
  122 91 SLOVENIAN P     VRV
  122 92 SERBOCROATIAN P VRVCA
  122 85 RUSSIAN P       VER OVKA
  122 51 Russian         VEREVKA
  122 49 Byelorussian    VJAROWKA
  122 40 Lithuanian ST   VIRVE
  122 39 Lithuanian O    VIRVE
  122 41 Latvian         VIRVE
  122 94 BULGARIAN P     VRUV
  122 87 BYELORUSSIAN P  V AROUKA
b                      006
  122 27 Afrikaans       TOU
  122 28 Flemish         TOUW
  122 29 Frisian         TOU
  122 34 Riksmal         TAU
  122 26 Dutch List      TOUW, KOORD
b                      007
  122 30 Swedish Up      REP
  122 31 Swedish VL      REP
  122 04 Welsh C         RHAFF
  122 03 Welsh N         RHAFF
  122 35 Icelandic ST    REIPI
  122 32 Swedish List    REP, LINA
  122 36 Faroese         REIP
  122 33 Danish          REP
  122 37 English ST      ROPE
b                      008
  122 09 Vlach           FUNI
  122 18 Sardinian L     FUNE
  122 19 Sardinian C     FUNI
b                      009
  122 74 Afghan          PERAJ
  122 75 Waziri          PERAI
b                      010
  122 22 Brazilian       CORDA
  122 21 Portuguese ST   CORDA, BARACO
  122 10 Italian         CORDA
  122 23 Catalan         CORDA, CORDILL
  122 20 Spanish         CUERDA
  122 12 Provencal       CORDO
  122 14 Walloon         CWEDE
  122 16 French Creole D KOD
  122 13 French          CORDE
  122 11 Ladin           CORDA
  122 15 French Creole C KOD, LIN
b                      011
  122 68 Greek Mod       SKINI
  122 66 Greek ML        SKOINI
  122 70 Greek K         CHONDRON SCHOINION
  122 67 Greek MD        SKOINI, PALAMARI
  122 69 Greek D         SKOINI
b                      012
  122 81 Albanian Top    TERKUZE
  122 84 Albanian C      TRIKUZ
b                      013
  122 80 Albanian T      LITAR
  122 82 Albanian G      LITARI
  122 95 ALBANIAN        LITARI, KONOPI
b                      100
  122 76 Persian List    TANAB
  122 79 Wakhi           SIVEN, TUNOV, DEROWI, NUS
b                      200
c                         200  3  400
  122 61 Lahnda          RESSI
  122 62 Hindi           RESSA
  122 60 Panjabi ST      RESSA
b                      400
c                         200  3  400
  122 57 Kashmiri        RAZ
  122 78 Baluchi         REZ
b                      201
c                         201  2  202
  122 89 SLOVAK P        POVRAZ
  122 88 POLISH P        POWROZ
  122 45 Czech           PROVAZ
  122 90 CZECH P         PROVAZ
  122 43 Lusatian L      POWEZ
  122 44 Lusatian U      POWJAC
  122 47 Czech E         SPAGAT, PROVAS
b                      202
c                         201  2  202
c                         202  2  203
  122 46 Slovak          POVRAZ, MOTUZ
b                      203
c                         202  2  203
c                         203  3  204
  122 48 Ukrainian       LYNVA, SNUR, MOTUZ
b                      204
c                         203  3  204
  122 50 Polish          SZNUR
a 123 ROTTEN (LOG)
b                      000
  123 69 Greek D
  123 67 Greek MD
  123 70 Greek K
  123 59 Gujarati
  123 65 Khaskura
b                      001
  123 38 Takitaki        PORI
  123 73 Ossetic         AEMBYD
  123 56 Singhalese      DIRACCA
  123 57 Kashmiri        DODURU
  123 02 Irish B         DREOIGHTE
  123 78 Baluchi         GALAGH
  123 42 Slovenian       GRULA
  123 17 Sardinian N     ISKUSSERTU
  123 01 Irish A         LOBHTHA
  123 64 Nepali List     MAKINU (VB.), BISADDE
  123 10 Italian         MARCIO
  123 58 Marathi         NASKA
  123 71 Armenian Mod    NEXAC
  123 79 Wakhi           PITK
  123 72 Armenian List   PUDAZ
  123 63 Bengali         POCE+JAOA (TO ROT)
b                      002
  123 13 French          POURRI
  123 22 Brazilian       PODRE
  123 21 Portuguese ST   PODRE
  123 20 Spanish         PODRIDO
  123 12 Provencal       POURRI, COUNFI, IDO
  123 14 Walloon         (TO ROT) POURI
  123 16 French Creole D PUWI
  123 23 Catalan         PUDRIT, CORROMPUT
  123 11 Ladin           PUTIRD
  123 08 Rumanian List   PUTRED
  123 15 French Creole C PUHWI
  123 09 Vlach           ASPARTU, PRUDITU
b                      003
  123 04 Welsh C         PWDR
  123 03 Welsh N         PWDR, PYDREDIG
b                      004
  123 86 UKRAINIAN P     HNYLYJ
  123 91 SLOVENIAN P     GNIL
  123 89 SLOVAK P        HNILY
  123 46 Slovak          ZHNITY
  123 93 MACEDONIAN P    GNIL
  123 50 Polish          ZGNILY
  123 88 POLISH P        ZGNILY
  123 51 Russian         GNILOJ
  123 85 RUSSIAN P       GNILOJ
  123 54 Serbocroatian   GNJIO
  123 92 SERBOCROATIAN P GNJIO
  123 44 Lusatian U      HNILY
  123 43 Lusatian L      GNILY
  123 90 CZECH P         SHNILY
  123 87 BYELORUSSIAN P  HNILY
  123 45 Czech           SHNILY, ZETLELY
  123 94 BULGARIAN P     GNIL
  123 52 Macedonian      IZGNIEN, SKAPAN, GNILI
  123 47 Czech E         HNYILE
  123 49 Byelorussian    HNILY
  123 48 Ukrainian       HNYLYJ, ZIPSOVANYJ
  123 53 Bulgarian       GNILO
b                      005
  123 55 Gypsy Gk        SAPYO
  123 41 Latvian         SAPUVIS, SATRUDEJIS
  123 39 Lithuanian O    SUPUVES
  123 40 Lithuanian ST   SUPUVES
  123 66 Greek ML        SAPIOS
  123 68 Greek Mod       SAPYOS
b                      006
  123 24 German ST       FAUL
  123 25 Penn. Dutch     FAUL
b                      007
  123 77 Tadzik          PUSIDA
  123 76 Persian List    PUSIDE
b                      008
  123 19 Sardinian C     MALU
  123 18 Sardinian L     MALZU
b                      009
  123 75 Waziri          WROST
  123 74 Afghan          VROST
b                      010
  123 61 Lahnda          SERI
  123 62 Hindi           SERA
  123 60 Panjabi ST      SEREA HOYA
b                      011
  123 05 Breton List     BREIN
  123 06 Breton SE       BREIN
  123 07 Breton ST       BREIN
b                      200
c                         200  2  201
  123 30 Swedish Up      RUTTEN
  123 31 Swedish VL      ROTAN
  123 37 English ST      ROTTEN
  123 34 Riksmal         ROTTEN
  123 32 Swedish List    RUTTEN
  123 33 Danish          RAADDEN
  123 29 Frisian         ROTSJE
  123 28 Flemish         VERROTTEN
  123 26 Dutch List      VERROT, VERSLETEN
  123 27 Afrikaans       ROT, VERROT, BEDERF, BEDERWE
b                      201
c                         200  2  201
c                         201  2  202
  123 36 Faroese         FUGVIN, ROTIN
b                      202
c                         201  2  202
  123 35 Icelandic ST    FUINN
b                      203
c                         203  2  204
  123 81 Albanian Top    KALHBUR
  123 80 Albanian T      I, E KALBUR
  123 83 Albanian K      I KALHBETE
  123 84 Albanian C      I-KALBET
b                      204
c                         203  2  204
c                         204  2  205
  123 82 Albanian G      DEMEL, KALBET, PERTATS
b                      205
c                         204  2  205
  123 95 ALBANIAN        PERTATS, DEMEL
a 124 RUB
b                      000
  124 17 Sardinian N
  124 25 Penn. Dutch
b                      001
  124 41 Latvian         BERZT
  124 20 Spanish         FROTAR, ESTREGAR
  124 83 Albanian K      KRUAN
  124 56 Singhalese      MADINAWA
  124 79 Wakhi           MAND, SUX
  124 61 Lahnda          MANEN
  124 35 Icelandic ST    NUA
  124 73 Ossetic         SAERFYN, XAFYN
  124 11 Ladin           SFRUSCHER
  124 55 Gypsy Gk        TRIVO
b                      002
  124 15 French Creole C FWOTE
  124 13 French          FROTTER
  124 16 French Creole D FWOTE
  124 14 Walloon         FROTER
  124 12 Provencal       FRETA
  124 22 Brazilian       ESFREGAR
  124 21 Portuguese ST   ESFREGAR
  124 23 Catalan         FREGAR
  124 10 Italian         FREGARE
  124 19 Sardinian C     FRIGAI
  124 08 Rumanian List   (SE) FRECA (DE)
  124 18 Sardinian L     FRIGARE
  124 09 Vlach           FREK
b                      003
  124 68 Greek Mod       TRIVO
  124 66 Greek ML        TRIBO
  124 70 Greek K         TRIBO
  124 67 Greek MD        TRIBO
  124 69 Greek D         TRIBO
  124 53 Bulgarian       TERKANE
  124 91 SLOVENIAN P     TRETI
  124 86 UKRAINIAN P     TERTY
  124 87 BYELORUSSIAN P  CERCI
  124 49 Byelorussian    CERCI, SARAVAC'
  124 48 Ukrainian       TERTJA, NATYRANNJA
  124 45 Czech           TRITI
  124 90 CZECH P         TRITI
  124 43 Lusatian L      TRES
  124 44 Lusatian U      TREC
  124 93 MACEDONIAN P    TRIAM
  124 50 Polish          TRZEC
  124 88 POLISH P        TRZEC
  124 51 Russian         TERET
  124 85 RUSSIAN P       TERET
  124 54 Serbocroatian   TRENJE
  124 92 SERBOCROATIAN P TRTI
  124 46 Slovak          TRET
  124 89 SLOVAK P        TRIET
  124 52 Macedonian      TRIE
  124 94 BULGARIAN P     TRIJA
  124 40 Lithuanian ST   TRINTI
  124 39 Lithuanian O    TRINTI
b                      004
  124 30 Swedish Up      GNIDA, GNUGGA
  124 31 Swedish VL      GNI, GNOG
  124 34 Riksmal         GNI
  124 36 Faroese         GNIGGJA
  124 33 Danish          GNIDE
  124 32 Swedish List    GNUGGA, GNIDA
b                      005
  124 62 Hindi           REGERNA
  124 60 Panjabi ST      REGERNA
b                      006
  124 05 Breton List     RENVIA, RIMIA, SKRABA, FROTA, RUZA
  124 07 Breton ST       FROTAN, RIMIAN
  124 06 Breton SE       FROTEIN
b                      007
  124 81 Albanian Top    FERKON, AOR. FERKOVA
  124 80 Albanian T      ME FERKUAR
  124 84 Albanian C      FERKON
  124 82 Albanian G      FERKOJ
  124 95 ALBANIAN        FERKOJ
b                      008
  124 75 Waziri          MASHEL
  124 74 Afghan          MUSEL
b                      009
  124 04 Welsh C         RHWBIO
  124 03 Welsh N         RHWBIO, CRAFU
b                      010
  124 01 Irish A         CUIMILT
  124 02 Irish B         CUIMLIM
b                      011
  124 47 Czech E         MASTYIT
  124 42 Slovenian       MAZATI, DRGNI
b                      012
  124 71 Armenian Mod    SP`EL, K`OREL
  124 72 Armenian List   SHUPEL
b                      200
c                         200  2  201
  124 77 Tadzik          SOIGAN, SUDAN, MOLIDAN
  124 76 Persian List    MALIDAN
  124 78 Baluchi         MALAGH, MALITHA, MALTHA
  124 57 Kashmiri        MALUN, MATHUN
  124 65 Khaskura        MICHNU, MALNU
b                      201
c                         200  2  201
c                         201  2  202
  124 64 Nepali List     GHASNU, MALNU, MARNU
b                      202
c                         201  2  202
  124 59 Gujarati        GHESWU
  124 58 Marathi         GHASNE
  124 63 Bengali         GHOSA
b                      203
c                         203  2  204
  124 38 Takitaki        ROBI LOBI
  124 37 English ST      RUB
  124 24 German ST       REIBEN
  124 29 Frisian         WRIUWE
  124 26 Dutch List      WRIJVEN
b                      204
c                         203  2  204
c                         204  2  205
  124 27 Afrikaans       VRYF, VRYWE, SKUUR
b                      205
c                         204  2  205
  124 28 Flemish         SCHUREN
c                         200  2  201
c                         201  2  202
a 125 SALT
b                      001
  125 73 Ossetic         CAEXX
  125 62 Hindi           NEMEK
  125 78 Baluchi         WHADH, WAHADH
b                      002
  125 71 Armenian Mod    AL
  125 72 Armenian List   AGH
  125 30 Swedish Up      SALT
  125 31 Swedish VL      SALT
  125 09 Vlach           SARE
  125 17 Sardinian N     SALE
  125 18 Sardinian L     SALE
  125 91 SLOVENIAN P     SOL
  125 86 UKRAINIAN P     SIL
  125 15 French Creole C SEL
  125 42 Slovenian       SOV
  125 51 Russian         SOL
  125 85 RUSSIAN P       SOL
  125 54 Serbocroatian   SOL
  125 92 SERBOCROATIAN P SO
  125 46 Slovak          SOL
  125 89 SLOVAK P        SOL
  125 50 Polish          SOL
  125 88 POLISH P        SOL
  125 93 MACEDONIAN P    SOL
  125 44 Lusatian U      SOL
  125 43 Lusatian L      SOL
  125 90 CZECH P         SUL
  125 45 Czech           SUL
  125 87 BYELORUSSIAN P  SOL
  125 94 BULGARIAN P     SOL
  125 41 Latvian         SALS
  125 69 Greek D         HALATI
  125 67 Greek MD        HALATI
  125 70 Greek K         HALAS
  125 66 Greek ML        HALATI
  125 68 Greek Mod       ALATI
  125 08 Rumanian List   SARE
  125 11 Ladin           SAL
  125 10 Italian         SALE
  125 19 Sardinian C     SALI
  125 23 Catalan         SAL
  125 20 Spanish         SAL
  125 12 Provencal       SAU
  125 14 Walloon         SE
  125 16 French Creole D SEL
  125 13 French          SEL
  125 01 Irish A         SALANN
  125 02 Irish B         SALANN
  125 03 Welsh N         HALEN
  125 04 Welsh C         HALEN
  125 05 Breton List     HOLEN, C'HOALEN
  125 06 Breton SE       HOLEN
  125 07 Breton ST       HOLEN
  125 24 German ST       SALZ
  125 35 Icelandic ST    SALT
  125 34 Riksmal         SALT
  125 32 Swedish List    SALT
  125 33 Danish          SALT
  125 36 Faroese         SALT
  125 29 Frisian         SALT
  125 28 Flemish         ZOUT
  125 25 Penn. Dutch     SOLSZ
  125 26 Dutch List      ZOUT
  125 27 Afrikaans       SOUT
  125 52 Macedonian      SOL
  125 47 Czech E         SUL
  125 49 Byelorussian    SOL'
  125 48 Ukrainian       SIL'
  125 53 Bulgarian       SOL
  125 21 Portuguese ST   SAL
  125 22 Brazilian       SAL
  125 38 Takitaki        ZOUTOE
  125 37 English ST      SALT
b                      003
  125 79 Wakhi           NIMUK
  125 77 Tadzik          NAMAK
  125 76 Persian List    NAMAK
b                      004
  125 74 Afghan          MALGA
  125 75 Waziri          MOLGA
b                      005
  125 81 Albanian Top    KRIPE
  125 80 Albanian T      KRIPE
  125 83 Albanian K      KRIPE
  125 84 Albanian C      KRIP
  125 82 Albanian G      KRYPA
  125 95 ALBANIAN        KRYP
b                      006
  125 39 Lithuanian O    DRUSKA
  125 40 Lithuanian ST   DRUSKA
b                      200
c                         200  2  201
  125 59 Gujarati        MITHU
b                      201
  125 58 Marathi         MITH, LON
b                      202
c                         201  2  202
  125 55 Gypsy Gk        LON
  125 56 Singhalese      LUNU
  125 57 Kashmiri        NUN
  125 64 Nepali List     NUN
  125 61 Lahnda          LUN
  125 63 Bengali         NUN, LOBON
  125 60 Panjabi ST      LUN
  125 65 Khaskura        NUN
a 126 SAND
b                      000
  126 77 Tadzik
b                      001
  126 55 Gypsy Gk        KISAY
  126 81 Albanian Top    KUM
  126 79 Wakhi           LUWORC
  126 08 Rumanian List   NISIP
  126 84 Albanian C      RER
  126 06 Breton SE       SABL
  126 76 Persian List    SHEN
  126 23 Catalan         SORRA
  126 73 Ossetic         YZMIC
b                      002
  126 94 BULGARIAN P     P ASUK
  126 87 BYELORUSSIAN P  P ASOK
  126 45 Czech           PISEK
  126 90 CZECH P         PISEK
  126 43 Lusatian L      PESK
  126 44 Lusatian U      PESK
  126 93 MACEDONIAN P    PESOK
  126 50 Polish          PIASEK
  126 88 POLISH P        PIASEK
  126 51 Russian         PESOK
  126 85 RUSSIAN P       PESOK
  126 54 Serbocroatian   PESAK
  126 92 SERBOCROATIAN P PESAK
  126 46 Slovak          PIESOK
  126 89 SLOVAK P        PIESOK
  126 42 Slovenian       PESK
  126 91 SLOVENIAN P     PESEK
  126 86 UKRAINIAN P     PISOK
  126 52 Macedonian      PESOK
  126 47 Czech E         PISEK
  126 49 Byelorussian    PJASOK
  126 48 Ukrainian       PISOK
  126 53 Bulgarian       PJASEK
b                      003
  126 40 Lithuanian ST   SMELIS, SMELYS
  126 39 Lithuanian O    SMELIS
  126 41 Latvian         SMILTIS
b                      004
  126 30 Swedish Up      SAND
  126 31 Swedish VL      SAN
  126 24 German ST       SAND
  126 35 Icelandic ST    SANDR
  126 34 Riksmal         SAND
  126 32 Swedish List    SAND
  126 33 Danish          SAND
  126 36 Faroese         SANDUR
  126 29 Frisian         SAN
  126 28 Flemish         ZAND
  126 25 Penn. Dutch     SONNDT
  126 26 Dutch List      ZAND
  126 27 Afrikaans       SAND
  126 38 Takitaki        SANTI
  126 37 English ST      SAND
b                      005
  126 02 Irish B         GAINIMH
  126 01 Irish A         GAINEAMH
b                      006
  126 68 Greek Mod       AMOS
  126 66 Greek ML        HAMMOS
  126 70 Greek K         AMMOS
  126 67 Greek MD        AMMOS
  126 69 Greek D         HAMMOS
b                      007
  126 05 Breton List     TRAEZ
  126 07 Breton ST       TRAEZH
b                      008
  126 03 Welsh N         TYWOD
  126 04 Welsh C         TYWOD
b                      009
  126 82 Albanian G      RANA
  126 95 ALBANIAN        RANA
b                      010
  126 71 Armenian Mod    AWAZ
  126 72 Armenian List   AVAZ
b                      011
  126 80 Albanian T      SHUR
  126 83 Albanian K      SUUR
b                      200
c                         200  2  201
  126 64 Nepali List     RETI
  126 61 Lahnda          RET
  126 59 Gujarati        RETI
  126 60 Panjabi ST      RET
b                      201
c                         200  2  201
c                         201  2  202
  126 58 Marathi         VALU, RETI
b                      202
c                         201  2  202
  126 56 Singhalese      VALI
  126 63 Bengali         BALU
  126 62 Hindi           BALU
  126 65 Khaskura        BALUWA
b                      203
c                         203  2  204
  126 75 Waziri          SHEGGA
  126 57 Kashmiri        SEKH
b                      204
c                         203  2  204
c                         204  2  205
  126 74 Afghan          SEGA, RIG
b                      205
c                         204  2  205
  126 78 Baluchi         REKH
b                      206
c                         206  2  207
  126 15 French Creole C SAB
  126 11 Ladin           SABLUN
  126 14 Walloon         SAVION
  126 16 French Creole D SAB
  126 13 French          SABLE
  126 12 Provencal       SABLO
b                      207
c                         206  2  207
c                         207  2  208
  126 10 Italian         SABBIA, RENA
b                      208
c                         207  2  208
  126 22 Brazilian       AREIA
  126 21 Portuguese ST   AREA, AREIA
  126 20 Spanish         ARENA
  126 19 Sardinian C     ARENA
  126 09 Vlach           ARINE
  126 18 Sardinian L     RENA
  126 17 Sardinian N     RENA
a 127 TO SAY
b                      000
  127 36 Faroese
b                      001
  127 02 Irish B         DEIRIM
  127 73 Ossetic         DZURYN, (NYXAC, KAENYN)
  127 78 Baluchi         GUSHAGH, GUSTA, GWASHAGH, GWASHTA
  127 58 Marathi         MHENNE.
  127 01 Irish A         RADH
  127 38 Takitaki        TAKI
  127 79 Wakhi           XAN
  127 57 Kashmiri        WANUN
b                      002
  127 76 Persian List    GOFTAN
  127 77 Tadzik          GUFTAN, GAP ZADAN
b                      003
  127 13 French          DIRE
  127 15 French Creole C DI
  127 11 Ladin           DIR
  127 16 French Creole D DI
  127 14 Walloon         DIRE
  127 12 Provencal       DIRE
  127 20 Spanish         DECIR
  127 23 Catalan         DIR
  127 10 Italian         DIRE
  127 22 Brazilian       DIZER
  127 21 Portuguese ST   DIZER
  127 08 Rumanian List   A ZICE, A SPUNE
  127 09 Vlach           ZYKU
b                      004
  127 89 SLOVAK P        MLUVIT
  127 50 Polish          MOWIC
b                      005
  127 24 German ST       SAGEN
  127 33 Danish          SIGE
  127 37 English ST      TO SAY
  127 32 Swedish List    SAGA
  127 34 Riksmal         SI
  127 35 Icelandic ST    SEGJA
  127 27 Afrikaans       SE
  127 26 Dutch List      ZEGGEN
  127 25 Penn. Dutch     SAWG
  127 28 Flemish         ZEGGEN
  127 29 Frisian         SIZZE
  127 30 Swedish Up      SAJA, SAGA
  127 31 Swedish VL      SAGA
  127 39 Lithuanian O    SAKYTI
  127 40 Lithuanian ST   SAKYTI
  127 41 Latvian         SACIT, TEIKT, RUNAT
b                      006
  127 71 Armenian Mod    ASEL
  127 72 Armenian List   USELL
b                      007
  127 66 Greek ML        LEGO
  127 70 Greek K         LEGO
  127 67 Greek MD        LEGO, LEO
  127 69 Greek D         LEO
  127 68 Greek Mod       LEO
b                      008
  127 74 Afghan          VAJEL
  127 75 Waziri          WEYEL
b                      009
  127 07 Breton ST       LAVAROUT
  127 06 Breton SE       LARET
  127 05 Breton List     LAVAROUT, LAVARET, LARET
b                      010
  127 03 Welsh N         DWEUD
  127 04 Welsh C         DWEUD, DYWEDYD
b                      011
  127 65 Khaskura        BHANNU
  127 64 Nepali List     BHANNU
  127 55 Gypsy Gk        PHENAV
b                      012
  127 84 Albanian C      THOM
  127 82 Albanian G      DIFTOJ, THOM ( THAN = INF.)
  127 95 ALBANIAN        THOM (THAN = INF.)
  127 81 Albanian Top    THEM, AOR. THASE
  127 80 Albanian T      ME THENE
  127 83 Albanian K      THOM (AOR. THASE, PPLE. THENE)
b                      013
  127 17 Sardinian N     NARRERE
  127 18 Sardinian L     NARRER
  127 19 Sardinian C     NAI
b                      200
c                         200  2  201
c                         200  2  204
  127 45 Czech           RICI
  127 90 CZECH P         RICI
  127 44 Lusatian U      RJEC
  127 43 Lusatian L      RAC
  127 88 POLISH P        RZEC
  127 92 SERBOCROATIAN P RECI
  127 42 Slovenian       RECI
  127 91 SLOVENIAN P     RECI
  127 47 Czech E         POVIT, REKNUT
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  2  204
  127 52 Macedonian      IZUSTI/KAZE/VELI/RECE
b                      202
c                         201  2  202
c                         202  2  203
  127 93 MACEDONIAN P    KAZAM
  127 53 Bulgarian       DA KAZVA
  127 49 Byelorussian    SKAZAC'
  127 94 BULGARIAN P     KAZVAM
  127 87 BYELORUSSIAN P  KAZAC
  127 54 Serbocroatian   KAZATI
  127 85 RUSSIAN P       SKAZAT
  127 86 UKRAINIAN P     SKAZATY
b                      203
c                         201  2  203
c                         202  2  203
c                         203  2  204
c                         203  2  205
  127 48 Ukrainian       SKAZATY, HOOORYTY
b                      204
c                         200  2  204
c                         201  2  204
c                         203  2  204
c                         204  2  205
  127 46 Slovak          HOVORIT , RIEKNUT
b                      205
c                         203  2  205
c                         204  2  205
  127 51 Russian         GOVORIT
b                      206
c                         206  3  400
  127 62 Hindi           KEHNA
  127 59 Gujarati        KEHEWU
  127 60 Panjabi ST      KENA
  127 56 Singhalese      KIYANAWA
b                      400
c                         206  3  400
  127 61 Lahnda          AKHEN
  127 63 Bengali         KOOA
a 128 SCRATCH (ITCH)
b                      000
  128 09 Vlach
  128 73 Ossetic
  128 63 Bengali
b                      001
  128 79 Wakhi           DRUP-, CUNGOL DI-
  128 80 Albanian T      ME GERVROHTUR
  128 42 Slovenian       PODRGNI
  128 20 Spanish         RASCAR
  128 84 Albanian C      RASKAR
b                      002
  128 17 Sardinian N     GRATTARE TURA
  128 18 Sardinian L     RATTARE
  128 15 French Creole C GHWAFIYE
  128 11 Ladin           SGRATTER, GRATTER
  128 23 Catalan         GRATAR, FREGAR
  128 10 Italian         GRATTARE
  128 13 French          GRATTER
  128 16 French Creole D GWATE
  128 14 Walloon         GRETER
  128 12 Provencal       GRATA
b                      003
  128 35 Icelandic ST    KLORA
  128 34 Riksmal         KLO
  128 32 Swedish List    KLOSA, RIVA
  128 36 Faroese         KLORA
  128 30 Swedish Up      KLOSA, RISPA, RIVA
  128 31 Swedish VL      KLA
b                      004
  128 22 Brazilian       COCAR
  128 21 Portuguese ST   COCAR, RASPAR COM UNHAS
b                      005
  128 65 Khaskura        KANEAUNU
  128 64 Nepali List     KANYAUNU
b                      006
  128 24 German ST       KRATZEN
  128 33 Danish          KRADSE
  128 37 English ST      SCRATCH
  128 25 Penn. Dutch     GROTZ
  128 81 Albanian Top    KRUAN, AOR. KROVA
  128 83 Albanian K      KRUAN
  128 82 Albanian G      KRUJ
  128 95 ALBANIAN        KRUJ, KROUA
  128 38 Takitaki        KRASI, KRABOE
b                      007
  128 50 Polish          DRAPAC SIE
  128 48 Ukrainian       DRJAPADY, DRAPATY
b                      008
  128 71 Armenian Mod    CANKREL
  128 72 Armenian List   KEREL (GERK)
b                      009
  128 74 Afghan          GEREDEL
  128 75 Waziri          GARAWEL
b                      100
  128 52 Macedonian      DRASKA
  128 39 Lithuanian O    DRASKYTI
b                      101
  128 08 Rumanian List   A SCARPINA
  128 19 Sardinian C     SKRAFFI
b                      200
c                         200  2  201
c                         200  3  202
  128 91 SLOVENIAN P     CESATI
  128 92 SERBOCROATIAN P CESATI
  128 54 Serbocroatian   CESATI
  128 85 RUSSIAN P       CESAT
  128 51 Russian         CESAT SJA
  128 93 MACEDONIAN P    CESAM
  128 87 BYELORUSSIAN P  CASAC
  128 94 BULGARIAN P     CESA
  128 49 Byelorussian    CYXACCA
  128 53 Bulgarian       DA CESA
  128 68 Greek Mod       KSYO
  128 66 Greek ML        KSUNO
  128 70 Greek K         KSUO
  128 67 Greek MD        KSUNO
  128 69 Greek D         KSUNO
  128 41 Latvian         KASIT
b                      201
c                         200  2  201
c                         201  3  202
c                         201  2  203
c                         201  2  204
  128 40 Lithuanian ST   KASYTI, KRAPSTYTI
b                      202
c                         200  3  202
c                         201  3  202
  128 57 Kashmiri        KASHUN
  128 56 Singhalese      KASANAWA
b                      203
c                         201  2  203
c                         203  2  204
  128 86 UKRAINIAN P     SKREBTY
  128 89 SLOVAK P        SKRABAT
  128 46 Slovak          SKRABAT
  128 88 POLISH P        SKROBAC
  128 44 Lusatian U      SKRABAC
  128 43 Lusatian L      SKRABAS
  128 90 CZECH P         SKRABATI
  128 45 Czech           SKRABATI SE
  128 47 Czech E         SCRABAT
  128 03 Welsh N         CRAFU, COSI
  128 04 Welsh C         CRAFU
  128 06 Breton SE       KRAUAT
b                      204
c                         201  2  204
c                         203  2  204
c                         204  3  205
  128 05 Breton List     KRAVAT, SKRABA, DISKRABA, RIMIA
  128 07 Breton ST       SKRABAN, KRAVAT
b                      205
c                         204  3  205
c                         205  2  206
  128 02 Irish B         SCRIOBAIM, DO THOCHUR
b                      206
c                         205  2  206
  128 01 Irish A         TOCHAS
b                      207
c                         207  3  208
  128 28 Flemish         KRABBEN
  128 26 Dutch List      KRABLEN
  128 27 Afrikaans       KRAP
b                      208
c                         207  3  208
  128 29 Frisian         SKRAB, SKRAEB
b                      209
c                         209  3  210
  128 61 Lahnda          KHUJLAWEN
  128 59 Gujarati        KHEJEWALWU
  128 58 Marathi         KHAJEVNE
b                      210
c                         209  3  210
  128 55 Gypsy Gk        XALMAN
b                      211
c                         211  3  212
  128 60 Panjabi ST      KHURCENA
  128 62 Hindi           KHEROCNA
b                      212
c                         211  3  212
  128 77 Tadzik          XORIDAN
  128 76 Persian List    KHARIDAN
  128 78 Baluchi         KHARAGH, KHARITH
a 129 SEA (OCEAN)
b                      000
  129 79 Wakhi
  129 72 Armenian List
b                      001
  129 71 Armenian Mod    COV
  129 59 Gujarati        DERIGO
  129 56 Singhalese      MUHUDA
b                      002
  129 40 Lithuanian ST   JURA
  129 41 Latvian         JURA
b                      003
  129 77 Tadzik          BAXR
  129 74 Afghan          BAHR
b                      004
  129 01 Irish A         FAIRRGE
  129 02 Irish B         FAIRRGE
b                      005
  129 64 Nepali List     SAMUDRA
  129 61 Lahnda          SEMUNDER
  129 78 Baluchi         SAMUNDAR
  129 58 Marathi         SEMUDRE
  129 60 Panjabi ST      SEMUNDER
  129 65 Khaskura        SAMUNDAR
  129 63 Bengali         SAMUDRO, SAGOR
  129 62 Hindi           SEMUDR, SAGER
  129 57 Kashmiri        SODAR, SAGAR, SAMANDAR
b                      006
  129 75 Waziri          SAMUNDAR DARYOB
  129 76 Persian List    DARYA (OQYANUS)
b                      100
  129 73 Ossetic         DENDZYZ, FURD
  129 55 Gypsy Gk        DENIZI
b                      200
c                         200  2  201
  129 33 Danish          HAV
  129 31 Swedish VL      HAV
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
  129 32 Swedish List    HAV, SJO
  129 36 Faroese         SJOGVUR, HAV
b                      202
c                         201  2  202
c                         202  2  203
  129 37 English ST      SEA
  129 38 Takitaki        ZOUT-WATRA, ZEE
  129 27 Afrikaans       SEE
  129 26 Dutch List      ZEE
  129 25 Penn. Dutch     SAY
  129 28 Flemish         ZEE
  129 29 Frisian         SE
  129 30 Swedish Up      SJO
  129 35 Icelandic ST    SAER, SJOR
  129 34 Riksmal         SJO
b                      203
c                         201  2  203
c                         202  2  203
c                         203  2  204
  129 24 German ST       SEE, MEER OZEAN
b                      204
c                         203  2  204
  129 09 Vlach           MARE
  129 18 Sardinian L     MARE
  129 17 Sardinian N     MARE
  129 15 French Creole C LAME
  129 86 UKRAINIAN P     MORE
  129 91 SLOVENIAN P     MORJE
  129 42 Slovenian       MORJE
  129 89 SLOVAK P        MORE
  129 46 Slovak          MORE
  129 92 SERBOCROATIAN P MORE
  129 54 Serbocroatian   MORE
  129 85 RUSSIAN P       MORE
  129 51 Russian         MORE
  129 88 POLISH P        MORZE
  129 50 Polish          MORZE
  129 93 MACEDONIAN P    MORE
  129 44 Lusatian U      MORJO
  129 43 Lusatian L      MORO
  129 90 CZECH P         MORE
  129 45 Czech           MORE
  129 87 BYELORUSSIAN P  MORA
  129 94 BULGARIAN P     MORE
  129 39 Lithuanian O    MARES
  129 08 Rumanian List   MARE
  129 11 Ladin           MER
  129 19 Sardinian C     MARI
  129 10 Italian         MARE
  129 23 Catalan         MAR
  129 20 Spanish         MAR
  129 12 Provencal       MAR
  129 14 Walloon         MER
  129 16 French Creole D LAME
  129 13 French          MER
  129 03 Welsh N         MOR
  129 04 Welsh C         MOR
  129 05 Breton List     MOR
  129 06 Breton SE       MOR
  129 07 Breton ST       MOR
  129 52 Macedonian      MORE
  129 47 Czech E         MORE
  129 49 Byelorussian    MORA
  129 48 Ukrainian       MORE
  129 53 Bulgarian       MORE
  129 21 Portuguese ST   MAR
  129 22 Brazilian       MAR
b                      205
c                         205  3  206
  129 81 Albanian Top    DET
  129 80 Albanian T      DET
  129 83 Albanian K      DEET
  129 84 Albanian C      DEJT
  129 82 Albanian G      DET
  129 95 ALBANIAN        DETI
b                      206
c                         205  3  206
  129 68 Greek Mod       THALASA
  129 66 Greek ML        THALASSA
  129 70 Greek K         THALASSA
  129 67 Greek MD        THALASSA
  129 69 Greek D         THALASSA
a 130 TO SEE
b                      000
  130 02 Irish B
b                      001
  130 56 Singhalese      BALANAVA
  130 55 Gypsy Gk        DIKHAV
  130 01 Irish A         FEISCINT
  130 78 Baluchi         GINDAGH, DITHA
  130 59 Gujarati        JOWU
  130 58 Marathi         PAHNE
  130 41 Latvian         REDZET
  130 57 Kashmiri        WUCHUN
b                      002
  130 77 Tadzik          DIDAN, TAMOSO KARDAN
  130 76 Persian List    DIDAN
b                      003
  130 17 Sardinian N     VIDERE
  130 18 Sardinian L     BIDERE
  130 09 Vlach           VEDU
  130 90 CZECH P         VIDETI
  130 43 Lusatian L      WIZES
  130 44 Lusatian U      WIDZEC
  130 93 MACEDONIAN P    VIDAM
  130 50 Polish          WIDZIEC
  130 88 POLISH P        WIDZIEC
  130 51 Russian         VIDET
  130 85 RUSSIAN P       VIDET
  130 54 Serbocroatian   VIDETI
  130 92 SERBOCROATIAN P VIDETI
  130 46 Slovak          VIDET
  130 89 SLOVAK P        VIDET
  130 42 Slovenian       VIDIS
  130 91 SLOVENIAN P     VIDETI
  130 15 French Creole C VWE
  130 45 Czech           VIDETI
  130 94 BULGARIAN P     VIZDAM
  130 08 Rumanian List   A VEDEA
  130 11 Ladin           VAIR
  130 19 Sardinian C     BIRI
  130 10 Italian         VEDERE
  130 23 Catalan         VEURER
  130 20 Spanish         VER
  130 21 Portuguese ST   VER
  130 22 Brazilian       VER
  130 12 Provencal       VEIRE
  130 14 Walloon         VEY, VEYI
  130 16 French Creole D (V)WE
  130 13 French          VOIR
  130 52 Macedonian      VIDI/GLEDA
  130 47 Czech E         VIDET
  130 48 Ukrainian       DYVYTYS'
  130 53 Bulgarian       DA VIZDA
b                      004
  130 03 Welsh N         GWELD
  130 04 Welsh C         GWELED
  130 05 Breton List     GWELOUT, GWELET
  130 06 Breton SE       GUELET
  130 07 Breton ST       GWELOUT
b                      005
  130 30 Swedish Up      SI, SE
  130 31 Swedish VL      SI
  130 24 German ST       SEHEN
  130 35 Icelandic ST    SEA, SJA
  130 34 Riksmal         SE
  130 32 Swedish List    SE, SKADA
  130 33 Danish          SE
  130 36 Faroese         SIGGJA
  130 29 Frisian         SJEN
  130 28 Flemish         ZIEN
  130 25 Penn. Dutch     SAY
  130 26 Dutch List      ZIEN
  130 27 Afrikaans       SIEN
  130 38 Takitaki        SI
  130 37 English ST      TO SEE
  130 81 Albanian Top    SO, AOR. PASE
  130 83 Albanian K      SOX (AOR. PAASE, PPLE. PAARE)
  130 80 Albanian T      ME PARE
  130 84 Albanian C      SOX
  130 82 Albanian G      SHOF (PA = INF.)
  130 95 ALBANIAN        SHOF, (PASH = AOR.) (PA = INF.)
b                      006
  130 49 Byelorussian    BACYC'
  130 87 BYELORUSSIAN P  BACYC
  130 86 UKRAINIAN P     BACYTY
b                      007
  130 74 Afghan          LIDEL
  130 75 Waziri          KATEL, LIDEL
b                      008
  130 79 Wakhi           WIN-
  130 73 Ossetic         UYNYN
b                      009
  130 71 Armenian Mod    TESNEL
  130 72 Armenian List   DESNEL
b                      010
  130 64 Nepali List     DEKHNU
  130 61 Lahnda          DEKHEN
  130 63 Bengali         DEKHA
  130 62 Hindi           DEKHNA
  130 60 Panjabi ST      DEKHNA
  130 65 Khaskura        DEKHNU, HERNU
b                      011
  130 40 Lithuanian ST   MATYTI
  130 39 Lithuanian O    MATYTI
b                      012
  130 68 Greek Mod       VLEPO
  130 66 Greek ML        BLEPO
  130 70 Greek K         HORO, BLEPO
  130 67 Greek MD        BLEPO
  130 69 Greek D         BLEPO
a 131 SEED
b                      000
  131 82 Albanian G
  131 95 ALBANIAN
b                      001
  131 72 Armenian List   SERM
  131 55 Gypsy Gk        GIV
  131 71 Armenian Mod    HATIK
  131 73 Ossetic         NAEMYG, GAGA
b                      002
  131 56 Singhalese      ATA, BIJA
  131 57 Kashmiri        BYOLU
  131 64 Nepali List     BIU
  131 61 Lahnda          BIJ
  131 78 Baluchi         BIJ
  131 59 Gujarati        BI
  131 58 Marathi         BI
  131 63 Bengali         BIJ, BICI
  131 62 Hindi           BIJ
  131 60 Panjabi ST      BI
  131 65 Khaskura        BIU
b                      003
  131 30 Swedish Up      FRO
  131 31 Swedish VL      FRO
  131 35 Icelandic ST    FRAE
  131 34 Riksmal         FRO
  131 36 Faroese         FRAE
b                      004
  131 74 Afghan          DANA
  131 77 Tadzik          DON, DONA
b                      005
  131 15 French Creole C GHWEN
  131 23 Catalan         GRANA, GRA
  131 12 Provencal       GRANO
  131 16 French Creole D GWEN
b                      006
  131 84 Albanian C      FAR
  131 83 Albanian K      KOKE (SING.), FARE (COLLECTIVE)
  131 80 Albanian T      FARE
  131 81 Albanian Top    FARE
b                      007
  131 09 Vlach           SPOR
  131 68 Greek Mod       SPOROS
  131 66 Greek ML        SPOROS
  131 70 Greek K         SPOROS
  131 67 Greek MD        SPOROS
  131 69 Greek D         SPOROS
b                      200
c                         200  2  201
c                         200  2  203
  131 05 Breton List     HAD, SPER
  131 02 Irish B         SIOL
  131 01 Irish A         SIOL
  131 03 Welsh N         HEDYN
  131 04 Welsh C         HAD
  131 06 Breton SE       HAD
  131 07 Breton ST       HAD
  131 24 German ST       SAAT
  131 32 Swedish List    SAD
  131 33 Danish          SAED
  131 29 Frisian         SIE, SIED
  131 28 Flemish         ZAED
  131 26 Dutch List      ZAAD
  131 27 Afrikaans       SAAD
  131 38 Takitaki        SIRI
  131 37 English ST      SEED
  131 17 Sardinian N     SEMENE
  131 18 Sardinian L     SEMEN
  131 86 UKRAINIAN P     SIM A
  131 91 SLOVENIAN P     SEME
  131 42 Slovenian       SEME
  131 89 SLOVAK P        SEMENO
  131 46 Slovak          SEMENO
  131 92 SERBOCROATIAN P SEME
  131 54 Serbocroatian   SEME
  131 85 RUSSIAN P       SEM A
  131 88 POLISH P        SIEMIE
  131 93 MACEDONIAN P    SEME
  131 44 Lusatian U      SYMJO
  131 43 Lusatian L      SEME
  131 90 CZECH P         SEME
  131 87 BYELORUSSIAN P  SEM A
  131 94 BULGARIAN P     SEME
  131 08 Rumanian List   SAMINTA
  131 11 Ladin           SEM, SEMENZA
  131 19 Sardinian C     SEMINI
  131 10 Italian         SEME
  131 20 Spanish         SEMILLA
  131 14 Walloon         S(I)MINCE
  131 13 French          SEMENCE
  131 25 Penn. Dutch     SAWME
  131 52 Macedonian      SEME
  131 21 Portuguese ST   SEMENTE
  131 22 Brazilian       SEMENTE
  131 40 Lithuanian ST   SEKLA
  131 39 Lithuanian O    SEKLA
  131 41 Latvian         SEKLA
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
  131 48 Ukrainian       NASINNJA, ZERNO
  131 45 Czech           SEME, ZRNO
b                      202
c                         201  2  202
  131 53 Bulgarian       ZERNO
  131 47 Czech E         ZRNO
  131 51 Russian         ZERNO
  131 50 Polish          ZIARNO
b                      203
c                         200  2  203
c                         201  2  203
  131 49 Byelorussian    NASEN'NE
b                      204
c                         204  3  205
  131 79 Wakhi           TUGHUM
  131 76 Persian List    TOKHM
b                      205
c                         204  3  205
  131 75 Waziri          TEMNA, TEMNA
a 132 TO SEW
b                      000
  132 73 Ossetic
b                      001
  132 75 Waziri          GANDEL
  132 56 Singhalese      MAHANAWA
b                      002
  132 79 Wakhi           DREV-
  132 74 Afghan          DZORAVEL
b                      003
  132 78 Baluchi         DOSHAGH, DOKHTA
  132 77 Tadzik          DUXTAN
  132 76 Persian List    DUKHTAN
b                      004
  132 24 German ST       NAHEN
  132 29 Frisian         NAEIJE, NIDDELJE
  132 28 Flemish         NAIJEN
  132 25 Penn. Dutch     NAY
  132 26 Dutch List      NAAIEN
  132 27 Afrikaans       NAAIE
  132 38 Takitaki        NAI
b                      005
  132 01 Irish A         FUAGHAIL
  132 02 Irish B         D'FHUAGHAIL
b                      006
  132 68 Greek Mod       RAVO
  132 66 Greek ML        HRABO
  132 70 Greek K         RAPTO
  132 67 Greek MD        RABO
  132 69 Greek D         RABO
b                      007
  132 81 Albanian Top    KEP, AOR. KEPA
  132 80 Albanian T      ME GEPUR
  132 83 Albanian K      KEPIN
  132 84 Albanian C      KEP
  132 82 Albanian G      KJEP
  132 95 ALBANIAN        KJEP
b                      008
  132 03 Welsh N         GWNIO
  132 04 Welsh C         GWNIO
  132 05 Breton List     GWRAIT
  132 06 Breton SE       GROUIEIN
  132 07 Breton ST       GWRIAT
b                      009
  132 71 Armenian Mod    KAREL
  132 72 Armenian List   GAREL
b                      200
c                         200  2  201
  132 55 Gypsy Gk        SUVAV
  132 87 BYELORUSSIAN P  SYC
  132 45 Czech           SITI
  132 90 CZECH P         SITI
  132 43 Lusatian L      SYS
  132 44 Lusatian U      SIC
  132 93 MACEDONIAN P    SIAM
  132 50 Polish          SZYC
  132 88 POLISH P        SZYC
  132 51 Russian         SIT
  132 85 RUSSIAN P       SYT
  132 54 Serbocroatian   SITI
  132 92 SERBOCROATIAN P SITI
  132 46 Slovak          SIT
  132 89 SLOVAK P        SIT
  132 42 Slovenian       SIVAT
  132 91 SLOVENIAN P     SITI
  132 86 UKRAINIAN P     SYTY
  132 94 BULGARIAN P     SIJA
  132 41 Latvian         SUT
  132 39 Lithuanian O    SIUTI
  132 40 Lithuanian ST   SIUTI
  132 52 Macedonian      SIE
  132 47 Czech E         SIT
  132 49 Byelorussian    SYC'
  132 48 Ukrainian       SYTY
  132 53 Bulgarian       DA SIE
  132 57 Kashmiri        SUWUN
  132 64 Nepali List     SIUNU
  132 61 Lahnda          SIWEN
  132 59 Gujarati        SIWEWU
  132 58 Marathi         SIVNE.
  132 63 Bengali         SELAI+KORA
  132 62 Hindi           SINA
  132 60 Panjabi ST      SYUNA
  132 65 Khaskura        SIUNU
  132 34 Riksmal         SY
  132 32 Swedish List    SY
  132 33 Danish          SY
  132 37 English ST      TO SEW
  132 09 Vlach           KOSU
  132 17 Sardinian N     KOSIRE
  132 18 Sardinian L     COSIRE
  132 15 French Creole C KUD
  132 08 Rumanian List   A COASE
  132 11 Ladin           CUSIR
  132 19 Sardinian C     KUSIRI
  132 10 Italian         CUCIRE
  132 23 Catalan         CUSIR, JUNTAR
  132 20 Spanish         COSER
  132 12 Provencal       COURDURA
  132 14 Walloon         KEUSE
  132 16 French Creole D KUD
  132 13 French          COUDRE
  132 21 Portuguese ST   COSER
  132 22 Brazilian       COSER
b                      201
c                         200  2  201
c                         201  2  202
  132 30 Swedish Up      SY, SOMMA
  132 31 Swedish VL      SY, SOM
b                      202
c                         201  2  202
  132 35 Icelandic ST    SAUMA
  132 36 Faroese         SEYMA
a 133 SHARP (KNIFE)
b                      000
  133 09 Vlach
  133 55 Gypsy Gk
  133 84 Albanian C
b                      001
  133 70 Greek K         AICHMEROS
  133 14 Walloon         CWAHANT
  133 83 Albanian K      I-ECURE
  133 56 Singhalese      MUHATA
  133 69 Greek D         MUTEROS
  133 60 Panjabi ST      TIKKHA
b                      002
  133 06 Breton SE       LEMM
  133 05 Breton List     LEMM
  133 04 Welsh C         LLYM
  133 07 Breton ST       LEMM
b                      003
  133 58 Marathi         DHARDAR
  133 59 Gujarati        DHARDAR, DHARWALU
  133 63 Bengali         DHARALO
  133 65 Khaskura        LAGNE, DHARILO
  133 64 Nepali List     DHARILO, LAGNE
b                      004
  133 24 German ST       SCHARF
  133 33 Danish          SKARP
  133 32 Swedish List    SKARP
  133 34 Riksmal         SKARP
  133 29 Frisian         SKERP
  133 28 Flemish         SCHERP
  133 25 Penn. Dutch     SCHARIF
  133 26 Dutch List      SCHERP
  133 27 Afrikaans       SKERP
  133 38 Takitaki        SRAPOE
  133 37 English ST      SHARP
b                      005
  133 73 Ossetic         CYRG"
  133 74 Afghan          TERE
  133 75 Waziri          TERA
  133 79 Wakhi           TEGHD, TIZ
  133 78 Baluchi         TEZ
  133 77 Tadzik          TEZ
  133 76 Persian List    TIZ
b                      006
  133 57 Kashmiri        TEZ
  133 61 Lahnda          TEZ
  133 62 Hindi           TEJ
b                      007
  133 67 Greek MD        KOFTEROS
  133 68 Greek Mod       KOFTEROS
  133 66 Greek ML        KOFTEROS
b                      008
  133 17 Sardinian N     ARROTTATU
  133 18 Sardinian L     ARRODATU
b                      009
  133 71 Armenian Mod    SUR
  133 72 Armenian List   SOOR
b                      010
  133 11 Ladin           TAGLIAINT
  133 23 Catalan         TALLANT, CARNICER
  133 10 Italian         TAGLIENTE
b                      200
c                         200  2  201
c                         200  3  203
c                         200  3  204
  133 94 BULGARIAN P     OSTUR
  133 87 BYELORUSSIAN P  VOSTRY
  133 45 Czech           OSTRY
  133 90 CZECH P         OSTRY
  133 43 Lusatian L      WOTSY
  133 44 Lusatian U      WOTRY
  133 93 MACEDONIAN P    OSTAR
  133 50 Polish          OSTRY
  133 88 POLISH P        OSTRY
  133 51 Russian         OSTRYJ
  133 85 RUSSIAN P       OSTRYJ
  133 54 Serbocroatian   OSTAR
  133 92 SERBOCROATIAN P OSTAR
  133 46 Slovak          OSTRY
  133 89 SLOVAK P        OSTRY
  133 42 Slovenian       OSTER
  133 91 SLOVENIAN P     OSTER
  133 86 UKRAINIAN P     HOSTRYJ
  133 41 Latvian         ASS
  133 39 Lithuanian O    ASTRUS
  133 40 Lithuanian ST   ASTRUS
  133 52 Macedonian      OSTAR
  133 47 Czech E         OSTRE
  133 49 Byelorussian    VOSTRY
  133 48 Ukrainian       HOCTRYJ
  133 53 Bulgarian       OSTRO
  133 19 Sardinian C     AKKUCCU
  133 20 Spanish         AGUDO
  133 81 Albanian Top    I-MBRETE
  133 80 Albanian T      I, E MPREHTE
  133 82 Albanian G      PREFET
  133 95 ALBANIAN        PREFET
b                      201
c                         200  2  201
c                         201  2  202
c                         201  3  203
c                         201  3  204
  133 22 Brazilian       AFIADO, AGUCADO
b                      202
c                         201  2  202
  133 21 Portuguese ST   AFIADO
  133 15 French Creole C FILE
  133 16 French Creole D FILE
b                      203
c                         200  3  203
c                         201  3  203
c                         203  3  204
  133 03 Welsh N         AWCHUS, MINIOG
b                      204
c                         200  3  204
c                         201  3  204
c                         203  3  204
c                         204  2  205
  133 02 Irish B         FAOBHRACH, -AIGHE, GEAR
b                      205
c                         204  2  205
  133 01 Irish A         GEAR
b                      206
c                         206  3  207
  133 08 Rumanian List   ASCUTIT, TAIOS
b                      207
c                         206  3  207
c                         207  2  208
  133 12 Provencal       TRANCHU, TAIU
b                      208
c                         207  2  208
  133 13 French          TRANCHANT
b                      209
c                         209  2  210
  133 35 Icelandic ST    BEITTUR
b                      210
c                         209  2  210
c                         210  2  211
  133 36 Faroese         BEITUR, HVASSUR
b                      211
c                         210  2  211
  133 30 Swedish Up      VASS
  133 31 Swedish VL      VAS
a 134 SHORT
b                      001
  134 70 Greek K         BRACHUS
  134 12 Provencal       BREU, EVO
  134 73 Ossetic         CYBYR
  134 78 Baluchi         GWAND
  134 65 Khaskura        HOCHO
  134 41 Latvian         ISS
  134 53 Bulgarian       KESO
  134 60 Panjabi ST      MEDRA
  134 59 Gujarati        TUKU, BETKO (PERSON)
  134 55 Gypsy Gk        XARNO
b                      002
  134 07 Breton ST       BERR
  134 06 Breton SE       BERR
  134 05 Breton List     BERR
  134 04 Welsh C         BYR
  134 03 Welsh N         BYR
b                      003
  134 30 Swedish Up      KORT
  134 31 Swedish VL      KOT
  134 24 German ST       KURZ
  134 33 Danish          KORT
  134 32 Swedish List    KORT
  134 34 Riksmal         KORT
  134 27 Afrikaans       KORT
  134 26 Dutch List      KORT
  134 25 Penn. Dutch     KOTZ
  134 28 Flemish         KORT
  134 29 Frisian         KOART
b                      004
  134 01 Irish A         GEARR
  134 02 Irish B         GEARR
b                      005
  134 36 Faroese         STUTTUR
  134 35 Icelandic ST    STUTTR
b                      006
  134 67 Greek MD        KONTOS
  134 69 Greek D         KONTOS
  134 68 Greek Mod       KONDOS
  134 66 Greek ML        KONTOS
b                      007
  134 75 Waziri          LAND
  134 74 Afghan          MUXTASAR, LAND
b                      008
  134 62 Hindi           CHOTA
  134 57 Kashmiri        TSHOTU
  134 64 Nepali List     CHOTO
  134 61 Lahnda          CHOTA
b                      009
  134 40 Lithuanian ST   TRUMPAS
  134 39 Lithuanian O    TRUMPAS
b                      010
  134 81 Albanian Top    SKURTER
  134 82 Albanian G      SHKURT
  134 84 Albanian C      I-SKURTUR
  134 83 Albanian K      I SKURTERE
  134 80 Albanian T      I, E SHKURTER
  134 95 ALBANIAN        SHKURT
b                      011
  134 76 Persian List    KUTAH
  134 77 Tadzik          KUTOX
  134 79 Wakhi           KUT
b                      012
  134 13 French          COURT
  134 16 French Creole D KUT
  134 14 Walloon         COURT
  134 22 Brazilian       CURTO
  134 21 Portuguese ST   CURTO, BREVE
  134 17 Sardinian N     KURTHU
  134 18 Sardinian L     CURZU
  134 15 French Creole C KUT
  134 20 Spanish         CORTO
  134 23 Catalan         CURT
  134 10 Italian         CORTO
  134 19 Sardinian C     KURCU
  134 11 Ladin           CUORT
  134 94 BULGARIAN P     KRATUK
  134 87 BYELORUSSIAN P  KAROTKI
  134 45 Czech           KRATKY
  134 90 CZECH P         KRATKY
  134 43 Lusatian L      KROTKI
  134 44 Lusatian U      KROTKI
  134 93 MACEDONIAN P    KRATOK
  134 50 Polish          KROTKI
  134 88 POLISH P        KROTKI
  134 51 Russian         KOROTKIJ
  134 85 RUSSIAN P       KOROTKIJ
  134 54 Serbocroatian   KRATAK
  134 92 SERBOCROATIAN P KRATAK
  134 46 Slovak          KRATKY
  134 89 SLOVAK P        KRATKY
  134 42 Slovenian       KRATKO
  134 91 SLOVENIAN P     KRATEK
  134 86 UKRAINIAN P     KOROTKYJ
  134 52 Macedonian      KRATOK
  134 47 Czech E         KRATKE
  134 49 Byelorussian    KAROTKI, KAROTKA
  134 48 Ukrainian       KOROTKYJ
  134 37 English ST      SHORT
  134 38 Takitaki        SJATOE
  134 71 Armenian Mod    KARC
  134 72 Armenian List   GARJ
  134 09 Vlach           SKURTU
  134 08 Rumanian List   SCURT
b                      100
  134 58 Marathi         AKHUD
  134 56 Singhalese      KOTA
  134 63 Bengali         KHATO
a 135 TO SING
b                      001
  135 70 Greek K         ADO
  135 01 Irish A         AMHRAN DO RADH
  135 23 Catalan         COPLA
  135 41 Latvian         DZIEDAT
  135 55 Gypsy Gk        GILABAV
  135 78 Baluchi         GUSHAGH, GUSHTA, GWASHTA
  135 56 Singhalese      SINOU/KIYANAWA
  135 75 Waziri          SANDARA (SONG)
  135 73 Ossetic         ZARYN
b                      002
  135 57 Kashmiri        GEWUN
  135 64 Nepali List     GAUNU
  135 61 Lahnda          GAWEN
  135 59 Gujarati        GAWU
  135 58 Marathi         GANE
  135 63 Bengali         GAOA
  135 62 Hindi           GANA
  135 60 Panjabi ST      GONA
  135 65 Khaskura        GANU
b                      003
  135 02 Irish B         CANAIM, SEINIM
  135 03 Welsh N         CANU
  135 04 Welsh C         CANU
  135 05 Breton List     KANA
  135 07 Breton ST       KANAN
  135 06 Breton SE       KANNEIN
  135 09 Vlach           KYNTU
  135 81 Albanian Top    KENDON, AOR. KENDOVA
  135 18 Sardinian L     CANTARE
  135 17 Sardinian N     KANTARE
  135 15 French Creole C SATE
  135 08 Rumanian List   A CINTA
  135 11 Ladin           CHANTER
  135 19 Sardinian C     KANTAI
  135 10 Italian         CANTARE
  135 20 Spanish         CANTAR
  135 12 Provencal       CANTA
  135 14 Walloon         TCHANTER
  135 16 French Creole D SATE
  135 13 French          CHANTER
  135 21 Portuguese ST   CANTAR
  135 22 Brazilian       CANTAR
b                      004
  135 68 Greek Mod       TRAGUDHO
  135 66 Greek ML        TRAGOUDO
  135 67 Greek MD        TRAGOUDO
  135 69 Greek D         TRAGOUDAO
b                      005
  135 30 Swedish Up      SJUNGA
  135 31 Swedish VL      SONG
  135 24 German ST       SINGEN
  135 35 Icelandic ST    SYNGVA, SYNGJA
  135 34 Riksmal         SYNGE
  135 32 Swedish List    SJUNGA
  135 33 Danish          SYNGE
  135 36 Faroese         SYNGJA
  135 29 Frisian         SJONGE
  135 28 Flemish         ZINGEN
  135 25 Penn. Dutch     SING
  135 26 Dutch List      ZINGEN
  135 27 Afrikaans       SING
  135 38 Takitaki        SINGI
  135 37 English ST      TO SING
b                      006
  135 94 BULGARIAN P     PEJA
  135 87 BYELORUSSIAN P  PEC
  135 45 Czech           ZPIVATI
  135 90 CZECH P         ZPIVATI
  135 43 Lusatian L      SPIWAS
  135 44 Lusatian U      SPEWAC
  135 93 MACEDONIAN P    PEJAM
  135 50 Polish          SPIEWAC
  135 88 POLISH P        SPIEWAC
  135 51 Russian         PET
  135 85 RUSSIAN P       PET
  135 54 Serbocroatian   PEVATI
  135 92 SERBOCROATIAN P PEVATI
  135 46 Slovak          SPIEVAT
  135 89 SLOVAK P        SPIEVAT
  135 42 Slovenian       PETI
  135 91 SLOVENIAN P     PETI
  135 86 UKRAINIAN P     SPIVATY
  135 52 Macedonian      PEE
  135 47 Czech E         SPIVAT
  135 49 Byelorussian    PJAJAC'
  135 48 Ukrainian       SPIVATY
  135 53 Bulgarian       DA PEE
b                      007
  135 40 Lithuanian ST   DAINUOTI
  135 39 Lithuanian O    DAINUOTI
b                      008
  135 71 Armenian Mod    ERGEL
  135 72 Armenian List   YERKEL
b                      009
  135 80 Albanian T      ME KENDUAR
  135 83 Albanian K      KENDON
  135 84 Albanian C      KENDON
  135 82 Albanian G      KENDOJ
  135 95 ALBANIAN        KENDOJ
b                      200
c                         200  3  201
  135 74 Afghan          VAJEL
b                      201
c                         200  3  201
c                         201  3  202
  135 76 Persian List    AVAZ KHANDAN
b                      202
c                         201  3  202
  135 79 Wakhi           BAEIT XAN-
  135 77 Tadzik          XONDAN, SAROIDAN
a 136 TO SIT
b                      000
  136 22 Brazilian
b                      001
  136 73 Ossetic         BADYN
  136 25 Penn. Dutch     HUCK
  136 56 Singhalese      INDAGANAWA
b                      002
  136 77 Tadzik          NISASTAN, SISTAN
  136 76 Persian List    NESHASTAN
b                      003
  136 80 Albanian T      ME U UNJUR
  136 84 Albanian C      (T)UJEM
b                      004
  136 71 Armenian Mod    NSTEL
  136 72 Armenian List   NUSDEL
b                      005
  136 81 Albanian Top    RI, AOR. NDENA
  136 83 Albanian K      RII (PER DHEEU), (AOR. MBETA (...) NDINA)
  136 82 Albanian G      RRI NE BYTH
  136 95 ALBANIAN        RRI, (NDEJTA = AOR.)
b                      200
c                         200  3  201
  136 15 French Creole C ASIZ, ASID
  136 23 Catalan         ASSENTARSE
  136 20 Spanish         SENTARSE
  136 12 Provencal       ASSETA, ASSEIRE
  136 14 Walloon         ASSIR, ACHIR
  136 16 French Creole D ASIZ
  136 13 French          ASSEOIR (ETRE ASSIS)
  136 21 Portuguese ST   ESTAR ASSENTADO
  136 30 Swedish Up      SITTA
  136 31 Swedish VL      SITA
  136 09 Vlach           SEDU
  136 18 Sardinian L     SEZZERE
  136 17 Sardinian N     SEDERE
  136 88 POLISH P        SIEDZIEC
  136 51 Russian         SIDET
  136 85 RUSSIAN P       SIDET
  136 54 Serbocroatian   SEDITI
  136 92 SERBOCROATIAN P SEDETI
  136 46 Slovak          SEDET
  136 89 SLOVAK P        SEDIET
  136 42 Slovenian       SEDET
  136 91 SLOVENIAN P     SEDETI
  136 86 UKRAINIAN P     SYDITY
  136 50 Polish          SIEDZIEC
  136 44 Lusatian U      SEDZEC
  136 93 MACEDONIAN P    SEDAM
  136 43 Lusatian L      SEJZES
  136 90 CZECH P         SEDETI
  136 45 Czech           SEDETI
  136 87 BYELORUSSIAN P  S ADZEC
  136 94 BULGARIAN P     S ADAM
  136 41 Latvian         SEDET
  136 39 Lithuanian O    SEDETI
  136 40 Lithuanian ST   SEDETI
  136 08 Rumanian List   A SEDEA
  136 11 Ladin           SEZZER
  136 19 Sardinian C     SI SEZZI
  136 10 Italian         SEDERE
  136 02 Irish B         SUIDHIM
  136 01 Irish A         SUIDHE
  136 03 Welsh N         EISTEDD
  136 04 Welsh C         EISTEDD
  136 05 Breton List     AZEZA, KOAZEA, MONT EN E GOAZE
  136 06 Breton SE       AZE
  136 07 Breton ST       AZEZAN
  136 24 German ST       SITZEN
  136 35 Icelandic ST    SITJA
  136 34 Riksmal         SITTE
  136 32 Swedish List    SITTA
  136 33 Danish          SIDDE
  136 36 Faroese         SITA
  136 29 Frisian         SITTE
  136 28 Flemish         ZITTEN
  136 26 Dutch List      ZITTEN
  136 27 Afrikaans       SIT
  136 52 Macedonian      SEDI
  136 47 Czech E         SEDET
  136 49 Byelorussian    SJADZEC'
  136 48 Ukrainian       SYDITY
  136 53 Bulgarian       DA SEDI
  136 38 Takitaki        SIDOM
  136 37 English ST      TO SIT
b                      201
c                         200  3  201
  136 68 Greek Mod       KATHOME
  136 66 Greek ML        KATHOMAI
  136 70 Greek K         KEIMAI
  136 67 Greek MD        KATHOMAI
  136 69 Greek D         KATHOMAI
b                      202
c                         202  3  203
  136 79 Wakhi           NEZD
  136 78 Baluchi         NINDAGH, NISHTA
b                      203
c                         202  3  203
c                         203  3  204
  136 75 Waziri          KSHENAWEL, NOSTAI, PAND, (SITTING)
b                      204
c                         203  3  204
  136 74 Afghan          KSENASTEL
b                      205
c                         205  3  206
  136 64 Nepali List     BAITHANU
  136 61 Lahnda          BAETHEN
  136 62 Hindi           BETHNA
  136 60 Panjabi ST      BETHNA
b                      206
c                         205  3  206
  136 65 Khaskura        BASNU
  136 55 Gypsy Gk        BESAV
  136 59 Gujarati        BESWU
  136 58 Marathi         BESNE.
  136 63 Bengali         BOSA
  136 57 Kashmiri        BEHUN
a 137 SKIN (OF PERSON)
b                      001
  137 38 Takitaki        BOEBA
  137 56 Singhalese      HAMA
  137 58 Marathi         KATEDI
  137 55 Gypsy Gk        MORKHI
  137 60 Panjabi ST      PINDA
b                      002
  137 40 Lithuanian ST   ODA
  137 41 Latvian         ADA
b                      003
  137 82 Albanian G      LIKURA
  137 84 Albanian C      LIKUR
  137 83 Albanian K      LEKURE
  137 80 Albanian T      LEKURE
  137 81 Albanian Top    CIPE / LHEKURE
  137 95 ALBANIAN        LIKURA, ZHABAA
b                      004
  137 74 Afghan          POST
  137 78 Baluchi         PHOST
  137 79 Wakhi           PIST
  137 76 Persian List    PUST
  137 77 Tadzik          PUST
b                      005
  137 51 Russian         KOZA
  137 85 RUSSIAN P       KOZA
  137 54 Serbocroatian   KOZA
  137 92 SERBOCROATIAN P KOZA
  137 46 Slovak          KOZA
  137 89 SLOVAK P        KOZA
  137 42 Slovenian       KOZA
  137 91 SLOVENIAN P     KOZA
  137 45 Czech           KUZE
  137 90 CZECH P         KUZE
  137 43 Lusatian L      KOZA
  137 44 Lusatian U      KOZA
  137 93 MACEDONIAN P    KOZA
  137 94 BULGARIAN P     KOZA
  137 52 Macedonian      KOZA
  137 47 Czech E         KOZA
  137 53 Bulgarian       KOZA
b                      100
  137 64 Nepali List     KHALO
  137 65 Khaskura        CHHALA
b                      101
  137 72 Armenian List   MORT
  137 71 Armenian Mod    MASK
b                      200
c                         200  2  201
c                         200  3  205
  137 10 Italian         PELLE
  137 23 Catalan         PELL
  137 19 Sardinian C     PEDDI
  137 15 French Creole C LAPO
  137 17 Sardinian N     PEDDE
  137 18 Sardinian L     PEDDE
  137 11 Ladin           PEL
  137 08 Rumanian List   PIELE
  137 12 Provencal       PEAU
  137 14 Walloon         PE
  137 16 French Creole D LAPO
  137 13 French          PEAU
  137 22 Brazilian       PELE
  137 21 Portuguese ST   PELLE
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  3  205
  137 20 Spanish         CUTIS,PIEL
b                      202
c                         201  2  202
c                         202  2  203
  137 34 Riksmal         HUD
  137 24 German ST       HAUT
  137 33 Danish          HUD
  137 27 Afrikaans       HUID
  137 26 Dutch List      HUID
  137 25 Penn. Dutch     HAUT
  137 28 Flemish         HUID
  137 29 Frisian         HUD
b                      203
c                         201  2  203
c                         202  2  203
c                         203  2  204
  137 35 Icelandic ST    HUO, SKINN
  137 32 Swedish List    HUD, SKINN
  137 36 Faroese         HUO, SKINN
b                      204
c                         203  2  204
  137 37 English ST      SKIN
  137 30 Swedish Up      SKINN
  137 31 Swedish VL      SIN
b                      205
c                         200  3  205
c                         201  3  205
  137 09 Vlach           KALE
b                      206
c                         206  3  207
  137 86 UKRAINIAN P     SKURA
  137 50 Polish          SKORA
  137 88 POLISH P        SKORA
  137 87 BYELORUSSIAN P  SKURA
  137 39 Lithuanian O    SKURAS
  137 48 Ukrainian       SKURA, SKIRA
  137 49 Byelorussian    SKURA
  137 73 Ossetic         CARM
  137 57 Kashmiri        TSAM
  137 75 Waziri          TSARMAN
  137 61 Lahnda          CEMRI
  137 59 Gujarati        CAMERI
  137 62 Hindi           CAM
  137 63 Bengali         CAM
b                      207
c                         206  3  207
  137 07 Breton ST       KROC'HEN
  137 06 Breton SE       KROHEN
  137 05 Breton List     KROC'HEN
  137 04 Welsh C         CROEN
  137 03 Welsh N         CROEN
  137 01 Irish A         CRAICEANN
  137 02 Irish B         CROICEANN, -CNE
b                      208
c                         208  2  209
  137 70 Greek K         DERMA
  137 66 Greek ML        DERMA
  137 69 Greek D         DERMA
b                      209
c                         208  2  209
c                         209  2  210
  137 68 Greek Mod       PETSI, DHERMA
b                      210
c                         209  2  210
  137 67 Greek MD        PETSI
a 138 SKY
b                      001
  138 73 Ossetic         ARV, UAELARV
  138 09 Vlach           DUMNEZE(LU)
  138 71 Armenian Mod    ERKINK`
  138 72 Armenian List   GULIMA OT
  138 83 Albanian K      INEZOT
  138 05 Breton List     NENV
  138 38 Takitaki        TAPO
b                      002
  138 46 Slovak          OBLOHA, NEBO
  138 89 SLOVAK P        NEBO
  138 42 Slovenian       NEBO
  138 91 SLOVENIAN P     NEBO
  138 86 UKRAINIAN P     NEBO
  138 94 BULGARIAN P     NEBE
  138 87 BYELORUSSIAN P  NEBA
  138 45 Czech           NEBE
  138 90 CZECH P         NEBE
  138 43 Lusatian L      NJEBJO
  138 44 Lusatian U      NJEBJO
  138 93 MACEDONIAN P    NEBO
  138 50 Polish          NIEBO
  138 88 POLISH P        NIEBO
  138 51 Russian         NEBO
  138 85 RUSSIAN P       NEBO
  138 54 Serbocroatian   NEBO
  138 92 SERBOCROATIAN P NEBO
  138 41 Latvian         DEBESS
  138 57 Kashmiri        NAB
  138 52 Macedonian      NEBO
  138 47 Czech E         NEBE
  138 49 Byelorussian    NEBA
  138 48 Ukrainian       NEBO
  138 53 Bulgarian       NEBE
b                      003
  138 18 Sardinian L     CHELU
  138 17 Sardinian N     KELU
  138 15 French Creole C SYEL
  138 08 Rumanian List   CER
  138 11 Ladin           TSCHEL
  138 19 Sardinian C     CELU
  138 10 Italian         CIELO
  138 23 Catalan         CEL
  138 20 Spanish         CIELO
  138 12 Provencal       CEU
  138 14 Walloon         CIR
  138 16 French Creole D SYEL
  138 13 French          CIEL
  138 21 Portuguese ST   CEO, FIRMAMENTO
  138 22 Brazilian       CEU
b                      004
  138 95 ALBANIAN        KJILLI
  138 82 Albanian G      KJULLI
  138 84 Albanian C      KIEGHJA
  138 80 Albanian T      GIELL
  138 81 Albanian Top    KIEL
b                      005
  138 61 Lahnda          ESMAN
  138 79 Wakhi           OSMON
  138 78 Baluchi          ARSH, AZMAN
  138 74 Afghan          ASMAN
  138 77 Tadzik          OSMON
  138 76 Persian List    ASEMAN
  138 60 Panjabi ST      ESMAN
  138 75 Waziri          ASMON
b                      006
  138 65 Khaskura        AKAS, SARGA
  138 64 Nepali List     AKAS, SAGAR
  138 58 Marathi         AKAS
  138 56 Singhalese      AHASA
  138 59 Gujarati        AKAS
  138 62 Hindi           AKAS, ASMAN
  138 63 Bengali         AKAS, ASMAN
b                      007
  138 01 Irish A         SPEIR
  138 02 Irish B         SPEIR
b                      008
  138 04 Welsh C         AWYR
  138 03 Welsh N         AWYR
  138 06 Breton SE       EBR
  138 07 Breton ST       OABL
b                      009
  138 55 Gypsy Gk        URANOS
  138 68 Greek Mod       URANOS
  138 66 Greek ML        OURANOS
  138 70 Greek K         OURANOS
  138 67 Greek MD        OURANOS
  138 69 Greek D         OURANOS
b                      010
  138 40 Lithuanian ST   DANGUS
  138 39 Lithuanian O    DANGUS
b                      200
c                         200  2  201
  138 24 German ST       HIMMEL
  138 35 Icelandic ST    HIMINN
  138 34 Riksmal         HIMMEL
  138 32 Swedish List    HIMMEL
  138 33 Danish          HIMMEL
  138 36 Faroese         HIMIN, (HIMNAL)
  138 29 Frisian         HIMEL, HIMMEL
  138 28 Flemish         HEMEL
  138 25 Penn. Dutch     HIMMEL
  138 26 Dutch List      HEMEL
  138 27 Afrikaans       HEMEL, LUG
b                      201
c                         200  2  201
c                         201  3  202
  138 30 Swedish Up      SKY, LUFT, HIMMEL
  138 31 Swedish VL      SY, HIMAL
b                      202
c                         201  3  202
  138 37 English ST      SKY
a 139 TO SLEEP
b                      001
  139 78 Baluchi          AKSAGH,  AKASTHA
  139 74 Afghan          BIDEDEL
  139 73 Ossetic         FYNAEJ KAENYN, (XUYSSYN)
  139 41 Latvian         GULET
  139 55 Gypsy Gk        PASLAV
b                      002
  139 77 Tadzik          XOBIDAN
  139 76 Persian List    KHABIDAN
  139 75 Waziri          KHEB (SLEEP  SB. )
b                      003
  139 40 Lithuanian ST   MIEGOTI
  139 39 Lithuanian O    MIEGOTI
b                      004
  139 09 Vlach           DORMU
  139 18 Sardinian L     DORMIRE
  139 17 Sardinian N     DURMIRE
  139 15 French Creole C DOMI
  139 08 Rumanian List   A DORMI
  139 19 Sardinian C     DORMIRI
  139 11 Ladin           DORMIR
  139 10 Italian         DORMIRE
  139 23 Catalan         ADORMIRSE
  139 20 Spanish         DORMIR
  139 12 Provencal       DOURMI
  139 14 Walloon         DWERMI
  139 13 French          DORMIR
  139 16 French Creole D DOMI
  139 21 Portuguese ST   DORMIR
  139 22 Brazilian       DORMIR
b                      005
  139 38 Takitaki        SLIBI
  139 37 English ST      TO SLEEP
  139 24 German ST       SCHLAFEN
  139 29 Frisian         SLIEPE
  139 28 Flemish         SLAPEN
  139 25 Penn. Dutch     SCHLOEF
  139 26 Dutch List      SLAAP
  139 27 Afrikaans       SLAAP
b                      006
  139 56 Singhalese      NIDIYAGANAWA
  139 58 Marathi         NIJNE., JHOPNE.
  139 63 Bengali         NID JAOA
b                      007
  139 68 Greek Mod       KIMUME
  139 66 Greek ML        KOIMAMAI
  139 70 Greek K         KOIMOMAI
  139 67 Greek MD        KOIMAMAI
  139 69 Greek D         KOIMAMAI
b                      008
  139 03 Welsh N         CYSGU
  139 04 Welsh C         CYSGU
  139 05 Breton List     KOUSKET, HUNIA, HUNI
  139 06 Breton SE       KOUSKET
  139 07 Breton ST       KOUSKET
b                      009
  139 02 Irish B         CODLAIM
  139 01 Irish A         CODLADH
b                      010
  139 81 Albanian Top    FLE, AOR. FLEJTA
  139 80 Albanian T      ME FJETUR
  139 83 Albanian K      FLEE (AOR. FJETA)
  139 84 Albanian C      FLE
  139 82 Albanian G      FLE (FLEJT, FJET = INF.)
  139 95 ALBANIAN        FLE (FLEJT, FJET = INF.)
b                      200
c                         200  3  201
  139 36 Faroese         SOVA
  139 33 Danish          SOVE
  139 32 Swedish List    SOVA
  139 34 Riksmal         SOVE
  139 35 Icelandic ST    SOFA
  139 31 Swedish VL      SAVA  SAVA
  139 30 Swedish Up      SOVA
  139 51 Russian         SPAT
  139 85 RUSSIAN P       SPAT
  139 54 Serbocroatian   SPAVATI
  139 92 SERBOCROATIAN P SPATI
  139 46 Slovak          SPAT
  139 89 SLOVAK P        SPAT
  139 42 Slovenian       SPATI
  139 91 SLOVENIAN P     SPATI
  139 86 UKRAINIAN P     SPATY
  139 88 POLISH P        SPAC
  139 50 Polish          SPAC
  139 93 MACEDONIAN P    SPIJAM
  139 44 Lusatian U      SPAC
  139 43 Lusatian L      SPAS
  139 90 CZECH P         SPATI
  139 45 Czech           SPATI
  139 87 BYELORUSSIAN P  SPAC
  139 94 BULGARIAN P     SP A
  139 52 Macedonian      SPIE
  139 47 Czech E         SPAT
  139 49 Byelorussian    SPAC'
  139 48 Ukrainian       SPATY, ZASYPLJATY
  139 53 Bulgarian       DA SPI
  139 64 Nepali List     SUTNU
  139 61 Lahnda          SEMMEN
  139 59 Gujarati        UGHEWU, SUWU
  139 57 Kashmiri        SHONGUN
  139 62 Hindi           SONA
  139 60 Panjabi ST      SONA
  139 65 Khaskura        SUTNU
  139 71 Armenian Mod    K`NEL
  139 72 Armenian List   KUNANAL
b                      201
c                         200  3  201
  139 79 Wakhi           RUXP-, RUSEP-
a 140 SMALL
b                      001
  140 72 Armenian List   BUZDIG
  140 02 Irish B         CAOL
  140 58 Marathi         LEHAN
  140 57 Kashmiri        LUKU, LOKUTU, NIKA
  140 08 Rumanian List   MIC, MARUNT
  140 17 Sardinian N     MINORE
  140 59 Gujarati        NAHNU
  140 09 Vlach           NIKU
  140 38 Takitaki        PIKIN
  140 71 Armenian Mod    P`OK`R
b                      002
  140 24 German ST       KLEIN
  140 27 Afrikaans       KLEIN
  140 26 Dutch List      KLEIN
  140 25 Penn. Dutch     GLAY
  140 28 Flemish         KLEIN
  140 29 Frisian         KLIEN
b                      003
  140 23 Catalan         PETIT
  140 13 French          PETIT
  140 16 French Creole D PITI
  140 15 French Creole C PITI
  140 14 Walloon         P(I)TIT
  140 12 Provencal       PICHOT, OTO, PICHOUN
b                      004
  140 07 Breton ST       BIHAN
  140 06 Breton SE       BIHAN
  140 05 Breton List     BIHAN, MUNUT
  140 04 Welsh C         BACH
  140 03 Welsh N         BACH
  140 01 Irish A         BEAG
b                      005
  140 40 Lithuanian ST   MAZAS
  140 39 Lithuanian O    MAZAS
  140 41 Latvian         MAZS
b                      006
  140 20 Spanish         PEQUENO
  140 22 Brazilian       PEQUENO
  140 21 Portuguese ST   PEQUENO
b                      007
  140 11 Ladin           PITSCHEN
  140 18 Sardinian L     PICOCCU
  140 19 Sardinian C     PITTIKKU
  140 10 Italian         PICCOLO
b                      008
  140 68 Greek Mod       MIKRO
  140 66 Greek ML        MIKROS
  140 70 Greek K         MIKROS
  140 67 Greek MD        MIKROS
  140 69 Greek D         MIKROS
b                      009
  140 82 Albanian G      VOGEL
  140 84 Albanian C      I-VOGEL
  140 83 Albanian K      I VOGELE
  140 80 Albanian T      I, E VOGEL
  140 95 ALBANIAN        I VOGEL
  140 81 Albanian Top    I-VOGELH-I
b                      010
  140 35 Icelandic ST    LITILL
  140 34 Riksmal         LITEN
  140 32 Swedish List    LITEN
  140 33 Danish          LILLE
  140 30 Swedish Up      LITEN
  140 31 Swedish VL      LITN
  140 36 Faroese         LITIL, SMAUR
b                      011
  140 37 English ST      SMALL
  140 87 BYELORUSSIAN P  MALY
  140 45 Czech           MALY
  140 90 CZECH P         MALY
  140 43 Lusatian L      MALKI
  140 44 Lusatian U      MALY
  140 93 MACEDONIAN P    MAL
  140 50 Polish          MALY
  140 88 POLISH P        MALY
  140 51 Russian         MALEN KIJ
  140 85 RUSSIAN P       MALYJ
  140 54 Serbocroatian   MALI
  140 92 SERBOCROATIAN P MAO
  140 46 Slovak          MALY
  140 89 SLOVAK P        MALY
  140 42 Slovenian       MAJKEN, MICKN
  140 91 SLOVENIAN P     MAL
  140 86 UKRAINIAN P     MALYJ
  140 94 BULGARIAN P     MALUK
  140 52 Macedonian      DROBEN, MAL, MALECOK
  140 53 Bulgarian       MALKO
  140 48 Ukrainian       MALYJ, MALEN'KYJ, NEVELYKYJ
  140 49 Byelorussian    MALY
  140 47 Czech E         MALE
b                      200
c                         200  3  201
c                         200  3  202
  140 78 Baluchi         KIK
  140 79 Wakhi           ZUQ, ZUQIQ, ZUQULAEI
  140 73 Ossetic         CYSYL, GYCCYL
b                      201
c                         200  3  201
c                         201  3  202
  140 76 Persian List    KUCHEK
b                      202
c                         200  3  202
c                         201  3  202
c                         202  2  203
  140 74 Afghan          KUCNAJ, VOR
b                      203
c                         202  2  203
  140 75 Waziri          KAM, KAMKAI, WRIKAI WOR
b                      204
c                         204  2  205
  140 61 Lahnda          CHOTA
  140 60 Panjabi ST      CHOTTA
  140 62 Hindi           CHOTA
  140 63 Bengali         CHOTO
b                      205
c                         204  2  205
c                         205  2  206
  140 64 Nepali List     CHOTO, JHINU, SANU
b                      206
c                         205  2  206
  140 65 Khaskura        SIANO
b                      207
c                         207  3  400
  140 56 Singhalese      PODI, KUDA
b                      400
c                         207  3  400
  140 55 Gypsy Gk        XURDO
  140 77 Tadzik          XUDR, MAJDA
a 141 TO SMELL (PERCEIVE ODOR)
b                      000
  141 73 Ossetic
  141 79 Wakhi
  141 02 Irish B
  141 82 Albanian G
  141 75 Waziri
b                      001
  141 08 Rumanian List   A MIROSI
  141 09 Vlach           ANURYATE
  141 01 Irish A         BOLADH D'FHAGHAIL
  141 84 Albanian C      CURAR
  141 94 BULGARIAN P     DUCH
  141 19 Sardinian C     FRAGAI
  141 04 Welsh C         GWYNTIO
  141 56 Singhalese      IMBINAWA
  141 18 Sardinian L     INTENDERE
  141 55 Gypsy Gk        KHANDAV
  141 39 Lithuanian O    KVEPENTI
  141 17 Sardinian N     NUSKARE
  141 70 Greek K         OSFRAINOMAI
  141 57 Kashmiri        PHUKUN
  141 11 Ladin           SAVURER
  141 25 Penn. Dutch     SCHMOCK
  141 42 Slovenian       SMRDI
  141 29 Frisian         STJONKE
b                      002
  141 30 Swedish Up      LUKTA, KANNA LUKT
  141 31 Swedish VL      LUKT, TZAN LUKTA
  141 33 Danish          LUGTE
  141 32 Swedish List    LUKTA
  141 34 Riksmal         LUKTE
b                      003
  141 24 German ST       RIECHEN
  141 28 Flemish         RUIKEN
  141 27 Afrikaans       RUIK
  141 26 Dutch List      RUIKEN
b                      004
  141 52 Macedonian      MIRISA
  141 53 Bulgarian       DA POMIRISVA
  141 54 Serbocroatian   MIRISATI
  141 93 MACEDONIAN P    MIRIZBA
b                      005
  141 37 English ST      TO SMELL
  141 38 Takitaki        SMERI
b                      006
  141 95 ALBANIAN        MARR ER
  141 83 Albanian K      BIE EERE
  141 80 Albanian T      ME MANE ERE
  141 81 Albanian Top    MBAN ERE, AOR. MBAJTA
b                      007
  141 07 Breton ST       KLEVOUT
  141 06 Breton SE       KLEUET
  141 05 Breton List     KLEVOUT (EUR C'HOUEZ)
  141 03 Welsh N         AROGLEUO
b                      008
  141 22 Brazilian       CHEIRAR
  141 21 Portuguese ST   CHEIRAR
b                      009
  141 35 Icelandic ST    THEFA
  141 36 Faroese         TEVJA
b                      010
  141 77 Tadzik          XIS KARDAN
  141 74 Afghan          HYS KAVEL
b                      011
  141 68 Greek Mod       MIRIZO
  141 66 Greek ML        MURIDZO
  141 67 Greek MD        MURIDZOMAI
  141 69 Greek D         MURIDZO
b                      012
  141 76 Persian List    BU KARDAN (BU SHENIDAN)
  141 78 Baluchi         BO GIRAGH
b                      200
c                         200  2  201
  141 44 Lusatian U      WON
  141 89 SLOVAK P        VONA
  141 90 CZECH P         VUNE
  141 43 Lusatian L      WON
  141 88 POLISH P        WON
  141 92 SERBOCROATIAN P VONJA
  141 91 SLOVENIAN P     VONJA
  141 48 Ukrainian       NJUXATY
  141 47 Czech E         NYUXAT
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
  141 46 Slovak          NUCHAT , VONAT , PACHNUT
b                      202
c                         201  2  202
c                         202  2  203
  141 85 RUSSIAN P       ZAPACH
  141 86 UKRAINIAN P     ZAPACH
  141 87 BYELORUSSIAN P  PACH
b                      203
c                         201  2  203
c                         202  2  203
c                         203  2  204
  141 49 Byelorussian    CUC' PAX
b                      204
c                         203  2  204
  141 50 Polish          CZUC
  141 45 Czech           CITITI
  141 51 Russian         CUVSTVOVAT
b                      205
c                         205  2  206
  141 13 French          SENTIR
  141 16 French Creole D SATI
  141 14 Walloon         SINTI
  141 12 Provencal       SENTI
  141 15 French Creole C SATI
b                      206
c                         205  2  206
c                         206  2  207
  141 10 Italian         SENTIRE, ODORATE
b                      207
c                         206  2  207
  141 23 Catalan         OLORAR
  141 20 Spanish         OLER
  141 40 Lithuanian ST   UZUOSTI
  141 41 Latvian         OST
  141 72 Armenian List   HOD (HOD USKAL)
  141 71 Armenian Mod    HOTOTEL, HOT K`ASEL
b                      208
c                         208  3  209
  141 65 Khaskura        SUNGNU
  141 60 Panjabi ST      SUNGENA
  141 62 Hindi           SUGHNA
  141 64 Nepali List     SUNNU
  141 61 Lahnda          SUNNEN
  141 58 Marathi         HUNGNE.
b                      209
c                         208  3  209
  141 59 Gujarati        SUGHEWU
  141 63 Bengali         GONDHA+SOKA
a 142 SMOKE
b                      000
  142 70 Greek K
  142 69 Greek D
b                      001
  142 52 Macedonian      CAD
  142 71 Armenian Mod    CUX
  142 75 Waziri          DE YOR LIGAI
  142 73 Ossetic         FAEZDAEG, X"UAECAE
  142 53 Bulgarian       NUSEK
b                      002
  142 31 Swedish VL      ROK
  142 30 Swedish Up      ROK
  142 24 German ST       RAUCH
  142 35 Icelandic ST    REYKR
  142 34 Riksmal         ROK
  142 32 Swedish List    ROK
  142 33 Danish          ROG
  142 36 Faroese         ROYKUR
  142 29 Frisian         REEK, RIIK
  142 28 Flemish         ROOK
  142 26 Dutch List      ROOK
  142 27 Afrikaans       ROOK
b                      003
  142 25 Penn. Dutch     SCHMOECK
  142 38 Takitaki        SMOKO
  142 37 English ST      SMOKE
  142 03 Welsh N         MWG
  142 07 Breton ST       MOGED
  142 06 Breton SE       MOGED
  142 05 Breton List     MOGED, MOGEDENN
  142 04 Welsh C         MWG
  142 72 Armenian List   MOOGH
b                      004
  142 67 Greek MD        KAPNOS
  142 66 Greek ML        KAPNOS
  142 68 Greek Mod       KAPNOS
b                      005
  142 84 Albanian C      KAMNUA
  142 83 Albanian K      KAMNUA
b                      200
c                         200  3  201
c                         200  2  202
  142 09 Vlach           FUMU
  142 18 Sardinian L     FUMU
  142 17 Sardinian N     UMU
  142 15 French Creole C LAFIME
  142 08 Rumanian List   FUM
  142 11 Ladin           FUM
  142 19 Sardinian C     FUMU
  142 10 Italian         FUMO
  142 23 Catalan         FUM, GASSA
  142 20 Spanish         HUMO
  142 12 Provencal       FUM, FUMADO
  142 14 Walloon         FOUMIRE
  142 16 French Creole D LAFIME
  142 13 French          FUMEE
  142 21 Portuguese ST   FUMO
  142 22 Brazilian       FUMO
  142 02 Irish B         DEATACH, -AIGHE
  142 01 Irish A         DEATACH (TOIT U.)
  142 77 Tadzik          DUD
  142 79 Wakhi           DIT
  142 74 Afghan          DUD
  142 76 Persian List    DUD
  142 56 Singhalese      DUMA
  142 64 Nepali List     DHUWA
  142 61 Lahnda          DHU
  142 78 Baluchi         DUHON
  142 59 Gujarati        DHUMARO
  142 57 Kashmiri        DAH
  142 58 Marathi         DHUR
  142 63 Bengali         DHOA, DHUO
  142 62 Hindi           DHUA
  142 60 Panjabi ST      TUA
  142 65 Khaskura        DHUWAN
  142 55 Gypsy Gk        DUMANO
  142 91 SLOVENIAN P     DIM
  142 86 UKRAINIAN P     DYM
  142 42 Slovenian       DIM
  142 89 SLOVAK P        DYM
  142 44 Lusatian U      DYM
  142 93 MACEDONIAN P    DIM
  142 50 Polish          DYM
  142 88 POLISH P        DYM
  142 51 Russian         DYM
  142 85 RUSSIAN P       DYM
  142 54 Serbocroatian   DIM
  142 92 SERBOCROATIAN P DIM
  142 43 Lusatian L      DYM
  142 90 CZECH P         DYM
  142 87 BYELORUSSIAN P  DYM
  142 94 BULGARIAN P     DIM
  142 41 Latvian         DUMI
  142 39 Lithuanian O    DUMAI
  142 40 Lithuanian ST   DUMAI
  142 49 Byelorussian    DYM
  142 48 Ukrainian       DYM
b                      201
c                         200  3  201
c                         201  3  202
  142 80 Albanian T      TYM
  142 82 Albanian G      TYMI
  142 95 ALBANIAN        TYMI
  142 81 Albanian Top    TYM
b                      202
c                         200  2  202
c                         201  3  202
c                         202  2  203
  142 46 Slovak          DYM, KUR
b                      203
c                         202  2  203
  142 45 Czech           KOUR
  142 47 Czech E         KUR
a 143 SMOOTH
b                      001
  143 58 Marathi         GULGULIT
  143 71 Armenian Mod    HART`
  143 80 Albanian T      I, E BUTE
  143 81 Albanian Top    I-FERKUAR
  143 60 Panjabi ST      IK+SAR
  143 66 Greek ML        ISIOS
  143 09 Vlach           ISKU
  143 55 Gypsy Gk        ISYO
  143 39 Lithuanian O    LYGUS
  143 83 Albanian K      MALAKO
  143 69 Greek D         MALAKOS
  143 08 Rumanian List   NETED
  143 61 Lahnda          SAF
  143 64 Nepali List     SALAKKA
  143 57 Kashmiri        SATORU
  143 72 Armenian List   SHIDAG
  143 56 Singhalese      SILINOU
  143 37 English ST      SMOOTH
  143 59 Gujarati        SUWALU
  143 40 Lithuanian ST   SVELNUS, NESIURKSTUS
  143 63 Bengali         TELA
  143 77 Tadzik          XAMVOR, TAXT
b                      002
  143 78 Baluchi         LASUR
  143 79 Wakhi           LUS, HUNWOR
b                      003
  143 82 Albanian G      LIMUT
  143 95 ALBANIAN        LIMUT, BUT
b                      004
  143 67 Greek MD        HOMALOS
  143 68 Greek Mod       OMALOS
b                      005
  143 52 Macedonian      MAZEN
  143 93 MACEDONIAN P    MAZEN
b                      100
  143 62 Hindi           CIKNA
  143 65 Khaskura        CHILLO
b                      200
c                         200  3  201
  143 74 Afghan          HAVAR, SAF, MUSTAVI
  143 76 Persian List    SAF
b                      201
c                         200  3  201
  143 75 Waziri          SHOE, SHWE
b                      202
c                         202  2  203
  143 18 Sardinian L     LISU
  143 84 Albanian C      LISU
  143 15 French Creole C LIS
  143 11 Ladin           GLISCH
  143 19 Sardinian C     LISU
  143 23 Catalan         LLIS
  143 20 Spanish         LISO
  143 14 Walloon         LISSE
  143 16 French Creole D LIS
  143 13 French          LISSE
  143 22 Brazilian       LISO
  143 21 Portuguese ST   LISO
b                      203
c                         202  2  203
c                         203  2  204
  143 10 Italian         PIANO, LISCIO
b                      204
c                         203  2  204
  143 12 Provencal       UNI, IDO, PLANIE
  143 17 Sardinian N     PRANU
b                      205
c                         205  2  206
  143 06 Breton SE       FLOUR
b                      206
c                         205  2  206
c                         206  2  207
c                         206  2  208
c                         206  3  400
  143 07 Breton ST       LEVN, FLOUR
b                      207
c                         206  2  207
c                         207  2  208
c                         207  3  400
  143 03 Welsh N         LLYFN
  143 04 Welsh C         LLYFN
  143 70 Greek K         LEIOS
  143 73 Ossetic         LAEG"Z
  143 35 Icelandic ST    SLETTR
  143 36 Faroese         SLAETTUR
  143 30 Swedish Up      SLAT, JAMN
  143 31 Swedish VL      SLAT  SLET, JAMN
  143 01 Irish A         SLEAMHAIN, REIDH, MIN
b                      208
c                         206  2  208
c                         207  2  208
c                         208  2  209
c                         208  3  400
  143 32 Swedish List    SLAT, GLATT
b                      209
c                         208  2  209
  143 50 Polish          GLADKI
  143 88 POLISH P        GLADKI
  143 51 Russian         GLADKIJ
  143 85 RUSSIAN P       GLADKIJ
  143 54 Serbocroatian   GLADAK
  143 92 SERBOCROATIAN P GLADAK
  143 46 Slovak          HLADKY
  143 89 SLOVAK P        HLADKY
  143 42 Slovenian       GLADKO
  143 91 SLOVENIAN P     GLADEK
  143 86 UKRAINIAN P     HLADKYJ
  143 45 Czech           HLADKY
  143 90 CZECH P         HLADKY
  143 43 Lusatian L      GLADKI
  143 44 Lusatian U      HLADKI
  143 87 BYELORUSSIAN P  HLADKI
  143 94 BULGARIAN P     GLADUK
  143 38 Takitaki        GLATI
  143 24 German ST       GLATT
  143 34 Riksmal         GLATT, JEVN
  143 33 Danish          GLAT
  143 29 Frisian         GLAD
  143 28 Flemish         GLAD, EFFEN
  143 25 Penn. Dutch     GLOT
  143 26 Dutch List      GELIJK, GLAD
  143 27 Afrikaans       GLAD, SAG
  143 47 Czech E         HLADKE
  143 49 Byelorussian    HLADKI
  143 48 Ukrainian       HLADKYJ, RIVNYJ
  143 53 Bulgarian       GLADKO
  143 41 Latvian         GLUDS, LIDZENS
b                      400
c                         206  3  400
c                         207  3  400
c                         208  3  400
  143 05 Breton List     KOMPEZ, KUNV, LUFR, LINTR
  143 02 Irish B         BLAITH, -E, MIN, -E, LIMHTHA
a 144 SNAKE
b                      000
  144 16 French Creole D
  144 01 Irish A
b                      001
  144 41 Latvian         CUSKA
  144 79 Wakhi           FUKS
  144 42 Slovenian       KACA
  144 73 Ossetic         KALM
  144 75 Waziri          MANGER
  144 09 Vlach           NEPUNDIKE
  144 57 Kashmiri        SARAPH
b                      002
  144 46 Slovak          HAD
  144 90 CZECH P         HAD
  144 45 Czech           HAD
  144 47 Czech E         HAD
  144 48 Ukrainian       HADJUKA, HADYNA
b                      003
  144 74 Afghan          MAR
  144 78 Baluchi         MAR
  144 77 Tadzik          MOR
  144 76 Persian List    MAR
b                      004
  144 86 UKRAINIAN P     ZMIJA
  144 91 SLOVENIAN P     ZMIJA
  144 89 SLOVAK P        ZMIJA
  144 92 SERBOCROATIAN P ZMIJA
  144 54 Serbocroatian   ZMIJA
  144 85 RUSSIAN P       ZMEJA
  144 51 Russian         ZMEJA
  144 88 POLISH P        ZMIJA
  144 93 MACEDONIAN P    ZMIJA
  144 44 Lusatian U      ZMIJA
  144 43 Lusatian L      ZMIJA
  144 87 BYELORUSSIAN P  ZM AJA
  144 94 BULGARIAN P     ZMIJA
  144 52 Macedonian      ZMIJA
  144 49 Byelorussian    Z'MJAJA
  144 53 Bulgarian       ZMIJA
b                      005
  144 38 Takitaki        SNEKI
  144 37 English ST      SNAKE
b                      006
  144 18 Sardinian L     SERPENTE
  144 17 Sardinian N     THERPENTE
  144 08 Rumanian List   SARPE
  144 11 Ladin           SERP, ZERP
  144 19 Sardinian C     SERPENTI
  144 10 Italian         SERPE
  144 23 Catalan         SERP, SERPENT
  144 12 Provencal       SERP, SERPENT
  144 14 Walloon         SIERPINT, CHERPINT
  144 13 French          SERPENT
  144 64 Nepali List     SAP
  144 55 Gypsy Gk        SAP
  144 61 Lahnda          SEP
  144 58 Marathi         SAP
  144 63 Bengali         SAP
  144 62 Hindi           SAP
  144 60 Panjabi ST      SEPP
  144 59 Gujarati        SAP, (NAG)
b                      007
  144 20 Spanish         CULEBRA
  144 21 Portuguese ST   COBRA
  144 22 Brazilian       COBRA
  144 15 French Creole C (NO GENERIC TERM) KULEV, KUHWES (GRASS)
b                      008
  144 07 Breton ST       NAER
  144 06 Breton SE       NAER
  144 05 Breton List     AER (NAER)
  144 04 Welsh C         NEIDR
  144 03 Welsh N         NEIDR
  144 02 Irish B         NATHAIR NIMHE
b                      009
  144 40 Lithuanian ST   GYVATE, ZALTYS
  144 39 Lithuanian O    GYVATE
b                      010
  144 81 Albanian Top    GARPER
  144 80 Albanian T      GJARPER
  144 83 Albanian K      GARPER
  144 84 Albanian C      GALPHRH
  144 82 Albanian G      BERI, BOLLA, GJARPEN
  144 95 ALBANIAN        BOLLA, BERI, GJARPEN
b                      200
c                         200  3  400
  144 71 Armenian Mod    OJ
  144 72 Armenian List   OTZ
  144 68 Greek Mod       FIDHI
  144 66 Greek ML        FIDI
  144 67 Greek MD        FIDI
  144 69 Greek D         FIDI
  144 70 Greek K         OFUS
  144 50 Polish          WAZ
b                      400
c                         200  3  400
  144 56 Singhalese      NAYA
  144 65 Khaskura        LAMKIRA, NAG
b                      201
c                         201  2  202
  144 30 Swedish Up      ORM
  144 31 Swedish VL      ORM
  144 34 Riksmal         ORM
  144 32 Swedish List    ORM
  144 35 Icelandic ST    (HOGGORMUR)
b                      202
c                         201  2  202
c                         202  3  203
  144 36 Faroese         (HOGG)ORMUR, ALANGA
b                      203
c                         202  3  203
  144 24 German ST       SCHLANGE
  144 33 Danish          SLANGE
  144 29 Frisian         SLANG, SLANGE
  144 28 Flemish         SLANG
  144 25 Penn. Dutch     SCHLUNG
  144 26 Dutch List      SLANG
  144 27 Afrikaans       SLANG
a 145 SNOW
b                      000
  145 15 French Creole C LANEZ (ONLY AS PROPER NAME)
b                      001
  145 17 Sardinian N     FROKKA
  145 36 Faroese         KAVI
  145 73 Ossetic         MIT
  145 55 Gypsy Gk        YIV
  145 08 Rumanian List   ZAPADA
  145 79 Wakhi           ZEM
b                      002
  145 61 Lahnda          BERF, BERREF
  145 77 Tadzik          BARF
  145 59 Gujarati        BEREF
  145 76 Persian List    BARF
  145 63 Bengali         BOROP
  145 62 Hindi           BERPH
  145 60 Panjabi ST      BEREPH
  145 78 Baluchi         BAWAR
  145 74 Afghan          VAVRA
  145 75 Waziri          WOVRA
b                      003
  145 05 Breton List     ERC'H
  145 04 Welsh C         EIRA
  145 03 Welsh N         EIRA, OD
  145 06 Breton SE       ERH
  145 07 Breton ST       ERC'H
b                      004
  145 09 Vlach           NEAWE
  145 18 Sardinian L     NIE
  145 11 Ladin           NAIV
  145 19 Sardinian C     NI
  145 10 Italian         NEVE
  145 23 Catalan         NEU
  145 20 Spanish         NIEVE
  145 12 Provencal       NEU
  145 14 Walloon         NIVAYE
  145 16 French Creole D LANEZ
  145 13 French          NEIGE
  145 21 Portuguese ST   NEVE
  145 22 Brazilian       NEVE
  145 30 Swedish Up      SNO
  145 31 Swedish VL      SNO
  145 86 UKRAINIAN P     SNIH
  145 94 BULGARIAN P     SN AG
  145 87 BYELORUSSIAN P  SNEH
  145 45 Czech           SNIH
  145 90 CZECH P         SNIH
  145 43 Lusatian L      SNEG
  145 44 Lusatian U      SNEH
  145 93 MACEDONIAN P    SNEG
  145 50 Polish          SNIEG
  145 88 POLISH P        SNIEG
  145 51 Russian         SNEG
  145 85 RUSSIAN P       SNEG
  145 54 Serbocroatian   SNEG
  145 92 SERBOCROATIAN P SNEG
  145 46 Slovak          SNEH
  145 89 SLOVAK P        SNEH
  145 42 Slovenian       SNEK
  145 91 SLOVENIAN P     SNEG
  145 40 Lithuanian ST   SNIEGAS
  145 39 Lithuanian O    SNIEGAS
  145 41 Latvian         SNIEGS
  145 02 Irish B         SNEACHTADH, -AIDH
  145 01 Irish A         SNEACHTA
  145 33 Danish          SNE
  145 32 Swedish List    SNO
  145 34 Riksmal         SNE
  145 35 Icelandic ST    SNJOR
  145 24 German ST       SCHNEE
  145 29 Frisian         SNIE
  145 28 Flemish         SNEEUW
  145 25 Penn. Dutch     SCHNAY
  145 26 Dutch List      SNEEUW
  145 27 Afrikaans       KAPOK, SNEEU
  145 52 Macedonian      SNEG
  145 47 Czech E         SNEH
  145 49 Byelorussian    S'NEH
  145 48 Ukrainian       SNIH
  145 53 Bulgarian       SNJAG
  145 38 Takitaki        SNEEUW
  145 37 English ST      SNOW
b                      005
  145 81 Albanian Top    TEBORE
  145 80 Albanian T      DHBORE
  145 84 Albanian C      ZBOR
  145 83 Albanian K      BORE
  145 82 Albanian G      BORA
  145 95 ALBANIAN        BORA
b                      200
c                         200  3  201
  145 67 Greek MD        CHIONI
  145 69 Greek D         CHIONI
  145 70 Greek K         CHION
  145 66 Greek ML        CHIONI
  145 68 Greek Mod       CHYONI
  145 56 Singhalese      HIMA
  145 64 Nepali List     HIU
  145 58 Marathi         HIME
  145 65 Khaskura        HIUN
  145 71 Armenian Mod    JYUN
  145 72 Armenian List   SZUN
b                      201
c                         200  3  201
  145 57 Kashmiri        SHIN
a 146 SOME
b                      000
  146 57 Kashmiri
  146 07 Breton ST
  146 06 Breton SE
  146 72 Armenian List
b                      001
  146 05 Breton List     BENNAK
  146 08 Rumanian List   CITEVA
  146 25 Penn. Dutch     DAYL
  146 24 German ST       ETWAS
  146 29 Frisian         GUN(T)
  146 78 Baluchi         KHARD-E
  146 42 Slovenian       MALO
  146 09 Vlach           NEDEAME
  146 51 Russian         NEMNOGO
  146 71 Armenian Mod    OMANK`
  146 56 Singhalese      TIKA
  146 50 Polish          TROCHE
  146 55 Gypsy Gk        XARNWK
b                      002
  146 39 Lithuanian O    KELI
  146 40 Lithuanian ST   KELI, KELETAS
b                      003
  146 04 Welsh C         RHAI
  146 03 Welsh N         RHAI
b                      004
  146 01 Irish A         EIGIAN
  146 02 Irish B         EIGIN
b                      005
  146 16 French Creole D CEK
  146 15 French Creole C CEK (ADJ.), ADA (PN.)
b                      006
  146 82 Albanian G      DITSH
  146 95 ALBANIAN        GJA, SETSH, DITSH
  146 80 Albanian T      DISA
b                      200
c                         200  2  201
  146 33 Danish          NOGEN
  146 34 Riksmal         NOEN
  146 32 Swedish List    NAGON, NAGRA
  146 30 Swedish Up      NAGRA
  146 36 Faroese         NAKRIR
  146 35 Icelandic ST    NOKKRIR
b                      201
c                         200  2  201
c                         201  2  202
  146 31 Swedish VL      NAGRA, NA ENAR
b                      202
c                         201  2  202
c                         202  2  203
  146 28 Flemish         EENIGE, SOMMIGE
  146 26 Dutch List      EENIGE, SOMMIGE
  146 27 Afrikaans       ENIGE, PARTY, SOMMIGE
b                      203
c                         202  2  203
  146 37 English ST      SOME
  146 38 Takitaki        SOM
b                      204
c                         204  2  205
c                         204  2  207
c                         204  2  209
c                         204  3  210
c                         204  2  211
c                         204  3  400
  146 44 Lusatian U      NEKELKO
  146 59 Gujarati        KETLAK, THORU
  146 41 Latvian         KADS, DAZI, DRUSKU
  146 52 Macedonian      NEKOLKU
  146 53 Bulgarian       NJAKOLKO
  146 47 Czech E         NEKERE, NEKOLIK
  146 43 Lusatian L      NEKOTARY
  146 45 Czech           NEKTERY
  146 89 SLOVAK P        NIEKTORY
  146 46 Slovak          NIEKTORY
  146 93 MACEDONIAN P    NEKOJ
  146 92 SERBOCROATIAN P NEKI
  146 54 Serbocroatian   NEKI
  146 85 RUSSIAN P       NEKIJ
  146 91 SLOVENIAN P     NEKI
  146 94 BULGARIAN P     N AKOJ
  146 13 French          QUELQUE
  146 14 Walloon         KEKE, QUEQUE
  146 12 Provencal       QUAUQUIS-UN
  146 18 Sardinian L     CALCHI
  146 17 Sardinian N     KARKI
  146 23 Catalan         COLCOM
  146 81 Albanian Top    CA
  146 84 Albanian C      CA
  146 83 Albanian K      CA
  146 74 Afghan          CO, CE KADR
  146 65 Khaskura        KOI
  146 64 Nepali List     KOI
  146 58 Marathi         KAHI
  146 62 Hindi           KUCH, KOI, KEI
  146 60 Panjabi ST      KUS
  146 61 Lahnda          KUJH
  146 10 Italian         ALCUNI
  146 20 Spanish         ALGUNO
  146 22 Brazilian       ALGUM
  146 21 Portuguese ST   ALGUM, UM
  146 63 Bengali         KICU
  146 77 Tadzik          ANDAK, KAM
b                      205
c                         204  2  205
c                         205  2  206
c                         205  2  207
c                         205  2  209
c                         205  3  210
c                         205  2  211
c                         205  3  400
  146 48 Ukrainian       JAKYJS', AS', ES', XTOS', TROXY
  146 49 Byelorussian    NEKATORY, NEJKI
b                      206
c                         205  2  206
  146 87 BYELORUSSIAN P  NEJKI
  146 88 POLISH P        NIEJAKI
  146 90 CZECH P         NEJAKY
  146 86 UKRAINIAN P     DEJAKIJ
b                      207
c                         204  2  207
c                         205  2  207
c                         207  2  208
c                         207  2  209
c                         207  3  210
c                         207  2  211
c                         207  3  400
  146 11 Ladin           ALCH, QUALCHE, TSCHERTUNS
b                      208
c                         207  2  208
  146 19 Sardinian C     CERTU
b                      209
c                         204  2  209
c                         205  2  209
c                         207  2  209
c                         209  2  210
c                         209  2  211
c                         209  3  400
  146 79 Wakhi           TSUM, TSUMER, KUMD, CIZ
b                      210
c                         204  3  210
c                         205  3  210
c                         207  3  210
c                         209  2  210
c                         210  3  211
c                         210  3  400
  146 73 Ossetic         CYSYL
b                      211
c                         204  2  211
c                         205  2  211
c                         207  2  211
c                         209  2  211
c                         210  3  211
c                         211  2  212
c                         211  2  213
c                         211  3  400
  146 68 Greek Mod       MERIKI, KANENAS, KATI
b                      212
c                         211  2  212
c                         212  2  213
  146 70 Greek K         MERIKOI
  146 69 Greek D         MERIKOI
b                      213
c                         211  2  213
c                         212  2  213
c                         213  2  214
  146 67 Greek MD        LIGOS, MERIKOI
b                      214
c                         213  2  214
  146 66 Greek ML        LIGOS
b                      400
c                         204  3  400
c                         205  3  400
c                         207  3  400
c                         209  3  400
c                         210  3  400
c                         211  3  400
  146 75 Waziri          DZENE, TSE
  146 76 Persian List    BA'ZI
a 147 TO SPIT
b                      001
  147 55 Gypsy Gk        CUNGAR
  147 02 Irish B         DO CHUR AR BHIOR
  147 23 Catalan         ETJEGAR, EIXIR PANSAS
  147 56 Singhalese      KELAGAHANAWA
  147 62 Hindi           KHUKNA
  147 01 Irish A         SEILE DO CHAITHEAMH
  147 79 Wakhi           SEX
b                      002
  147 81 Albanian Top    PSTYT, AOR. PSTYTA
  147 80 Albanian T      ME PESHTYRE
  147 84 Albanian C      PUSTIN
  147 83 Albanian K      PESTIIN
  147 82 Albanian G      MESHTY J
  147 95 ALBANIAN        MESHTYJ
b                      003
  147 05 Breton List     SKOPA, TUFA, KRANCHAT
  147 06 Breton SE       SKOPEIN
  147 07 Breton ST       TUFAN, SKOPAN-
b                      004
  147 17 Sardinian N     GRUSPIRE
  147 18 Sardinian L     RUSPIARE
b                      005
  147 74 Afghan          TUKEL, TUKAVEL
  147 78 Baluchi         THUK (SB.)
b                      006
  147 04 Welsh C         POERI
  147 03 Welsh N         POERI
b                      200
c                         200  3  201
  147 73 Ossetic         TU KAENYN
  147 76 Persian List    TOF KARDAN
  147 77 Tadzik          TUF KARDAN
b                      201
c                         200  3  201
  147 75 Waziri          TIKAWEL
b                      202
c                         202  3  400
  147 57 Kashmiri        THOKUN
  147 64 Nepali List     THUKNU
  147 61 Lahnda          THUKKEN
  147 65 Khaskura        THUKNU
  147 60 Panjabi ST      THUKKENA
  147 58 Marathi         THUNKNE.
b                      400
c                         202  3  400
  147 59 Gujarati        THURWU
  147 63 Bengali         THUTU+PHELA
b                      203
c                         203  3  204
c                         203  3  205
  147 14 Walloon         RETCHI
b                      204
c                         203  3  204
c                         204  3  205
  147 13 French          CRACHER
  147 15 French Creole C KHWASE
  147 16 French Creole D KWASE
b                      205
c                         203  3  205
c                         204  3  205
c                         205  2  206
  147 11 Ladin           SCRACHER, SPUDER
b                      206
c                         205  2  206
  147 20 Spanish         ESCUPIR
  147 12 Provencal       ESCUPI, SALIVA
  147 21 Portuguese ST   CUSPIR
  147 22 Brazilian       CUSPIR
  147 08 Rumanian List   A SCUIPA
  147 19 Sardinian C     SKUPPI
  147 09 Vlach           ASKUKU
  147 68 Greek Mod       FTYO
  147 66 Greek ML        FTUNO
  147 70 Greek K         PTUO
  147 67 Greek MD        FTUNO
  147 69 Greek D         FTUNO
  147 30 Swedish Up      SPOTTA
  147 31 Swedish VL      SPOT
  147 40 Lithuanian ST   SPIAUTI
  147 39 Lithuanian O    SPIAUSTI
  147 41 Latvian         SPLAUTIES
  147 10 Italian         SPUTARE
  147 24 German ST       SPEIEN
  147 35 Icelandic ST    SPYTA
  147 34 Riksmal         SPYTTE
  147 32 Swedish List    SPAT
  147 33 Danish          SPYTTE
  147 36 Faroese         SPYTA
  147 27 Afrikaans       SPU(UG), SPOE(G)
  147 26 Dutch List      SPUWEN
  147 25 Penn. Dutch     SCHPAUTZ
  147 28 Flemish         SPUWEN
  147 29 Frisian         SPIJE
  147 38 Takitaki        SPITI
  147 37 English ST      TO SPIT
  147 86 UKRAINIAN P     PL UVATY
  147 91 SLOVENIAN P     PLJUVATI
  147 42 Slovenian       PLUNI
  147 89 SLOVAK P        PL UT
  147 46 Slovak          PL UT
  147 92 SERBOCROATIAN P PLJUVATI
  147 54 Serbocroatian   PLJUVATI
  147 85 RUSSIAN P       PLEVAT
  147 51 Russian         PLEVAT
  147 88 POLISH P        PLUC
  147 50 Polish          PLUC
  147 93 MACEDONIAN P    PLUKAM
  147 44 Lusatian U      PLUWAC
  147 43 Lusatian L      PLUWAS
  147 87 BYELORUSSIAN P  PL AVAC
  147 45 Czech           PLIVATI
  147 90 CZECH P         PLITI
  147 94 BULGARIAN P     PL UJA
  147 52 Macedonian      PLUE
  147 47 Czech E         PLUT
  147 49 Byelorussian    PLERAC'
  147 48 Ukrainian       PLJUVATY
  147 53 Bulgarian       DA PLJUE
  147 72 Armenian List   TUKNEL
  147 71 Armenian Mod    T`UK`
a 148 TO SPLIT
b                      000
  148 79 Wakhi
  148 77 Tadzik
  148 59 Gujarati
b                      001
  148 78 Baluchi         BURAGH, BURITHA
  148 75 Waziri          CHAWEL
  148 23 Catalan         CRIVELLAR, ESQUERDAR
  148 08 Rumanian List   A (SE) DESPICA
  148 09 Vlach           DISIKU
  148 48 Ukrainian       DROBYTY
  148 73 Ossetic         FANDYN
  148 72 Armenian List   JEGHKEL
  148 71 Armenian Mod    KTREL
  148 67 Greek MD        KOBO
  148 74 Afghan          MATAVEL
  148 76 Persian List    NESF KARDAN
  148 61 Lahnda          TOREN
  148 60 Panjabi ST      VEKKH+KERNA
  148 84 Albanian C      XAP
  148 19 Sardinian C     ZAKKAI
b                      002
  148 24 German ST       SPALTEN
  148 25 Penn. Dutch     SCHPOLLD
  148 29 Frisian         SPJALTE, SPLISSE, SPLITSE
  148 27 Afrikaans       SPLITS, VERDEEL
  148 37 English ST      TO SPLIT
  148 38 Takitaki        PLITI
  148 28 Flemish         SPLITSEN
  148 26 Dutch List      SPLIJTEN
  148 32 Swedish List    SPLITTRA
b                      003
  148 34 Riksmal         KLOVE
  148 35 Icelandic ST    KLJUFA
  148 33 Danish          KLOVE
  148 36 Faroese         KLUGVA
  148 30 Swedish Up      KLYVA
  148 31 Swedish VL      KLYV
b                      004
  148 70 Greek K         SPADZO
  148 69 Greek D         SPAO
b                      005
  148 91 SLOVENIAN P     LOMITI
  148 86 UKRAINIAN P     LAMATY
  148 89 SLOVAK P        LOMIT
  148 92 SERBOCROATIAN P LOMITI
  148 85 RUSSIAN P       LOMIT
  148 88 POLISH P        LAMAC
  148 90 CZECH P         LAMATI
  148 43 Lusatian L      LOMIS
  148 44 Lusatian U      LAMAC
  148 93 MACEDONIAN P    SLOMAM
  148 94 BULGARIAN P     LOM A
  148 87 BYELORUSSIAN P  LAMAC
b                      006
  148 46 Slovak          STIEPAT, ROZSTIEPIT
  148 50 Polish          ROZSZCZEPIAC
  148 45 Czech           STIPATI, ROZSTIPNOUTI
  148 47 Czech E         ROSCIPNUT
  148 49 Byelorussian    RAZSCAPLJAC'
b                      007
  148 80 Albanian T      ME CARE
  148 83 Albanian K      SKIER
b                      008
  148 82 Albanian G      TSHAJ
  148 95 ALBANIAN        TSHAJ
  148 81 Albanian Top    CAN, CAJTA = AOR.
b                      200
c                         200  2  201
  148 68 Greek Mod       SKIZO
  148 66 Greek ML        SKIDZO
  148 52 Macedonian      CEPI
  148 53 Bulgarian       DA RAZCEPI
  148 42 Slovenian       RASCEPAJ
  148 55 Gypsy Gk        CHINAV
  148 62 Hindi           CIRNA
  148 58 Marathi         CIRNE.
b                      201
c                         200  2  201
c                         201  2  202
  148 65 Khaskura        CHIRNU, PHATNU
  148 64 Nepali List     PHARNU, CIRNU
b                      202
c                         201  2  202
  148 63 Bengali         PHARA
  148 57 Kashmiri        PHALUN, PHATUN
  148 56 Singhalese      PALANAWA
b                      203
c                         203  2  204
  148 22 Brazilian       FENDER
  148 20 Spanish         HENDER, RAJAR
  148 21 Portuguese ST   FENDER, RACHAR
  148 14 Walloon         FINDE, HINER, FALIER, HIYI, CRENER
  148 15 French Creole C FAN
  148 11 Ladin           SFENDER, FENDER
  148 13 French          FENDRE
  148 16 French Creole D FAN
  148 12 Provencal       ESPECA, FENDRE
b                      204
c                         203  2  204
c                         204  2  205
  148 10 Italian         FENDARE, SPACCARE
b                      205
c                         204  2  205
  148 18 Sardinian L     ISPACCARE
  148 17 Sardinian N     ISPAKKARE
b                      206
c                         206  2  207
  148 54 Serbocroatian   KALATI
  148 51 Russian         RASKALYVAT
b                      207
c                         206  2  207
c                         207  2  208
  148 41 Latvian         SASKALDIT, SASKELT
b                      208
c                         207  2  208
  148 40 Lithuanian ST   SKELTI
  148 39 Lithuanian O    SKELTI
  148 07 Breton ST       FAOUTAN
  148 06 Breton SE       FEUTEIN
  148 05 Breton List     FAOUTA
  148 04 Welsh C         HOLLTI
  148 03 Welsh N         HOLLTI
  148 01 Irish A         SCOILTEADH
  148 02 Irish B         SCOILTIM
a 149 TO SQUEEZE
b                      000
  149 55 Gypsy Gk
  149 57 Kashmiri
  149 38 Takitaki
  149 75 Waziri
  149 72 Armenian List
b                      001
  149 73 Ossetic         AELX"IVYN, (AELVASYN)
  149 01 Irish A         BRUGHADH
  149 78 Baluchi         DABAGH, DABITHA
  149 66 Greek ML        DZOULO
  149 71 Armenian Mod    K`AMEL
  149 74 Afghan          KSEKSEL
  149 64 Nepali List     MICNU
  149 56 Singhalese      MIRIKANAWA
  149 58 Marathi         PILNE.
  149 54 Serbocroatian   PROTURATI
  149 67 Greek MD        SFIGGO
  149 37 English ST      TO SQUEEZE
  149 11 Ladin           SQUITSCHER
  149 05 Breton List     STARDA, STENNA
  149 84 Albanian C      STRENGON
  149 79 Wakhi           TRUNJ-, FERIL, WEZEM-
  149 68 Greek Mod       ZUPO
b                      002
  149 26 Dutch List      PERSEN
  149 27 Afrikaans       UITPERS
b                      003
  149 28 Flemish         WRINGEN
  149 29 Frisian         WRINGE
b                      004
  149 52 Macedonian      STEGA
  149 93 MACEDONIAN P    STEGAM
b                      005
  149 86 UKRAINIAN P     HNITYTY
  149 91 SLOVENIAN P     GNESTI
  149 89 SLOVAK P        HNIEST
  149 92 SERBOCROATIAN P GNJECITI
  149 85 RUSSIAN P       GNESTI
  149 50 Polish          GNIESC
  149 88 POLISH P        GNIESC
  149 43 Lusatian L      GNESIS
  149 90 CZECH P         HNISTI
  149 94 BULGARIAN P     GNETA
  149 87 BYELORUSSIAN P  HN ASCI
b                      006
  149 44 Lusatian U      ZIMAC
  149 51 Russian         SZIMAT
b                      007
  149 42 Slovenian       STISNI
  149 46 Slovak          TISNUT
  149 45 Czech           ZMACKNOUTI, STISKNOUTI
  149 47 Czech E         STYISKNUT
  149 49 Byelorussian    SCISKAC', VYCISKAC'
  149 48 Ukrainian       DAVYTY, TYSNUTY, DUSYTY
  149 53 Bulgarian       DA STISNE
b                      008
  149 34 Riksmal         KLEMME
  149 30 Swedish Up      KLAMMA
  149 31 Swedish VL      KLAM
  149 32 Swedish List    KRAMA, KLAMMA
b                      009
  149 24 German ST       DRUCKEN
  149 25 Penn. Dutch     DRICK
  149 33 Danish          TRYKKE
b                      010
  149 35 Icelandic ST    KREISTA
  149 36 Faroese         KROYSTA
b                      011
  149 82 Albanian G      SHTYP
  149 95 ALBANIAN        SHTYP
b                      012
  149 07 Breton ST       GWESKEL
  149 02 Irish B         FAISCIM
  149 06 Breton SE       GOASKEIN
  149 04 Welsh C         GWASGU
  149 03 Welsh N         GWASGU
b                      013
  149 70 Greek K         PIEDZO
  149 69 Greek D         PIEDZO
b                      014
  149 40 Lithuanian ST   SUSPAUSTI
  149 39 Lithuanian O    SPAUDYTI
  149 41 Latvian         SPIEST
b                      015
  149 76 Persian List    FESHAR DADAN
  149 77 Tadzik          FUSURDAN, FISOR DODAN
b                      016
  149 81 Albanian Top    STRYTH, AOR. STRYDHA
  149 83 Albanian K      STRIDHIN
  149 80 Albanian T      ME SHTRYDHUR
b                      017
  149 16 French Creole D PIZE
  149 15 French Creole C PIZE
b                      018
  149 62 Hindi           NICORNA
  149 60 Panjabi ST      NECORNA
  149 61 Lahnda          NICOREN
  149 59 Gujarati        NICOWEWU
b                      019
  149 65 Khaskura        NICHAUNU, CHEPNU, ANTIAUNU
  149 63 Bengali         CAP+DEOA
b                      200
c                         200  2  201
c                         200  2  203
c                         200  2  207
  149 10 Italian         PREMERE
  149 19 Sardinian C     SPREMI
  149 17 Sardinian N     ISPREMERE
  149 18 Sardinian L     PREMERE
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  3  207
  149 20 Spanish         APRETAR, COMORIMIR,ESTRECHAR
  149 21 Portuguese ST   APERTAR, COMPRIMIR
b                      202
c                         201  2  202
  149 22 Brazilian       APERTAR
b                      203
c                         200  2  203
c                         201  2  203
c                         203  3  204
c                         203  3  205
c                         203  3  207
  149 23 Catalan         COMPRIMIR, ESTRENYER, PITJAR
b                      204
c                         203  3  204
c                         204  3  205
c                         204  2  208
  149 08 Rumanian List   A STOARCE, A STRINGE
b                      205
c                         203  3  205
c                         204  3  205
c                         205  2  206
c                         205  2  207
  149 14 Walloon         SERER, STRINDE
b                      206
c                         205  2  206
c                         206  2  207
  149 13 French          SERRER
b                      207
c                         200  2  207
c                         201  3  207
c                         203  3  207
c                         205  2  207
c                         206  2  207
  149 12 Provencal       SARRA, PRESSA
b                      208
c                         204  2  208
  149 09 Vlach           STIRKORU
a 150 TO STAB (OR STICK)
b                      000
  150 55 Gypsy Gk
  150 67 Greek MD
  150 78 Baluchi
  150 07 Breton ST
  150 06 Breton SE
  150 82 Albanian G
  150 84 Albanian C
  150 76 Persian List
  150 95 ALBANIAN
  150 59 Gujarati
  150 75 Waziri
b                      001
  150 73 Ossetic         AERGAEVDYN
  150 56 Singhalese      ANINAWA
  150 09 Vlach           ARUPU
  150 58 Marathi         BHOSEKNE.
  150 61 Lahnda          CIPKAWEN
  150 53 Bulgarian       DA NAMUSI
  150 42 Slovenian       DREGNE
  150 10 Italian         FERIRE
  150 32 Swedish List    GENOMBORRA
  150 05 Breton List     GOUSTILHA, KONTELLA
  150 03 Welsh N         GWANU
  150 17 Sardinian N     ISTUKKITHTHARE
  150 68 Greek Mod       LAVONO
  150 66 Greek ML        MACHAIRONO
  150 77 Tadzik          OB DODAN, OBUTOB DODAN
  150 23 Catalan         PEGAR, ENGANYAR, BURLAR, MOCAR
  150 49 Byelorussian    PRABIC'
  150 38 Takitaki        SOETOE
  150 37 English ST      TO STAB
  150 31 Swedish VL      STAMP
  150 11 Ladin           STILETTER
  150 57 Kashmiri        TASANUN
  150 51 Russian         ZAKALYVAT
b                      002
  150 70 Greek K         KTUPO
  150 69 Greek D         CHTUPAO
b                      003
  150 30 Swedish Up      STICKA (IHJAL)
  150 34 Riksmal         STIKKE
  150 24 German ST       ERSTECHEN
  150 27 Afrikaans       STEEK
  150 26 Dutch List      STEKEN
  150 25 Penn. Dutch     SCHTECH
  150 28 Flemish         STEKEN
  150 29 Frisian         STYKJE
  150 33 Danish          STIKKE
b                      004
  150 36 Faroese         STINGA
  150 35 Icelandic ST    STINGA
b                      005
  150 81 Albanian Top    CPON, AOR. CPOVA
  150 83 Albanian K      CEPON ME THIKE
  150 80 Albanian T      ME CPUAR
b                      006
  150 50 Polish          KLUC
  150 88 POLISH P        KLUC
  150 43 Lusatian L      KLOJS
  150 44 Lusatian U      KLOC
  150 91 SLOVENIAN P     KLATI
  150 86 UKRAINIAN P     KOLOTY
  150 85 RUSSIAN P       KOLOT
  150 87 BYELORUSSIAN P  KALOC
  150 48 Ukrainian       RANYTY, KOLOTY, DJUGATY
b                      007
  150 40 Lithuanian ST   DURTI
  150 39 Lithuanian O    SMIEGTI, DURTI
  150 41 Latvian         IEDURT, IESPRAUST
b                      008
  150 16 French Creole D CUK
  150 15 French Creole C VAHWE, PICE, CUK, COKE
b                      100
  150 79 Wakhi           XULA DI-
  150 74 Afghan          HALALAVEL
b                      101
  150 01 Irish A         SATHADH
  150 04 Welsh C         BRATHU
  150 02 Irish B         DO RATHADH, LE SCIN, DO MHARBHADH
b                      102
  150 71 Armenian Mod    XREL
  150 72 Armenian List   ZARNEL
b                      200
c                         200  3  201
  150 13 French          POIGNARDER
  150 18 Sardinian L     PUNGHERE
  150 19 Sardinian C     PUNNALAI
  150 14 Walloon         POUGNARDER
  150 12 Provencal       POUGNARDA
  150 20 Spanish         DAR DE PUNALADAS
  150 22 Brazilian       APUNHALAR
  150 21 Portuguese ST   APUNHALAR
b                      201
c                         200  3  201
  150 08 Rumanian List   A INJUNGHIA CU PUMNALUL
b                      202
c                         202  2  203
  150 64 Nepali List     GOPNU, GHOCNU
b                      203
c                         202  2  203
c                         203  2  204
  150 65 Khaskura        GHOCHNU CHHURI DASNU
b                      204
c                         203  2  204
  150 60 Panjabi ST      CURA+MARNA
  150 62 Hindi           CHURA+MARNA
  150 63 Bengali         CHORA+MARA
b                      205
c                         205  2  206
  150 89 SLOVAK P        BODAT
  150 93 MACEDONIAN P    BODAM
  150 45 Czech           BODNOUTI, BODATI
  150 90 CZECH P         BODATI
  150 52 Macedonian      BODE
  150 94 BULGARIAN P     BODA
  150 54 Serbocroatian   UBOSTI
  150 92 SERBOCROATIAN P BOSTI
b                      206
c                         205  2  206
c                         206  2  207
  150 46 Slovak          BODAT , PICHAT
b                      207
c                         206  2  207
  150 47 Czech E         PIXNUT
a 151 TO STAND
b                      000
  151 79 Wakhi
  151 55 Gypsy Gk
  151 23 Catalan
  151 22 Brazilian
b                      001
  151 19 Sardinian C     ATTURAI
  151 72 Armenian List   GAYNEL
  151 56 Singhalese      HITAGANAWA
  151 71 Armenian Mod    KANGNEL
  151 73 Ossetic         LAEUUYN
  151 80 Albanian T      ME PENDRUAR
  151 78 Baluchi         OSHTAGH, OSHTATHA
b                      002
  151 74 Afghan          DAREDEL
  151 75 Waziri          DAREDEL
b                      003
  151 81 Albanian Top    RI NE KEMBE
  151 83 Albanian K      RII (AOR. (M)BETA  (N)DINA)
  151 84 Albanian C      RI STUERA
  151 82 Albanian G      RRI ME KAM
  151 95 ALBANIAN        RRI ME KAM
b                      004
  151 20 Spanish         ESTAR EN PIE
  151 21 Portuguese ST   ESTAR EM PE
  151 14 Walloon         SO PI, SO DJAMBE
  151 08 Rumanian List   A STA (IN PICIOARE)
b                      005
  151 15 French Creole C DUBUT, DIBUT
  151 12 Provencal       ARRESTA, ESTRE DEBOUT
  151 13 French          DEBOUT
  151 16 French Creole D DUBUT
b                      200
c                         200  3  201
  151 62 Hindi           KHERA+HONA
  151 63 Bengali         KHARA+HOOA
  151 61 Lahnda          KHEROWEN
b                      201
c                         200  3  201
  151 60 Panjabi ST      KHELONA
b                      202
c                         202  2  203
  151 64 Nepali List     UBHINU
  151 59 Gujarati        UBHA, ENEWU (UBHEWU)
  151 58 Marathi         UBHA+RAHNE.
b                      203
c                         202  2  203
c                         203  3  204
c                         203  2  205
  151 65 Khaskura        UBHINU, THARO HUNNU, ARINU
b                      204
c                         203  3  204
c                         204  3  205
  151 57 Kashmiri        THODU WOTHUN
b                      205
c                         203  2  205
c                         204  3  205
  151 04 Welsh C         SEFYLL
  151 03 Welsh N         SEFYLL
  151 05 Breton List     WAR ZAV, EN E ZAV, SOUNN
  151 06 Breton SE       BOUT EN E SAU
  151 07 Breton ST       BEZAN EN E SAV
  151 18 Sardinian L     ISTARE
  151 17 Sardinian N     ISTARE
  151 68 Greek Mod       STEKOME
  151 66 Greek ML        STEKOMAI
  151 67 Greek MD        STEKOMAI
  151 69 Greek D         STEKOMAI
  151 70 Greek K         HISTAMAI
  151 38 Takitaki        TANAPOE, TANAPO
  151 39 Lithuanian O    STOVETI
  151 41 Latvian         STAVET
  151 94 BULGARIAN P     STOJA
  151 87 BYELORUSSIAN P  STAJAC
  151 45 Czech           STATI
  151 90 CZECH P         STATI
  151 43 Lusatian L      STOJAS
  151 44 Lusatian U      STEJEC
  151 93 MACEDONIAN P    STOAM
  151 50 Polish          STAC
  151 88 POLISH P        STAC
  151 51 Russian         STOJAT
  151 85 RUSSIAN P       STOJAT
  151 54 Serbocroatian   STAJATI
  151 92 SERBOCROATIAN P STAJATI
  151 46 Slovak          STAT
  151 89 SLOVAK P        STAT
  151 42 Slovenian       STAJ
  151 91 SLOVENIAN P     STATI
  151 86 UKRAINIAN P     STOJATY
  151 40 Lithuanian ST   STOVETI
  151 11 Ladin           STER
  151 10 Italian         STARE
  151 30 Swedish Up      STA
  151 31 Swedish VL      STA
  151 09 Vlach           STAU
  151 02 Irish B         SEASAIM
  151 01 Irish A         SEASAMH
  151 24 German ST       STEHEN
  151 35 Icelandic ST    STANDA
  151 34 Riksmal         STA
  151 32 Swedish List    STA
  151 33 Danish          STAA
  151 36 Faroese         STANDA
  151 29 Frisian         STEAN
  151 28 Flemish         STAEN
  151 25 Penn. Dutch     SCHTAY
  151 26 Dutch List      STAAN
  151 27 Afrikaans       STAAN
  151 77 Tadzik          ISTODAN
  151 52 Macedonian      STANE, STOI
  151 76 Persian List    ISTADAN
  151 53 Bulgarian       DA STOI
  151 48 Ukrainian       STOJATY
  151 47 Czech E         STAT
  151 49 Byelorussian    STAMC'
  151 37 English ST      TO STAND
a 152 STAR
b                      001
  152 55 Gypsy Gk        CERAIN
  152 84 Albanian C      IZE (DEF. IZJA)
b                      002
  152 49 Byelorussian    ZORKA
  152 48 Ukrainian       ZIRKA, ZORA
  152 87 BYELORUSSIAN P  ZARA
b                      003
  152 86 UKRAINIAN P     ZVIZDA
  152 91 SLOVENIAN P     ZVEZDA
  152 42 Slovenian       ZVEZDO
  152 89 SLOVAK P        HVIEZDA
  152 46 Slovak          HVIEZDA
  152 92 SERBOCROATIAN P ZVEZDA
  152 54 Serbocroatian   ZVEZDA
  152 85 RUSSIAN P       ZVEZDA
  152 51 Russian         ZVEZDA
  152 88 POLISH P        GWIAZDA
  152 50 Polish          GWIAZDA
  152 93 MACEDONIAN P    DZVEZDA
  152 44 Lusatian U      HWEZDA
  152 43 Lusatian L      GWEZDA
  152 90 CZECH P         HVEZDA
  152 45 Czech           HVEZDA
  152 94 BULGARIAN P     ZVEZDA
  152 41 Latvian         ZVAIGZNE
  152 39 Lithuanian O    ZVAIGZDE
  152 40 Lithuanian ST   ZVAIGZDE
  152 52 Macedonian      SVEZDA
  152 47 Czech E         HVEZDA
  152 53 Bulgarian       ZVEZDA
b                      004
  152 06 Breton SE       STIREN
  152 05 Breton List     STERED
  152 04 Welsh C         SEREN
  152 03 Welsh N         SEREN
  152 28 Flemish         STER
  152 29 Frisian         STER(RE), STJIR(RE)
  152 25 Penn. Dutch     SCHTAAN
  152 26 Dutch List      STER
  152 27 Afrikaans       STER
  152 38 Takitaki        STAR, STARI
  152 37 English ST      STAR
  152 36 Faroese         STJORNA
  152 33 Danish          STJERNE
  152 32 Swedish List    STJARNA
  152 34 Riksmal         STJERNE
  152 35 Icelandic ST    STJARNA
  152 24 German ST       STERN
  152 07 Breton ST       STEREDENN
  152 08 Rumanian List   STEA
  152 11 Ladin           ASTER
  152 30 Swedish Up      STJARNA
  152 31 Swedish VL      SANA
  152 69 Greek D         ASTRO
  152 67 Greek MD        ASTERI
  152 70 Greek K         ASTER
  152 66 Greek ML        ASTRO
  152 68 Greek Mod       ASTRO
  152 71 Armenian Mod    ASTL
  152 72 Armenian List   ARD
  152 09 Vlach           STEAWE
  152 18 Sardinian L     ISTELLA
  152 17 Sardinian N     ISTEDDU
  152 15 French Creole C ZETWEL
  152 19 Sardinian C     STELLA
  152 10 Italian         STELLA
  152 23 Catalan         ESTELA, ESTEL
  152 20 Spanish         ESTRELLA
  152 12 Provencal       ESTELLO
  152 14 Walloon         STEULE
  152 16 French Creole D ZETWEL
  152 13 French          ETOILE
  152 21 Portuguese ST   ESTRELLA
  152 22 Brazilian       ESTRELA (ESTRELLA)
  152 75 Waziri          STORAI
  152 73 Ossetic         YST"ALY
  152 79 Wakhi           STOR
  152 78 Baluchi         ISTAR
  152 74 Afghan          STORAJ
  152 76 Persian List    SETARE
  152 77 Tadzik          SITORA
  152 56 Singhalese      TARUVA
  152 57 Kashmiri        TARUKH
  152 64 Nepali List     TARO
  152 61 Lahnda          TARA
  152 59 Gujarati        TARO
  152 60 Panjabi ST      TARA
  152 62 Hindi           TARA
  152 63 Bengali         TARA
  152 58 Marathi         TARA
  152 65 Khaskura        TARA
b                      005
  152 02 Irish B         REALT, -TAN, -TANNA
  152 01 Irish A         REALT
b                      006
  152 81 Albanian Top    YL
  152 83 Albanian K      IIU
  152 80 Albanian T      YLL
  152 82 Albanian G      YLLI
  152 95 ALBANIAN        YLLI
a 153 STICK (OF WOOD)
b                      000
  153 09 Vlach
  153 35 Icelandic ST
  153 52 Macedonian
  153 22 Brazilian
b                      001
  153 76 Persian List    CHUB
  153 03 Welsh N         FFON, PASTWN
  153 79 Wakhi           GHWUZ, SUNG
  153 04 Welsh C         GWIALEN
  153 55 Gypsy Gk        KAS
  153 67 Greek MD        KLARI
  153 43 Lusatian L      KOLK
  153 32 Swedish List    KVIST
  153 73 Ossetic         LAEDZAEG
  153 71 Armenian Mod    MAHAK, BIR
  153 01 Irish A         MAIDE
  153 39 Lithuanian O    MALKAS
  153 16 French Creole D MOSO BWA
  153 41 Latvian         NUJA, KOKS
  153 40 Lithuanian ST   PAGALYS
  153 72 Armenian List   PAYD (I)
  153 23 Catalan         PERN, GARROT
  153 17 Sardinian N     RAMU
  153 60 Panjabi ST      SOTTI
  153 54 Serbocroatian   STAP
  153 36 Faroese         STAVUR
  153 77 Tadzik          TAEK, ASO
b                      002
  153 86 UKRAINIAN P     PALKA
  153 91 SLOVENIAN P     PALICA
  153 42 Slovenian       PALCA
  153 89 SLOVAK P        PALICA
  153 92 SERBOCROATIAN P PALICA
  153 85 RUSSIAN P       PALKA
  153 51 Russian         PALKA
  153 88 POLISH P        PALKA
  153 93 MACEDONIAN P    PALICA
  153 87 BYELORUSSIAN P  PALKA
  153 94 BULGARIAN P     PALICA
  153 47 Czech E         PALICKA
b                      003
  153 20 Spanish         PALO
  153 21 Portuguese ST   PAO
b                      004
  153 50 Polish          KIJ
  153 44 Lusatian U      KIJ
  153 49 Byelorussian    KIJ
  153 48 Ukrainian       KYJOK, NALYCKA
b                      005
  153 18 Sardinian L     BASTONE
  153 15 French Creole C BATO
  153 13 French          BATON
  153 10 Italian         BASTONE
  153 19 Sardinian C     BASTONI
  153 11 Ladin           BASTUN
  153 08 Rumanian List   BAT
  153 12 Provencal       BASTOUN, TRICO, CANO
  153 14 Walloon         BASTON, BORDON
b                      006
  153 46 Slovak          PRUT
  153 53 Bulgarian       PRECKA
b                      007
  153 58 Marathi         DANDU
  153 62 Hindi           DENDA
b                      008
  153 74 Afghan          LARGAJ, LAKARA
  153 75 Waziri          LARGAI
b                      009
  153 81 Albanian Top    SKOP
  153 80 Albanian T      SHKOP
  153 83 Albanian K      SKOP
  153 82 Albanian G      SHKOPI
  153 95 ALBANIAN        SHKOPI, TSHOMAGU
b                      010
  153 02 Irish B         BATA
  153 07 Breton ST       BAZH
  153 06 Breton SE       BAH
  153 05 Breton List     BAZ
b                      011
  153 45 Czech           TYCKA, HUL
  153 90 CZECH P         HUL
b                      012
  153 69 Greek D         KSULARAKI
  153 68 Greek Mod       KSILO
  153 66 Greek ML        KSULO
  153 70 Greek K         KSULON
b                      013
  153 25 Penn. Dutch     SCHTECKE
  153 30 Swedish Up      KAPP, STICKA
  153 31 Swedish VL      STIKA, TZVET,TZAP
  153 38 Takitaki        TIKI
  153 37 English ST      STICK
  153 27 Afrikaans       STOK
  153 26 Dutch List      STOK
  153 28 Flemish         STOK
  153 29 Frisian         STOK
  153 33 Danish          STOK
  153 34 Riksmal         STOKK
  153 24 German ST       STOCK
b                      100
  153 84 Albanian C      DRU
  153 56 Singhalese      DARA/KALLA, DARA/KOTTA
b                      200
c                         200  2  201
  153 78 Baluchi         LATH
  153 63 Bengali         LATHI
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
  153 64 Nepali List     JHATARO, LATHO, LAURO
b                      202
c                         201  2  202
c                         202  2  203
  153 57 Kashmiri        LURU
  153 59 Gujarati        LAKRI (WOOD = LAKRU)
b                      203
c                         201  2  203
c                         202  2  203
c                         203  2  204
  153 65 Khaskura        LAURO, CHHARI
b                      204
c                         203  2  204
  153 61 Lahnda          CHERI
a 154 STONE
b                      001
  154 11 Ladin           CRAP, SASS
  154 74 Afghan          DABARA
  154 73 Ossetic         DUR
  154 56 Singhalese      GALA
  154 79 Wakhi           GHAR
  154 09 Vlach           KATRE
  154 78 Baluchi         KHOH
  154 75 Waziri          KONRAI, TIZHA
b                      002
  154 67 Greek MD        PETRA
  154 69 Greek D         PETRA
  154 68 Greek Mod       PETRA
  154 66 Greek ML        PETRA
  154 70 Greek K         PETRA
b                      003
  154 07 Breton ST       MAEN
  154 06 Breton SE       MAEN
  154 05 Breton List     MAEN
b                      004
  154 30 Swedish Up      STEN
  154 31 Swedish VL      STEN
  154 24 German ST       STEIN
  154 35 Icelandic ST    STEINN
  154 34 Riksmal         STEN
  154 32 Swedish List    STEN
  154 33 Danish          STEN
  154 36 Faroese         STEINUR, GROT
  154 29 Frisian         STIEN
  154 28 Flemish         STEEN
  154 25 Penn. Dutch     SCHTAY
  154 26 Dutch List      STEEN
  154 27 Afrikaans       STEEN
  154 38 Takitaki        STOON, STON
  154 37 English ST      STONE
b                      005
  154 77 Tadzik          SANG
  154 76 Persian List    SANG
b                      006
  154 43 Lusatian L      KAMEN
  154 44 Lusatian U      KAMJEN
  154 93 MACEDONIAN P    KAMEN
  154 50 Polish          KAMIEN
  154 88 POLISH P        KAMIEN
  154 51 Russian         KAMEN
  154 85 RUSSIAN P       KAMEN
  154 54 Serbocroatian   KAMEN
  154 92 SERBOCROATIAN P KAMEN
  154 46 Slovak          KAMEN
  154 89 SLOVAK P        KAMEN
  154 42 Slovenian       KAMEN
  154 91 SLOVENIAN P     KAMEN
  154 86 UKRAINIAN P     KAMIN
  154 94 BULGARIAN P     KAMUK
  154 87 BYELORUSSIAN P  KAMEN
  154 45 Czech           KAMEN
  154 90 CZECH P         KAMEN
  154 40 Lithuanian ST   AKMUO
  154 39 Lithuanian O    AKMUO
  154 41 Latvian         AKMENS
  154 52 Macedonian      KAMEN
  154 47 Czech E         KAMENY
  154 49 Byelorussian    KAMEN'
  154 48 Ukrainian       KAMIN'
  154 53 Bulgarian       KAMEK
b                      007
  154 81 Albanian Top    GUR
  154 80 Albanian T      GUR
  154 83 Albanian K      GUUR
  154 84 Albanian C      GUR
  154 82 Albanian G      GURI
  154 95 ALBANIAN        GURI
b                      008
  154 64 Nepali List     DHUNGO
  154 65 Khaskura        DHUNGA
b                      009
  154 61 Lahnda          PETTHER
  154 59 Gujarati        PETTNER
  154 58 Marathi         PETTHER
  154 63 Bengali         PATHOR
  154 62 Hindi           PETTHER
  154 60 Panjabi ST      PETTHER
b                      010
  154 01 Irish A         CLOCH
  154 02 Irish B         CLOCH, -OICHE, -A
b                      100
  154 55 Gypsy Gk        BAR
  154 57 Kashmiri        WATH, KUNU
b                      200
c                         200  3  201
  154 04 Welsh C         CARREG
  154 03 Welsh N         CARREG
b                      201
c                         200  3  201
  154 71 Armenian Mod    K`AR
  154 72 Armenian List   KAR
b                      202
c                         202  2  203
  154 18 Sardinian L     PEDRA
  154 17 Sardinian N     PRETA
  154 08 Rumanian List   PIATRA
  154 19 Sardinian C     PERDA
  154 10 Italian         PIETRA
  154 20 Spanish         PIEDRA
  154 12 Provencal       PEIRO, CLAPO
  154 14 Walloon         PIRE
  154 13 French          PIERRE
  154 21 Portuguese ST   PEDRA
  154 22 Brazilian       PEDRA
b                      203
c                         202  2  203
c                         203  2  204
  154 23 Catalan         PEDRA, ROCH
b                      204
c                         203  2  204
  154 15 French Creole C HWOS
  154 16 French Creole D WOS
a 155 STRAIGHT
b                      000
  155 91 SLOVENIAN P
  155 86 UKRAINIAN P
  155 89 SLOVAK P
  155 92 SERBOCROATIAN P
  155 85 RUSSIAN P
  155 90 CZECH P
  155 43 Lusatian L
  155 44 Lusatian U
  155 93 MACEDONIAN P
  155 88 POLISH P
  155 94 BULGARIAN P
  155 87 BYELORUSSIAN P
  155 52 Macedonian
  155 38 Takitaki
b                      001
  155 70 Greek K         EITHUS
  155 55 Gypsy Gk        ISYO
  155 56 Singhalese      KELIN
  155 33 Danish          LIGE
  155 58 Marathi         SEREL
  155 78 Baluchi         SIDHA
  155 72 Armenian List   SHIDAG
  155 37 English ST      STRAIGHT
  155 82 Albanian G      TAMAM, BASH
  155 71 Armenian Mod    ULIL
b                      002
  155 68 Greek Mod       ISYOS
  155 66 Greek ML        ISIOS
  155 67 Greek MD        ISIOS
  155 69 Greek D         ISIOS
b                      003
  155 40 Lithuanian ST   TIESUS
  155 39 Lithuanian O    TIESUS
  155 41 Latvian         TAISNI
b                      004
  155 64 Nepali List     SOJO
  155 65 Khaskura        SOJHO
  155 63 Bengali         SOJA
b                      005
  155 51 Russian         PRJAMOJ
  155 48 Ukrainian       PRJAMYJ
  155 45 Czech           PRIMY
b                      006
  155 61 Lahnda          SIDDHA
  155 59 Gujarati        SIDHU
  155 60 Panjabi ST      SIDDA
  155 62 Hindi           SIDHA
  155 57 Kashmiri        SYODU
b                      007
  155 75 Waziri          SAM, SIKH
  155 74 Afghan          SAM
b                      008
  155 49 Byelorussian    PROSTY, PROSTA
  155 50 Polish          PROSTY
b                      009
  155 53 Bulgarian       PRAVO
  155 54 Serbocroatian   USPRAVAN
b                      010
  155 24 German ST       GERADE
  155 25 Penn. Dutch     GRAWD
b                      011
  155 47 Czech E         ROVNE
  155 46 Slovak          ROVNY
  155 42 Slovenian       NREOVNAJT
b                      012
  155 95 ALBANIAN        DREJT
  155 81 Albanian Top    DREJTE
  155 84 Albanian C      I-DREJT
  155 83 Albanian K      I DREJTE
  155 80 Albanian T      I, E DREJTE
b                      013
  155 01 Irish A         DIREACH
  155 02 Irish B         DIREACH, -RIGHE
b                      200
c                         200  2  201
  155 07 Breton ST       EEUN
  155 06 Breton SE       EANN
  155 05 Breton List     EEUN, EUN
b                      201
c                         200  2  201
c                         201  2  202
  155 04 Welsh C         SYTH, UNION
b                      202
c                         201  2  202
  155 03 Welsh N         SYTH
b                      203
c                         203  2  204
  155 28 Flemish         RECHT
  155 34 Riksmal         RETT
  155 32 Swedish List    RAK, RAT
  155 29 Frisian         RJUCHT
  155 27 Afrikaans       REG
  155 26 Dutch List      RECHT
  155 30 Swedish Up      RAT
  155 31 Swedish VL      RAT
  155 77 Tadzik          ROST, MUSTAKIM
  155 76 Persian List    RAST
  155 73 Ossetic         RAST, KOMKOMMAE
  155 79 Wakhi           ROST
  155 22 Brazilian       DIREITO, RETO (RECTO)
  155 20 Spanish         DERECHO, RECTO
  155 23 Catalan         RECTE, DRET
  155 10 Italian         DIRITTO
  155 19 Sardinian C     DERETTU
  155 11 Ladin           DRET
  155 08 Rumanian List   DREPT
  155 13 French          DROIT
  155 16 French Creole D DWET
  155 14 Walloon         DREUT
  155 12 Provencal       DRE, IERO, DRECHURIE
  155 09 Vlach           NDREAPTE
  155 21 Portuguese ST   DIREITO
  155 17 Sardinian N     DERETTU
  155 18 Sardinian L     DERETTU
  155 15 French Creole C DWET
b                      204
c                         203  2  204
c                         204  2  205
  155 36 Faroese         RAETTUR, BEINUR
b                      205
c                         204  2  205
  155 35 Icelandic ST    BEINN
a 156 TO SUCK
b                      000
  156 55 Gypsy Gk
  156 25 Penn. Dutch
b                      001
  156 58 Marathi         COKHNE.
  156 73 Ossetic         DAEJYN, C"IRYN
  156 83 Albanian K      MENT   PII SI LEPUSE
  156 11 Ladin           TETTER, TSCHUTSCHER
  156 56 Singhalese      URANAWA
  156 68 Greek Mod       VIZENO
b                      002
  156 64 Nepali List     CUSNU
  156 61 Lahnda          CHUSEN
  156 59 Gujarati        CUSWU
  156 63 Bengali         CHOSA
  156 62 Hindi           CUSNA
  156 60 Panjabi ST      CUSNA
  156 65 Khaskura        CHUSNU
  156 57 Kashmiri        TSAHUN
b                      003
  156 74 Afghan          RUDEL
  156 75 Waziri          RAVDEL
b                      004
  156 66 Greek ML        HROUFO
  156 70 Greek K         ROUFO
  156 67 Greek MD        ROUFO, BUDZAINO, THELADZO
  156 69 Greek D         ROUFAO
b                      005
  156 39 Lithuanian O    CIULPTI
  156 40 Lithuanian ST   CIULPTI
b                      006
  156 71 Armenian Mod    CCEL
  156 72 Armenian List   KASHEL
b                      007
  156 95 ALBANIAN        THITH
  156 80 Albanian T      ME THETHIRE
  156 84 Albanian C      THITH
  156 82 Albanian G      THITH
  156 81 Albanian Top    THETHIN, AOR. THETHIVA
b                      200
c                         200  3  201
  156 77 Tadzik          MAKIDAN
  156 76 Persian List    MEKIDAN
b                      201
c                         200  3  201
  156 78 Baluchi         MISHAGH, MIKHTA
b                      202
c                         202  2  203
  156 93 MACEDONIAN P    CICAM
  156 47 Czech E         CUCAT
  156 43 Lusatian L      CYCAS
  156 44 Lusatian U      CYCAC
b                      203
c                         202  2  203
c                         203  2  204
c                         203  2  205
  156 52 Macedonian      SMUKNE/CICA
b                      204
c                         203  2  204
c                         204  2  205
  156 94 BULGARIAN P     SMUCA
  156 53 Bulgarian       DA SMUCI
b                      205
c                         203  2  205
c                         204  2  205
c                         205  2  206
c                         205  2  207
c                         205  2  209
c                         205  2  210
  156 48 Ukrainian       SMOKTATY, SSATY
b                      206
c                         205  2  206
c                         206  2  207
c                         206  2  209
c                         206  2  210
  156 49 Byelorussian    SSAC'
  156 41 Latvian         ZIST, SUKT
  156 87 BYELORUSSIAN P  SSAC
  156 45 Czech           SSATI
  156 90 CZECH P         SSATI
  156 50 Polish          SSAC
  156 88 POLISH P        SSAC
  156 51 Russian         SOSAT
  156 85 RUSSIAN P       SOSAT
  156 54 Serbocroatian   SISATI
  156 92 SERBOCROATIAN P SISATI
  156 46 Slovak          SAT
  156 89 SLOVAK P        SAT
  156 42 Slovenian       SOSAT
  156 91 SLOVENIAN P     SISATI
  156 86 UKRAINIAN P     SSATY
  156 27 Afrikaans       SUIG, SUIE
  156 38 Takitaki        ZUIGI
  156 37 English ST      TO SUCK
  156 30 Swedish Up      SUGA
  156 31 Swedish VL      SUG
  156 09 Vlach           SUKU
  156 18 Sardinian L     SUZZARE
  156 17 Sardinian N     SUTHTHARE
  156 15 French Creole C SUSE
  156 08 Rumanian List   A SUGE
  156 19 Sardinian C     SUCCAI
  156 10 Italian         SUCCHIARE
  156 23 Catalan         XUCLAR, TRAGAR, ATRACAR
  156 12 Provencal       SUCA, CHUCHA, TETA
  156 14 Walloon         SUCI
  156 16 French Creole D SUSE
  156 13 French          SUCER
  156 24 German ST       SAUGEN
  156 35 Icelandic ST    SJUGA
  156 34 Riksmal         SU
  156 32 Swedish List    SUGA  PA
  156 33 Danish          SUGE
  156 36 Faroese         SUGVA
  156 29 Frisian         SUGE, SUGJE
  156 28 Flemish         ZUIGEN
  156 26 Dutch List      ZUIGEN
  156 03 Welsh N         SUGNO
  156 04 Welsh C         SUGNO
  156 05 Breton List     SUN
  156 79 Wakhi           SUP-
b                      207
c                         205  2  207
c                         206  2  207
c                         207  2  208
c                         207  2  209
c                         207  2  210
  156 22 Brazilian       CHUPAR, CHUCHAR, SUGAR
b                      208
c                         207  2  208
  156 21 Portuguese ST   CHUPAR, CHUCHAR, MAMAR
  156 20 Spanish         CHUPAR
b                      209
c                         205  2  209
c                         206  2  209
c                         207  2  209
c                         209  2  210
c                         209  3  211
  156 07 Breton ST       SUNAN, DENAN (OF BABIES)
  156 06 Breton SE       SUNEIN, DENEIN ( OF BABIES)
b                      210
c                         205  2  210
c                         206  2  210
c                         207  2  210
c                         209  2  210
c                         210  2  211
  156 02 Irish B         DO DHIUIL, DO DHEOL, SUGHAIM
b                      211
c                         209  3  211
c                         210  2  211
  156 01 Irish A         DIUL
a 157 SUN
b                      001
  157 56 Singhalese      IRA
b                      002
  157 71 Armenian Mod    AREW, AREGAK
  157 72 Armenian List   AREV
b                      003
  157 74 Afghan          LMAR
  157 75 Waziri          LMER, MYER
b                      004
  157 81 Albanian Top    DIEL
  157 80 Albanian T      DIELLE
  157 84 Albanian C      DIEX
  157 83 Albanian K      DIEU
  157 82 Albanian G      DILLI
  157 95 ALBANIAN        DILLI
b                      200
c                         200  2  201
  157 77 Tadzik          OFTOB
  157 76 Persian List    AFTAB (KHORSHID)
b                      201
c                         200  2  201
c                         201  3  202
  157 79 Wakhi           YIR, OFTOB
b                      202
c                         201  3  202
  157 78 Baluchi         RO, ROSH
b                      203
c                         203  2  204
  157 24 German ST       SONNE
  157 29 Frisian         SINNE
  157 28 Flemish         ZON
  157 25 Penn. Dutch     SUUN
  157 26 Dutch List      ZON
  157 27 Afrikaans       SON
  157 38 Takitaki        ZON
  157 37 English ST      SUN
  157 30 Swedish Up      SOL
  157 31 Swedish VL      SOL
  157 09 Vlach           SWARE
  157 18 Sardinian L     SOLE
  157 17 Sardinian N     SOLE
  157 15 French Creole C SOLEY
  157 40 Lithuanian ST   SAULE
  157 39 Lithuanian O    SAULE
  157 41 Latvian         SAULE
  157 68 Greek Mod       ILYOS
  157 66 Greek ML        HELIOS
  157 70 Greek K         HELIOS
  157 67 Greek MD        HELIOS
  157 69 Greek D         HELIOS
  157 08 Rumanian List   SOARE
  157 11 Ladin           SOLAGL
  157 19 Sardinian C     SOLI
  157 10 Italian         SOLE
  157 23 Catalan         SOL
  157 20 Spanish         SOL
  157 12 Provencal       SOULEU
  157 14 Walloon         SOLO
  157 16 French Creole D SOLEY
  157 13 French          SOLEIL
  157 03 Welsh N         HAUL
  157 04 Welsh C         HAUL
  157 05 Breton List     HEOL
  157 06 Breton SE       HIAUL
  157 07 Breton ST       HEOL
  157 35 Icelandic ST    SOL
  157 34 Riksmal         SOL
  157 32 Swedish List    SOL
  157 33 Danish          SOL
  157 36 Faroese         SOL
  157 21 Portuguese ST   SOL
  157 22 Brazilian       SOL
  157 94 BULGARIAN P     SLUNCE
  157 87 BYELORUSSIAN P  SONCA
  157 45 Czech           SLUNCE
  157 90 CZECH P         SLUNCE
  157 43 Lusatian L      SLYNCO
  157 44 Lusatian U      SLONCO
  157 93 MACEDONIAN P    SLNCE
  157 50 Polish          SLONCE
  157 88 POLISH P        SLONCE
  157 51 Russian         SOLNCE
  157 85 RUSSIAN P       SOLNCE
  157 54 Serbocroatian   SUNCE
  157 92 SERBOCROATIAN P SUNCE
  157 46 Slovak          SLNKO
  157 89 SLOVAK P        SLNCE
  157 42 Slovenian       SUNCE
  157 91 SLOVENIAN P     SUNCE
  157 86 UKRAINIAN P     SONCE
  157 52 Macedonian      SONCE
  157 47 Czech E         SLUNKO
  157 49 Byelorussian    SONCA
  157 48 Ukrainian       SONCE
  157 53 Bulgarian       SLENCE
  157 73 Ossetic         XUR, XURZAERIN
  157 57 Kashmiri        SURE
  157 64 Nepali List     SURJE
  157 61 Lahnda          SUREJ
  157 59 Gujarati        SURDJ
  157 58 Marathi         SURYYE
  157 63 Bengali         SUJJO, SURJO
  157 62 Hindi           SUREJ
  157 60 Panjabi ST      SUREJ
b                      204
c                         203  2  204
c                         204  2  205
  157 65 Khaskura        GHAM, SURJ
b                      205
c                         204  2  205
  157 55 Gypsy Gk        KHAM
  157 02 Irish B         GRIAN
  157 01 Irish A         GRIAN
a 158 TO SWELL
b                      000
  158 38 Takitaki
b                      001
  158 76 Persian List    BAD KARDAN
  158 53 Bulgarian       DA SE PODUE
  158 57 Kashmiri        HANUN, WOTHUN
  158 34 Riksmal         HOVNE OPP
  158 56 Singhalese      IDIMENAWA
  158 52 Macedonian      NABABRI
  158 73 Ossetic         RAESIJYN
  158 78 Baluchi         SIAGH, SITHA
b                      002
  158 30 Swedish Up      SVALLA, SVULLNA
  158 31 Swedish VL      SVAL
  158 24 German ST       SCHWELLEN
  158 33 Danish          SVULME
  158 32 Swedish List    SVALLA  UPP, UT , POSA
  158 25 Penn. Dutch     SCHWELLE UF
  158 28 Flemish         OPZWELLEN
  158 26 Dutch List      ZWELLEN
  158 27 Afrikaans       OPSWEL, SWEL
  158 37 English ST      TO SWELL
b                      003
  158 91 SLOVENIAN P     NABUHNITI SE
  158 92 SERBOCROATIAN P NABUHNUTI
b                      004
  158 65 Khaskura        SUNINU
  158 64 Nepali List     SUJNU, SUNINU
  158 61 Lahnda          SUJJEN
  158 59 Gujarati        SUJWU
  158 58 Marathi         PHUGNE., SUJNE.
  158 55 Gypsy Gk        SUVLI  AV
b                      005
  158 63 Bengali         PHOLA
  158 62 Hindi           PHULNA
  158 60 Panjabi ST      PHULLENA
b                      006
  158 35 Icelandic ST    BOLGNA
  158 29 Frisian         FORBOLGEN
  158 36 Faroese         TRUTNA, BOLGNA
b                      007
  158 07 Breton ST       C'HWEZHAN, KOENVIN
  158 06 Breton SE       HUEHEIN, FOEUEIN
  158 05 Breton List     C'HOUEZA, STAMBOUC'HA, PENBOUFI
  158 04 Welsh C         CHWYDDO
  158 03 Welsh N         CHWYDDO
b                      008
  158 01 Irish A         AT
  158 02 Irish B         ATAIM
b                      009
  158 74 Afghan          PARSEDEL
  158 75 Waziri          PARSEDEL
b                      010
  158 82 Albanian G      AJEM
  158 95 ALBANIAN        AJEM
b                      011
  158 80 Albanian T      ME U FRYRE
  158 83 Albanian K      FRIXEM
b                      100
  158 71 Armenian Mod    URC`EL, UREL
  158 72 Armenian List   SURIL
b                      101
  158 79 Wakhi           PEDEMES-
  158 77 Tadzik          VARAM KARDAN, OMOSIDAN
b                      102
  158 81 Albanian Top    ENTEM, AOR. UENTA
  158 84 Albanian C      EXET (3 SG.)
b                      103
  158 41 Latvian         PAMPT, TUKT
  158 42 Slovenian       ZETEKLU
  158 54 Serbocroatian   OTECI
b                      200
c                         200  2  201
  158 70 Greek K         PRIDZOMAI
  158 67 Greek MD        PREDZOMAI
b                      201
c                         200  2  201
c                         201  2  202
  158 69 Greek D         PRIDZOMAI, FOUSKONO
b                      202
c                         201  2  202
  158 68 Greek Mod       FUSKONO
  158 66 Greek ML        FOUSKONO
b                      203
c                         203  2  204
  158 86 UKRAINIAN P     PUCHNUTY
  158 89 SLOVAK P        PUCHNUT
  158 46 Slovak          PUCHNUT
  158 85 RUSSIAN P       PUCHNUT
  158 51 Russian         PUXNUT
  158 88 POLISH P        PUCHNAC
  158 50 Polish          PUCHNAC
  158 44 Lusatian U      ZAPUCHAC
  158 43 Lusatian L      SPUCHAS SE
  158 90 CZECH P         PUCHNOUTI
  158 45 Czech           OPUCHNOUTI
  158 87 BYELORUSSIAN P  PUCHNUC
  158 40 Lithuanian ST   PUSTI
  158 39 Lithuanian O    ISSIPUSTI, PASIPUSTI
  158 47 Czech E         SPUXNUT
  158 49 Byelorussian    PUXNUC'
b                      204
c                         203  2  204
c                         204  2  205
  158 48 Ukrainian       PUXNUTY, NADUVATYS'
b                      205
c                         204  2  205
  158 93 MACEDONIAN P    NADUVAM SE
  158 94 BULGARIAN P     NADUVAM SE
b                      206
c                         206  2  207
  158 22 Brazilian       INCHAR
  158 20 Spanish         HINCHAR
b                      207
c                         206  2  207
c                         207  2  208
  158 21 Portuguese ST   INCHAR, INTUMECER
b                      208
c                         207  2  208
c                         208  2  209
  158 23 Catalan         INFLAR, ENTUMIR
b                      209
c                         208  2  209
  158 18 Sardinian L     UNFIARE
  158 17 Sardinian N     UFFRARE
  158 15 French Creole C AFLE
  158 08 Rumanian List   A (SE) UMFLA
  158 11 Ladin           IFFLER, SCUFFLER
  158 19 Sardinian C     UNFRAI
  158 10 Italian         GONFIARE
  158 12 Provencal       ENFLA, BOUFIGA, GOUNFLA
  158 14 Walloon         INFLER
  158 16 French Creole D AFLE
  158 13 French          ENFLER
  158 09 Vlach           SUFLU
a 159 TO SWIM
b                      001
  159 09 Vlach           KULIMBISESKU
  159 42 Slovenian       JE SOV SE KAPAT
  159 55 Gypsy Gk        NAYAV
  159 56 Singhalese      PINANAWA
  159 58 Marathi         POHNE.
  159 63 Bengali         SATAR KATA
  159 23 Catalan         SURAR
  159 41 Latvian         PELDETIES
  159 78 Baluchi         TARAGH, TARATHA, THAHARAGH, THAHARTHA
  159 79 Wakhi           USINAWERI TSER, QELOC XUS-, WEZAN DI-
b                      002
  159 30 Swedish Up      SIMMA
  159 31 Swedish VL      SAM  SEM
  159 24 German ST       SCHWIMMEN
  159 35 Icelandic ST    SYNDA
  159 33 Danish          SVOMME
  159 32 Swedish List    SIMMA
  159 34 Riksmal         SVOMME
  159 36 Faroese         SVIMJA
  159 29 Frisian         SWIMME
  159 28 Flemish         ZWEMMEN
  159 25 Penn. Dutch     SCHWIMM
  159 27 Afrikaans       SWEM
  159 26 Dutch List      ZWEMMEN
  159 38 Takitaki        SWEM
  159 37 English ST      TO SWIM
b                      003
  159 91 SLOVENIAN P     PLAVATI
  159 86 UKRAINIAN P     PLAVATY
  159 45 Czech           PLAVATI
  159 90 CZECH P         PLAVATI
  159 43 Lusatian L      PLUWAS
  159 44 Lusatian U      PLUWAC
  159 93 MACEDONIAN P    PLIVAM
  159 50 Polish          PLYNAC
  159 88 POLISH P        PLYWAC
  159 51 Russian         PLYT
  159 85 RUSSIAN P       PLAVAT
  159 54 Serbocroatian   PLIVATI
  159 92 SERBOCROATIAN P PLIVATI
  159 46 Slovak          PLAVAT
  159 89 SLOVAK P        PLAVAT
  159 87 BYELORUSSIAN P  PLAVAC
  159 94 BULGARIAN P     PLAVAM
  159 39 Lithuanian O    PLAUKTI
  159 40 Lithuanian ST   PLAUKTI
  159 52 Macedonian      PLIVA
  159 47 Czech E         PLOVAT
  159 49 Byelorussian    PLAVAC'
  159 48 Ukrainian       PLYVTY, PLAVATY
  159 53 Bulgarian       DA PLURA
b                      004
  159 61 Lahnda          TAEREN
  159 59 Gujarati        TERWU
  159 62 Hindi           TERNA
  159 60 Panjabi ST      TERNA
b                      005
  159 77 Tadzik          SINO KARDAN
  159 76 Persian List    SHENA KARDAN
b                      006
  159 68 Greek Mod       KOLIMBO
  159 66 Greek ML        KOLUMPO
  159 70 Greek K         KOLUMBO
  159 67 Greek MD        KOLUMPO
  159 69 Greek D         KOLUMPAO
b                      007
  159 15 French Creole C NAZE
  159 14 Walloon         NOYI
  159 13 French          NAGER
  159 16 French Creole D NEZE
b                      008
  159 01 Irish A         SNAMH
  159 02 Irish B         SNAMH DO DHEANAMH
  159 03 Welsh N         NOFIO
  159 04 Welsh C         NOFIO
  159 05 Breton List     NEUNVIER, NEUI, NEUNVIAL, NEUIAL
  159 06 Breton SE       NEANNEIN
  159 07 Breton ST       NEUIN, NEUNVIAL
  159 18 Sardinian L     NADARE
  159 17 Sardinian N     ANATARE
  159 08 Rumanian List   A INOTA
  159 11 Ladin           NUDER
  159 19 Sardinian C     NARAI
  159 10 Italian         NUOTARE
  159 20 Spanish         NADAR
  159 84 Albanian C      NATAR
  159 21 Portuguese ST   NADAR
  159 22 Brazilian       NADAR
  159 12 Provencal       NADA
b                      009
  159 81 Albanian Top    BEN MNOTE, AOR. BERA MNOTE
  159 80 Albanian T      ME NOTUAR
  159 83 Albanian K      LUAN NOT
  159 82 Albanian G      NOTI ME BA
  159 95 ALBANIAN        BAJ NOT
b                      010
  159 65 Khaskura        PAURNU
  159 64 Nepali List     PAURANU
b                      011
  159 74 Afghan          LAMBO VAHEL
  159 75 Waziri          LAMBEYA (SWIMMING)
b                      012
  159 71 Armenian Mod    LOLAL
  159 72 Armenian List   LOGHAL
b                      100
  159 73 Ossetic         LENK KAENYN
  159 57 Kashmiri        TSATH, LAYUNU
a 160 TAIL
b                      000
  160 35 Icelandic ST
b                      001
  160 79 Wakhi           KICIKAM
  160 63 Bengali         LEJ
  160 57 Kashmiri        LOTU
  160 55 Gypsy Gk        PORIN
  160 58 Marathi         SEPTI
  160 56 Singhalese      VALIGAYA
b                      002
  160 24 German ST       SCHWANZ
  160 25 Penn. Dutch     SCHWONNSZ
b                      003
  160 44 Lusatian U      WOPUS
  160 93 MACEDONIAN P    OPASKA
  160 94 BULGARIAN P     OPASKA
  160 52 Macedonian      OPASKA
  160 53 Bulgarian       OPASKA
b                      004
  160 34 Riksmal         HALE
  160 33 Danish          HALE
  160 36 Faroese         HALI
b                      005
  160 73 Ossetic         DYMAEG
  160 78 Baluchi         DUMB
  160 77 Tadzik          DUM
  160 76 Persian List    DOM
b                      006
  160 61 Lahnda          PUCH
  160 64 Nepali List     PUCHAR
  160 59 Gujarati        PUCHRI
  160 62 Hindi           PUCH
  160 60 Panjabi ST      PUCH
  160 65 Khaskura        PUCHHAR
b                      007
  160 91 SLOVENIAN P     HVOST
  160 86 UKRAINIAN P     CHVIST
  160 46 Slovak          CHVOST
  160 89 SLOVAK P        CHVOST
  160 51 Russian         XVOST
  160 85 RUSSIAN P       CHVOST
  160 90 CZECH P         CHVOST
  160 87 BYELORUSSIAN P  CHVOST
  160 41 Latvian         ASTE
  160 40 Lithuanian ST   UODEGA
  160 39 Lithuanian O    VUODEGA
  160 49 Byelorussian    XVOST
  160 48 Ukrainian       XVIST
b                      008
  160 42 Slovenian       RIPP
  160 92 SERBOCROATIAN P REP
  160 54 Serbocroatian   REP
b                      009
  160 43 Lusatian L      HOGON
  160 50 Polish          OGON
  160 88 POLISH P        OGON
b                      010
  160 74 Afghan          LAKEJ
  160 75 Waziri          LAKAI
b                      011
  160 38 Takitaki        TERE
  160 37 English ST      TAIL
b                      012
  160 04 Welsh C         CWT, CYNFFON
  160 03 Welsh N         CYNFFON, CWT
b                      013
  160 01 Irish A         EARBALL
  160 02 Irish B         EARBALL
  160 68 Greek Mod       URA
  160 66 Greek ML        OURA
  160 70 Greek K         OURA
  160 67 Greek MD        OURA
  160 69 Greek D         OURA
b                      014
  160 07 Breton ST       LOST
  160 06 Breton SE       LOST
  160 05 Breton List     LOST
b                      015
  160 15 French Creole C LACE
  160 16 French Creole D LACE
b                      016
  160 45 Czech           OCAS
  160 47 Czech E         OCAS
b                      017
  160 81 Albanian Top    BIST
  160 80 Albanian T      BISHT
  160 83 Albanian K      BIST
  160 84 Albanian C      BIST
  160 82 Albanian G      BISHTI
  160 95 ALBANIAN        BISHTI
b                      018
  160 72 Armenian List   BOCH
  160 71 Armenian Mod    POC`
b                      200
c                         200  2  201
  160 31 Swedish VL       ROMPA
b                      201
c                         200  2  201
c                         201  2  202
  160 30 Swedish Up      RUMPA, STJART
b                      202
c                         201  2  202
  160 32 Swedish List    STJART
  160 29 Frisian         STIRT
  160 28 Flemish         STEERT
  160 26 Dutch List      STAART
  160 27 Afrikaans       STERT
b                      203
c                         203  2  204
  160 09 Vlach           KWADE
  160 17 Sardinian N     KOA
  160 18 Sardinian L     COA
  160 13 French          QUEUE
  160 08 Rumanian List   COADA
  160 11 Ladin           CUA
  160 19 Sardinian C     KOA
  160 10 Italian         CODA
  160 23 Catalan         CUA, LLUFA
  160 14 Walloon         COWE
  160 12 Provencal       CO
b                      204
c                         203  2  204
c                         204  2  205
  160 20 Spanish         COLA, RABO
  160 22 Brazilian       RABO, CAUDA
b                      205
c                         204  2  205
  160 21 Portuguese ST   RABO
a 161 THAT
b                      001
  161 54 Serbocroatian   DA
  161 30 Swedish Up      ATT
  161 25 Penn. Dutch     ASZ
  161 55 Gypsy Gk        KODOVA
  161 59 Gujarati        PELU
b                      200
c                         200  2  201
c                         200  2  203
c                         200  2  208
  161 04 Welsh C         HWNNA
  161 03 Welsh N         HWNNW (MASC.), HONNO (FEM.), HYNNY (PLURAL)
  161 69 Greek D         HOTI
  161 70 Greek K         HOTI
  161 01 Irish A         SAN
  161 02 Irish B         UD, SIN, SUD
  161 07 Breton ST       AN...-SE
  161 06 Breton SE       EN...-SE
  161 05 Breton List     AN DRA-ZE, KEMENT-SE
  161 51 Russian         TOT
  161 86 UKRAINIAN P     TOJ
  161 88 POLISH P        TAMTEN
  161 50 Polish          TEN
  161 93 MACEDONIAN P    TOJ
  161 92 SERBOCROATIAN P TAJ
  161 85 RUSSIAN P       TOT
  161 46 Slovak          TEN, TA, TO
  161 87 BYELORUSSIAN P  TOJ
  161 40 Lithuanian ST   TAS
  161 39 Lithuanian O    TAS
  161 41 Latvian         TAS
  161 58 Marathi         TO
  161 65 Khaskura        TIO
  161 47 Czech E         TO
  161 48 Ukrainian       TOJ, TA, TE
  161 49 Byelorussian    HETY
  161 42 Slovenian       TISTO
  161 91 SLOVENIAN P     TISTI
  161 26 Dutch List      DIE, DAT, GENE
  161 24 German ST       DAS, JENE
  161 27 Afrikaans       DAT
  161 37 English ST      THAT
  161 38 Takitaki        DATI
  161 32 Swedish List    DENNE, DENNA, DETTA
  161 34 Riksmal         DEN, DET
  161 33 Danish          DEN, DET
  161 28 Flemish         DAT, DIE
  161 29 Frisian         DAT, DET
  161 36 Faroese         TANN, HIN
  161 31 Swedish VL      A DANA
  161 35 Icelandic ST    THESSI, THETTA
  161 81 Albanian Top    AY, AJO, ATA
  161 80 Albanian T      AJO
  161 83 Albanian K      AJ (M.), AJO (F.), ATA (N. +M. PL.)
  161 84 Albanian C      AJI (M.), (F.), ATA (M. PL. + N.)
  161 82 Albanian G      AI
  161 95 ALBANIAN        KJO, AI
  161 72 Armenian List   AYT
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  3  205
c                         201  3  206
c                         201  2  207
c                         201  2  208
c                         201  3  400
  161 45 Czech           TO, KTERY, ONEN
  161 52 Macedonian      TOJ/ONOJ
b                      202
c                         201  2  202
c                         202  2  207
c                         202  3  208
c                         202  3  400
  161 90 CZECH P         ONEN
  161 43 Lusatian L      WON
  161 44 Lusatian U      WON
  161 89 SLOVAK P        ONEN
  161 94 BULGARIAN P     ON A
  161 53 Bulgarian       ONOVA
  161 68 Greek Mod       EKINOS, AFTOS, PU, NA
  161 66 Greek ML        EKEINOS
  161 67 Greek MD        EKEINOS
  161 71 Armenian Mod    AYN
  161 76 Persian List    AN (UN)
b                      203
c                         200  2  203
c                         201  2  203
c                         203  2  204
c                         203  3  205
c                         203  3  206
c                         203  2  208
c                         203  3  400
  161 64 Nepali List     U, TYO
  161 63 Bengali         SETA, OTA
b                      204
c                         203  2  204
c                         204  3  205
c                         204  3  206
c                         204  3  208
c                         204  3  400
  161 61 Lahnda          O
  161 60 Panjabi ST      O
  161 62 Hindi           VOH
b                      205
c                         201  3  205
c                         203  3  205
c                         204  3  205
c                         205  2  206
c                         205  3  207
c                         205  3  208
c                         205  3  400
  161 75 Waziri          AGHA, HAGHA
b                      206
c                         201  3  206
c                         203  3  206
c                         204  3  206
c                         205  2  206
c                         206  3  207
  161 74 Afghan          HAGA, HUGA
b                      207
c                         201  2  207
c                         202  2  207
c                         205  3  207
c                         206  3  207
c                         207  3  208
c                         207  3  400
  161 77 Tadzik          ON, XAMON
b                      208
c                         200  2  208
c                         201  2  208
c                         202  3  208
c                         203  2  208
c                         204  3  208
c                         205  3  208
c                         207  3  208
c                         208  3  400
  161 57 Kashmiri        ATH, TIH
b                      400
c                         201  3  400
c                         202  3  400
c                         203  3  400
c                         204  3  400
c                         205  3  400
c                         207  3  400
c                         208  3  400
  161 56 Singhalese      AKA
  161 73 Ossetic         UCY
  161 78 Baluchi         AN
  161 79 Wakhi           YA
b                      209
c                         209  2  210
  161 10 Italian         QUEL
  161 20 Spanish         AQUEL
  161 22 Brazilian       AQUELE
  161 21 Portuguese ST   AQUELLE, AQUILLO
  161 09 Vlach           ACEL
  161 08 Rumanian List   ACEL(A), ACE(E)A
  161 19 Sardinian C     KUDDU
  161 17 Sardinian N     KUSSU
  161 18 Sardinian L     CUDDU
  161 13 French          CELA
  161 14 Walloon         COULA
  161 16 French Creole D SA
  161 15 French Creole C SA
b                      210
c                         209  2  210
c                         210  2  211
  161 11 Ladin           LESS, QUEL
  161 23 Catalan         ES, AQUEIX, EIX
b                      211
c                         210  2  211
  161 12 Provencal       AQUEST, ESTO
a 162 THERE
b                      001
  162 71 Armenian Mod    AYNTEL
  162 25 Penn. Dutch     ES
  162 72 Armenian List   HON
  162 17 Sardinian N     IN KUE
  162 38 Takitaki        JANDA, JANDASO
  162 55 Gypsy Gk        KOTE
  162 78 Baluchi         ODHA
b                      002
  162 74 Afghan          HALTA
  162 75 Waziri          WOLATA
b                      003
  162 19 Sardinian C     INNIA
  162 18 Sardinian L     INNI
b                      004
  162 68 Greek Mod       EKI
  162 66 Greek ML        EKEI
  162 70 Greek K         EKEI
  162 67 Greek MD        EKEI
  162 69 Greek D         EKEI
  162 36 Faroese         HAR
b                      100
  162 73 Ossetic         UM
  162 76 Persian List    UNJA
b                      101
  162 04 Welsh C         YNA
  162 03 Welsh N         YWO, ACW
b                      102
  162 77 Tadzik          DAR ON CO
  162 79 Wakhi           DRA, HUDRA, TRA, HUTRA, TRET, DRET
b                      200
c                         200  2  201
  162 13 French          LA
  162 15 French Creole C LA
  162 16 French Creole D LA
  162 14 Walloon         LA
  162 10 Italian         LA, COLA
  162 20 Spanish         ALLA
  162 22 Brazilian       AI, ALI, LA
  162 21 Portuguese ST   ALLI, ACOLA
  162 08 Rumanian List   ACOLO
  162 09 Vlach           AKLO
  162 12 Provencal       LA, CAI, SIAN
b                      201
c                         200  2  201
c                         201  2  202
  162 11 Ladin           ACQUI / ALLO, QUANDER / QUI
b                      202
c                         201  2  202
  162 23 Catalan         AQUI
b                      203
c                         203  2  204
c                         203  3  206
c                         203  3  208
c                         203  3  209
  162 48 Ukrainian       TAM, TUDY, OS', TUT
  162 41 Latvian         TUR
  162 37 English ST      THERE
  162 27 Afrikaans       DAAR
  162 26 Dutch List      DAAR, ALDAAR
  162 28 Flemish         DAER
  162 29 Frisian         DER, DERRE
  162 33 Danish          DER
  162 32 Swedish List    DAR, DARI, DARVIDLAG
  162 34 Riksmal         DER
  162 35 Icelandic ST    THAR(NA)
  162 24 German ST       DORT
  162 30 Swedish Up      DAR
  162 31 Swedish VL      DAR, DENA  DENAN
  162 49 Byelorussian    TAM
  162 47 Czech E         TAM
  162 94 BULGARIAN P     TAM
  162 87 BYELORUSSIAN P  TAM
  162 45 Czech           TAM
  162 90 CZECH P         TAM
  162 43 Lusatian L      TAM
  162 44 Lusatian U      TAM
  162 93 MACEDONIAN P    TAMU
  162 50 Polish          TAM
  162 88 POLISH P        TAM
  162 51 Russian         TAM
  162 85 RUSSIAN P       TAM
  162 54 Serbocroatian   TAMO
  162 92 SERBOCROATIAN P TAMO
  162 46 Slovak          TAM
  162 89 SLOVAK P        TAM
  162 42 Slovenian       TOM
  162 91 SLOVENIAN P     TAMO
  162 86 UKRAINIAN P     TAM
  162 52 Macedonian      TAMY
  162 53 Bulgarian       TAM
  162 81 Albanian Top    ATJE
  162 82 Albanian G      ATJE, ATY
  162 84 Albanian C      ATJE
  162 83 Albanian K      ATJE
  162 80 Albanian T      ATJE
  162 95 ALBANIAN        ATJE
  162 40 Lithuanian ST   TEN, TENAI
  162 39 Lithuanian O    TENAI
  162 59 Gujarati        TYA
  162 57 Kashmiri        TOR, TOTU
  162 58 Marathi         TITHE., TIKDE.
b                      204
c                         203  2  204
c                         204  2  205
c                         204  3  206
c                         204  3  207
c                         204  3  208
c                         204  3  209
  162 64 Nepali List     TYAHA, UTA
b                      205
c                         204  2  205
c                         205  3  206
c                         205  3  207
c                         205  3  208
c                         205  3  209
  162 63 Bengali         OKHANE
  162 61 Lahnda          UTTHA
  162 65 Khaskura        UTHA
  162 60 Panjabi ST      OTTHE
  162 62 Hindi           VEHA
b                      206
c                         203  3  206
c                         204  3  206
c                         205  3  206
c                         206  3  207
c                         206  3  208
  162 01 Irish A         ANNSAN
  162 02 Irish B         ANN SUD, ANN SAN, AG SIN
b                      207
c                         204  3  207
c                         205  3  207
c                         206  3  207
c                         207  2  208
  162 07 Breton ST       AZE
  162 06 Breton SE       AZE
b                      208
c                         203  3  208
c                         204  3  208
c                         205  3  208
c                         206  3  208
c                         207  2  208
  162 05 Breton List     AZE (CLOSE), AHONT (FAR)
b                      209
c                         203  3  209
c                         204  3  209
c                         205  3  209
  162 56 Singhalese      ETANA
a 163 THEY
b                      000
  163 23 Catalan
  163 77 Tadzik
b                      001
  163 27 Afrikaans       HULLE, HUL
  163 55 Gypsy Gk        KOLA
  163 73 Ossetic         UDON
  163 41 Latvian         VINI
  163 79 Wakhi           YUST, HAEIUST
b                      002
  163 16 French Creole D YO
  163 15 French Creole C YO
b                      003
  163 72 Armenian List   ANONK
  163 71 Armenian Mod    NRANK`
b                      200
c                         200  2  201
c                         200  2  203
  163 58 Marathi         TE, HE
  163 59 Gujarati        EO, TEO
  163 37 English ST      THEY
  163 38 Takitaki        DEM
  163 33 Danish          DE
  163 32 Swedish List    DE
  163 34 Riksmal         DE
  163 36 Faroese         TEIR
  163 35 Icelandic ST    THEIR
  163 30 Swedish Up      DE
  163 31 Swedish VL      DAM
  163 93 MACEDONIAN P    TIE
  163 94 BULGARIAN P     TE
  163 53 Bulgarian       TE
  163 68 Greek Mod       TUS (ACC.)
  163 24 German ST       SIE
  163 26 Dutch List      ZIJ
  163 25 Penn. Dutch     SIE
  163 28 Flemish         ZY
  163 29 Frisian         SE
  163 64 Nepali List     TI
  163 57 Kashmiri        TIM
  163 81 Albanian Top    ATA, ATO
  163 83 Albanian K      ATA
  163 80 Albanian T      ATA
  163 84 Albanian C      ATA
  163 82 Albanian G      ATA
  163 95 ALBANIAN        ATA
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  3  205
c                         201  3  206
  163 52 Macedonian      ONI/TIE
b                      202
c                         201  2  202
c                         202  3  205
c                         202  3  206
  163 48 Ukrainian       VONY
  163 49 Byelorussian    JANY
  163 47 Czech E         ONI
  163 45 Czech           ONI
  163 90 CZECH P         ONI
  163 43 Lusatian L      WONI
  163 44 Lusatian U      WONI
  163 50 Polish          ONI
  163 88 POLISH P        ONI
  163 51 Russian         ONI
  163 85 RUSSIAN P       ONI
  163 54 Serbocroatian   ONI
  163 92 SERBOCROATIAN P ONI
  163 46 Slovak          ONI, ONY
  163 89 SLOVAK P        ONI
  163 42 Slovenian       ONI
  163 91 SLOVENIAN P     ONI
  163 86 UKRAINIAN P     VONY
b                      203
c                         200  2  203
c                         201  2  203
c                         203  2  204
  163 67 Greek MD        AUTOI, TOUS
b                      204
c                         203  2  204
  163 66 Greek ML        AUTOI
  163 70 Greek K         AUTOI
  163 69 Greek D         AUTOI
b                      205
c                         201  3  205
c                         202  3  205
c                         205  3  206
  163 76 Persian List    ISHAN (UNA)
  163 78 Baluchi         ESHAN
b                      206
c                         201  3  206
c                         202  3  206
c                         205  3  206
  163 07 Breton ST       I, INT
  163 06 Breton SE       I, INT
  163 05 Breton List     I, INT
  163 40 Lithuanian ST   JIE, JOS
  163 39 Lithuanian O    JIE
  163 87 BYELORUSSIAN P  JANY
  163 04 Welsh C         HWY
  163 03 Welsh N         HWY
  163 01 Irish A         SIAD
  163 02 Irish B         IAD, IADSAN
  163 74 Afghan          DUJ, JE
  163 62 Hindi           VE, YE
b                      207
c                         207  2  208
  163 19 Sardinian C     ISSOS
  163 17 Sardinian N     ISSOS
  163 18 Sardinian L     IPSOS (M.PL.)
b                      208
c                         207  2  208
c                         208  2  209
  163 10 Italian         COLORO, EGLINO, ESSI
  163 09 Vlach           AESTI, ACELI (FEM)
b                      209
c                         208  2  209
  163 11 Ladin           ELS
  163 08 Rumanian List   EI, ELE
  163 13 French          ILS
  163 14 Walloon         I (BEFORE CONSONANT), IL (BEFORE VOWEL)
  163 12 Provencal       ELI
  163 20 Spanish         ELLOS
  163 22 Brazilian       ELES
  163 21 Portuguese ST   ELLES
b                      210
c                         210  3  211
  163 61 Lahnda          O
  163 60 Panjabi ST      O
  163 56 Singhalese      OVHU, OHU
  163 63 Bengali         ORA ORA
  163 65 Khaskura        UNIHARU
b                      211
c                         210  3  211
  163 75 Waziri          AGHA
a 164 THICK
b                      000
  164 55 Gypsy Gk
  164 11 Ladin
b                      001
  164 71 Armenian Mod    C`AL
  164 60 Panjabi ST      GARA
  164 75 Waziri          GHWUT
  164 72 Armenian List   HASD (T)
  164 76 Persian List    KOLOFT
  164 56 Singhalese      MAHATA
  164 74 Afghan          PEND, ZAXIM
  164 02 Irish B         RAMHAR
  164 78 Baluchi         THULAR
  164 73 Ossetic         YSTAVD
  164 77 Tadzik          WAFS, FARBEX
b                      002
  164 70 Greek K         PUKNOS
  164 69 Greek D         PUKNOS
b                      003
  164 40 Lithuanian ST   STORAS
  164 39 Lithuanian O    STORAS
b                      004
  164 81 Albanian Top    TRASE
  164 82 Albanian G      TRASH
  164 84 Albanian C      I-TRAS
  164 83 Albanian K      I TRAS
  164 80 Albanian T      I, E TRASHE
  164 95 ALBANIAN        TRASH
b                      005
  164 58 Marathi         JAD
  164 59 Gujarati        JARU
b                      006
  164 04 Welsh C         TRWCHUS
  164 03 Welsh N         TRWCHUS
b                      007
  164 54 Serbocroatian   DEBEO
  164 92 SERBOCROATIAN P DEBEO
  164 93 MACEDONIAN P    DEBEL
  164 53 Bulgarian       DEBELO
  164 94 BULGARIAN P     DEBEL
b                      200
c                         200  2  201
c                         200  3  203
  164 66 Greek ML        PACHUS
  164 41 Latvian         BIEZS
  164 79 Wakhi           BAJ
b                      201
c                         200  2  201
c                         201  2  202
c                         201  3  203
  164 67 Greek MD        PACHUS, CHONTROS
b                      202
c                         201  2  202
  164 68 Greek Mod       KHONDROS
b                      203
c                         200  3  203
c                         201  3  203
c                         203  2  204
c                         203  2  205
  164 65 Khaskura        MOTO, BAKLO, KHASRO
b                      204
c                         203  2  204
  164 57 Kashmiri        MOTU
  164 61 Lahnda          MOTA
  164 62 Hindi           MOTA
  164 63 Bengali         MOTA
b                      205
c                         203  2  205
  164 64 Nepali List     KHASRO
b                      206
c                         206  2  207
  164 48 Ukrainian       HRUBYJ
  164 50 Polish          GRUBY
b                      207
c                         206  2  207
c                         207  2  208
  164 46 Slovak          HRUBY, HUSTY
b                      208
c                         207  2  208
  164 42 Slovenian       GOSTO
  164 52 Macedonian      GUST
  164 45 Czech           HUSTY
b                      209
c                         209  2  210
  164 10 Italian         GROSSO
  164 19 Sardinian C     GRUSSU
  164 22 Brazilian       GROSSO
  164 21 Portuguese ST   GROSSO
  164 09 Vlach           GROS
  164 17 Sardinian N     GRUSSU
  164 18 Sardinian L     RUSSU
  164 08 Rumanian List   GROS
b                      210
c                         209  2  210
c                         210  2  211
  164 23 Catalan         GROS, GRUIXUT, ESPES
b                      211
c                         210  2  211
  164 13 French          EPAIS
  164 16 French Creole D EPE
  164 14 Walloon         SPES
  164 12 Provencal       ESPES, ESSO
  164 20 Spanish         ESPESO
  164 15 French Creole C EPE
b                      212
c                         212  2  213
  164 37 English ST      THICK
  164 24 German ST       DICK
  164 26 Dutch List      DIK
  164 25 Penn. Dutch     DICK
  164 28 Flemish         DIK
  164 38 Takitaki        DEKI, TEKI
  164 27 Afrikaans       DIK, DIG, TROEBEL, TROEWEL
  164 33 Danish          TYK
  164 32 Swedish List    TJOCK
  164 34 Riksmal         TYKK
  164 30 Swedish Up      TJOCK
  164 31 Swedish VL      TZAK  TZOK
  164 29 Frisian         TSJOK, TSJUK
  164 35 Icelandic ST    THYKKR, DIGR
  164 36 Faroese         TJUKKUR, DIGUR
  164 07 Breton ST       TEV
  164 06 Breton SE       TEU
  164 01 Irish A         TIUGH
b                      213
c                         212  2  213
c                         213  3  214
  164 05 Breton List     TEO, TEV, FETIS, TUZUM
b                      214
c                         213  3  214
  164 88 POLISH P        TLUSTY
  164 51 Russian         TOLSTYJ
  164 85 RUSSIAN P       TOLSTYJ
  164 87 BYELORUSSIAN P  TOUSTY
  164 49 Byelorussian    TAWSTY
  164 47 Czech E         TLUSTE
  164 91 SLOVENIAN P     TOLST
  164 86 UKRAINIAN P     TOUSTYJ
  164 89 SLOVAK P        TLSTY
  164 90 CZECH P         TLUSTY
  164 43 Lusatian L      TLUSTY
  164 44 Lusatian U      TOLSTY
a 165 THIN
b                      000
  165 86 UKRAINIAN P
  165 91 SLOVENIAN P
  165 89 SLOVAK P
  165 92 SERBOCROATIAN P
  165 85 RUSSIAN P
  165 88 POLISH P
  165 93 MACEDONIAN P
  165 44 Lusatian U
  165 43 Lusatian L
  165 90 CZECH P
  165 94 BULGARIAN P
  165 87 BYELORUSSIAN P
b                      001
  165 72 Armenian List   BARAK
  165 23 Catalan         FLACH, PRIM
  165 56 Singhalese      HINI
  165 55 Gypsy Gk        KISLO
  165 78 Baluchi         LAGHAR
  165 68 Greek Mod       LYANOS
  165 76 Persian List    NAZOK (BARIK)
  165 71 Armenian Mod    NOSR
  165 42 Slovenian       RETKO
  165 17 Sardinian N     ROMASU
  165 11 Ladin           STIGL
b                      002
  165 41 Latvian         TIEVS
  165 73 Ossetic         TAENAEG
  165 02 Irish B         CAOLUIGHIM, TANUIGHIM
  165 01 Irish A         TANAI
  165 03 Welsh N         TENAU
  165 04 Welsh C         TENAU
  165 05 Breton List     MOAN, TANO
  165 06 Breton SE       MOEN, TENAU
  165 07 Breton ST       MOAN, TANAV
  165 30 Swedish Up      TUNN
  165 31 Swedish VL      TON
  165 24 German ST       DUNN
  165 35 Icelandic ST    THUNNR, MJOR, GRANNR
  165 34 Riksmal         TYNN
  165 32 Swedish List    TUNN
  165 33 Danish          TYND
  165 36 Faroese         TUNNUR
  165 29 Frisian         TIN
  165 28 Flemish         DUN
  165 25 Penn. Dutch     DIN
  165 26 Dutch List      DUN
  165 27 Afrikaans       DUN
  165 38 Takitaki        FINI
  165 37 English ST      THIN
  165 14 Walloon         TENE, HATE, MWINDE
  165 46 Slovak          TENKY
  165 54 Serbocroatian   TANAK
  165 51 Russian         TONKIJ
  165 50 Polish          CIENKI
  165 45 Czech           TENKY
  165 57 Kashmiri        TONU, NYUKU
  165 52 Macedonian      TENOK/TANOK
  165 47 Czech E         TENKE
  165 49 Byelorussian    CENKI
  165 48 Ukrainian       TONKYJ, XUDYJ
  165 53 Bulgarian       TENKO
  165 77 Tadzik          TUNUK, BORIK
  165 79 Wakhi           BIRIK, SENOR, SENUF, TENUK, XEROB
b                      003
  165 18 Sardinian L     SUTTILE
  165 08 Rumanian List   SUBTIRE
  165 10 Italian         SOTTILE
b                      004
  165 20 Spanish         DELGADO
  165 21 Portuguese ST   DELGADO
  165 22 Brazilian       MAGRO, DELGADO
b                      005
  165 40 Lithuanian ST   PLONAS
  165 39 Lithuanian O    PLONAS
b                      006
  165 83 Albanian K      I XOU
  165 84 Albanian C      I-XOGH
  165 81 Albanian Top    HOLE
  165 80 Albanian T      I, E HOLLE
  165 82 Albanian G      HOLL, IMET
  165 95 ALBANIAN        HOLL
b                      007
  165 75 Waziri          NARAI
  165 74 Afghan          NARAJ
b                      008
  165 70 Greek K         ARAIOS
  165 69 Greek D         ARAIOS
b                      009
  165 67 Greek MD        PSILOS
  165 66 Greek ML        PSILOS
b                      200
c                         200  2  201
c                         200  2  202
c                         200  2  203
  165 64 Nepali List     PATALO, MASINU
b                      201
c                         200  2  201
c                         201  2  202
  165 65 Khaskura        DUBLO, MASINO
b                      202
c                         200  2  202
c                         201  2  202
c                         202  2  203
  165 62 Hindi           DUBLA, PETLA
  165 59 Gujarati        PATLU, DUBLU
b                      203
c                         200  2  203
c                         202  2  203
  165 60 Panjabi ST      PETLA
  165 58 Marathi         PATEL
  165 61 Lahnda          PETLA
  165 63 Bengali         PATLA, ROGA
b                      204
c                         204  3  205
c                         204  2  206
  165 12 Provencal       MINCE, INCO
  165 16 French Creole D MES
  165 13 French          MINCE
b                      205
c                         204  3  205
c                         205  3  206
  165 09 Vlach           MINUTU
b                      206
c                         204  2  206
c                         205  3  206
c                         206  2  207
  165 15 French Creole C MES, FIN (OBJECT), MEG (PERSON)
b                      207
c                         206  2  207
  165 19 Sardinian C     FINI
a 166 TO THINK
b                      000
  166 79 Wakhi
  166 75 Waziri
b                      001
  166 08 Rumanian List   A (SE) GINDI (LA)
  166 63 Bengali         BHABA
  166 64 Nepali List     CITAUNU, GUNNU
  166 55 Gypsy Gk        DWSINIRIM
  166 40 Lithuanian ST   GALVOTI, MASTYTI
  166 72 Armenian List   GHORIL
  166 56 Singhalese      HITANAWA
  166 81 Albanian Top    MEJTO(H)EM ( ), AOR. MEJTOVA
  166 39 Lithuanian O    MISLYTI
  166 71 Armenian Mod    MTACEL
  166 84 Albanian C      PINCAR
  166 05 Breton List     PREDERIA
  166 83 Albanian K      SKEPSEM
  166 09 Vlach           MISKIPSESKU
  166 58 Marathi         VATNE.
  166 73 Ossetic         X"UYDY KAENYN
  166 78 Baluchi         ZANAGH, ZANTHA
  166 57 Kashmiri        ZANUN
b                      002
  166 74 Afghan          FIKR KAVEL, GUMAN KAVEL
  166 77 Tadzik          FIKR KARDAN
  166 76 Persian List    FEKR KARDAN
b                      003
  166 30 Swedish Up      TANKA
  166 31 Swedish VL      TANGK
  166 24 German ST       DENKEN
  166 34 Riksmal         TENKE
  166 32 Swedish List    TANKA
  166 33 Danish          TAENKE
  166 29 Frisian         TINKE
  166 28 Flemish         DENKEN
  166 25 Penn. Dutch     DENK
  166 26 Dutch List      DENKEN
  166 27 Afrikaans       DINK
  166 38 Takitaki        DENKI
  166 37 English ST      TO THINK
b                      004
  166 04 Welsh C         MEDDWL
  166 03 Welsh N         MEDDWL, MYFYRIO
b                      005
  166 07 Breton ST       SONJAL, MEIZAN
  166 06 Breton SE       CHONJAL
b                      006
  166 36 Faroese         HUGSA
  166 35 Icelandic ST    HUGSA
b                      200
c                         200  2  201
  166 66 Greek ML        SKEBOMAI
  166 70 Greek K         SKEPTOMAI
  166 69 Greek D         SKEPTOMAI
b                      201
c                         200  2  201
c                         201  2  202
  166 68 Greek Mod       SKEFTOME, NOMIZO
b                      202
c                         201  2  202
  166 67 Greek MD        NOMIDZO
b                      203
c                         203  2  204
  166 80 Albanian T      ME U MENDUAR
b                      204
c                         203  2  204
c                         204  2  205
  166 82 Albanian G      KUJTOJ, MENDOJ
b                      205
c                         204  2  205
  166 95 ALBANIAN        KUJTOJ
b                      206
c                         206  2  207
  166 61 Lahnda          SOCAN
  166 62 Hindi           SOCNA
  166 60 Panjabi ST      SOCNA
b                      207
c                         206  2  207
c                         207  2  208
  166 65 Khaskura        BICHAR GARNU, SOCHNU
b                      208
c                         207  2  208
  166 59 Gujarati        VICARWU, VICAR KERWO
b                      209
c                         209  2  210
  166 51 Russian         DUMAT
  166 41 Latvian         DOMAT
  166 49 Byelorussian    DUMAC'
b                      210
c                         209  2  210
c                         210  2  211
  166 48 Ukrainian       MYSLYTY, DUMATY
b                      211
c                         210  2  211
c                         211  3  212
  166 53 Bulgarian       DA MISLI
  166 47 Czech E         MISLET
  166 52 Macedonian      MISLI
  166 86 UKRAINIAN P     MYSLYTY
  166 91 SLOVENIAN P     MISLITI
  166 42 Slovenian       ZAMISLIT
  166 89 SLOVAK P        MYSLIET
  166 46 Slovak          MYSLET
  166 92 SERBOCROATIAN P MISLITI
  166 54 Serbocroatian   MISLITI
  166 85 RUSSIAN P       MYSLIT
  166 88 POLISH P        MYSLEC
  166 50 Polish          MYSLEC
  166 93 MACEDONIAN P    MISLAM
  166 44 Lusatian U      MYSLIC
  166 43 Lusatian L      MYSLIS
  166 90 CZECH P         MYSLITI
  166 45 Czech           MYSLETI
  166 87 BYELORUSSIAN P  MYSLIC
  166 94 BULGARIAN P     MISL A
b                      212
c                         211  3  212
  166 01 Irish A         SMAOINEAMH
  166 02 Irish B         MEASAIM, SMUAINIM, SAOILIM, CUIMHNIGHIM
b                      213
c                         213  2  214
  166 15 French Creole C SOZE
  166 16 French Creole D SOZE
b                      214
c                         213  2  214
c                         214  2  215
  166 14 Walloon         PINSER, SONDJI
b                      215
c                         214  2  215
  166 12 Provencal       PENSA, CUJA
  166 22 Brazilian       PENSAR
  166 21 Portuguese ST   PENSAR
  166 13 French          PENSER
  166 20 Spanish         PENSAR
  166 23 Catalan         DONAR PIENSO
  166 10 Italian         PENSARE
  166 19 Sardinian C     PENSAI
  166 11 Ladin           S'IMPISSER, PENSER
  166 17 Sardinian N     PESSARE
  166 18 Sardinian L     PENSARE
a 167 THIS
b                      000
  167 73 Ossetic
b                      001
  167 63 Bengali         ETA
  167 55 Gypsy Gk        KOVA
  167 56 Singhalese      ME
b                      002
  167 07 Breton ST       AN...-MAN
  167 06 Breton SE       EN...-MEN
  167 05 Breton List     AN DRA-MAN, KEMENT-MAN
b                      003
  167 74 Afghan          DA, DAGA
  167 75 Waziri          DAI, DA, DAGHA
b                      200
c                         200  2  201
  167 39 Lithuanian O    SIS
  167 41 Latvian         SIS
  167 86 UKRAINIAN P     CEJ
  167 48 Ukrainian       CEJ, CJA, CE
  167 81 Albanian Top    KY, KJO
  167 82 Albanian G      KY
  167 84 Albanian C      KI (M.), KJO  KO (F.) XTA (M. PL. +N.)
  167 83 Albanian K      KII (M.), KIJO (F.), KETA (N. +M. PL.)
  167 80 Albanian T      KJO
  167 95 ALBANIAN        KY
  167 13 French          CECI
  167 15 French Creole C SA
  167 16 French Creole D SA
  167 12 Provencal       CO, ACO
  167 14 Walloon         COUCHAL
  167 71 Armenian Mod    AYS
  167 72 Armenian List   AYS
  167 36 Faroese         HETTA
  167 31 Swedish VL      A HANA
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  204
c                         201  2  205
c                         201  2  206
c                         201  2  208
c                         201  2  210
  167 30 Swedish Up      DEN HAR
  167 32 Swedish List    DEN HAR, DET
  167 40 Lithuanian ST   SIS, SITAS
b                      202
c                         201  2  202
c                         202  2  203
c                         202  2  205
c                         202  2  206
c                         202  2  208
c                         202  2  210
  167 68 Greek Mod       TUTOS, AFTOS
  167 67 Greek MD        AUTOS, TOUTOS
  167 70 Greek K         AUTO, TOUTO
b                      203
c                         202  2  203
  167 66 Greek ML        AUTOS
  167 69 Greek D         AUTO
b                      204
c                         201  2  204
c                         204  2  205
c                         204  2  206
c                         204  2  208
c                         204  2  210
c                         204  3  211
  167 20 Spanish         ESTE
  167 09 Vlach           AESTU
  167 23 Catalan         AQUEST, EST
  167 10 Italian         QUESTO
  167 17 Sardinian N     KUSTU
  167 18 Sardinian L     CUSTU
  167 19 Sardinian C     KUSTU
  167 11 Ladin           QUAIST, QUIST
  167 08 Rumanian List   ACEST(A)
  167 22 Brazilian       ESTE
  167 21 Portuguese ST   ESTE, ISTO
  167 58 Marathi         HA
  167 65 Khaskura        YO
  167 64 Nepali List     YO
  167 61 Lahnda          E
  167 60 Panjabi ST      E
  167 62 Hindi           YEH
  167 57 Kashmiri        ATH, YIH
  167 59 Gujarati        A
b                      205
c                         201  2  205
c                         202  2  205
c                         204  2  205
c                         205  2  206
c                         205  2  208
c                         205  2  210
  167 51 Russian         ETOT
  167 85 RUSSIAN P       ETOT
  167 49 Byelorussian    HETA
  167 87 BYELORUSSIAN P  HETY
  167 27 Afrikaans       DIE, DIT, NIERDIE
  167 29 Frisian         DY, DIT, DITTE
  167 33 Danish          DENNE, DETTE
  167 34 Riksmal         DENNE, DETTE
  167 25 Penn. Dutch     DAIIR (M.), DIE (F.), DES (N.)
  167 89 SLOVAK P        TEN
  167 90 CZECH P         TEN
  167 43 Lusatian L      TEN
  167 50 Polish          TEN
  167 88 POLISH P        TEN
  167 45 Czech           TO TENTO
  167 46 Slovak          TEN, TA, TO
  167 44 Lusatian U      TON
  167 47 Czech E         TOTO
  167 42 Slovenian       TU
  167 91 SLOVENIAN P     TA
  167 53 Bulgarian       TOVA
b                      206
c                         201  2  206
c                         202  2  206
c                         204  2  206
c                         205  2  206
c                         206  2  207
c                         206  2  208
c                         206  2  210
c                         206  3  211
c                         206  3  212
c                         206  3  213
  167 28 Flemish         DIT, DEZE
  167 35 Icelandic ST    THESSI, THETTA
  167 26 Dutch List      DEZE, DIT
  167 38 Takitaki        DISI, DI
  167 37 English ST      THIS
  167 24 German ST       DIESER
b                      207
c                         206  2  207
c                         207  3  211
c                         207  3  212
c                         207  3  213
  167 04 Welsh C         HWN
  167 03 Welsh N         HWN (MASC.), HON (FEM.), HYN (PL)
  167 01 Irish A         SO
  167 02 Irish B         SO, E SEO
b                      208
c                         201  2  208
c                         202  2  208
c                         204  2  208
c                         205  2  208
c                         206  2  208
c                         208  2  209
c                         208  2  210
  167 52 Macedonian      TOJ/OBOJ
b                      209
c                         208  2  209
  167 54 Serbocroatian   OVAJ
  167 92 SERBOCROATIAN P OVAJ
  167 93 MACEDONIAN P    OVOJ
b                      210
c                         201  2  210
c                         202  2  210
c                         204  2  210
c                         205  2  210
c                         206  2  210
c                         208  2  210
c                         210  3  211
  167 94 BULGARIAN P     TOJA
b                      211
c                         204  3  211
c                         206  3  211
c                         207  3  211
c                         210  3  211
c                         211  3  212
c                         211  3  213
  167 79 Wakhi           YEM, HAEIEM
b                      212
c                         206  3  212
c                         207  3  212
c                         211  3  212
c                         212  2  213
  167 78 Baluchi         HAM-ESH
b                      213
c                         206  3  213
c                         207  3  213
c                         211  3  213
c                         212  2  213
c                         213  2  214
  167 77 Tadzik          XAMIN
b                      214
c                         213  2  214
  167 76 Persian List    IN
a 168 THOU
b                      000
  168 42 Slovenian
  168 72 Armenian List
b                      001
  168 56 Singhalese      UMBA
b                      002
  168 37 English ST      THOU
  168 38 Takitaki        JOE
b                      003
  168 28 Flemish         U, GY
  168 26 Dutch List      GIJ, JE
  168 27 Afrikaans       U, JY
b                      004
  168 15 French Creole C U  W
  168 16 French Creole D U
b                      200
c                         200  3  201
  168 40 Lithuanian ST   TU
  168 39 Lithuanian O    TU
  168 41 Latvian         TU
  168 94 BULGARIAN P     TI
  168 87 BYELORUSSIAN P  TY
  168 45 Czech           TY
  168 90 CZECH P         TY
  168 43 Lusatian L      TY
  168 44 Lusatian U      TY
  168 93 MACEDONIAN P    TI
  168 50 Polish          TY
  168 88 POLISH P        TY
  168 51 Russian         TY
  168 85 RUSSIAN P       TY
  168 54 Serbocroatian   TI
  168 92 SERBOCROATIAN P TI
  168 46 Slovak          TY
  168 89 SLOVAK P        TY
  168 22 Brazilian       TU
  168 21 Portuguese ST   TU
  168 53 Bulgarian       TI
  168 48 Ukrainian       TY
  168 49 Byelorussian    TY
  168 47 Czech E         TI
  168 71 Armenian Mod    DU
  168 65 Khaskura        T
  168 60 Panjabi ST      TU
  168 62 Hindi           TU
  168 63 Bengali         TUMI
  168 58 Marathi         TU
  168 76 Persian List    TO
  168 95 ALBANIAN        TI
  168 59 Gujarati        TU
  168 52 Macedonian      TI
  168 77 Tadzik          TU
  168 82 Albanian G      TI
  168 84 Albanian C      TI
  168 83 Albanian K      TI
  168 80 Albanian T      TI
  168 25 Penn. Dutch     DU
  168 29 Frisian         DOU, DU
  168 36 Faroese         TU
  168 33 Danish          DU
  168 32 Swedish List    DU
  168 34 Riksmal         DU
  168 35 Icelandic ST    THU
  168 24 German ST       DU
  168 07 Breton ST       TE
  168 06 Breton SE       TE
  168 05 Breton List     TE
  168 04 Welsh C         TI
  168 03 Welsh N         TI
  168 01 Irish A         TU
  168 02 Irish B         TU, TUSA
  168 13 French          TU
  168 14 Walloon         TI
  168 12 Provencal       TU, TE
  168 20 Spanish         TU
  168 23 Catalan         TEU, TON, TA
  168 10 Italian         TU
  168 19 Sardinian C     TUI
  168 11 Ladin           TU
  168 08 Rumanian List   TU
  168 74 Afghan          TE
  168 78 Baluchi         THAU
  168 79 Wakhi           TU
  168 61 Lahnda          TU
  168 64 Nepali List     TA, TIMI
  168 75 Waziri          TE
  168 66 Greek ML        ESU
  168 68 Greek Mod       ESI
  168 70 Greek K         ESU, SO
  168 67 Greek MD        ESU, SE
  168 69 Greek D         ESU, SU
  168 91 SLOVENIAN P     TI
  168 86 UKRAINIAN P     TY
  168 73 Ossetic         DY
  168 17 Sardinian N     TUE
  168 18 Sardinian L     TUE
  168 81 Albanian Top    TI
  168 09 Vlach           TINE
  168 55 Gypsy Gk        TU
  168 30 Swedish Up      DU
  168 31 Swedish VL      DU
b                      201
c                         200  3  201
  168 57 Kashmiri        TSAH
a 169 THREE
b                      002
  169 71 Armenian Mod    EREK`
  169 72 Armenian List   YEREK
  169 30 Swedish Up      TRE
  169 31 Swedish VL      TRI
  169 02 Irish B         TRI
  169 01 Irish A         TRI
  169 03 Welsh N         TRI
  169 04 Welsh C         TRI
  169 05 Breton List     TRI (M), TEIR (F)
  169 06 Breton SE       TRI
  169 07 Breton ST       TRI
  169 24 German ST       DREI
  169 35 Icelandic ST    THRIR
  169 34 Riksmal         TRE
  169 32 Swedish List    TRE
  169 33 Danish          TRE
  169 36 Faroese         TRIGGIR
  169 29 Frisian         TRIJE
  169 28 Flemish         DRIE
  169 25 Penn. Dutch     DREI
  169 26 Dutch List      DRIE
  169 27 Afrikaans       DRIE
  169 38 Takitaki        DRI
  169 37 English ST      THREE
  169 17 Sardinian N     TRES
  169 18 Sardinian L     TRES
  169 15 French Creole C THWA
  169 69 Greek D         TREIS, TRIA
  169 67 Greek MD        TRIA
  169 70 Greek K         TREIS, TRIA
  169 66 Greek ML        TRIA
  169 68 Greek Mod       TRIA
  169 40 Lithuanian ST   TRYS
  169 39 Lithuanian O    TRYS
  169 41 Latvian         TRIS
  169 08 Rumanian List   TREI
  169 11 Ladin           TRAIS
  169 19 Sardinian C     TRESI
  169 10 Italian         TRE
  169 23 Catalan         TRES
  169 20 Spanish         TRES
  169 12 Provencal       TRES
  169 14 Walloon         TREUS
  169 21 Portuguese ST   TRES
  169 22 Brazilian       TRES
  169 13 French          TROIS
  169 16 French Creole D TWA
  169 86 UKRAINIAN P     TRY
  169 91 SLOVENIAN P     TRI
  169 42 Slovenian       TRI
  169 89 SLOVAK P        TRI
  169 46 Slovak          TRI
  169 92 SERBOCROATIAN P TRI
  169 54 Serbocroatian   TRI
  169 85 RUSSIAN P       TRI
  169 51 Russian         TRI
  169 88 POLISH P        TRZY
  169 50 Polish          TRZY
  169 93 MACEDONIAN P    TRI
  169 44 Lusatian U      TRI
  169 43 Lusatian L      TSI
  169 90 CZECH P         TRI
  169 45 Czech           TRI
  169 87 BYELORUSSIAN P  TRY
  169 94 BULGARIAN P     TRI
  169 52 Macedonian      TRI
  169 47 Czech E         TRI
  169 49 Byelorussian    TRY
  169 48 Ukrainian       TRY
  169 53 Bulgarian       TRI
  169 55 Gypsy Gk        TRIN
  169 81 Albanian Top    TRI (GRA)
  169 09 Vlach           TRE
  169 57 Kashmiri        TREH
  169 61 Lahnda          TRAE
  169 79 Wakhi           TROI
  169 74 Afghan          DRE
  169 80 Albanian T      TRE, TRI
  169 83 Albanian K      TRE (M.), TRII (F.)
  169 84 Albanian C      TRI
  169 82 Albanian G      TRE
  169 95 ALBANIAN        TRE
  169 59 Gujarati        TRAN
  169 75 Waziri          DRE
  169 56 Singhalese      TUNA
  169 64 Nepali List     TIN
  169 58 Marathi         TIN
  169 63 Bengali         TIN
  169 62 Hindi           TIN
  169 60 Panjabi ST      TINN
  169 65 Khaskura        TIN
  169 78 Baluchi         SAI
  169 77 Tadzik          SE
  169 76 Persian List    SE
  169 73 Ossetic         AERTAE
a 170 TO THROW
b                      001
  170 73 Ossetic         AEPPARYN
  170 54 Serbocroatian   BACITI
  170 51 Russian         BROSAT
  170 01 Irish A         CAITHEAMH
  170 53 Bulgarian       DA XVERLJA
  170 09 Vlach           ERUK
  170 81 Albanian Top    ETH, AOR. ODHA
  170 38 Takitaki        FRINGI
  170 71 Armenian Mod    GC`EL
  170 79 Wakhi           KUT-
  170 80 Albanian T      ME HEDHUR
  170 59 Gujarati        NAKHWU
  170 72 Armenian List   NEDEL
  170 78 Baluchi         PHIRENAGH, PHIRENTHA
  170 50 Polish          RZUCAC
  170 02 Irish B         TEILGIM
  170 57 Kashmiri        TSHUNUN
  170 56 Singhalese      VISI/KARAWA
b                      002
  170 30 Swedish Up      KASTA, SLUNGA
  170 31 Swedish VL      KAST, SMOR
  170 36 Faroese         KASTA
  170 33 Danish          KASTE
  170 32 Swedish List    KASTA, SLANGA
  170 34 Riksmal         KASTE
  170 35 Icelandic ST    KASTA
b                      003
  170 61 Lahnda          SUTTEN
  170 60 Panjabi ST      SUTTENA
b                      004
  170 03 Welsh N         TAFLU
  170 04 Welsh C         TAFLU
  170 06 Breton SE       TAULEIN
  170 07 Breton ST       TEUREL
  170 05 Breton List     TEUREL, STLEPEL, STLAPA
b                      005
  170 55 Gypsy Gk        CHAV
  170 74 Afghan          ACAVEL, GURZAVEL
  170 75 Waziri          ACHAWEL, WOCHAWEL, TREYEL
b                      006
  170 77 Tadzik          PARTOFTAN, ANDOXTAN
  170 76 Persian List    ANDAKHTAN
b                      007
  170 62 Hindi           PHEKNA
  170 58 Marathi         PHEKNE
b                      008
  170 64 Nepali List     APHALNU, HALNU
  170 63 Bengali         PHELA
  170 65 Khaskura        PHALNU
b                      009
  170 46 Slovak          DODIT , HADZAT
  170 45 Czech           HAZETI
  170 47 Czech E         HODYIT
b                      010
  170 83 Albanian K      STIE (AOR. STIVA, PPLE. STIIRE )
  170 84 Albanian C      STIE
  170 82 Albanian G      SHTI J
  170 95 ALBANIAN        SHTI
b                      011
  170 93 MACEDONIAN P    FRLAM
  170 52 Macedonian      FRLA
b                      200
c                         200  2  201
c                         200  2  202
  170 08 Rumanian List   LANSA, A ARUNCA, A AZVIRLI
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
  170 23 Catalan         LLANSAR, ETJEGAR, TIRAR, DISPARAR, DECANTARSE
b                      202
c                         200  2  202
c                         201  2  202
c                         202  2  203
  170 21 Portuguese ST   LANCAR, ATIRAR, BOTAR, DIETAR
b                      203
c                         201  2  203
c                         202  2  203
c                         203  2  204
  170 22 Brazilian       ATIRAR, BOTAR
b                      204
c                         203  2  204
  170 11 Ladin           BUTTER, PATTER
b                      205
c                         205  2  206
  170 13 French          JETER
  170 18 Sardinian L     BETTARE
  170 17 Sardinian N     GETTARE
  170 19 Sardinian C     GETTAI
  170 10 Italian         GETTARE
  170 14 Walloon         DJETER, HINER
  170 20 Spanish         ECHAR
  170 12 Provencal       JITA, TRAIRE, BANDI
b                      206
c                         205  2  206
c                         206  2  207
  170 15 French Creole C VOYE (AT), ZETE (AWAY)
b                      207
c                         206  2  207
  170 16 French Creole D VOYE
b                      208
c                         208  2  209
  170 91 SLOVENIAN P     METATI
  170 86 UKRAINIAN P     METATY
  170 89 SLOVAK P        METAT
  170 92 SERBOCROATIAN P METATI
  170 85 RUSSIAN P       METAT
  170 88 POLISH P        MIOTAC
  170 43 Lusatian L      MJATAS
  170 44 Lusatian U      MJETAC
  170 90 CZECH P         METATI
  170 40 Lithuanian ST   MESTI
  170 39 Lithuanian O    MESTI
  170 41 Latvian         MEST, SVIEST
  170 94 BULGARIAN P     M ATAM
b                      209
c                         208  2  209
c                         209  2  210
  170 48 Ukrainian       KYDATY, METATY
b                      210
c                         209  2  210
  170 49 Byelorussian    KIDAC'
  170 87 BYELORUSSIAN P  KIDAC
b                      211
c                         211  2  212
  170 37 English ST      TO THROW
b                      212
c                         211  2  212
c                         212  2  213
  170 29 Frisian         DROAIJE, WERPE
b                      213
c                         212  2  213
c                         213  2  214
  170 28 Flemish         WERPEN
  170 24 German ST       WERFEN
  170 70 Greek K         RIPTO
  170 68 Greek Mod       RIKHNO
  170 66 Greek ML        HRICHNO
  170 67 Greek MD        RICHNO
  170 69 Greek D         RICHNO
  170 42 Slovenian       VRZI
b                      214
c                         213  2  214
c                         214  2  215
  170 26 Dutch List      WERPEN, SMIJTEN
b                      215
c                         214  2  215
  170 25 Penn. Dutch     SCHMEISS
  170 27 Afrikaans       GOOI, SMYT
a 171 TO TIE
b                      001
  171 19 Sardinian C     AKKAPPIAI
  171 29 Frisian         FLEUGELJE, STRUSE
  171 65 Khaskura        KASNU
  171 41 Latvian         SIET
  171 07 Breton ST       SKOULMAN
  171 05 Breton List     STAGA, EREN, KEVREA, LIAMMA
b                      002
  171 86 UKRAINIAN P     V AZATY
  171 91 SLOVENIAN P     VEZATI
  171 42 Slovenian       ZVEZI
  171 89 SLOVAK P        VIAZAT
  171 46 Slovak          VIAZAT , SPUTAT
  171 92 SERBOCROATIAN P VEZATI
  171 54 Serbocroatian   VEZATI
  171 85 RUSSIAN P       V AZAT
  171 51 Russian         VJAZAT
  171 88 POLISH P        WIAZAC
  171 50 Polish          WIAZAC
  171 44 Lusatian U      WJAZAC
  171 43 Lusatian L      WEZAS
  171 90 CZECH P         VAZATI
  171 45 Czech           VAZATI, SVAZOVATI
  171 87 BYELORUSSIAN P  V AZAC
  171 47 Czech E         ZVAZAT
  171 49 Byelorussian    VJAZAC'
  171 48 Ukrainian       ZV'JAZUVATY
b                      003
  171 93 MACEDONIAN P    VRZAM
  171 94 BULGARIAN P     VURZVAM
  171 52 Macedonian      VRZE/POVIE
  171 53 Bulgarian       DA VREZVA
  171 40 Lithuanian ST   RISTI
  171 39 Lithuanian O    RISTI
b                      004
  171 01 Irish A         CEANGAL
  171 02 Irish B         DO CHEANGAL
b                      005
  171 06 Breton SE       KLOMMEIN
  171 04 Welsh C         CLYMU
  171 03 Welsh N         CLYMU
b                      006
  171 74 Afghan          TAREL
  171 75 Waziri          TAREL
b                      007
  171 38 Takitaki        TAI
  171 37 English ST      TO TIE
b                      008
  171 71 Armenian Mod    PAT`AT`EL, KAPEL
  171 72 Armenian List   GABEL
b                      009
  171 68 Greek Mod       DHENO
  171 66 Greek ML        DENO
  171 70 Greek K         PROSDENO
  171 67 Greek MD        DENO
  171 69 Greek D         DENO
b                      010
  171 16 French Creole D MAWE
  171 15 French Creole C MAHWE
b                      200
c                         200  2  201
  171 09 Vlach           LEGU
  171 18 Sardinian L     LIGARE
  171 17 Sardinian N     LIGARE
  171 08 Rumanian List   A LEGA
  171 11 Ladin           LIER
  171 10 Italian         LEGARE
  171 23 Catalan         UNIR, JUNTAR, LLIGAR
  171 12 Provencal       LIA, LIGA
  171 14 Walloon         LOYI
  171 13 French          LIER
  171 22 Brazilian       LIGAR
  171 81 Albanian Top    LITH, AOR. LIDHA
  171 80 Albanian T      ME LIDHUR
  171 83 Albanian K      LIDHIN
  171 84 Albanian C      LITH (PRET. LIDHA)
  171 82 Albanian G      LIDH
  171 95 ALBANIAN        LIDH
b                      201
c                         200  2  201
c                         201  2  202
  171 21 Portuguese ST   ATAR, LIGAR
b                      202
c                         201  2  202
  171 20 Spanish         ATAR
b                      203
c                         203  2  204
  171 73 Ossetic         BAETTYN
  171 76 Persian List    BASTAN
  171 78 Baluchi         BANDAGH, BASTHA
  171 77 Tadzik          BASTAN, BOFTAN
  171 30 Swedish Up      BINDA, KNYTA
  171 31 Swedish VL      BIN, KNYT
  171 56 Singhalese      BANDINAWA
  171 61 Lahnda          BENNEN
  171 79 Wakhi           VUND
  171 24 German ST       BINDEN
  171 35 Icelandic ST    BINDA
  171 34 Riksmal         BINDE
  171 32 Swedish List    BINDA
  171 33 Danish          BINDE
  171 36 Faroese         BINDA
  171 28 Flemish         BINDEN
  171 25 Penn. Dutch     BINN
  171 26 Dutch List      BINDEN, KNOOPEN
  171 27 Afrikaans       VASMAAK, BIND(E), AANBIND(E)
  171 59 Gujarati        BAHDHWU
  171 58 Marathi         BANDHNE.
  171 63 Bengali         BADHA
  171 62 Hindi           BADHNA
  171 60 Panjabi ST      BENNENA
  171 55 Gypsy Gk        PHANDAV
b                      204
c                         203  2  204
c                         204  2  205
  171 64 Nepali List     GATHNU, BADHNU
b                      205
c                         204  2  205
  171 57 Kashmiri        GANDUN
a 172 TONGUE
b                      000
  172 73 Ossetic
b                      001
  172 41 Latvian         MELE
b                      002
  172 68 Greek Mod       GHLOSA
  172 66 Greek ML        GLOSSA
  172 70 Greek K         GLOSSA
  172 67 Greek MD        GLOSSA
  172 69 Greek D         GLOSSA
b                      200
c                         200  3  201
c                         200  3  202
c                         200  3  203
  172 30 Swedish Up      TUNGA
  172 31 Swedish VL      TONGA
  172 02 Irish B         TEANGA, -AN, -ANNA
  172 01 Irish A         TEANGA
  172 24 German ST       ZUNGE
  172 35 Icelandic ST    TUNGA
  172 34 Riksmal         TUNGE
  172 32 Swedish List    TUNGA
  172 33 Danish          TUNGE
  172 36 Faroese         TUNGA
  172 29 Frisian         BLAEIJER, TONGE
  172 28 Flemish         TONG
  172 25 Penn. Dutch     ZUUNG
  172 26 Dutch List      TONG
  172 27 Afrikaans       TONG
  172 38 Takitaki        TONGO
  172 37 English ST      TONGUE
  172 03 Welsh N         TAFOD
  172 04 Welsh C         TAFOD
  172 05 Breton List     TEOD
  172 06 Breton SE       TEAD
  172 07 Breton ST       TEOD
  172 09 Vlach           LIMBE
  172 17 Sardinian N     LIMBA
  172 18 Sardinian L     LIMBA
  172 15 French Creole C LAN
  172 08 Rumanian List   LIMBA
  172 11 Ladin           LAUNGIA
  172 19 Sardinian C     LINGUA
  172 10 Italian         LINGUA
  172 23 Catalan         LLENGUA
  172 20 Spanish         LENGUA
  172 12 Provencal       LENGO
  172 14 Walloon         LINWE
  172 16 French Creole D LAN
  172 13 French          LANGUE
  172 21 Portuguese ST   LINGUA
  172 22 Brazilian       LINGUA
  172 93 MACEDONIAN P    JAZIK
  172 50 Polish          JEZYK
  172 88 POLISH P        JEZYK
  172 51 Russian         JAZYK
  172 85 RUSSIAN P       JAZYK
  172 54 Serbocroatian   JEZIK
  172 92 SERBOCROATIAN P JEZIK
  172 46 Slovak          JAZYK
  172 89 SLOVAK P        JAZYK
  172 42 Slovenian       JEZIK
  172 91 SLOVENIAN P     JEZIK
  172 86 UKRAINIAN P     JAZYK
  172 44 Lusatian U      JAZYK
  172 43 Lusatian L      JEZYK
  172 90 CZECH P         JAZYK
  172 45 Czech           JAZYK
  172 87 BYELORUSSIAN P  JAZYK
  172 94 BULGARIAN P     EZIK
  172 52 Macedonian      JAZIK
  172 47 Czech E         JAZIK
  172 49 Byelorussian    JAZYK
  172 48 Ukrainian       JAZYK
  172 53 Bulgarian       EZIK
  172 39 Lithuanian O    LIEZUVIS
  172 40 Lithuanian ST   LIEZUVIS
  172 71 Armenian Mod    LEZU
  172 72 Armenian List   LEZOO
  172 55 Gypsy Gk        CHIP
  172 56 Singhalese      DIVA
  172 57 Kashmiri        ZEV
  172 64 Nepali List     JIBRO
  172 61 Lahnda          JIBH
  172 59 Gujarati        JIB
  172 58 Marathi         JIBH
  172 63 Bengali         JIB
  172 62 Hindi           JIBH
  172 60 Panjabi ST      JIB
  172 65 Khaskura        JIBRO
b                      201
c                         200  3  201
c                         201  3  202
c                         201  3  203
  172 81 Albanian Top    GUE
  172 80 Albanian T      GJUHE
  172 83 Albanian K      GLHUXE
  172 84 Albanian C      GLUX
  172 82 Albanian G      GJUHENA
  172 95 ALBANIAN        GJUHENA
b                      202
c                         200  3  202
c                         201  3  202
c                         202  3  203
  172 74 Afghan          ZEBA
  172 78 Baluchi         ZAWAN
  172 75 Waziri          ZHEBBA
  172 76 Persian List    ZABAN (ZABUN)
  172 77 Tadzik          ZABON
b                      203
c                         200  3  203
c                         201  3  203
c                         202  3  203
  172 79 Wakhi           ZIK
a 173 TOOTH (FRONT)
b                      001
  173 72 Armenian List   AGRA
  173 29 Frisian         TOSK
  173 25 Penn. Dutch     ZAW (FEDDERSCHT)
b                      002
  173 81 Albanian Top    DHEMP
  173 80 Albanian T      DHEMB
  173 83 Albanian K      DHEMP
  173 84 Albanian C      DHEMB
  173 82 Albanian G      DHAM B I (ALSO SPELLED DAM B I)
  173 95 ALBANIAN        DAM B I
  173 91 SLOVENIAN P     ZOB
  173 86 UKRAINIAN P     ZUB
  173 42 Slovenian       OD NAPREJ ZOBY
  173 92 SERBOCROATIAN P ZUB
  173 46 Slovak          ZUB
  173 89 SLOVAK P        ZUB
  173 87 BYELORUSSIAN P  ZUB
  173 45 Czech           ZUB
  173 90 CZECH P         ZUB
  173 43 Lusatian L      ZUB
  173 44 Lusatian U      ZUB
  173 93 MACEDONIAN P    ZAB
  173 50 Polish          ZAB
  173 88 POLISH P        ZAB
  173 51 Russian         ZUB
  173 85 RUSSIAN P       ZUB
  173 54 Serbocroatian   ZUB
  173 41 Latvian         ZOBS
  173 94 BULGARIAN P     ZUB
  173 52 Macedonian      ZAB, ZABI
  173 47 Czech E         ZUP
  173 49 Byelorussian    ZUB
  173 48 Ukrainian       ZUB
  173 53 Bulgarian       ZEB
b                      003
  173 70 Greek K         ODOUS
  173 71 Armenian Mod    ATAM
  173 30 Swedish Up      TAND, FRAMTAND
  173 31 Swedish VL      TAN, FRAMTAN
  173 24 German ST       ZAHN
  173 35 Icelandic ST    TONN
  173 34 Riksmal         TANN
  173 32 Swedish List    TAND
  173 33 Danish          TAND
  173 36 Faroese         TONN
  173 28 Flemish         TAND
  173 27 Afrikaans       TAND
  173 26 Dutch List      TAND
  173 55 Gypsy Gk        DANT
  173 17 Sardinian N     DENTE
  173 18 Sardinian L     DENTE
  173 15 French Creole C DA
  173 67 Greek MD        DONTI
  173 69 Greek D         DONTI
  173 40 Lithuanian ST   DANTIS
  173 39 Lithuanian O    DANTIS
  173 68 Greek Mod       DHONDI
  173 66 Greek ML        DONTI
  173 08 Rumanian List   DINTE, ZIMT
  173 11 Ladin           DAINT
  173 19 Sardinian C     DENTI
  173 10 Italian         DENTE
  173 23 Catalan         DENT
  173 20 Spanish         DIENTE
  173 12 Provencal       DENT
  173 14 Walloon         DINT
  173 16 French Creole D DA
  173 13 French          DENT
  173 03 Welsh N         DANT
  173 04 Welsh C         DANT
  173 05 Breton List     DANT
  173 06 Breton SE       DANT
  173 07 Breton ST       DANT
  173 21 Portuguese ST   DENTE
  173 22 Brazilian       DENTE
  173 38 Takitaki        TIFI
  173 37 English ST      TOOTH
  173 58 Marathi         DAT
  173 56 Singhalese      DATA
  173 57 Kashmiri        DAND
  173 64 Nepali List     DAT
  173 61 Lahnda          DEND
  173 78 Baluchi         DATHAN
  173 77 Tadzik          DANDON
  173 59 Gujarati        DAT
  173 76 Persian List    DANDAN
  173 65 Khaskura        DANT
  173 62 Hindi           DAT
  173 63 Bengali         DAT
  173 60 Panjabi ST      DEND
  173 09 Vlach           DINC
  173 79 Wakhi           DENDUK
  173 73 Ossetic         DAENDAG
b                      004
  173 74 Afghan          GAS
  173 75 Waziri          GHWOSH, GHOSH
b                      005
  173 02 Irish B         FIACAL
  173 01 Irish A         FIACAL
a 174 TREE
b                      001
  174 84 Albanian C      ARVUGHAM
  174 73 Ossetic         BAELAC
  174 11 Ladin           BOS
  174 83 Albanian K      DHENDRO
  174 41 Latvian         KOKS
  174 55 Gypsy Gk        KOPAC
  174 57 Kashmiri        KULU
  174 19 Sardinian C     MATTA
  174 81 Albanian Top    PEME
  174 62 Hindi           PER
  174 80 Albanian T      SHELG
  174 17 Sardinian N     UNNU
b                      002
  174 71 Armenian Mod    CAR
  174 72 Armenian List   SZAR
b                      003
  174 46 Slovak          STROM
  174 44 Lusatian U      STOM
  174 45 Czech           STROM
  174 90 CZECH P         STROM
  174 43 Lusatian L      STROM
  174 47 Czech E         STROM
b                      004
  174 24 German ST       BAUM
  174 29 Frisian         BOME
  174 28 Flemish         BOOM
  174 25 Penn. Dutch     BAWM
  174 26 Dutch List      BOOM
  174 27 Afrikaans       BOOM
  174 38 Takitaki        BOOM
b                      005
  174 04 Welsh C         COEDEN
  174 03 Welsh N         COEDEN
  174 01 Irish A         CRANN
  174 02 Irish B         CRANN
b                      006
  174 08 Rumanian List   ARBORE, POM
  174 10 Italian         ALBERO
  174 23 Catalan         ARBRE, ABRE
  174 20 Spanish         ARBOL
  174 12 Provencal       AUBRE
  174 14 Walloon         ABE
  174 13 French          ARBRE
  174 21 Portuguese ST   ARVORE
  174 22 Brazilian       ARVORE
  174 09 Vlach           ARBURI
  174 18 Sardinian L     ARBURE
b                      007
  174 58 Marathi         JHAD
  174 59 Gujarati        JHAR
b                      008
  174 15 French Creole C PYE BWA
  174 16 French Creole D PYE
b                      009
  174 07 Breton ST       GWEZENN
  174 06 Breton SE       GUEEN
  174 05 Breton List     GWEZ
b                      010
  174 40 Lithuanian ST   MEDIS
  174 39 Lithuanian O    MEDIS
b                      200
c                         200  2  201
  174 77 Tadzik          DARAXT, CUB
  174 76 Persian List    DERAKHT
  174 60 Panjabi ST      DEREKHET
  174 61 Lahnda          DREXT
  174 79 Wakhi           DERUXT
  174 78 Baluchi         DRASHK
b                      201
c                         200  2  201
c                         201  2  202
  174 74 Afghan          VENA, DIRAXT
b                      202
c                         201  2  202
  174 75 Waziri          WUNA
b                      203
c                         203  2  204
  174 65 Khaskura        RUKH, BOT
b                      204
c                         203  2  204
c                         204  2  205
  174 64 Nepali List     GACH, RUKH
b                      205
c                         204  2  205
  174 63 Bengali         GAC
  174 56 Singhalese      GASA
b                      206
c                         206  3  207
  174 86 UKRAINIAN P     DEREVO
  174 91 SLOVENIAN P     DREVO
  174 42 Slovenian       DREV
  174 89 SLOVAK P        DREVO
  174 92 SERBOCROATIAN P DRVO
  174 54 Serbocroatian   DRVO
  174 85 RUSSIAN P       DEREVO
  174 51 Russian         DEREVO
  174 88 POLISH P        DRZEWO
  174 50 Polish          DRZEWO
  174 93 MACEDONIAN P    DRVO
  174 87 BYELORUSSIAN P  DREVA
  174 94 BULGARIAN P     DURVO
  174 52 Macedonian      DRVO
  174 49 Byelorussian    DREVA
  174 48 Ukrainian       DEREVO
  174 53 Bulgarian       DERVO
  174 30 Swedish Up      TRA(D)
  174 31 Swedish VL      TRE  TRA
  174 35 Icelandic ST    TRE
  174 32 Swedish List    TRAD
  174 34 Riksmal         TRE
  174 33 Danish          TRAE
  174 36 Faroese         TRAE
  174 37 English ST      TREE
  174 82 Albanian G      DRUJA
  174 95 ALBANIAN        DRUJA, DRUNI
b                      207
c                         206  3  207
  174 68 Greek Mod       DHENDRO
  174 66 Greek ML        DENDRO
  174 70 Greek K         DENDRON
  174 67 Greek MD        DENTRO
  174 69 Greek D         DENTRO
a 175 TO TURN (VEER)
b                      000
  175 09 Vlach
  175 55 Gypsy Gk
  175 57 Kashmiri
  175 79 Wakhi
  175 78 Baluchi
b                      001
  175 01 Irish A         CASADH
  175 02 Irish B         COR
  175 19 Sardinian C     FURRIAI
  175 77 Tadzik          GARDONDAN, TOFTAN
  175 63 Bengali         GHORA
  175 56 Singhalese      HARENAWA
  175 17 Sardinian N     ORTARE
  175 76 Persian List    PICHIDAN
  175 05 Breton List     TURGNA
  175 37 English ST      TO TURN
  175 20 Spanish         VOLVER
  175 73 Ossetic         YZDAXYN
b                      002
  175 60 Panjabi ST      MORNA
  175 62 Hindi           MURNA
b                      003
  175 25 Penn. Dutch     DRAY
  175 28 Flemish         DRAAIJEN
  175 29 Frisian         DRAEIJE, WIELE, WIELJE
  175 38 Takitaki        DRAI
  175 27 Afrikaans       OMDRAAI, DRAAI, KEER
b                      004
  175 84 Albanian C      PRIREM
  175 83 Albanian K      PRIREM
b                      005
  175 07 Breton ST       TREIN
  175 06 Breton SE       TROEIN
  175 04 Welsh C         TROI
  175 03 Welsh N         TROI
b                      006
  175 72 Armenian List   TARNEL
  175 71 Armenian Mod    (VERA)DARNAL
b                      007
  175 74 Afghan          GERZEDEL
  175 75 Waziri          GERZEDEL
b                      008
  175 40 Lithuanian ST   KRYPTI, SUKTI
  175 39 Lithuanian O    KREIPTI
b                      009
  175 12 Provencal       VIRA, VIROUIA
  175 22 Brazilian       VIRAR
  175 21 Portuguese ST   VIRAR
  175 08 Rumanian List   A VIRA, A COTI
  175 16 French Creole D VIWE
b                      010
  175 13 French          TOURNER
  175 23 Catalan         TORNAR
  175 14 Walloon         TOURNER
  175 15 French Creole C VUHWE, TUNE
b                      011
  175 47 Czech E         KRUTIT
  175 54 Serbocroatian   OKRENUTI SE
b                      012
  175 95 ALBANIAN        KETHEJ
  175 82 Albanian G      KETHEJ
  175 80 Albanian T      ME U KTHYER
  175 81 Albanian Top    KTHENEM, AOR. UKTHEVA
b                      200
c                         200  2  201
  175 10 Italian         GIRARE
  175 18 Sardinian L     GIRARE
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  3  400
  175 11 Ladin           GIRER, VERDSCHER
b                      202
c                         201  2  202
c                         202  2  203
c                         202  3  400
  175 85 RUSSIAN P       VERTET
  175 87 BYELORUSSIAN P  VAROCAC
  175 41 Latvian         PAGRIEZT, PAVERST
  175 91 SLOVENIAN P     VRTETU
  175 86 UKRAINIAN P     VERTITY
  175 89 SLOVAK P        VRTIET
  175 90 CZECH P         VRATITI
  175 43 Lusatian L      WERSES
  175 44 Lusatian U      WJERCEC
  175 50 Polish          ZAWRACAC
  175 88 POLISH P        WIERCIC
  175 49 Byelorussian    PAVORACYVAC'
  175 51 Russian         POVORACIVAT
  175 48 Ukrainian       OBERTATYS'
  175 93 MACEDONIAN P    VRTAM
  175 53 Bulgarian       DA SE VERTI
  175 94 BULGARIAN P     VURT A
  175 52 Macedonian      VRTI, ZAVRTI, OBRNE
  175 92 SERBOCROATIAN P VRNUTI
  175 42 Slovenian       ABRNI SE
b                      203
c                         201  2  203
c                         202  2  203
c                         203  2  204
c                         203  3  400
  175 46 Slovak          OBRACAT , TOCIT
b                      204
c                         203  2  204
  175 45 Czech           TOCITI, OTACETI
b                      400
c                         201  3  400
c                         202  3  400
c                         203  3  400
  175 58 Marathi         VELNE.
  175 61 Lahnda          ULTAWEN
b                      205
c                         205  2  206
  175 65 Khaskura        PHARKNU
b                      206
c                         205  2  206
c                         206  2  207
  175 64 Nepali List     PHARKANU, PHIRNU
b                      207
c                         206  2  207
  175 59 Gujarati        FERWU
b                      208
c                         208  2  209
  175 36 Faroese         SNUGVA
  175 34 Riksmal         SNU
  175 35 Icelandic ST    SNUA(SK)
b                      209
c                         208  2  209
c                         209  2  210
  175 31 Swedish VL      SNO, VAN
b                      210
c                         209  2  210
  175 32 Swedish List    VANDA  PA
  175 30 Swedish Up      VANDA SIG OM
  175 24 German ST       WENDEN
  175 33 Danish          VENDE SIG
  175 26 Dutch List      WENDEN, LOEVEN
b                      211
c                         211  2  212
  175 68 Greek Mod       STRIVO
  175 70 Greek K         STREFO
b                      212
c                         211  2  212
c                         212  2  213
  175 67 Greek MD        STRIBO, GURISZO, GURNO
b                      213
c                         212  2  213
  175 69 Greek D         GURNAO
  175 66 Greek ML        GURIDZO
a 176 TWO
b                      002
  176 59 Gujarati        BE
  176 56 Singhalese      DEKA
  176 58 Marathi         DON
  176 30 Swedish Up      TVA
  176 31 Swedish VL      TZVA
  176 24 German ST       ZWEI
  176 35 Icelandic ST    TVEIR
  176 34 Riksmal         TO
  176 32 Swedish List    TVA
  176 33 Danish          TO
  176 36 Faroese         TVEIR
  176 29 Frisian         TWA
  176 28 Flemish         TWEE
  176 25 Penn. Dutch     ZWAY
  176 26 Dutch List      TWEE
  176 27 Afrikaans       TWEE
  176 38 Takitaki        TOE
  176 37 English ST      TWO
  176 09 Vlach           DWAWE
  176 17 Sardinian N     DUOS
  176 18 Sardinian L     DUOS
  176 15 French Creole C DE
  176 68 Greek Mod       DHIO
  176 66 Greek ML        DUO
  176 70 Greek K         DUO
  176 67 Greek MD        DUO
  176 69 Greek D         DUO
  176 08 Rumanian List   DOI
  176 11 Ladin           DUOS
  176 19 Sardinian C     DUSU
  176 10 Italian         DUE
  176 23 Catalan         DOS
  176 20 Spanish         DOS
  176 12 Provencal       DOUS, DOS
  176 14 Walloon         DEUS
  176 16 French Creole D DE
  176 13 French          DEUX
  176 21 Portuguese ST   DOUS
  176 22 Brazilian       DOIS
  176 87 BYELORUSSIAN P  DVA
  176 45 Czech           DVA, DVE
  176 90 CZECH P         DVA
  176 43 Lusatian L      DWA
  176 44 Lusatian U      DWAJ
  176 93 MACEDONIAN P    DVA
  176 50 Polish          DWA
  176 88 POLISH P        DWA
  176 51 Russian         DVA
  176 85 RUSSIAN P       DVA
  176 54 Serbocroatian   DVA
  176 92 SERBOCROATIAN P DVA
  176 46 Slovak          DVA
  176 89 SLOVAK P        DVA
  176 42 Slovenian       DUA
  176 91 SLOVENIAN P     DVA
  176 86 UKRAINIAN P     DVA
  176 94 BULGARIAN P     DVA
  176 41 Latvian         DIVI
  176 40 Lithuanian ST   DU, DVI
  176 39 Lithuanian O    DU, DVI
  176 52 Macedonian      DVA, DVE
  176 47 Czech E         DVA
  176 49 Byelorussian    DVA
  176 48 Ukrainian       DVA, DVOJE
  176 53 Bulgarian       DVE
  176 55 Gypsy Gk        DUI
  176 73 Ossetic         DUUAE
  176 57 Kashmiri        ZAH (DOYE = OBL.)
  176 64 Nepali List     DUI
  176 61 Lahnda          DU
  176 78 Baluchi         DO
  176 02 Irish B         DA
  176 01 Irish A         DO (DHA)
  176 03 Welsh N         DAU
  176 04 Welsh C         DAU
  176 05 Breton List     DAOU (M), DIOU (F)
  176 06 Breton SE       DEU
  176 07 Breton ST       DAOU
  176 77 Tadzik          DU
  176 76 Persian List    DO
  176 63 Bengali         DUI
  176 62 Hindi           DO
  176 60 Panjabi ST      DO
  176 65 Khaskura        DUITA, DUI
  176 74 Afghan          DVA
  176 75 Waziri          DWA
  176 79 Wakhi           BOJ
  176 81 Albanian Top    DY
  176 80 Albanian T      DY
  176 83 Albanian K      DI (M.), DII (F.)
  176 84 Albanian C      DI
  176 82 Albanian G      DY
  176 95 ALBANIAN        DY
  176 71 Armenian Mod    ERKU
  176 72 Armenian List   YERGU
a 177 TO VOMIT
b                      000
  177 02 Irish B
  177 82 Albanian G
  177 95 ALBANIAN
  177 25 Penn. Dutch
b                      001
  177 89 SLOVAK P        CHRLIT
  177 04 Welsh C         CYFOGI
  177 06 Breton SE       DAKOREIN
  177 76 Persian List    ESTEFRAG KARDAN (OQ ZADAN)
  177 60 Panjabi ST      KE+KERNA
  177 42 Slovenian       KOZLAT
  177 38 Takitaki        PIO, OFER
  177 73 Ossetic         TONYN
  177 23 Catalan         TRAURER, GITAR
  177 78 Baluchi         UCHALNA
  177 37 English ST      TO VOMIT
  177 79 Wakhi           WOQ-
b                      002
  177 50 Polish          WYMIOTOWAC
  177 88 POLISH P        WYMIOTOWAC
b                      003
  177 24 German ST       ASUBRECHEN
  177 28 Flemish         BRAKEN
  177 26 Dutch List      BRAKEN
  177 27 Afrikaans       BRAAK, VOMEER, VERMEER
b                      004
  177 21 Portuguese ST   VOMITAR
  177 22 Brazilian       VOMITAR
  177 13 French          VOMIR
  177 16 French Creole D VOMI
  177 14 Walloon         VOMI
  177 20 Spanish         VOMITAR
  177 10 Italian         VOMITARE
  177 19 Sardinian C     VOMITAI
  177 11 Ladin           VOMITER
  177 08 Rumanian List   A VOMITA
  177 40 Lithuanian ST   VEMTI
  177 39 Lithuanian O    VEMTI
  177 41 Latvian         VEMT
  177 09 Vlach           VOMU
  177 18 Sardinian L     VOMITARE
  177 15 French Creole C VOMI
  177 17 Sardinian N     BOMBERE
  177 12 Provencal       BOUMI, REGOULA
  177 57 Kashmiri        WAMUN
  177 56 Singhalese      VAMARANAWA
  177 63 Bengali         BOMI+KORA
b                      005
  177 46 Slovak          VYVRAVAT
  177 51 Russian         RVAT
  177 85 RUSSIAN P       RVAT
  177 87 BYELORUSSIAN P  RVAC
b                      006
  177 71 Armenian Mod    P`XCKAL
  177 72 Armenian List   PISKEL
b                      007
  177 81 Albanian Top    VIEL, AOR. VOTA
  177 83 Albanian K      VIEU (AOR. VOWA)
  177 84 Albanian C      VIGHEM
  177 80 Albanian T      ME YELLE
b                      008
  177 75 Waziri          KAI (VOMITING)
  177 74 Afghan          KANGI KAVEL
  177 77 Tadzik          KANDAN
b                      200
c                         200  2  201
  177 55 Gypsy Gk        CHADAMAN
  177 64 Nepali List     UGELNU, CHADNU
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
  177 65 Khaskura        CHHADNU, WAK, WAK GARNU, OKWAKNU
b                      202
c                         201  2  202
c                         202  2  203
  177 58 Marathi         OKNE.
b                      203
c                         201  2  203
c                         202  2  203
c                         203  2  204
  177 59 Gujarati        ULTI KERWI, OKWA
b                      204
c                         203  2  204
  177 61 Lahnda          ULTI KEREN
  177 62 Hindi           ULTI+KERNA
b                      205
c                         205  2  206
  177 66 Greek ML        KSERNO
b                      206
c                         205  2  206
c                         206  2  207
c                         206  2  208
  177 67 Greek MD        KANO, KSERNO
b                      207
c                         206  2  207
c                         207  2  208
  177 68 Greek Mod       KANO ANAGHULA
b                      208
c                         206  2  208
c                         207  2  208
c                         208  2  209
  177 69 Greek D         KANO EMETTO
b                      209
c                         208  2  209
  177 70 Greek K         EMESSO
b                      210
c                         210  3  211
  177 03 Welsh N         TAFLUIFYNY, CHWYDU
  177 05 Breton List     C'HOUEDI, DISLONKA, DISTEUREL
  177 07 Breton ST       DISLONKAN, DIC'HWEDIN
b                      211
c                         210  3  211
  177 01 Irish A         CAITHEAMH AMACH, AISEAG
b                      212
c                         212  2  213
  177 29 Frisian         SPUIJE
  177 36 Faroese         SPYGGJA
b                      213
c                         212  2  213
c                         213  2  214
  177 31 Swedish VL      SPY, KRAKAS
b                      214
c                         213  2  214
c                         214  2  215
  177 32 Swedish List    KRAKAS, KASTA (FA) UPP, SPY
  177 30 Swedish Up      KRAKAS, KASTA OPP
b                      215
c                         214  2  215
  177 33 Danish          KASTE OP
  177 35 Icelandic ST    KASTA UPP
  177 34 Riksmal         KASTE OPP
b                      216
c                         216  2  217
  177 53 Bulgarian       DA POVERNE
  177 54 Serbocroatian   POVRACATI
  177 45 Czech           ZVRACETI
  177 47 Czech E         VRACAT
  177 49 Byelorussian    VYRACAC'
b                      217
c                         216  2  217
c                         217  2  218
  177 48 Ukrainian       BLJUVATY, VERTATY
b                      218
c                         217  2  218
  177 52 Macedonian      BLUE
  177 86 UKRAINIAN P     BL UVATY
  177 91 SLOVENIAN P     BLJUVATI
  177 94 BULGARIAN P     BULVAM
  177 92 SERBOCROATIAN P BLJUVATI
  177 90 CZECH P         BLITI
  177 43 Lusatian L      BLUWAS
  177 44 Lusatian U      BLUWAC
  177 93 MACEDONIAN P    BLUVAM
a 178 TO WALK
b                      000
  178 79 Wakhi
b                      001
  178 08 Rumanian List   A SE PLIMBA, MERGE
  178 56 Singhalese      AVIDINAWA
  178 70 Greek K         BADIDZO
  178 73 Ossetic         CAEUYN
  178 53 Bulgarian       DA VERVI
  178 63 Bengali         HATA
  178 09 Vlach           IMNU
  178 78 Baluchi         JUZAGH, JUZITHA
  178 72 Armenian List   KALEB
  178 71 Armenian Mod    MAN GAL, SRJEL
  178 57 Kashmiri        PAKUN
  178 55 Gypsy Gk        PIRAV
  178 14 Walloon         ROTER
  178 75 Waziri          SAIL
  178 54 Serbocroatian   SETATI
  178 74 Afghan          TLEL
  178 26 Dutch List      WANDELEN
b                      002
  178 76 Persian List    RAH RAFTAN
  178 77 Tadzik          RAFTAN, OMADAN
b                      003
  178 59 Gujarati        CALWU
  178 58 Marathi         CELNE.
  178 62 Hindi           CELNA
b                      004
  178 07 Breton ST       KERZHOUT, BALE (SW)
  178 06 Breton SE       KERHET
  178 05 Breton List     KERZOUT, KERZET
  178 04 Welsh C         CERDDED
  178 03 Welsh N         CERDDED
b                      005
  178 30 Swedish Up      GA
  178 31 Swedish VL      GA
  178 36 Faroese         GANGA
  178 33 Danish          GAA
  178 32 Swedish List    GA  TILL FOTS  (I.E., ON FOOT)
  178 34 Riksmal         GA
  178 35 Icelandic ST    GANGA
  178 24 German ST       GEHEN
b                      006
  178 15 French Creole C MASE
  178 12 Provencal       MARCHA, ANA, SE GANDI
  178 13 French          MARCHER
  178 16 French Creole D MASE
b                      007
  178 01 Irish A         SIUBHAL
  178 02 Irish B         SIUBHLAIM
b                      008
  178 64 Nepali List     HIRNU, DULNU
  178 65 Khaskura        DULNU
b                      009
  178 38 Takitaki        WAKA
  178 37 English ST      TO WALK
b                      010
  178 40 Lithuanian ST   VAIKSCIOTI
  178 39 Lithuanian O    VAIKSCIOTI
b                      011
  178 69 Greek D         PERPATAO
  178 67 Greek MD        PERPATO
  178 68 Greek Mod       PERPATO
  178 66 Greek ML        PERPATO
b                      012
  178 81 Albanian Top    ECEN, AOR. ECA
  178 83 Albanian K      ECEN
  178 80 Albanian T      ME ECUR, ME BARITUR
  178 84 Albanian C      JEC
b                      013
  178 82 Albanian G      SKKOJ, VETE (VOJT)
  178 95 ALBANIAN        VETE (VOJT = INF.)
b                      014
  178 27 Afrikaans       LOOP, VOETSLAAN
  178 25 Penn. Dutch     LAWF
  178 28 Flemish         LOOPEN
  178 29 Frisian         LIPPEN, SOALJE
b                      015
  178 61 Lahnda          TUREN
  178 60 Panjabi ST      TURNA
b                      016
  178 86 UKRAINIAN P     ITY
  178 91 SLOVENIAN P     ITI
  178 42 Slovenian       HODIT
  178 89 SLOVAK P        IST
  178 46 Slovak          CHODIT
  178 92 SERBOCROATIAN P ICI
  178 85 RUSSIAN P       ITTI
  178 51 Russian         XODIT
  178 88 POLISH P        ISC
  178 50 Polish          CHODZIC
  178 93 MACEDONIAN P    IDAM
  178 44 Lusatian U      HIC
  178 43 Lusatian L      HIS
  178 90 CZECH P         JITI
  178 45 Czech           PROCHAZETI SE, CHODITI
  178 87 BYELORUSSIAN P  ISCI
  178 94 BULGARIAN P     OTIVAM
  178 41 Latvian         IET, STAIGAT
  178 52 Macedonian      ODI
  178 49 Byelorussian    SPACYRAVAC', ISCI
  178 48 Ukrainian       XODYTY, ITY
  178 47 Czech E         XODYIT
b                      200
c                         200  2  201
  178 20 Spanish         PASEAR
  178 19 Sardinian C     PASSILLAI
  178 18 Sardinian L     PASSIZZARE
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  2  204
  178 21 Portuguese ST   ANDAR, CAMINHAR, PASSEAR
b                      202
c                         201  2  202
c                         202  2  203
c                         202  2  204
  178 23 Catalan         ANAR, CAMINAR
b                      203
c                         201  2  203
c                         202  2  203
  178 22 Brazilian       ANDAR A PE
  178 17 Sardinian N     ANNARE
b                      204
c                         201  2  204
c                         202  2  204
  178 11 Ladin           CHAMINER
  178 10 Italian         CAMMIRARE
a 179 WARM (WEATHER)
b                      000
  179 35 Icelandic ST
b                      001
  179 01 Irish A         BROTHALLACH
  179 72 Armenian List   DAK
  179 36 Faroese         HEITUR, LYGGJUR
  179 64 Nepali List     NIYANU
  179 56 Singhalese      RASNE
  179 71 Armenian Mod    TOT`, SOG
  179 57 Kashmiri        WUSHUNU
b                      002
  179 24 German ST       WARM
  179 34 Riksmal         VARM
  179 32 Swedish List    VARM
  179 33 Danish          VARM
  179 29 Frisian         WAERM
  179 28 Flemish         WARM
  179 25 Penn. Dutch     WAAREM
  179 26 Dutch List      WARM
  179 27 Afrikaans       WARM
  179 38 Takitaki        WARAM
  179 37 English ST      WARM
  179 31 Swedish VL      VARM
  179 30 Swedish Up      VARM
  179 73 Ossetic         X"ARM
  179 61 Lahnda          GERMI
  179 79 Wakhi           THIN, GERM, SONDER
  179 78 Baluchi         GARM
  179 77 Tadzik          GARM
  179 59 Gujarati        GEREM
  179 60 Panjabi ST      GEREM
  179 62 Hindi           GEREM
  179 63 Bengali         GOROM
  179 58 Marathi         GEREM, UN
  179 76 Persian List    GARM
  179 70 Greek K         THERMOS
  179 42 Slovenian       GORKO
  179 80 Albanian T      I, E NXEHTE
  179 81 Albanian Top    NGROTE
  179 83 Albanian K      NGROXETE
  179 84 Albanian C      NGROXT
  179 82 Albanian G      NGROFET
  179 95 ALBANIAN        NGROFET
b                      003
  179 40 Lithuanian ST   SILTAS
  179 39 Lithuanian O    SILTAS
  179 41 Latvian         SILTS
  179 09 Vlach           KELDURE
  179 18 Sardinian L     CALDU
  179 17 Sardinian N     KAENTE
  179 15 French Creole C SO
  179 08 Rumanian List   CALD, CALDUROS
  179 11 Ladin           CHOD
  179 19 Sardinian C     KALLENTI
  179 10 Italian         CALDO
  179 13 French          CHAUD
  179 16 French Creole D SO
  179 14 Walloon         TCHOD
  179 12 Provencal       CAUD, AUDO
  179 20 Spanish         CALIENTE
  179 23 Catalan         CALENT
b                      004
  179 65 Khaskura        MANTATO, TATO
  179 55 Gypsy Gk        TATO
b                      005
  179 74 Afghan          TOD
  179 75 Waziri          TOD
b                      006
  179 07 Breton ST       TOMM
  179 06 Breton SE       TUEM
  179 05 Breton List     TOMM
  179 04 Welsh C         TWYM
  179 03 Welsh N         CYNNES, TEG
  179 02 Irish B         TE
  179 86 UKRAINIAN P     TEPLYJ
  179 91 SLOVENIAN P     TOPEL
  179 89 SLOVAK P        TEPLY
  179 46 Slovak          TEPLY
  179 92 SERBOCROATIAN P TOPAO
  179 54 Serbocroatian   TOPLO
  179 85 RUSSIAN P       T OPLYJ
  179 51 Russian         TEPLYJ
  179 88 POLISH P        CIEPLY
  179 50 Polish          CIEPLY
  179 93 MACEDONIAN P    TOPOL
  179 44 Lusatian U      COPLY
  179 43 Lusatian L      SOPLY
  179 90 CZECH P         TEPLY
  179 45 Czech           TEPLY
  179 87 BYELORUSSIAN P  C OPLY
  179 94 BULGARIAN P     TOPUL
  179 52 Macedonian      GREE, TOPLI, TOPUL
  179 47 Czech E         TEPLE
  179 49 Byelorussian    CEPLY
  179 48 Ukrainian       TEPLYJ, PALKYJ
  179 53 Bulgarian       TOPLO
b                      007
  179 69 Greek D         DZESTOS
  179 67 Greek MD        DZESTOS
  179 68 Greek Mod       ZESTOS
  179 66 Greek ML        DZESTOS
b                      008
  179 21 Portuguese ST   QUENTE
  179 22 Brazilian       QUENTE
a 180 TO WASH
b                      000
  180 65 Khaskura
b                      001
  180 73 Ossetic         AEXSYN
  180 77 Tadzik          MUSTAN
  180 23 Catalan         RENTAR, CERAR
  180 19 Sardinian C     SAKKUAI
  180 18 Sardinian L     SAMUNARE
  180 79 Wakhi           WUZDI-
  180 55 Gypsy Gk        XALAVAV
b                      002
  180 06 Breton SE       GOLHEIN
  180 05 Breton List     GWALC'HI
  180 07 Breton ST       GWALC'HIN
  180 04 Welsh C         GOLCHI
  180 03 Welsh N         GOLCHI, YMOLCHI (REFLEXIVE)
b                      003
  180 01 Irish A         NIGHE
  180 02 Irish B         NIGHIM, D'IONNLAT, IONNAILIM
b                      004
  180 10 Italian         LAVARE
  180 09 Vlach           LAU
  180 17 Sardinian N     LAVARE
  180 15 French Creole C LAVE (CLOTHES), BEYE (SELF)
  180 11 Ladin           LAVER
  180 13 French          LAVER
  180 16 French Creole D LAVE
  180 14 Walloon         LAVER
  180 12 Provencal       LAVA
  180 20 Spanish         LAVAR
  180 22 Brazilian       LAVAR
  180 21 Portuguese ST   LAVAR
  180 08 Rumanian List   A (SE) SPALA
b                      005
  180 68 Greek Mod       PLENO
  180 66 Greek ML        PLUNO
  180 70 Greek K         PLINO
  180 67 Greek MD        PLENO
  180 69 Greek D         PLENO
b                      006
  180 24 German ST       WASCHEN
  180 34 Riksmal         VASKE
  180 33 Danish          VASKE
  180 27 Afrikaans       WAS
  180 26 Dutch List      WASSCHEN
  180 25 Penn. Dutch     WESCH
  180 28 Flemish         WASSCHEN
  180 29 Frisian         GROBBELJE, WAECHSE
  180 38 Takitaki        WASI
  180 37 English ST      TO WASH
b                      007
  180 75 Waziri          WINZEL
  180 74 Afghan          MINDZEL
b                      008
  180 84 Albanian C      LAN
  180 81 Albanian Top    LHAN, AOR. LHAVA
  180 82 Albanian G      LAJ
  180 83 Albanian K      LAAN
  180 80 Albanian T      ME LARE
  180 95 ALBANIAN        LAJ, (LAVA = AOR.)
b                      009
  180 30 Swedish Up      TVATTA
  180 31 Swedish VL      TZVAT
  180 35 Icelandic ST    THVO
  180 32 Swedish List    TVATTA
  180 36 Faroese         TVAA
b                      010
  180 72 Armenian List   LUVAL
  180 71 Armenian Mod    LVANAL
b                      011
  180 76 Persian List    SHOSTAN
  180 78 Baluchi         SHODHAGH, SHUSTA
b                      100
  180 56 Singhalese      SODANAWA
  180 57 Kashmiri        CHALUN, SORSHUN
b                      200
c                         200  2  201
  180 62 Hindi           DHONA
  180 63 Bengali         DHOA
  180 58 Marathi         DHUNE.
  180 61 Lahnda          DHOWEN
  180 59 Gujarati        DHOWU
  180 60 Panjabi ST      TONA
b                      201
c                         200  2  201
c                         201  2  202
  180 64 Nepali List     DHUNU, PAKHALNU, MAJNU
b                      202
c                         201  2  202
  180 40 Lithuanian ST   MAZGOTI
  180 39 Lithuanian O    MAZGOTI, SKALBTI
  180 41 Latvian         MAZGAT
b                      203
c                         203  2  204
  180 91 SLOVENIAN P     MITI
  180 86 UKRAINIAN P     MYTY
  180 92 SERBOCROATIAN P MITI
  180 46 Slovak          MYT
  180 89 SLOVAK P        MYT
  180 53 Bulgarian       DA MIE
  180 52 Macedonian      MIE/ISKAPE/PLAKNE
  180 49 Byelorussian    MYC'
  180 94 BULGARIAN P     MIJA
  180 87 BYELORUSSIAN P  MYC
  180 45 Czech           MYTI
  180 90 CZECH P         MITI
  180 43 Lusatian L      MYS
  180 44 Lusatian U      MYC
  180 93 MACEDONIAN P    MIJAM
  180 50 Polish          MYC
  180 88 POLISH P        MYC
  180 51 Russian         MYT
  180 85 RUSSIAN P       MYT
b                      204
c                         203  2  204
c                         204  2  205
  180 48 Ukrainian       MYTYSJA, PRATY, MYTY
  180 47 Czech E         UMIT, PRAT
b                      205
c                         204  2  205
  180 54 Serbocroatian   PRATI
  180 42 Slovenian       PRAT
a 181 WATER
b                      002
  181 68 Greek Mod       NERO
  181 66 Greek ML        NERO
  181 67 Greek MD        NERO
  181 69 Greek D         NERO
b                      003
  181 08 Rumanian List   APA
  181 09 Vlach           APE
  181 18 Sardinian L     ABBA
  181 17 Sardinian N     ABBA
  181 15 French Creole C DLO, GLO
  181 11 Ladin           OVA
  181 19 Sardinian C     AKKUA
  181 10 Italian         ACQUA
  181 23 Catalan         AYGUA
  181 20 Spanish         AGUA
  181 12 Provencal       AIGO
  181 14 Walloon         EWE
  181 16 French Creole D DLO
  181 13 French          EAU
  181 21 Portuguese ST   AGUA
  181 22 Brazilian       AGUA
b                      004
  181 70 Greek K         HUDOR
  181 01 Irish A         UISGE
  181 02 Irish B         UISCE
  181 51 Russian         VODA
  181 85 RUSSIAN P       VODA
  181 54 Serbocroatian   VODA
  181 92 SERBOCROATIAN P VODA
  181 46 Slovak          VODA
  181 89 SLOVAK P        VODA
  181 42 Slovenian       VODA
  181 91 SLOVENIAN P     VODA
  181 86 UKRAINIAN P     VODA
  181 88 POLISH P        WODA
  181 50 Polish          WODA
  181 93 MACEDONIAN P    VODA
  181 44 Lusatian U      WODA
  181 43 Lusatian L      WODA
  181 90 CZECH P         VODA
  181 45 Czech           VODA
  181 87 BYELORUSSIAN P  VADA
  181 40 Lithuanian ST   VANDUO
  181 41 Latvian         UDENS
  181 39 Lithuanian O    VANDUO
  181 94 BULGARIAN P     VODA
  181 52 Macedonian      VODA
  181 47 Czech E         VODA
  181 49 Byelorussian    VADA
  181 48 Ukrainian       VODA
  181 53 Bulgarian       VODA
  181 30 Swedish Up      VATTEN
  181 31 Swedish VL      VATN
  181 56 Singhalese      WATURA
  181 24 German ST       WASSER
  181 35 Icelandic ST    VATN
  181 34 Riksmal         VANN
  181 32 Swedish List    VATTEN
  181 33 Danish          VAND
  181 36 Faroese         VATN
  181 29 Frisian         WETTER
  181 28 Flemish         WATER
  181 25 Penn. Dutch     WASSER
  181 26 Dutch List      WATER
  181 27 Afrikaans       WATER
  181 38 Takitaki        WATRA
  181 37 English ST      WATER
  181 81 Albanian Top    UJE
  181 80 Albanian T      UJE
  181 83 Albanian K      UJE
  181 84 Albanian C      UJ
  181 82 Albanian G      UJT
  181 95 ALBANIAN        UJT
  181 73 Ossetic         DON
b                      005
  181 03 Welsh N         DWR
  181 04 Welsh C         DWR
  181 05 Breton List     DOUR
  181 06 Breton SE       DEUR
  181 07 Breton ST       DOUR
b                      006
  181 71 Armenian Mod    JUR
  181 72 Armenian List   CZOOR
b                      200
c                         200  2  201
  181 63 Bengali         JOL
b                      201
c                         200  2  201
c                         201  2  202
  181 65 Khaskura        PANI, JEL
b                      202
c                         201  2  202
  181 55 Gypsy Gk        PAI
  181 57 Kashmiri        PONU
  181 64 Nepali List     PANI
  181 61 Lahnda          PANI
  181 59 Gujarati        PANI
  181 58 Marathi         PANI
  181 62 Hindi           PANI
  181 60 Panjabi ST      PANI
b                      203
c                         203  3  204
  181 75 Waziri          EBO
  181 78 Baluchi         AF
  181 74 Afghan          OBE
  181 77 Tadzik          OB
  181 76 Persian List    AB
b                      204
c                         203  3  204
  181 79 Wakhi           YUPK
a 182 WE
b                      001
  182 79 Wakhi           SUK
b                      002
  182 37 English ST      WE
  182 38 Takitaki        WI
  182 30 Swedish Up      VI
  182 31 Swedish VL      VI
  182 28 Flemish         WY
  182 29 Frisian         WY
  182 36 Faroese         VIT
  182 33 Danish          VI
  182 32 Swedish List    VI
  182 34 Riksmal         VI
  182 35 Icelandic ST    VIO
  182 24 German ST       WIR
  182 26 Dutch List      WIJ
  182 68 Greek Mod       EMIS
  182 66 Greek ML        EMEIS
  182 70 Greek K         HEMEIS
  182 67 Greek MD        EMEIS, MEIS, MAS
  182 69 Greek D         EMEIS
  182 57 Kashmiri        ASI
  182 60 Panjabi ST      ESI
  182 61 Lahnda          ESSA
  182 55 Gypsy Gk        AMEN
  182 59 Gujarati        EHME
  182 64 Nepali List     HAMI
  182 62 Hindi           HEM
  182 65 Khaskura        HAMIHARU
  182 63 Bengali         AMRA
  182 58 Marathi         AMHI (EXCL.), APEN (INCL.)
  182 56 Singhalese      API
  182 27 Afrikaans       ONS
  182 87 BYELORUSSIAN P  MY
  182 45 Czech           MY
  182 90 CZECH P         MY
  182 43 Lusatian L      MY
  182 44 Lusatian U      MY
  182 50 Polish          MY
  182 88 POLISH P        MY
  182 51 Russian         MY
  182 85 RUSSIAN P       MY
  182 54 Serbocroatian   MI
  182 92 SERBOCROATIAN P MI
  182 46 Slovak          MY
  182 89 SLOVAK P        MY
  182 42 Slovenian       MI
  182 91 SLOVENIAN P     MI
  182 86 UKRAINIAN P     MY
  182 48 Ukrainian       MY
  182 49 Byelorussian    MY
  182 47 Czech E         MI
  182 40 Lithuanian ST   MES
  182 39 Lithuanian O    MES
  182 41 Latvian         MES
  182 72 Armenian List   MENK
  182 71 Armenian Mod    MENK`
  182 81 Albanian Top    NEVE, NE
  182 80 Albanian T      NE
  182 83 Albanian K      NA
  182 84 Albanian C      NA
  182 82 Albanian G      NE
  182 95 ALBANIAN        NE, NA
  182 13 French          NOUS
  182 09 Vlach           NOI
  182 17 Sardinian N     NOIS
  182 18 Sardinian L     NOS
  182 15 French Creole C NU
  182 16 French Creole D NU
  182 14 Walloon         NOS
  182 12 Provencal       NOUS, NAUTRE
  182 20 Spanish         NOSOTROS
  182 23 Catalan         NOSALTRES
  182 10 Italian         NOI
  182 19 Sardinian C     NOSUS
  182 11 Ladin           NUS
  182 08 Rumanian List   NOI
  182 22 Brazilian       NOS
  182 21 Portuguese ST   NOS
  182 52 Macedonian      MIE/NIE
  182 53 Bulgarian       NIE
  182 94 BULGARIAN P     NIE
  182 93 MACEDONIAN P    NIE
  182 07 Breton ST       NI
  182 06 Breton SE       NI
  182 05 Breton List     NI
  182 04 Welsh C         NI
  182 03 Welsh N         NI
  182 01 Irish A         SINN
  182 02 Irish B         INN, SINN, SINNE, INNE
  182 78 Baluchi         MA
  182 77 Tadzik          MO, MOEN
  182 76 Persian List    MA
  182 74 Afghan          MUZ
  182 75 Waziri          MIZH
  182 73 Ossetic         MAX
  182 25 Penn. Dutch     MIER
a 183 WET
b                      000
  183 52 Macedonian
b                      001
  183 10 Italian         BAGNATO
  183 11 Ladin           BLETSCH, CREGN
  183 64 Nepali List     CISO
  183 65 Khaskura        CHILO, RUJHIYO
  183 60 Panjabi ST      GILLA
  183 55 Gypsy Gk        KINGO
  183 57 Kashmiri        ODURU, KYONU
  183 58 Marathi         OLA
  183 72 Armenian List   TATZ
  183 56 Singhalese      TETA
  183 61 Lahnda          SINNA
  183 71 Armenian Mod    XONAW
b                      002
  183 78 Baluchi         THAR
  183 77 Tadzik          TAR, NAM
  183 76 Persian List    TAR
b                      003
  183 07 Breton ST       GLEB
  183 01 Irish A         FLIUCH
  183 02 Irish B         FLIUCH
  183 03 Welsh N         GWLYB
  183 04 Welsh C         GWLYB
  183 05 Breton List     (TO WET)  GLEBIA, DOURA
  183 06 Breton SE       GLOEB
b                      004
  183 24 German ST       NASS
  183 28 Flemish         NAT
  183 25 Penn. Dutch     NAASZ
  183 26 Dutch List      NAT
  183 27 Afrikaans       NAT
  183 38 Takitaki        NATI
b                      005
  183 30 Swedish Up      VAT
  183 31 Swedish VL      BLOT, VOT  VAT
  183 35 Icelandic ST    VOTUR
  183 34 Riksmal         VAT
  183 32 Swedish List    VAT
  183 33 Danish          VAAD
  183 36 Faroese         VATUR
  183 29 Frisian         WIET
  183 37 English ST      WET
b                      006
  183 40 Lithuanian ST   SLAPIAS
  183 39 Lithuanian O    SLAPIAS
  183 41 Latvian         SLAPS
b                      007
  183 94 BULGARIAN P     MOKUR
  183 87 BYELORUSSIAN P  MOKRY
  183 45 Czech           MOKRY, VLHKY
  183 90 CZECH P         MOKRY
  183 43 Lusatian L      MOKSY
  183 44 Lusatian U      MOKRY
  183 93 MACEDONIAN P    MOKAR
  183 50 Polish          MOKRY
  183 88 POLISH P        MOKRY
  183 51 Russian         MOKRYJ
  183 85 RUSSIAN P       MOKRYJ
  183 54 Serbocroatian   MOKAR
  183 92 SERBOCROATIAN P MOKAR
  183 46 Slovak          MOKRY
  183 89 SLOVAK P        MOKRY
  183 42 Slovenian       MAKRO
  183 91 SLOVENIAN P     MOKER
  183 86 UKRAINIAN P     MOKRYJ
  183 47 Czech E         MOKRE
  183 49 Byelorussian    MOKRY, MOKRA
  183 53 Bulgarian       MOKRO
  183 48 Ukrainian       MOKRYJ, VOHKYJ
b                      008
  183 81 Albanian Top    LHAGUR-I
  183 80 Albanian T      I, E LAGUR
  183 83 Albanian K      I-NOTISURE   I-LAGURE
  183 84 Albanian C      LAGET
  183 82 Albanian G      LAKT
  183 95 ALBANIAN        LAKT
b                      009
  183 19 Sardinian C     SFUSTU
  183 17 Sardinian N     IFUSTU
b                      010
  183 69 Greek D         BREMMENOS
  183 66 Greek ML        BREMENOS
  183 67 Greek MD        BREMENOS
b                      011
  183 70 Greek K         HUGROS
  183 68 Greek Mod       OGHROS
  183 18 Sardinian L     UMIDU
  183 08 Rumanian List   UD
  183 09 Vlach           UDER
b                      012
  183 15 French Creole C MUYE  MWIYE
  183 23 Catalan         MULLADA, MULLADURA
  183 20 Spanish         MOJADO
  183 12 Provencal       MUIA, IME, IMO, MOUISSE
  183 14 Walloon         (TO WET) MOUYI
  183 16 French Creole D MUYE
  183 13 French          MOUILLE
  183 21 Portuguese ST   MOLHADO
  183 22 Brazilian       MOLHADO
b                      200
c                         200  3  201
  183 63 Bengali         BHIJA
  183 62 Hindi           BHIGA
b                      201
c                         200  3  201
  183 59 Gujarati        BHIHNU
b                      202
c                         202  3  203
  183 75 Waziri          LIMD, TOND
b                      203
c                         202  3  203
c                         203  2  204
c                         203  3  205
  183 74 Afghan          LUND, XIST
b                      204
c                         203  2  204
c                         204  3  205
  183 79 Wakhi           XUSC
b                      205
c                         203  3  205
c                         204  3  205
  183 73 Ossetic         XUYLYDZ
a 184 WHAT
b                      000
  184 73 Ossetic
b                      001
  184 38 Takitaki        HOESAN, SANI
  184 56 Singhalese      MOKADA
b                      002
  184 17 Sardinian N     ITTE
  184 19 Sardinian C     ITTA
b                      003
  184 40 Lithuanian ST   KAS
  184 39 Lithuanian O    KA
  184 41 Latvian         KAS
  184 68 Greek Mod       TI
  184 66 Greek ML        TI
  184 70 Greek K         TI
  184 67 Greek MD        TI
  184 69 Greek D         TI
  184 58 Marathi         KAY
  184 63 Bengali         KI
  184 62 Hindi           KYA
  184 60 Panjabi ST      KI
  184 65 Khaskura        KYA
  184 61 Lahnda          KE
  184 64 Nepali List     KE, KO
  184 57 Kashmiri        KYAH
  184 79 Wakhi           CIZ, CICIZ
  184 74 Afghan          CE
  184 77 Tadzik          CI
  184 76 Persian List    CHE
  184 75 Waziri          KIM, TSE
  184 09 Vlach           CI
  184 18 Sardinian L     CHI
  184 11 Ladin           CHE
  184 08 Rumanian List   CE
  184 14 Walloon         QUI, QWE
  184 12 Provencal       QUE
  184 20 Spanish         QUE
  184 23 Catalan         QUIN, QUE
  184 10 Italian         CHE
  184 13 French          QUE
  184 22 Brazilian       QUE
  184 15 French Creole C KI SA
  184 16 French Creole D (KI)SA
  184 21 Portuguese ST   QUE
  184 94 BULGARIAN P     STO
  184 87 BYELORUSSIAN P  STO
  184 45 Czech           CO
  184 90 CZECH P         CO
  184 43 Lusatian L      CO
  184 44 Lusatian U      STO
  184 93 MACEDONIAN P    STO
  184 50 Polish          CO
  184 88 POLISH P        CO
  184 51 Russian         CTO
  184 85 RUSSIAN P       STO
  184 54 Serbocroatian   STO
  184 92 SERBOCROATIAN P STO
  184 46 Slovak          CO
  184 89 SLOVAK P        CO
  184 86 UKRAINIAN P     SCO
  184 52 Macedonian      STO
  184 47 Czech E         CO
  184 49 Byelorussian    STO
  184 48 Ukrainian       SCO, SKIL'KY' JAKYJ
  184 30 Swedish Up      VAD, VA
  184 31 Swedish VL      VA, VA
  184 26 Dutch List      WAT
  184 25 Penn. Dutch     WAAS
  184 28 Flemish         WAT
  184 29 Frisian         DET, HWAT
  184 36 Faroese         HVAT
  184 33 Danish          HVAD
  184 32 Swedish List    VAD
  184 34 Riksmal         HVAD
  184 35 Icelandic ST    HVAO
  184 24 German ST       WAS
  184 27 Afrikaans       WAT, WATTER, HOE
  184 37 English ST      WHAT
  184 07 Breton ST       PETRA
  184 06 Breton SE       PETRA
  184 05 Breton List     PETRA
  184 04 Welsh C         BETH
  184 03 Welsh N         BETH
  184 01 Irish A         CAD
  184 02 Irish B         CAD
  184 71 Armenian Mod    INC`
  184 72 Armenian List   INCH
  184 81 Albanian Top    CE
  184 82 Albanian G      TSH
  184 84 Albanian C      CE
  184 83 Albanian K      CE
  184 95 ALBANIAN        TSH, TSHFAR, SE
  184 80 Albanian T      CFARE
  184 42 Slovenian       KAY
  184 91 SLOVENIAN P     KAJ
  184 53 Bulgarian       KAKVO
  184 78 Baluchi         KITHAN
b                      100
  184 59 Gujarati        SU
  184 55 Gypsy Gk        SO
a 185 WHEN
b                      001
  185 38 Takitaki        HOETEM
  185 59 Gujarati        RYARE
  185 79 Wakhi           TSOGHD, TSOGHDER, TSEWUXT
b                      002
  185 16 French Creole D KITA
  185 15 French Creole C KI TA
b                      003
  185 71 Armenian Mod    ERB
  185 72 Armenian List   YERP
b                      004
  185 86 UKRAINIAN P     KOLY
  185 87 BYELORUSSIAN P  KALI
  185 49 Byelorussian    KALI
  185 48 Ukrainian       KOLY
b                      005
  185 01 Irish A         CATHAIN
  185 02 Irish B         ANTAN, AN UAIR, CATHOIN
b                      200
c                         200  2  201
  185 37 English ST      WHEN
  185 24 German ST       WANN
  185 25 Penn. Dutch     WONN
  185 27 Afrikaans       WANNEER, TOE, AS
  185 26 Dutch List      WANNEER
  185 28 Flemish         WANNEER
  185 29 Frisian         HONEAR, HWENNEAR
  185 35 Icelandic ST    HVENAER
  185 13 French          QUAND
  185 22 Brazilian       QUANDO
  185 21 Portuguese ST   QUANDO
  185 09 Vlach           KYNTU
  185 17 Sardinian N     KANDO
  185 18 Sardinian L     CANDU
  185 08 Rumanian List   CIND
  185 14 Walloon         CWAND, QWAND
  185 12 Provencal       QUAND, QUOURO
  185 20 Spanish         CUANDO
  185 23 Catalan         QUANT
  185 10 Italian         QUANDO
  185 19 Sardinian C     KANDU
  185 68 Greek Mod       POTE
  185 66 Greek ML        POTE
  185 70 Greek K         POTE
  185 67 Greek MD        POTE
  185 69 Greek D         POTE
  185 81 Albanian Top    KUR
  185 82 Albanian G      KUR
  185 84 Albanian C      KUR
  185 83 Albanian K      KUUR
  185 80 Albanian T      KUR
  185 95 ALBANIAN        KUR
  185 92 SERBOCROATIAN P KADA
  185 46 Slovak          KEDY
  185 89 SLOVAK P        KEDY
  185 42 Slovenian       KEDAJ
  185 91 SLOVENIAN P     KADAR
  185 54 Serbocroatian   KADA
  185 50 Polish          KIEDY
  185 88 POLISH P        KIEDY
  185 90 CZECH P         KDY
  185 43 Lusatian L      GDY
  185 44 Lusatian U      HDY
  185 45 Czech           KDY
  185 40 Lithuanian ST   KADA
  185 39 Lithuanian O    KADA
  185 41 Latvian         KAD
  185 47 Czech E         KEDI
  185 64 Nepali List     KABA
  185 62 Hindi           KEB
  185 58 Marathi         KEVHA
  185 57 Kashmiri        KAR
  185 61 Lahnda          KERE WELE
  185 60 Panjabi ST      KED, KEDO
  185 55 Gypsy Gk        KANA
  185 73 Ossetic         KAED
  185 78 Baluchi         KHADHE
  185 63 Bengali         KOKHON
  185 51 Russian         KOGDA
  185 85 RUSSIAN P       KOGDA
  185 93 MACEDONIAN P    KOGA
  185 94 BULGARIAN P     KOGA
  185 52 Macedonian      KOGA
  185 53 Bulgarian       KOGA
  185 77 Tadzik          KAJ
  185 76 Persian List    KEY
  185 75 Waziri          KALLA
  185 74 Afghan          KELA
  185 56 Singhalese      KOI
  185 65 Khaskura        KAILE
  185 11 Ladin           CUR, CURA
  185 07 Breton ST       PEUR, PEGOULZ
  185 06 Breton SE       PEUR
  185 05 Breton List     PEUR, PEGOULS, PE VARE
  185 04 Welsh C         PRYD
  185 03 Welsh N         PRYD
b                      201
c                         200  2  201
c                         201  2  202
  185 33 Danish          HVORNAAR, NAAR
b                      202
c                         201  2  202
  185 32 Swedish List    NAR
  185 34 Riksmal         NAR
  185 30 Swedish Up      NAR
  185 31 Swedish VL      NAR
  185 36 Faroese         NAER
a 186 WHERE
b                      001
  186 29 Frisian         DER'T
  186 06 Breton SE       MEN
  186 38 Takitaki        PEE
  186 59 Gujarati        RYA
  186 78 Baluchi         THANGO
b                      200
c                         200  3  201
c                         200  3  202
c                         200  3  203
c                         200  3  204
  186 68 Greek Mod       PU
  186 66 Greek ML        POU
  186 70 Greek K         POU
  186 67 Greek MD        POU
  186 69 Greek D         POU
  186 40 Lithuanian ST   KUR
  186 39 Lithuanian O    KUR
  186 41 Latvian         KUR
  186 81 Albanian Top    KU
  186 82 Albanian G      KU
  186 84 Albanian C      KU
  186 83 Albanian K      KU
  186 80 Albanian T      KU
  186 95 ALBANIAN        KU
  186 94 BULGARIAN P     GDE
  186 87 BYELORUSSIAN P  DZE
  186 45 Czech           KDE
  186 90 CZECH P         KDE
  186 43 Lusatian L      ZO
  186 44 Lusatian U      HDZE
  186 93 MACEDONIAN P    KADE
  186 50 Polish          GDZIE
  186 88 POLISH P        GDZIE
  186 51 Russian         GDE
  186 85 RUSSIAN P       GDE
  186 54 Serbocroatian   GDE
  186 92 SERBOCROATIAN P GDE
  186 46 Slovak          KDE
  186 89 SLOVAK P        KDE
  186 42 Slovenian       KJE
  186 91 SLOVENIAN P     KJE
  186 86 UKRAINIAN P     DE
  186 52 Macedonian      KADE
  186 47 Czech E         GDE, KAM
  186 49 Byelorussian    DZE
  186 53 Bulgarian       KEDE
  186 48 Ukrainian       DE KUDY
  186 30 Swedish Up      VAR
  186 31 Swedish VL      VAS
  186 36 Faroese         HVAR
  186 33 Danish          HVOR
  186 32 Swedish List    VAR
  186 34 Riksmal         HVOR
  186 35 Icelandic ST    HVAR
  186 24 German ST       WO
  186 27 Afrikaans       WAAR, WAARHEEN
  186 26 Dutch List      WAAR
  186 25 Penn. Dutch     WUU
  186 28 Flemish         WAER
  186 37 English ST      WHERE
  186 58 Marathi         KUTHE.
  186 63 Bengali         KOTHAE
  186 56 Singhalese      KOTANADA
  186 57 Kashmiri        KATI, KOTU
  186 55 Gypsy Gk        KAY
  186 64 Nepali List     KAHA
  186 62 Hindi           KEHA
  186 65 Khaskura        KAHAN
  186 73 Ossetic         KAEM
  186 79 Wakhi           KUMER, KUMJAEI
  186 77 Tadzik          KUCO
  186 76 Persian List    KOJA
  186 13 French          OU
  186 14 Walloon         WICE
  186 10 Italian         DOVE
  186 09 Vlach           YU
  186 15 French Creole C KI KOTE / O LA
  186 16 French Creole D OLA
  186 11 Ladin           INUA
  186 17 Sardinian N     INUMBE
  186 18 Sardinian L     INUE
  186 19 Sardinian C     AUNDI
  186 23 Catalan         AHONT
  186 08 Rumanian List   UNDE, INCOTRO
  186 22 Brazilian       ONDE
  186 21 Portuguese ST   ONDE
  186 20 Spanish         DONDE
  186 12 Provencal       OUNTE, MOUNTE
  186 60 Panjabi ST      KITTHE
  186 61 Lahnda          KITTHA
b                      201
c                         200  3  201
c                         201  3  202
c                         201  3  203
c                         201  3  204
  186 07 Breton ST       PELEC'H
  186 05 Breton List     PELEC'H
  186 04 Welsh C         LLE
  186 03 Welsh N         PLE
b                      202
c                         200  3  202
c                         201  3  202
c                         202  3  203
c                         202  3  204
  186 01 Irish A         CA
  186 02 Irish B         CAIT, CA, CA IONAD
b                      203
c                         200  3  203
c                         201  3  203
c                         202  3  203
c                         203  3  204
  186 71 Armenian Mod    UR
  186 72 Armenian List   OOR
b                      204
c                         200  3  204
c                         201  3  204
c                         202  3  204
c                         203  3  204
  186 75 Waziri          CHERE
  186 74 Afghan          CIRI, CIRTA
a 187 WHITE
b                      001
  187 60 Panjabi ST      CITTA
  187 42 Slovenian       KELO
  187 70 Greek K         LEUKOS
  187 55 Gypsy Gk        PARNO
  187 79 Wakhi           ROXUN
  187 63 Bengali         SADA
  187 73 Ossetic         URS
b                      002
  187 61 Lahnda          SEFED
  187 62 Hindi           SEPHED
  187 58 Marathi         SEPHET
  187 59 Gujarati        SEFED, DHOHLU
b                      003
  187 03 Welsh N         GWYN
  187 04 Welsh C         GWYN
  187 05 Breton List     GWENN
  187 06 Breton SE       GUEN
  187 07 Breton ST       GWENN
b                      004
  187 81 Albanian Top    I-BARDHE
  187 80 Albanian T      I, E BARDHE
  187 83 Albanian K      I BARDH
  187 84 Albanian C      I-BARDH
  187 82 Albanian G      BARDH
  187 95 ALBANIAN        BARDH
b                      005
  187 69 Greek D         ASPROS
  187 67 Greek MD        ASPRAS
  187 68 Greek Mod       ASPROS
  187 66 Greek ML        ASPROS
b                      006
  187 71 Armenian Mod    SPITAK, CERMAK
  187 72 Armenian List   SBIDAG
b                      100
  187 56 Singhalese      SUDU
  187 57 Kashmiri        CHOTU
b                      200
c                         200  2  201
  187 22 Brazilian       BRANCO
  187 17 Sardinian N     BIANKU
  187 18 Sardinian L     BIANCU
  187 15 French Creole C BLA
  187 14 Walloon         BLANC
  187 12 Provencal       BLANC, ANCO
  187 20 Spanish         BLANCO
  187 23 Catalan         BLANCH
  187 10 Italian         BIANCO
  187 19 Sardinian C     BIANKU
  187 16 French Creole D BLA
  187 13 French          BLANC
b                      201
c                         200  2  201
c                         201  2  202
  187 21 Portuguese ST   BRANCO, CANDIDO, ALVO
b                      202
c                         201  2  202
  187 08 Rumanian List   ALB
  187 11 Ladin           ALV
  187 09 Vlach           ALBE
b                      203
c                         203  3  204
  187 91 SLOVENIAN P     BEL
  187 86 UKRAINIAN P     BILYJ
  187 43 Lusatian L      BELY
  187 44 Lusatian U      BELY
  187 93 MACEDONIAN P    BEL
  187 50 Polish          BIALY
  187 88 POLISH P        BIALY
  187 51 Russian         BELYJ
  187 85 RUSSIAN P       BELYJ
  187 54 Serbocroatian   BELO
  187 92 SERBOCROATIAN P BIO
  187 46 Slovak          BIELY
  187 89 SLOVAK P        BIELY
  187 90 CZECH P         BILY
  187 45 Czech           BILY
  187 87 BYELORUSSIAN P  BELY
  187 94 BULGARIAN P     B AL
  187 40 Lithuanian ST   BALTAS
  187 39 Lithuanian O    BALTAS
  187 41 Latvian         BALTS
  187 52 Macedonian      BEL
  187 47 Czech E         BILE
  187 49 Byelorussian    BELY
  187 48 Ukrainian       BILYJ
  187 53 Bulgarian       BJALO
b                      204
c                         203  3  204
  187 01 Irish A         BAN, GEAL
  187 02 Irish B         BAN, -INE, GEAL
b                      205
c                         205  3  206
  187 30 Swedish Up      VIT
  187 31 Swedish VL      VIT
  187 35 Icelandic ST    HVITR
  187 24 German ST       WEISS
  187 34 Riksmal         HVIT
  187 32 Swedish List    VIT
  187 33 Danish          HVID
  187 36 Faroese         HVITUR
  187 29 Frisian         WYT
  187 28 Flemish         WIT
  187 25 Penn. Dutch     WEISZ
  187 26 Dutch List      WIT
  187 27 Afrikaans       WIT
  187 38 Takitaki        WETI
  187 37 English ST      WHITE
  187 64 Nepali List     SETO
  187 65 Khaskura        SETO
  187 77 Tadzik          SAFED
  187 76 Persian List    SEFID
  187 78 Baluchi         SWETH
b                      206
c                         205  3  206
  187 74 Afghan          SPIN
  187 75 Waziri          SPIN
a 188 WHO
b                      200
c                         200  3  201
  188 70 Greek K         POIOS
  188 67 Greek MD        POIOS
  188 69 Greek D         POIOS
  188 68 Greek Mod       PYOS
  188 66 Greek ML        POIOS
  188 43 Lusatian L      CHTO
  188 50 Polish          KTO
  188 88 POLISH P        KTO
  188 51 Russian         KTO
  188 85 RUSSIAN P       KTO
  188 54 Serbocroatian   TKO
  188 92 SERBOCROATIAN P TKO
  188 93 MACEDONIAN P    KOJ
  188 46 Slovak          KTO
  188 89 SLOVAK P        KTO
  188 42 Slovenian       KEDU
  188 91 SLOVENIAN P     KDO
  188 86 UKRAINIAN P     CHTO
  188 90 CZECH P         KDO
  188 45 Czech           KDO
  188 87 BYELORUSSIAN P  CHTO
  188 94 BULGARIAN P     KOJ
  188 52 Macedonian      KOJ, KOJSTO
  188 47 Czech E         GDO
  188 49 Byelorussian    XTO
  188 48 Ukrainian       XTO, JAKYJ, KOTRYJ, TOJ SCO
  188 53 Bulgarian       KOJ
  188 55 Gypsy Gk        KON
  188 64 Nepali List     KUN, KO
  188 61 Lahnda          KON
  188 59 Gujarati        KON
  188 58 Marathi         KON
  188 63 Bengali         KE
  188 62 Hindi           KON
  188 60 Panjabi ST      KON
  188 65 Khaskura        KO
  188 56 Singhalese      KAVUDA
  188 30 Swedish Up      VEM, HOCKEN
  188 31 Swedish VL      VAM, HOKAN
  188 33 Danish          HVEM
  188 32 Swedish List    VEM
  188 34 Riksmal         HVEM
  188 35 Icelandic ST    HVER
  188 24 German ST       WER
  188 29 Frisian         HWA, HWA'T
  188 36 Faroese         HVOR
  188 25 Penn. Dutch     WAIIR
  188 38 Takitaki        HOESOEMA
  188 37 English ST      WHO
  188 81 Albanian Top    KUS, CILI
  188 82 Albanian G      KUSH
  188 84 Albanian C      KUS
  188 83 Albanian K      KUS
  188 80 Albanian T      KUSH
  188 95 ALBANIAN        KUSH
  188 07 Breton ST       PIV
  188 06 Breton SE       PIU
  188 05 Breton List     PIOU
  188 04 Welsh C         PWY
  188 03 Welsh N         PWY
  188 01 Irish A         CIA
  188 02 Irish B         CIA, CIACA
  188 40 Lithuanian ST   KAS
  188 39 Lithuanian O    KAS
  188 41 Latvian         KAS, KURS
  188 71 Armenian Mod    OV
  188 72 Armenian List   OV
  188 79 Wakhi           KUI
  188 22 Brazilian       QUEM
  188 21 Portuguese ST   QUEM
  188 17 Sardinian N     KIE
  188 18 Sardinian L     CHINI
  188 15 French Creole C KI MUN
  188 13 French          QUI
  188 16 French Creole D KIMUN
  188 14 Walloon         KI, QUI
  188 12 Provencal       QUE, QUAU, QU'
  188 20 Spanish         QUIEN
  188 23 Catalan         QUI
  188 10 Italian         CHI
  188 19 Sardinian C     KINI
  188 11 Ladin           CHI
  188 08 Rumanian List   CINE
  188 73 Ossetic         CI
  188 77 Tadzik          KI
  188 76 Persian List    KI
  188 78 Baluchi         KITHAN
  188 28 Flemish         WIE
  188 26 Dutch List      WIE
  188 27 Afrikaans       WIE
  188 44 Lusatian U      STO
  188 57 Kashmiri        KYAH
  188 09 Vlach           KARE
b                      201
c                         200  3  201
  188 74 Afghan          COK
  188 75 Waziri          TSOK
a 189 WIDE
b                      000
  189 73 Ossetic
b                      001
  189 57 Kashmiri        KHULA
  189 56 Singhalese      PALAL
  189 58 Marathi         RUNDE
  189 77 Tadzik          VASE
b                      002
  189 82 Albanian G      GJAN
  189 95 ALBANIAN        GJAN
  189 81 Albanian Top    I-GERE
  189 84 Albanian C      I-GER
  189 83 Albanian K      I GERE
  189 80 Albanian T      I, E GJERE
b                      003
  189 08 Rumanian List   LARG, LAT
  189 11 Ladin           LARG, LED
  189 19 Sardinian C     LARGU
  189 10 Italian         LARGO
  189 12 Provencal       LARG, ARGO, LARGE
  189 14 Walloon         LADJE
  189 16 French Creole D LAZ
  189 13 French          LARGE
  189 21 Portuguese ST   LARGO
  189 22 Brazilian       LARGO
  189 15 French Creole C LAZ
  189 17 Sardinian N     LARGU
  189 18 Sardinian L     LARGU
  189 09 Vlach           LARGU
b                      004
  189 20 Spanish         ANCHO
  189 23 Catalan         AMPLE
b                      005
  189 90 CZECH P         SIROKY
  189 43 Lusatian L      SYROKI
  189 44 Lusatian U      SEROKI
  189 93 MACEDONIAN P    SIROK
  189 50 Polish          SZEROKI
  189 88 POLISH P        SZEROKI
  189 51 Russian         SIROKIJ
  189 85 RUSSIAN P       SYROKIJ
  189 54 Serbocroatian   SIROK
  189 92 SERBOCROATIAN P SIROK
  189 46 Slovak          SIROKY
  189 89 SLOVAK P        SIROKY
  189 42 Slovenian       SROKO
  189 91 SLOVENIAN P     SIROK
  189 86 UKRAINIAN P     SYROKYJ
  189 45 Czech           SIROKY
  189 87 BYELORUSSIAN P  SYROKI
  189 94 BULGARIAN P     SIROK
  189 52 Macedonian      SI'ROK
  189 47 Czech E         SIROKE
  189 49 Byelorussian    SYROKI
  189 48 Ukrainian       SYROKYJ
  189 53 Bulgarian       SIROKO
b                      100
  189 55 Gypsy Gk        BULO
  189 59 Gujarati        POHLU
b                      200
c                         200  2  201
  189 29 Frisian         WIID
  189 28 Flemish         WYD
  189 26 Dutch List      WIJD, RUIM
  189 27 Afrikaans       WYDE
  189 37 English ST      WIDE
  189 32 Swedish List    VID
b                      201
c                         200  2  201
c                         201  2  202
  189 30 Swedish Up      VID, BRED
  189 31 Swedish VL      VI, BRE
  189 35 Icelandic ST    VIOR, BREIOR
  189 34 Riksmal         VID, BRED
  189 36 Faroese         VIDUR, BREIDUR
b                      202
c                         201  2  202
  189 24 German ST       BREIT
  189 33 Danish          BRED
  189 25 Penn. Dutch     BRAYT
  189 38 Takitaki        BRADI
b                      203
c                         203  2  204
  189 69 Greek D         FARDUS
  189 66 Greek ML        FARDUS
  189 70 Greek K         FARDUS
b                      204
c                         203  2  204
c                         204  2  205
  189 67 Greek MD        FARDUS, PLATUS
b                      205
c                         204  2  205
  189 68 Greek Mod       PLATIS
  189 40 Lithuanian ST   PLATUS
  189 39 Lithuanian O    PLATUS
  189 41 Latvian         PLATS
  189 07 Breton ST       LEDAN
  189 06 Breton SE       LEDAN
  189 05 Breton List     LEDAN, EC'HON, FRANK, LARK
  189 04 Welsh C         LLYDAN
  189 03 Welsh N         LLYDAN
  189 01 Irish A         LEATHAN
  189 02 Irish B         LEATHAN, FEIRRING
  189 71 Armenian Mod    LAYN ENDARJAK
  189 72 Armenian List   LINE
b                      206
c                         206  2  207
  189 65 Khaskura        GAJILO
b                      207
c                         206  2  207
c                         207  2  208
  189 64 Nepali List     CAURO, PHATILO, GAJILO
b                      208
c                         207  2  208
  189 61 Lahnda          CORA
  189 63 Bengali         COORA
  189 62 Hindi           CORA
  189 60 Panjabi ST      CORA
b                      209
c                         209  2  210
c                         209  3  212
  189 78 Baluchi         PRAH
  189 74 Afghan          PRAX
b                      210
c                         209  2  210
c                         210  2  211
  189 79 Wakhi           KESOD, FERUX
b                      211
c                         210  2  211
c                         211  3  212
  189 76 Persian List    GOSHAD, PAHN
b                      212
c                         209  3  212
c                         211  3  212
  189 75 Waziri          PLAN
a 190 WIFE
b                      000
  190 91 SLOVENIAN P
  190 86 UKRAINIAN P
  190 89 SLOVAK P
  190 92 SERBOCROATIAN P
  190 85 RUSSIAN P
  190 88 POLISH P
  190 44 Lusatian U
  190 93 MACEDONIAN P
  190 43 Lusatian L
  190 90 CZECH P
  190 87 BYELORUSSIAN P
  190 94 BULGARIAN P
b                      001
  190 58 Marathi         BAYKO
  190 73 Ossetic         BINOJNAG
  190 56 Singhalese      BIRIYA, GANI
  190 63 Bengali         BOU
  190 02 Irish B         CEILE
  190 79 Wakhi           JUMAUT, KEND, YUPKWOR
  190 57 Kashmiri        KOLAY
  190 61 Lahnda          KWAR
  190 55 Gypsy Gk        ROMNI  JUVLI
  190 74 Afghan          SEDZA
  190 41 Latvian         SIEVA
  190 08 Rumanian List   SOTIE, NEVASTA
  190 70 Greek K         SUDZUGOS
  190 75 Waziri          TABAR
  190 31 Swedish VL      TZARING
  190 60 Panjabi ST      VOTTI
b                      002
  190 38 Takitaki        WEFI
  190 37 English ST      WIFE
b                      003
  190 03 Welsh N         GWRAIG
  190 04 Welsh C         GWRAIG
  190 05 Breton List     GWREG, PRIED
  190 06 Breton SE       MOEZ, GROEG (DIAL.)
  190 07 Breton ST       GWREG
b                      004
  190 15 French Creole C MADAM
  190 16 French Creole D MADAM
b                      005
  190 27 Afrikaans       VROU, EGGENOTE, GADE
  190 28 Flemish         ECHTGENOOTE, VROUW
  190 25 Penn. Dutch     FRAW
  190 26 Dutch List      HUISVROUW, VROUW
  190 24 German ST       FRAU, GATTIN
  190 29 Frisian         FROU
  190 30 Swedish Up      HUSTRU, GUMMA
  190 32 Swedish List    HUSTRU, MAKA
b                      006
  190 64 Nepali List     AIMAI, JOI, STRI, SWASNI
  190 65 Khaskura        SWASHNI
b                      200
c                         200  2  201
c                         200  2  203
c                         200  3  205
c                         200  3  206
  190 71 Armenian Mod    KIN
  190 72 Armenian List   GIN
  190 01 Irish A         BEAN
  190 78 Baluchi         ZAL
  190 76 Persian List    ZAN
  190 77 Tadzik          ZAN, ZAVCA
  190 35 Icelandic ST    KONA, EIGINKONA
  190 34 Riksmal         KONE
  190 33 Danish          KONE
  190 36 Faroese         KONA
  190 66 Greek ML        GUNAIKA
  190 67 Greek MD        GUNAIKA
  190 68 Greek Mod       YINEKA
  190 69 Greek D         GUNAIKA
  190 42 Slovenian       ZENA
  190 51 Russian         ZENA
  190 50 Polish          ZONA
  190 47 Czech E         ZENA
  190 49 Byelorussian    ZONKA
  190 48 Ukrainian       DRUZYNA, ZINKA
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  3  205
c                         201  3  206
  190 46 Slovak          MANZELKA, ZENA
b                      202
c                         201  2  202
  190 45 Czech           MANZELKA
b                      203
c                         200  2  203
c                         201  2  203
c                         203  2  204
c                         203  3  205
c                         203  3  206
  190 54 Serbocroatian   ZENA, SUPRUGA
  190 52 Macedonian      ZENA, SUPRUG
b                      204
c                         203  2  204
  190 53 Bulgarian       SEPRUGA
b                      205
c                         200  3  205
c                         201  3  205
c                         203  3  205
c                         205  2  206
  190 81 Albanian Top    GRUA
  190 95 ALBANIAN        GRUJA
  190 83 Albanian K      GRUA
b                      206
c                         200  3  206
c                         201  3  206
c                         203  3  206
c                         205  2  206
c                         206  2  207
  190 80 Albanian T      GRUA, SHAGE
  190 82 Albanian G      GRUJA, ZOJA, SHOKJE
b                      207
c                         206  2  207
  190 84 Albanian C      SOKE
b                      208
c                         208  2  209
  190 14 Walloon         FEUME
  190 18 Sardinian L     FEMINA
b                      209
c                         208  2  209
c                         209  2  210
c                         209  2  211
  190 13 French          FEMME, EPOUSE
b                      210
c                         209  2  210
c                         210  2  211
  190 20 Spanish         ESPOSA
  190 22 Brazilian       ESPOSA
b                      211
c                         209  2  211
c                         210  2  211
c                         211  2  212
  190 10 Italian         MOGLIE, SPOSA
  190 21 Portuguese ST   MULHER CASADA, ESPOSA
b                      212
c                         211  2  212
  190 12 Provencal       MOUIE
  190 23 Catalan         MULLER, DONA
  190 19 Sardinian C     MULLERI
  190 11 Ladin           MUGLIER
  190 17 Sardinian N     MUTHTHERE
  190 09 Vlach           MBLARE
b                      213
c                         213  2  214
  190 59 Gujarati        PETNI
  190 62 Hindi           PETNI
b                      214
c                         213  2  214
c                         214  2  215
  190 39 Lithuanian O    PATI, ZMONA
b                      215
c                         214  2  215
  190 40 Lithuanian ST   ZMONA
a 191 WIND (BREEZE)
b                      001
  191 55 Gypsy Gk        BALVAL
  191 78 Baluchi         GO
  191 71 Armenian Mod    HOLM, K`AMI
  191 72 Armenian List   HOV
  191 59 Gujarati        PEWEN
  191 42 Slovenian       SAPA
  191 56 Singhalese      SULANGA
b                      002
  191 81 Albanian Top    ERE
  191 80 Albanian T      ERE
  191 83 Albanian K      EERE
  191 84 Albanian C      ER
  191 82 Albanian G      ERA
  191 95 ALBANIAN        ERA
b                      003
  191 70 Greek K         ANEMOS
  191 69 Greek D         ANEMOS
b                      004
  191 67 Greek MD        AERAS
  191 68 Greek Mod       AERAS
  191 66 Greek ML        AGERAS
b                      005
  191 01 Irish A         GAOTH
  191 02 Irish B         GAOTH, -AIOTHE
b                      200
c                         200  2  201
  191 31 Swedish VL      BLASVER  BLASVAR, BLAST
b                      201
c                         200  2  201
c                         201  2  202
c                         201  2  203
c                         201  3  204
c                         201  3  205
c                         201  3  206
  191 32 Swedish List    VIND, BLAST
b                      202
c                         201  2  202
c                         202  2  203
c                         202  3  204
c                         202  3  205
c                         202  3  206
  191 07 Breton ST       AVEL
  191 06 Breton SE       AUEL
  191 05 Breton List     AVEL, GWENT
  191 03 Welsh N         GWYNT, AWEL, CHWA
  191 37 English ST      WIND
  191 30 Swedish Up      VIND
  191 09 Vlach           VINTU
  191 18 Sardinian L     BENTU
  191 17 Sardinian N     VENTU
  191 15 French Creole C VA
  191 08 Rumanian List   VINT
  191 11 Ladin           SOFFEL, VENT
  191 19 Sardinian C     BENTU
  191 10 Italian         VENTO
  191 23 Catalan         VENT, AYRE
  191 20 Spanish         VIENTO
  191 12 Provencal       VENT, AURO
  191 14 Walloon         VINT
  191 16 French Creole D VA
  191 13 French          VENT
  191 04 Welsh C         GWYNT
  191 24 German ST       WIND
  191 35 Icelandic ST    VINDR
  191 34 Riksmal         VIND
  191 33 Danish          VIND
  191 36 Faroese         VINDUR
  191 29 Frisian         WYN
  191 28 Flemish         WIND
  191 25 Penn. Dutch     WINDT
  191 26 Dutch List      WIND
  191 27 Afrikaans       WIND
  191 21 Portuguese ST   VENTO
  191 22 Brazilian       VENTO
  191 38 Takitaki        WINTI
  191 91 SLOVENIAN P     VETER
  191 86 UKRAINIAN P     VITER
  191 88 POLISH P        WIATR
  191 51 Russian         VETER
  191 85 RUSSIAN P       VETER
  191 54 Serbocroatian   VETAR
  191 92 SERBOCROATIAN P VETAR
  191 46 Slovak          VIETOR
  191 89 SLOVAK P        VIETOR
  191 50 Polish          WIATR
  191 93 MACEDONIAN P    VETER
  191 44 Lusatian U      WETR
  191 43 Lusatian L      WETS
  191 90 CZECH P         VITR
  191 45 Czech           VITR
  191 87 BYELORUSSIAN P  VECER
  191 94 BULGARIAN P     V ATUR
  191 41 Latvian         VEJS
  191 40 Lithuanian ST   VEJAS
  191 39 Lithuanian O    VEJAS
  191 57 Kashmiri        WAV
  191 52 Macedonian      VETER
  191 60 Panjabi ST      VA
  191 47 Czech E         LUFT, VETR
  191 49 Byelorussian    VECER
  191 48 Ukrainian       VITER
  191 53 Bulgarian       VJATER
b                      203
c                         201  2  203
c                         202  2  203
c                         203  3  204
c                         203  3  205
c                         203  3  206
c                         203  3  400
  191 62 Hindi           VAYU, HEVA
  191 63 Bengali         BAIU, HAOA
b                      400
c                         203  3  400
  191 58 Marathi         HEVA
  191 61 Lahnda          HEWA
b                      204
c                         201  3  204
c                         202  3  204
c                         203  3  204
c                         204  3  205
c                         204  3  206
  191 65 Khaskura        BATAS
  191 64 Nepali List     BATAS
b                      205
c                         201  3  205
c                         202  3  205
c                         203  3  205
c                         204  3  205
c                         205  2  206
  191 76 Persian List    BAD
  191 75 Waziri          BOD
  191 74 Afghan          BAD
b                      206
c                         201  3  206
c                         202  3  206
c                         203  3  206
c                         204  3  206
c                         205  2  206
c                         206  2  207
  191 77 Tadzik          SAMOL, BOD
b                      207
c                         206  2  207
c                         207  2  208
  191 79 Wakhi           DUMA, SEMOL
b                      208
c                         207  2  208
  191 73 Ossetic         DYMGAE
a 192 WING
b                      000
  192 65 Khaskura
b                      001
  192 08 Rumanian List   ARIPA
  192 83 Albanian K      PENDE
  192 01 Irish A         SGIATHAN
  192 09 Vlach           PEANE
  192 77 Tadzik          BOL, KANOT
  192 23 Catalan         FILA, FLIERA, RENGLERA
  192 38 Takitaki        FLEI
  192 56 Singhalese      TATTA
  192 79 Wakhi           TUP
  192 29 Frisian         WJOK, WJUK
b                      002
  192 30 Swedish Up      VINGE
  192 31 Swedish VL      VINGA
  192 33 Danish          VINGE
  192 32 Swedish List    VINGE
  192 34 Riksmal         VINGE
  192 35 Icelandic ST    VAENGR
  192 36 Faroese         VONGUR
  192 37 English ST      WING
b                      003
  192 87 BYELORUSSIAN P  KRYLO
  192 45 Czech           KRIDLO
  192 90 CZECH P         KRIDLO
  192 43 Lusatian L      KSIDLO
  192 44 Lusatian U      KRIDLO
  192 93 MACEDONIAN P    KRILO
  192 50 Polish          SKRYDLO
  192 88 POLISH P        SKRZYDLO
  192 51 Russian         KRYLO
  192 85 RUSSIAN P       KRYLO
  192 54 Serbocroatian   KRILO
  192 92 SERBOCROATIAN P KRILO
  192 46 Slovak          KRIDLO
  192 89 SLOVAK P        KRIDLO
  192 42 Slovenian       KRELUTA
  192 91 SLOVENIAN P     KRILO
  192 86 UKRAINIAN P     KRYLO
  192 94 BULGARIAN P     KRILO
  192 52 Macedonian      KRILO
  192 47 Czech E         KRIDLO
  192 49 Byelorussian    KRYLO
  192 48 Ukrainian       KRYLO
  192 53 Bulgarian       KRILO
b                      004
  192 24 German ST       FLUGEL
  192 28 Flemish         VLEUGEL
  192 25 Penn. Dutch     FLIGGEL
  192 26 Dutch List      VLEUGEL
  192 27 Afrikaans       VLEUEL
b                      005
  192 63 Bengali         PAKHA, DANA
  192 55 Gypsy Gk        PHAK
  192 57 Kashmiri        PAKH
  192 64 Nepali List     PWAKH
  192 59 Gujarati        PAKH
  192 58 Marathi         PENKHE
  192 62 Hindi           PENKH
b                      006
  192 15 French Creole C ZEL
  192 14 Walloon         ELE
  192 16 French Creole D ZEL
  192 13 French          AILE
  192 18 Sardinian L     ALA
  192 17 Sardinian N     ALA
  192 11 Ladin           ELA
  192 19 Sardinian C     ALA
  192 10 Italian         ALA
  192 20 Spanish         ALA
  192 12 Provencal       ALO
  192 22 Brazilian       ASA
  192 21 Portuguese ST   AZA
b                      007
  192 07 Breton ST       ASKELL
  192 06 Breton SE       ASKEL
  192 05 Breton List     ASKELL
b                      008
  192 71 Armenian Mod    T`EW
  192 72 Armenian List   TEV
b                      009
  192 82 Albanian G      FLETA
  192 95 ALBANIAN        FLETA
b                      010
  192 61 Lahnda          PER
  192 60 Panjabi ST      PER
b                      011
  192 81 Albanian Top    KRA
  192 80 Albanian T      KRAH
  192 84 Albanian C      KRAX
b                      200
c                         200  3  201
c                         200  3  202
c                         200  3  203
  192 68 Greek Mod       FTERUGHA
  192 66 Greek ML        FTEROUGA
  192 70 Greek K         PTERON
  192 67 Greek MD        FTERO, FTEROUGA
  192 69 Greek D         FTERO
  192 04 Welsh C         ADEN
  192 03 Welsh N         ADAIN, ADEN
  192 02 Irish B         EITIOLLAIM
b                      201
c                         200  3  201
c                         201  2  202
c                         201  2  203
  192 40 Lithuanian ST   SPARNAS
  192 39 Lithuanian O    SPARNAS
  192 41 Latvian         SPARNS
b                      202
c                         200  3  202
c                         201  2  202
c                         202  2  203
  192 78 Baluchi         PHAR
  192 76 Persian List    PAR
b                      203
c                         200  3  203
c                         201  2  203
c                         202  2  203
c                         203  2  204
  192 75 Waziri          PAR, WAZAR
b                      204
c                         203  2  204
  192 74 Afghan          VAZAR
  192 73 Ossetic         BAZYR
a 193 WIPE
b                      000
  193 09 Vlach
  193 78 Baluchi
  193 82 Albanian G
  193 52 Macedonian
  193 95 ALBANIAN
b                      001
  193 25 Penn. Dutch     BUUTZ
  193 38 Takitaki        FIGI
  193 14 Walloon         HORBI
  193 43 Lusatian L      HUSERAS
  193 59 Gujarati        LUCHWU
  193 71 Armenian Mod    MAK`REL
  193 75 Waziri          MASHEL
  193 62 Hindi           MITANA
  193 56 Singhalese      PIHADANAWA
  193 18 Sardinian L     PULIRE
  193 73 Ossetic         SAERFYN
  193 61 Lahnda          SAF KEREN
  193 83 Albanian K      SFUNGARISIN
  193 19 Sardinian C     SPRUINAI
  193 55 Gypsy Gk        SULAVAV
  193 72 Armenian List   SURPEL
  193 24 German ST       WISCHEN
  193 37 English ST      WIPE
  193 57 Kashmiri        WOTHARUN
b                      002
  193 28 Flemish         VEEG
  193 29 Frisian         FEIJE
  193 26 Dutch List      VEGEN
  193 27 Afrikaans       AFDROE, AFDROOG, AFVEE(G)
b                      003
  193 68 Greek Mod       SFONGIZO
  193 70 Greek K         SFOUGGIDZO
b                      004
  193 51 Russian         VYTIRAT
  193 85 RUSSIAN P       VYTIRAT
  193 50 Polish          WYCIERAC
  193 88 POLISH P        WYCIERAC
  193 90 CZECH P         UTIRATI
  193 87 BYELORUSSIAN P  VYCIRAC
  193 45 Czech           UTIRATI
  193 94 BULGARIAN P     IZTRIVAM
  193 44 Lusatian U      WUTREC
  193 86 UKRAINIAN P     VYTYRATY
  193 53 Bulgarian       IZTRIVANE
  193 48 Ukrainian       ZYRATY, VYTYRATY
  193 49 Byelorussian    VYCIRAC'
  193 47 Czech E         UTRIT
  193 46 Slovak          UTRET
  193 89 SLOVAK P        UTIERAT
b                      005
  193 42 Slovenian       ABRESI
  193 91 SLOVENIAN P     BRISATI
  193 54 Serbocroatian   OBRISAC
  193 92 SERBOCROATIAN P BRISATI
  193 93 MACEDONIAN P    BRISAM
b                      006
  193 08 Rumanian List   A STERGE
  193 11 Ladin           TERDSCHER
b                      007
  193 81 Albanian Top    FSI, AOR. FSIVA
  193 84 Albanian C      FSIN
  193 80 Albanian T      ME FSHIRE
b                      008
  193 30 Swedish Up      TORKA (AV)
  193 31 Swedish VL      TORK
  193 36 Faroese         TURKA
  193 33 Danish          TORRE
  193 32 Swedish List    TORKA
  193 34 Riksmal         TORKE
  193 35 Icelandic ST    THURRKA
b                      009
  193 07 Breton ST       SEC'HAN
  193 06 Breton SE       SEHEIN
  193 05 Breton List     TORCHA, SEC'HA, DIZEC'HA
  193 04 Welsh C         SYCHU
  193 03 Welsh N         SYCHU
b                      010
  193 01 Irish A         CUIMILT
  193 02 Irish B         CUMAILIM, GLANAIM
b                      011
  193 79 Wakhi           VISUV, TUF DI-
  193 74 Afghan          VUCAVEL
b                      012
  193 40 Lithuanian ST   SLUOSTYTI
  193 39 Lithuanian O    NUSLUOSTYTI
  193 41 Latvian         SLAUCIT
b                      013
  193 76 Persian List    PAK KARDAN
  193 77 Tadzik          POK KARDAN
b                      014
  193 64 Nepali List     PUCHNU
  193 63 Bengali         POCHA
  193 58 Marathi         PUSNE.
  193 65 Khaskura        POCHHNU, GASNU
  193 60 Panjabi ST      PUJNA
b                      200
c                         200  2  201
  193 69 Greek D         SKOUPIDZO
b                      201
c                         200  2  201
c                         201  2  202
  193 67 Greek MD        KATHARIDZO, SKOUPIDZO
b                      202
c                         201  2  202
  193 66 Greek ML        KATHARIDZO
b                      203
c                         203  2  204
  193 13 French          ESSUYER
  193 15 French Creole C SWIYE  SUYE
  193 16 French Creole D SWIYE
  193 12 Provencal       EISSUGA
  193 22 Brazilian       ENXUGAR, ESFREGAR
  193 10 Italian         RASCIUGARE
b                      204
c                         203  2  204
c                         204  2  205
c                         204  2  206
  193 21 Portuguese ST   ALIMPAR, ENXUGAR, ESFREGAR
b                      205
c                         204  2  205
c                         205  2  206
  193 20 Spanish         LIMPIAR
b                      206
c                         204  2  206
c                         205  2  206
c                         206  2  207
  193 23 Catalan         NETEJAR, ESCURAR, LLIMPIAR
b                      207
c                         206  2  207
  193 17 Sardinian N     INNETTARE
a 194 WITH (ACCOMPANYING)
b                      001
  194 41 Latvian         AR
  194 76 Persian List    BA
  194 78 Baluchi         GO, GON, GON
  194 79 Wakhi           DU
  194 12 Provencal       EME
  194 95 ALBANIAN        ME
  194 38 Takitaki        NANGA
b                      002
  194 60 Panjabi ST      NAL
  194 61 Lahnda          NAL
b                      003
  194 71 Armenian Mod    HET
  194 72 Armenian List   HED
b                      004
  194 01 Irish A         LE
  194 02 Irish B         AG, LE, LEIS, RE, RIS
b                      005
  194 55 Gypsy Gk        BARABERI
  194 58 Marathi         BEROBER
b                      100
  194 77 Tadzik          AZ
  194 73 Ossetic         AED
b                      200
c                         200  3  201
  194 91 SLOVENIAN P     S
  194 86 UKRAINIAN P     Z
  194 94 BULGARIAN P     S
  194 87 BYELORUSSIAN P  Z
  194 45 Czech           S
  194 90 CZECH P         S
  194 43 Lusatian L      Z
  194 44 Lusatian U      Z
  194 93 MACEDONIAN P    S
  194 50 Polish          Z
  194 88 POLISH P        Z
  194 51 Russian         S
  194 85 RUSSIAN P       S
  194 54 Serbocroatian   SA
  194 92 SERBOCROATIAN P S
  194 46 Slovak          S, SO
  194 89 SLOVAK P        S
  194 56 Singhalese      SAMAGA
  194 57 Kashmiri        SUTY, SAN
  194 64 Nepali List     SANA, SAMET, SATH
  194 59 Gujarati        SATHE
  194 62 Hindi           SATH
  194 63 Bengali         SATH, SONGE
  194 65 Khaskura        SITA, SANG
  194 75 Waziri          SARA, DE...SARA, PA...SARA
  194 74 Afghan          DE...SERA
  194 52 Macedonian      SO
  194 47 Czech E         S, SE
  194 49 Byelorussian    Z
  194 48 Ukrainian       Z, IZ, ZI
  194 53 Bulgarian       S, SES
  194 42 Slovenian       ZMONO
b                      201
c                         200  3  201
  194 40 Lithuanian ST   SU
  194 39 Lithuanian O    SU
b                      202
c                         202  2  203
  194 69 Greek D         MADZI
  194 66 Greek ML        MADZI
b                      203
c                         202  2  203
c                         203  2  204
c                         203  3  205
  194 67 Greek MD        MADZI, ME
b                      204
c                         203  2  204
c                         204  3  205
  194 68 Greek Mod       ME
  194 70 Greek K         META
  194 81 Albanian Top    ME
  194 82 Albanian G      ME
  194 84 Albanian C      ME
  194 83 Albanian K      ME
  194 80 Albanian T      ME
b                      205
c                         203  3  205
c                         204  3  205
  194 30 Swedish Up      MED
  194 33 Danish          MED
  194 32 Swedish List    MED
  194 34 Riksmal         MED
  194 35 Icelandic ST    MEO
  194 24 German ST       MIT
  194 27 Afrikaans       MET
  194 26 Dutch List      MET, MEDE
  194 25 Penn. Dutch     MIT
  194 28 Flemish         MET
  194 29 Frisian         MEI
b                      206
c                         206  2  207
  194 16 French Creole D EPI
b                      207
c                         206  2  207
c                         207  2  208
  194 15 French Creole C EPI, EVE(K)
b                      208
c                         207  2  208
  194 13 French          AVEC
  194 14 Walloon         AVOU
  194 23 Catalan         AB
b                      209
c                         209  3  210
  194 37 English ST      WITH
  194 36 Faroese         VID
b                      210
c                         209  3  210
  194 31 Swedish VL      VA
b                      211
c                         211  3  212
  194 10 Italian         CON
  194 19 Sardinian C     KUN
  194 11 Ladin           CUN
  194 08 Rumanian List   CU
  194 20 Spanish         CON
  194 22 Brazilian       COM
  194 21 Portuguese ST   COM
  194 09 Vlach           KU
  194 17 Sardinian N     KIN
  194 18 Sardinian L     CUM
  194 07 Breton ST       GANT
  194 05 Breton List     GANT
  194 06 Breton SE       GET
b                      212
c                         211  3  212
  194 04 Welsh C         GYDA
  194 03 Welsh N         GYDA
a 195 WOMAN
b                      000
  195 82 Albanian G
b                      001
  195 34 Riksmal         DAME
  195 58 Marathi         BAI
  195 73 Ossetic         BINOJNAG
  195 03 Welsh N         DYNES, GWRAIG
  195 63 Bengali         MEELOK
  195 29 Frisian         MINSKE
  195 40 Lithuanian ST   MOTERISKE
  195 55 Gypsy Gk        ROMNI  JUVLI
  195 41 Latvian         SIEVIETE
  195 79 Wakhi           XUINUN, AURUT, OJIZ
b                      002
  195 28 Flemish         VROUW
  195 26 Dutch List      VROUW
  195 27 Afrikaans       VROU
b                      003
  195 38 Takitaki        OEMAN
  195 37 English ST      WOMAN
  195 25 Penn. Dutch     WEIBSMENSCH
  195 24 German ST       WEIB
b                      004
  195 09 Vlach           MBLARE
  195 20 Spanish         MUJER
  195 21 Portuguese ST   MULHER
  195 22 Brazilian       MULHER
b                      005
  195 50 Polish          KOBIETA
  195 88 POLISH P        KOBIETA
b                      006
  195 07 Breton ST       MAOUEZ
  195 06 Breton SE       MOEZ
  195 05 Breton List     MAOUEZ
b                      007
  195 75 Waziri          SHEZA
  195 74 Afghan          SEDZA
b                      200
c                         200  2  201
  195 18 Sardinian L     FEMINA
  195 17 Sardinian N     EMINA
  195 15 French Creole C FAM
  195 08 Rumanian List   FEMEIE
  195 12 Provencal       FEMO
  195 14 Walloon         FEUME
  195 13 French          FEMME
  195 16 French Creole D FAM
  195 19 Sardinian C     FEMMINA
b                      201
c                         200  2  201
c                         201  2  202
  195 11 Ladin           DUONNA, FEMNA
b                      202
c                         201  2  202
  195 10 Italian         DONNA
  195 23 Catalan         DONA
b                      203
c                         203  3  204
c                         203  3  205
  195 81 Albanian Top    GRUA
  195 80 Albanian T      GRUA
  195 83 Albanian K      GRUA
  195 84 Albanian C      GRUA
  195 95 ALBANIAN        GRUA
b                      204
c                         203  3  204
c                         204  3  205
  195 31 Swedish VL      KVINA, KVINFOLK  KVINFALK
  195 30 Swedish Up      KVINNA
  195 35 Icelandic ST    KONA, KVENNMAOR
  195 36 Faroese         KONA
  195 33 Danish          KVINDE
  195 32 Swedish List    KVINNA, DAM
  195 71 Armenian Mod    KIN
  195 72 Armenian List   GIN
  195 51 Russian         ZENSCINA
  195 85 RUSSIAN P       ZENSCINA
  195 54 Serbocroatian   ZENA
  195 92 SERBOCROATIAN P ZENA
  195 46 Slovak          ZENA
  195 89 SLOVAK P        ZENA
  195 42 Slovenian       ZENSKA
  195 91 SLOVENIAN P     ZENA
  195 86 UKRAINIAN P     ZINKA
  195 87 BYELORUSSIAN P  ZANCYNA
  195 45 Czech           ZENA
  195 90 CZECH P         ZENA
  195 43 Lusatian L      ZONA
  195 44 Lusatian U      ZONA
  195 93 MACEDONIAN P    ZENA
  195 94 BULGARIAN P     ZENA
  195 39 Lithuanian O    ZMONA
  195 69 Greek D         GUNAIKA
  195 67 Greek MD        GUNAIKA
  195 70 Greek K         GUNE
  195 66 Greek ML        GUNAIKA
  195 68 Greek Mod       YINEKA
  195 78 Baluchi         ZAL
  195 02 Irish B         BEAN
  195 01 Irish A         BEAN
  195 76 Persian List    ZAN
  195 77 Tadzik          ZAN
  195 52 Macedonian      ZENA
  195 47 Czech E         ZENA
  195 49 Byelorussian    ZANCYNA
  195 48 Ukrainian       ZINKA
  195 53 Bulgarian       ZENA
  195 04 Welsh C         BENYW
b                      205
c                         203  3  205
c                         204  3  205
c                         205  2  206
c                         205  2  209
c                         205  2  210
  195 57 Kashmiri        ZANANA, TRIY
b                      206
c                         205  2  206
c                         206  2  207
c                         206  2  209
c                         206  2  210
  195 60 Panjabi ST      ORET, TIVI
b                      207
c                         206  2  207
c                         207  2  208
c                         207  2  210
  195 62 Hindi           ORET, STRI
b                      208
c                         207  2  208
c                         208  2  210
  195 56 Singhalese      GANI, ISTRIYAK
  195 59 Gujarati        STRI
b                      209
c                         205  2  209
c                         206  2  209
c                         209  2  210
  195 61 Lahnda          TRIMMET
b                      210
c                         205  2  210
c                         206  2  210
c                         207  2  210
c                         208  2  210
c                         209  2  210
c                         210  2  211
  195 64 Nepali List     AIMAI, SWASNI, TIRIYA, STRI
b                      211
c                         210  2  211
  195 65 Khaskura        AIMAI
a 196 WOODS
b                      000
  196 52 Macedonian
  196 79 Wakhi
  196 87 BYELORUSSIAN P
  196 94 BULGARIAN P
  196 90 CZECH P
  196 43 Lusatian L
  196 44 Lusatian U
  196 93 MACEDONIAN P
  196 88 POLISH P
  196 85 RUSSIAN P
  196 92 SERBOCROATIAN P
  196 89 SLOVAK P
  196 91 SLOVENIAN P
  196 86 UKRAINIAN P
  196 55 Gypsy Gk
b                      001
  196 83 Albanian K      DHASO
  196 04 Welsh C         GALLT
  196 18 Sardinian L     ISCI
  196 56 Singhalese      KALE
  196 78 Baluchi         LADH
  196 54 Serbocroatian   SUMA
  196 84 Albanian C      VOSKU
  196 73 Ossetic         X"AED
b                      002
  196 36 Faroese         SKOG(V)UR
  196 33 Danish          SKOV
  196 32 Swedish List    SKOG
  196 34 Riksmal         SKOG
  196 35 Icelandic ST    SKOGR
  196 31 Swedish VL      SKOGA
  196 30 Swedish Up      SKOGAR
b                      003
  196 02 Irish B         FASCHOILL, -E, FEADH, FIODH, FORAOIR
  196 01 Irish A         COILLTE
b                      004
  196 09 Vlach           PEDURI
  196 08 Rumanian List   PADURE
b                      005
  196 71 Armenian Mod    ANTAR
  196 72 Armenian List   ANDAR
b                      006
  196 80 Albanian T      PYJE
  196 82 Albanian G      PYLLI
  196 81 Albanian Top    KORIE, PYL
  196 95 ALBANIAN        PYLLI
b                      007
  196 70 Greek K         DASOS
  196 67 Greek MD        DASOS
  196 69 Greek D         DASOS
  196 66 Greek ML        DASOS
  196 68 Greek Mod       DHASOS
b                      008
  196 03 Welsh N         COED
  196 07 Breton ST       KOAD
  196 06 Breton SE       KOED
  196 05 Breton List     KOAD
b                      200
c                         200  2  201
  196 42 Slovenian       DOVO
b                      201
c                         200  2  201
c                         201  2  202
  196 48 Ukrainian       LIS, DEREVO, DROVA
b                      202
c                         201  2  202
  196 46 Slovak          LES
  196 51 Russian         LES
  196 50 Polish          LAS
  196 45 Czech           LES
  196 47 Czech E         LES
  196 49 Byelorussian    LES
b                      203
c                         203  2  204
  196 53 Bulgarian       GORA
b                      204
c                         203  2  204
c                         204  2  205
  196 39 Lithuanian O    MISKAS, GIRIA
b                      205
c                         204  2  205
  196 41 Latvian         MEZA
  196 40 Lithuanian ST   MISKAS
b                      206
c                         206  2  207
  196 11 Ladin           GOD, SELVA
  196 12 Provencal       FOUREST, SEUVO
b                      207
c                         206  2  207
c                         207  2  208
  196 21 Portuguese ST   SELVA, FLORESTA, BOSQUE
  196 22 Brazilian       SELVA, FLORESTA, BOSQUE
b                      208
c                         207  2  208
  196 17 Sardinian N     BUSKU
  196 19 Sardinian C     BOSKU
  196 15 French Creole C GHWA BWA
  196 10 Italian         BOSCO
  196 23 Catalan         BOSCH
  196 20 Spanish         BOSQUE
  196 14 Walloon         BWES
  196 16 French Creole D BWE
  196 13 French          BOIS
b                      209
c                         209  2  210
  196 29 Frisian         BOSK
  196 27 Afrikaans       BOS
  196 26 Dutch List      BOSCH
  196 25 Penn. Dutch     BUSCH
  196 38 Takitaki        BOESI
b                      210
c                         209  2  210
c                         210  2  211
  196 28 Flemish         BOSCH, WOUD
b                      211
c                         210  2  211
  196 24 German ST       WALD
  196 37 English ST      WOODS
b                      212
c                         212  2  213
  196 64 Nepali List     BAN
  196 65 Khaskura        BAN
  196 57 Kashmiri        WAN
b                      213
c                         212  2  213
c                         213  2  214
  196 63 Bengali         JONGOL, BON
b                      214
c                         213  2  214
  196 62 Hindi           JENGEL
  196 60 Panjabi ST      JENGEL
  196 75 Waziri          ZANGAL
  196 61 Lahnda          JENGEL
  196 74 Afghan          DZANGAL
  196 77 Tadzik          CANGAL, BESA
  196 59 Gujarati        JENGEE
  196 76 Persian List    JANGAL
  196 58 Marathi         JENGEL
a 197 WORM
b                      000
  197 73 Ossetic
  197 65 Khaskura
b                      001
  197 75 Waziri          CHENJAI
  197 23 Catalan         CUCH, CUCA
  197 42 Slovenian       GLISTA
  197 04 Welsh C         MWYDYN
  197 56 Singhalese      PANUWA
  197 01 Irish A         PEIST
  197 79 Wakhi           PERIC
  197 63 Bengali         POKA
  197 41 Latvian         TARPS
b                      002
  197 68 Greek Mod       SKULIKI
  197 66 Greek ML        SKOULEKI
  197 70 Greek K         SKOLEKS
  197 67 Greek MD        SKOULEKI
  197 69 Greek D         SKOULEKI
b                      003
  197 71 Armenian Mod    ORD, CICU
  197 72 Armenian List   VORT
b                      004
  197 64 Nepali List     KIRO
  197 61 Lahnda          KIRA
  197 59 Gujarati        KIRO
  197 58 Marathi         KIDA
  197 62 Hindi           KIRA
  197 60 Panjabi ST      KIRA
b                      200
c                         200  2  201
  197 57 Kashmiri        KIRM, KYOMU
  197 40 Lithuanian ST   SLIEKAS, KIRMELE
  197 55 Gypsy Gk        KERMO
  197 39 Lithuanian O    KIRMELE
  197 78 Baluchi         KIRM
  197 74 Afghan          KIRM
  197 02 Irish B         CRUIMH
  197 80 Albanian T      KRIMB
  197 83 Albanian K      KRIMP
  197 84 Albanian C      KRIMP
  197 82 Albanian G      KARREMA, KRYMI
  197 77 Tadzik          KIRM
  197 81 Albanian Top    GELHISTER / KRIMP
  197 95 ALBANIAN        KRYMI
  197 76 Persian List    KERM
  197 03 Welsh N         PRYF GENWAIR
  197 05 Breton List     PRENV
  197 06 Breton SE       PREAN
  197 07 Breton ST       PRENV
  197 86 UKRAINIAN P     CERV AK
  197 91 SLOVENIAN P     CRV
  197 89 SLOVAK P        CERV
  197 46 Slovak          CERV
  197 92 SERBOCROATIAN P CRV
  197 54 Serbocroatian   CRV
  197 85 RUSSIAN P       CERV
  197 51 Russian         CERV
  197 88 POLISH P        CZERW
  197 93 MACEDONIAN P    CRVEC
  197 44 Lusatian U      CREW
  197 43 Lusatian L      CERW
  197 90 CZECH P         CERV
  197 45 Czech           CERV
  197 87 BYELORUSSIAN P  CARV AK
  197 94 BULGARIAN P     CERVEJ
  197 52 Macedonian      CRV
  197 47 Czech E         CERF
  197 49 Byelorussian    CARVJAK
  197 53 Bulgarian       CERVEJ
b                      201
c                         200  2  201
c                         201  2  202
  197 48 Ukrainian       CERV'JAK, XROBAK
b                      202
c                         201  2  202
  197 50 Polish          ROBAK
b                      203
c                         203  2  204
  197 32 Swedish List    MASK, LARV
  197 30 Swedish Up      MASK
  197 31 Swedish VL      MARK  MASK
  197 35 Icelandic ST    MAOKR
  197 34 Riksmal         MARK
b                      204
c                         203  2  204
c                         204  2  205
c                         204  2  206
  197 36 Faroese         MADKUR, ORMUR
b                      205
c                         204  2  205
c                         205  2  206
  197 24 German ST       WURM
  197 33 Danish          ORM
  197 29 Frisian         WJIRM
  197 28 Flemish         WORM
  197 25 Penn. Dutch     WAAREM
  197 26 Dutch List      WORM
  197 27 Afrikaans       WURM
  197 38 Takitaki        WOROM, WORM
  197 37 English ST      WORM
  197 13 French          VER
  197 16 French Creole D VE
  197 14 Walloon         VIER
  197 12 Provencal       VERME, TORO, CANIHO
  197 10 Italian         VERME
  197 19 Sardinian C     BREMI
  197 11 Ladin           VERM, VIERM
  197 08 Rumanian List   VIERME
  197 15 French Creole C VE TE
  197 17 Sardinian N     MERME
  197 18 Sardinian L     BERME
  197 09 Vlach           IERMU
b                      206
c                         204  2  206
c                         205  2  206
c                         206  2  207
  197 22 Brazilian       BICHO, VERME
b                      207
c                         206  2  207
c                         207  2  208
  197 21 Portuguese ST   BICHO, GUSANO
b                      208
c                         207  2  208
  197 20 Spanish         GUSANO
a 198 YE
b                      000
  198 25 Penn. Dutch
  198 26 Dutch List
b                      001
  198 34 Riksmal         DERE
  198 30 Swedish Up      NI
  198 38 Takitaki        OENOE
  198 74 Afghan          TASI
  198 68 Greek Mod       TULOGHUSAS
  198 48 Ukrainian       TY
  198 56 Singhalese      UMBALA
b                      002
  198 66 Greek ML        ESEIS
  198 70 Greek K         SEIS
  198 67 Greek MD        ESEIS, SEIS, SAS
  198 69 Greek D         ESEIS, SEIS
b                      003
  198 60 Panjabi ST      TUSI
  198 61 Lahnda          TUSSA
  198 57 Kashmiri        TOHI
  198 58 Marathi         TUMHI (INFORMAL), APEN (FORMAL)
  198 55 Gypsy Gk        TUMEN
  198 59 Gujarati        TEME
  198 63 Bengali         TUMI
  198 62 Hindi           TUM (INFORMAL), AP (FORMAL)
  198 64 Nepali List     TIMIHARU
  198 65 Khaskura        TIMIHARU
b                      004
  198 71 Armenian Mod    DUK`
  198 72 Armenian List   TOOK
b                      005
  198 36 Faroese         TIT
  198 35 Icelandic ST    THIO
b                      100
  198 79 Wakhi           SUST
  198 78 Baluchi         SHA
  198 75 Waziri          TUS, TOSE
b                      200
c                         200  3  201
  198 37 English ST      YE
  198 27 Afrikaans       JULLE, JUL
  198 28 Flemish         U, GY
  198 29 Frisian         JY, JO, JIM(ME)
  198 33 Danish          I
  198 32 Swedish List    I
  198 42 Slovenian       JE
  198 31 Swedish VL      JI
  198 40 Lithuanian ST   JUS
  198 39 Lithuanian O    JUS
  198 41 Latvian         JUS
  198 80 Albanian T      JU
  198 83 Albanian K      JU
  198 84 Albanian C      JU
  198 82 Albanian G      JU
  198 95 ALBANIAN        JU, JUVE
  198 81 Albanian Top    JURE
  198 09 Vlach           VOI
  198 18 Sardinian L     VOS
  198 17 Sardinian N     VOIS
  198 08 Rumanian List   VOI
  198 11 Ladin           VUS
  198 19 Sardinian C     BOSATRUS
  198 10 Italian         VOI
  198 23 Catalan         VOSALTRES
  198 20 Spanish         VOSOTROS
  198 12 Provencal       VOUS, VAUTRE
  198 13 French          VOUS
  198 14 Walloon         VOS
  198 21 Portuguese ST   VOS
  198 22 Brazilian       VOS
  198 91 SLOVENIAN P     VI
  198 86 UKRAINIAN P     VY
  198 45 Czech           VY
  198 90 CZECH P         VY
  198 43 Lusatian L      WY
  198 44 Lusatian U      WY
  198 93 MACEDONIAN P    VIE
  198 50 Polish          WY
  198 88 POLISH P        WY
  198 51 Russian         VY
  198 85 RUSSIAN P       VY
  198 54 Serbocroatian   VI
  198 92 SERBOCROATIAN P VI
  198 46 Slovak          VY
  198 89 SLOVAK P        VY
  198 87 BYELORUSSIAN P  VY
  198 94 BULGARIAN P     VIE
  198 52 Macedonian      VE, VIE
  198 47 Czech E         VI
  198 49 Byelorussian    VY
  198 53 Bulgarian       VIE
  198 07 Breton ST       C'HWI
  198 06 Breton SE       HUI
  198 05 Breton List     C'HOUI
  198 04 Welsh C         CHWI
  198 03 Welsh N         CHWI
  198 01 Irish A         SIBH
  198 02 Irish B         SIBH, SIBH-SE
  198 77 Tadzik          SUMO, SUMOEN
  198 76 Persian List    SHOMA
  198 73 Ossetic         CMAX
  198 24 German ST       IHR
b                      201
c                         200  3  201
  198 15 French Creole C ZOT
  198 16 French Creole D ZOT
a 199 YEAR
b                      001
  199 73 Ossetic         AFAED
  199 56 Singhalese      AVURUDDA
  199 63 Bengali         BOTSOR
  199 55 Gypsy Gk        BRES
  199 41 Latvian         GADS
  199 57 Kashmiri        WAHAR, WARIH
b                      002
  199 09 Vlach           ANU
  199 18 Sardinian L     ANNU
  199 17 Sardinian N     ANNU
  199 15 French Creole C LANE,   A(BOUND FORM)
  199 08 Rumanian List   AN
  199 11 Ladin           AN, ANNEDA
  199 19 Sardinian C     ANNU
  199 10 Italian         ANNO
  199 23 Catalan         ANY
  199 20 Spanish         ANO
  199 12 Provencal       AN, ANNADO
  199 14 Walloon         AN, ANNEYE
  199 16 French Creole D LANE
  199 13 French          AN
  199 21 Portuguese ST   ANNO
  199 22 Brazilian       ANO (ANNO)
b                      003
  199 89 SLOVAK P        ROK
  199 46 Slovak          ROK
  199 88 POLISH P        ROK
  199 50 Polish          ROK
  199 45 Czech           ROK
  199 90 CZECH P         ROK
  199 47 Czech E         ROK
  199 48 Ukrainian       RIK
b                      004
  199 30 Swedish Up      AR
  199 31 Swedish VL      AR
  199 24 German ST       JAHR
  199 35 Icelandic ST    AR
  199 34 Riksmal         AR
  199 32 Swedish List    AR
  199 33 Danish          AAR
  199 36 Faroese         AR
  199 29 Frisian         JIER
  199 28 Flemish         JAER
  199 25 Penn. Dutch     YAWR
  199 26 Dutch List      JAAR
  199 27 Afrikaans       JAAR
  199 38 Takitaki        JARI
  199 37 English ST      YEAR
b                      005
  199 92 SERBOCROATIAN P GODINA
  199 54 Serbocroatian   GODINA
  199 51 Russian         GOD
  199 93 MACEDONIAN P    GODINA
  199 87 BYELORUSSIAN P  HOD
  199 94 BULGARIAN P     GODINA
  199 52 Macedonian      GODINA
  199 49 Byelorussian    HOD
  199 53 Bulgarian       GODINA
b                      006
  199 02 Irish B         BLIADHAN
  199 01 Irish A         BLIADHAIN
  199 03 Welsh N         BLWYDDYN, BLWYDD
  199 04 Welsh C         BLWYDDYN
  199 05 Breton List     BLOAZ
  199 06 Breton SE       BLE
  199 07 Breton ST       BLOAZ
b                      007
  199 70 Greek K         ETOS
  199 81 Albanian Top    VIT
  199 80 Albanian T      MOT, VIT
  199 83 Albanian K      VIT
  199 84 Albanian C      VIT
  199 82 Albanian G      MOTI, VITI
  199 95 ALBANIAN        VITI
b                      008
  199 86 UKRAINIAN P     LITA
  199 91 SLOVENIAN P     LETO
  199 42 Slovenian       LETO
  199 85 RUSSIAN P       LETA
  199 43 Lusatian L      LETO
  199 44 Lusatian U      LETO
b                      009
  199 40 Lithuanian ST   METAI
  199 39 Lithuanian O    METAI (PL.)
b                      010
  199 76 Persian List    SAL
  199 77 Tadzik          SOL
  199 78 Baluchi         SAL
  199 79 Wakhi           SOL
b                      011
  199 74 Afghan          KAL
  199 75 Waziri          KOL
b                      012
  199 71 Armenian Mod    TARI
  199 72 Armenian List   DARI
b                      013
  199 69 Greek D         CHRONOS
  199 67 Greek MD        CHRONOS
  199 68 Greek Mod       KHRONOS
  199 66 Greek ML        CHRONOS
b                      200
c                         200  2  201
  199 58 Marathi         VERSE
b                      201
c                         200  2  201
c                         201  2  202
  199 62 Hindi           SAL, VERS
  199 59 Gujarati        VERES, SAL, (VERS)
  199 64 Nepali List     BARSA, SAL
b                      202
c                         201  2  202
  199 65 Khaskura        SAL
  199 60 Panjabi ST      SAL
  199 61 Lahnda          SAL
a 200 YELLOW
b                      000
  200 84 Albanian C
b                      001
  200 73 Ossetic         BUR
  200 71 Armenian Mod    DELIN
  200 63 Bengali         HOLDE
  200 56 Singhalese      KAHA
  200 57 Kashmiri        LEDORU
  200 42 Slovenian       NUMENO
  200 55 Gypsy Gk        SARI
  200 72 Armenian List   TEKHIN
b                      002
  200 07 Breton ST       MELEN
  200 06 Breton SE       MELEN
  200 05 Breton List     MELEN
  200 04 Welsh C         MELYN
  200 03 Welsh N         MELYN
b                      003
  200 20 Spanish         AMARILLO
  200 21 Portuguese ST   AMARELLO
  200 22 Brazilian       AMARELO (AMARELLO)
b                      004
  200 01 Irish A         BUIDHE
  200 02 Irish B         BUIDHE
b                      005
  200 18 Sardinian L     GROGU
  200 17 Sardinian N     GROGU
  200 23 Catalan         GROCH
  200 19 Sardinian C     GROGU
b                      006
  200 68 Greek Mod       KITRINOS
  200 66 Greek ML        KITRINOS
  200 70 Greek K         KITRINON
  200 67 Greek MD        KITRINOS
  200 69 Greek D         KITRINO
b                      007
  200 81 Albanian Top    I-VERDHE
  200 80 Albanian T      I, E VERDHE
  200 83 Albanian K      I VERDHE
  200 82 Albanian G      VERDH
  200 95 ALBANIAN        VERDH
b                      200
c                         200  3  201
  200 37 English ST      YELLOW
  200 30 Swedish Up      GUL
  200 31 Swedish VL      GUL
  200 24 German ST       GELB
  200 35 Icelandic ST    GULR
  200 34 Riksmal         GUL
  200 32 Swedish List    GUL
  200 33 Danish          GULT
  200 36 Faroese         GULUR
  200 29 Frisian         GEEL
  200 28 Flemish         GEEL
  200 25 Penn. Dutch     GAYL
  200 26 Dutch List      GEEL
  200 27 Afrikaans       GEEL
  200 38 Takitaki        GEELI
  200 86 UKRAINIAN P     ZOUTYJ
  200 91 SLOVENIAN P     ZOLT
  200 87 BYELORUSSIAN P  ZOUTY
  200 45 Czech           ZLUTY
  200 90 CZECH P         ZLUTY
  200 43 Lusatian L      ZOLTY
  200 44 Lusatian U      ZOLTY
  200 93 MACEDONIAN P    ZOLT
  200 50 Polish          ZOLTY
  200 88 POLISH P        ZOLTY
  200 51 Russian         ZELTYJ
  200 85 RUSSIAN P       ZOLTYJ
  200 54 Serbocroatian   ZUT
  200 92 SERBOCROATIAN P ZUT
  200 46 Slovak          ZLTY
  200 89 SLOVAK P        ZLTY
  200 94 BULGARIAN P     ZULT
  200 41 Latvian         DZELTENS
  200 40 Lithuanian ST   GELTONAS
  200 39 Lithuanian O    GELTONAS
  200 52 Macedonian      ZOLT
  200 47 Czech E         ZLUTE
  200 49 Byelorussian    ZOWTY
  200 48 Ukrainian       ZOVTYJ
  200 53 Bulgarian       ZELTO
  200 79 Wakhi           ZERT
  200 78 Baluchi         ZARD, ZHALOKH
  200 74 Afghan          ZER
  200 75 Waziri          ZYER
  200 77 Tadzik          ZARD
  200 76 Persian List    ZARD
b                      201
c                         200  3  201
  200 09 Vlach           GALBINE
  200 15 French Creole C ZON
  200 12 Provencal       JAUNE, AUNO
  200 13 French          JAUNE
  200 16 French Creole D ZON
  200 14 Walloon         DJENE
  200 10 Italian         GIALLO
  200 08 Rumanian List   GALBEN
  200 11 Ladin           MELLEN, GIALV
b                      202
c                         202  3  203
c                         202  3  204
  200 64 Nepali List     PAHELO
  200 65 Khaskura        PAHILO
b                      203
c                         202  3  203
c                         203  3  204
  200 61 Lahnda          PILA
  200 59 Gujarati        PILU
  200 62 Hindi           PILA
b                      204
c                         202  3  204
c                         203  3  204
  200 60 Panjabi ST      PILLA
  200 58 Marathi         PIVLA""".split("\n")
# }}}

# Dyen Codes {{{
# conversion Dyen form to Ludewig id
meaning2id = {"ALL":1,
"AND":2,
"ANIMAL":3,
"ASHES":4,
"AT":5,
"BACK":6,
"BAD":7,
"BARK (OF A TREE)":8,
"BECAUSE":9,
"BELLY":10,
"BIG":11,
"BIRD":12,
"BLACK":14,
"BLOOD":15,
"BONE":17,
"CHILD (YOUNG)":21,
"CLOUD":22,
"COLD (WEATHER)":23,
"DAY (NOT NIGHT)":27,
"DIRTY":30,
"DOG":31,
"DRY (SUBSTANCE)":33,
"DULL (KNIFE)":34,
"DUST":35,
"EAR":36,
"EARTH (SOIL)":37,
"EGG":39,
"EYE":40,
"FAR":42,
"FAT (SUBSTANCE)":43,
"FATHER":44,
"FEATHER (LARGE)":46,
"FEW":47,
"FIRE":50,
"FISH":51,
"FIVE":52,
"FLOWER":55,
"FOG":57,
"FOOT":58,
"FOUR":59,
"FRUIT":61,
"GOOD":64,
"GRASS":65,
"GREEN":66,
"GUTS":67,
"HAIR":68,
"HAND":69,
"HE":70,
"HEAD":71,
"HEART":73,
"HEAVY":74,
"HERE":75,
"HOLD (IN HAND)":77,
"HOW":79,
"HUSBAND":81,
"I":82,
"ICE":83,
"IF":84,
"IN":85,
"KNOW (FACTS)":88,
"LAKE":89,
"LEAF":91,
"LEFT (HAND)":92,
"LEG":93,
"LIVER":96,
"LONG":97,
"LOUSE":98,
"MAN (MALE)":99,
"MANY":100,
"MEAT (FLESH)":101,
"MOTHER":103,
"MOUNTAIN":104,
"MOUTH":105,
"NAME":106,
"NARROW":107,
"NEAR":108,
"NECK":109,
"NEW":110,
"NIGHT":111,
"NOSE":112,
"NOT":113,
"OLD":114,
"ONE":115,
"OTHER":116,
"PERSON":117,
"RED":122,
"RIGHT (CORRECT)":123,
"RIGHT (HAND)":124,
"RIVER":125,
"ROAD":126,
"ROOT":127,
"ROPE":128,
"ROTTEN (LOG)":129,
"RUB":131,
"SALT":132,
"SAND":133,
"SCRATCH (ITCH)":135,
"SEA (OCEAN)":136,
"SEED":138,
"SHARP (KNIFE)":140,
"SHORT":141,
"SKIN (OF PERSON)":144,
"SKY":145,
"SMALL":147,
"SMOKE":149,
"SMOOTH":150,
"SNAKE":151,
"SNOW":152,
"SOME":153,
"STAR":159,
"STICK (OF WOOD)":160,
"STONE":161,
"STRAIGHT":162,
"SUN":164,
"TAIL":167,
"THAT":168,
"THERE":169,
"THEY":170,
"THICK":171,
"THIN":172,
"THIS":174,
"THOU":175,
"THREE":176,
"TO BITE":13,
"TO BLOW (WIND)":16,
"TO BREATHE":19,
"TO BURN (INTRANSITIVE)":20,
"TO COME":24,
"TO COUNT":25,
"TO CUT":26,
"TO DIE":28,
"TO DIG":29,
"TO DRINK":32,
"TO EAT":38,
"TO FALL (DROP)":41,
"TO FEAR":45,
"TO FIGHT":48,
"TO FLOAT":53,
"TO FLOW":54,
"TO FLY":56,
"TO FREEZE":60,
"TO GIVE":63,
"TO HEAR":72,
"TO HIT":76,
"TO HUNT (GAME)":80,
"TO KILL":86,
"TO LAUGH":90,
"TO LIE (ON SIDE)":94,
"TO LIVE":95,
"TO PLAY":118,
"TO PULL":119,
"TO PUSH":120,
"TO RAIN":121,
"TO SAY":134,
"TO SEE":137,
"TO SEW":139,
"TO SING":142,
"TO SIT":143,
"TO SLEEP":146,
"TO SMELL (PERCEIVE ODOR)":148,
"TO SPIT":154,
"TO SPLIT":155,
"TO SQUEEZE":156,
"TO STAB (OR STICK)":157,
"TO STAND":158,
"TO SUCK":163,
"TO SWELL":165,
"TO SWIM":166,
"TO THINK":173,
"TO THROW":177,
"TO TIE":178,
"TO TURN (VEER)":182,
"TO VOMIT":184,
"TO WALK":185,
"TO WASH":187,
"TONGUE":179,
"TOOTH (FRONT)":180,
"TREE":181,
"TWO":183,
"WARM (WEATHER)":186,
"WATER":188,
"WE":189,
"WET":190,
"WHAT":191,
"WHEN":192,
"WHERE":193,
"WHITE":194,
"WHO":195,
"WIDE":196,
"WIFE":197,
"WIND (BREEZE)":198,
"WING":199,
"WIPE":200,
"WITH (ACCOMPANYING)":201,
"WOMAN":202,
"WOODS":203,
"WORM":204,
"YE":205,
"YEAR":206,
"YELLOW":207,
# forms not in Dyen
"BREAST":18,
"FINGERNAIL":49,
"FULL":62,
"HORN":78,
"KNEE":87,
"MOON":102,
"ROUND":130,
}
# }}}

# Ludewig Codes {{{
id_list = [("1", "ALL"),
("2", "AND"),
("3", "ANIMAL"),
("4", "ASHES"),
("5", "AT"),
("6", "BACK (PERSON'S)"),
("7", "BAD (UNSUITABLE, DELETERIOUS)"),
("8", "BARK (OF A TREE)"),
("9", "BECAUSE"),
("10", "BELLY"),
("11", "BIG"),
("12", "BIRD"),
("13", "TO BITE"),
("14", "BLACK"),
("15", "BLOOD"),
("16", "TO BLOW (WIND)"),
("17", "BONE"),
("18", "BREAST"),
("19", "TO BREATHE"),
("20", "TO BURN (INTR.)"),
("21", "CHILD (YOUNG)"),
("22", "CLOUD"),
("23", "COLD (WEATHER)"),
("24", "TO COME"),
("25", "TO COUNT"),
("26", "TO CUT"),
("27", "DAY (NOT NIGHT)"),
("28", "TO DIE"),
("29", "TO DIG"),
("30", "DIRTY"),
("31", "DOG"),
("32", "TO DRINK"),
("33", "DRY (SUBSTANCE)"),
("34", "DULL (KNIFE)"),
("35", "DUST"),
("36", "EAR"),
("37", "EARTH (SOIL)"),
("38", "TO EAT"),
("39", "EGG"),
("40", "EYE"),
("41", "TO FALL (DROP)"),
("42", "FAR"),
("43", "FAT (SUBSTANCE)"),
("44", "FATHER"),
("45", "TO FEAR"),
("46", "FEATHER (LARGE)"),
("47", "FEW (NOT MANY)"),
("48", "TO FIGHT"),
("49", "FINGERNAIL"),
("50", "FIRE"),
("51", "FISH"),
("52", "FIVE"),
("53", "TO FLOAT"),
("54", "TO FLOW"),
("55", "FLOWER"),
("56", "TO FLY"),
("57", "FOG"),
("58", "FOOT"),
("59", "FOUR"),
("60", "TO FREEZE"),
("61", "FRUIT"),
("62", "FULL"),
("63", "TO GIVE"),
("64", "GOOD"),
("65", "GRASS"),
("66", "GREEN"),
("67", "GUTS"),
("68", "HAIR (OF HEAD)"),
("69", "HAND"),
("70", "HE"),
("71", "HEAD"),
("72", "TO HEAR"),
("73", "HEART"),
("74", "HEAVY"),
("75", "HERE"),
("76", "TO HIT (STRIKE, WITH FIST)"),
("77", "HOLD (IN HAND)"),
("78", "HORN"),
("79", "HOW?"),
("80", "TO HUNT (GAME)"),
("81", "HUSBAND"),
("82", "I"),
("83", "ICE"),
("84", "IF"),
("85", "IN"),
("86", "TO KILL"),
("87", "KNEE"),
("88", "KNOW (FACTS)"),
("89", "LAKE"),
("90", "TO LAUGH"),
("91", "LEAF"),
("92", "LEFT (HAND, SIDE)"),
("93", "LEG"),
("94", "TO LIE (ON SIDE)"),
("95", "TO LIVE (BE ALIVE)"),
("96", "LIVER"),
("97", "LONG (in space)"),
("98", "LOUSE"),
("99", "MAN (MALE HUMAN)"),
("100", "MANY"),
("101", "MEAT (FLESH)"),
("102", "MOON"),
("103", "MOTHER"),
("104", "MOUNTAIN"),
("105", "MOUTH"),
("106", "NAME"),
("107", "NARROW"),
("108", "NEAR"),
("109", "NECK"),
("110", "NEW"),
("111", "NIGHT"),
("112", "NOSE"),
("113", "NOT"),
("114", "OLD (THING)"),
("115", "ONE"),
("116", "OTHER"),
("117", "PERSON (HUMAN BEING)"),
("118", "TO PLAY (GAMES)"),
("119", "TO PULL"),
("120", "TO PUSH"),
("121", "TO RAIN"),
("122", "RED"),
("123", "RIGHT (CORRECT)"),
("124", "RIGHT (HAND, SIDE)"),
("125", "RIVER"),
("126", "ROAD (PATH)"),
("127", "ROOT"),
("128", "ROPE"),
("129", "ROTTEN (LOG)"),
("130", "ROUND"),
("131", "RUB"),
("132", "SALT"),
("133", "SAND"),
("134", "TO SAY"),
("135", "SCRATCH (ITCH)"),
("136", "SEA (OCEAN)"),
("137", "TO SEE"),
("138", "SEED"),
("139", "TO SEW"),
("140", "SHARP (KNIFE)"),
("141", "SHORT"),
("142", "TO SING"),
("143", "TO SIT"),
("144", "SKIN (OF PERSON)"),
("145", "SKY"),
("146", "TO SLEEP"),
("147", "SMALL"),
("148", "TO SMELL (PERCEIVE ODOR)"),
("149", "SMOKE (OF FIRE)"),
("150", "SMOOTH"),
("151", "SNAKE"),
("152", "SNOW"),
("153", "SOME"),
("154", "TO SPIT"),
("155", "TO SPLIT"),
("156", "TO SQUEEZE"),
("157", "TO STAB (OR STICK)"),
("158", "TO STAND (PERSON)"),
("159", "STAR"),
("160", "STICK (OF WOOD)"),
("161", "STONE"),
("162", "STRAIGHT"),
("163", "TO SUCK"),
("164", "SUN"),
("165", "TO SWELL"),
("166", "TO SWIM"),
("167", "TAIL (LAND ANIMAL)"),
("168", "THAT"),
("169", "THERE"),
("170", "THEY"),
("171", "THICK"),
("172", "THIN"),
("173", "TO THINK (cogitate)"),
("174", "THIS"),
("175", "THOU/YOU (sg.)"),
("176", "THREE"),
("177", "TO THROW"),
("178", "TO TIE"),
("179", "TONGUE"),
("180", "TOOTH (FRONT)"),
("181", "TREE"),
("182", "TO TURN (VEER)"),
("183", "TWO"),
("184", "TO VOMIT"),
("185", "TO WALK"),
("186", "WARM (WEATHER)"),
("187", "TO WASH"),
("188", "WATER"),
("189", "WE"),
("190", "WET (OBJECTS)"),
("191", "WHAT?"),
("192", "WHEN?"),
("193", "WHERE?"),
("194", "WHITE"),
("195", "WHO?"),
("196", "WIDE"),
("197", "WIFE"),
("198", "WIND (BREEZE)"),
("199", "WING"),
("200", "TO WIPE"),
("201", "WITH (ACCOMPANYING)"),
("202", "WOMAN"),
("203", "WOODS"),
("204", "WORM"),
("205", "YE (pl.)"),
("206", "YEAR"),
("207", "YELLOW")]
# }}}

if __name__ == "__main__":
    write_csv()
    write_doubtful()

# vim:fdm=marker