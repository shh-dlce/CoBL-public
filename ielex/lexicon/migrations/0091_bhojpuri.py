# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations


def forwards_func(apps, schema_editor):
    '''
    I accidentially deleted a citation in production.
    This migration adds it again.
    '''
    # Models to work with:
    Language = apps.get_model('lexicon', 'Language')
    Lexeme = apps.get_model('lexicon', 'Lexeme')
    # Data to work with:
    source = Language.objects.get(ascii_name='Bhojpuri')
    target = Language.objects.get(ascii_name='BhojpuriNew')
    # Mapping meaning.id -> Lexeme
    mIdLexemeMap = {}
    for l in Lexeme.objects.filter(language=target).all():
        mIdLexemeMap[l.meaning_id] = l
    # Replacing lexemes in target:
    for l in Lexeme.objects.filter(language=source).all():
        mId = l.meaning_id
        if mId in mIdLexemeMap:
            mIdLexemeMap[mId].delete()
            l.language_id = target.id
            l.save()


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [('lexicon', '0090_remove_meaninglist_data')]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]