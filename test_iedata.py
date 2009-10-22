"""
sets to test:

MOTHER

c                         200  3  204
b                      205
c                         204  2  205
  097 65 Khaskura        AMA
  097 64 Nepali List     AMA

Khaskura and Nepali should have the same class, and it should be cognate class
A if we're conflating doubtful classes.

Likewise,

3  Albanian G    AMA, MOMA, NANA    B
2  Albanian C    MEM                A
4  Albanian K    MEME               A
5  Albanian T    NENE               A <- should be B
6  Albanian Top  NENE               B

"""

# FATHER

CODES = [001, 002, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 400, 210,
        211, 212, 213, 214, 215, 216, 217]

# equiv {{{
equiv = """\
200  2  201
200  2  202
200  2  206
200  2  201
201  3  202
201  3  203
201  3  204
201  3  205
201  3  206
201  3  207
201  3  208
201  3  209
201  3  400
200  2  202
201  3  202
202  2  203
202  3  204
202  3  205
202  3  206
202  3  207
202  3  208
202  3  209
202  3  400
201  3  203
202  2  203
203  3  204
203  3  205
203  3  206
203  3  207
203  3  208
203  3  209
203  3  400
201  3  204
202  3  204
203  3  204
204  3  205
204  3  206
204  3  207
204  3  208
204  3  209
204  3  400
201  3  205
202  3  205
203  3  205
204  3  205
205  3  206
205  3  207
205  3  208
205  3  209
205  3  400
200  2  206
201  3  206
202  3  206
203  3  206
204  3  206
205  3  206
206  2  207
206  3  208
206  3  209
206  3  400
201  3  207
202  3  207
203  3  207
204  3  207
205  3  207
206  2  207
207  3  208
207  3  209
207  3  400
201  3  208
202  3  208
203  3  208
204  3  208
205  3  208
206  3  208
207  3  208
208  3  209
208  3  400
201  3  209
202  3  209
203  3  209
204  3  209
205  3  209
206  3  209
207  3  209
208  3  209
209  3  400
209  2  210
209  2  211
209  2  213
209  2  216
201  3  400
202  3  400
203  3  400
204  3  400
205  3  400
206  3  400
207  3  400
208  3  400
209  3  400
209  2  210
210  2  211
210  2  213
210  2  216
209  2  211
210  2  211
211  3  212
211  2  213
211  3  214
211  3  215
211  2  216
211  3  212
212  3  213
212  3  214
212  3  215
209  2  213
210  2  213
211  2  213
212  3  213
213  3  214
213  3  215
213  2  216
211  3  214
212  3  214
213  3  214
214  3  215
211  3  215
212  3  215
213  3  215
214  3  215
209  2  216
210  2  216
211  2  216
213  2  216
216  3  217
216  3  217""" #}}}


sets = {}
for line in equiv.split("\n"):
    row = [int(i) for i in line.strip().split()]
    if row[1] == 2:
        set1, set2 = row[0], row[2]
        if set1 in sets:
            set1 = sets[set1]
        sets[set2] = set1
print sets


sets = {}
for line in equiv.split("\n"):
    row = [int(i) for i in line.strip().split()]
    if row[1] == 3:
        set1, set2 = row[0], row[2]
        if set1 in sets:
            set1 = sets[set1]
        sets[set2] = set1
print sets



# vim:fdm=marker
