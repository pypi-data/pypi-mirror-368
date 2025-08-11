# flake8: noqa
# type: ignore
# Generated from verse/ql/grammar/VerseQLParser.g4 by ANTLR 4.13.0
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,52,427,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,
        2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,2,31,7,31,2,32,7,32,2,33,
        7,33,2,34,7,34,2,35,7,35,2,36,7,36,2,37,7,37,2,38,7,38,2,39,7,39,
        2,40,7,40,2,41,7,41,2,42,7,42,2,43,7,43,1,0,1,0,1,0,1,1,1,1,1,1,
        1,2,1,2,1,2,1,3,1,3,1,3,1,4,1,4,1,4,1,5,1,5,1,5,1,6,1,6,1,6,1,7,
        1,7,5,7,112,8,7,10,7,12,7,115,9,7,1,7,1,7,1,7,1,7,1,7,1,7,5,7,123,
        8,7,10,7,12,7,126,9,7,1,7,1,7,3,7,130,8,7,1,8,1,8,1,8,1,8,1,8,1,
        8,1,8,3,8,139,8,8,1,9,1,9,1,9,1,10,1,10,1,10,1,11,1,11,1,11,1,11,
        5,11,151,8,11,10,11,12,11,154,9,11,1,11,3,11,157,8,11,1,12,1,12,
        1,12,3,12,162,8,12,1,13,1,13,1,13,1,14,1,14,1,14,5,14,170,8,14,10,
        14,12,14,173,9,14,1,14,3,14,176,8,14,1,15,1,15,1,15,1,16,1,16,1,
        16,1,17,1,17,1,17,1,17,1,17,1,17,1,17,1,17,1,17,1,17,1,17,1,17,1,
        17,1,17,1,17,1,17,1,17,1,17,3,17,202,8,17,1,17,1,17,1,17,1,17,1,
        17,5,17,209,8,17,10,17,12,17,212,9,17,1,17,1,17,1,17,1,17,3,17,218,
        8,17,1,17,1,17,1,17,1,17,1,17,1,17,5,17,226,8,17,10,17,12,17,229,
        9,17,1,18,1,18,1,18,1,18,1,18,3,18,236,8,18,1,19,1,19,1,19,1,19,
        1,20,1,20,1,20,5,20,245,8,20,10,20,12,20,248,9,20,1,20,3,20,251,
        8,20,1,21,1,21,3,21,255,8,21,1,22,1,22,1,22,1,23,1,23,1,23,5,23,
        263,8,23,10,23,12,23,266,9,23,1,23,3,23,269,8,23,1,24,1,24,1,24,
        1,24,1,25,1,25,3,25,277,8,25,1,25,1,25,1,25,1,26,1,26,1,26,1,26,
        1,26,1,26,5,26,288,8,26,10,26,12,26,291,9,26,1,26,1,26,1,26,1,26,
        1,26,1,26,5,26,299,8,26,10,26,12,26,302,9,26,1,26,1,26,3,26,306,
        8,26,1,27,1,27,1,27,1,27,1,28,1,28,1,28,1,28,1,28,1,28,1,29,1,29,
        1,29,1,29,3,29,322,8,29,1,29,1,29,1,29,1,29,1,30,1,30,1,30,1,31,
        1,31,5,31,333,8,31,10,31,12,31,336,9,31,1,32,1,32,1,32,1,32,1,32,
        1,32,1,32,1,32,1,32,3,32,347,8,32,1,33,1,33,1,34,1,34,1,34,1,34,
        1,34,1,34,1,34,1,34,3,34,359,8,34,1,35,1,35,1,36,1,36,1,36,1,36,
        1,36,1,36,5,36,369,8,36,10,36,12,36,372,9,36,1,36,1,36,3,36,376,
        8,36,1,37,1,37,1,38,1,38,1,38,1,38,5,38,384,8,38,10,38,12,38,387,
        9,38,1,38,1,38,1,38,1,38,3,38,393,8,38,1,39,1,39,1,39,1,39,1,40,
        1,40,1,40,1,40,5,40,403,8,40,10,40,12,40,406,9,40,1,40,1,40,1,40,
        1,40,3,40,412,8,40,1,41,1,41,1,41,1,41,1,41,1,41,1,41,3,41,421,8,
        41,1,42,1,42,1,43,1,43,1,43,0,1,34,44,0,2,4,6,8,10,12,14,16,18,20,
        22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,62,64,
        66,68,70,72,74,76,78,80,82,84,86,0,5,3,0,6,6,10,10,12,12,1,0,28,
        33,2,0,3,3,7,7,1,0,44,45,1,0,46,47,443,0,88,1,0,0,0,2,91,1,0,0,0,
        4,94,1,0,0,0,6,97,1,0,0,0,8,100,1,0,0,0,10,103,1,0,0,0,12,106,1,
        0,0,0,14,129,1,0,0,0,16,138,1,0,0,0,18,140,1,0,0,0,20,143,1,0,0,
        0,22,156,1,0,0,0,24,158,1,0,0,0,26,163,1,0,0,0,28,175,1,0,0,0,30,
        177,1,0,0,0,32,180,1,0,0,0,34,217,1,0,0,0,36,235,1,0,0,0,38,237,
        1,0,0,0,40,250,1,0,0,0,42,252,1,0,0,0,44,256,1,0,0,0,46,268,1,0,
        0,0,48,270,1,0,0,0,50,276,1,0,0,0,52,305,1,0,0,0,54,307,1,0,0,0,
        56,311,1,0,0,0,58,321,1,0,0,0,60,327,1,0,0,0,62,330,1,0,0,0,64,346,
        1,0,0,0,66,348,1,0,0,0,68,358,1,0,0,0,70,360,1,0,0,0,72,375,1,0,
        0,0,74,377,1,0,0,0,76,392,1,0,0,0,78,394,1,0,0,0,80,411,1,0,0,0,
        82,420,1,0,0,0,84,422,1,0,0,0,86,424,1,0,0,0,88,89,3,14,7,0,89,90,
        5,0,0,1,90,1,1,0,0,0,91,92,3,34,17,0,92,93,5,0,0,1,93,3,1,0,0,0,
        94,95,3,34,17,0,95,96,5,0,0,1,96,5,1,0,0,0,97,98,3,22,11,0,98,99,
        5,0,0,1,99,7,1,0,0,0,100,101,3,28,14,0,101,102,5,0,0,1,102,9,1,0,
        0,0,103,104,3,40,20,0,104,105,5,0,0,1,105,11,1,0,0,0,106,107,3,46,
        23,0,107,108,5,0,0,1,108,13,1,0,0,0,109,113,5,48,0,0,110,112,3,16,
        8,0,111,110,1,0,0,0,112,115,1,0,0,0,113,111,1,0,0,0,113,114,1,0,
        0,0,114,130,1,0,0,0,115,113,1,0,0,0,116,117,5,48,0,0,117,118,3,14,
        7,0,118,124,5,41,0,0,119,120,3,14,7,0,120,121,5,41,0,0,121,123,1,
        0,0,0,122,119,1,0,0,0,123,126,1,0,0,0,124,122,1,0,0,0,124,125,1,
        0,0,0,125,127,1,0,0,0,126,124,1,0,0,0,127,128,5,8,0,0,128,130,1,
        0,0,0,129,109,1,0,0,0,129,116,1,0,0,0,130,15,1,0,0,0,131,139,3,20,
        10,0,132,139,3,26,13,0,133,139,3,44,22,0,134,139,3,30,15,0,135,139,
        3,32,16,0,136,139,3,38,19,0,137,139,3,18,9,0,138,131,1,0,0,0,138,
        132,1,0,0,0,138,133,1,0,0,0,138,134,1,0,0,0,138,135,1,0,0,0,138,
        136,1,0,0,0,138,137,1,0,0,0,139,17,1,0,0,0,140,141,5,48,0,0,141,
        142,3,36,18,0,142,19,1,0,0,0,143,144,5,18,0,0,144,145,3,22,11,0,
        145,21,1,0,0,0,146,157,5,25,0,0,147,152,3,24,12,0,148,149,5,22,0,
        0,149,151,3,24,12,0,150,148,1,0,0,0,151,154,1,0,0,0,152,150,1,0,
        0,0,152,153,1,0,0,0,153,157,1,0,0,0,154,152,1,0,0,0,155,157,3,60,
        30,0,156,146,1,0,0,0,156,147,1,0,0,0,156,155,1,0,0,0,157,23,1,0,
        0,0,158,161,3,62,31,0,159,160,5,2,0,0,160,162,3,62,31,0,161,159,
        1,0,0,0,161,162,1,0,0,0,162,25,1,0,0,0,163,164,7,0,0,0,164,165,3,
        28,14,0,165,27,1,0,0,0,166,171,5,48,0,0,167,168,5,26,0,0,168,170,
        5,48,0,0,169,167,1,0,0,0,170,173,1,0,0,0,171,169,1,0,0,0,171,172,
        1,0,0,0,172,176,1,0,0,0,173,171,1,0,0,0,174,176,3,60,30,0,175,166,
        1,0,0,0,175,174,1,0,0,0,176,29,1,0,0,0,177,178,5,17,0,0,178,179,
        3,34,17,0,179,31,1,0,0,0,180,181,5,21,0,0,181,182,3,34,17,0,182,
        33,1,0,0,0,183,184,6,17,-1,0,184,218,3,36,18,0,185,186,5,38,0,0,
        186,187,3,34,17,0,187,188,5,39,0,0,188,218,1,0,0,0,189,190,3,36,
        18,0,190,191,7,1,0,0,191,192,3,36,18,0,192,218,1,0,0,0,193,194,3,
        36,18,0,194,195,5,4,0,0,195,196,3,36,18,0,196,197,5,1,0,0,197,198,
        3,36,18,0,198,218,1,0,0,0,199,201,3,36,18,0,200,202,5,13,0,0,201,
        200,1,0,0,0,201,202,1,0,0,0,202,203,1,0,0,0,203,204,5,11,0,0,204,
        205,5,38,0,0,205,210,3,36,18,0,206,207,5,22,0,0,207,209,3,36,18,
        0,208,206,1,0,0,0,209,212,1,0,0,0,210,208,1,0,0,0,210,211,1,0,0,
        0,211,213,1,0,0,0,212,210,1,0,0,0,213,214,5,39,0,0,214,218,1,0,0,
        0,215,216,5,13,0,0,216,218,3,34,17,3,217,183,1,0,0,0,217,185,1,0,
        0,0,217,189,1,0,0,0,217,193,1,0,0,0,217,199,1,0,0,0,217,215,1,0,
        0,0,218,227,1,0,0,0,219,220,10,2,0,0,220,221,5,1,0,0,221,226,3,34,
        17,3,222,223,10,1,0,0,223,224,5,15,0,0,224,226,3,34,17,2,225,219,
        1,0,0,0,225,222,1,0,0,0,226,229,1,0,0,0,227,225,1,0,0,0,227,228,
        1,0,0,0,228,35,1,0,0,0,229,227,1,0,0,0,230,236,3,68,34,0,231,236,
        3,62,31,0,232,236,3,60,30,0,233,236,3,56,28,0,234,236,3,50,25,0,
        235,230,1,0,0,0,235,231,1,0,0,0,235,232,1,0,0,0,235,233,1,0,0,0,
        235,234,1,0,0,0,236,37,1,0,0,0,237,238,5,16,0,0,238,239,5,5,0,0,
        239,240,3,40,20,0,240,39,1,0,0,0,241,246,3,42,21,0,242,243,5,22,
        0,0,243,245,3,42,21,0,244,242,1,0,0,0,245,248,1,0,0,0,246,244,1,
        0,0,0,246,247,1,0,0,0,247,251,1,0,0,0,248,246,1,0,0,0,249,251,3,
        60,30,0,250,241,1,0,0,0,250,249,1,0,0,0,251,41,1,0,0,0,252,254,3,
        62,31,0,253,255,7,2,0,0,254,253,1,0,0,0,254,255,1,0,0,0,255,43,1,
        0,0,0,256,257,5,19,0,0,257,258,3,46,23,0,258,45,1,0,0,0,259,264,
        3,48,24,0,260,261,5,22,0,0,261,263,3,48,24,0,262,260,1,0,0,0,263,
        266,1,0,0,0,264,262,1,0,0,0,264,265,1,0,0,0,265,269,1,0,0,0,266,
        264,1,0,0,0,267,269,3,60,30,0,268,259,1,0,0,0,268,267,1,0,0,0,269,
        47,1,0,0,0,270,271,3,62,31,0,271,272,5,32,0,0,272,273,3,50,25,0,
        273,49,1,0,0,0,274,275,5,48,0,0,275,277,5,26,0,0,276,274,1,0,0,0,
        276,277,1,0,0,0,277,278,1,0,0,0,278,279,5,48,0,0,279,280,3,52,26,
        0,280,51,1,0,0,0,281,282,5,38,0,0,282,306,5,39,0,0,283,284,5,38,
        0,0,284,289,3,36,18,0,285,286,5,22,0,0,286,288,3,36,18,0,287,285,
        1,0,0,0,288,291,1,0,0,0,289,287,1,0,0,0,289,290,1,0,0,0,290,292,
        1,0,0,0,291,289,1,0,0,0,292,293,5,39,0,0,293,306,1,0,0,0,294,295,
        5,38,0,0,295,300,3,54,27,0,296,297,5,22,0,0,297,299,3,54,27,0,298,
        296,1,0,0,0,299,302,1,0,0,0,300,298,1,0,0,0,300,301,1,0,0,0,301,
        303,1,0,0,0,302,300,1,0,0,0,303,304,5,39,0,0,304,306,1,0,0,0,305,
        281,1,0,0,0,305,283,1,0,0,0,305,294,1,0,0,0,306,53,1,0,0,0,307,308,
        5,48,0,0,308,309,5,32,0,0,309,310,3,36,18,0,310,55,1,0,0,0,311,312,
        5,36,0,0,312,313,5,36,0,0,313,314,3,58,29,0,314,315,5,37,0,0,315,
        316,5,37,0,0,316,57,1,0,0,0,317,318,5,48,0,0,318,319,5,40,0,0,319,
        320,5,43,0,0,320,322,5,43,0,0,321,317,1,0,0,0,321,322,1,0,0,0,322,
        323,1,0,0,0,323,324,5,48,0,0,324,325,5,26,0,0,325,326,3,62,31,0,
        326,59,1,0,0,0,327,328,5,42,0,0,328,329,5,48,0,0,329,61,1,0,0,0,
        330,334,3,66,33,0,331,333,3,64,32,0,332,331,1,0,0,0,333,336,1,0,
        0,0,334,332,1,0,0,0,334,335,1,0,0,0,335,63,1,0,0,0,336,334,1,0,0,
        0,337,338,5,34,0,0,338,339,3,68,34,0,339,340,5,35,0,0,340,347,1,
        0,0,0,341,342,5,34,0,0,342,343,5,24,0,0,343,347,5,35,0,0,344,345,
        5,26,0,0,345,347,3,66,33,0,346,337,1,0,0,0,346,341,1,0,0,0,346,344,
        1,0,0,0,347,65,1,0,0,0,348,349,5,48,0,0,349,67,1,0,0,0,350,359,5,
        14,0,0,351,359,5,20,0,0,352,359,5,9,0,0,353,359,3,70,35,0,354,359,
        5,46,0,0,355,359,5,47,0,0,356,359,3,74,37,0,357,359,3,72,36,0,358,
        350,1,0,0,0,358,351,1,0,0,0,358,352,1,0,0,0,358,353,1,0,0,0,358,
        354,1,0,0,0,358,355,1,0,0,0,358,356,1,0,0,0,358,357,1,0,0,0,359,
        69,1,0,0,0,360,361,7,3,0,0,361,71,1,0,0,0,362,363,5,34,0,0,363,376,
        5,35,0,0,364,365,5,34,0,0,365,370,3,68,34,0,366,367,5,22,0,0,367,
        369,3,68,34,0,368,366,1,0,0,0,369,372,1,0,0,0,370,368,1,0,0,0,370,
        371,1,0,0,0,371,373,1,0,0,0,372,370,1,0,0,0,373,374,5,35,0,0,374,
        376,1,0,0,0,375,362,1,0,0,0,375,364,1,0,0,0,376,73,1,0,0,0,377,378,
        3,82,41,0,378,75,1,0,0,0,379,380,5,36,0,0,380,385,3,78,39,0,381,
        382,5,22,0,0,382,384,3,78,39,0,383,381,1,0,0,0,384,387,1,0,0,0,385,
        383,1,0,0,0,385,386,1,0,0,0,386,388,1,0,0,0,387,385,1,0,0,0,388,
        389,5,37,0,0,389,393,1,0,0,0,390,391,5,36,0,0,391,393,5,37,0,0,392,
        379,1,0,0,0,392,390,1,0,0,0,393,77,1,0,0,0,394,395,3,84,42,0,395,
        396,5,40,0,0,396,397,3,82,41,0,397,79,1,0,0,0,398,399,5,34,0,0,399,
        404,3,82,41,0,400,401,5,22,0,0,401,403,3,82,41,0,402,400,1,0,0,0,
        403,406,1,0,0,0,404,402,1,0,0,0,404,405,1,0,0,0,405,407,1,0,0,0,
        406,404,1,0,0,0,407,408,5,35,0,0,408,412,1,0,0,0,409,410,5,34,0,
        0,410,412,5,35,0,0,411,398,1,0,0,0,411,409,1,0,0,0,412,81,1,0,0,
        0,413,421,3,84,42,0,414,421,3,86,43,0,415,421,3,76,38,0,416,421,
        3,80,40,0,417,421,5,20,0,0,418,421,5,9,0,0,419,421,5,14,0,0,420,
        413,1,0,0,0,420,414,1,0,0,0,420,415,1,0,0,0,420,416,1,0,0,0,420,
        417,1,0,0,0,420,418,1,0,0,0,420,419,1,0,0,0,421,83,1,0,0,0,422,423,
        5,45,0,0,423,85,1,0,0,0,424,425,7,4,0,0,425,87,1,0,0,0,35,113,124,
        129,138,152,156,161,171,175,201,210,217,225,227,235,246,250,254,
        264,268,276,289,300,305,321,334,346,358,370,375,385,392,404,411,
        420
    ]

class VerseQLParser ( Parser ):

    grammarFileName = "VerseQLParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'AND'", "'AS'", "'ASC'", "'BETWEEN'", 
                     "'BY'", "'COLLECTION'", "'DESC'", "'END'", "'FALSE'", 
                     "'FROM'", "'IN'", "'INTO'", "'NOT'", "'NULL'", "'OR'", 
                     "'ORDER'", "'SEARCH'", "'SELECT'", "'SET'", "'TRUE'", 
                     "'WHERE'", "','", "'+'", "'-'", "'*'", "'.'", "'?'", 
                     "'<'", "'<='", "'>'", "'>='", "'='", "<INVALID>", "'['", 
                     "']'", "'{'", "'}'", "'('", "')'", "':'", "';'", "'@'", 
                     "'/'" ]

    symbolicNames = [ "<INVALID>", "AND", "AS", "ASC", "BETWEEN", "BY", 
                      "COLLECTION", "DESC", "END", "FALSE", "FROM", "IN", 
                      "INTO", "NOT", "NULL", "OR", "ORDER", "SEARCH", "SELECT", 
                      "SET", "TRUE", "WHERE", "COMMA", "PLUS", "MINUS", 
                      "STAR", "DOT", "QUESTION_MARK", "LT", "LT_EQ", "GT", 
                      "GT_EQ", "EQ", "NEQ", "BRACKET_LEFT", "BRACKET_RIGHT", 
                      "BRACE_LEFT", "BRACE_RIGHT", "PAREN_LEFT", "PAREN_RIGHT", 
                      "COLON", "SEMI_COLON", "AT", "SLASH", "LITERAL_STRING_SINGLE", 
                      "LITERAL_STRING_DOUBLE", "LITERAL_INTEGER", "LITERAL_DECIMAL", 
                      "IDENTIFIER", "WS", "COMMENT_SINGLE_LINE", "COMMENT_MULTILINE", 
                      "UNRECOGNIZED" ]

    RULE_parse_statement = 0
    RULE_parse_search = 1
    RULE_parse_where = 2
    RULE_parse_select = 3
    RULE_parse_collection = 4
    RULE_parse_order_by = 5
    RULE_parse_update = 6
    RULE_statement = 7
    RULE_clause = 8
    RULE_generic_clause = 9
    RULE_select_clause = 10
    RULE_select = 11
    RULE_select_term = 12
    RULE_collection_clause = 13
    RULE_collection = 14
    RULE_search_clause = 15
    RULE_where_clause = 16
    RULE_expression = 17
    RULE_operand = 18
    RULE_order_by_clause = 19
    RULE_order_by = 20
    RULE_order_by_term = 21
    RULE_set_clause = 22
    RULE_update = 23
    RULE_update_operation = 24
    RULE_function = 25
    RULE_function_args = 26
    RULE_named_arg = 27
    RULE_ref = 28
    RULE_ref_path = 29
    RULE_parameter = 30
    RULE_field = 31
    RULE_field_path = 32
    RULE_field_primitive = 33
    RULE_value = 34
    RULE_literal_string = 35
    RULE_array = 36
    RULE_json = 37
    RULE_json_obj = 38
    RULE_json_pair = 39
    RULE_json_arr = 40
    RULE_json_value = 41
    RULE_json_string = 42
    RULE_json_number = 43

    ruleNames =  [ "parse_statement", "parse_search", "parse_where", "parse_select", 
                   "parse_collection", "parse_order_by", "parse_update", 
                   "statement", "clause", "generic_clause", "select_clause", 
                   "select", "select_term", "collection_clause", "collection", 
                   "search_clause", "where_clause", "expression", "operand", 
                   "order_by_clause", "order_by", "order_by_term", "set_clause", 
                   "update", "update_operation", "function", "function_args", 
                   "named_arg", "ref", "ref_path", "parameter", "field", 
                   "field_path", "field_primitive", "value", "literal_string", 
                   "array", "json", "json_obj", "json_pair", "json_arr", 
                   "json_value", "json_string", "json_number" ]

    EOF = Token.EOF
    AND=1
    AS=2
    ASC=3
    BETWEEN=4
    BY=5
    COLLECTION=6
    DESC=7
    END=8
    FALSE=9
    FROM=10
    IN=11
    INTO=12
    NOT=13
    NULL=14
    OR=15
    ORDER=16
    SEARCH=17
    SELECT=18
    SET=19
    TRUE=20
    WHERE=21
    COMMA=22
    PLUS=23
    MINUS=24
    STAR=25
    DOT=26
    QUESTION_MARK=27
    LT=28
    LT_EQ=29
    GT=30
    GT_EQ=31
    EQ=32
    NEQ=33
    BRACKET_LEFT=34
    BRACKET_RIGHT=35
    BRACE_LEFT=36
    BRACE_RIGHT=37
    PAREN_LEFT=38
    PAREN_RIGHT=39
    COLON=40
    SEMI_COLON=41
    AT=42
    SLASH=43
    LITERAL_STRING_SINGLE=44
    LITERAL_STRING_DOUBLE=45
    LITERAL_INTEGER=46
    LITERAL_DECIMAL=47
    IDENTIFIER=48
    WS=49
    COMMENT_SINGLE_LINE=50
    COMMENT_MULTILINE=51
    UNRECOGNIZED=52

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Parse_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def statement(self):
            return self.getTypedRuleContext(VerseQLParser.StatementContext,0)


        def EOF(self):
            return self.getToken(VerseQLParser.EOF, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_parse_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParse_statement" ):
                listener.enterParse_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParse_statement" ):
                listener.exitParse_statement(self)




    def parse_statement(self):

        localctx = VerseQLParser.Parse_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_parse_statement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 88
            self.statement()
            self.state = 89
            self.match(VerseQLParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Parse_searchContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(VerseQLParser.ExpressionContext,0)


        def EOF(self):
            return self.getToken(VerseQLParser.EOF, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_parse_search

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParse_search" ):
                listener.enterParse_search(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParse_search" ):
                listener.exitParse_search(self)




    def parse_search(self):

        localctx = VerseQLParser.Parse_searchContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_parse_search)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 91
            self.expression(0)
            self.state = 92
            self.match(VerseQLParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Parse_whereContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(VerseQLParser.ExpressionContext,0)


        def EOF(self):
            return self.getToken(VerseQLParser.EOF, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_parse_where

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParse_where" ):
                listener.enterParse_where(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParse_where" ):
                listener.exitParse_where(self)




    def parse_where(self):

        localctx = VerseQLParser.Parse_whereContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_parse_where)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 94
            self.expression(0)
            self.state = 95
            self.match(VerseQLParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Parse_selectContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def select(self):
            return self.getTypedRuleContext(VerseQLParser.SelectContext,0)


        def EOF(self):
            return self.getToken(VerseQLParser.EOF, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_parse_select

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParse_select" ):
                listener.enterParse_select(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParse_select" ):
                listener.exitParse_select(self)




    def parse_select(self):

        localctx = VerseQLParser.Parse_selectContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_parse_select)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 97
            self.select()
            self.state = 98
            self.match(VerseQLParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Parse_collectionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def collection(self):
            return self.getTypedRuleContext(VerseQLParser.CollectionContext,0)


        def EOF(self):
            return self.getToken(VerseQLParser.EOF, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_parse_collection

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParse_collection" ):
                listener.enterParse_collection(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParse_collection" ):
                listener.exitParse_collection(self)




    def parse_collection(self):

        localctx = VerseQLParser.Parse_collectionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_parse_collection)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 100
            self.collection()
            self.state = 101
            self.match(VerseQLParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Parse_order_byContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def order_by(self):
            return self.getTypedRuleContext(VerseQLParser.Order_byContext,0)


        def EOF(self):
            return self.getToken(VerseQLParser.EOF, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_parse_order_by

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParse_order_by" ):
                listener.enterParse_order_by(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParse_order_by" ):
                listener.exitParse_order_by(self)




    def parse_order_by(self):

        localctx = VerseQLParser.Parse_order_byContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_parse_order_by)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 103
            self.order_by()
            self.state = 104
            self.match(VerseQLParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Parse_updateContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def update(self):
            return self.getTypedRuleContext(VerseQLParser.UpdateContext,0)


        def EOF(self):
            return self.getToken(VerseQLParser.EOF, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_parse_update

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParse_update" ):
                listener.enterParse_update(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParse_update" ):
                listener.exitParse_update(self)




    def parse_update(self):

        localctx = VerseQLParser.Parse_updateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_parse_update)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 106
            self.update()
            self.state = 107
            self.match(VerseQLParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return VerseQLParser.RULE_statement

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class Statement_multiContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.StatementContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(VerseQLParser.StatementContext)
            else:
                return self.getTypedRuleContext(VerseQLParser.StatementContext,i)

        def SEMI_COLON(self, i:int=None):
            if i is None:
                return self.getTokens(VerseQLParser.SEMI_COLON)
            else:
                return self.getToken(VerseQLParser.SEMI_COLON, i)
        def END(self):
            return self.getToken(VerseQLParser.END, 0)
        def IDENTIFIER(self):
            return self.getToken(VerseQLParser.IDENTIFIER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatement_multi" ):
                listener.enterStatement_multi(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatement_multi" ):
                listener.exitStatement_multi(self)


    class Statement_singleContext(StatementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.StatementContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def IDENTIFIER(self):
            return self.getToken(VerseQLParser.IDENTIFIER, 0)
        def clause(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(VerseQLParser.ClauseContext)
            else:
                return self.getTypedRuleContext(VerseQLParser.ClauseContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatement_single" ):
                listener.enterStatement_single(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatement_single" ):
                listener.exitStatement_single(self)



    def statement(self):

        localctx = VerseQLParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_statement)
        self._la = 0 # Token type
        try:
            self.state = 129
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,2,self._ctx)
            if la_ == 1:
                localctx = VerseQLParser.Statement_singleContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 109
                localctx.op = self.match(VerseQLParser.IDENTIFIER)
                self.state = 113
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while (((_la) & ~0x3f) == 0 and ((1 << _la) & 281474979796032) != 0):
                    self.state = 110
                    self.clause()
                    self.state = 115
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 2:
                localctx = VerseQLParser.Statement_multiContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 116
                localctx.op = self.match(VerseQLParser.IDENTIFIER)
                self.state = 117
                self.statement()
                self.state = 118
                self.match(VerseQLParser.SEMI_COLON)
                self.state = 124
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==48:
                    self.state = 119
                    self.statement()
                    self.state = 120
                    self.match(VerseQLParser.SEMI_COLON)
                    self.state = 126
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 127
                self.match(VerseQLParser.END)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ClauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def select_clause(self):
            return self.getTypedRuleContext(VerseQLParser.Select_clauseContext,0)


        def collection_clause(self):
            return self.getTypedRuleContext(VerseQLParser.Collection_clauseContext,0)


        def set_clause(self):
            return self.getTypedRuleContext(VerseQLParser.Set_clauseContext,0)


        def search_clause(self):
            return self.getTypedRuleContext(VerseQLParser.Search_clauseContext,0)


        def where_clause(self):
            return self.getTypedRuleContext(VerseQLParser.Where_clauseContext,0)


        def order_by_clause(self):
            return self.getTypedRuleContext(VerseQLParser.Order_by_clauseContext,0)


        def generic_clause(self):
            return self.getTypedRuleContext(VerseQLParser.Generic_clauseContext,0)


        def getRuleIndex(self):
            return VerseQLParser.RULE_clause

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterClause" ):
                listener.enterClause(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitClause" ):
                listener.exitClause(self)




    def clause(self):

        localctx = VerseQLParser.ClauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_clause)
        try:
            self.state = 138
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [18]:
                self.enterOuterAlt(localctx, 1)
                self.state = 131
                self.select_clause()
                pass
            elif token in [6, 10, 12]:
                self.enterOuterAlt(localctx, 2)
                self.state = 132
                self.collection_clause()
                pass
            elif token in [19]:
                self.enterOuterAlt(localctx, 3)
                self.state = 133
                self.set_clause()
                pass
            elif token in [17]:
                self.enterOuterAlt(localctx, 4)
                self.state = 134
                self.search_clause()
                pass
            elif token in [21]:
                self.enterOuterAlt(localctx, 5)
                self.state = 135
                self.where_clause()
                pass
            elif token in [16]:
                self.enterOuterAlt(localctx, 6)
                self.state = 136
                self.order_by_clause()
                pass
            elif token in [48]:
                self.enterOuterAlt(localctx, 7)
                self.state = 137
                self.generic_clause()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Generic_clauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.name = None # Token

        def operand(self):
            return self.getTypedRuleContext(VerseQLParser.OperandContext,0)


        def IDENTIFIER(self):
            return self.getToken(VerseQLParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_generic_clause

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGeneric_clause" ):
                listener.enterGeneric_clause(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGeneric_clause" ):
                listener.exitGeneric_clause(self)




    def generic_clause(self):

        localctx = VerseQLParser.Generic_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_generic_clause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 140
            localctx.name = self.match(VerseQLParser.IDENTIFIER)
            self.state = 141
            self.operand()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Select_clauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SELECT(self):
            return self.getToken(VerseQLParser.SELECT, 0)

        def select(self):
            return self.getTypedRuleContext(VerseQLParser.SelectContext,0)


        def getRuleIndex(self):
            return VerseQLParser.RULE_select_clause

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSelect_clause" ):
                listener.enterSelect_clause(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSelect_clause" ):
                listener.exitSelect_clause(self)




    def select_clause(self):

        localctx = VerseQLParser.Select_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_select_clause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 143
            self.match(VerseQLParser.SELECT)
            self.state = 144
            self.select()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SelectContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return VerseQLParser.RULE_select

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class Select_parameterContext(SelectContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.SelectContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def parameter(self):
            return self.getTypedRuleContext(VerseQLParser.ParameterContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSelect_parameter" ):
                listener.enterSelect_parameter(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSelect_parameter" ):
                listener.exitSelect_parameter(self)


    class Select_termsContext(SelectContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.SelectContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def select_term(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(VerseQLParser.Select_termContext)
            else:
                return self.getTypedRuleContext(VerseQLParser.Select_termContext,i)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(VerseQLParser.COMMA)
            else:
                return self.getToken(VerseQLParser.COMMA, i)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSelect_terms" ):
                listener.enterSelect_terms(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSelect_terms" ):
                listener.exitSelect_terms(self)


    class Select_allContext(SelectContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.SelectContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def STAR(self):
            return self.getToken(VerseQLParser.STAR, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSelect_all" ):
                listener.enterSelect_all(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSelect_all" ):
                listener.exitSelect_all(self)



    def select(self):

        localctx = VerseQLParser.SelectContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_select)
        self._la = 0 # Token type
        try:
            self.state = 156
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [25]:
                localctx = VerseQLParser.Select_allContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 146
                self.match(VerseQLParser.STAR)
                pass
            elif token in [48]:
                localctx = VerseQLParser.Select_termsContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 147
                self.select_term()
                self.state = 152
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==22:
                    self.state = 148
                    self.match(VerseQLParser.COMMA)
                    self.state = 149
                    self.select_term()
                    self.state = 154
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            elif token in [42]:
                localctx = VerseQLParser.Select_parameterContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 155
                self.parameter()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Select_termContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def field(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(VerseQLParser.FieldContext)
            else:
                return self.getTypedRuleContext(VerseQLParser.FieldContext,i)


        def AS(self):
            return self.getToken(VerseQLParser.AS, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_select_term

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSelect_term" ):
                listener.enterSelect_term(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSelect_term" ):
                listener.exitSelect_term(self)




    def select_term(self):

        localctx = VerseQLParser.Select_termContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_select_term)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 158
            self.field()
            self.state = 161
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==2:
                self.state = 159
                self.match(VerseQLParser.AS)
                self.state = 160
                self.field()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Collection_clauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def collection(self):
            return self.getTypedRuleContext(VerseQLParser.CollectionContext,0)


        def COLLECTION(self):
            return self.getToken(VerseQLParser.COLLECTION, 0)

        def FROM(self):
            return self.getToken(VerseQLParser.FROM, 0)

        def INTO(self):
            return self.getToken(VerseQLParser.INTO, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_collection_clause

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCollection_clause" ):
                listener.enterCollection_clause(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCollection_clause" ):
                listener.exitCollection_clause(self)




    def collection_clause(self):

        localctx = VerseQLParser.Collection_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_collection_clause)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 163
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 5184) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 164
            self.collection()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CollectionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return VerseQLParser.RULE_collection

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class Collection_parameterContext(CollectionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.CollectionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def parameter(self):
            return self.getTypedRuleContext(VerseQLParser.ParameterContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCollection_parameter" ):
                listener.enterCollection_parameter(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCollection_parameter" ):
                listener.exitCollection_parameter(self)


    class Collection_identifierContext(CollectionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.CollectionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def IDENTIFIER(self, i:int=None):
            if i is None:
                return self.getTokens(VerseQLParser.IDENTIFIER)
            else:
                return self.getToken(VerseQLParser.IDENTIFIER, i)
        def DOT(self, i:int=None):
            if i is None:
                return self.getTokens(VerseQLParser.DOT)
            else:
                return self.getToken(VerseQLParser.DOT, i)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCollection_identifier" ):
                listener.enterCollection_identifier(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCollection_identifier" ):
                listener.exitCollection_identifier(self)



    def collection(self):

        localctx = VerseQLParser.CollectionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_collection)
        self._la = 0 # Token type
        try:
            self.state = 175
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [48]:
                localctx = VerseQLParser.Collection_identifierContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 166
                self.match(VerseQLParser.IDENTIFIER)
                self.state = 171
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==26:
                    self.state = 167
                    self.match(VerseQLParser.DOT)
                    self.state = 168
                    self.match(VerseQLParser.IDENTIFIER)
                    self.state = 173
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            elif token in [42]:
                localctx = VerseQLParser.Collection_parameterContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 174
                self.parameter()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Search_clauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SEARCH(self):
            return self.getToken(VerseQLParser.SEARCH, 0)

        def expression(self):
            return self.getTypedRuleContext(VerseQLParser.ExpressionContext,0)


        def getRuleIndex(self):
            return VerseQLParser.RULE_search_clause

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSearch_clause" ):
                listener.enterSearch_clause(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSearch_clause" ):
                listener.exitSearch_clause(self)




    def search_clause(self):

        localctx = VerseQLParser.Search_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_search_clause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 177
            self.match(VerseQLParser.SEARCH)
            self.state = 178
            self.expression(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Where_clauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WHERE(self):
            return self.getToken(VerseQLParser.WHERE, 0)

        def expression(self):
            return self.getTypedRuleContext(VerseQLParser.ExpressionContext,0)


        def getRuleIndex(self):
            return VerseQLParser.RULE_where_clause

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterWhere_clause" ):
                listener.enterWhere_clause(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitWhere_clause" ):
                listener.exitWhere_clause(self)




    def where_clause(self):

        localctx = VerseQLParser.Where_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_where_clause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 180
            self.match(VerseQLParser.WHERE)
            self.state = 181
            self.expression(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return VerseQLParser.RULE_expression

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class Expression_operandContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def operand(self):
            return self.getTypedRuleContext(VerseQLParser.OperandContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpression_operand" ):
                listener.enterExpression_operand(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpression_operand" ):
                listener.exitExpression_operand(self)


    class Expression_notContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NOT(self):
            return self.getToken(VerseQLParser.NOT, 0)
        def expression(self):
            return self.getTypedRuleContext(VerseQLParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpression_not" ):
                listener.enterExpression_not(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpression_not" ):
                listener.exitExpression_not(self)


    class Expression_orContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.ExpressionContext
            super().__init__(parser)
            self.lhs = None # ExpressionContext
            self.rhs = None # ExpressionContext
            self.copyFrom(ctx)

        def OR(self):
            return self.getToken(VerseQLParser.OR, 0)
        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(VerseQLParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(VerseQLParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpression_or" ):
                listener.enterExpression_or(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpression_or" ):
                listener.exitExpression_or(self)


    class Expression_comparisonContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.ExpressionContext
            super().__init__(parser)
            self.lhs = None # OperandContext
            self.op = None # Token
            self.rhs = None # OperandContext
            self.copyFrom(ctx)

        def operand(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(VerseQLParser.OperandContext)
            else:
                return self.getTypedRuleContext(VerseQLParser.OperandContext,i)

        def EQ(self):
            return self.getToken(VerseQLParser.EQ, 0)
        def NEQ(self):
            return self.getToken(VerseQLParser.NEQ, 0)
        def GT(self):
            return self.getToken(VerseQLParser.GT, 0)
        def GT_EQ(self):
            return self.getToken(VerseQLParser.GT_EQ, 0)
        def LT(self):
            return self.getToken(VerseQLParser.LT, 0)
        def LT_EQ(self):
            return self.getToken(VerseQLParser.LT_EQ, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpression_comparison" ):
                listener.enterExpression_comparison(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpression_comparison" ):
                listener.exitExpression_comparison(self)


    class Expression_comparison_inContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.ExpressionContext
            super().__init__(parser)
            self.lhs = None # OperandContext
            self.not_in = None # Token
            self.copyFrom(ctx)

        def IN(self):
            return self.getToken(VerseQLParser.IN, 0)
        def PAREN_LEFT(self):
            return self.getToken(VerseQLParser.PAREN_LEFT, 0)
        def operand(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(VerseQLParser.OperandContext)
            else:
                return self.getTypedRuleContext(VerseQLParser.OperandContext,i)

        def PAREN_RIGHT(self):
            return self.getToken(VerseQLParser.PAREN_RIGHT, 0)
        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(VerseQLParser.COMMA)
            else:
                return self.getToken(VerseQLParser.COMMA, i)
        def NOT(self):
            return self.getToken(VerseQLParser.NOT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpression_comparison_in" ):
                listener.enterExpression_comparison_in(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpression_comparison_in" ):
                listener.exitExpression_comparison_in(self)


    class Expression_paranthesisContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def PAREN_LEFT(self):
            return self.getToken(VerseQLParser.PAREN_LEFT, 0)
        def expression(self):
            return self.getTypedRuleContext(VerseQLParser.ExpressionContext,0)

        def PAREN_RIGHT(self):
            return self.getToken(VerseQLParser.PAREN_RIGHT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpression_paranthesis" ):
                listener.enterExpression_paranthesis(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpression_paranthesis" ):
                listener.exitExpression_paranthesis(self)


    class Expression_comparison_betweenContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.ExpressionContext
            super().__init__(parser)
            self.lhs = None # OperandContext
            self.low = None # OperandContext
            self.high = None # OperandContext
            self.copyFrom(ctx)

        def BETWEEN(self):
            return self.getToken(VerseQLParser.BETWEEN, 0)
        def AND(self):
            return self.getToken(VerseQLParser.AND, 0)
        def operand(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(VerseQLParser.OperandContext)
            else:
                return self.getTypedRuleContext(VerseQLParser.OperandContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpression_comparison_between" ):
                listener.enterExpression_comparison_between(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpression_comparison_between" ):
                listener.exitExpression_comparison_between(self)


    class Expression_andContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.ExpressionContext
            super().__init__(parser)
            self.lhs = None # ExpressionContext
            self.rhs = None # ExpressionContext
            self.copyFrom(ctx)

        def AND(self):
            return self.getToken(VerseQLParser.AND, 0)
        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(VerseQLParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(VerseQLParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpression_and" ):
                listener.enterExpression_and(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpression_and" ):
                listener.exitExpression_and(self)



    def expression(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = VerseQLParser.ExpressionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 34
        self.enterRecursionRule(localctx, 34, self.RULE_expression, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 217
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,11,self._ctx)
            if la_ == 1:
                localctx = VerseQLParser.Expression_operandContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 184
                self.operand()
                pass

            elif la_ == 2:
                localctx = VerseQLParser.Expression_paranthesisContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 185
                self.match(VerseQLParser.PAREN_LEFT)
                self.state = 186
                self.expression(0)
                self.state = 187
                self.match(VerseQLParser.PAREN_RIGHT)
                pass

            elif la_ == 3:
                localctx = VerseQLParser.Expression_comparisonContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 189
                localctx.lhs = self.operand()
                self.state = 190
                localctx.op = self._input.LT(1)
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 16911433728) != 0)):
                    localctx.op = self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 191
                localctx.rhs = self.operand()
                pass

            elif la_ == 4:
                localctx = VerseQLParser.Expression_comparison_betweenContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 193
                localctx.lhs = self.operand()
                self.state = 194
                self.match(VerseQLParser.BETWEEN)
                self.state = 195
                localctx.low = self.operand()
                self.state = 196
                self.match(VerseQLParser.AND)
                self.state = 197
                localctx.high = self.operand()
                pass

            elif la_ == 5:
                localctx = VerseQLParser.Expression_comparison_inContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 199
                localctx.lhs = self.operand()
                self.state = 201
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==13:
                    self.state = 200
                    localctx.not_in = self.match(VerseQLParser.NOT)


                self.state = 203
                self.match(VerseQLParser.IN)
                self.state = 204
                self.match(VerseQLParser.PAREN_LEFT)
                self.state = 205
                self.operand()
                self.state = 210
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==22:
                    self.state = 206
                    self.match(VerseQLParser.COMMA)
                    self.state = 207
                    self.operand()
                    self.state = 212
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 213
                self.match(VerseQLParser.PAREN_RIGHT)
                pass

            elif la_ == 6:
                localctx = VerseQLParser.Expression_notContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 215
                self.match(VerseQLParser.NOT)
                self.state = 216
                self.expression(3)
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 227
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,13,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 225
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,12,self._ctx)
                    if la_ == 1:
                        localctx = VerseQLParser.Expression_andContext(self, VerseQLParser.ExpressionContext(self, _parentctx, _parentState))
                        localctx.lhs = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 219
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 220
                        self.match(VerseQLParser.AND)
                        self.state = 221
                        localctx.rhs = self.expression(3)
                        pass

                    elif la_ == 2:
                        localctx = VerseQLParser.Expression_orContext(self, VerseQLParser.ExpressionContext(self, _parentctx, _parentState))
                        localctx.lhs = _prevctx
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 222
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                        self.state = 223
                        self.match(VerseQLParser.OR)
                        self.state = 224
                        localctx.rhs = self.expression(2)
                        pass

             
                self.state = 229
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,13,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class OperandContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return VerseQLParser.RULE_operand

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class Operand_fieldContext(OperandContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.OperandContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def field(self):
            return self.getTypedRuleContext(VerseQLParser.FieldContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOperand_field" ):
                listener.enterOperand_field(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOperand_field" ):
                listener.exitOperand_field(self)


    class Operand_valueContext(OperandContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.OperandContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def value(self):
            return self.getTypedRuleContext(VerseQLParser.ValueContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOperand_value" ):
                listener.enterOperand_value(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOperand_value" ):
                listener.exitOperand_value(self)


    class Operand_refContext(OperandContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.OperandContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def ref(self):
            return self.getTypedRuleContext(VerseQLParser.RefContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOperand_ref" ):
                listener.enterOperand_ref(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOperand_ref" ):
                listener.exitOperand_ref(self)


    class Operand_parameterContext(OperandContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.OperandContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def parameter(self):
            return self.getTypedRuleContext(VerseQLParser.ParameterContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOperand_parameter" ):
                listener.enterOperand_parameter(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOperand_parameter" ):
                listener.exitOperand_parameter(self)


    class Operand_functionContext(OperandContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.OperandContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def function(self):
            return self.getTypedRuleContext(VerseQLParser.FunctionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOperand_function" ):
                listener.enterOperand_function(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOperand_function" ):
                listener.exitOperand_function(self)



    def operand(self):

        localctx = VerseQLParser.OperandContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_operand)
        try:
            self.state = 235
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,14,self._ctx)
            if la_ == 1:
                localctx = VerseQLParser.Operand_valueContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 230
                self.value()
                pass

            elif la_ == 2:
                localctx = VerseQLParser.Operand_fieldContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 231
                self.field()
                pass

            elif la_ == 3:
                localctx = VerseQLParser.Operand_parameterContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 232
                self.parameter()
                pass

            elif la_ == 4:
                localctx = VerseQLParser.Operand_refContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 233
                self.ref()
                pass

            elif la_ == 5:
                localctx = VerseQLParser.Operand_functionContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 234
                self.function()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Order_by_clauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ORDER(self):
            return self.getToken(VerseQLParser.ORDER, 0)

        def BY(self):
            return self.getToken(VerseQLParser.BY, 0)

        def order_by(self):
            return self.getTypedRuleContext(VerseQLParser.Order_byContext,0)


        def getRuleIndex(self):
            return VerseQLParser.RULE_order_by_clause

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOrder_by_clause" ):
                listener.enterOrder_by_clause(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOrder_by_clause" ):
                listener.exitOrder_by_clause(self)




    def order_by_clause(self):

        localctx = VerseQLParser.Order_by_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_order_by_clause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 237
            self.match(VerseQLParser.ORDER)
            self.state = 238
            self.match(VerseQLParser.BY)
            self.state = 239
            self.order_by()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Order_byContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return VerseQLParser.RULE_order_by

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class Order_by_parameterContext(Order_byContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.Order_byContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def parameter(self):
            return self.getTypedRuleContext(VerseQLParser.ParameterContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOrder_by_parameter" ):
                listener.enterOrder_by_parameter(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOrder_by_parameter" ):
                listener.exitOrder_by_parameter(self)


    class Order_by_termsContext(Order_byContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.Order_byContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def order_by_term(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(VerseQLParser.Order_by_termContext)
            else:
                return self.getTypedRuleContext(VerseQLParser.Order_by_termContext,i)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(VerseQLParser.COMMA)
            else:
                return self.getToken(VerseQLParser.COMMA, i)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOrder_by_terms" ):
                listener.enterOrder_by_terms(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOrder_by_terms" ):
                listener.exitOrder_by_terms(self)



    def order_by(self):

        localctx = VerseQLParser.Order_byContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_order_by)
        self._la = 0 # Token type
        try:
            self.state = 250
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [48]:
                localctx = VerseQLParser.Order_by_termsContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 241
                self.order_by_term()
                self.state = 246
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==22:
                    self.state = 242
                    self.match(VerseQLParser.COMMA)
                    self.state = 243
                    self.order_by_term()
                    self.state = 248
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            elif token in [42]:
                localctx = VerseQLParser.Order_by_parameterContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 249
                self.parameter()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Order_by_termContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.direction = None # Token

        def field(self):
            return self.getTypedRuleContext(VerseQLParser.FieldContext,0)


        def ASC(self):
            return self.getToken(VerseQLParser.ASC, 0)

        def DESC(self):
            return self.getToken(VerseQLParser.DESC, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_order_by_term

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOrder_by_term" ):
                listener.enterOrder_by_term(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOrder_by_term" ):
                listener.exitOrder_by_term(self)




    def order_by_term(self):

        localctx = VerseQLParser.Order_by_termContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_order_by_term)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 252
            self.field()
            self.state = 254
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3 or _la==7:
                self.state = 253
                localctx.direction = self._input.LT(1)
                _la = self._input.LA(1)
                if not(_la==3 or _la==7):
                    localctx.direction = self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Set_clauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SET(self):
            return self.getToken(VerseQLParser.SET, 0)

        def update(self):
            return self.getTypedRuleContext(VerseQLParser.UpdateContext,0)


        def getRuleIndex(self):
            return VerseQLParser.RULE_set_clause

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSet_clause" ):
                listener.enterSet_clause(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSet_clause" ):
                listener.exitSet_clause(self)




    def set_clause(self):

        localctx = VerseQLParser.Set_clauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_set_clause)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 256
            self.match(VerseQLParser.SET)
            self.state = 257
            self.update()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class UpdateContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return VerseQLParser.RULE_update

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class Update_operationsContext(UpdateContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.UpdateContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def update_operation(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(VerseQLParser.Update_operationContext)
            else:
                return self.getTypedRuleContext(VerseQLParser.Update_operationContext,i)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(VerseQLParser.COMMA)
            else:
                return self.getToken(VerseQLParser.COMMA, i)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterUpdate_operations" ):
                listener.enterUpdate_operations(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitUpdate_operations" ):
                listener.exitUpdate_operations(self)


    class Update_parameterContext(UpdateContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.UpdateContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def parameter(self):
            return self.getTypedRuleContext(VerseQLParser.ParameterContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterUpdate_parameter" ):
                listener.enterUpdate_parameter(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitUpdate_parameter" ):
                listener.exitUpdate_parameter(self)



    def update(self):

        localctx = VerseQLParser.UpdateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_update)
        self._la = 0 # Token type
        try:
            self.state = 268
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [48]:
                localctx = VerseQLParser.Update_operationsContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 259
                self.update_operation()
                self.state = 264
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==22:
                    self.state = 260
                    self.match(VerseQLParser.COMMA)
                    self.state = 261
                    self.update_operation()
                    self.state = 266
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass
            elif token in [42]:
                localctx = VerseQLParser.Update_parameterContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 267
                self.parameter()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Update_operationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def field(self):
            return self.getTypedRuleContext(VerseQLParser.FieldContext,0)


        def EQ(self):
            return self.getToken(VerseQLParser.EQ, 0)

        def function(self):
            return self.getTypedRuleContext(VerseQLParser.FunctionContext,0)


        def getRuleIndex(self):
            return VerseQLParser.RULE_update_operation

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterUpdate_operation" ):
                listener.enterUpdate_operation(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitUpdate_operation" ):
                listener.exitUpdate_operation(self)




    def update_operation(self):

        localctx = VerseQLParser.Update_operationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_update_operation)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 270
            self.field()
            self.state = 271
            self.match(VerseQLParser.EQ)
            self.state = 272
            self.function()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FunctionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.namespace = None # Token
            self.name = None # Token

        def function_args(self):
            return self.getTypedRuleContext(VerseQLParser.Function_argsContext,0)


        def IDENTIFIER(self, i:int=None):
            if i is None:
                return self.getTokens(VerseQLParser.IDENTIFIER)
            else:
                return self.getToken(VerseQLParser.IDENTIFIER, i)

        def DOT(self):
            return self.getToken(VerseQLParser.DOT, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_function

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFunction" ):
                listener.enterFunction(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFunction" ):
                listener.exitFunction(self)




    def function(self):

        localctx = VerseQLParser.FunctionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_function)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 276
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,20,self._ctx)
            if la_ == 1:
                self.state = 274
                localctx.namespace = self.match(VerseQLParser.IDENTIFIER)
                self.state = 275
                self.match(VerseQLParser.DOT)


            self.state = 278
            localctx.name = self.match(VerseQLParser.IDENTIFIER)
            self.state = 279
            self.function_args()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Function_argsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return VerseQLParser.RULE_function_args

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class Function_no_argsContext(Function_argsContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.Function_argsContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def PAREN_LEFT(self):
            return self.getToken(VerseQLParser.PAREN_LEFT, 0)
        def PAREN_RIGHT(self):
            return self.getToken(VerseQLParser.PAREN_RIGHT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFunction_no_args" ):
                listener.enterFunction_no_args(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFunction_no_args" ):
                listener.exitFunction_no_args(self)


    class Function_with_argsContext(Function_argsContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.Function_argsContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def PAREN_LEFT(self):
            return self.getToken(VerseQLParser.PAREN_LEFT, 0)
        def operand(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(VerseQLParser.OperandContext)
            else:
                return self.getTypedRuleContext(VerseQLParser.OperandContext,i)

        def PAREN_RIGHT(self):
            return self.getToken(VerseQLParser.PAREN_RIGHT, 0)
        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(VerseQLParser.COMMA)
            else:
                return self.getToken(VerseQLParser.COMMA, i)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFunction_with_args" ):
                listener.enterFunction_with_args(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFunction_with_args" ):
                listener.exitFunction_with_args(self)


    class Function_with_named_argsContext(Function_argsContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.Function_argsContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def PAREN_LEFT(self):
            return self.getToken(VerseQLParser.PAREN_LEFT, 0)
        def named_arg(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(VerseQLParser.Named_argContext)
            else:
                return self.getTypedRuleContext(VerseQLParser.Named_argContext,i)

        def PAREN_RIGHT(self):
            return self.getToken(VerseQLParser.PAREN_RIGHT, 0)
        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(VerseQLParser.COMMA)
            else:
                return self.getToken(VerseQLParser.COMMA, i)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFunction_with_named_args" ):
                listener.enterFunction_with_named_args(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFunction_with_named_args" ):
                listener.exitFunction_with_named_args(self)



    def function_args(self):

        localctx = VerseQLParser.Function_argsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_function_args)
        self._la = 0 # Token type
        try:
            self.state = 305
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,23,self._ctx)
            if la_ == 1:
                localctx = VerseQLParser.Function_no_argsContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 281
                self.match(VerseQLParser.PAREN_LEFT)
                self.state = 282
                self.match(VerseQLParser.PAREN_RIGHT)
                pass

            elif la_ == 2:
                localctx = VerseQLParser.Function_with_argsContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 283
                self.match(VerseQLParser.PAREN_LEFT)
                self.state = 284
                self.operand()
                self.state = 289
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==22:
                    self.state = 285
                    self.match(VerseQLParser.COMMA)
                    self.state = 286
                    self.operand()
                    self.state = 291
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 292
                self.match(VerseQLParser.PAREN_RIGHT)
                pass

            elif la_ == 3:
                localctx = VerseQLParser.Function_with_named_argsContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 294
                self.match(VerseQLParser.PAREN_LEFT)
                self.state = 295
                self.named_arg()
                self.state = 300
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==22:
                    self.state = 296
                    self.match(VerseQLParser.COMMA)
                    self.state = 297
                    self.named_arg()
                    self.state = 302
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 303
                self.match(VerseQLParser.PAREN_RIGHT)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Named_argContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.name = None # Token

        def EQ(self):
            return self.getToken(VerseQLParser.EQ, 0)

        def operand(self):
            return self.getTypedRuleContext(VerseQLParser.OperandContext,0)


        def IDENTIFIER(self):
            return self.getToken(VerseQLParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_named_arg

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNamed_arg" ):
                listener.enterNamed_arg(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNamed_arg" ):
                listener.exitNamed_arg(self)




    def named_arg(self):

        localctx = VerseQLParser.Named_argContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_named_arg)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 307
            localctx.name = self.match(VerseQLParser.IDENTIFIER)
            self.state = 308
            self.match(VerseQLParser.EQ)
            self.state = 309
            self.operand()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RefContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.path = None # Ref_pathContext

        def BRACE_LEFT(self, i:int=None):
            if i is None:
                return self.getTokens(VerseQLParser.BRACE_LEFT)
            else:
                return self.getToken(VerseQLParser.BRACE_LEFT, i)

        def BRACE_RIGHT(self, i:int=None):
            if i is None:
                return self.getTokens(VerseQLParser.BRACE_RIGHT)
            else:
                return self.getToken(VerseQLParser.BRACE_RIGHT, i)

        def ref_path(self):
            return self.getTypedRuleContext(VerseQLParser.Ref_pathContext,0)


        def getRuleIndex(self):
            return VerseQLParser.RULE_ref

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRef" ):
                listener.enterRef(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRef" ):
                listener.exitRef(self)




    def ref(self):

        localctx = VerseQLParser.RefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_ref)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 311
            self.match(VerseQLParser.BRACE_LEFT)
            self.state = 312
            self.match(VerseQLParser.BRACE_LEFT)
            self.state = 313
            localctx.path = self.ref_path()
            self.state = 314
            self.match(VerseQLParser.BRACE_RIGHT)
            self.state = 315
            self.match(VerseQLParser.BRACE_RIGHT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Ref_pathContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self, i:int=None):
            if i is None:
                return self.getTokens(VerseQLParser.IDENTIFIER)
            else:
                return self.getToken(VerseQLParser.IDENTIFIER, i)

        def DOT(self):
            return self.getToken(VerseQLParser.DOT, 0)

        def field(self):
            return self.getTypedRuleContext(VerseQLParser.FieldContext,0)


        def COLON(self):
            return self.getToken(VerseQLParser.COLON, 0)

        def SLASH(self, i:int=None):
            if i is None:
                return self.getTokens(VerseQLParser.SLASH)
            else:
                return self.getToken(VerseQLParser.SLASH, i)

        def getRuleIndex(self):
            return VerseQLParser.RULE_ref_path

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRef_path" ):
                listener.enterRef_path(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRef_path" ):
                listener.exitRef_path(self)




    def ref_path(self):

        localctx = VerseQLParser.Ref_pathContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_ref_path)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 321
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,24,self._ctx)
            if la_ == 1:
                self.state = 317
                self.match(VerseQLParser.IDENTIFIER)
                self.state = 318
                self.match(VerseQLParser.COLON)
                self.state = 319
                self.match(VerseQLParser.SLASH)
                self.state = 320
                self.match(VerseQLParser.SLASH)


            self.state = 323
            self.match(VerseQLParser.IDENTIFIER)
            self.state = 324
            self.match(VerseQLParser.DOT)
            self.state = 325
            self.field()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParameterContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.name = None # Token

        def AT(self):
            return self.getToken(VerseQLParser.AT, 0)

        def IDENTIFIER(self):
            return self.getToken(VerseQLParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_parameter

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParameter" ):
                listener.enterParameter(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParameter" ):
                listener.exitParameter(self)




    def parameter(self):

        localctx = VerseQLParser.ParameterContext(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_parameter)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 327
            self.match(VerseQLParser.AT)
            self.state = 328
            localctx.name = self.match(VerseQLParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FieldContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def field_primitive(self):
            return self.getTypedRuleContext(VerseQLParser.Field_primitiveContext,0)


        def field_path(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(VerseQLParser.Field_pathContext)
            else:
                return self.getTypedRuleContext(VerseQLParser.Field_pathContext,i)


        def getRuleIndex(self):
            return VerseQLParser.RULE_field

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterField" ):
                listener.enterField(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitField" ):
                listener.exitField(self)




    def field(self):

        localctx = VerseQLParser.FieldContext(self, self._ctx, self.state)
        self.enterRule(localctx, 62, self.RULE_field)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 330
            self.field_primitive()
            self.state = 334
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,25,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 331
                    self.field_path() 
                self.state = 336
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,25,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Field_pathContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BRACKET_LEFT(self):
            return self.getToken(VerseQLParser.BRACKET_LEFT, 0)

        def value(self):
            return self.getTypedRuleContext(VerseQLParser.ValueContext,0)


        def BRACKET_RIGHT(self):
            return self.getToken(VerseQLParser.BRACKET_RIGHT, 0)

        def MINUS(self):
            return self.getToken(VerseQLParser.MINUS, 0)

        def DOT(self):
            return self.getToken(VerseQLParser.DOT, 0)

        def field_primitive(self):
            return self.getTypedRuleContext(VerseQLParser.Field_primitiveContext,0)


        def getRuleIndex(self):
            return VerseQLParser.RULE_field_path

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterField_path" ):
                listener.enterField_path(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitField_path" ):
                listener.exitField_path(self)




    def field_path(self):

        localctx = VerseQLParser.Field_pathContext(self, self._ctx, self.state)
        self.enterRule(localctx, 64, self.RULE_field_path)
        try:
            self.state = 346
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,26,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 337
                self.match(VerseQLParser.BRACKET_LEFT)
                self.state = 338
                self.value()
                self.state = 339
                self.match(VerseQLParser.BRACKET_RIGHT)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 341
                self.match(VerseQLParser.BRACKET_LEFT)
                self.state = 342
                self.match(VerseQLParser.MINUS)
                self.state = 343
                self.match(VerseQLParser.BRACKET_RIGHT)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 344
                self.match(VerseQLParser.DOT)
                self.state = 345
                self.field_primitive()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Field_primitiveContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(VerseQLParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_field_primitive

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterField_primitive" ):
                listener.enterField_primitive(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitField_primitive" ):
                listener.exitField_primitive(self)




    def field_primitive(self):

        localctx = VerseQLParser.Field_primitiveContext(self, self._ctx, self.state)
        self.enterRule(localctx, 66, self.RULE_field_primitive)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 348
            self.match(VerseQLParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ValueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return VerseQLParser.RULE_value

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class Value_jsonContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def json(self):
            return self.getTypedRuleContext(VerseQLParser.JsonContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValue_json" ):
                listener.enterValue_json(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValue_json" ):
                listener.exitValue_json(self)


    class Value_integerContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def LITERAL_INTEGER(self):
            return self.getToken(VerseQLParser.LITERAL_INTEGER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValue_integer" ):
                listener.enterValue_integer(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValue_integer" ):
                listener.exitValue_integer(self)


    class Value_trueContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def TRUE(self):
            return self.getToken(VerseQLParser.TRUE, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValue_true" ):
                listener.enterValue_true(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValue_true" ):
                listener.exitValue_true(self)


    class Value_falseContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def FALSE(self):
            return self.getToken(VerseQLParser.FALSE, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValue_false" ):
                listener.enterValue_false(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValue_false" ):
                listener.exitValue_false(self)


    class Value_stringContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def literal_string(self):
            return self.getTypedRuleContext(VerseQLParser.Literal_stringContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValue_string" ):
                listener.enterValue_string(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValue_string" ):
                listener.exitValue_string(self)


    class Value_nullContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NULL(self):
            return self.getToken(VerseQLParser.NULL, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValue_null" ):
                listener.enterValue_null(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValue_null" ):
                listener.exitValue_null(self)


    class Value_decimalContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def LITERAL_DECIMAL(self):
            return self.getToken(VerseQLParser.LITERAL_DECIMAL, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValue_decimal" ):
                listener.enterValue_decimal(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValue_decimal" ):
                listener.exitValue_decimal(self)


    class Value_arrayContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def array(self):
            return self.getTypedRuleContext(VerseQLParser.ArrayContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValue_array" ):
                listener.enterValue_array(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValue_array" ):
                listener.exitValue_array(self)



    def value(self):

        localctx = VerseQLParser.ValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 68, self.RULE_value)
        try:
            self.state = 358
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,27,self._ctx)
            if la_ == 1:
                localctx = VerseQLParser.Value_nullContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 350
                self.match(VerseQLParser.NULL)
                pass

            elif la_ == 2:
                localctx = VerseQLParser.Value_trueContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 351
                self.match(VerseQLParser.TRUE)
                pass

            elif la_ == 3:
                localctx = VerseQLParser.Value_falseContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 352
                self.match(VerseQLParser.FALSE)
                pass

            elif la_ == 4:
                localctx = VerseQLParser.Value_stringContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 353
                self.literal_string()
                pass

            elif la_ == 5:
                localctx = VerseQLParser.Value_integerContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 354
                self.match(VerseQLParser.LITERAL_INTEGER)
                pass

            elif la_ == 6:
                localctx = VerseQLParser.Value_decimalContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 355
                self.match(VerseQLParser.LITERAL_DECIMAL)
                pass

            elif la_ == 7:
                localctx = VerseQLParser.Value_jsonContext(self, localctx)
                self.enterOuterAlt(localctx, 7)
                self.state = 356
                self.json()
                pass

            elif la_ == 8:
                localctx = VerseQLParser.Value_arrayContext(self, localctx)
                self.enterOuterAlt(localctx, 8)
                self.state = 357
                self.array()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Literal_stringContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LITERAL_STRING_SINGLE(self):
            return self.getToken(VerseQLParser.LITERAL_STRING_SINGLE, 0)

        def LITERAL_STRING_DOUBLE(self):
            return self.getToken(VerseQLParser.LITERAL_STRING_DOUBLE, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_literal_string

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLiteral_string" ):
                listener.enterLiteral_string(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLiteral_string" ):
                listener.exitLiteral_string(self)




    def literal_string(self):

        localctx = VerseQLParser.Literal_stringContext(self, self._ctx, self.state)
        self.enterRule(localctx, 70, self.RULE_literal_string)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 360
            _la = self._input.LA(1)
            if not(_la==44 or _la==45):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArrayContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return VerseQLParser.RULE_array

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class Array_itemsContext(ArrayContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.ArrayContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BRACKET_LEFT(self):
            return self.getToken(VerseQLParser.BRACKET_LEFT, 0)
        def value(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(VerseQLParser.ValueContext)
            else:
                return self.getTypedRuleContext(VerseQLParser.ValueContext,i)

        def BRACKET_RIGHT(self):
            return self.getToken(VerseQLParser.BRACKET_RIGHT, 0)
        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(VerseQLParser.COMMA)
            else:
                return self.getToken(VerseQLParser.COMMA, i)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArray_items" ):
                listener.enterArray_items(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArray_items" ):
                listener.exitArray_items(self)


    class Array_emptyContext(ArrayContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a VerseQLParser.ArrayContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BRACKET_LEFT(self):
            return self.getToken(VerseQLParser.BRACKET_LEFT, 0)
        def BRACKET_RIGHT(self):
            return self.getToken(VerseQLParser.BRACKET_RIGHT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArray_empty" ):
                listener.enterArray_empty(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArray_empty" ):
                listener.exitArray_empty(self)



    def array(self):

        localctx = VerseQLParser.ArrayContext(self, self._ctx, self.state)
        self.enterRule(localctx, 72, self.RULE_array)
        self._la = 0 # Token type
        try:
            self.state = 375
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,29,self._ctx)
            if la_ == 1:
                localctx = VerseQLParser.Array_emptyContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 362
                self.match(VerseQLParser.BRACKET_LEFT)
                self.state = 363
                self.match(VerseQLParser.BRACKET_RIGHT)
                pass

            elif la_ == 2:
                localctx = VerseQLParser.Array_itemsContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 364
                self.match(VerseQLParser.BRACKET_LEFT)
                self.state = 365
                self.value()
                self.state = 370
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==22:
                    self.state = 366
                    self.match(VerseQLParser.COMMA)
                    self.state = 367
                    self.value()
                    self.state = 372
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 373
                self.match(VerseQLParser.BRACKET_RIGHT)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class JsonContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def json_value(self):
            return self.getTypedRuleContext(VerseQLParser.Json_valueContext,0)


        def getRuleIndex(self):
            return VerseQLParser.RULE_json

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterJson" ):
                listener.enterJson(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitJson" ):
                listener.exitJson(self)




    def json(self):

        localctx = VerseQLParser.JsonContext(self, self._ctx, self.state)
        self.enterRule(localctx, 74, self.RULE_json)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 377
            self.json_value()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Json_objContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BRACE_LEFT(self):
            return self.getToken(VerseQLParser.BRACE_LEFT, 0)

        def json_pair(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(VerseQLParser.Json_pairContext)
            else:
                return self.getTypedRuleContext(VerseQLParser.Json_pairContext,i)


        def BRACE_RIGHT(self):
            return self.getToken(VerseQLParser.BRACE_RIGHT, 0)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(VerseQLParser.COMMA)
            else:
                return self.getToken(VerseQLParser.COMMA, i)

        def getRuleIndex(self):
            return VerseQLParser.RULE_json_obj

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterJson_obj" ):
                listener.enterJson_obj(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitJson_obj" ):
                listener.exitJson_obj(self)




    def json_obj(self):

        localctx = VerseQLParser.Json_objContext(self, self._ctx, self.state)
        self.enterRule(localctx, 76, self.RULE_json_obj)
        self._la = 0 # Token type
        try:
            self.state = 392
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,31,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 379
                self.match(VerseQLParser.BRACE_LEFT)
                self.state = 380
                self.json_pair()
                self.state = 385
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==22:
                    self.state = 381
                    self.match(VerseQLParser.COMMA)
                    self.state = 382
                    self.json_pair()
                    self.state = 387
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 388
                self.match(VerseQLParser.BRACE_RIGHT)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 390
                self.match(VerseQLParser.BRACE_LEFT)
                self.state = 391
                self.match(VerseQLParser.BRACE_RIGHT)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Json_pairContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def json_string(self):
            return self.getTypedRuleContext(VerseQLParser.Json_stringContext,0)


        def COLON(self):
            return self.getToken(VerseQLParser.COLON, 0)

        def json_value(self):
            return self.getTypedRuleContext(VerseQLParser.Json_valueContext,0)


        def getRuleIndex(self):
            return VerseQLParser.RULE_json_pair

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterJson_pair" ):
                listener.enterJson_pair(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitJson_pair" ):
                listener.exitJson_pair(self)




    def json_pair(self):

        localctx = VerseQLParser.Json_pairContext(self, self._ctx, self.state)
        self.enterRule(localctx, 78, self.RULE_json_pair)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 394
            self.json_string()
            self.state = 395
            self.match(VerseQLParser.COLON)
            self.state = 396
            self.json_value()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Json_arrContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BRACKET_LEFT(self):
            return self.getToken(VerseQLParser.BRACKET_LEFT, 0)

        def json_value(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(VerseQLParser.Json_valueContext)
            else:
                return self.getTypedRuleContext(VerseQLParser.Json_valueContext,i)


        def BRACKET_RIGHT(self):
            return self.getToken(VerseQLParser.BRACKET_RIGHT, 0)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(VerseQLParser.COMMA)
            else:
                return self.getToken(VerseQLParser.COMMA, i)

        def getRuleIndex(self):
            return VerseQLParser.RULE_json_arr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterJson_arr" ):
                listener.enterJson_arr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitJson_arr" ):
                listener.exitJson_arr(self)




    def json_arr(self):

        localctx = VerseQLParser.Json_arrContext(self, self._ctx, self.state)
        self.enterRule(localctx, 80, self.RULE_json_arr)
        self._la = 0 # Token type
        try:
            self.state = 411
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,33,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 398
                self.match(VerseQLParser.BRACKET_LEFT)
                self.state = 399
                self.json_value()
                self.state = 404
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==22:
                    self.state = 400
                    self.match(VerseQLParser.COMMA)
                    self.state = 401
                    self.json_value()
                    self.state = 406
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 407
                self.match(VerseQLParser.BRACKET_RIGHT)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 409
                self.match(VerseQLParser.BRACKET_LEFT)
                self.state = 410
                self.match(VerseQLParser.BRACKET_RIGHT)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Json_valueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def json_string(self):
            return self.getTypedRuleContext(VerseQLParser.Json_stringContext,0)


        def json_number(self):
            return self.getTypedRuleContext(VerseQLParser.Json_numberContext,0)


        def json_obj(self):
            return self.getTypedRuleContext(VerseQLParser.Json_objContext,0)


        def json_arr(self):
            return self.getTypedRuleContext(VerseQLParser.Json_arrContext,0)


        def TRUE(self):
            return self.getToken(VerseQLParser.TRUE, 0)

        def FALSE(self):
            return self.getToken(VerseQLParser.FALSE, 0)

        def NULL(self):
            return self.getToken(VerseQLParser.NULL, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_json_value

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterJson_value" ):
                listener.enterJson_value(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitJson_value" ):
                listener.exitJson_value(self)




    def json_value(self):

        localctx = VerseQLParser.Json_valueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 82, self.RULE_json_value)
        try:
            self.state = 420
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [45]:
                self.enterOuterAlt(localctx, 1)
                self.state = 413
                self.json_string()
                pass
            elif token in [46, 47]:
                self.enterOuterAlt(localctx, 2)
                self.state = 414
                self.json_number()
                pass
            elif token in [36]:
                self.enterOuterAlt(localctx, 3)
                self.state = 415
                self.json_obj()
                pass
            elif token in [34]:
                self.enterOuterAlt(localctx, 4)
                self.state = 416
                self.json_arr()
                pass
            elif token in [20]:
                self.enterOuterAlt(localctx, 5)
                self.state = 417
                self.match(VerseQLParser.TRUE)
                pass
            elif token in [9]:
                self.enterOuterAlt(localctx, 6)
                self.state = 418
                self.match(VerseQLParser.FALSE)
                pass
            elif token in [14]:
                self.enterOuterAlt(localctx, 7)
                self.state = 419
                self.match(VerseQLParser.NULL)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Json_stringContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LITERAL_STRING_DOUBLE(self):
            return self.getToken(VerseQLParser.LITERAL_STRING_DOUBLE, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_json_string

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterJson_string" ):
                listener.enterJson_string(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitJson_string" ):
                listener.exitJson_string(self)




    def json_string(self):

        localctx = VerseQLParser.Json_stringContext(self, self._ctx, self.state)
        self.enterRule(localctx, 84, self.RULE_json_string)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 422
            self.match(VerseQLParser.LITERAL_STRING_DOUBLE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Json_numberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LITERAL_INTEGER(self):
            return self.getToken(VerseQLParser.LITERAL_INTEGER, 0)

        def LITERAL_DECIMAL(self):
            return self.getToken(VerseQLParser.LITERAL_DECIMAL, 0)

        def getRuleIndex(self):
            return VerseQLParser.RULE_json_number

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterJson_number" ):
                listener.enterJson_number(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitJson_number" ):
                listener.exitJson_number(self)




    def json_number(self):

        localctx = VerseQLParser.Json_numberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 86, self.RULE_json_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 424
            _la = self._input.LA(1)
            if not(_la==46 or _la==47):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[17] = self.expression_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expression_sempred(self, localctx:ExpressionContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 2)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 1)
         
